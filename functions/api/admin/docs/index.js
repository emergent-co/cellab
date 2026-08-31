// POST /api/admin/docs   { order_id, type }  → 문서 생성(스냅샷 고정) + 문서번호 채번
import { json, isAdmin, needAdmin, kstISO, kstDate, nextDocNo, plusDays,
         randomToken, logEvent, DOC_LABEL, adminOK} from '../../_lib.js';
import { ISSUER } from '../../_doctpl.js';

export async function onRequestPost({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  const b = await request.json().catch(() => ({}));
  const type = ['quote', 'statement'].includes(b.type) ? b.type : 'quote';

  const order = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(b.order_id).first();
  if (!order) return json({ error: 'order_not_found' }, 404);

  const customer = order.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(order.customer_id).first()
    : null;
  const items = (await env.DB.prepare(
    'SELECT name, spec, unit, qty, unit_price, note FROM order_items WHERE order_id=? ORDER BY seq, id'
  ).bind(order.id).all()).results || [];

  // 계산서 발행 정보(고객이 정산 시점에 등록) → 없으면 주문의 소속 기관명으로.
  const bill = order.bill_profile_id
    ? await env.DB.prepare('SELECT * FROM bill_profiles WHERE id=?').bind(order.bill_profile_id).first()
    : null;

  if (!items.length) return json({ error: 'no_items', message: '품목이 없습니다.' }, 400);
  const unpriced = items.filter((i) => !Number(i.unit_price));
  if (unpriced.length) {
    return json({ error: 'no_price', message: `단가가 비어 있는 품목이 ${unpriced.length}개 있습니다.` }, 400);
  }

  const issue = b.issue_date || kstDate();
  const docNo = await nextDocNo(env, type);
  const payload = {
    type,
    doc_no: docNo,
    issue_date: issue,
    valid_until: b.valid_until || plusDays(issue, 30),
    title: b.title || order.title || '',
    client: {
      company: bill?.company || order.org_name || customer?.company || '',
      biz_no: bill?.biz_no || customer?.biz_no || '',
      ceo: bill?.ceo || customer?.ceo || '',
      contact: order.orderer_name || customer?.name || '',
      email: bill?.tax_email || order.orderer_email || customer?.work_email || customer?.email || '',
      address: bill?.address || order.ship_address || customer?.address || '',
    },
    items: items.map((i) => ({
      name: i.name, spec: i.spec, qty: i.qty, unit_price: i.unit_price, note: i.note,
    })),
    note: b.note || ISSUER.bank,
  };

  const ver = ((await env.DB.prepare('SELECT COUNT(*) AS c FROM documents WHERE order_id=? AND type=?')
    .bind(order.id, type).first())?.c || 0) + 1;

  const now = kstISO();
  const tok = randomToken();
  const r = await env.DB.prepare(
    `INSERT INTO documents (order_id, customer_id, source, type, doc_no, version, status, issue_date, payload_json, access_token, created_at, updated_at)
     VALUES (?,?, 'order', ?,?,?,?,?,?,?,?,?)`
  ).bind(order.id, order.customer_id || null, type, docNo, ver, '작성됨', issue, JSON.stringify(payload), tok, now, now).run();

  const id = r.meta.last_row_id;
  await logEvent(env, {
    order_id: order.id, document_id: id, action: 'created', actor: 'admin',
    detail: `${DOC_LABEL[type]} ${docNo} 생성 (v${ver})`,
  });

  return json({ ok: true, id, doc_no: docNo, version: ver, view: `/doc/${id}?t=${tok}` });
}
