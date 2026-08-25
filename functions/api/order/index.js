// GET  /api/order        → 내 주문 목록
// POST /api/order        → 주문요청 생성
import { json, currentCustomer, kstISO, nextOrderNo, recalcOrder, logEvent } from '../_lib.js';

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      `SELECT id, order_no, status, title, want_date, total_amount, created_at
         FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 100`
    ).bind(me.id).all();
    return json({ orders: results || [] });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const items = Array.isArray(b.items) ? b.items.filter((i) => (i.name || '').trim()) : [];
  if (!items.length) return json({ error: 'no_items', message: '품목을 1개 이상 입력해주세요.' }, 400);
  if (!me.company || !me.biz_no) return json({ error: 'profile_required', message: '거래처 정보를 먼저 입력해주세요.' }, 400);

  const orderNo = await nextOrderNo(env);
  const now = kstISO();
  const r = await env.DB.prepare(
    `INSERT INTO orders (order_no, customer_id, status, title, want_date, ship_address, request_note, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?)`
  ).bind(
    orderNo, me.id, '요청접수',
    (b.title || '').trim() || items[0].name,
    (b.want_date || '').trim(),
    (b.ship_address || me.address || '').trim(),
    (b.request_note || '').trim(),
    now, now
  ).run();
  const orderId = r.meta.last_row_id;

  let seq = 1;
  for (const it of items) {
    const qty = Number(it.qty) > 0 ? Number(it.qty) : 1;
    await env.DB.prepare(
      `INSERT INTO order_items (order_id, seq, product_id, name, spec, unit, qty, unit_price, amount, note)
       VALUES (?,?,?,?,?,?,?,0,0,?)`
    ).bind(
      orderId, seq++, it.product_id || null,
      String(it.name).trim(), String(it.spec || '').trim(),
      String(it.unit || 'EA').trim(), qty, String(it.note || '').trim()
    ).run();
  }

  await recalcOrder(env, orderId);
  await logEvent(env, { order_id: orderId, action: 'created', actor: 'customer', detail: `주문요청 접수 (${items.length}개 품목)` });

  return json({ ok: true, order_no: orderNo, order_id: orderId });
}
