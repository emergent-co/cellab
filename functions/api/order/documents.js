// GET /api/order/documents → 내 모든 주문의 발행 문서 모아보기 (정산하기 화면용)
import { json, currentCustomer } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  const { results } = await env.DB.prepare(
    `SELECT d.id, d.type, d.doc_no, d.status, d.issue_date, d.sent_at, d.opened_at, d.created_at,
            o.id AS order_id, o.order_no, o.title, o.total_amount
       FROM documents d JOIN orders o ON o.id = d.order_id
      WHERE o.customer_id = ?
      ORDER BY d.id DESC LIMIT 200`
  ).bind(me.id).all();

  return json({ documents: results || [] });
}
