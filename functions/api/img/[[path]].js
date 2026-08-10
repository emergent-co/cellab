// functions/api/img/[[path]].js — 실험실닷컴(silhumsil.com) 이미지 프록시
//   배경: silhumsil이 외부 사이트에서의 이미지 핫링크를 차단(cross-site 요청 거부)
//   → 서버(Cloudflare)가 대신 받아 같은 도메인(/api/img/...)에서 서빙 + 엣지 캐시.
//   허용 경로: /web/ 이하 이미지 전용. 그 외 경로·비이미지 응답은 차단.
//   사용 예: /api/img/web/product/big/202305/xxx.jpg → https://silhumsil.com/web/product/big/202305/xxx.jpg

const ORIGIN = 'https://silhumsil.com';

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  // /api/img/ 이후를 인코딩 보존한 채 추출 (공백 %20 등 유지)
  const idx = url.pathname.indexOf('/api/img/');
  const path = url.pathname.slice(idx + '/api/img/'.length);

  if (!path.startsWith('web/')) {
    return new Response('Not found', { status: 404 });
  }

  const upstream = `${ORIGIN}/${path}${url.search || ''}`;

  let res;
  try {
    res = await fetch(upstream, {
      headers: {
        // 서버측 요청: 원 사이트 기준 same-site처럼 보이도록 최소 헤더 구성
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
        'Referer': ORIGIN + '/',
        'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
      },
      cf: { cacheTtl: 2592000, cacheEverything: true }, // 엣지 30일 캐시
    });
  } catch (e) {
    return new Response('Upstream error', { status: 502 });
  }

  if (!res.ok) {
    return new Response('Upstream ' + res.status, { status: res.status === 404 ? 404 : 502 });
  }

  const ct = res.headers.get('content-type') || '';
  if (!ct.startsWith('image/')) {
    return new Response('Not an image', { status: 415 });
  }

  return new Response(res.body, {
    status: 200,
    headers: {
      'content-type': ct,
      'cache-control': 'public, max-age=2592000, stale-while-revalidate=86400',
      'access-control-allow-origin': '*',
    },
  });
}
