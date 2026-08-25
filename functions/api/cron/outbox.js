// GET/POST /api/cron/outbox?key=<CRON_SECRET>  → 예약 발송 큐 처리
// Cloudflare Worker cron 트리거나 외부 스케줄러가 주기적으로 호출.
// 관리자 페이지를 열 때도 자동으로 한 번 돌아간다(모바일에서 확인만 해도 밀린 예약이 나감).
import { json, isAdmin } from '../_lib.js';
import { flushOutbox } from '../_send.js';

export async function onRequest({ request, env }) {
  const key = new URL(request.url).searchParams.get('key') || '';
  const ok = (env.CRON_SECRET && key === env.CRON_SECRET) || isAdmin(request, env);
  if (!ok) return json({ error: 'unauthorized' }, 401);

  try {
    const r = await flushOutbox(env, 20);
    return json({ ok: true, ...r });
  } catch (e) {
    return json({ error: 'flush_failed', message: String(e?.message || e) }, 500);
  }
}
