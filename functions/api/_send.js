// functions/api/_send.js — 문서 발송 공통 로직 (즉시 발송 · 예약 큐 처리에서 공용)
import { kstISO, logEvent, DOC_LABEL } from './_lib.js';
import { renderDocHTML } from './_doctpl.js';
import { getOrMakePdf, pdfConfigured, b64 } from './_pdf.js';
import { sendMail, mailConfigured } from './_mailer.js';

export function calcTotals(items, fixed) {
  if (fixed && Number(fixed.total)) {
    return { supply: Math.round(Number(fixed.supply) || 0),
             vat: Math.round(Number(fixed.vat) || 0),
             total: Math.round(Number(fixed.total) || 0) };
  }
  const supply = (items || []).reduce(
    (s, i) => s + Math.round((Number(i.qty) || 0) * (Number(i.unit_price) || 0)), 0);
  const vat = Math.round(supply * 0.1);
  return { supply, vat, total: supply + vat };
}

// 문서 한 건 — 아래 deliverMany 를 그대로 쓴다.
export async function deliver(env, { doc, payload, to, cc, subject, html, actor = 'admin' }) {
  return deliverMany(env, { docs: [{ doc, payload }], to, cc, subject, html, actor });
}

/**
 * 여러 문서를 메일 '한 통'으로 보낸다.
 * 견적서·거래명세서·세금계산서를 한 벌로 뽑았으면 고객도 한 통으로 받아야 한다.
 * 세 통으로 나눠 보내면 받는 쪽에서 어느 게 짝인지 알 수 없다.
 * @param docs [{ doc, payload }]
 */
export async function deliverMany(env, { docs, to, cc, subject, html, actor = 'admin' }) {
  const list = (docs || []).filter((x) => x && x.doc);
  if (!list.length) return { ok: false, error: '보낼 문서가 없습니다' };

  const logAll = (e) => Promise.all(list.map(({ doc }) =>
    logEvent(env, { order_id: doc.order_id, document_id: doc.id, ...e })));

  if (!mailConfigured(env)) {
    const err = 'RESEND_API_KEY 미설정';
    await logAll({ action: 'send', channel: 'email', actor, to_addr: to, result: 'fail', detail: err });
    return { ok: false, error: err };
  }

  // 첨부는 전부 붙거나, 아예 안 보내거나 둘 중 하나다.
  // 두 장 중 한 장만 간 메일은 받는 쪽에서 알아챌 방법이 없다 — 그게 제일 나쁘다.
  const attachments = [];
  const missing = [];
  let linkOnly = '';        // PDF 를 못 만들어 링크로만 보낸 경우의 사유
  if (pdfConfigured(env)) {
    for (const { doc, payload } of list) {
      const label = DOC_LABEL[doc.type] || '문서';
      try {
        const { bytes } = await getOrMakePdf(env, doc, renderDocHTML(payload));
        attachments.push({ filename: `${label}_${doc.doc_no}.pdf`, content: b64(bytes) });
      } catch (e) {
        missing.push(`${label} ${doc.doc_no}`);
        await logEvent(env, { order_id: doc.order_id, document_id: doc.id, action: 'pdf',
          actor: 'system', result: 'fail', detail: String(e?.message || e) });
      }
    }
    if (missing.length) {
      // 한 장만 붙은 메일은 받는 쪽에서 빠진 걸 알 방법이 없다 — 그래서 첨부는 전부 아니면 전무다.
      // 다만 «아예 못 보냄»으로 끝내지는 않는다. 메일 본문에는 문서 링크가 이미 들어 있으니,
      // 첨부를 모두 떼고 링크로 보낸다. 고객은 열어볼 수 있고, 나중에 PDF 로 다시 보낼 수도 있다.
      attachments.length = 0;
      linkOnly = `${missing.join(', ')} 의 PDF를 만들지 못했습니다`;
      await logAll({ action: 'pdf', actor: 'system', result: 'fail',
        detail: `${linkOnly} — 첨부 없이 링크로 보냅니다` });
    }
  }

  const body = linkOnly
    ? String(html || '').replace(/<\/div>\s*$/,
        '<p style="color:#92400E;font-size:13px;background:#FFFBF3;border:1px solid #F0C98A;'
        + 'border-radius:9px;padding:11px 13px">PDF 파일 첨부가 준비되지 않아 <b>문서 링크로 보내드립니다.</b> '
        + '위 버튼으로 열어보실 수 있고, 필요하시면 PDF 로 다시 보내드리겠습니다.</p></div>')
    : html;

  const r = await sendMail(env, { to, cc, subject, html: body, attachments });
  const now = kstISO();

  if (!r.ok) {
    await logAll({ action: 'send', channel: 'email', actor, to_addr: to, result: 'fail', detail: r.error });
    return { ok: false, error: r.error };
  }

  const names = list.map(({ doc }) => `${DOC_LABEL[doc.type] || '문서'} ${doc.doc_no}`).join(', ');
  for (const { doc } of list) {
    await env.DB.prepare("UPDATE documents SET status='발송됨', sent_at=?, updated_at=? WHERE id=?")
      .bind(now, now, doc.id).run();

    // 주문에서 만든 문서만 주문 상태를 옮긴다 — 단독 발행 건에는 옮길 주문이 없다.
    if (doc.order_id) {
      if (doc.type === 'quote') {
        await env.DB.prepare("UPDATE orders SET status='견적발송', updated_at=? WHERE id=? AND status IN ('요청접수','보류')")
          .bind(now, doc.order_id).run();
      } else if (doc.type === 'statement') {
        await env.DB.prepare("UPDATE orders SET status='배송중', updated_at=? WHERE id=? AND status IN ('발주확정','견적승인')")
          .bind(now, doc.order_id).run();
      }
    }

    await logEvent(env, {
      order_id: doc.order_id, document_id: doc.id, action: 'sent', channel: 'email',
      actor, to_addr: to, result: 'ok',
      detail: (list.length > 1 ? `${names} 한 통으로 발송` : names)
            + (attachments.length ? ` (PDF ${attachments.length}건 첨부)` : ' (PDF 미첨부)'),
    });
  }
  return { ok: true, sent: list.length, attached: attachments.length,
           link_only: linkOnly || null };
}

// 예약 큐 처리 — 발송 시각이 지난 '대기' 건을 보낸다.
export async function flushOutbox(env, limit = 10) {
  const now = kstISO();
  const { results } = await env.DB.prepare(
    "SELECT * FROM outbox WHERE status='대기' AND send_at <= ? ORDER BY send_at LIMIT ?"
  ).bind(now, limit).all();

  let sent = 0, failed = 0;
  for (const job of results || []) {
    // doc_ids 가 있으면 한 벌로 예약한 건 — 한 통에 모두 첨부해 보낸다
    let ids = [];
    try { ids = JSON.parse(job.doc_ids || 'null') || []; } catch { ids = []; }
    if (!ids.length && job.document_id) ids = [job.document_id];

    const docs = [];
    for (const id of ids) {
      const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(id).first();
      if (!doc) continue;
      let payload = {};
      try { payload = JSON.parse(doc.payload_json || '{}'); } catch { /* noop */ }
      docs.push({ doc, payload });
    }
    if (!docs.length) {
      await env.DB.prepare("UPDATE outbox SET status='실패', last_error='문서 없음' WHERE id=?").bind(job.id).run();
      failed++; continue;
    }

    const r = await deliverMany(env, {
      docs, to: job.to_addr, cc: job.cc_addr,
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
