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
  // 계산서 발행 정보 — 내 것인지 확인하고, 없으면 기본값을 쓴다
  let billId = Number(b.bill_profile_id) || null;
  if (billId) {
    const own = await env.DB.prepare('SELECT id FROM bill_profiles WHERE id=? AND customer_id=?')
      .bind(billId, me.id).first();
    if (!own) billId = null;
  }
  if (!billId) {
    const def = await env.DB.prepare('SELECT id FROM bill_profiles WHERE customer_id=? AND is_default=1')
      .bind(me.id).first();
    billId = def?.id || null;
  }
  const email = String(b.reply_email || '').trim();
  if (!email) return json({ error: 'no_email', message: '회신받을 이메일을 입력해주세요.' }, 400);

  // 필요 서류 날짜 — 카드결제는 세금계산서를 발행하지 않는다(매출전표로 갈음)
  const qd = String(b.quote_date || '').trim();
  const sd = String(b.statement_date || '').trim();
  const td = method === '카드' ? '' : String(b.taxinvoice_date || '').trim();
  if (!qd || !sd || (method !== '카드' && !td)) {
    return json({ error: 'no_dates', message: '필요 서류의 날짜를 모두 입력해주세요.' }, 400);
  }

  // 금액은 '부가세 포함 단가'로 받는다.
  //   공급가액에 1.1을 곱하면 999,100.1 처럼 지저분한 값이 나와 서류가 안 맞는다.
  //   총액을 먼저 10원 단위로 확정하고 거기서 공급가액을 역산하면 항상 딱 떨어진다.
  //     총액 T (10원 단위) → 공급가액 S = round(T / 1.1) → 부가세 V = T − S  (S+V = T 보장)
  const round10 = (n) => Math.round(Number(n || 0) / 10) * 10;
  let supply, vat, total;
  if (b.vat_included) {
    total = items.reduce((s, i) => s + round10(i.qty * i.price), 0);
    supply = Math.round(total / 1.1);
    vat = total - supply;
  } else {
    supply = items.reduce((s, i) => s + i.qty * i.price, 0);
    vat = Math.round(supply * 0.1);
    total = supply + vat;
  }
  const now = kstISO();

  const r = await env.DB.prepare(
    `INSERT INTO settlements (customer_id, status, items_json, supply, vat, total, method,
       quote_date, statement_date, taxinvoice_date, reply_email, memo, bill_profile_id, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(me.id, '정산요청', JSON.stringify(items), supply, vat, total, method,
         qd, sd, td, email, String(b.memo || ''), billId, now, now).run();

  await logEvent(env, {
    action: 'settle_request', actor: 'customer',
    detail: `정산 요청 ${items[0].name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''} · ${total.toLocaleString('ko-KR')}원`,
  });

  return json({ ok: true, id: r.meta.last_row_id });
}

function safe(s) { try { return JSON.parse(s || '[]'); } catch { return []; } }
