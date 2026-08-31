// functions/api/admin/clients.js — 거래처 관리
//   한 거래처를 통으로 본다: 기본정보 · 실험실 · 발행정보 · 주문 · 정산 · 문서 · 잔여금.
//   GET  ?q=&access=&mode=   목록
//   GET  ?id=<id>            상세
//   POST { id, action }      access · mode · memo · profile(연락처 수정)
//   권한(role)은 여기서 못 바꾼다 — DB에서 직접만. 화면을 타고 관리자가 번지지 않게.
import { json, needAdmin, adminOK, kstISO, logEvent } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

const ACCESS = ['승인', '대기', '거절'];
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

    const [profiles, orders, settles, docs, members, sum, led] = await Promise.all([
      env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id')
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, order_no, title, status, total_amount, created_at
                        FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, status, items_json, supply, vat, total, method, created_at
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

  // ---------------- 목록 ----------------
  const w = [], bind = [];
  const access = u.get('access');
  if (access && ACCESS.includes(access)) { w.push('c.access=?'); bind.push(access); }
  const mode = u.get('mode');
  if (mode === '후불' || mode === '선불') { w.push('c.billing_mode=?'); bind.push(mode); }
  const q = (u.get('q') || '').trim();
  if (q) {
    w.push('(c.name LIKE ? OR c.company LIKE ? OR c.email LIKE ? OR c.work_email LIKE ? OR c.phone LIKE ? OR l.name LIKE ?)');
    for (let i = 0; i < 6; i++) bind.push(`%${q}%`);
  }
  const where = w.length ? `WHERE ${w.join(' AND ')}` : '';

  const { results } = await env.DB.prepare(
    `SELECT c.id, c.name, c.company, c.phone, c.email, c.work_email, c.billing_mode,
            c.access, c.memo, c.created_at, l.name AS lab_name,
            COALESCE((SELECT SUM(o.total_amount) FROM orders o
                       WHERE o.customer_id=c.id AND o.status<>'취소'),0) AS spent,
            COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS paid,
            (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id AND o.status<>'취소') AS orders_n,
            (SELECT MAX(o.created_at) FROM orders o WHERE o.customer_id=c.id) AS last_order,
            (SELECT COUNT(*) FROM documents d WHERE d.customer_id=c.id) AS docs_n
       FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
       ${where}
      ORDER BY (c.access='대기') DESC, c.id DESC LIMIT 200`).bind(...bind).all();

  const clients = (results || []).map((r) => ({ ...r, due: (r.spent || 0) - (r.paid || 0) }));
  const stats = (await env.DB.prepare(
    `SELECT SUM(CASE WHEN access='승인' THEN 1 ELSE 0 END) AS ok,
            SUM(CASE WHEN access='대기' THEN 1 ELSE 0 END) AS wait,
            SUM(CASE WHEN access='거절' THEN 1 ELSE 0 END) AS no,
            SUM(CASE WHEN billing_mode='후불' THEN 1 ELSE 0 END) AS post,
            COUNT(*) AS all_ FROM customers`).first()) || {};
  return json({ clients, stats });
}

async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  if (!b.id) return json({ error: 'no_id' }, 400);
  const c = await env.DB.prepare('SELECT id, name, company FROM customers WHERE id=?').bind(b.id).first();
  if (!c) return json({ error: 'not_found' }, 404);
  const now = kstISO();
  const who = c.company || c.name || `#${c.id}`;

  if (b.action === 'access') {
    if (!ACCESS.includes(b.access)) return json({ error: 'bad_access' }, 400);
    await env.DB.prepare('UPDATE customers SET access=?, updated_at=? WHERE id=?').bind(b.access, now, c.id).run();
    await logEvent(env, { action: 'member_access', actor: 'admin', detail: `${who} 멤버십 ${b.access}` });
    return json({ ok: true, access: b.access });
  }

  if (b.action === 'mode') {
    const mode = b.billing_mode === '후불' ? '후불' : '선불';
    await env.DB.prepare('UPDATE customers SET billing_mode=?, updated_at=? WHERE id=?').bind(mode, now, c.id).run();
    await logEvent(env, { action: 'billing_mode', actor: 'admin', detail: `${who} ${mode} 전환` });
    return json({ ok: true, billing_mode: mode });
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
      `UPDATE customers SET name=?, company=?, phone=?, work_email=?, address=?, updated_at=? WHERE id=?`
    ).bind(String(b.name || ''), String(b.company || ''), String(b.phone || ''),
           email, String(b.address || ''), now, c.id).run();
    await logEvent(env, { action: 'client_edit', actor: 'admin', detail: `${who} 거래처 정보 수정` });
    return json({ ok: true });
  }

  return json({ error: 'unknown_action' }, 400);
}
