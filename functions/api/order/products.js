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

// 분류(소분+대분) / 제품명(품명+모델) — 어디에 걸렸는지로 순위를 가른다
const CAT_BLOB = `(IFNULL(sobun,'')||' '||IFNULL(daebun,''))`;
const NM_BLOB  = `(IFNULL(name,'')||' '||IFNULL(model,''))`;

// 확장된 단어들을 (blob LIKE ? OR blob LIKE ? ...) 조건 + 바인드로
function likeGroup(blob, alts, binds) {
  const use = alts.slice(0, 12);
  binds.push(...use.map((a) => `%${a}%`));
  return '(' + use.map(() => `${blob} LIKE ?`).join(' OR ') + ')';
}

/**
 * 점수 = 어디에 걸렸는지 + 사용자가 친 말 그대로인지.
 *   분류(대분/소분)에 걸린 것  → 그 카테고리의 대표 제품일 확률이 높다
 *   제품명에 친 말 그대로 있음 → 찾던 그 물건일 확률이 높다
 * 동점이면 분류명이 짧은 쪽(= 더 일반적인 카테고리)을 위로 올린다.
 */
function scoreSql(groups, literals, binds) {
  const parts = [];
  // 사용자가 친 말이 그대로 들어있는 단어 수 (단어당 2점)
  for (const w of literals) {
    binds.push(`%${w}%`);
    parts.push(`(CASE WHEN ${P_BLOB} LIKE ? THEN 2 ELSE 0 END)`);
  }
  // 첫 단어(= 찾는 물건의 머리말)를 제품명에 그대로 가지고 있으면 3점
  binds.push(`%${literals[0]}%`);
  parts.push(`(CASE WHEN ${NM_BLOB} LIKE ? THEN 3 ELSE 0 END)`);
  // 첫 단어(동의어 포함)가 분류에 걸리면 4점 — "퍼니스"는 전기로 카테고리가 먼저다
  const head = groups[0].slice(0, 10);
  binds.push(...head.map((a) => `%${a}%`));
  parts.push('(CASE WHEN (' + head.map(() => `${CAT_BLOB} LIKE ?`).join(' OR ') + ') THEN 4 ELSE 0 END)');
  return parts.join(' + ');
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
  const rank = [];
  const rankSql = scoreSql(groups, literals, rank);

  const { results } = await env.DB.prepare(
    `SELECT id, brand, model, name, sobun, daebun
       FROM products
      WHERE ${cond2}
      ORDER BY (${rankSql}) DESC, length(${CAT_BLOB}) ASC, id
      LIMIT 14`
  ).bind(...b2, ...rank).all();

  const cat = (results || []).map((p) => ({
    src: 'catalog', id: p.id, name: p.name || p.model, model: p.model || '',
    spec: p.model || '', brand: p.brand || '', sobun: p.sobun || p.daebun || '', link: '',
  }));

  return json({ items: mine.concat(cat) });
}
