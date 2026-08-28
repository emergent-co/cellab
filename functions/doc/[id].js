// GET /doc/:id?t=<access_token>        → 문서 HTML (인쇄 가능)
// GET /doc/:id?t=<access_token>&f=pdf  → PDF 다운로드
// 관리자 Basic Auth 또는 로그인한 주문 당사자도 열람 가능.
import { isAdmin, currentCustomer, kstISO, logEvent, DOC_LABEL, adminOK} from '../api/_lib.js';
import { renderDocHTML } from '../api/_doctpl.js';
import { getOrMakePdf, pdfConfigured } from '../api/_pdf.js';

export async function onRequestGet({ request, env, params }) {
  const url = new URL(request.url);
  const doc = await env.DB.prepare('SELECT * FROM documents WHERE id=?').bind(params.id).first();
  if (!doc) return new Response('문서를 찾을 수 없습니다.', { status: 404, headers: htxt() });

  // ---- 권한 ----
  const token = url.searchParams.get('t') || '';
  let viewer = null;
  if (await adminOK(request, env)) viewer = 'admin';
  else if (token && doc.access_token && token === doc.access_token) viewer = 'link';
  else {
    const me = await currentCustomer(request, env);
    if (me) {
      const own = await env.DB.prepare('SELECT id FROM orders WHERE id=? AND customer_id=?')
        .bind(doc.order_id, me.id).first();
      if (own) viewer = 'customer';
    }
  }
  if (!viewer) return new Response('열람 권한이 없습니다.', { status: 403, headers: htxt() });

  let payload;
  try { payload = JSON.parse(doc.payload_json || '{}'); } catch { payload = {}; }
  const html = renderDocHTML(payload);

  // 고객 최초 열람 기록
  if (viewer !== 'admin' && !doc.opened_at) {
    await env.DB.prepare("UPDATE documents SET opened_at=?, status=CASE WHEN status='발송됨' THEN '열람됨' ELSE status END WHERE id=?")
      .bind(kstISO(), doc.id).run();
    await logEvent(env, {
      order_id: doc.order_id, document_id: doc.id, action: 'opened',
      channel: viewer === 'link' ? 'email' : 'web', actor: 'customer',
      detail: `${DOC_LABEL[doc.type] || doc.type} ${doc.doc_no} 열람`,
    });
  }

  if (url.searchParams.get('f') === 'pdf') {
    if (!pdfConfigured(env)) return new Response('PDF 생성이 아직 설정되지 않았습니다.', { status: 503, headers: htxt() });
    try {
      const { bytes } = await getOrMakePdf(env, doc, html);
      const name = `${DOC_LABEL[doc.type] || '문서'}_${doc.doc_no}.pdf`;
      return new Response(bytes, {
        headers: {
          'content-type': 'application/pdf',
          'content-disposition': `inline; filename*=UTF-8''${encodeURIComponent(name)}`,
          'cache-control': 'private, max-age=300',
        },
      });
    } catch (e) {
      return new Response(String(e?.message || e), { status: 502, headers: htxt() });
    }
  }

  return new Response(html, {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
  });
}

function htxt() {
  return { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' };
}
