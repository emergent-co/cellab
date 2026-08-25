// GET /api/order/settlement → 정산하기 화면에 필요한 전부 (한 번의 요청으로)
//   후불이면 지출/정산/잔여 + 원장, 그리고 계산서 발행 정보 · 발급 서류까지 함께 준다.
//   화면 하나를 그리려고 API를 세 번 왕복하면 그만큼 빈 화면이 길어진다.
import { json, currentCustomer } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  const postpaid = (me.billing_mode || '선불') === '후불';

  const [profiles, documents] = await Promise.all([
    env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id DESC')
      .bind(me.id).all().then((r) => r.results || []),
    env.DB.prepare(
      `SELECT d.id, d.type, d.doc_no, d.status, d.issue_date, d.sent_at, d.opened_at,
              o.order_no, o.title
         FROM documents d JOIN orders o ON o.id = d.order_id
        WHERE o.customer_id = ? ORDER BY d.id DESC LIMIT 200`
    ).bind(me.id).all().then((r) => r.results || []),
  ]);

  if (!postpaid) return json({ postpaid: false, profiles, documents });

  const s = await settlement(env, me.id);
  const rows = await ledger(env, me.id);
  return json({ postpaid: true, ...s, ledger: rows, profiles, documents });
}
