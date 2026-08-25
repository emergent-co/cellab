// GET  /api/order/:id            → 내 주문 상세 (품목 + 문서 + 이력)
// POST /api/order/:id  {action}  → approve(견적승인) / cancel(요청취소)
import { json, currentCustomer, kstISO, logEvent } from '../_lib.js';

export async function onRequest({ request, env, params }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  const order = await env.DB.prepare('SELECT * FROM orders WHERE id=? AND customer_id=?')
    .bind(params.id, me.id).first();
  if (!order) return json({ error: 'not_found' }, 404);

  if (request.method === 'GET') {
    const items = (await env.DB.prepare('SELECT id, seq, name, spec, unit, qty, unit_price, amount, note FROM order_items WHERE order_id=? ORDER BY seq').bind(order.id).all()).results || [];
    const docs = (await env.DB.prepare('SELECT id, type, doc_no, version, status, issue_date, pdf_key, created_at FROM documents WHERE order_id=? ORDER BY id DESC').bind(order.id).all()).results || [];
    const events = (await env.DB.prepare("SELECT action, channel, actor, result, detail, created_at FROM doc_events WHERE order_id=? AND actor<>'admin_internal' ORDER BY id DESC LIMIT 50").bind(order.id).all()).results || [];
    return json({ order, items, documents: docs, events });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  if (b.action === 'approve') {
    if (order.status !== '견적발송') return json({ error: 'bad_status', message: '견적 발송 상태에서만 승인할 수 있습니다.' }, 400);
    await env.DB.prepare('UPDATE orders SET status=?, updated_at=? WHERE id=?').bind('견적승인', kstISO(), order.id).run();
    await env.DB.prepare("UPDATE documents SET status='승인됨', updated_at=? WHERE order_id=? AND type='quote'").bind(kstISO(), order.id).run();
    await logEvent(env, { order_id: order.id, action: 'approved', actor: 'customer', detail: '고객이 견적을 승인함' });
    return json({ ok: true, status: '견적승인' });
  }

  if (b.action === 'cancel') {
    if (['납품완료', '계산서발행', '완료'].includes(order.status)) return json({ error: 'bad_status', message: '진행된 주문은 취소할 수 없습니다. 담당자에게 연락해주세요.' }, 400);
    await env.DB.prepare('UPDATE orders SET status=?, updated_at=? WHERE id=?').bind('취소', kstISO(), order.id).run();
    await logEvent(env, { order_id: order.id, action: 'cancelled', actor: 'customer', detail: (b.reason || '고객 취소') });
    return json({ ok: true, status: '취소' });
  }

  return json({ error: 'unknown_action' }, 400);
}
