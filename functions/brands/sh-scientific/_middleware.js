// functions/sh-scientific/_middleware.js
// /sh-scientific/catalog/ 및 그 하위 페이지에 D1의 소비자가를 서버측에서 주입한다.
// (JS 없이도 크롤러/AI가 제품·가격을 읽을 수 있게 → GEO 대응)
//
// 마크업 계약 — HTML 쪽에 아래 두 마커만 심으면 된다.
//   <td  data-d1="SH-CVD-50TG300">견적 문의</td>
//        → 해당 모델의 소비자가를 "5,846,000원" 으로 치환
//   <div data-d1-min="SH-CVD-50TG300,SH-CVD-80TG300,...">견적 문의</div>
//        → 나열된 모델 중 최저가를 "기본 바디 ₩5,846,000~" 으로 치환
//   <script type="application/ld+json" data-d1-ld="SH-CVD-50TG300,...">{...}</script>
//        → Product 의 offers 를 AggregateOffer(lowPrice·highPrice·offerCount)로 승격.
//          정적 원문은 가격 없는 Offer(견적 유도)라 D1이 죽어도 스키마가 유효하다.
//
// 안전 규칙 (수정 시 반드시 유지)
//   · SELECT 는 model, retail_price 만. supply_price(공급가)는 절대 조회하지 않는다.
//   · D1 조회 실패·값 없음 → 원문("견적 문의")을 그대로 남긴다.
//     틀린 숫자가 노출되는 것보다 숫자가 없는 편이 낫다.
//   · status 로 거르지 않는다. '이미지대기' 모델도 가격은 유효하다.
//   · model 이 D1에서 2행 이상이면 그 모델은 주입하지 않는다.
//     삼흥 일부 모델(SH-FU-4MS/11MS/22MS, 2MSU/4MSU/6MSU)은 온도등급(1700/1800/1900℃)이
//     같은 model 값을 공유해 가격이 서로 다르다 → 아무거나 고르면 틀린 가격이 노출된다.

const PREFIX = '/brands/sh-scientific';

export async function onRequest(context) {
  const res = await context.next();

  const path = new URL(context.request.url).pathname.replace(/\/+$/, '') || '/';
  if (path !== PREFIX && !path.startsWith(PREFIX + '/')) return res;

  const ct = res.headers.get('content-type') || '';
  if (!ct.includes('text/html')) return res;

  // 1) 본문에서 필요한 모델명 수집 (응답을 복제해서 읽는다)
  let html;
  try {
    html = await res.clone().text();
  } catch (_) {
    return res;
  }

  const models = collectModels(html);
  if (!models.size) return res;

  // 2) D1에서 해당 모델들의 소비자가만 조회
  let priceOf;
  try {
    priceOf = await fetchPrices(context.env, [...models]);
  } catch (_) {
    return res; // 조회 실패 → 정적 원문(견적 문의) 유지
  }
  if (!priceOf.size) return res;

  // 3) JSON-LD 의 offers 를 AggregateOffer 로 승격 (원문을 미리 파싱해 둔다)
  const ldPatched = patchLd(html, priceOf);

  // 4) 마커 치환
  const rewritten = new HTMLRewriter()
    .on('script[data-d1-ld]', {
      element(el) {
        if (ldPatched) el.setInnerContent(ldPatched, { html: true });
      },
    })
    .on('[data-d1]', {
      element(el) {
        const v = priceOf.get(el.getAttribute('data-d1'));
        if (v != null) el.setInnerContent(comma(v) + '원');
      },
    })
    .on('[data-d1-min]', {
      element(el) {
        const list = splitModels(el.getAttribute('data-d1-min'))
          .map((m) => priceOf.get(m))
          .filter((v) => v != null);
        if (!list.length) return;
        el.setInnerContent('기본 바디 ₩' + comma(Math.min(...list)) + '~');
        el.setAttribute('class', 'ds-price'); // .ask(견적문의 스타일) 해제 → 가격 스타일
      },
    })
    .transform(res);

  const out = new Response(rewritten.body, rewritten);
  // 엣지 캐시로 D1 히트를 줄이고 크롤러 응답 속도를 확보한다.
  // 가격 갱신은 최대 10분 뒤 반영(그동안 stale 재검증).
  out.headers.set('cache-control', 'public, s-maxage=600, stale-while-revalidate=3600');
  return out;
}

// ---- 본문에서 data-d1 / data-d1-min 값 수집 ----
function collectModels(html) {
  const set = new Set();
  const re = /data-d1(?:-min)?\s*=\s*"([^"]+)"/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    for (const s of splitModels(m[1])) set.add(s);
  }
  return set;
}

function splitModels(v) {
  return (v || '').split(',').map((s) => s.trim()).filter(Boolean);
}

// ---- Product JSON-LD 의 offers 승격 ----
// 실패하면 null 을 돌려주고, 호출부는 정적 원문(가격 없는 Offer)을 그대로 둔다.
function patchLd(html, priceOf) {
  const m = html.match(
    /<script[^>]*type="application\/ld\+json"[^>]*data-d1-ld="([^"]+)"[^>]*>([\s\S]*?)<\/script>/
  );
  if (!m) return null;

  const prices = splitModels(m[1])
    .map((k) => priceOf.get(k))
    .filter((v) => v != null);
  if (!prices.length) return null;

  let obj;
  try {
    obj = JSON.parse(m[2]);
  } catch (_) {
    return null;
  }
  if (!obj || typeof obj !== 'object') return null;

  const seller = obj.offers && obj.offers.seller;
  const url = obj.offers && obj.offers.url;
  obj.offers = {
    '@type': 'AggregateOffer',
    priceCurrency: 'KRW',
    lowPrice: Math.min(...prices),
    highPrice: Math.max(...prices),
    offerCount: prices.length,
    description: '기본 바디 기준 · 부가세 및 옵션(MFC·BPR·Safety Cover 등) 별도',
    availability: 'https://schema.org/InStock',
    ...(url ? { url } : {}),
    ...(seller ? { seller } : {}),
  };

  // </script> 로 스크립트가 조기 종료되지 않도록 '<' 를 이스케이프
  return JSON.stringify(obj).replace(/</g, '\\u003c');
}

// ---- D1 조회 (소비자가만) ----
async function fetchPrices(env, models) {
  const map = new Map();
  if (!env || !env.DB || !models.length) return map;

  const ambiguous = new Set(); // 같은 model 이 2행 이상 → 어느 가격인지 확정 불가
  const CHUNK = 50; // D1 바인딩 상한 여유
  for (let i = 0; i < models.length; i += CHUNK) {
    const part = models.slice(i, i + CHUNK);
    const holes = part.map(() => '?').join(',');
    const { results } = await env.DB
      .prepare(`SELECT model, retail_price FROM products WHERE model IN (${holes})`)
      .bind(...part)
      .all();
    for (const r of results || []) {
      if (!r || !r.model) continue;
      if (map.has(r.model) || ambiguous.has(r.model)) {
        // 두 번째 행이 나온 시점에 그 모델을 통째로 포기한다.
        ambiguous.add(r.model);
        map.delete(r.model);
        continue;
      }
      if (r.retail_price != null) map.set(r.model, r.retail_price);
    }
  }
  return map;
}

function comma(n) {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
