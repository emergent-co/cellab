// functions/admin/customers/index.js — /member/#admMembers 로 이관됨
//   관리자 화면은 이제 /member/ 셸 안에서 열린다 (사이드바를 그대로 쓰기 위해).
//   기존 북마크가 깨지지 않도록 리다이렉트만 남긴다.
export function onRequest({ request }) {
  const url = new URL(request.url);
  return Response.redirect(`${url.origin}/member/#admMembers`, 302);
}
