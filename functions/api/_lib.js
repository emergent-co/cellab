// functions/api/_lib.js — 주문관리 공용 유틸 (라우팅 안 됨: 밑줄 시작 파일)

export const KST = 9 * 3600 * 1000;

export function kstISO(d = new Date()) {
  return new Date(d.getTime() + KST).toISOString().slice(0, 19).replace('T', ' ');
}
export function kstDate(d = new Date()) {
  return new Date(d.getTime() + KST).toISOString().slice(0, 10);
}

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers },
  });
}

export function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

export function won(n) {
  return Number(n || 0).toLocaleString('ko-KR');
}

// ---------- 관리자 ----------
//   두 가지 길이 있다.
//     ① ADMIN_PASSWORD Basic Auth — 카카오 없이 어디서든 들어가는 비상구
//     ② customers.role = 'admin' 인 사람의 카카오 세션 — 평소에 쓰는 길
//   ①을 남겨두는 이유: 카카오 로그인이 막히거나 계정에 문제가 생겨도 관리자가 잠기지 않는다.
export const REALM = 'rndsetup-admin';

/** 카카오 세션까지 본다. 비동기라 호출부에서 await 해야 한다. */
export async function adminOK(request, env) {
  if (isAdmin(request, env)) return true;
  const me = await currentCustomer(request, env).catch(() => null);
  return !!(me && me.role === 'admin');
}

export function isAdmin(request, env) {
  const pw = env.ADMIN_PASSWORD || '';
  if (!pw) return false;
  const auth = request.headers.get('Authorization') || '';
  if (!auth.startsWith('Basic ')) return false;
  let d = '';
  try { d = atob(auth.slice(6)); } catch { return false; }
  const i = d.indexOf(':');
  return (i >= 0 ? d.slice(i + 1) : d) === pw;
}
export function needAdmin() {
  return json({ error: 'unauthorized' }, 401, {
    'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
  });
}

// ---------- 고객 세션 ----------
const COOKIE = 'rs_sess';

export function readCookie(request, name = COOKIE) {
  const raw = request.headers.get('Cookie') || '';
  for (const part of raw.split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === name) return decodeURIComponent(v.join('='));
  }
  return '';
}

export function sessionCookie(token, maxAge = 60 * 60 * 24 * 30) {
  return `${COOKIE}=${encodeURIComponent(token)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}
export function clearCookie() {
  return `${COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

export function randomToken() {
  const b = new Uint8Array(32);
  crypto.getRandomValues(b);
  return [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
}

export async function createSession(env, customerId) {
  const token = randomToken();
  const exp = new Date(Date.now() + 30 * 86400000);
  await env.DB.prepare('INSERT INTO sessions (token, customer_id, expires_at, created_at) VALUES (?,?,?,?)')
    .bind(token, customerId, kstISO(exp), kstISO()).run();
  return token;
}

export async function currentCustomer(request, env) {
  const token = readCookie(request);
  if (!token) return null;
  const row = await env.DB.prepare(
    `SELECT c.* FROM sessions s JOIN customers c ON c.id = s.customer_id
     WHERE s.token = ? AND s.expires_at > ?`
  ).bind(token, kstISO()).first();
  return row || null;
}

export async function dropSession(request, env) {
  const token = readCookie(request);
  if (token) await env.DB.prepare('DELETE FROM sessions WHERE token = ?').bind(token).run();
}

// ---------- 주문번호 ----------
export async function nextOrderNo(env) {
  const day = kstDate().replace(/-/g, '');
  /* COUNT 로 세면 중간 것을 지웠을 때 번호가 되돌아가 이미 쓴 번호를 다시 준다.
     order_no 는 UNIQUE 라 그 순간 INSERT 가 터진다 — 지금까지 쓴 «가장 큰 번호»의 다음을 준다. */
  const row = await env.DB.prepare(
    "SELECT MAX(order_no) AS m FROM orders WHERE order_no LIKE ?"
  ).bind(`ORD-${day}-%`).first();
  const last = Number(String(row?.m || '').slice(-2)) || 0;
  return `ORD-${day}-${String(last + 1).padStart(2, '0')}`;
}

// ---------- 문서번호 (기존 발행본 규칙: YYYYMMDD-Q / -T / -X) ----------
/* 예약 시각은 큐에서 «문자열 비교»로 걸러진다(`send_at <= now`). 형식이 조금만 달라도
   («2026-09-05T14:00» 처럼 T 가 남거나 초가 빠지면) 그날 안에는 절대 안 나가고 엉뚱한 때 나간다. */
export function validSendAt(v) {
  const s = String(v || '').trim();
  if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) return null;
  const [d, t] = s.split(' ');
  const [Y, M, D] = d.split('-').map(Number); const [h, m, sec] = t.split(':').map(Number);
  if (M < 1 || M > 12 || D < 1 || D > 31 || h > 23 || m > 59 || sec > 59) return null;
  if (Y < 2020 || Y > 2100) return null;
  return s;
}

export const DOC_SUFFIX = { quote: 'Q', statement: 'T', taxinvoice: 'X' };
export const DOC_LABEL  = { quote: '견적서', statement: '거래명세서', taxinvoice: '세금계산서' };

export async function nextDocNo(env, type) {
  const sfx = DOC_SUFFIX[type] || 'Q';
  const day = kstDate().replace(/-/g, '');
  /* 여기도 COUNT 로 세면 안 된다 — 가운데 문서를 지우면 다음 발행이 이미 쓴 번호를 되받는다.
     doc_no 에는 UNIQUE 가 없어 중복이 조용히 저장되고, 바로빌 관리번호까지 충돌한다.
     오늘 쓴 번호 중 «가장 큰 것»의 다음을 준다. (`YYYYMMDD-Q` 는 1번으로 친다) */
  const { results } = await env.DB.prepare(
    'SELECT doc_no FROM documents WHERE doc_no LIKE ?'
  ).bind(`${day}%-${sfx}`).all();
  let last = 0;
  for (const r of results || []) {
    const m = String(r.doc_no || '').match(/^\d{8}(?:-(\d{2}))?-/);
    if (m) last = Math.max(last, m[1] ? Number(m[1]) : 1);
  }
  return last === 0 ? `${day}-${sfx}` : `${day}-${String(last + 1).padStart(2, '0')}-${sfx}`;
}

// 유효기간 = 발행일 + 30일
export function plusDays(ymd, days) {
  const [y, m, d] = String(ymd).split('-').map(Number);
  const t = new Date(Date.UTC(y, m - 1, d) + days * 86400000);
  return t.toISOString().slice(0, 10);
}

// ---------- 이력 ----------
export async function logEvent(env, e) {
  await env.DB.prepare(
    `INSERT INTO doc_events (order_id, document_id, action, channel, actor, to_addr, result, detail, created_at)
     VALUES (?,?,?,?,?,?,?,?,?)`
  ).bind(
    e.order_id || null, e.document_id || null, e.action || '', e.channel || 'web',
    e.actor || 'system', e.to_addr || null, e.result || 'ok', e.detail || null, kstISO()
  ).run();
}

// ---------- 금액 재계산 ----------
export async function recalcOrder(env, orderId) {
  const { results } = await env.DB.prepare(
    'SELECT qty, unit_price FROM order_items WHERE order_id = ?'
  ).bind(orderId).all();
  /* 장부 금액도 서류와 같은 규칙으로 낸다. 반올림으로 내면 서류 합계와 몇 원씩 어긋나고,
     그 차이 때문에 «같은 건 중복 주문» 감지(총액 정확 일치)가 통째로 무력해진다. */
  let supply = 0, vat = 0;
  for (const r of results || []) {
    const line = Math.round((r.qty || 0) * (r.unit_price || 0));
    supply += line;
    vat += Math.floor(line * 0.1 / 10) * 10;
  }
  await env.DB.prepare(
    'UPDATE orders SET supply_amount=?, vat_amount=?, total_amount=?, updated_at=? WHERE id=?'
  ).bind(supply, vat, supply + vat, kstISO(), orderId).run();
  return { supply, vat, total: supply + vat };
}

// 배송중까지가 관리자 몫, 수령확인은 고객이 누른다.
export const STATUSES = ['요청접수', '견적발송', '견적승인', '발주확정', '배송중', '수령확인', '계산서발행', '완료', '보류', '취소'];

// ---------- 공급자(이머전트) 정보 ----------
/**
 * /member/ (주문·정산) 는 멤버십 = 승인 + 후불 거래처 전용이다.
 *   - access '승인'  : 거래처로 확정된 사람. 새 카카오 가입자는 '대기'.
 *   - billing_mode '후불' : 쓴 만큼 쌓아두고 중간정산하는 방식. 이 화면 전체가 그 전제로 짜여 있다.
 * 선불 고객은 여기 들어오지 않는다 — 주문 이력은 선불 전용 페이지에서 본다.
 */
export function isApproved(c) { return !!(c && c.access === '승인'); }
export function isPostpaid(c) { return !!(c && (c.billing_mode || '선불') === '후불'); }
export function isMember(c) { return isApproved(c) && isPostpaid(c); }

/** 멤버십 전용 API 앞에 세우는 문지기. 통과하면 null, 아니면 Response. */
export function memberGate(me) {
  if (!me) return json({ error: 'login_required' }, 401);
  if (me.role === 'admin') return null;          // 관리자 화면이 이 안에 있다 — 플래그로 잠그지 않는다
  if (!isApproved(me)) {
    return json({
      error: 'not_member',
      message: '주문·정산은 멤버십 회원만 이용할 수 있습니다. 견적 문의로 남겨주시면 연락드리겠습니다.',
    }, 403);
  }
  if (!isPostpaid(me)) {
    return json({
      error: 'prepaid_only',
      message: '이 화면은 후불(멤버십) 거래처 전용입니다. 선불 거래는 주문 조회 페이지에서 확인해주세요.',
    }, 403);
  }
  return null;
}

/**
 * 회신받을 이메일.
 * 카카오 계정 이메일은 대개 개인 메일이라 업무 서류를 거기로 보내면 안 된다.
 * 고객이 따로 적어둔 업무용 메일(work_email)이 있으면 그것을 우선한다.
 */
export function replyEmail(c) {
  if (!c) return '';
  return String(c.work_email || c.email || '').trim();
}

export const SUPPLIER = {
  company: '이머전트',
  brand: '실험셋업연구소',
  ceo: '이영현',
  biz_no: '328-03-02926',
  tel: '070-8983-2600',
  email: 'info@rndsetup.com',
  address: '부산광역시',
  biz_type: '서비스·도매/소매업',
  biz_item: '정밀·과학기기 도매, 전기·전자·정밀기기 수리',
};
