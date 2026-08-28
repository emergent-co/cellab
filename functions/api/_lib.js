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

// ---------- 관리자 Basic Auth (기존 /admin 과 동일 규칙) ----------
export const REALM = 'rndsetup-admin';
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
  const row = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM orders WHERE order_no LIKE ?"
  ).bind(`ORD-${day}-%`).first();
  const n = String((row?.c || 0) + 1).padStart(2, '0');
  return `ORD-${day}-${n}`;
}

// ---------- 문서번호 (기존 발행본 규칙: YYYYMMDD-Q / -T / -X) ----------
export const DOC_SUFFIX = { quote: 'Q', statement: 'T', taxinvoice: 'X' };
export const DOC_LABEL  = { quote: '견적서', statement: '거래명세서', taxinvoice: '세금계산서' };

export async function nextDocNo(env, type) {
  const sfx = DOC_SUFFIX[type] || 'Q';
  const day = kstDate().replace(/-/g, '');
  const { results } = await env.DB.prepare(
    'SELECT doc_no FROM documents WHERE doc_no LIKE ?'
  ).bind(`${day}%-${sfx}`).all();
  const n = (results || []).length;
  return n === 0 ? `${day}-${sfx}` : `${day}-${String(n + 1).padStart(2, '0')}-${sfx}`;
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
  const supply = (results || []).reduce((s, r) => s + Math.round((r.qty || 0) * (r.unit_price || 0)), 0);
  const vat = Math.round(supply * 0.1);
  await env.DB.prepare(
    'UPDATE orders SET supply_amount=?, vat_amount=?, total_amount=?, updated_at=? WHERE id=?'
  ).bind(supply, vat, supply + vat, kstISO(), orderId).run();
  return { supply, vat, total: supply + vat };
}

// 배송중까지가 관리자 몫, 수령확인은 고객이 누른다.
export const STATUSES = ['요청접수', '견적발송', '견적승인', '발주확정', '배송중', '수령확인', '계산서발행', '완료', '보류', '취소'];

// ---------- 공급자(이머전트) 정보 ----------
/**
 * 주문·정산 페이지는 등록된 거래처(VIP) 전용이다.
 * customers.access 가 '승인' 인 사람만 열린다. 새 카카오 가입자는 '대기'.
 */
export function isVip(c) {
  return !!(c && c.access === '승인');
}

/** VIP 전용 API 앞에 세우는 문지기. 통과하면 null, 아니면 Response. */
export function vipGate(me) {
  if (!me) return json({ error: 'login_required' }, 401);
  if (!isVip(me)) {
    return json({
      error: 'not_vip',
      message: '주문·정산은 등록된 거래처만 이용할 수 있습니다. 견적 문의로 남겨주시면 연락드리겠습니다.',
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
