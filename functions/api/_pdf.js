// functions/api/_pdf.js — Cloudflare Browser Rendering REST API로 HTML → PDF
// 필요한 환경변수: CF_ACCOUNT_ID, CF_BROWSER_TOKEN (권한: Account · Browser Rendering · Edit)

export function pdfConfigured(env) {
  return !!(env.CF_ACCOUNT_ID && env.CF_BROWSER_TOKEN);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** @returns {Promise<ArrayBuffer>} PDF 바이트
 *  서류를 여러 장 연달아 만들면 429(Rate limit)가 난다. 몇 초 쉬었다 다시 걸면 대개 통과한다. */
export async function htmlToPdf(env, html, tries = 3) {
  if (!pdfConfigured(env)) {
    throw new Error('PDF 생성 미설정 — CF_ACCOUNT_ID / CF_BROWSER_TOKEN 환경변수가 필요합니다.');
  }
  const url = `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/browser-rendering/pdf`;
  let last = '';
  for (let i = 0; i < tries; i++) {
    if (i) await sleep(i * 2500);                 // 2.5초 → 5초
    const r = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.CF_BROWSER_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        html,
        gotoOptions: { waitUntil: 'networkidle0', timeout: 25000 },
        pdfOptions: { format: 'a4', printBackground: true, preferCSSPageSize: true },
      }),
    });
    if (r.ok) return await r.arrayBuffer();

    let detail = '';
    try { detail = (await r.text()).slice(0, 300); } catch { /* noop */ }
    last = `PDF 생성 실패 (${r.status}) ${detail}`;
    // 429(한도)·5xx(일시 장애)만 다시 시도한다. 401·400 은 다시 걸어도 똑같다.
    if (r.status !== 429 && r.status < 500) break;
  }
  throw new Error(last);
}

// R2 버킷(env.DOCS)이 연결돼 있으면 캐시, 없으면 매번 생성.
export async function getOrMakePdf(env, doc, html) {
  const key = `docs/${doc.id}-v${doc.version || 1}.pdf`;
  if (env.DOCS) {
    const hit = await env.DOCS.get(key);
    if (hit) return { bytes: await hit.arrayBuffer(), key, cached: true };
  }
  const bytes = await htmlToPdf(env, html);
  if (env.DOCS) {
    await env.DOCS.put(key, bytes, { httpMetadata: { contentType: 'application/pdf' } });
  }
  return { bytes, key, cached: false };
}

export function b64(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);
  let s = '';
  const CH = 0x8000;
  for (let i = 0; i < bytes.length; i += CH) {
    s += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
  }
  return btoa(s);
}
