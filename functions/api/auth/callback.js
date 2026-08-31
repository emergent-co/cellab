// GET /api/auth/callback?code=...&state=next  → 토큰 교환 → 고객 upsert → 세션 쿠키
import { kstISO, createSession, sessionCookie } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const next = decodeURIComponent(url.searchParams.get('state') || '/member/');
  if (!code) return Response.redirect(`${url.origin}/member/?err=no_code`, 302);

  const redirectUri = `${url.origin}/api/auth/callback`;
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: env.KAKAO_REST_KEY || '',
    redirect_uri: redirectUri,
    code,
  });
  if (env.KAKAO_CLIENT_SECRET) body.set('client_secret', env.KAKAO_CLIENT_SECRET);

  const tr = await fetch('https://kauth.kakao.com/oauth/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded;charset=utf-8' },
    body,
  });
  const tok = await tr.json();
  if (!tok.access_token) {
    return Response.redirect(`${url.origin}/member/?err=token&d=${encodeURIComponent(tok.error_description || tok.error || '')}`, 302);
  }

  const ur = await fetch('https://kapi.kakao.com/v2/user/me', {
    headers: { Authorization: `Bearer ${tok.access_token}` },
  });
  const me = await ur.json();
  const kakaoId = String(me.id || '');
  if (!kakaoId) return Response.redirect(`${url.origin}/member/?err=profile`, 302);

  const acc = me.kakao_account || {};
  const nickname = (acc.profile && acc.profile.nickname) || '';
  // 실명 동의를 받았으면 실명을, 아니면 닉네임을 담당자명 기본값으로.
  const name = (acc.name || '').trim() || nickname;
  const email = (acc.email || '').trim();
  const phone = normPhone(acc.phone_number);

  // 조회→수정(또는 추가)→자동승인 세 번을 한 번의 UPSERT 로 묶는다.
  // D1 왕복 한 번이 60ms 쯤이라, 로그인처럼 사람이 기다리는 길목에서는 그대로 체감된다.
  // 새로 들어온 사람은 처음부터 '승인 · 후불' — /member/ 가 후불 멤버십 전용이라
  // 승인만 하고 선불로 두면 가입하자마자 못 들어온다.
  const NOW = kstISO();
  const up = await env.DB.prepare(
    `INSERT INTO customers (kakao_id, name, email, phone, access, billing_mode, created_at, updated_at)
     VALUES (?1, ?2, ?3, ?4, '승인', '후불', ?5, ?5)
     ON CONFLICT(kakao_id) DO UPDATE SET
       name  = COALESCE(NULLIF(customers.name,''),  ?2),
       email = COALESCE(NULLIF(customers.email,''), ?3),
       phone = COALESCE(NULLIF(customers.phone,''), ?4),
       access = CASE WHEN customers.access IS NULL OR customers.access IN ('','대기')
                     THEN '승인' ELSE customers.access END,
       billing_mode = CASE WHEN customers.access IS NULL OR customers.access IN ('','대기')
                           THEN '후불' ELSE customers.billing_mode END,
       updated_at = ?5
     RETURNING id`
  ).bind(kakaoId, name, email, phone, NOW).first();
  const cid = up && up.id;
  if (!cid) return Response.redirect(`${url.origin}/member/?err=save`, 302);
  // (당분간 멤버십 자동 승인 — 승인제로 바꾸려면 위 UPSERT 의 access 기본값을 '대기' 로 둔다)

  const token = await createSession(env, cid);
  return new Response(null, {
    status: 302,
    headers: { Location: `${url.origin}${next.startsWith('/') ? next : '/member/'}`, 'Set-Cookie': sessionCookie(token) },
  });
}

// 카카오는 "+82 10-1234-5678" 형태로 준다 → 국내 표기로 정규화.
function normPhone(v) {
  if (!v) return '';
  let s = String(v).trim();
  if (s.startsWith('+82')) s = '0' + s.slice(3).replace(/^\s*/, '');
  return s.replace(/[^0-9]/g, '').replace(/^(01[016789])(\d{3,4})(\d{4})$/, '$1-$2-$3');
}
