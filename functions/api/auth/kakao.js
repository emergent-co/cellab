// GET /api/auth/kakao?next=/order/  → 카카오 로그인 시작
import { json } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const next = url.searchParams.get('next') || '/order/';
  const key = env.KAKAO_REST_KEY || '';
  if (!key) return json({ error: 'kakao_not_configured', message: 'KAKAO_REST_KEY 환경변수가 없습니다.' }, 503);

  const redirectUri = `${url.origin}/api/auth/callback`;
  const state = encodeURIComponent(next);
  const auth = new URL('https://kauth.kakao.com/oauth/authorize');
  auth.searchParams.set('client_id', key);
  auth.searchParams.set('redirect_uri', redirectUri);
  auth.searchParams.set('response_type', 'code');
  auth.searchParams.set('scope', 'profile_nickname,account_email,name,phone_number');
  auth.searchParams.set('state', state);
  return Response.redirect(auth.toString(), 302);
}
