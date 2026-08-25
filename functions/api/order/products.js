// GET /api/order/products?q= → 주문 입력 자동완성
//   내가(또는 같은 소속이) 전에 주문한 품목 + 자사 제품을 함께 찾는다.
//   ① 검색어를 단어로 쪼개고  ② 각 단어를 연관검색어(_syn.js)로 확장한 뒤
//   ③ "단어끼리는 AND, 같은 단어의 동의어끼리는 OR" 로 찾는다.
//      예) "퍼니스 1200" → (전기로|퍼니스|furnace|머플로…) AND (1200)
import { json, currentCustomer } from '../_lib.js';
import { labMateIds } from './lab.js';
import { expandQuery } from '../_syn.js';

// 제품 한 행을 검색용 한 덩어리 텍스트로
const P_BLOB = `(IFNULL(name,'')||' '||IFNULL(model,'')||' '||IFNULL(sku,'')||' '||IFNULL(sobun,'')||' '||IFNULL(daebun,'')||' '||IFNULL(brand,''))`;
// 주문이력 한 행
const I_BLOB = `(IFNULL(oi.name,'')||' '||IFNULL(oi.spec,''))`;

// 확장된 단어들을 (blob LIKE ? OR blob LIKE ? ...) 조건 + 바인드로
function likeGroup(blob, alts, binds) {
  const use = alts.slice(0, 12);
  binds.push(...use.map((a) => `%${a}%`));
  return '(' + use.map(() => `${blob} LIKE ?`).join(' OR ') + ')';
}

export async function onRequestGet({ request, env }) {
  const q = (new URL(request.url).searchParams.get('q') || '').trim();
  if (q.length < 1) return json({ items: [] });

  const groups = expandQuery(q);                 // [[원본, 동의어…], …]
  if (!groups.length) return json({ items: [] });
  const literals = groups.map((g) => g[0]);      // 사용자가 실제로 친 말
  const me = await currentCustomer(request, env);

  // ---- 1) 주문 이력 (내 소속 공유) ----
  let mine = [];
  if (me) {
    const ids = await labMateIds(env, me);
    const binds = [];
    const cond = groups.map((g) => likeGroup(I_BLOB, g, binds)).join(' AND ');
    try {
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
    } catch (e) { mine = []; }
  }

  // ---- 2) 자사 제품 ----
  const b2 = [];
  const cond2 = groups.map((g) => likeGroup(P_BLOB, g, b2)).join(' AND ');

  // 정렬: 사용자가 친 말 그대로 걸린 것 → 모델명이 그 말로 시작하는 것 순
  const rank = [];
  const rankSql = literals.map((w) => {
    rank.push(`%${w}%`);
    return `(CASE WHEN ${P_BLOB} LIKE ? THEN 1 ELSE 0 END)`;
  }).join(' + ');
  rank.push(`${literals[0]}%`);

  const { results } = await env.DB.prepare(
    `SELECT id, brand, model, name, sobun, daebun
       FROM products
      WHERE ${cond2}
      ORDER BY (${rankSql}) DESC, (IFNULL(model,'') LIKE ?) DESC, id
      LIMIT 14`
  ).bind(...b2, ...rank).all();

  const cat = (results || []).map((p) => ({
    src: 'catalog', id: p.id, name: p.name || p.model, model: p.model || '',
    spec: p.model || '', brand: p.brand || '', sobun: p.sobun || p.daebun || '', link: '',
  }));

  return json({ items: mine.concat(cat) });
}
