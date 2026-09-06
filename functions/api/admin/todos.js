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

  const sql = (withOrder) => `SELECT t.*, c.name AS contact, c.company, o.order_no, d.doc_no, d.type AS doc_type, d.access_token
       FROM todos t
       LEFT JOIN customers c ON c.id=t.customer_id
       LEFT JOIN orders    o ON o.id=t.order_id
       LEFT JOIN documents d ON d.id=t.document_id
       ${where}
      ORDER BY (t.status='완료') ASC, t.pinned DESC,
               ${withOrder ? "CASE WHEN t.sort_order IS NULL THEN 1 ELSE 0 END, t.sort_order," : ''}
               CASE WHEN t.due_date IS NULL OR t.due_date='' THEN 1 ELSE 0 END,
               t.due_date, t.id DESC
      LIMIT 200`;
  /* sort_order 는 나중에 붙인 칸이다. 코드를 먼저 올리고 ALTER 를 안 돌린 상태면
     이 쿼리가 통째로 터져 할 일 목록이 안 뜬다 — 그 경우 정렬만 빼고 한 번 더 시도한다. */
  let results;
  try {
    ({ results } = await env.DB.prepare(sql(true)).bind(...bind).all());
  } catch (e) {
    ({ results } = await env.DB.prepare(sql(false)).bind(...bind).all());
  }

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

  /* 목록에서 한 칸만 고칠 때 쓴다.
     전체 저장(id 를 담은 일반 POST)을 쓰면 보내지 않은 칸 — 메모·품목·거래처·마감일 — 이
     통째로 지워진다. 인라인 편집은 반드시 이 길로 온다. */
  if (b.action === 'patch') {
    if (!b.id) return json({ error: 'no_id' }, 400);
    const set = [], bind = [];
    if (b.title !== undefined) {
      const title = String(b.title || '').trim();
      if (!title) return json({ error: 'no_title', message: '할 일을 적어주세요.' }, 400);
      set.push('title=?'); bind.push(title.slice(0, 300));
    }
    if (b.kind !== undefined) {
      if (!TODO_KINDS.includes(b.kind)) return json({ error: 'bad_kind', message: '없는 종류입니다.' }, 400);
      set.push('kind=?'); bind.push(b.kind);
    }
    if (b.status !== undefined) {
      if (!STATUS.includes(b.status)) return json({ error: 'bad_status', message: '없는 상태입니다.' }, 400);
      set.push('status=?'); bind.push(b.status);
      set.push('done_at=?'); bind.push(b.status === '완료' ? now : null);
    }
    if (b.due_date !== undefined) { set.push('due_date=?'); bind.push(String(b.due_date || '').slice(0, 10) || null); }
    if (b.memo !== undefined) { set.push('memo=?'); bind.push(String(b.memo || '').slice(0, 2000)); }
    if (b.pinned !== undefined) { set.push('pinned=?'); bind.push(b.pinned ? 1 : 0); }
    if (!set.length) return json({ error: 'nothing', message: '고칠 내용이 없습니다.' }, 400);
    set.push('updated_at=?'); bind.push(now);
    const r = await env.DB.prepare(`UPDATE todos SET ${set.join(', ')} WHERE id=?`)
      .bind(...bind, b.id).run();
    if (!r?.meta || r.meta.changes !== 1) return json({ error: 'not_found', message: '없는 할 일입니다.' }, 404);
    return json({ ok: true, id: b.id });
  }

  /* 드래그로 바꾼 순서를 통째로 저장한다.
     화면에 보이는 순서 그대로 10, 20, 30… 을 다시 매긴다 — 값이 겹치면 순서가 흔들리기 때문이다.
     batch 라 전부 아니면 전무 — 절반만 반영돼 순서가 뒤섞이는 일이 없다. */
  if (b.action === 'reorder') {
    const list = (Array.isArray(b.order) ? b.order : []).slice(0, 300)
      .map((x) => ({ id: Number(x.id) || 0, pinned: x.pinned ? 1 : 0 }))
      .filter((x) => x.id);
    if (!list.length) return json({ error: 'no_order', message: '바꿀 순서가 없습니다.' }, 400);
    const seen = new Set();
    for (const x of list) {
      if (seen.has(x.id)) return json({ error: 'dup_id', message: '같은 할 일이 두 번 들어왔습니다.' }, 400);
      seen.add(x.id);
    }
    await env.DB.batch(list.map((x, k) => env.DB.prepare(
      'UPDATE todos SET pinned=?, sort_order=?, updated_at=? WHERE id=?')
      .bind(x.pinned, (k + 1) * 10, now, x.id)));
    return json({ ok: true, n: list.length });
  }

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
