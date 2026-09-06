// GET /api/general/orders        → 일반회원 본인 주문·견적문의 목록
// GET /api/general/orders?id=12  → 주문 1건 상세 (품목 + 발행 문서)
//   /api/order/* 는 멤버십(후불) 전용이라 일반회원이 못 쓴다.
//   여기서는 «내 것 읽기»만 한다 — 만들고 고치는 길은 열지 않는다.
import { json, currentCustomer, generalGate } from '../_lib.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  const gate = generalGate(me); if (gate) return gate;

  const id = Number(new URL(request.url).searchParams.get('id') || 0);

  if (id) {
    const o = await env.DB.prepare(
      `SELECT id, order_no, status, title, org_name, ship_address, want_date, request_note,
              orderer_name, orderer_email, orderer_phone,
              supply_amount, vat_amount, total_amount, received_at, created_at, updated_at
         FROM orders WHERE id=? AND customer_id=?`
    ).bind(id, me.id).first();
    if (!o) return json({ error: 'not_found' }, 404);
    const { results: items } = await env.DB.prepare(
      'SELECT seq, name, spec, unit, qty, unit_price, link FROM order_items WHERE order_id=? ORDER BY seq, id'
    ).bind(id).all();
    const { results: docs } = await env.DB.prepare(
      `SELECT id, type, doc_no, status, issue_date, sent_at
         FROM documents WHERE order_id=? ORDER BY id DESC`
    ).bind(id).all();
    return json({ order: o, items: items || [], documents: docs || [] });
  }

  const { results: orders } = await env.DB.prepare(
    `SELECT o.id, o.order_no, o.status, o.title, o.org_name, o.total_amount,
            o.ship_address, o.received_at, o.created_at,
            (SELECT COUNT(*) FROM order_items i WHERE i.order_id=o.id) AS item_count
       FROM orders o WHERE o.customer_id=? ORDER BY o.id DESC LIMIT 100`
  ).bind(me.id).all();

  /* 일반회원의 «주문»은 대개 견적 문의에서 시작한다.
     문의는 아직 주문번호가 없어 orders 에 없다 — 같이 보여줘야 내가 뭘 넣었는지 안다. */
  const { results: inqs } = await env.DB.prepare(
    `SELECT id, name, org_name, items_json, note, status, created_at
       FROM inquiries WHERE customer_id=? ORDER BY id DESC LIMIT 50`
  ).bind(me.id).all();

  return json({
    orders: orders || [],
    inquiries: (inqs || []).map((r) => ({ ...r, items: safe(r.items_json), items_json: undefined })),
  });
}

function safe(t) { try { return JSON.parse(t || '[]') || []; } catch (e) { return []; } }
