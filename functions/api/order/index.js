// GET  /api/order        → 내 주문 목록
// POST /api/order        → 주문요청 생성
import { json, currentCustomer, kstISO, nextOrderNo, recalcOrder, logEvent } from '../_lib.js';

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      `SELECT o.id, o.order_no, o.status, o.title, o.org_name, o.total_amount, o.created_at,
              (SELECT COUNT(*) FROM order_items i WHERE i.order_id=o.id) AS item_count
         FROM orders o WHERE o.customer_id=? ORDER BY o.id DESC LIMIT 100`
    ).bind(me.id).all();
    return json({ orders: results || [] });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const items = Array.isArray(b.items) ? b.items.filter((i) => (i.name || '').trim()) : [];
  if (!items.length) return json({ error: 'no_items', message: '품목을 1개 이상 입력해주세요.' }, 400);
  // 납품지는 반드시 등록된 것 중에서 고른다 (주소 정확도 때문에 직접 입력을 받지 않는다)
  if (!b.site_id) {
    return json({ error: 'no_site', message: '납품지를 먼저 추가해주세요.' }, 400);
  }
  const site = await env.DB.prepare('SELECT * FROM sites WHERE id=? AND customer_id=?')
    .bind(b.site_id, me.id).first();
  if (!site) return json({ error: 'no_site', message: '납품지를 찾을 수 없습니다.' }, 400);
  const org = site.org_name || '';
  const ship = site.address || '';

  // 제목은 받지 않고 품목에서 만든다 — "첫 품목 외 N건"
  const title = items.length > 1
    ? `${String(items[0].name).trim()} 외 ${items.length - 1}건`
    : String(items[0].name).trim();
  // 사업자정보는 정산 시점에 받는다 — 여기서 요구하지 않는다.

  const orderNo = await nextOrderNo(env);
  const now = kstISO();
  const r = await env.DB.prepare(
    `INSERT INTO orders (order_no, customer_id, status, title, org_name, want_date, ship_address, request_note, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?)`
  ).bind(
    orderNo, me.id, '요청접수',
    title,
    org,
    '',
    ship || me.address || '',
    '',
    now, now
  ).run();
  const orderId = r.meta.last_row_id;

  let seq = 1;
  for (const it of items) {
    const qty = Number(it.qty) > 0 ? Number(it.qty) : 1;
    await env.DB.prepare(
      `INSERT INTO order_items (order_id, seq, product_id, name, spec, unit, qty, unit_price, amount, note, link)
       VALUES (?,?,?,?,?,?,?,0,0,?,?)`
    ).bind(
      orderId, seq++, it.product_id || null,
      String(it.name).trim(), String(it.spec || '').trim(),
      'EA', qty, String(it.note || '').trim(),
      String(it.link || '').trim() || null
    ).run();
  }

  await env.DB.prepare(
    "UPDATE customers SET company=?, address=COALESCE(NULLIF(?,''), address), updated_at=? WHERE id=?"
  ).bind(org, ship, kstISO(), me.id).run();

  const def = await env.DB.prepare(
    'SELECT id FROM bill_profiles WHERE customer_id=? AND is_default=1'
  ).bind(me.id).first();
  if (def) await env.DB.prepare('UPDATE orders SET bill_profile_id=? WHERE id=?').bind(def.id, orderId).run();

  await recalcOrder(env, orderId);
  await logEvent(env, { order_id: orderId, action: 'created', actor: 'customer', detail: `주문요청 접수 (${items.length}개 품목)` });

  return json({ ok: true, order_no: orderNo, order_id: orderId });
}
