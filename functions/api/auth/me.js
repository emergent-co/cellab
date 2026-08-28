// GET  /api/auth/me     → 로그인 상태 + 거래처 정보
// POST /api/auth/me     → 거래처 정보 저장
// DELETE /api/auth/me   → 로그아웃
import { json, currentCustomer, dropSession, clearCookie, kstISO, isVip } from '../_lib.js';
import { labInfo } from '../order/lab.js';

const FIELDS = ['name', 'email', 'work_email', 'phone', 'company', 'biz_no', 'ceo', 'biz_type', 'biz_item', 'tax_email', 'address'];

export async function onRequest({ request, env }) {
  if (request.method === 'DELETE') {
    await dropSession(request, env);
    return json({ ok: true }, 200, { 'Set-Cookie': clearCookie() });
  }

  const me = await currentCustomer(request, env);
  if (!me) return json({ login: false }, 200);

  if (request.method === 'GET') {
    // 승인 전이면 실험실을 만들거나 조회하지 않는다 — 거래처가 확정된 뒤의 개념이다
    if (!isVip(me)) return json({ login: true, vip: false, customer: me, lab: null, members: [] });
    const info = await labInfo(env, me);
    return json({ login: true, vip: true, customer: me, lab: info.lab, members: info.members });
  }

  if (request.method === 'POST') {
    const b = await request.json().catch(() => ({}));
    const sets = [], vals = [];
    for (const f of FIELDS) {
      if (b[f] !== undefined) { sets.push(`${f}=?`); vals.push(String(b[f]).trim()); }
    }
    if (!sets.length) return json({ error: 'no_fields' }, 400);
    sets.push('updated_at=?'); vals.push(kstISO(), me.id);
    await env.DB.prepare(`UPDATE customers SET ${sets.join(', ')} WHERE id=?`).bind(...vals).run();
    const row = await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(me.id).first();
    return json({ ok: true, customer: row });
  }

  return json({ error: 'method_not_allowed' }, 405);
}
