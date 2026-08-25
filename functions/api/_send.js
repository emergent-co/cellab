// functions/api/_send.js — 문서 발송 공통 로직 (즉시 발송 · 예약 큐 처리에서 공용)
import { kstISO, logEvent, DOC_LABEL } from './_lib.js';
import { renderDocHTML } from './_doctpl.js';
import { getOrMakePdf, pdfConfigured, b64 } from './_pdf.js';
import { sendMail, mailConfigured } from './_mailer.js';

export function calcTotals(items) {
  const supply = (items || []).reduce(
    (s, i) => s + Math.round((Number(i.qty) || 0) * (Number(i.unit_price) || 0)), 0);
  const vat = Math.round(supply * 0.1);
  return { supply, vat, total: supply + vat };
}

export async function deliver(env, { doc, payload, to, cc, subject, html, actor = 'admin' }) {
  const label = DOC_LABEL[doc.type] || '문서';

  if (!mailConfigured(env)) {
    const err = 'RESEND_API_KEY 미설정';
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'send',
      channel: 'email', actor, to_addr: to, result: 'fail', detail: err });
    return { ok: false, error: err };
  }

  const attachments = [];
  if (pdfConfigured(env)) {
    try {
      const { bytes } = await getOrMakePdf(env, doc, renderDocHTML(payload));
      attachments.push({ filename: `${label}_${doc.doc_no}.pdf`, content: b64(bytes) });
    } catch (e) {
      await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'pdf',
        actor: 'system', result: 'fail', detail: String(e?.message || e) });
    }
  }

  const r = await sendMail(env, { to, cc, subject, html, attachments });
  const now = kstISO();

  if (!r.ok) {
    await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'send',
      channel: 'email', actor, to_addr: to, result: 'fail', detail: r.error });
    return { ok: false, error: r.error };
  }

  await env.DB.prepare("UPDATE documents SET status='발송됨', sent_at=?, updated_at=? WHERE id=?")
    .bind(now, now, doc.id).run();

  if (doc.type === 'quote') {
    await env.DB.prepare("UPDATE orders SET status='견적발송', updated_at=? WHERE id=? AND status IN ('요청접수','보류')")
      .bind(now, doc.order_id).run();
  } else if (doc.type === 'statement') {
    await env.DB.prepare("UPDATE orders SET status='배송중', updated_at=? WHERE id=? AND status IN ('발주확정','견적승인')")
      .bind(now, doc.order_id).run();
  }

  await logEvent(env, {
    order_id: doc.order_id, document_id: doc.id, action: 'sent', channel: 'email',
    actor, to_addr: to, result: 'ok',
    detail: `${label} ${doc.doc_no} 발송${attachments.length ? ' (PDF 첨부)' : ' (PDF 미첨부)'}`,
  });
  return { ok: true };
}

// 예약 큐 처리 — 발송 시각이 지난 '대기' 건을 보낸다.
export async function flushOutbox(env, limit = 10) {
  const now = kstISO();
  const { results } = await env.DB.prepare(
    "SELECT * FROM outbox WHERE status='대기' AND send_at <= ? ORDER BY send_at LIMIT ?"
  ).bind(now, limit).all();

  let sent = 0, failed = 0;
  for (const job of results || []) {
    const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(job.document_id).first();
    if (!doc) {
      await env.DB.prepare("UPDATE outbox SET status='실패', last_error='문서 없음' WHERE id=?").bind(job.id).run();
      failed++; continue;
    }
    let payload = {};
    try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }

    const r = await deliver(env, {
      doc, payload, to: job.to_addr, cc: job.cc_addr,
      subject: job.subject, html: job.body, actor: 'system',
    });

    if (r.ok) {
      await env.DB.prepare("UPDATE outbox SET status='발송됨', sent_at=?, tries=tries+1 WHERE id=?")
        .bind(kstISO(), job.id).run();
      sent++;
    } else {
      const tries = (job.tries || 0) + 1;
      const status = tries >= 3 ? '실패' : '대기';
      await env.DB.prepare('UPDATE outbox SET status=?, tries=?, last_error=? WHERE id=?')
        .bind(status, tries, r.error, job.id).run();
      failed++;
    }
  }
  return { sent, failed, picked: (results || []).length };
}
