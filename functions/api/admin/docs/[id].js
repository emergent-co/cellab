// GET  /api/admin/docs/:id            → 문서 상세(스냅샷 포함)
// POST /api/admin/docs/:id  {action}  → send(즉시/예약) · cancel(예약취소) · void(취소처리)
import { json, isAdmin, needAdmin, kstISO, logEvent, DOC_LABEL, adminOK} from '../../_lib.js';
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
    return json({ document: doc, payload, events, queued, siblings, linked,
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
