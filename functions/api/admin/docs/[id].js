// GET  /api/admin/docs/:id            → 문서 상세(스냅샷 포함)
// POST /api/admin/docs/:id  {action}  → send(즉시/예약) · cancel(예약취소) · void(취소처리)
import { json, isAdmin, needAdmin, kstISO, logEvent, DOC_LABEL, adminOK} from '../../_lib.js';
import { ISSUER } from '../../_doctpl.js';
import { barobillConfig, barobillReady, buildTaxInvoice, issueTaxInvoice, taxInvoiceState }
  from '../../_barobill.js';
import { docMailBody } from '../../_mailer.js';
import { deliver, calcTotals } from '../../_send.js';

export async function onRequest({ request, env, params }) {
  if (!(await adminOK(request, env))) return needAdmin();

  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(params.id).first();
  if (!doc) return json({ error: 'not_found' }, 404);
  let payload = {};
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }

  if (request.method === 'GET') {
    const events = (await env.DB.prepare('SELECT * FROM doc_events WHERE document_id=? ORDER BY id DESC').bind(doc.id).all()).results || [];
    const queued = (await env.DB.prepare(
      "SELECT * FROM outbox WHERE (document_id=? OR doc_ids LIKE ?) AND status='대기'")
      .bind(doc.id, `%${doc.id}%`).all()).results || [];
    // 한 벌로 뽑은 서류는 같이 보여야 한다 — 따로 떼어 보내면 짝이 어긋난다
    const siblings = doc.batch
      ? ((await env.DB.prepare(
          'SELECT id, type, doc_no, status, access_token FROM documents WHERE batch=? ORDER BY id')
          .bind(doc.batch).all()).results || []).map((d) => ({
            id: d.id, type: d.type, doc_no: d.doc_no, status: d.status,
            view: `/doc/${d.id}?t=${d.access_token}`,
          }))
      : [];
    const linked = doc.customer_id
      ? await env.DB.prepare('SELECT id, company, alias, name, work_email, access FROM customers WHERE id=?')
          .bind(doc.customer_id).first()
      : null;
    const order = doc.order_id
      ? await env.DB.prepare('SELECT id, order_no, status, total_amount FROM orders WHERE id=?')
          .bind(doc.order_id).first()
      : null;
    return json({ document: doc, payload, events, queued, siblings, linked, order,
                  view: `/doc/${doc.id}?t=${doc.access_token}` });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);
  const b = await request.json().catch(() => ({}));

  // ---- 예약 취소 ----
  if (b.action === 'cancel') {
    await env.DB.prepare("UPDATE outbox SET status='취소' WHERE document_id=? AND status='대기'").bind(doc.id).run();
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'schedule_cancelled', actor: 'admin', detail: '예약 발송 취소' });
    return json({ ok: true });
  }

  // ---- 문서 취소 ----
  if (b.action === 'void') {
    await env.DB.prepare("UPDATE documents SET status='취소됨', updated_at=? WHERE id=?").bind(kstISO(), doc.id).run();
    await env.DB.prepare("UPDATE outbox SET status='취소' WHERE document_id=? AND status='대기'").bind(doc.id).run();
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'cancelled', actor: 'admin', detail: b.reason || '문서 취소' });
    return json({ ok: true });
  }

  /* ---- 국세청 발행 (바로빌) ----
     세금계산서만. 우리 문서 번호를 바로빌 관리번호로 그대로 쓴다 — 한 건이 두 곳에서 같은 이름을 갖는다. */
  if (b.action === 'nts_issue') {
    if (doc.type !== 'taxinvoice') {
      return json({ error: 'not_taxinvoice', message: '세금계산서만 국세청으로 발행할 수 있습니다.' }, 400);
    }
    if (doc.status === '취소됨') return json({ error: 'voided', message: '취소된 문서입니다.' }, 400);
    if (doc.barobill_mgtkey) {
      return json({ error: 'already', message: `이미 발행했습니다 (관리번호 ${doc.barobill_mgtkey}).` }, 400);
    }
    if (!barobillReady(env)) {
      return json({ error: 'not_configured', message: '바로빌 환경변수가 덜 채워졌습니다.' }, 400);
    }

    const cfg = barobillConfig(env);
    // 공급받는자 사업자정보 — 문서에 붙은 계산서 발행 정보를 쓴다
    const bill = doc.customer_id || payload?.client?.bill_profile_id
      ? await env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1')
          .bind(doc.customer_id).first()
      : null;

    const mgtKey = String(doc.doc_no || `D${doc.id}`).slice(0, 24);
    const invoice = buildTaxInvoice({
      mgtKey,
      issuer: { ...ISSUER, email: env.MAIL_FROM_ADDR || 'info@rndsetup.com' },
      bill: bill || {},
      payload,
      contactId: cfg.id,
      writeDate: doc.issue_date || kstISO().slice(0, 10),
    });

    if (!invoice.InvoiceeParty.CorpNum || invoice.InvoiceeParty.CorpNum.length < 10) {
      return json({ error: 'no_bizno',
        message: '공급받는자 사업자번호가 없습니다. 거래처의 계산서 발행 정보를 먼저 등록해주세요.' }, 400);
    }

    const r = await issueTaxInvoice(env, invoice, {
      sms: false, force: !!b.force,
      mailTitle: `[세금계산서] ${payload?.title || doc.doc_no}`,
    });
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'nts_issue', actor: 'admin',
      result: r.ok ? 'ok' : 'fail',
      detail: r.ok ? `국세청 발행 (${cfg.mode}) ${mgtKey}` : `국세청 발행 실패: ${r.error}` });
    if (!r.ok) return json({ error: 'barobill', code: r.code, message: r.error, raw: (r.raw || '').slice(0, 400) }, 502);

    await env.DB.prepare("UPDATE documents SET barobill_mgtkey=?, barobill_state=?, updated_at=? WHERE id=?")
      .bind(mgtKey, `발행요청(${cfg.mode})`, kstISO(), doc.id).run();
    return json({ ok: true, mgt_key: mgtKey, mode: cfg.mode });
  }

  /* ---- 국세청 상태 조회 ---- */
  if (b.action === 'nts_state') {
    if (!doc.barobill_mgtkey) return json({ error: 'not_issued', message: '아직 국세청으로 발행하지 않았습니다.' }, 400);
    const r = await taxInvoiceState(env, doc.barobill_mgtkey);
    if (!r.ok) return json({ error: 'barobill', message: r.error || `상태 ${r.state}` }, 502);
    await env.DB.prepare('UPDATE documents SET barobill_state=?, barobill_ncid=?, updated_at=? WHERE id=?')
      .bind(r.label, r.nts_confirm || null, kstISO(), doc.id).run();
    return json({ ok: true, ...r });
  }

  /* ---- 문서 삭제 ----
     «취소»는 기록을 남기는 것이고, 삭제는 흔적까지 지우는 것이다.
     잘못 만든 문서를 정리하는 용도라, 보낸 이력(doc_events)은 연결만 끊고 남긴다. */
  if (b.action === 'delete') {
    await env.DB.batch([
      env.DB.prepare('DELETE FROM outbox WHERE document_id=?').bind(doc.id),
      env.DB.prepare('UPDATE doc_events SET document_id=NULL WHERE document_id=?').bind(doc.id),
      env.DB.prepare('UPDATE todos SET document_id=NULL WHERE document_id=?').bind(doc.id),
      env.DB.prepare('DELETE FROM documents WHERE id=?').bind(doc.id),
    ]);
    if (doc.pdf_key && env.DOCS) { try { await env.DOCS.delete(doc.pdf_key); } catch (e) {} }
    await logEvent(env, { order_id: doc.order_id, action: 'doc_deleted', actor: 'admin',
      detail: `문서 삭제 ${doc.doc_no || ''}` });
    return json({ ok: true, deleted: doc.doc_no });
  }

  if (b.action !== 'send') return json({ error: 'unknown_action' }, 400);

  // ---- 발송 ----
  const label = DOC_LABEL[doc.type] || '문서';
  const to = String(b.to || payload.client?.email || '').trim();
  if (!to) return json({ error: 'no_recipient', message: '받는 사람 이메일이 없습니다.' }, 400);

  const totals = calcTotals(payload.items, payload.totals);
  const subject = b.subject || `[실험셋업연구소] ${label} ${doc.doc_no}`;
  const origin = new URL(request.url).origin;
  const viewUrl = `${origin}/doc/${doc.id}?t=${doc.access_token}`;
  const html = b.body || docMailBody({
    label, docNo: doc.doc_no, company: payload.client?.company,
    contact: payload.client?.contact, total: totals.total, viewUrl,
  });

  // 예약 발송
  if (b.send_at) {
    await env.DB.prepare(
      `INSERT INTO outbox (document_id, order_id, to_addr, cc_addr, subject, body, send_at, status, created_at)
       VALUES (?,?,?,?,?,?,?, '대기', ?)`
    ).bind(doc.id, doc.order_id, to, b.cc || null, subject, html, b.send_at, kstISO()).run();
    await logEvent(env, {
      order_id: doc.order_id, document_id: doc.id, action: 'scheduled', channel: 'email',
      actor: 'admin', to_addr: to, detail: `${b.send_at} 발송 예약`,
    });
    return json({ ok: true, scheduled: b.send_at });
  }

  const res = await deliver(env, { doc, payload, to, cc: b.cc, subject, html });
  if (!res.ok) return json({ error: 'send_failed', message: res.error }, 502);
  return json({ ok: true, sent: true });
}
