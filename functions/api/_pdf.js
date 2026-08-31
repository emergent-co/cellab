// functions/api/_pdf.js — Cloudflare Browser Rendering REST API로 HTML → PDF
// 필요한 환경변수: CF_ACCOUNT_ID, CF_BROWSER_TOKEN (권한: Account · Browser Rendering · Edit)

export function pdfConfigured(env) {
  return !!(env.CF_ACCOUNT_ID && env.CF_BROWSER_TOKEN);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** @returns {Promise<ArrayBuffer>} PDF 바이트
 *  서류를 여러 장 연달아 만들면 429(Rate limit)가 난다. 몇 초 쉬었다 다시 걸면 대개 통과한다. */
export async function htmlToPdf(env, html, tries = 2) {
  if (!pdfConfigured(env)) {
    throw new Error('PDF 생성 미설정 — CF_ACCOUNT_ID / CF_BROWSER_TOKEN 환경변수가 필요합니다.');
  }
  const url = `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/browser-rendering/pdf`;
  let last = '';
  for (let i = 0; i < tries; i++) {
    if (i) await sleep(2000);                     // 한 번만, 2초
    const r = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.CF_BROWSER_TOKEN}`,
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        html,
        // networkidle0 은 다 받은 뒤에도 500ms 를 더 기다린다. 한 장에 몇 초씩 브라우저 시간을
        // 잡아먹어 무료 한도(하루 10분)를 금방 태운다. load 로 충분하다.
        gotoOptions: { waitUntil: 'load', timeout: 15000 },
        pdfOptions: { format: 'a4', printBackground: true, preferCSSPageSize: true },
      }),
    });
    if (r.ok) return await r.arrayBuffer();

    let detail = '';
    try { detail = (await r.text()).slice(0, 300); } catch { /* noop */ }
    last = r.status === 429
      ? 'PDF 생성 한도에 걸렸습니다 (429). Cloudflare 무료 플랜은 브라우저 사용이 하루 10분입니다 — '
        + '대시보드 Compute > Browser Run 에서 오늘 사용량을 확인해보세요. '
        + `원문: ${detail}`
      : `PDF 생성 실패 (${r.status}) ${detail}`;
    // 429(한도)·5xx(일시 장애)만 다시 시도한다. 401·400 은 다시 걸어도 똑같다.
    if (r.status !== 429 && r.status < 500) break;
  }
  throw new Error(last);
}

export function r2Ready(env) { return !!env.DOCS; }

// R2 버킷(env.DOCS)이 연결돼 있으면 캐시, 없으면 매번 새로 만든다.
// 한 번 만든 PDF 를 다시 쓰는 것이 무료 한도를 아끼는 가장 확실한 방법이다.
export async function getOrMakePdf(env, doc, html) {
  const key = `docs/${doc.id}-v${doc.version || 1}.pdf`;
  if (env.DOCS) {
    const hit = await env.DOCS.get(key);
    if (hit) return { bytes: await hit.arrayBuffer(), key, cached: true };
  }
  const bytes = await htmlToPdf(env, html);
  if (env.DOCS) {
    await env.DOCS.put(key, bytes, { httpMetadata: { contentType: 'application/pdf' } });
    // 어떤 문서가 캐시에 올라갔는지 남긴다 — 이게 없으면 R2 가 도는지 알 수가 없다
    try {
      await env.DB.prepare('UPDATE documents SET pdf_key=? WHERE id=?').bind(key, doc.id).run();
    } catch { /* 캐시 표시는 실패해도 발송을 막지 않는다 */ }
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
