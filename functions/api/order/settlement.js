// GET /api/order/settlement → 정산하기 화면에 필요한 전부 (한 번의 요청으로)
//   지출/정산/잔여 + 원장, 계산서 발행 정보, 발급 서류까지 함께 준다.
//   화면 하나를 그리려고 API를 세 번 왕복하면 그만큼 빈 화면이 길어진다.
//   숫자는 결제 방식과 상관없이 항상 준다 — 선불이라고 빼면 주문 금액이 있는데도 0원으로 보인다.
import { json, currentCustomer, memberGate} from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);
  const gate = memberGate(me); if (gate) return gate;

  const [profiles, documents] = await Promise.all([
    env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id DESC')
      .bind(me.id).all().then((r) => r.results || []),
    // 주문 없이 바로 발행한 서류도 내 것이면 보여준다 (거래처로만 등록된 건)
    env.DB.prepare(
      `SELECT d.id, d.type, d.doc_no, d.status, d.issue_date, d.sent_at, d.opened_at,
              o.order_no,
              COALESCE(o.title, json_extract(d.payload_json, '$.title')) AS title
         FROM documents d LEFT JOIN orders o ON o.id = d.order_id
        WHERE o.customer_id = ?1 OR d.customer_id = ?1
        ORDER BY d.id DESC LIMIT 200`
    ).bind(me.id).all().then((r) => r.results || []),
  ]);

  const s = await settlement(env, me.id);
  const rows = await ledger(env, me.id);
  return json({ postpaid: true, ...s, ledger: rows, profiles, documents });
}
