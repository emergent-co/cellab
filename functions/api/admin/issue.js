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
         randomToken, logEvent, DOC_LABEL, nextOrderNo, STATUSES } from '../_lib.js';
import { ISSUER } from '../_doctpl.js';
import { deliverMany, calcTotals } from '../_send.js';
import { docMailBody, splitAddr } from '../_mailer.js';

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
            WHERE c.name LIKE ? OR c.company LIKE ? OR c.alias LIKE ? OR c.email LIKE ?
               OR c.work_email LIKE ? OR c.phone LIKE ? OR c.biz_no LIKE ? OR l.name LIKE ?
            ORDER BY c.id DESC LIMIT 20`)
          .bind(...Array(8).fill(`%${q}%`)).all()).results
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
      // 고객이 정산 요청할 때 서류별로 적어 보낸 날짜 — 그대로 쓴다
      dates: { quote: s.quote_date || '', statement: s.statement_date || '', taxinvoice: s.taxinvoice_date || '' },
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
             total: p.totals?.total || 0, is_order: !!d.order_id,
             view: `/doc/${d.id}?t=${d.access_token}` };
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
    id: c.id, name: c.name, company: c.company, alias: c.alias || '',
    email: c.email, work_email: c.work_email,
    phone: c.phone, address: c.address, biz_no: c.biz_no, ceo: c.ceo,
    tax_email: c.tax_email, billing_mode: c.billing_mode, access: c.access,
    lab_id: c.lab_id, lab_name: c.lab_name || '', lab_code: c.lab_code || '',
  };
}

/* ============================ 발행 ============================ */
async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  if (b.action === 'send') return sendBatch(request, env, b);
  if (b.action === 'relink') return relink(env, b);
  if (b.action === 'to_order') return toOrder(env, b);
  if (b.action === 'to_settlement') return toSettlement(env, b);
  if (b.action === 'to_payment') return toPayment(env, b);
  if (b.action === 'undo_payment') return undoPayment(env, b);

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

  // 서류마다 발행일이 다를 수 있다 — 견적은 오늘, 거래명세서는 납품일, 계산서는 월말 식으로.
  // dates 에 없으면 공통 발행일을, 그것도 없으면 오늘을 쓴다.
  const common = b.issue_date || kstDate();
  const dateOf = (t) => (b.dates && b.dates[t]) || common;
  // 견적명·거래명은 첫 품목 이름으로 자동 생성한다 — 매번 손으로 적을 이유가 없다
  const autoTitle = items.length
    ? `${items[0].name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''}` : '';
  const base = {
    title: String(b.title || '').trim() || autoTitle,
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
    const issue = dateOf(doc.type);
    // 유효기간은 발행일 + 1개월. 화면에서 따로 받지 않는다 — 견적서에만 뜻이 있고 늘 같은 값이다.
    const payload = { ...base, type: doc.type, doc_no: doc.doc_no,
                      issue_date: issue, valid_until: plusDays(issue, 30) };
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
  // 발행 목적 — 무엇으로 기록할지는 여기서 정해진다. 발행하고 나서 되묻지 않는다.
  //   quote 견적서만 (기록 없음) · delivery 납품 서류(주문) · advance 중간정산금 청구(정산요청)
  //   settle 고객 정산요청 처리(기존 정산요청에 연결)
  const purpose = ['quote', 'delivery', 'advance', 'settle'].includes(b.purpose) ? b.purpose : null;

  const batch = types.length > 1 ? randomToken().slice(0, 16) : null;
  const made = [];
  for (const type of types) {
    const docNo = await nextDocNo(env, type);
    const issue = dateOf(type);
    const payload = { ...base, type, doc_no: docNo,
                      issue_date: issue, valid_until: plusDays(issue, 30) };
    const tok = randomToken();
    const r = await env.DB.prepare(
      `INSERT INTO documents (order_id, customer_id, settlement_id, source, batch, type, doc_no, version, status,
                              issue_date, payload_json, access_token, purpose, created_at, updated_at)
       VALUES (?,?,?,?,?,?,?,1,'작성됨',?,?,?,?,?,?)`
    ).bind(b.order_id || null, customer.id, b.settlement_id || null, b.source || 'manual', batch,
           type, docNo, issue, JSON.stringify(payload), tok, purpose, now, now).run();

    const id = r.meta.last_row_id;
    await logEvent(env, {
      order_id: b.order_id || null, document_id: id, action: 'created', actor: 'admin',
      detail: `${DOC_LABEL[type]} ${docNo} 발행 (${customer.company || customer.name || ''})`,
    });
    made.push({ id, type, doc_no: docNo, issue_date: issue, view: `/doc/${id}?t=${tok}` });
  }

  // 목적이 정해졌으면 그대로 기록한다. (purpose 없이 오는 옛 호출은 make_order 로 동작)
  const docIds = made.map((m) => m.id);
  let order = null, settle = null;

  if (purpose === 'delivery' || (!purpose && b.make_order)) {
    order = await makeOrder(env, {
      customer, payload: { ...base, title: base.title },
      items, totals, status: b.order_status, issueDate: dateOf(types[0]),
      docIds,
    });
  }

  if (purpose === 'advance') {
    // 아직 돈은 안 들어왔다 — «입금 대기» 상태의 정산요청만 만든다.
    // 중간정산금(입금)은 나중에 이 요청을 «입금완료»로 바꾸는 순간 자동으로 잡힌다.
    settle = await makeSettlement(env, {
      customer, base, items, totals, made, docIds, status: '서류발급 완료',
    });
  }

  if (purpose === 'settle' && b.settlement_id) {
    const st = await env.DB.prepare('SELECT id, customer_id FROM settlements WHERE id=?')
      .bind(b.settlement_id).first();
    if (st && Number(st.customer_id) === Number(customer.id)) {
      await env.DB.batch([
        ...docIds.map((id) => env.DB.prepare(
          'UPDATE documents SET settlement_id=?, updated_at=? WHERE id=?').bind(st.id, now, id)),
        env.DB.prepare("UPDATE settlements SET status='서류발급 완료', updated_at=? WHERE id=?")
          .bind(now, st.id),
      ]);
      settle = { id: st.id, status: '서류발급 완료' };
    }
  }

  return json({
    ok: true, batch, totals, docs: made, order, settlement: settle, purpose,
    to: base.client.email,
    // 예전 호출부 호환 — 첫 문서를 단건처럼 돌려준다
    id: made[0].id, doc_no: made[0].doc_no, view: made[0].view,
  });
}

/* ---- 발행한 내용을 주문으로도 기록 ----
   견적만 내고 성사 안 되는 건이 많다. 그래서 기본은 '주문 아님'이고,
   실제로 물건이 나가는 건일 때만 켜서 장부에 올린다.
   금액은 서류의 값을 그대로 옮긴다 — 다시 계산하면 1원씩 어긋난다. */
async function makeOrder(env, { customer, payload, items, totals, status, issueDate, docIds }) {
  const st = STATUSES.includes(status) ? status : '발주확정';
  const day = String(issueDate || '').slice(0, 10);
  const at = /^\d{4}-\d{2}-\d{2}$/.test(day) ? `${day} 00:00:00` : kstISO();
  const now = kstISO();

  const order_no = await nextOrderNo(env);
  const r = await env.DB.prepare(
    `INSERT INTO orders (order_no, customer_id, status, title, org_name, ship_address,
                         orderer_name, orderer_email, orderer_phone, bill_profile_id,
                         supply_amount, vat_amount, total_amount, manual, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 1, ?, ?)`
  ).bind(order_no, customer.id, st, payload.title || '(제목 없음)',
         payload.client?.company || customer.company || '', customer.address || '',
         payload.client?.contact || customer.name || '',
         payload.client?.email || customer.work_email || customer.email || '',
         customer.phone || '', null,
         totals.supply, totals.vat, totals.total, at, now).run();

  const orderId = r.meta.last_row_id;
  let seq = 1;
  for (const it of items) {
    await env.DB.prepare(
      `INSERT INTO order_items (order_id, seq, name, spec, unit, qty, unit_price, amount, note)
       VALUES (?,?,?,?,?,?,?,?,?)`
    ).bind(orderId, seq++, it.name, it.spec || '', 'EA', it.qty,
           Math.round(it.unit_price || 0),
           Math.round((it.qty || 0) * (it.unit_price || 0)), it.note || '').run();
  }

  // 서류를 이 주문에 붙인다 — 주문 화면에서 발급 서류가 보이게
  for (const id of docIds || []) {
    await env.DB.prepare("UPDATE documents SET order_id=?, source='order', updated_at=? WHERE id=?")
      .bind(orderId, now, id).run();
  }

  await logEvent(env, { order_id: orderId, action: 'created', actor: 'admin',
    detail: `발행 문서를 주문으로 기록 ${order_no} · ${st}` });
  return { id: orderId, order_no, status: st };
}

/* 이미 발행한 문서를 나중에 주문으로 올린다 */
async function toOrder(env, b) {
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  if (doc.order_id) return json({ error: 'already', message: '이미 주문에 연결된 문서입니다.' }, 409);
  const customer = doc.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(doc.customer_id).first()
    : null;
  if (!customer) return json({ error: 'no_client', message: '거래처가 연결돼 있지 않습니다. 먼저 거래처를 지정해주세요.' }, 400);

  let payload = {};
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }
  const items = payload.items || [];
  if (!items.length) return json({ error: 'no_items', message: '품목이 없습니다.' }, 400);

  // 같은 벌로 뽑은 서류가 있으면 함께 붙인다
  const sibs = doc.batch
    ? ((await env.DB.prepare('SELECT id FROM documents WHERE batch=? AND order_id IS NULL')
        .bind(doc.batch).all()).results || []).map((x) => x.id)
    : [doc.id];

  const order = await makeOrder(env, {
    customer, payload, items, totals: payload.totals || { supply: 0, vat: 0, total: 0 },
    status: b.status, issueDate: payload.issue_date, docIds: sibs.length ? sibs : [doc.id],
  });
  return json({ ok: true, order, linked: sibs.length || 1 });
}

/* ---- 발행과 동시에 «입금 대기» 정산요청을 만든다 ----
   중간정산금 청구는 «돈을 달라»는 서류다. 발행하는 순간엔 아직 안 들어왔으니
   입금으로 잡으면 잔여정산금이 실제 통장과 어긋난다. 여기서는 대기 줄만 세운다. */
async function makeSettlement(env, { customer, base, items, totals, made, docIds, status }) {
  const now = kstISO();
  const rows = (items || []).map((i) => ({
    name: String(i.name || '').trim(),
    qty: Math.max(1, Number(i.qty) || 1),
    price: Math.round(Number(i.unit_price ?? i.price) || 0),
  })).filter((i) => i.name);

  const dateOfType = (t) => (made.find((m) => m.type === t) || {}).issue_date || null;
  const bill = await env.DB.prepare(
    'SELECT id FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1')
    .bind(customer.id).first();

  const r = await env.DB.prepare(
    `INSERT INTO settlements (customer_id, status, items_json, supply, vat, total, method,
            quote_date, statement_date, taxinvoice_date, reply_email, memo, admin_memo,
            bill_profile_id, manual, created_at, updated_at, done_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, 1, ?,?, NULL)`
  ).bind(customer.id, status, JSON.stringify(rows),
         totals.supply, totals.vat, totals.total, '통장',
         dateOfType('quote'), dateOfType('statement'), dateOfType('taxinvoice'),
         String(base?.client?.email || ''), '', '중간정산금 청구 — 발행과 함께 등록',
         bill?.id || null, now, now).run();

  const sid = r.meta.last_row_id;
  await env.DB.batch(docIds.map((id) => env.DB.prepare(
    'UPDATE documents SET settlement_id=?, updated_at=? WHERE id=?').bind(sid, now, id)));
  await logEvent(env, { action: 'settle_add', actor: 'admin',
    detail: `중간정산금 청구 정산요청 #${sid} · ${Number(totals.total || 0).toLocaleString('ko-KR')}원 (입금 대기)` });
  return { id: sid, status, total: totals.total };
}

/* ---- 발행한 서류를 «중간정산금»(입금)으로 기록한다 ----
   중도금·선입금처럼 물건이 새로 나간 게 아니라 돈이 들어온 건이 있다. 그걸 주문으로 잡으면
   지출금이 두 번 올라 잔여정산금이 틀어진다. 이미 주문으로 잡아둔 것도 여기서 바꾼다.

   주문을 «떼기만» 하면 지출금은 그대로 남아 아무것도 고쳐지지 않는다. 그래서 이 문서에서
   만들어진 주문이면 지운다. 고객이 직접 넣은 주문은 손대지 않고 거절한다 — 남의 기록이다. */
async function toPayment(env, b) {
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  if (doc.payment_id) return json({ error: 'already', message: '이미 중간정산금으로 기록된 문서입니다.' }, 409);
  if (!doc.customer_id) {
    return json({ error: 'no_client', message: '거래처가 연결돼 있지 않습니다. 먼저 거래처를 지정해주세요.' }, 400);
  }

  let payload = {};
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }
  const amount = Math.round(Number(payload?.totals?.total) || 0);
  if (!amount) return json({ error: 'no_amount', message: '문서에 금액이 없습니다.' }, 400);

  // 한 벌로 뽑은 서류는 같은 건이다 — 하나만 바꾸고 나머지를 남겨두면
  // 나중에 견적서를 열어 «아무 데도 안 잡힘»으로 보고 또 누르게 된다. 그러면 두 번 계산된다.
  const family = new Set([doc.id]);
  if (doc.batch) {
    for (const x of (await env.DB.prepare('SELECT id FROM documents WHERE batch=?')
      .bind(doc.batch).all()).results || []) family.add(x.id);
  }

  let removed = null;
  if (doc.order_id) {
    const order = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(doc.order_id).first();
    if (order) {
      if (!order.manual) {
        return json({ error: 'customer_order',
          message: `${order.order_no} 는 고객이 넣은 주문입니다. 여기서 지울 수 없으니 주문 화면에서 처리해주세요.` }, 400);
      }
      const docs = ((await env.DB.prepare('SELECT id FROM documents WHERE order_id=?')
        .bind(order.id).all()).results || []).map((x) => x.id);
      for (const id of docs) family.add(id);          // 그 주문에 붙어 있던 서류도 같은 건이다
      await env.DB.batch([
        ...docs.map((id) => env.DB.prepare(
          "UPDATE documents SET order_id=NULL, source='issue', updated_at=? WHERE id=?").bind(kstISO(), id)),
        env.DB.prepare('DELETE FROM order_items WHERE order_id=?').bind(order.id),
        env.DB.prepare('DELETE FROM orders WHERE id=?').bind(order.id),
      ]);
      removed = order.order_no;
    }
  }

  const day = String(doc.issue_date || '').slice(0, 10);
  const label = DOC_LABEL[doc.type] || '문서';
  const r = await env.DB.prepare(
    'INSERT INTO payments (customer_id, kind, amount, method, paid_at, memo, created_at, created_by) VALUES (?,?,?,?,?,?,?,?)'
  ).bind(doc.customer_id, '입금', amount, String(b.method || '통장'),
         /^\d{4}-\d{2}-\d{2}$/.test(day) ? day : kstDate(),
         `중간정산금 · ${label} ${doc.doc_no}`, kstISO(), 'admin').run();

  const pid = r.meta.last_row_id;
  const ids = [...family];
  await env.DB.batch(ids.map((id) => env.DB.prepare(
    'UPDATE documents SET payment_id=?, updated_at=? WHERE id=?').bind(pid, kstISO(), id)));

  await logEvent(env, { document_id: doc.id, action: 'to_payment', actor: 'admin',
    detail: `중간정산금으로 기록 ${amount.toLocaleString('ko-KR')}원`
      + (ids.length > 1 ? ` (서류 ${ids.length}건)` : '')
      + (removed ? ` · 주문 ${removed} 취소` : '') });
  return json({ ok: true, payment: { id: pid, amount }, removed_order: removed, linked: ids.length });
}

/* 잘못 눌렀을 때 되돌린다 — 입금 줄을 지우고 연결을 끊는다.
   지웠던 주문까지 되살리지는 않는다. 필요하면 «주문으로 기록»을 다시 누르면 된다. */
async function undoPayment(env, b) {
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  if (!doc.payment_id) return json({ error: 'not_linked', message: '중간정산금으로 기록된 문서가 아닙니다.' }, 400);
  // 붙일 때 한 벌을 다 붙였으니 뗄 때도 다 뗀다
  await env.DB.batch([
    env.DB.prepare('DELETE FROM payments WHERE id=?').bind(doc.payment_id),
    env.DB.prepare('UPDATE documents SET payment_id=NULL, updated_at=? WHERE payment_id=?')
      .bind(kstISO(), doc.payment_id),
  ]);
  await logEvent(env, { document_id: doc.id, action: 'undo_payment', actor: 'admin',
    detail: '중간정산금 기록 취소' });
  return json({ ok: true });
}

/* ---- 발행한 서류를 정산 요청으로 올린다 ----
   주문으로 잡는 것과는 다른 일이다. 물건이 나간 기록은 주문, 돈을 받을 기록은 정산이다.
   둘 다 필요한 건도 있고 하나만 필요한 건도 있어서 각각 따로 누를 수 있게 둔다. */
async function toSettlement(env, b) {
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  if (doc.settlement_id) return json({ error: 'already', message: '이미 정산에 연결된 문서입니다.' }, 409);
  if (!doc.customer_id) {
    return json({ error: 'no_client', message: '거래처가 연결돼 있지 않습니다. 먼저 거래처를 지정해주세요.' }, 400);
  }

  let payload = {};
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }
  const items = (payload.items || []).map((i) => ({
    name: String(i.name || '').trim(),
    qty: Math.max(1, Number(i.qty) || 1),
    price: Math.round(Number(i.unit_price) || 0),
  })).filter((i) => i.name);
  if (!items.length) return json({ error: 'no_items', message: '품목이 없습니다.' }, 400);

  const t = payload.totals || {};
  const total = Math.round(Number(t.total) || 0);
  const supply = Math.round(Number(t.supply) || Math.round(total / 1.1));
  const vat = Math.round(Number(t.vat) || (total - supply));

  const ok = ['정산요청', '처리중', '서류발급 완료', '입금완료', '반려'];
  const status = ok.includes(b.status) ? b.status : '서류발급 완료';
  const done = status === '입금완료' ? kstISO() : null;

  const bill = await env.DB.prepare(
    'SELECT id FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1')
    .bind(doc.customer_id).first();

  // 같은 벌로 뽑은 서류는 같이 붙인다 — 견적서·거래명세서·세금계산서가 한 정산 건이다
  const sibs = doc.batch
    ? ((await env.DB.prepare('SELECT id, type, issue_date FROM documents WHERE batch=? AND settlement_id IS NULL')
        .bind(doc.batch).all()).results || [])
    : [{ id: doc.id, type: doc.type, issue_date: doc.issue_date }];
  const dateOf = (ty) => (sibs.find((x) => x.type === ty) || {}).issue_date || null;

  const r = await env.DB.prepare(
    `INSERT INTO settlements (customer_id, status, items_json, supply, vat, total, method,
            quote_date, statement_date, taxinvoice_date, reply_email, memo, admin_memo,
            bill_profile_id, manual, created_at, updated_at, done_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, 1, ?,?,?)`
  ).bind(doc.customer_id, status, JSON.stringify(items), supply, vat, total, '통장',
         dateOf('quote'), dateOf('statement'), dateOf('taxinvoice'),
         String(payload?.client?.email || ''), '',
         `발행 서류에서 기록 (${DOC_LABEL[doc.type] || doc.type} ${doc.doc_no})`,
         bill?.id || null, doc.issue_date ? `${doc.issue_date} 00:00:00` : kstISO(), kstISO(), done).run();

  const sid = r.meta.last_row_id;
  const ids = sibs.length ? sibs.map((x) => x.id) : [doc.id];
  await env.DB.batch(ids.map((id) => env.DB.prepare(
    'UPDATE documents SET settlement_id=?, updated_at=? WHERE id=?').bind(sid, kstISO(), id)));

  await logEvent(env, { document_id: doc.id, action: 'to_settlement', actor: 'admin',
    detail: `정산 #${sid} 으로 기록 · ${total.toLocaleString('ko-KR')}원 (${status})` });
  return json({ ok: true, settlement: { id: sid, status, total }, linked: ids.length });
}

/* ---- 문서를 다른 거래처로 옮기기 ----
   서류를 먼저 뽑고 거래처를 나중에 등록하는 일이 흔하다. 그러면 문서가 엉뚱한 곳에 매여
   거래처 이력에 안 보인다. 여기서 연결을 옮긴다.

   초안(작성됨)이면 서류에 찍히는 공급받는자까지 새 거래처로 다시 쓴다.
   이미 발송한 문서는 연결만 옮긴다 — 상대가 받은 종이의 내용을 뒤늦게 바꾸면 안 된다. */
async function relink(env, b) {
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(b.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  const customer = await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(b.customer_id).first();
  if (!customer) return json({ error: 'no_client', message: '거래처를 선택해주세요.' }, 400);

  let payload = {};
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }

  const draft = doc.status === '작성됨';
  if (draft) {
    const bill = await env.DB.prepare(
      'SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1')
      .bind(customer.id).first();
    payload.client = {
      company: bill?.company || customer.company || '',
      biz_no:  bill?.biz_no  || customer.biz_no  || '',
      ceo:     bill?.ceo     || customer.ceo     || '',
      contact: customer.name || '',
      email:   bill?.tax_email || customer.work_email || customer.email || '',
      address: bill?.address || customer.address || '',
    };
  }

  const now = kstISO();
  await env.DB.prepare('UPDATE documents SET customer_id=?, payload_json=?, updated_at=? WHERE id=?')
    .bind(customer.id, JSON.stringify(payload), now, doc.id).run();

  const who = customer.company || customer.name || `#${customer.id}`;
  await logEvent(env, {
    order_id: doc.order_id, document_id: doc.id, action: 'relinked', actor: 'admin',
    detail: `${DOC_LABEL[doc.type] || '문서'} ${doc.doc_no} → ${who}`
          + (draft ? ' (공급받는자도 함께 수정)' : ' (연결만 이동 · 서류 내용은 그대로)'),
  });
  return json({ ok: true, rewritten: draft, company: who });
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
  // '홍길동 <a@b.com>' 로 적어도 되게 — 본문에는 이름, 실제 발송에는 주소만 쓴다
  const rawTo = String(b.to || first.payload.client?.email || '').trim();
  if (!rawTo) return json({ error: 'no_recipient', message: '받는 사람 이메일이 없습니다.' }, 400);
  const to = splitAddr(rawTo).addr;
  const rawCc = String(b.cc || '').trim();
  const cc = rawCc
    ? rawCc.split(/[,;]/).map((x) => splitAddr(x).addr).filter(Boolean).join(', ')
    : null;

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
    to: rawTo, cc: rawCc,
  });

  // 손으로 붙인 첨부 — 총 10MB, 5개까지. base64 는 원본의 약 4/3 이라 그만큼 여유를 둔다.
  const files = (Array.isArray(b.files) ? b.files : []).slice(0, 5)
    .map((f) => ({ name: String(f.name || 'file').slice(0, 120), b64: String(f.b64 || '') }))
    .filter((f) => f.b64);
  const fbytes = files.reduce((n, f) => n + Math.floor(f.b64.length * 3 / 4), 0);
  if (fbytes > 10 * 1024 * 1024) {
    return json({ error: 'too_big', message: '첨부 파일이 총 10MB를 넘습니다.' }, 400);
  }
  // 예약 발송은 나중에 큐가 꺼내 보낸다 — 파일을 담아둘 자리가 아직 없다.
  if (b.send_at && files.length) {
    return json({ error: 'no_attach_schedule',
      message: '예약 발송에는 파일을 붙일 수 없습니다. 지금 보내시거나, 파일을 빼고 예약해주세요.' }, 400);
  }

  // 예약
  if (b.send_at) {
    await env.DB.prepare(
      `INSERT INTO outbox (document_id, doc_ids, order_id, to_addr, cc_addr, subject, body, send_at, status, created_at)
       VALUES (?,?,?,?,?,?,?,?, '대기', ?)`
    ).bind(first.doc.id, JSON.stringify(docs.map(({ doc }) => doc.id)), first.doc.order_id || null,
           to, cc, subject, html, b.send_at, kstISO()).run();
    for (const { doc } of docs) {
      await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'scheduled',
        channel: 'email', actor: 'admin', to_addr: to, detail: `${b.send_at} 발송 예약` });
    }
    return json({ ok: true, scheduled: b.send_at, count: docs.length });
  }

  const res = await deliverMany(env, { docs, to, cc, subject, html, files });
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
