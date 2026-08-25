// GET /api/order/products?q=  → 주문폼 제품 자동완성 (판매 가능 제품만)
import { json } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const q = (new URL(request.url).searchParams.get('q') || '').trim();
  if (q.length < 1) return json({ items: [] });
  const like = `%${q}%`;
  const { results } = await env.DB.prepare(
    `SELECT id, brand, model, name, unit, sobun
       FROM products
      WHERE (model LIKE ? OR name LIKE ? OR sku LIKE ?)
      ORDER BY (model LIKE ?) DESC, id
      LIMIT 20`
  ).bind(like, like, like, `${q}%`).all();
  return json({ items: results || [] });
}
