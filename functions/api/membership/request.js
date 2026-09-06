// POST /api/membership/request — 멤버십 가입 요청 (로그인 없이도 보낼 수 있다)
//   카카오 «바로 시작»으로는 멤버십이 열리지 않는다. 여기 남긴 요청을 사장이 읽고
//   가입코드를 메일로 보내주면, 그 코드로만 후불 장부에 오른다.
import { json, currentCustomer, kstISO, esc, logEvent } from '../_lib.js';
import { sendMail, mailConfigured, mailReplyTo } from '../_mailer.js';

export async function onRequestPost({ request, env }) {
  const b = await request.json().catch(() => ({}));

  const name  = String(b.name     || '').trim().slice(0, 60);
  const org   = String(b.org_name || '').trim().slice(0, 120);
  const email = String(b.email    || '').trim().slice(0, 120);
  const phone = String(b.phone    || '').trim().slice(0, 40);
  const note  = String(b.note     || '').trim().slice(0, 2000);

  if (!name) return json({ error: 'no_name', message: '성함을 입력해주세요.' }, 400);
  if (!org)  return json({ error: 'no_org',  message: '소속(기관·연구실·회사)을 입력해주세요.' }, 400);
  // 코드를 메일로 보내야 하므로 이메일은 선택이 아니다
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'bad_email', message: '가입코드를 받을 이메일을 정확히 입력해주세요.' }, 400);
  }

  const me = await currentCustomer(request, env).catch(() => null);
  const now = kstISO();

  /* 같은 메일로 이미 «접수/코드발급» 건이 살아 있으면 새로 쌓지 않는다.
     목록에 같은 사람이 여러 줄로 늘어나면 어느 줄에 코드를 냈는지 헷갈린다. */
  const dup = await env.DB.prepare(
    `SELECT id, status, code FROM membership_requests
      WHERE email=? AND status IN ('접수','코드발급') ORDER BY id DESC LIMIT 1`
  ).bind(email).first();
  if (dup) {
    await env.DB.prepare(
      'UPDATE membership_requests SET name=?, org_name=?, phone=?, note=?, updated_at=? WHERE id=?'
    ).bind(name, org, phone, note, now, dup.id).run();
    return json({
      ok: true, id: dup.id, already: true,
      message: dup.status === '코드발급'
        ? '이미 가입코드를 보내드렸습니다. 메일함(스팸함 포함)을 확인해주세요.'
        : '이미 접수된 요청이 있습니다. 확인 후 가입코드를 보내드리겠습니다.',
    });
  }

  const r = await env.DB.prepare(
    `INSERT INTO membership_requests (name, org_name, email, phone, note, status, customer_id, created_at, updated_at)
     VALUES (?,?,?,?,?,'접수',?,?,?)`
  ).bind(name, org, email, phone, note, me?.id || null, now, now).run();
  const id = r.meta.last_row_id;

  await logEvent(env, {
    action: 'membership_request', actor: me ? `cust:${me.id}` : 'guest',
    detail: `멤버십 요청 ${name} (${org})`,
  });

  if (mailConfigured(env)) {
    const rows = [
      ['성함', name], ['소속', org], ['이메일', email], ['연락처', phone || '—'],
      ['로그인 계정', me ? `#${me.id} ${me.name || ''}` : '비로그인'],
    ].map(([k, v]) => `<tr><th align="left" style="padding:6px 14px 6px 0;color:#6B6B6B;font-weight:600;white-space:nowrap">${esc(k)}</th><td style="padding:6px 0">${esc(v)}</td></tr>`).join('');
    const adminHtml =
      `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;color:#1A1A1A;line-height:1.6">
        <h2 style="font-size:17px;margin:0 0 14px">멤버십 가입 요청 #${id}</h2>
        <table style="font-size:14px;border-collapse:collapse">${rows}</table>
        ${note ? `<p style="margin:14px 0 0;padding:12px 14px;background:#F2F4F6;border-radius:8px;font-size:14px;white-space:pre-wrap">${esc(note)}</p>` : ''}
        <p style="margin:18px 0 0;font-size:13px;color:#6B6B6B">
          관리자 화면에서 <b>가입코드 발급</b>을 누르면 코드가 신청자에게 바로 나갑니다 →
          <a href="https://rndsetup.com/member/#admClients" style="color:#3B3695">거래처 관리</a></p>
      </div>`;
    await sendMail(env, {
      to: mailReplyTo(env),
      subject: `[멤버십 요청] ${name} · ${org}`,
      html: adminHtml,
    }).catch(() => {});

    await sendMail(env, {
      to: email,
      subject: '[실험셋업연구소] 멤버십 가입 요청이 접수되었습니다',
      html:
        `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;color:#1A1A1A;line-height:1.7">
          <p><b>${esc(name)}</b> 님, 멤버십 가입 요청을 받았습니다.</p>
          <p>내용을 확인한 뒤 <b>가입코드</b>를 이 메일 주소로 보내드립니다.<br>
             코드를 받으시면 <a href="https://rndsetup.com/login/" style="color:#3B3695">로그인 페이지</a>에서
             카카오로 로그인한 뒤 코드를 입력하시면 멤버십이 열립니다.</p>
          <p style="font-size:13px;color:#6B6B6B">그동안에도 카카오로 시작하시면 일반회원으로 제품 열람·견적 문의는 바로 이용하실 수 있습니다.</p>
          <hr style="border:0;border-top:1px solid #EAEAEA;margin:20px 0">
          <p style="font-size:12.5px;color:#9A9A9A">실험셋업연구소(이머전트) · 070-8983-2600 · info@rndsetup.com</p>
        </div>`,
    }).catch(() => {});
  }

  return json({ ok: true, id, message: '요청이 접수되었습니다. 확인 후 가입코드를 메일로 보내드리겠습니다.' });
}
