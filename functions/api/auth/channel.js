// GET /api/auth/channel → 채널톡 회원 인증값
//   채널톡은 memberId 를 넘기면 memberHash(HMAC-SHA256)를 함께 요구한다.
//   해시 없이 memberId 만 넘기면 boot 이 401 로 죽고 상담창이 아예 안 열린다.
//   CHANNEL_SECRET 이 없으면 회원 식별을 포기하고 익명으로 붙인다(그래도 상담은 된다).
import { json, currentCustomer } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ ok: true, member: null });

  const secret = env.CHANNEL_SECRET || '';
  const memberId = 'rs-' + me.id;
  if (!secret) return json({ ok: true, member: null, memberId });

  try {
    const key = await crypto.subtle.importKey(
      'raw', new TextEncoder().encode(secret),
      { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    );
    const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(memberId));
    const hex = [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
    return json({ ok: true, member: { memberId, memberHash: hex } });
  } catch (e) {
    return json({ ok: true, member: null, memberId });
  }
}
