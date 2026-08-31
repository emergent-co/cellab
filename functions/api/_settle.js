// functions/api/_settle.js — 후불(멤버십) 정산 계산 공통
//   지출금   = 그 거래처 주문 금액 합계 (취소 제외) — 주문에 단가를 넣는 순간 오른다
//   중간정산금 = payments 합계 (입금 + 조정, 조정은 음수 가능)
//   정산금 잔여 = 지출금 − 중간정산금
// 지출을 따로 적어두지 않는다: 장부를 두 벌 두면 반드시 어긋난다.

export async function settlement(env, customerId) {
  // 두 합계를 한 번의 왕복으로 — 따로 물으면 그만큼 느려진다
  const r = await env.DB.prepare(
    `SELECT COALESCE((SELECT SUM(total_amount) FROM orders
                       WHERE customer_id=?1 AND status<>'취소'),0) AS spent,
            COALESCE((SELECT SUM(amount) FROM payments WHERE customer_id=?1),0) AS paid`
  ).bind(customerId).first();
  const spent = r?.spent || 0;
  const paid = r?.paid || 0;
  return { spent, paid, due: spent - paid };
}

// 주문·입금을 한 줄씩 시간순으로 엮은 원장 (잔액 누적 포함)
export async function ledger(env, customerId, limit = 200) {
  const rs = await env.DB.batch([
    env.DB.prepare(`SELECT id, order_no, title, total_amount, created_at
                      FROM orders WHERE customer_id=? AND status<>'취소' AND total_amount>0`).bind(customerId),
    env.DB.prepare('SELECT id, kind, amount, method, paid_at, memo, created_at FROM payments WHERE customer_id=?')
      .bind(customerId),
  ]);
  const os = (rs[0] && rs[0].results) || [];
  const ps = (rs[1] && rs[1].results) || [];

  const rows = []
    .concat(os.map((o) => ({
      at: (o.created_at || '').slice(0, 10),
      kind: '지출', label: o.title || o.order_no, ref: o.order_no,
      amount: o.total_amount, order_id: o.id,
    })))
    .concat(ps.map((p) => ({
      at: (p.paid_at || p.created_at || '').slice(0, 10),
      kind: p.kind || '입금', label: p.memo || (p.method ? p.method + ' 입금' : '입금'),
      ref: p.method || '', amount: -p.amount, payment_id: p.id,
    })))
    .sort((a, b) => (a.at < b.at ? -1 : a.at > b.at ? 1 : 0));

  let bal = 0;
  for (const r of rows) { bal += r.amount; r.balance = bal; }
  return rows.reverse().slice(0, limit);   // 최신이 위로
}
