// functions/api/admin/clients.js — 거래처 관리
//   한 거래처를 통으로 본다: 기본정보 · 실험실 · 발행정보 · 주문 · 정산 · 문서 · 잔여금.
//   GET  ?q=&access=&mode=   목록
//   GET  ?id=<id>            상세
//   POST { id, action }      access · mode · memo · profile(연락처 수정)
//   권한(role)은 여기서 못 바꾼다 — DB에서 직접만. 화면을 타고 관리자가 번지지 않게.
import { json, needAdmin, adminOK, kstISO, logEvent } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

// '거래처' = 로그인 계정이 아니라 서류 발행용으로만 들고 있는 곳(기존 사이트에서 옮겨온 것).
// 멤버십 권한은 없다 — isMember() 는 '승인' 만 통과시킨다.
const ACCESS = ['승인', '대기', '거절', '거래처'];
const safe = (s) => { try { return JSON.parse(s || '[]'); } catch { return []; } };

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  if (request.method === 'GET') return get(request, env);
  if (request.method === 'POST') return post(request, env);
  return json({ error: 'method_not_allowed' }, 405);
}

async function get(request, env) {
  const u = new URL(request.url).searchParams;

  // ---------------- 상세 ----------------
  if (u.get('id')) {
    const c = await env.DB.prepare(
      `SELECT c.*, l.name AS lab_name, l.code AS lab_code
         FROM customers c LEFT JOIN labs l ON l.id=c.lab_id WHERE c.id=?`).bind(u.get('id')).first();
    if (!c) return json({ error: 'not_found' }, 404);

    // 아래 다섯 개는 batch 한 번, 합계·원장은 각자 이미 batch 로 묶여 있다
    const [profiles, orders, settles, docs, members, sum, led] = await Promise.all([
      env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id')
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, order_no, title, status, total_amount, manual, created_at
                        FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      // 수정 폼에서 그대로 쓸 수 있게 필요한 칸을 다 실어 보낸다
      env.DB.prepare(`SELECT id, status, items_json, supply, vat, total, method, manual,
                             quote_date, statement_date, taxinvoice_date, bill_profile_id,
                             memo, admin_memo, created_at
                        FROM settlements WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, type, doc_no, status, issue_date, access_token, payload_json
                        FROM documents WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      c.lab_id
        ? env.DB.prepare('SELECT id, name, email, work_email, access FROM customers WHERE lab_id=? ORDER BY id')
            .bind(c.lab_id).all().then((r) => r.results || [])
        : Promise.resolve([]),
      settlement(env, c.id),
      ledger(env, c.id, 40),
    ]);

    const { role, kakao_id, ...safeCustomer } = c;   // 카카오 식별자·권한은 화면에 내보내지 않는다
    return json({
      client: { ...safeCustomer, is_admin: role === 'admin' },
      profiles, orders, members, ledger: led, ...sum,
      settlements: settles.map((s) => ({ ...s, items: safe(s.items_json) })),
      documents: docs.map((d) => {
        let p = {}; try { p = JSON.parse(d.payload_json || '{}'); } catch { /* noop */ }
        // 열람 토큰은 링크로만 내보내고 원본 필드는 지운다
        const { payload_json, access_token, ...rest } = d;
        return { ...rest, title: p.title || '', total: p.totals?.total || 0,
                 view: `/doc/${d.id}?t=${access_token}` };
      }),
    });
  }

  // ---------------- 사업자 단위 목록 (거래처 추가에서 '기존 사업자 찾기') ----------------
  if (u.get('orgs')) {
    const q = (u.get('q') || '').trim();
    const w = ["c.biz_no IS NOT NULL", "c.biz_no <> ''"], bind = [];
    if (q) {
      w.push('(c.company LIKE ? OR c.alias LIKE ? OR c.biz_no LIKE ? OR c.ceo LIKE ?)');
      for (let i = 0; i < 4; i++) bind.push(`%${q}%`);
    }
    // 같은 사업자번호를 쓰는 곳들을 하나로 묶는다. 대표자·주소는 가장 최근에 적어둔 것.
    const { results } = await env.DB.prepare(
      `SELECT c.biz_no,
              MAX(c.company) AS company,
              MAX(c.ceo)     AS ceo,
              MAX(c.address) AS address,
              COUNT(*)       AS n,
              MIN(c.id)      AS any_id
         FROM customers c
        WHERE ${w.join(' AND ')}
        GROUP BY c.biz_no
        ORDER BY n DESC, company
        LIMIT 30`).bind(...bind).all();

    const orgs = [];
    for (const o of results || []) {
      const kids = (await env.DB.prepare(
        'SELECT id, alias, name, work_email FROM customers WHERE biz_no=? ORDER BY id LIMIT 20')
        .bind(o.biz_no).all()).results || [];
      orgs.push({ ...o, children: kids });
    }
    return json({ orgs });
  }

  // ---------------- 목록 ----------------
  const w = [], bind = [];
  const access = u.get('access');
  if (access && ACCESS.includes(access)) { w.push('c.access=?'); bind.push(access); }
  const mode = u.get('mode');
  if (mode === '후불' || mode === '선불') { w.push('c.billing_mode=?'); bind.push(mode); }
  const q = (u.get('q') || '').trim();
  if (q) {
    w.push('(c.name LIKE ? OR c.company LIKE ? OR c.alias LIKE ? OR c.email LIKE ?'
         + ' OR c.work_email LIKE ? OR c.phone LIKE ? OR c.biz_no LIKE ? OR c.memo LIKE ? OR l.name LIKE ?)');
    for (let i = 0; i < 9; i++) bind.push(`%${q}%`);
  }
  const where = w.length ? `WHERE ${w.join(' AND ')}` : '';

  const { results } = await env.DB.prepare(
    `SELECT c.id, c.name, c.company, c.alias, c.biz_no, c.phone, c.email, c.work_email, c.billing_mode,
            c.access, c.memo, c.created_at, l.name AS lab_name,
            COALESCE((SELECT SUM(o.total_amount) FROM orders o
                       WHERE o.customer_id=c.id AND o.status<>'취소'),0) AS spent,
            COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS paid,
            (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id AND o.status<>'취소') AS orders_n,
            (SELECT MAX(o.created_at) FROM orders o WHERE o.customer_id=c.id) AS last_order,
            (SELECT COUNT(*) FROM documents d WHERE d.customer_id=c.id) AS docs_n
       FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
       ${where}
      ORDER BY (c.access='대기') DESC, c.company, c.id LIMIT 300`).bind(...bind).all();

  const clients = (results || []).map((r) => ({ ...r, due: (r.spent || 0) - (r.paid || 0) }));
  const stats = (await env.DB.prepare(
    `SELECT SUM(CASE WHEN access='승인' THEN 1 ELSE 0 END) AS ok,
            SUM(CASE WHEN access='대기' THEN 1 ELSE 0 END) AS wait,
            SUM(CASE WHEN access='거절' THEN 1 ELSE 0 END) AS no,
            SUM(CASE WHEN access='거래처' THEN 1 ELSE 0 END) AS client,
            SUM(CASE WHEN billing_mode='후불' THEN 1 ELSE 0 END) AS post,
            COUNT(*) AS all_ FROM customers`).first()) || {};
  return json({ clients, stats });
}

async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  if (b.action === 'create') return create(env, b);
  if (!b.id) return json({ error: 'no_id' }, 400);
  const c = await env.DB.prepare(
    'SELECT id, name, company, billing_mode, role, access, kakao_id FROM customers WHERE id=?'
  ).bind(b.id).first();
  if (!c) return json({ error: 'not_found' }, 404);
  const now = kstISO();
  const who = c.company || c.name || `#${c.id}`;

  if (b.action === 'access') {
    if (!ACCESS.includes(b.access)) return json({ error: 'bad_access' }, 400);
    // 멤버십 승인 = 후불. /member/ 는 후불 전제로 짜여 있어, 승인만 하고 선불로 두면 못 들어온다.
    const toPostpaid = b.access === '승인' && (c.billing_mode || '선불') !== '후불';
    await env.DB.prepare(
      toPostpaid
        ? "UPDATE customers SET access=?, billing_mode='후불', updated_at=? WHERE id=?"
        : 'UPDATE customers SET access=?, updated_at=? WHERE id=?'
    ).bind(b.access, now, c.id).run();
    await logEvent(env, { action: 'member_access', actor: 'admin',
      detail: `${who} 멤버십 ${b.access}${toPostpaid ? ' · 후불 전환' : ''}` });
    return json({ ok: true, access: b.access, billing_mode: toPostpaid ? '후불' : c.billing_mode });
  }

  if (b.action === 'mode') {
    const mode = b.billing_mode === '후불' ? '후불' : '선불';
    await env.DB.prepare('UPDATE customers SET billing_mode=?, updated_at=? WHERE id=?').bind(mode, now, c.id).run();
    await logEvent(env, { action: 'billing_mode', actor: 'admin', detail: `${who} ${mode} 전환` });
    return json({ ok: true, billing_mode: mode });
  }

  /* 거래처 삭제.
     이력이 한 건이라도 있으면 지우지 않는다 — 주문·정산·문서가 사라지면 장부가 어긋나고,
     이미 나간 서류의 발행처만 없어진다. 그럴 땐 «거절»로 돌려 목록에서 내리는 게 맞다. */
  if (b.action === 'delete') {
    if (c.role === 'admin') {
      return json({ error: 'is_admin', message: '관리자 계정은 지울 수 없습니다.' }, 400);
    }
    const n = await env.DB.prepare(
      `SELECT (SELECT COUNT(*) FROM orders      WHERE customer_id=?1) AS o,
              (SELECT COUNT(*) FROM settlements WHERE customer_id=?1) AS s,
              (SELECT COUNT(*) FROM documents   WHERE customer_id=?1) AS d,
              (SELECT COUNT(*) FROM payments    WHERE customer_id=?1) AS p`
    ).bind(c.id).first();
    const left = [];
    if (n.o) left.push(`주문 ${n.o}건`);
    if (n.s) left.push(`정산 ${n.s}건`);
    if (n.d) left.push(`발행 문서 ${n.d}건`);
    if (n.p) left.push(`입금 ${n.p}건`);
    if (left.length) {
      return json({ error: 'has_history',
        message: `${left.join(' · ')}이 남아 있어 지울 수 없습니다.\n`
               + '이력을 먼저 지우거나, 멤버십을 «거절»로 돌려 목록에서 내려주세요.' }, 400);
    }
    // 딸린 부속만 함께 정리한다. 이력이 없는 것은 위에서 확인했다.
    await env.DB.batch([
      env.DB.prepare('DELETE FROM bill_profiles WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM sites         WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM sessions      WHERE customer_id=?').bind(c.id),
      env.DB.prepare('UPDATE todos     SET customer_id=NULL WHERE customer_id=?').bind(c.id),
      env.DB.prepare('UPDATE inquiries SET customer_id=NULL WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM customers WHERE id=?').bind(c.id),
    ]);
    await logEvent(env, { action: 'client_deleted', actor: 'admin',
      detail: `거래처 삭제 ${who}${c.kakao_id ? ' (카카오 계정 연결됨 — 다시 로그인하면 새로 만들어집니다)' : ''}` });
    return json({ ok: true, deleted: who });
  }

  if (b.action === 'memo') {
    await env.DB.prepare('UPDATE customers SET memo=?, updated_at=? WHERE id=?')
      .bind(String(b.memo || ''), now, c.id).run();
    return json({ ok: true });
  }

  // 연락처 오타 수정 — 권한(role)·카카오 식별자는 건드리지 않는다
  if (b.action === 'profile') {
    const email = String(b.work_email || '').trim();
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'bad_email', message: '업무 이메일 형식이 올바르지 않습니다.' }, 400);
    }
    await env.DB.prepare(
      `UPDATE customers SET name=?, company=?, alias=?, biz_no=?, ceo=?, phone=?, work_email=?, address=?, updated_at=? WHERE id=?`
    ).bind(String(b.name || ''), String(b.company || ''), String(b.alias || ''),
           String(b.biz_no || ''), String(b.ceo || ''), String(b.phone || ''),
           email, String(b.address || ''), now, c.id).run();
    await logEvent(env, { action: 'client_edit', actor: 'admin', detail: `${who} 거래처 정보 수정` });
    return json({ ok: true });
  }

  return json({ error: 'unknown_action' }, 400);
}

/* 거래처 추가.
   양식은 하나다 — 기존 사업자든 새 사업자든 같은 칸을 채운다.
   사업자번호가 이미 쓰이고 있으면, 상호·대표자·주소는 그 사업자에 맞춰 정리한다
   (화면에서 골라 채웠어도 손으로 고쳐 어긋나는 일이 생긴다). */
async function create(env, b) {
  const now = kstISO();
  const email = String(b.work_email || '').trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'bad_email', message: '업무 이메일 형식이 올바르지 않습니다.' }, 400);
  }

  let company = String(b.company || '').trim();
  let biz_no  = String(b.biz_no || '').trim();
  let ceo     = String(b.ceo || '').trim();
  let address = String(b.address || '').trim();
  if (!company) return json({ error: 'no_company', message: '거래처명을 입력해주세요.' }, 400);

  if (biz_no) {
    const twin = await env.DB.prepare(
      `SELECT company, ceo, address FROM customers
        WHERE biz_no=? AND company IS NOT NULL AND company <> '' ORDER BY id LIMIT 1`)
      .bind(biz_no).first();
    if (twin) {                       // 같은 사업자번호는 같은 상호를 쓴다
      company = twin.company;
      ceo     = ceo || twin.ceo || '';
      address = address || twin.address || '';
    }
  }

  const alias = String(b.alias || '').trim() || company;

  // 같은 사업자번호에 같은 별칭이 이미 있으면 막는다 — 목록에서 구분이 안 된다
  if (biz_no) {
    const dup = await env.DB.prepare(
      'SELECT id FROM customers WHERE biz_no=? AND alias=? LIMIT 1').bind(biz_no, alias).first();
    if (dup) {
      return json({ error: 'duplicate',
        message: `'${company}' 에 '${alias}' 별칭이 이미 있습니다. 다른 별칭을 써주세요.` }, 409);
    }
  }

  const r = await env.DB.prepare(
    `INSERT INTO customers (company, alias, biz_no, ceo, name, work_email, phone, address, memo,
                            access, role, billing_mode, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?, '거래처','member',?,?,?)`
  ).bind(company, alias, biz_no || null, ceo || null,
         String(b.name || '').trim() || null, email || null,
         String(b.phone || '').trim() || null, address || null,
         String(b.memo || '').trim() || null,
         b.billing_mode === '후불' ? '후불' : '선불', now, now).run();

  const id = r.meta.last_row_id;

  // 사업자번호가 있으면 계산서 발행정보도 같이 만들어 둔다 — 견적서를 바로 뽑을 수 있게
  if (biz_no) {
    await env.DB.prepare(
      `INSERT INTO bill_profiles (customer_id, label, company, biz_no, ceo, tax_email, address, is_default, created_at, updated_at)
       VALUES (?, '기본', ?,?,?,?,?, 1, ?, ?)`
    ).bind(id, company, biz_no, ceo || null, String(b.tax_email || '').trim() || email || null,
           address || null, now, now).run();
  }

  await logEvent(env, { action: 'client_add', actor: 'admin',
    detail: `거래처 추가 ${company}${alias !== company ? ` (${alias})` : ''}` });

  // 만든 거래처를 그대로 돌려준다 — 문서 발행 화면에서 곧바로 골라 쓸 수 있게
  return json({ ok: true, id, client: {
    id, company, alias, biz_no, ceo, address,
    name: String(b.name || '').trim(),
    work_email: email, email: '', phone: String(b.phone || '').trim(),
    access: '거래처', billing_mode: b.billing_mode === '후불' ? '후불' : '선불',
    lab_id: null, lab_name: '', lab_code: '',
  } });
}
