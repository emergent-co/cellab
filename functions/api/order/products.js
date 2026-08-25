// GET /api/order/products?q=  → 주문폼 제품 자동완성 (판매 가능 제품만)
import { json, currentCustomer } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const q = (new URL(request.url).searchParams.get('q') || '').trim();
  if (q.length < 1) return json({ items: [] });
  const like = `%${q}%`;

  // 1) 내가 전에 주문한 품목 — 반복 주문이 많으므로 위에 둔다
  const me = await currentCustomer(request, env);
  let mine = [];
  if (me) {
    const r = await env.DB.prepare(
      `SELECT oi.name, oi.spec, oi.link, MAX(oi.id) AS last_id
         FROM order_items oi JOIN orders o ON o.id = oi.order_id
        WHERE o.customer_id = ? AND oi.name LIKE ?
        GROUP BY oi.name, oi.spec
        ORDER BY last_id DESC LIMIT 6`
    ).bind(me.id, like).all();
    mine = (r.results || []).map((x) => ({
      src: 'mine', name: x.name, model: x.spec || '', spec: x.spec || '', link: x.link || '',
    }));
  }

  // 2) 자사 제품
  const { results } = await env.DB.prepare(
    `SELECT id, brand, model, name, sobun
       FROM products
      WHERE (model LIKE ? OR name LIKE ? OR sku LIKE ?)
      ORDER BY (model LIKE ?) DESC, id
      LIMIT 14`
  ).bind(like, like, like, `${q}%`).all();
  const cat = (results || []).map((p) => ({
    src: 'catalog', id: p.id, name: p.name || p.model, model: p.model || '',
    spec: p.model || '', brand: p.brand || '', sobun: p.sobun || '', link: '',
  }));

  return json({ items: mine.concat(cat) });
}
