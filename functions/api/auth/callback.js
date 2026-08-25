// GET /api/auth/callback?code=...&state=next  → 토큰 교환 → 고객 upsert → 세션 쿠키
import { kstISO, createSession, sessionCookie } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const next = decodeURIComponent(url.searchParams.get('state') || '/order/');
  if (!code) return Response.redirect(`${url.origin}/order/?err=no_code`, 302);

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
    return Response.redirect(`${url.origin}/order/?err=token&d=${encodeURIComponent(tok.error_description || tok.error || '')}`, 302);
  }

  const ur = await fetch('https://kapi.kakao.com/v2/user/me', {
    headers: { Authorization: `Bearer ${tok.access_token}` },
  });
  const me = await ur.json();
  const kakaoId = String(me.id || '');
  if (!kakaoId) return Response.redirect(`${url.origin}/order/?err=profile`, 302);

  const acc = me.kakao_account || {};
  const nickname = (acc.profile && acc.profile.nickname) || '';
  // 실명 동의를 받았으면 실명을, 아니면 닉네임을 담당자명 기본값으로.
  const name = (acc.name || '').trim() || nickname;
  const email = (acc.email || '').trim();
  const phone = normPhone(acc.phone_number);

  const exist = await env.DB.prepare('SELECT id FROM customers WHERE kakao_id = ?').bind(kakaoId).first();
  let cid;
  if (exist) {
    cid = exist.id;
    // 이미 입력한 값은 덮어쓰지 않고, 비어 있는 칸만 카카오 정보로 채운다.
    await env.DB.prepare(
      `UPDATE customers SET
         name  = COALESCE(NULLIF(name,''),  ?),
         email = COALESCE(NULLIF(email,''), ?),
         phone = COALESCE(NULLIF(phone,''), ?),
         updated_at = ?
       WHERE id = ?`
    ).bind(name, email, phone, kstISO(), cid).run();
  } else {
    const r = await env.DB.prepare(
      'INSERT INTO customers (kakao_id, name, email, phone, created_at, updated_at) VALUES (?,?,?,?,?,?)'
    ).bind(kakaoId, name, email, phone, kstISO(), kstISO()).run();
    cid = r.meta.last_row_id;
  }

  const token = await createSession(env, cid);
  return new Response(null, {
    status: 302,
    headers: { Location: `${url.origin}${next.startsWith('/') ? next : '/order/'}`, 'Set-Cookie': sessionCookie(token) },
  });
}

// 카카오는 "+82 10-1234-5678" 형태로 준다 → 국내 표기로 정규화.
function normPhone(v) {
  if (!v) return '';
  let s = String(v).trim();
  if (s.startsWith('+82')) s = '0' + s.slice(3).replace(/^\s*/, '');
  return s.replace(/[^0-9]/g, '').replace(/^(01[016789])(\d{3,4})(\d{4})$/, '$1-$2-$3');
}
