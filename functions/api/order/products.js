// GET /api/order/products?q= → 주문 입력 자동완성
//   내가(또는 같은 소속이) 전에 주문한 품목 + 자사 제품을 함께 찾는다.
//   제품명이 "SH Scientific 전기로 1200℃ 27L SH-FU-27MG"처럼 길어서
//   단어를 쪼개 모두 포함하는 것을 찾는다("전기로 1200" → 매칭).
import { json, currentCustomer } from '../_lib.js';
import { labMateIds } from './lab.js';

export async function onRequestGet({ request, env }) {
  const q = (new URL(request.url).searchParams.get('q') || '').trim();
  if (q.length < 1) return json({ items: [] });

  const words = q.split(/\s+/).filter(Boolean).slice(0, 4);
  const me = await currentCustomer(request, env);

  // ---- 1) 주문 이력 (내 소속 공유) ----
  let mine = [];
  if (me) {
    const ids = await labMateIds(env, me);      // 같은 실험실이면 함께 검색된다
    const cond = words.map(() => '(oi.name LIKE ? OR oi.spec LIKE ?)').join(' AND ');
    const binds = [];
    for (const w of words) binds.push(`%${w}%`, `%${w}%`);

    const r = await env.DB.prepare(
      `SELECT oi.name, oi.spec, oi.link, MAX(oi.id) AS last_id
         FROM order_items oi JOIN orders o ON o.id = oi.order_id
        WHERE o.customer_id IN (${ids.map(() => '?').join(',')}) AND ${cond}
        GROUP BY oi.name, oi.spec
        ORDER BY last_id DESC LIMIT 6`
    ).bind(...ids, ...binds).all();

    mine = (r.results || []).map((x) => ({
      src: 'mine', name: x.name, spec: x.spec || '', model: '', link: x.link || '',
    }));
  }

  // ---- 2) 자사 제품 ----
  const cond2 = words
    .map(() => '(name LIKE ? OR model LIKE ? OR sku LIKE ? OR sobun LIKE ? OR daebun LIKE ? OR brand LIKE ?)')
    .join(' AND ');
  const b2 = [];
  for (const w of words) { const L = `%${w}%`; b2.push(L, L, L, L, L, L); }

  const { results } = await env.DB.prepare(
    `SELECT id, brand, model, name, sobun
       FROM products
      WHERE ${cond2}
      ORDER BY (model LIKE ?) DESC, id
      LIMIT 14`
  ).bind(...b2, `${words[0]}%`).all();

  const cat = (results || []).map((p) => ({
    src: 'catalog', id: p.id, name: p.name || p.model, model: p.model || '',
    spec: p.model || '', brand: p.brand || '', sobun: p.sobun || '', link: '',
  }));

  return json({ items: mine.concat(cat) });
}
