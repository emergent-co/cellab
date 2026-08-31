// GET/POST /api/cron/outbox?key=<CRON_SECRET>  → 예약 발송 큐 처리
// Cloudflare Worker cron 트리거나 외부 스케줄러가 주기적으로 호출.
// 관리자 페이지를 열 때도 자동으로 한 번 돌아간다(모바일에서 확인만 해도 밀린 예약이 나감).
import { json, adminOK } from '../_lib.js';
import { flushOutbox } from '../_send.js';

export async function onRequest({ request, env }) {
  const key = new URL(request.url).searchParams.get('key') || '';
  // CRON_SECRET 을 든 스케줄러, 또는 로그인한 관리자(세션 쿠키)면 돌릴 수 있다.
  // 전에는 Basic Auth 만 봐서, 브라우저로 로그인한 관리자도 큐를 못 돌렸다.
  const ok = (env.CRON_SECRET && key === env.CRON_SECRET) || (await adminOK(request, env));
  if (!ok) return json({ error: 'unauthorized' }, 401);

  try {
    const r = await flushOutbox(env, 20);
    return json({ ok: true, ...r });
  } catch (e) {
    return json({ error: 'flush_failed', message: String(e?.message || e) }, 500);
  }
}
