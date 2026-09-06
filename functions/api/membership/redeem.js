// POST /api/membership/redeem  { code }  → 가입코드로 멤버십 전환
//   로그인(카카오) 한 사람만 쓸 수 있다. 코드가 맞으면 그 자리에서
//   access='승인' · billing_mode='후불' 로 올려 /member/ 를 연다.
import { json, currentCustomer, kstISO, logEvent, isApproved, isBlocked } from '../_lib.js';
import { sendMail, mailConfigured, mailReplyTo } from '../_mailer.js';

export async function onRequestPost({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required', message: '먼저 카카오로 로그인해주세요.' }, 401);
  if (isBlocked(me)) return json({ error: 'blocked', message: '이용이 제한된 계정입니다.' }, 403);
  if (isApproved(me)) return json({ ok: true, already: true, message: '이미 멤버십 회원입니다.' });

  const b = await request.json().catch(() => ({}));
  // 사람이 메일에서 복사해 붙인다 — 공백·대소문자·하이픈은 서버가 흡수한다
  const code = String(b.code || '').trim().toUpperCase().replace(/[\s-]/g, '');
  if (!code) return json({ error: 'no_code', message: '가입코드를 입력해주세요.' }, 400);

  const row = await env.DB.prepare('SELECT * FROM member_codes WHERE code=?').bind(code).first();
  if (!row) return json({ error: 'bad_code', message: '없는 코드입니다. 메일에 적힌 코드를 다시 확인해주세요.' }, 400);
  if (row.used_by) {
    return json({ error: 'used_code', message: '이미 사용된 코드입니다. 새 코드가 필요하시면 연락 주세요.' }, 400);
  }
  const now = kstISO();
  if (row.expires_at && String(row.expires_at) < now) {
    return json({ error: 'expired_code', message: '만료된 코드입니다. 새 코드를 요청해주세요.' }, 400);
  }

  /* 코드 소모와 계정 승격은 한 배치로 묶는다.
     둘 사이에서 끊기면 코드는 살아 있는데 계정은 안 올라가거나(재시도 가능),
     계정만 올라가고 코드가 남아 두 번째 사람이 같은 코드로 또 들어온다. */
  await env.DB.batch([
    env.DB.prepare('UPDATE member_codes SET used_by=?, used_at=? WHERE code=? AND used_by IS NULL')
      .bind(me.id, now, code),
    env.DB.prepare("UPDATE customers SET access='승인', billing_mode='후불', updated_at=? WHERE id=?")
      .bind(now, me.id),
    env.DB.prepare(
      `UPDATE membership_requests SET status='가입완료', customer_id=?, updated_at=? WHERE id=?`
    ).bind(me.id, now, row.request_id || 0),
  ]);

  await logEvent(env, {
    action: 'membership_redeem', actor: `cust:${me.id}`,
    detail: `${me.name || ''}${me.company ? ` (${me.company})` : ''} 가입코드 ${code} 사용 → 멤버십(후불)`,
  });

  if (mailConfigured(env)) {
    await sendMail(env, {
      to: mailReplyTo(env),
      subject: `[멤버십 가입] ${me.name || ''} · ${me.company || ''}`,
      html: `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif">
        <p>가입코드 <b>${code}</b> 가 사용되었습니다.</p>
        <p>계정 #${me.id} ${me.name || ''} (${me.email || ''}) → 승인 · 후불</p></div>`,
    }).catch(() => {});
  }

  return json({ ok: true, message: '멤버십이 열렸습니다.', next: '/member/' });
}
