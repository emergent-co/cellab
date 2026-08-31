// GET  /api/auth/me     → 로그인 상태 + 거래처 정보
// POST /api/auth/me     → 거래처 정보 저장
// DELETE /api/auth/me   → 로그아웃
import { json, currentCustomer, dropSession, clearCookie, kstISO,
         isMember, isApproved, isPostpaid } from '../_lib.js';
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
    const admin = me.role === 'admin';
    // 못 들어오는 이유를 구분해서 준다 — 승인 전인지, 선불 거래처인지에 따라 갈 곳이 다르다
    if (!admin && !isMember(me)) {
      return json({ login: true, member: false, admin,
        reason: isApproved(me) && !isPostpaid(me) ? 'prepaid' : 'pending',
        customer: me, lab: null, members: [] });
    }
    const info = await labInfo(env, me);
    return json({ login: true, member: true, admin, customer: me, lab: info.lab, members: info.members });
  }

  if (request.method === 'POST') {
    const b = await request.json().catch(() => ({}));
    // 업무 이메일은 서류가 실제로 가는 곳이라 형식을 서버에서도 확인한다
    if (b.work_email !== undefined) {
      const we = String(b.work_email).trim();
      if (!we || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(we)) {
        return json({ error: 'bad_work_email', message: '업무 이메일 형식을 확인해주세요.' }, 400);
      }
      b.work_email = we;
    }
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
