// GET /api/auth/callback?code=...&state=next  → 토큰 교환 → 고객 upsert → 세션 쿠키
import { kstISO, createSession, sessionCookie } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const next = decodeURIComponent(url.searchParams.get('state') || '/member-general/');
  if (!code) return Response.redirect(`${url.origin}/login/?err=no_code`, 302);

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
    return Response.redirect(`${url.origin}/login/?err=token&d=${encodeURIComponent(tok.error_description || tok.error || '')}`, 302);
  }

  const ur = await fetch('https://kapi.kakao.com/v2/user/me', {
    headers: { Authorization: `Bearer ${tok.access_token}` },
  });
  const me = await ur.json();
  const kakaoId = String(me.id || '');
  if (!kakaoId) return Response.redirect(`${url.origin}/login/?err=profile`, 302);

  const acc = me.kakao_account || {};
  const nickname = (acc.profile && acc.profile.nickname) || '';
  // 실명 동의를 받았으면 실명을, 아니면 닉네임을 담당자명 기본값으로.
  const name = (acc.name || '').trim() || nickname;
  const email = (acc.email || '').trim();
  const phone = normPhone(acc.phone_number);

  // 조회→수정(또는 추가)를 한 번의 UPSERT 로 묶는다.
  // D1 왕복 한 번이 60ms 쯤이라, 로그인처럼 사람이 기다리는 길목에서는 그대로 체감된다.
  // 새로 들어온 사람은 '일반'(선불) — 카카오만으로 여기까지다. 바로 /member-general/ 를 쓴다.
  // 멤버십(후불 장부)은 요청 → 사장이 준 가입코드 → /api/membership/redeem 으로만 올라간다.
  // 자동 승인하면 아무나 후불 장부에 오르고, 되돌리려 할 때는 이미 주문이 쌓여 있다.
  // 이미 있는 사람의 access·billing_mode 는 건드리지 않는다.
  const NOW = kstISO();
  const up = await env.DB.prepare(
    `INSERT INTO customers (kakao_id, name, email, phone, access, billing_mode, created_at, updated_at)
     VALUES (?1, ?2, ?3, ?4, '일반', '선불', ?5, ?5)
     ON CONFLICT(kakao_id) DO UPDATE SET
       name  = COALESCE(NULLIF(customers.name,''),  ?2),
       email = COALESCE(NULLIF(customers.email,''), ?3),
       phone = COALESCE(NULLIF(customers.phone,''), ?4),
       access = COALESCE(NULLIF(customers.access,''), '일반'),
       billing_mode = COALESCE(NULLIF(customers.billing_mode,''), '선불'),
       updated_at = ?5
     RETURNING id`
  ).bind(kakaoId, name, email, phone, NOW).first();
  const cid = up && up.id;
  if (!cid) return Response.redirect(`${url.origin}/login/?err=save`, 302);

  const token = await createSession(env, cid);
  return new Response(null, {
    status: 302,
    headers: { Location: `${url.origin}${next.startsWith('/') ? next : '/member-general/'}`, 'Set-Cookie': sessionCookie(token) },
  });
}

// 카카오는 "+82 10-1234-5678" 형태로 준다 → 국내 표기로 정규화.
function normPhone(v) {
  if (!v) return '';
  let s = String(v).trim();
  if (s.startsWith('+82')) s = '0' + s.slice(3).replace(/^\s*/, '');
  return s.replace(/[^0-9]/g, '').replace(/^(01[016789])(\d{3,4})(\d{4})$/, '$1-$2-$3');
}
