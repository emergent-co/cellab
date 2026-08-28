// 고객의 정산 요청
//   GET  /api/order/settlements  → 내 요청 목록
//   POST /api/order/settlements  → 새 요청
import { json, currentCustomer, kstISO, logEvent, memberGate} from '../_lib.js';

export const SETTLE_STATUS = ['정산요청', '처리중', '서류발급 완료', '입금완료', '반려'];

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);
  const gate = memberGate(me); if (gate) return gate;

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT * FROM settlements WHERE customer_id=? ORDER BY id DESC LIMIT 100'
    ).bind(me.id).all();
    return json({
      settlements: (results || []).map((r) => ({ ...r, items: safe(r.items_json) })),
    });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const items = (Array.isArray(b.items) ? b.items : [])
    .map((i) => ({
      name: String(i.name || '').trim(),
      qty: Math.max(1, Number(i.qty) || 1),
      price: Math.round(Number(i.price) || 0),
    }))
    .filter((i) => i.name);

  if (!items.length) return json({ error: 'no_items', message: '항목을 1개 이상 입력해주세요.' }, 400);

  const method = b.method === '카드' ? '카드' : '통장';
  const email = String(b.reply_email || '').trim();
  if (!email) return json({ error: 'no_email', message: '회신받을 이메일을 입력해주세요.' }, 400);

  // 필요 서류 날짜 — 카드결제는 세금계산서를 발행하지 않는다(매출전표로 갈음)
  const qd = String(b.quote_date || '').trim();
  const sd = String(b.statement_date || '').trim();
  const td = method === '카드' ? '' : String(b.taxinvoice_date || '').trim();
  if (!qd || !sd || (method !== '카드' && !td)) {
    return json({ error: 'no_dates', message: '필요 서류의 날짜를 모두 입력해주세요.' }, 400);
  }

  const supply = items.reduce((s, i) => s + i.qty * i.price, 0);
  const vat = Math.round(supply * 0.1);
  const now = kstISO();

  const r = await env.DB.prepare(
    `INSERT INTO settlements (customer_id, status, items_json, supply, vat, total, method,
       quote_date, statement_date, taxinvoice_date, reply_email, memo, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(me.id, '정산요청', JSON.stringify(items), supply, vat, supply + vat, method,
         qd, sd, td, email, String(b.memo || ''), now, now).run();

  await logEvent(env, {
    action: 'settle_request', actor: 'customer',
    detail: `정산 요청 ${items[0].name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''} · ${(supply + vat).toLocaleString('ko-KR')}원`,
  });

  return json({ ok: true, id: r.meta.last_row_id });
}

function safe(s) { try { return JSON.parse(s || '[]'); } catch { return []; } }
