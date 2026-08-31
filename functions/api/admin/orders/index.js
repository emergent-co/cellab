// GET  /api/admin/orders?stats=1
// GET  /api/admin/orders?status=&q=&page=&size=
// POST /api/admin/orders  → 관리자가 주문을 직접 만든다
//   시스템 쓰기 전에 오가던 거래를 옮겨 적을 때 필요하다. 거래일을 과거로 넣을 수 있다.
import { json, isAdmin, needAdmin, STATUSES, adminOK, kstISO, kstDate,
         nextOrderNo, recalcOrder, logEvent } from '../../_lib.js';

export async function onRequestGet({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  const p = new URL(request.url).searchParams;

  if (p.get('stats')) {
    const { results } = await env.DB.prepare('SELECT status, COUNT(*) AS c FROM orders GROUP BY status').all();
    const byStatus = {};
    for (const s of STATUSES) byStatus[s] = 0;
    for (const r of results || []) byStatus[r.status] = r.c;
    const total = (results || []).reduce((s, r) => s + r.c, 0);
    return json({ total, byStatus });
  }

  const status = p.get('status') || '';
  const q = (p.get('q') || '').trim();
  const size = Math.min(Number(p.get('size') || 30), 100);
  const page = Math.max(Number(p.get('page') || 1), 1);

  const where = [], vals = [];
  if (status && status !== '전체') { where.push('o.status = ?'); vals.push(status); }
  if (q) {
    where.push('(o.order_no LIKE ? OR o.title LIKE ? OR c.company LIKE ? OR c.name LIKE ?)');
    const like = `%${q}%`; vals.push(like, like, like, like);
  }
  const sql = `SELECT o.id, o.order_no, o.status, o.title, o.want_date, o.total_amount, o.created_at, o.updated_at,
                      c.company, c.name AS contact, c.phone, c.email
                 FROM orders o LEFT JOIN customers c ON c.id = o.customer_id
                ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
                ORDER BY o.id DESC LIMIT ? OFFSET ?`;
  const { results } = await env.DB.prepare(sql).bind(...vals, size, (page - 1) * size).all();
  return json({ orders: results || [], page, size });
}

export async function onRequestPost({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  const b = await request.json().catch(() => ({}));

  const customer = b.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(b.customer_id).first()
    : null;
  if (!customer) return json({ error: 'no_client', message: '거래처를 선택해주세요.' }, 400);

  const items = (Array.isArray(b.items) ? b.items : [])
    .map((i) => ({
      name: String(i.name || '').trim(),
      spec: String(i.spec || '').trim(),
      unit: String(i.unit || 'EA').trim() || 'EA',
      qty: Math.max(0, Number(i.qty) || 0),
      unit_price: Math.round(Number(i.unit_price) || 0),
      note: String(i.note || '').trim(),
    }))
    .filter((i) => i.name);
  if (!items.length) return json({ error: 'no_items', message: '품목을 1개 이상 넣어주세요.' }, 400);

  // 소속·납품지는 서류와 배송에 그대로 찍힌다. 비면 «—» 로 남아 나중에 아무도 못 채운다.
  //   ① 관리자가 적어 넣은 값 ② 거래처의 기본 납품지 ③ 거래처 기본 정보 순으로 채운다.
  const site = await env.DB.prepare(
    'SELECT * FROM sites WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1'
  ).bind(customer.id).first();
  // sites.address 는 저장할 때 이미 상세주소까지 합쳐 넣는다 — 여기서 또 붙이면 뒷부분이 두 번 찍힌다
  const siteAddr = site ? String(site.address || '').trim() : '';
  const orgName = String(b.org_name || (site && site.org_name) || customer.company || '').trim();
  const shipAddr = String(b.ship_address || siteAddr || customer.address || '').trim();

  const status = STATUSES.includes(b.status) ? b.status : '완료';
  // 거래일(created_at)을 직접 정한다 — 옮겨 적는 이력은 오늘 날짜가 아니다
  const day = String(b.trade_date || '').slice(0, 10) || kstDate();
  const at = /^\d{4}-\d{2}-\d{2}$/.test(day) ? `${day} 00:00:00` : kstISO();

  const order_no = await nextOrderNo(env);
  const r = await env.DB.prepare(
    `INSERT INTO orders (order_no, customer_id, status, title, org_name, ship_address,
                         request_note, admin_memo, orderer_name, orderer_email, orderer_phone,
                         manual, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?, 1, ?, ?)`
  ).bind(order_no, customer.id, status, String(b.title || '').trim() || '(제목 없음)',
         orgName, shipAddr,
         String(b.request_note || ''), String(b.admin_memo || ''),
         String(b.orderer_name || customer.name || ''),
         String(b.orderer_email || customer.work_email || customer.email || ''),
         String(b.orderer_phone || customer.phone || ''),
         at, kstISO()).run();

  const id = r.meta.last_row_id;
  let seq = 1;
  for (const it of items) {
    await env.DB.prepare(
      `INSERT INTO order_items (order_id, seq, name, spec, unit, qty, unit_price, amount, note)
       VALUES (?,?,?,?,?,?,?,?,?)`
    ).bind(id, seq++, it.name, it.spec, it.unit, it.qty, it.unit_price,
           Math.round(it.qty * it.unit_price), it.note).run();
  }
  const sums = await recalcOrder(env, id);
  await logEvent(env, { order_id: id, action: 'created', actor: 'admin',
    detail: `주문 직접 입력 ${order_no} · ${day} (${customer.company || customer.name || ''})` });
  return json({ ok: true, id, order_no, ...sums });
}
