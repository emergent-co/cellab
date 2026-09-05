// functions/api/_send.js — 문서 발송 공통 로직 (즉시 발송 · 예약 큐 처리에서 공용)
import { kstISO, logEvent, DOC_LABEL } from './_lib.js';
import { renderDocHTML } from './_doctpl.js';
import { getOrMakePdf, pdfConfigured, b64 } from './_pdf.js';
import { sendMail, mailConfigured, mailBcc } from './_mailer.js';
import { notifyShipped } from './_notify.js';

export function calcTotals(items, fixed) {
  if (fixed && Number(fixed.total)) {
    return { supply: Math.round(Number(fixed.supply) || 0),
             vat: Math.round(Number(fixed.vat) || 0),
             total: Math.round(Number(fixed.total) || 0) };
  }
  // 저장된 총계가 없을 때의 예비 계산 — 발행 때와 같은 «원 단위 절삭» 규칙을 쓴다
  let supply = 0, vat = 0;
  for (const i of items || []) {
    const line = Math.round((Number(i.qty) || 0) * (Number(i.unit_price) || 0));
    supply += line;
    vat += Math.floor(line * 0.1 / 10) * 10;   // 발행 때(compute)와 같은 «줄마다 10원 절삭»
  }
  return { supply, vat, total: supply + vat };
}

// 문서 한 건 — 아래 deliverMany 를 그대로 쓴다.
export async function deliver(env, { doc, payload, to, cc, subject, html, actor = 'admin', files, origin }) {
  return deliverMany(env, { docs: [{ doc, payload }], to, cc, subject, html, actor, files, origin });
}

/**
 * 여러 문서를 메일 '한 통'으로 보낸다.
 * 견적서·거래명세서·세금계산서를 한 벌로 뽑았으면 고객도 한 통으로 받아야 한다.
 * 세 통으로 나눠 보내면 받는 쪽에서 어느 게 짝인지 알 수 없다.
 * @param docs [{ doc, payload }]
 */
export async function deliverMany(env, { docs, to, cc, subject, html, actor = 'admin', files, origin }) {
  /* 취소한 문서는 어느 경로로도 나가면 안 된다. 묶음 발송 화면에는 검사가 있었지만
     예약 큐와 단건 발송에는 없어서, 3종 중 하나만 취소해도 예약 시각에 셋 다 나갔다. */
  const list = (docs || []).filter((x) => x && x.doc && x.doc.status !== '취소됨');
  if (!list.length) return { ok: false, error: '보낼 문서가 없습니다 (취소된 문서는 보내지 않습니다)' };
  /* 내용을 못 읽은 서류는 «합계 0원» 짜리 빈 메일이 되어 나간다 — 그럴 바엔 보내지 않는다. */
  const empty = list.filter(({ payload }) => !payload || !Array.isArray(payload.items) || !payload.items.length);
  if (empty.length) {
    return { ok: false, error: `문서 내용을 읽지 못했습니다 (${empty.map(({ doc }) => doc.doc_no).join(', ')})` };
  }

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

  // 손으로 붙인 파일은 서류 PDF 와 운명을 같이하지 않는다 —
  // PDF 생성이 실패해 첨부를 다 떼는 경우에도 이건 그대로 나가야 한다.
  const extra = (files || [])
    .map((f) => ({ filename: String(f.name || 'file').slice(0, 120), content: String(f.b64 || '') }))
    .filter((f) => f.content);
  // 보낸 서류는 지메일에도 한 통 남긴다 — 숨은참조라 고객에게는 보이지 않는다
  const r = await sendMail(env, { to, cc, bcc: mailBcc(env), subject, html: body,
    attachments: attachments.concat(extra) });
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
        /* 거래명세서가 나갔다 = 물건이 나갔다. 전에는 상태만 바꾸고 끝나서
           shipped_at 이 안 남고 «수령 확인하기» 안내도 고객에게 안 갔다.
           («견적발송»·«요청접수» 상태에서 바로 명세서를 보내는 일도 흔해서 조건도 넓혔다) */
        const up = await env.DB.prepare(
          "UPDATE orders SET status='배송중', updated_at=? WHERE id=? AND status IN ('요청접수','견적발송','견적승인','발주확정','보류')")
          .bind(now, doc.order_id).run();
        if (up?.meta?.changes) {
          const ord = await env.DB.prepare('SELECT * FROM orders WHERE id=?').bind(doc.order_id).first();
          // 알림이 실패해도 발송 자체를 되돌리지는 않는다 — 이력에는 남는다
          if (ord) {
            try { await notifyShipped(env, origin || 'https://rndsetup.com', ord); }
            catch (e) {
              await logEvent(env, { order_id: ord.id, document_id: doc.id, action: 'notify', actor: 'system',
                result: 'fail', detail: `발송 안내 실패: ${String(e?.message || e)}` });
            }
          }
        }
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
    /* 큐를 도는 입구가 여럿이다 — 5분 워커, 관리자 화면 진입, 예약 직후 호출.
       집어만 두고 발송이 끝나야 상태를 바꾸면, 그 사이 다른 입구가 같은 행을 또 집어
       고객에게 같은 견적서가 두 통 간다. 먼저 «발송중» 으로 찜하고, 찜에 성공한 것만 보낸다. */
    const claim = await env.DB.prepare(
      "UPDATE outbox SET status='발송중' WHERE id=? AND status='대기'").bind(job.id).run();
    if (!claim?.meta || claim.meta.changes !== 1) continue;

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

    // 발송 도중 예외가 나면 «발송중» 인 채로 굳어 영영 안 나간다 — 반드시 되돌린다
    let r;
    try {
      r = await deliverMany(env, {
        docs, to: job.to_addr, cc: job.cc_addr,
        subject: job.subject, html: job.body, actor: 'system',
      });
    } catch (e) {
      r = { ok: false, error: String(e?.message || e) };
    }

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
