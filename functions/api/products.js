// functions/api/products.js — 공개 제품 API
//   GET /api/products?status=&brand=&sobun=&q=&id=&page=&size=
//   응답: { page, size, count, items }
//   q= 는 연관검색어(_syn.js)로 확장해서 찾는다. ("퍼니스" → 전기로/furnace/머플로…)
import { expandQuery } from './_syn.js';

const BLOB = `(IFNULL(name,'')||' '||IFNULL(model,'')||' '||IFNULL(sku,'')||' '||IFNULL(sobun,'')||' '||IFNULL(daebun,'')||' '||IFNULL(brand,''))`;
const CAT_BLOB = `(IFNULL(sobun,'')||' '||IFNULL(daebun,''))`;
const NM_BLOB  = `(IFNULL(name,'')||' '||IFNULL(model,''))`;

export async function onRequest(context) {
  const { request, env } = context;
  const p = new URL(request.url).searchParams;
  const id = p.get("id");
  const brand = p.get("brand"), sobun = p.get("sobun"), status = p.get("status"), q = p.get("q");
  const page = Math.max(1, parseInt(p.get("page") || "1", 10));
  const size = Math.min(200, Math.max(1, parseInt(p.get("size") || "24", 10)));

  const cols = `id,sku,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,
                unit,supply_price,retail_price,list_price,image_url,product_url,lead_time,cert,stock,
                attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v,status`;

  // 단일 상세
  if (id) {
    const row = await env.DB.prepare(`SELECT ${cols} FROM products WHERE id = ?`).bind(id).first();
    return json({ page: 1, size: 1, count: row ? 1 : 0, items: row ? [row] : [] });
  }

  const where = [], binds = [];
  if (brand)  { where.push("brand = ?");  binds.push(brand); }
  if (sobun)  { where.push("sobun = ?");  binds.push(sobun); }
  if (status) { where.push("status = ?"); binds.push(status); }
  const qGroups = q ? expandQuery(q) : [];
  if (qGroups.length) {
    // 단어끼리는 AND, 같은 단어의 동의어끼리는 OR
    for (const alts of qGroups) {
      const use = alts.slice(0, 12);
      where.push("(" + use.map(() => `${BLOB} LIKE ?`).join(" OR ") + ")");
      for (const a of use) binds.push("%" + a + "%");
    }
  }
  const clause = where.length ? "WHERE " + where.join(" AND ") : "";

  // 검색어가 있으면 관련도 순으로 — 분류에 걸린 것, 친 말 그대로 걸린 것이 위로
  let order = "brand, sobun, model";
  if (qGroups.length) {
    const rank = [];
    const parts = [];
    for (const g of qGroups) {
      rank.push("%" + g[0] + "%");
      parts.push(`(CASE WHEN ${BLOB} LIKE ? THEN 2 ELSE 0 END)`);
    }
    rank.push("%" + qGroups[0][0] + "%");
    parts.push(`(CASE WHEN ${NM_BLOB} LIKE ? THEN 3 ELSE 0 END)`);
    const head = qGroups[0].slice(0, 10);
    for (const a of head) rank.push("%" + a + "%");
    parts.push("(CASE WHEN (" + head.map(() => `${CAT_BLOB} LIKE ?`).join(" OR ") + ") THEN 4 ELSE 0 END)");
    order = `(${parts.join(" + ")}) DESC, length(${CAT_BLOB}) ASC, id`;
    binds.push(...rank);
  }

  const sql = `SELECT ${cols} FROM products ${clause} ORDER BY ${order} LIMIT ? OFFSET ?`;
  binds.push(size, (page - 1) * size);
  const { results } = await env.DB.prepare(sql).bind(...binds).all();

  return json({ page, size, count: results.length, items: results }, {
    "cache-control": "public, max-age=300",
  });
}

function json(obj, extra = {}) {
  return new Response(JSON.stringify(obj), {
    headers: { "content-type": "application/json; charset=utf-8", ...extra },
  });
}
