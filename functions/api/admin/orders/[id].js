// GET  /api/admin/orders/:id           → 상세(주문·고객·품목·문서·이력)
// PUT  /api/admin/orders/:id           → 주문 필드/품목 수정
// POST /api/admin/orders/:id {action}  → status 변경 등
import { json, isAdmin, needAdmin, kstISO, recalcOrder, logEvent, STATUSES } from '../../_lib.js';

export async function onRequest({ request, env, params }) {
  if (!isAdmin(request, env)) return needAdmin();

  const order = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(params.id).first();
  if (!order) return json({ error: 'not_found' }, 404);

  if (request.method === 'GET') {
    const customer = order.customer_id
      ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(order.customer_id).first()
      : null;
    const items = (await env.DB.prepare('SELECT * FROM order_items WHERE order_id=? ORDER BY seq, id').bind(order.id).all()).results || [];
    const docs = (await env.DB.prepare('SELECT * FROM documents WHERE order_id=? ORDER BY id DESC').bind(order.id).all()).results || [];
    const events = (await env.DB.prepare('SELECT * FROM doc_events WHERE order_id=? ORDER BY id DESC LIMIT 100').bind(order.id).all()).results || [];
    const queued = (await env.DB.prepare("SELECT * FROM outbox WHERE order_id=? AND status='대기' ORDER BY send_at").bind(order.id).all()).results || [];
    const profiles = order.customer_id
      ? (await env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id DESC').bind(order.customer_id).all()).results || []
      : [];
    const bill = order.bill_profile_id ? profiles.find((p) => p.id === order.bill_profile_id) || null : null;
    return json({ order, customer, items, documents: docs, events, queued, profiles, bill, statuses: STATUSES });
  }

  if (request.method === 'PUT') {
    const b = await request.json().catch(() => ({}));

    const sets = [], vals = [];
    for (const f of ['title', 'org_name', 'want_date', 'ship_address', 'request_note', 'admin_memo', 'status']) {
      if (b[f] !== undefined) { sets.push(`${f}=?`); vals.push(String(b[f])); }
    }
    if (sets.length) {
      sets.push('updated_at=?'); vals.push(kstISO(), order.id);
      await env.DB.prepare(`UPDATE orders SET ${sets.join(', ')} WHERE id=?`).bind(...vals).run();
    }

    if (Array.isArray(b.items)) {
      await env.DB.prepare('DELETE FROM order_items WHERE order_id=?').bind(order.id).run();
      let seq = 1;
      for (const it of b.items) {
        if (!String(it.name || '').trim()) continue;
        const qty = Number(it.qty) || 0;
        const up = Math.round(Number(it.unit_price) || 0);
        await env.DB.prepare(
          `INSERT INTO order_items (order_id, seq, product_id, name, spec, unit, qty, unit_price, amount, cost_price, note, link)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
        ).bind(
          order.id, seq++, it.product_id || null, String(it.name).trim(), String(it.spec || ''),
          String(it.unit || 'EA'), qty, up, Math.round(qty * up), Math.round(Number(it.cost_price) || 0),
          String(it.note || ''), String(it.link || '').trim() || null
        ).run();
      }
    }

    const sums = await recalcOrder(env, order.id);
    await logEvent(env, { order_id: order.id, action: 'updated', actor: 'admin', detail: b.status ? `상태→${b.status}` : '주문 수정' });
    const fresh = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(order.id).first();
    return json({ ok: true, order: fresh, sums });
  }

  if (request.method === 'POST') {
    const b = await request.json().catch(() => ({}));
    if (b.action === 'status' && STATUSES.includes(b.status)) {
      await env.DB.prepare('UPDATE orders SET status=?, updated_at=? WHERE id=?').bind(b.status, kstISO(), order.id).run();
      await logEvent(env, { order_id: order.id, action: 'status', actor: 'admin', detail: `${order.status} → ${b.status}` });
      return json({ ok: true, status: b.status });
    }
    if (b.action === 'bill') {
      await env.DB.prepare('UPDATE orders SET bill_profile_id=?, updated_at=? WHERE id=?')
        .bind(b.bill_profile_id || null, kstISO(), order.id).run();
      await logEvent(env, { order_id: order.id, action: 'bill_set', actor: 'admin',
        detail: b.bill_profile_id ? '계산서 발행 정보 지정' : '계산서 발행 정보 해제' });
      return json({ ok: true });
    }
    if (b.action === 'memo') {
      await env.DB.prepare('UPDATE orders SET admin_memo=?, updated_at=? WHERE id=?').bind(String(b.admin_memo || ''), kstISO(), order.id).run();
      return json({ ok: true });
    }
    return json({ error: 'unknown_action' }, 400);
  }

  return json({ error: 'method_not_allowed' }, 405);
}
