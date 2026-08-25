// GET /api/order/settlement → 내 정산 현황 (후불 고객용)
import { json, currentCustomer } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

export async function onRequestGet({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  const postpaid = (me.billing_mode || '선불') === '후불';
  if (!postpaid) return json({ postpaid: false });

  const s = await settlement(env, me.id);
  const rows = await ledger(env, me.id);
  return json({ postpaid: true, ...s, ledger: rows });
}
