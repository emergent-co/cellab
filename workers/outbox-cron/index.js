// 5분마다 예약 발송 큐를 비우라고 본체에 알린다.
// 하는 일은 이게 전부다 — 발송 로직은 전부 Pages 쪽에 있다.
export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(ping(env));
  },
  // 수동 확인용: 이 Worker 주소를 열면 즉시 한 번 돌린다.
  async fetch(request, env) {
    const r = await ping(env);
    return new Response(JSON.stringify(r), {
      headers: { 'content-type': 'application/json; charset=utf-8' },
    });
  },
};

async function ping(env) {
  if (!env.CRON_SECRET) return { ok: false, error: 'CRON_SECRET 미설정' };
  const url = `${env.TARGET}?key=${encodeURIComponent(env.CRON_SECRET)}`;
  try {
    const res = await fetch(url, { headers: { 'user-agent': 'rndsetup-outbox-cron' } });
    const body = await res.text();
    return { ok: res.ok, status: res.status, body: body.slice(0, 300) };
  } catch (e) {
    return { ok: false, error: String(e?.message || e) };
  }
}
