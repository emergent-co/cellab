// GET /api/order/recent → 같은 소속이 구매한 품목 (연구실 단위 공유)
//   같은 연구실 사람이 이미 산 물건을 다시 찾아 헤매지 않게 한다.
import { json, currentCustomer, memberGate} from '../_lib.js';
import { labMateIds } from './lab.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);
  const gate = memberGate(me); if (gate) return gate;

  const ids = await labMateIds(env, me);
  const where = `o.customer_id IN (${ids.map(() => '?').join(',')})`;
  const binds = ids;

  const { results } = await env.DB.prepare(
    `SELECT oi.name, oi.spec, oi.link, oi.qty,
            MAX(oi.id) AS last_id,
            MAX(o.created_at) AS last_at,
            MAX(o.org_name) AS org_name,
            MAX(c.name) AS orderer,
            COUNT(*) AS times
       FROM order_items oi
       JOIN orders o    ON o.id = oi.order_id
       JOIN customers c ON c.id = o.customer_id
      WHERE ${where} AND o.status <> '취소'
      GROUP BY oi.name, oi.spec
      ORDER BY last_id DESC
      LIMIT 60`
  ).bind(...binds).all();

  return json({ items: results || [] });
}
