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
  const email = acc.email || '';

  const exist = await env.DB.prepare('SELECT id, name, email FROM customers WHERE kakao_id = ?').bind(kakaoId).first();
  let cid;
  if (exist) {
    cid = exist.id;
    await env.DB.prepare('UPDATE customers SET name=COALESCE(NULLIF(name,\'\'),?), email=COALESCE(NULLIF(email,\'\'),?), updated_at=? WHERE id=?')
      .bind(nickname, email, kstISO(), cid).run();
  } else {
    const r = await env.DB.prepare('INSERT INTO customers (kakao_id, name, email, created_at, updated_at) VALUES (?,?,?,?,?)')
      .bind(kakaoId, nickname, email, kstISO(), kstISO()).run();
    cid = r.meta.last_row_id;
  }

  const token = await createSession(env, cid);
  return new Response(null, {
    status: 302,
    headers: { Location: `${url.origin}${next.startsWith('/') ? next : '/order/'}`, 'Set-Cookie': sessionCookie(token) },
  });
}
