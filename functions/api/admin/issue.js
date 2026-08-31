// functions/api/admin/issue.js — 문서 발행 (견적서 · 거래명세서 · 세금계산서)
//   주문에 매이지 않는 단독 발행이 기본이다. 주문·정산 요청에서 내용을 끌어올 수도 있다.
//
//   GET  ?clients=1&q=          거래처 검색
//   GET  ?client=<id>           거래처 상세(실험실 · 발행정보 · 최근 주문/정산)
//   GET  ?from=order&id=        주문에서 항목 끌어오기
//   GET  ?from=settlement&id=   정산 요청에서 항목 끌어오기
//   GET  ?list=1&type=&status=&q=   발행 이력
//   POST                        문서 생성 / 수정(작성됨 상태만)
import { json, needAdmin, adminOK, kstISO, kstDate, nextDocNo, plusDays,
         randomToken, logEvent, DOC_LABEL } from '../_lib.js';
import { ISSUER } from '../_doctpl.js';
import { deliverMany, calcTotals } from '../_send.js';
import { docMailBody } from '../_mailer.js';

const TYPES = ['quote', 'statement', 'taxinvoice'];
const round10 = (n) => Math.round(Number(n || 0) / 10) * 10;
const safe = (s) => { try { return JSON.parse(s || '[]'); } catch { return []; } };

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  if (request.method === 'GET') return get(request, env);
  if (request.method === 'POST') return post(request, env);
  return json({ error: 'method_not_allowed' }, 405);
}

/* ============================ 조회 ============================ */
async function get(request, env) {
  const u = new URL(request.url).searchParams;

  // ---- 거래처 검색 ----
  if (u.get('clients')) {
    const q = (u.get('q') || '').trim();
    const rows = q
      ? (await env.DB.prepare(
          `SELECT c.*, l.name AS lab_name FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
            WHERE c.name LIKE ? OR c.company LIKE ? OR c.email LIKE ?
               OR c.work_email LIKE ? OR c.phone LIKE ? OR l.name LIKE ?
            ORDER BY c.id DESC LIMIT 20`)
          .bind(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`).all()).results
      : (await env.DB.prepare(
          `SELECT c.*, l.name AS lab_name FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
            ORDER BY (c.access='승인') DESC, c.id DESC LIMIT 20`).all()).results;
    return json({ clients: (rows || []).map(slimClient) });
  }

  // ---- 거래처 상세 ----
  if (u.get('client')) {
    const c = await env.DB.prepare(
      'SELECT c.*, l.name AS lab_name, l.code AS lab_code FROM customers c LEFT JOIN labs l ON l.id=c.lab_id WHERE c.id=?'
    ).bind(u.get('client')).first();
    if (!c) return json({ error: 'not_found' }, 404);

    // 같은 실험실 사람이 넣은 주문·정산도 함께 끌어올 수 있어야 한다
    const ids = c.lab_id
      ? ((await env.DB.prepare('SELECT id FROM customers WHERE lab_id=?').bind(c.lab_id).all()).results || []).map((r) => r.id)
      : [c.id];
    const ph = ids.map(() => '?').join(',');

    const profiles = (await env.DB.prepare(
      'SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id').bind(c.id).all()).results || [];
    const orders = (await env.DB.prepare(
      `SELECT id, order_no, title, status, total_amount, created_at FROM orders
        WHERE customer_id IN (${ph}) AND status<>'취소' ORDER BY id DESC LIMIT 10`).bind(...ids).all()).results || [];
    const settles = (await env.DB.prepare(
      `SELECT id, status, items_json, supply, vat, total, created_at FROM settlements
        WHERE customer_id IN (${ph}) ORDER BY id DESC LIMIT 10`).bind(...ids).all()).results || [];
    const members = c.lab_id
      ? (await env.DB.prepare('SELECT id, name, email, work_email FROM customers WHERE lab_id=? ORDER BY id')
          .bind(c.lab_id).all()).results || []
      : [];

    return json({
      client: slimClient(c), profiles, members, orders,
      settlements: settles.map((s) => ({ ...s, items: safe(s.items_json) })),
    });
  }

  // ---- 주문에서 끌어오기 ----
  if (u.get('from') === 'order') {
    const o = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(u.get('id')).first();
    if (!o) return json({ error: 'not_found' }, 404);
    const items = (await env.DB.prepare(
      'SELECT name, spec, qty, unit_price, note FROM order_items WHERE order_id=? ORDER BY seq, id')
      .bind(o.id).all()).results || [];
    return json({
      source: 'order', order_id: o.id, customer_id: o.customer_id,
      bill_profile_id: o.bill_profile_id || null,
      title: o.title || '', vat_included: false,
      items: items.map((i) => ({
        name: i.name, spec: i.spec || '', qty: Number(i.qty) || 1,
        price: Math.round(Number(i.unit_price) || 0), note: i.note || '',
      })),
    });
  }

  // ---- 정산 요청에서 끌어오기 (금액을 그대로 지킨다) ----
  if (u.get('from') === 'settlement') {
    const s = await env.DB.prepare('SELECT * FROM settlements WHERE id=?').bind(u.get('id')).first();
    if (!s) return json({ error: 'not_found' }, 404);
    const items = safe(s.items_json);
    return json({
      source: 'settlement', settlement_id: s.id, customer_id: s.customer_id,
      bill_profile_id: s.bill_profile_id || null,
      title: items.length ? `${items[0].name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''}` : '',
      vat_included: true,
      target_total: Number(s.total) || 0,
      items: items.map((i) => ({
        name: i.name, spec: '', qty: Number(i.qty) || 1,
        price: Math.round(Number(i.price) || 0), note: '',
      })),
    });
  }

  // ---- 발행 이력 ----
  const type = u.get('type');
  const status = u.get('status');
  const q = (u.get('q') || '').trim();
  const w = [], bind = [];
  if (type && TYPES.includes(type)) { w.push('d.type=?'); bind.push(type); }
  if (status) { w.push('d.status=?'); bind.push(status); }
  if (q) { w.push('(d.doc_no LIKE ? OR c.name LIKE ? OR c.company LIKE ? OR d.payload_json LIKE ?)');
           bind.push(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`); }
  const where = w.length ? `WHERE ${w.join(' AND ')}` : '';
  const { results } = await env.DB.prepare(
    `SELECT d.id, d.type, d.doc_no, d.status, d.issue_date, d.source, d.order_id, d.settlement_id,
            d.customer_id, d.access_token, d.sent_at, d.opened_at, d.created_at, d.payload_json,
            c.name AS contact, c.company,
            (SELECT COUNT(*) FROM outbox ob WHERE ob.document_id=d.id AND ob.status='대기') AS queued,
            (SELECT MIN(ob.send_at) FROM outbox ob WHERE ob.document_id=d.id AND ob.status='대기') AS send_at
       FROM documents d LEFT JOIN customers c ON c.id=d.customer_id
       ${where} ORDER BY d.id DESC LIMIT 120`).bind(...bind).all();

  const docs = (results || []).map((d) => {
    let p = {}; try { p = JSON.parse(d.payload_json || '{}'); } catch { /* noop */ }
    const { payload_json, ...rest } = d;
    return { ...rest, title: p.title || '', company: d.company || p.client?.company || '',
             total: p.totals?.total || 0, view: `/doc/${d.id}?t=${d.access_token}` };
  });

  const st = (await env.DB.prepare(
    `SELECT SUM(CASE WHEN status='작성됨' THEN 1 ELSE 0 END) AS draft,
            SUM(CASE WHEN status='발송됨' THEN 1 ELSE 0 END) AS sent,
            SUM(CASE WHEN status='열람됨' THEN 1 ELSE 0 END) AS opened,
            SUM(CASE WHEN status='취소됨' THEN 1 ELSE 0 END) AS voided,
            COUNT(*) AS all_ FROM documents`).first()) || {};
  return json({ docs, stats: st });
}

function slimClient(c) {
  return {
    id: c.id, name: c.name, company: c.company, email: c.email, work_email: c.work_email,
    phone: c.phone, address: c.address, biz_no: c.biz_no, ceo: c.ceo,
    tax_email: c.tax_email, billing_mode: c.billing_mode, access: c.access,
    lab_id: c.lab_id, lab_name: c.lab_name || '', lab_code: c.lab_code || '',
  };
}

/* ============================ 발행 ============================ */
async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  if (b.action === 'send') return sendBatch(request, env, b);

  // 한 벌로 발행한다 — 견적서·거래명세서·세금계산서를 같은 내용으로 동시에.
  const types = (Array.isArray(b.types) && b.types.length ? b.types : [b.type || 'quote'])
    .filter((t) => TYPES.includes(t));
  if (!types.length) return json({ error: 'no_type', message: '발행할 문서 종류를 골라주세요.' }, 400);

  const customer = b.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(b.customer_id).first()
    : null;
  if (!customer) return json({ error: 'no_client', message: '거래처를 선택해주세요.' }, 400);

  // 발행정보는 그 거래처 것만 — 없으면 기본값으로 되돌린다
  let bill = null;
  if (b.bill_profile_id) {
    bill = await env.DB.prepare('SELECT * FROM bill_profiles WHERE id=? AND customer_id=?')
      .bind(b.bill_profile_id, customer.id).first();
  }
  if (!bill) {
    bill = await env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1')
      .bind(customer.id).first();
  }

  const raw = (Array.isArray(b.items) ? b.items : [])
    .map((i) => ({
      name: String(i.name || '').trim(),
      spec: String(i.spec || '').trim(),
      qty: Math.max(0, Number(i.qty) || 0),
      price: Math.round(Number(i.price) || 0),
      note: String(i.note || '').trim(),
    }))
    .filter((i) => i.name);
  if (!raw.length) return json({ error: 'no_items', message: '품목을 1개 이상 입력해주세요.' }, 400);
  if (raw.length > 40) return json({ error: 'too_many', message: '품목은 40개까지 넣을 수 있습니다.' }, 400);
  const unpriced = raw.filter((i) => !i.price);
  if (unpriced.length) {
    return json({ error: 'no_price', message: `단가가 비어 있는 품목이 ${unpriced.length}개 있습니다.` }, 400);
  }

  const { items, totals } = compute(raw, b.vat_included !== false);

  const issue = b.issue_date || kstDate();
  // 유효기간은 발행일 + 1개월. 화면에서 따로 받지 않는다 — 견적서에만 뜻이 있고 늘 같은 값이다.
  const base = {
    issue_date: issue,
    valid_until: plusDays(issue, 30),
    title: String(b.title || '').trim(),
    client: {
      company: bill?.company || customer.company || '',
      biz_no: bill?.biz_no || customer.biz_no || '',
      ceo: bill?.ceo || customer.ceo || '',
      contact: String(b.contact || customer.name || ''),
      email: String(b.email || bill?.tax_email || customer.work_email || customer.email || ''),
      address: bill?.address || customer.address || '',
    },
    items, totals,
    note: String(b.note || '').trim(),   // 입금계좌는 양식이 늘 따로 찍는다
  };

  const now = kstISO();

  // ---- 수정 (작성됨 상태만) — 한 건씩만 고친다 ----
  if (b.id) {
    const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
    if (!doc) return json({ error: 'not_found' }, 404);
    if (doc.status !== '작성됨') {
      return json({ error: 'locked', message: '이미 발송된 문서는 수정할 수 없습니다. 새로 발행해주세요.' }, 409);
    }
    const payload = { ...base, type: doc.type, doc_no: doc.doc_no };
    await env.DB.prepare(
      `UPDATE documents SET customer_id=?, order_id=?, settlement_id=?, source=?, issue_date=?, payload_json=?, updated_at=? WHERE id=?`
    ).bind(customer.id, b.order_id || null, b.settlement_id || null,
           b.source || doc.source || 'manual', issue, JSON.stringify(payload), now, doc.id).run();
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'updated', actor: 'admin',
      detail: `${DOC_LABEL[doc.type]} ${doc.doc_no} 수정` });
    return json({ ok: true, id: doc.id, doc_no: doc.doc_no, totals, batch: doc.batch,
                  view: `/doc/${doc.id}?t=${doc.access_token}`,
                  docs: [{ id: doc.id, type: doc.type, doc_no: doc.doc_no,
                           view: `/doc/${doc.id}?t=${doc.access_token}` }] });
  }

  // ---- 신규 — 고른 종류만큼 같은 내용으로 만든다 ----
  const batch = types.length > 1 ? randomToken().slice(0, 16) : null;
  const made = [];
  for (const type of types) {
    const docNo = await nextDocNo(env, type);
    const payload = { ...base, type, doc_no: docNo };
    const tok = randomToken();
    const r = await env.DB.prepare(
      `INSERT INTO documents (order_id, customer_id, settlement_id, source, batch, type, doc_no, version, status,
                              issue_date, payload_json, access_token, created_at, updated_at)
       VALUES (?,?,?,?,?,?,?,1,'작성됨',?,?,?,?,?)`
    ).bind(b.order_id || null, customer.id, b.settlement_id || null, b.source || 'manual', batch,
           type, docNo, issue, JSON.stringify(payload), tok, now, now).run();

    const id = r.meta.last_row_id;
    await logEvent(env, {
      order_id: b.order_id || null, document_id: id, action: 'created', actor: 'admin',
      detail: `${DOC_LABEL[type]} ${docNo} 발행 (${customer.company || customer.name || ''})`,
    });
    made.push({ id, type, doc_no: docNo, view: `/doc/${id}?t=${tok}` });
  }

  return json({
    ok: true, batch, totals, docs: made,
    to: base.client.email,
    // 예전 호출부 호환 — 첫 문서를 단건처럼 돌려준다
    id: made[0].id, doc_no: made[0].doc_no, view: made[0].view,
  });
}

/* ---- 묶음 발송 · 예약 ----
   한 벌로 뽑은 서류는 고객도 한 통으로 받아야 짝이 맞는다. */
async function sendBatch(request, env, b) {
  const ids = (Array.isArray(b.ids) ? b.ids : []).map(Number).filter(Boolean).slice(0, 5);
  if (!ids.length) return json({ error: 'no_docs', message: '보낼 문서를 골라주세요.' }, 400);

  const docs = [];
  for (const id of ids) {
    const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(id).first();
    if (!doc) continue;
    if (doc.status === '취소됨') continue;
    let payload = {};
    try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }
    docs.push({ doc, payload });
  }
  if (!docs.length) return json({ error: 'not_found', message: '보낼 수 있는 문서가 없습니다.' }, 404);

  const first = docs[0];
  const to = String(b.to || first.payload.client?.email || '').trim();
  if (!to) return json({ error: 'no_recipient', message: '받는 사람 이메일이 없습니다.' }, 400);

  const labels = docs.map(({ doc }) => DOC_LABEL[doc.type] || '문서');
  const subject = String(b.subject || '').trim()
    || `[실험셋업연구소] ${labels.join(' · ')} ${first.doc.doc_no}`;
  const totals = calcTotals(first.payload.items, first.payload.totals);
  const origin = new URL(request.url).origin;
  const html = docMailBody({
    label: labels.join(' · '),
    docNo: docs.map(({ doc }) => doc.doc_no).join(', '),
    company: first.payload.client?.company,
    contact: first.payload.client?.contact,
    total: totals.total,
    viewUrl: `${origin}${first.doc ? `/doc/${first.doc.id}?t=${first.doc.access_token}` : ''}`,
  });

  // 예약
  if (b.send_at) {
    await env.DB.prepare(
      `INSERT INTO outbox (document_id, doc_ids, order_id, to_addr, cc_addr, subject, body, send_at, status, created_at)
       VALUES (?,?,?,?,?,?,?,?, '대기', ?)`
    ).bind(first.doc.id, JSON.stringify(docs.map(({ doc }) => doc.id)), first.doc.order_id || null,
           to, b.cc || null, subject, html, b.send_at, kstISO()).run();
    for (const { doc } of docs) {
      await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'scheduled',
        channel: 'email', actor: 'admin', to_addr: to, detail: `${b.send_at} 발송 예약` });
    }
    return json({ ok: true, scheduled: b.send_at, count: docs.length });
  }

  const res = await deliverMany(env, { docs, to, cc: b.cc, subject, html });
  if (!res.ok) return json({ error: 'send_failed', message: res.error }, 502);
  return json({ ok: true, sent: true, count: docs.length, attached: res.attached });
}

/**
 * 부가세 포함 총액이 먼저 정해지는 방식(정산과 같다):
 *   금액 = 10원 단위로 맞춘 (수량 × 부가세포함단가)  →  총계 = 금액 합
 *   공급가액 = round(총계 / 1.1),  부가세 = 총계 − 공급가액   ← 합이 반드시 맞는다
 * 부가세 별도 방식이면 기존대로 공급가에 10%를 얹는다.
 */
function compute(raw, vatIncluded) {
  if (vatIncluded) {
    const items = raw.map((i) => {
      const amount = round10(i.qty * i.price);
      return { name: i.name, spec: i.spec, qty: i.qty, note: i.note,
               unit_price: Math.round(i.price / 1.1), amount };
    });
    const total = items.reduce((s, i) => s + i.amount, 0);
    const supply = Math.round(total / 1.1);
    return { items, totals: { supply, vat: total - supply, total, vat_included: true } };
  }
  const items = raw.map((i) => {
    const line = Math.round(i.qty * i.price);
    return { name: i.name, spec: i.spec, qty: i.qty, note: i.note,
             unit_price: i.price, amount: Math.round(line * 1.1) };
  });
  const supply = raw.reduce((s, i) => s + Math.round(i.qty * i.price), 0);
  const vat = Math.round(supply * 0.1);
  return { items, totals: { supply, vat, total: supply + vat, vat_included: false } };
}
