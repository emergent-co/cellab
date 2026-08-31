// GET /view/order/:id?t=<token>   → 주문 내용 확인 페이지
// GET /view/settle/:id?t=<token>  → 정산 내용 확인 페이지
//   고객에게 링크로 보내는 읽기 전용 화면. 승인 버튼 같은 건 없다.
//   토큰이 맞거나, 관리자거나, 본인(같은 거래처)이면 볼 수 있다.
import { currentCustomer, adminOK } from '../../api/_lib.js';
import { orderViewHTML, settleViewHTML } from '../../api/_viewtpl.js';

const html = (b, s = 200) => new Response(b, {
  status: s,
  headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
});
const txt = (m, s) => new Response(m, {
  status: s, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' },
});

export async function onRequestGet({ request, env, params }) {
  const kind = params.kind === 'settle' ? 'settle' : params.kind === 'order' ? 'order' : null;
  if (!kind) return txt('없는 주소입니다.', 404);

  const table = kind === 'order' ? 'orders' : 'settlements';
  const row = await env.DB.prepare(`SELECT * FROM ${table} WHERE id=?`).bind(params.id).first();
  if (!row) return txt('내용을 찾을 수 없습니다.', 404);

  const token = new URL(request.url).searchParams.get('t') || '';
  let ok = !!(token && row.access_token && token === row.access_token);
  if (!ok && (await adminOK(request, env))) ok = true;
  if (!ok) {
    const me = await currentCustomer(request, env).catch(() => null);
    if (me && Number(me.id) === Number(row.customer_id)) ok = true;
  }
  if (!ok) return txt('열람 권한이 없습니다. 받으신 링크를 그대로 열어주세요.', 403);

  const customer = row.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(row.customer_id).first()
    : null;

  if (kind === 'order') {
    const items = (await env.DB.prepare(
      'SELECT name, spec, unit, qty, unit_price FROM order_items WHERE order_id=? ORDER BY seq, id')
      .bind(row.id).all()).results || [];
    return html(orderViewHTML(row, items, customer));
  }

  let items = [];
  try { items = JSON.parse(row.items_json || '[]'); } catch { items = []; }
  const bill = row.bill_profile_id
    ? await env.DB.prepare('SELECT * FROM bill_profiles WHERE id=?').bind(row.bill_profile_id).first()
    : null;
  return html(settleViewHTML(row, items, customer, bill));
}
