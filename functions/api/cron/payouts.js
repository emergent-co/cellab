// GET /api/cron/payouts?key=<CRON_SECRET>  → 매월 1일, 지난달 용역비 지급내역을 세무사에게 보낸다.
// Pages 에는 cron 이 없다. 스케줄러(Worker)가 부르거나, 관리자가 화면을 열 때 한 번 돌아간다.
// 같은 달을 두 번 보내지 않는다 — payout_shares 에 그 달 기록이 있으면 건너뛴다.
import { json, adminOK, kstDate } from '../_lib.js';

export async function onRequest({ request, env }) {
  const u = new URL(request.url);
  const key = u.searchParams.get('key') || '';
  const ok = (env.CRON_SECRET && key === env.CRON_SECRET) || (await adminOK(request, env));
  if (!ok) return json({ error: 'unauthorized' }, 401);

  const today = kstDate();                       // YYYY-MM-DD (KST)
  const force = u.searchParams.get('force') === '1';
  if (!force && !today.endsWith('-01')) return json({ ok: true, skipped: '1일이 아닙니다', today });

  // 지난달
  const d = new Date(`${today}T00:00:00Z`);
  d.setUTCDate(0);
  const ym = d.toISOString().slice(0, 7);

  const sent = await env.DB.prepare('SELECT id FROM payout_shares WHERE ym=? LIMIT 1').bind(ym).first();
  if (sent && !force) return json({ ok: true, skipped: '이미 보냈습니다', ym });

  const n = await env.DB.prepare(
    'SELECT COUNT(*) AS n FROM payouts WHERE substr(paid_at,1,7)=?').bind(ym).first();
  if (!n || !n.n) return json({ ok: true, skipped: '지급 기록이 없습니다', ym });

  // 발송 로직은 한 곳에만 둔다 — 화면의 「보내기」와 같은 경로를 그대로 부른다
  const r = await fetch(`${u.origin}/api/admin/payouts`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      // 관리자 세션이 없는 스케줄러 호출을 위해 Basic 을 그대로 넘긴다
      ...(request.headers.get('authorization') ? { authorization: request.headers.get('authorization') } : {}),
      ...(request.headers.get('cookie') ? { cookie: request.headers.get('cookie') } : {}),
    },
    body: JSON.stringify({ action: 'share', ym }),
  }).then((x) => x.json()).catch((e) => ({ error: String(e?.message || e) }));

  return json({ ok: !!r.ok, ym, ...r });
}
