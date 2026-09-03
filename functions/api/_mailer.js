// functions/api/_mailer.js — Resend로 이메일 발송
// 필요한 환경변수: RESEND_API_KEY, (선택) MAIL_FROM

export function mailConfigured(env) {
  return !!env.RESEND_API_KEY;
}

export function mailFrom(env) {
  return env.MAIL_FROM || '실험셋업연구소 <order@rndsetup.com>';
}

/* 서류 메일의 «보관용 숨은참조».
   서류는 Resend 가 직접 보내므로 지메일에는 아무 흔적이 남지 않는다.
   보낸 서류를 지메일에서도 찾고 첨부 PDF까지 그대로 두려면 사본이 한 통 필요하다.
   숨은참조라 받는 사람에게는 보이지 않는다. 주소를 바꾸려면 MAIL_BCC 를 넣으면 된다. */
export function mailBcc(env) {
  return env.MAIL_BCC === '' ? '' : (env.MAIL_BCC || 'emgt.yhlee@gmail.com');
}

/* 답장이 돌아올 주소.
   보내는 주소(order@)는 발송 전용이라 수신 라우팅이 없다 —
   고객이 견적서 메일에 그냥 «답장»을 누르면 그 메일은 아무 데도 도착하지 않는다.
   그래서 모든 메일에 답장 주소를 박아 둔다. 받는 주소는 실제로 살아 있는 곳이어야 한다. */
export function mailReplyTo(env) {
  return env.MAIL_REPLY_TO || 'info@rndsetup.com';
}

/**
 * @param {object} m { to, cc?, subject, html, text?, attachments?: [{filename, content(base64)}] }
 * @returns {Promise<{ok:boolean, id?:string, error?:string}>}
 */
export async function sendMail(env, m) {
  if (!mailConfigured(env)) return { ok: false, error: 'RESEND_API_KEY 미설정' };

  const body = {
    from: mailFrom(env),
    to: Array.isArray(m.to) ? m.to : [m.to],
    subject: m.subject,
    html: m.html,
  };
  if (m.text) body.text = m.text;
  if (m.cc) body.cc = Array.isArray(m.cc) ? m.cc : [m.cc];
  if (m.bcc) {
    const list = (Array.isArray(m.bcc) ? m.bcc : [m.bcc])
      .map((x) => splitAddr(x).addr).filter(Boolean);
    // 받는 사람·참조에 이미 있는 주소는 뺀다 — 같은 메일이 두 통 오면 그게 더 성가시다
    // cc 는 «a@x.com, b@y.com» 처럼 한 줄로 올 수도 있다 — 쉼표까지 풀어서 본다
    const had = new Set([].concat(body.to, body.cc || [])
      .flatMap((x) => String(x || '').split(/[,;]/))
      .map((x) => splitAddr(x).addr.toLowerCase()).filter(Boolean));
    const bcc = [...new Set(list.filter((a) => !had.has(a.toLowerCase())))];
    if (bcc.length) body.bcc = bcc;
  }
  body.reply_to = m.reply_to || mailReplyTo(env);
  if (m.attachments?.length) body.attachments = m.attachments;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) return { ok: false, error: j?.message || `HTTP ${r.status}` };
    return { ok: true, id: j.id };
  } catch (e) {
    return { ok: false, error: String(e?.message || e) };
  }
}

// 문서 발송 기본 메일 본문
// '홍길동 <a@b.com>' 처럼 이름을 붙여 적을 수 있게 한다. 없으면 메일 앞부분을 이름으로 쓴다.
export function splitAddr(v) {
  const raw = String(v || '').trim();
  const m = raw.match(/^\s*(.*?)\s*<\s*([^>]+)\s*>\s*$/);
  const addr = (m ? m[2] : raw).trim();
  let name = (m ? m[1] : '').replace(/^["']|["']$/g, '').trim();
  if (!name) name = addr.split('@')[0] || '';
  return { name, addr };
}

export function docMailBody({ label, docNo, company, contact, total, viewUrl, to, cc }) {
  const won = (n) => Number(n || 0).toLocaleString('ko-KR');
  const esc = (t) => String(t == null ? '' : t)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  // 수신 / 참조 — 누구에게 가는 메일인지 첫 줄에서 바로 보이게
  const t = to ? splitAddr(to) : null;
  const toName = contact || (t && t.name) || '담당자';
  const line = (k, nm, ad) =>
    `<tr><td style="padding:2px 12px 2px 0;color:#5a6779;white-space:nowrap">${k}</td>`
    + `<td style="padding:2px 0"><b>${esc(nm)} 님</b>`
    + (ad ? ` <span style="color:#8a94a3;font-size:13px">&lt;${esc(ad)}&gt;</span>` : '') + '</td></tr>';

  const ccList = String(cc || '').split(/[,;]/).map((x) => x.trim()).filter(Boolean).map(splitAddr);

  return `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;font-size:15px;color:#1a2332;line-height:1.65">
  <table style="border-collapse:collapse;font-size:14px;margin-bottom:20px">
    ${line('수신', toName, t && t.addr)}
    ${ccList.map((c) => line('참조', c.name, c.addr)).join('')}
  </table>
  <p>${esc(company || '')} ${esc(toName)} 님, 안녕하세요.<br>실험셋업연구소(이머전트)입니다.</p>
  <p>요청하신 <b>${label}</b>를 보내드립니다. 첨부 PDF를 확인해주세요.</p>
  <table style="border-collapse:collapse;margin:18px 0;font-size:14px">
    <tr><td style="padding:5px 14px 5px 0;color:#5a6779">문서번호</td><td style="padding:5px 0"><b>${docNo}</b></td></tr>
    <tr><td style="padding:5px 14px 5px 0;color:#5a6779">합계금액</td><td style="padding:5px 0"><b>${won(total)}원</b> (VAT 포함)</td></tr>
  </table>
  ${viewUrl ? `<p><a href="${viewUrl}" style="display:inline-block;background:#1a6e56;color:#fff;text-decoration:none;padding:11px 20px;border-radius:9px;font-weight:700">문서 열어보기</a></p>` : ''}
  <p style="color:#5a6779;font-size:13px;margin-top:22px">문의 070-8983-2600 · info@rndsetup.com<br>이머전트 · 대표 이영현 · 사업자등록번호 328-03-02926</p>
</div>`;
}

/** 주문·정산 내용 확인 요청 메일.
 *  승인을 받는 게 아니라 '이렇게 적었으니 봐 달라'는 안내다. 버튼도 하나만 둔다. */
export function confirmMailBody({ kind, title, company, contact, total, viewUrl, to, cc, memo }) {
  const won = (n) => Number(n || 0).toLocaleString('ko-KR');
  const e = (t) => String(t == null ? '' : t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const label = kind === 'settle' ? '정산 내용' : '주문 내용';

  const t = to ? splitAddr(to) : null;
  const toName = contact || (t && t.name) || '담당자';
  const line = (k, nm, ad) =>
    `<tr><td style="padding:2px 12px 2px 0;color:#5a6779;white-space:nowrap">${k}</td>`
    + `<td style="padding:2px 0"><b>${e(nm)} 님</b>`
    + (ad ? ` <span style="color:#8a94a3;font-size:13px">&lt;${e(ad)}&gt;</span>` : '') + '</td></tr>';
  const ccList = String(cc || '').split(/[,;]/).map((x) => x.trim()).filter(Boolean).map(splitAddr);

  return `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;font-size:15px;color:#1a2332;line-height:1.65">
  <table style="border-collapse:collapse;font-size:14px;margin-bottom:20px">
    ${line('수신', toName, t && t.addr)}
    ${ccList.map((c) => line('참조', c.name, c.addr)).join('')}
  </table>
  <p>${e(company || '')} ${e(toName)} 님, 안녕하세요.<br>실험셋업연구소(이머전트)입니다.</p>
  <p>진행 중인 <b>${e(label)}</b>을 아래와 같이 정리했습니다. 확인해주시고,
     <b>다른 점이 있으면 알려주시면 바로 고쳐드리겠습니다.</b></p>
  <table style="border-collapse:collapse;margin:18px 0;font-size:14px">
    <tr><td style="padding:5px 14px 5px 0;color:#5a6779">내용</td><td style="padding:5px 0"><b>${e(title || '')}</b></td></tr>
    ${total ? `<tr><td style="padding:5px 14px 5px 0;color:#5a6779">금액</td><td style="padding:5px 0"><b>${won(total)}원</b> (VAT 포함)</td></tr>` : ''}
  </table>
  ${memo ? `<p style="background:#F7F8FA;border-radius:9px;padding:12px 14px;font-size:14px;white-space:pre-wrap">${e(memo)}</p>` : ''}
  <p><a href="${viewUrl}" style="display:inline-block;background:#1a6e56;color:#fff;text-decoration:none;padding:12px 22px;border-radius:9px;font-weight:700">내용 확인하기</a></p>
  <p style="color:#5a6779;font-size:13px">따로 눌러야 할 버튼은 없습니다. 보시고 알려주시기만 하면 됩니다.</p>
  <p style="color:#5a6779;font-size:13px;margin-top:22px">문의 070-8983-2600 · info@rndsetup.com<br>이머전트 · 대표 이영현 · 사업자등록번호 328-03-02926</p>
</div>`;
}
