// functions/api/admin/todos.js — 관리자 할 일 목록
//   종류를 '견적발행'으로 적어두면 목록에서 버튼 한 번으로 견적서 준비 화면으로 넘어간다.
//   GET    ?status=&kind=&q=
//   POST   { id?, title, kind, status, due_date, customer_id, order_id, settlement_id, items, memo, pinned }
//   POST   { id, action:'done'|'undone'|'delete' }
//   POST   { id, action:'link_doc', document_id }   문서를 발행하면 그 할 일을 닫는다
import { json, needAdmin, adminOK, kstISO, kstDate } from '../_lib.js';

export const TODO_KINDS = ['견적발행', '거래명세서', '세금계산서', '연락', '발주·배송', '입금확인', '기타'];
const STATUS = ['할일', '진행중', '완료'];
const safe = (s) => { try { return JSON.parse(s || 'null'); } catch { return null; } };

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  if (request.method === 'GET') return get(request, env);
  if (request.method === 'POST') return post(request, env);
  return json({ error: 'method_not_allowed' }, 405);
}

async function get(request, env) {
  const u = new URL(request.url).searchParams;
  const w = [], bind = [];
  const status = u.get('status');
  if (status && STATUS.includes(status)) { w.push('t.status=?'); bind.push(status); }
  else if (u.get('open')) w.push("t.status<>'완료'");
  const kind = u.get('kind');
  if (kind && TODO_KINDS.includes(kind)) { w.push('t.kind=?'); bind.push(kind); }
  const q = (u.get('q') || '').trim();
  // ?와 ?1을 섞으면 번호가 어긋나 엉뚱한 값이 묶인다 — 자리표시자는 ?로 통일한다.
  if (q) { w.push('(t.title LIKE ? OR t.memo LIKE ? OR c.name LIKE ? OR c.company LIKE ?)');
           bind.push(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`); }
  const where = w.length ? `WHERE ${w.join(' AND ')}` : '';

  const { results } = await env.DB.prepare(
    `SELECT t.*, c.name AS contact, c.company, o.order_no, d.doc_no, d.type AS doc_type, d.access_token
       FROM todos t
       LEFT JOIN customers c ON c.id=t.customer_id
       LEFT JOIN orders    o ON o.id=t.order_id
       LEFT JOIN documents d ON d.id=t.document_id
       ${where}
      ORDER BY (t.status='완료') ASC, t.pinned DESC,
               CASE WHEN t.due_date IS NULL OR t.due_date='' THEN 1 ELSE 0 END,
               t.due_date, t.id DESC
      LIMIT 200`).bind(...bind).all();

  const today = kstDate();
  const todos = (results || []).map((t) => {
    const { items_json, ...rest } = t;
    return {
      ...rest,
      items: safe(items_json) || [],
      overdue: !!(t.due_date && t.status !== '완료' && t.due_date < today),
      view: t.document_id ? `/doc/${t.document_id}?t=${t.access_token || ''}` : '',
    };
  });

  const st = (await env.DB.prepare(
    `SELECT SUM(CASE WHEN status='할일'  THEN 1 ELSE 0 END) AS todo,
            SUM(CASE WHEN status='진행중' THEN 1 ELSE 0 END) AS doing,
            SUM(CASE WHEN status='완료'  THEN 1 ELSE 0 END) AS done,
            SUM(CASE WHEN status<>'완료' AND due_date IS NOT NULL AND due_date<>'' AND due_date<? THEN 1 ELSE 0 END) AS overdue,
            COUNT(*) AS all_ FROM todos`).bind(today).first()) || {};
  return json({ todos, stats: st, kinds: TODO_KINDS });
}

async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  const now = kstISO();

  if (b.action === 'delete') {
    if (!b.id) return json({ error: 'no_id' }, 400);
    await env.DB.prepare('DELETE FROM todos WHERE id=?').bind(b.id).run();
    return json({ ok: true, deleted: true });
  }

  if (b.action === 'done' || b.action === 'undone') {
    if (!b.id) return json({ error: 'no_id' }, 400);
    const done = b.action === 'done';
    await env.DB.prepare('UPDATE todos SET status=?, done_at=?, updated_at=? WHERE id=?')
      .bind(done ? '완료' : '할일', done ? now : null, now, b.id).run();
    return json({ ok: true });
  }

  // 문서를 발행하면 그 할 일을 닫는다 — 두 번 만들지 않게 한다
  if (b.action === 'link_doc') {
    if (!b.id || !b.document_id) return json({ error: 'no_id' }, 400);
    await env.DB.prepare("UPDATE todos SET document_id=?, status='완료', done_at=?, updated_at=? WHERE id=?")
      .bind(b.document_id, now, now, b.id).run();
    return json({ ok: true });
  }

  const title = String(b.title || '').trim();
  if (!title) return json({ error: 'no_title', message: '할 일을 적어주세요.' }, 400);
  const kind = TODO_KINDS.includes(b.kind) ? b.kind : '기타';
  const status = STATUS.includes(b.status) ? b.status : '할일';
  const items = Array.isArray(b.items)
    ? b.items.map((i) => ({ name: String(i.name || '').trim(),
                            qty: Math.max(1, Number(i.qty) || 1),
                            price: Math.round(Number(i.price) || 0) }))
             .filter((i) => i.name).slice(0, 40)
    : null;
  const due = String(b.due_date || '').slice(0, 10) || null;

  if (b.id) {
    await env.DB.prepare(
      `UPDATE todos SET title=?, kind=?, status=?, due_date=?, customer_id=?, order_id=?, settlement_id=?,
                        items_json=?, memo=?, pinned=?, done_at=?, updated_at=? WHERE id=?`
    ).bind(title, kind, status, due, b.customer_id || null, b.order_id || null, b.settlement_id || null,
           items ? JSON.stringify(items) : null, String(b.memo || ''), b.pinned ? 1 : 0,
           status === '완료' ? now : null, now, b.id).run();
    return json({ ok: true, id: b.id });
  }

  const r = await env.DB.prepare(
    `INSERT INTO todos (title, kind, status, due_date, customer_id, order_id, settlement_id,
                        items_json, memo, pinned, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(title, kind, status, due, b.customer_id || null, b.order_id || null, b.settlement_id || null,
         items ? JSON.stringify(items) : null, String(b.memo || ''), b.pinned ? 1 : 0, now, now).run();
  return json({ ok: true, id: r.meta.last_row_id });
}
