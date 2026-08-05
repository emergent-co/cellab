// functions/api/products.js — 공개 제품 API
//   GET /api/products?status=&brand=&sobun=&q=&id=&page=&size=
//   응답: { page, size, count, items }
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
  if (q)      { where.push("(name LIKE ? OR model LIKE ?)"); binds.push("%" + q + "%", "%" + q + "%"); }
  const clause = where.length ? "WHERE " + where.join(" AND ") : "";

  const sql = `SELECT ${cols} FROM products ${clause} ORDER BY brand, sobun, model LIMIT ? OFFSET ?`;
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
