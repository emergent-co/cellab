// functions/api/admin/publish.js — "사이트 반영"(발행) 엔드포인트 · Basic Auth
//   POST /api/admin/publish   → 현재 등록가능 삼흥 퍼니스로 데이터시트 조각(HTML+JSON-LD) 생성 후 D1 published 테이블에 저장
//   GET  /api/admin/publish   → 마지막 발행 상태 조회
// 공개 페이지(/brands/sh-scientific/)의 _middleware 가 이 조각을 읽어 서버측에서 주입(크롤러/GEO 대응).

const REALM = 'rndsetup-admin';
const KEY = 'sh-datasheet';

export async function onRequest(context) {
  const { request, env } = context;
  if (!checkAuth(request, env)) {
    return json({ error: 'unauthorized' }, 401, { 'WWW-Authenticate': `Basic realm="${REALM}"` });
  }
  try {
    await ensureTable(env);
    if (request.method === 'POST') return await doPublish(env);
    if (request.method === 'GET') {
      const row = await env.DB.prepare('SELECT count, updated_at FROM published WHERE key = ?').bind(KEY).first();
      return json({ ok: true, published: row || null });
    }
    return json({ error: 'method_not_allowed' }, 405);
  } catch (e) {
    return json({ error: 'server_error', message: String(e && e.message || e) }, 500);
  }
}

function checkAuth(request, env) {
  const pw = env.ADMIN_PASSWORD || '';
  if (!pw) return false;
  const auth = request.headers.get('Authorization') || '';
  if (!auth.startsWith('Basic ')) return false;
  let d = ''; try { d = atob(auth.slice(6)); } catch { return false; }
  const i = d.indexOf(':');
  return (i >= 0 ? d.slice(i + 1) : d) === pw;
}

async function ensureTable(env) {
  await env.DB.prepare(
    'CREATE TABLE IF NOT EXISTS published (key TEXT PRIMARY KEY, html TEXT, count INTEGER, updated_at TEXT)'
  ).run();
}

async function doPublish(env) {
  const { results } = await env.DB.prepare(
    `SELECT model, opt_value, name, sobun, retail_price, image_url, product_url, lead_time,
            attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v
     FROM products
     WHERE brand='SH Scientific' AND status='등록가능'
     ORDER BY retail_price`
  ).all();

  const items = results.map(mapRow);
  const html = buildFragment(items);
  const updated_at = new Date().toISOString();

  await env.DB.prepare(
    'INSERT INTO published (key, html, count, updated_at) VALUES (?,?,?,?) ' +
    'ON CONFLICT(key) DO UPDATE SET html=excluded.html, count=excluded.count, updated_at=excluded.updated_at'
  ).bind(KEY, html, items.length, updated_at).run();

  return json({ ok: true, count: items.length, updated_at });
}

// ---- 분류 로직 ----
function attr(r, name) {
  for (const i of [1, 2, 3, 4]) if (r['attr' + i + '_n'] === name) return r['attr' + i + '_v'];
  return null;
}
function tnum(v) { if (!v) return null; const m = String(v).match(/(\d{3,4})/); return m ? parseInt(m[1], 10) : null; }
function tier(n) {
  if (!n || n < 900) return '';
  if (n <= 1100) return '1050';
  if (n <= 1300) return '1200';
  if (n <= 1650) return '1500';
  if (n <= 1700) return '1700';
  return '1800';
}
function ftype(sobun, name) {
  const s = (sobun || '') + ' ' + (name || '');
  if (/Rotary|Rotation|회전/.test(s)) return '회전튜브로';
  if (/CVD|Gas Flow/.test(s)) return 'CVD·가스플로';
  if (/Elevator|엘레베이터/.test(s)) return '엘레베이터';
  if (/튜브|Tube|관상/.test(s)) return '튜브전기로';
  if (/진공/.test(s)) return '진공전기로';
  return '박스전기로';
}
function mapRow(r) {
  const tmaxRaw = attr(r, '최고온도');
  const n = tnum(tmaxRaw);
  return {
    model: r.model, opt: r.opt_value || r.model, name: r.name, sobun: r.sobun,
    type: ftype(r.sobun, r.name),
    tmax: (n && n >= 900) ? tmaxRaw : null,
    tier: tier(n),
    vol: attr(r, '노내용량'), power: attr(r, '소비전력'), chamber: attr(r, '챔버치수'),
    price: r.retail_price, lead: r.lead_time, img: r.image_url, url: r.product_url,
  };
}

// ---- 렌더 ----
function esc(s) { return (s == null ? '' : String(s)).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function comma(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

function card(p) {
  const im = p.img ? `<img src="${esc(p.img)}" loading="lazy" alt="${esc(p.model)}">` : '';
  const tb = p.tmax ? `<span class="b t">${esc(p.tmax)}</span>` : '<span class="b y">온도확인중</span>';
  const yb = `<span class="b y">${esc(p.type)}</span>`;
  let sp = '';
  if (p.tmax) sp += `<div class="r"><span class="k">최고온도</span><span class="v">${esc(p.tmax)}</span></div>`;
  if (p.vol) sp += `<div class="r"><span class="k">노내용량</span><span class="v">${esc(p.vol)}</span></div>`;
  if (p.power) sp += `<div class="r"><span class="k">소비전력</span><span class="v">${esc(p.power)}</span></div>`;
  if (p.chamber) sp += `<div class="r"><span class="k">챔버</span><span class="v">${esc(p.chamber)}</span></div>`;
  const price = (p.price != null)
    ? `<div class="ds-price">₩${comma(p.price)} <small>부가세별도</small></div>`
    : '<div class="ds-price ask">가격 문의</div>';
  const text = esc(((p.opt || '') + ' ' + (p.model || '') + ' ' + (p.name || '')).toLowerCase());
  return `<article class="dscard" data-tier="${esc(p.tier)}" data-type="${esc(p.type)}" data-text="${text}">`
    + `<div class="dscard-im">${im}<div class="dscard-bdg">${tb}${yb}</div></div>`
    + `<div class="dscard-bd"><div class="dscard-mdl">${esc(p.opt || p.model)}</div>`
    + `<div class="dscard-nm">${esc(p.name)}</div>`
    + `<div class="dscard-sp">${sp}</div>`
    + `<div class="dscard-ft"><div>${price}<div class="ds-lead">납기 ${esc(p.lead || '-')}</div></div>`
    + `<a class="ds-detail" href="${esc(p.url)}" target="_blank" rel="noopener">상세 →</a></div>`
    + `</div></article>`;
}

function jsonLd(items) {
  const el = items.map((p, i) => {
    const prod = {
      "@type": "Product",
      "name": p.name || p.model,
      "sku": p.model,
      "brand": { "@type": "Brand", "name": "SH Scientific" },
      "category": "실험용 전기로/튜브퍼니스",
    };
    if (p.img) prod.image = p.img;
    if (p.url) prod.url = p.url;
    const props = [];
    if (p.tmax) props.push({ "@type": "PropertyValue", "name": "최고온도", "value": p.tmax });
    if (p.vol) props.push({ "@type": "PropertyValue", "name": "노내용량", "value": p.vol });
    if (props.length) prod.additionalProperty = props;
    if (p.price != null) prod.offers = { "@type": "Offer", "price": p.price, "priceCurrency": "KRW", "availability": "https://schema.org/InStock", "url": p.url || "https://rndsetup.com/brands/sh-scientific/catalog/" };
    return { "@type": "ListItem", "position": i + 1, "item": prod };
  });
  const obj = { "@context": "https://schema.org", "@type": "ItemList", "name": "삼흥에너지(SH Scientific) 퍼니스 데이터시트", "numberOfItems": items.length, "itemListElement": el };
  return `<script type="application/ld+json">${JSON.stringify(obj)}</script>`;
}

function buildFragment(items) {
  return items.map(card).join('') + jsonLd(items);
}

function json(obj, status = 200, extra = {}) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
  });
}
