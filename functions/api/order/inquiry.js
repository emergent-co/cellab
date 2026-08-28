// POST /api/order/inquiry — 견적 문의 (로그인 없이도 보낼 수 있다)
//   등록된 거래처가 아닌 방문자가 장바구니에 담은 것을 그대로 문의로 넘긴다.
//   주문이 아니라 문의다 — 값을 매기지 않고, 사람이 읽고 회신한다.
import { json, currentCustomer, kstISO, esc, logEvent } from '../_lib.js';
import { sendMail, mailConfigured } from '../_mailer.js';

const MAX_ITEMS = 60;

export async function onRequestPost({ request, env }) {
  const b = await request.json().catch(() => ({}));

  const name  = String(b.name  || '').trim().slice(0, 60);
  const email = String(b.email || '').trim().slice(0, 120);
  const phone = String(b.phone || '').trim().slice(0, 40);
  const org   = String(b.org_name || '').trim().slice(0, 120);
  const note  = String(b.note  || '').trim().slice(0, 2000);

  const items = (Array.isArray(b.items) ? b.items : []).slice(0, MAX_ITEMS)
    .map((i) => ({
      name: String(i.name || '').trim().slice(0, 200),
      spec: String(i.spec || '').trim().slice(0, 200),
      qty : Math.max(1, Math.min(99999, Number(i.qty) || 1)),
      link: String(i.link || '').trim().slice(0, 500),
    }))
    .filter((i) => i.name);

  if (!name)  return json({ error: 'no_name',    message: '성함을 입력해주세요.' }, 400);
  if (!email && !phone) {
    return json({ error: 'no_contact', message: '이메일 또는 연락처 중 하나는 남겨주세요.' }, 400);
  }
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'bad_email', message: '이메일 형식을 확인해주세요.' }, 400);
  }
  if (!items.length && !note) {
    return json({ error: 'empty', message: '문의하실 품목이나 내용을 남겨주세요.' }, 400);
  }

  const me = await currentCustomer(request, env).catch(() => null);
  const now = kstISO();

  const r = await env.DB.prepare(
    `INSERT INTO inquiries (customer_id, name, email, phone, org_name, items_json, note, status, created_at)
     VALUES (?,?,?,?,?,?,?,?,?)`
  ).bind(me?.id || null, name, email, phone, org, JSON.stringify(items), note, '접수', now).run();

  await logEvent(env, {
    action: 'inquiry', actor: 'guest',
    detail: `견적 문의 ${name}${org ? ` (${org})` : ''} · ${items.length}건`,
  });

  // 관리자에게 알린다. 메일이 안 나가도 DB 에는 남으니 문의를 잃지는 않는다.
  if (mailConfigured(env)) {
    const rows = items.map((i, n) => `<tr>
      <td style="padding:6px 8px;border-bottom:1px solid #eee">${n + 1}</td>
      <td style="padding:6px 8px;border-bottom:1px solid #eee">${esc(i.name)}
        ${i.spec ? `<br><small style="color:#888">${esc(i.spec)}</small>` : ''}
        ${i.link ? `<br><a href="${esc(i.link)}">${esc(i.link)}</a>` : ''}</td>
      <td style="padding:6px 8px;border-bottom:1px solid #eee;text-align:right">${i.qty}</td>
    </tr>`).join('');

    await sendMail(env, {
      to: env.ADMIN_EMAIL || 'info@rndsetup.com',
      subject: `[견적문의] ${name}${org ? ` · ${org}` : ''} — ${items.length}건`,
      html: `<div style="font-family:system-ui,sans-serif;font-size:14px;color:#1A1A1A">
        <h2 style="font-size:17px">견적 문의가 들어왔습니다</h2>
        <p><b>${esc(name)}</b>${org ? ` · ${esc(org)}` : ''}<br>
           ${email ? `${esc(email)}<br>` : ''}${phone ? `${esc(phone)}<br>` : ''}
           ${me ? `가입 계정 #${me.id} (승인 상태: ${esc(me.access || '대기')})` : '비로그인'}</p>
        ${items.length ? `<table style="border-collapse:collapse;width:100%;margin-top:10px">
          <thead><tr><th style="text-align:left;padding:6px 8px">#</th>
          <th style="text-align:left;padding:6px 8px">품목</th>
          <th style="text-align:right;padding:6px 8px">수량</th></tr></thead>
          <tbody>${rows}</tbody></table>` : ''}
        ${note ? `<p style="margin-top:12px;white-space:pre-wrap">${esc(note)}</p>` : ''}
        <p style="margin-top:16px;color:#888;font-size:12px">문의번호 #${r.meta.last_row_id} · ${esc(now)}</p>
      </div>`,
    }).catch(() => {});
  }

  return json({ ok: true, id: r.meta.last_row_id });
}
