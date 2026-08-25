// functions/api/_notify.js — 고객 알림 (카카오 알림톡 → 없으면 이메일)
//
// 알림톡은 발신프로필 등록 + 템플릿 사전승인 + 발송대행사 계약이 있어야 쓸 수 있다.
// 준비되면 ALIMTALK_* 환경변수만 채우면 이쪽으로 나가고, 그 전에는 이메일로 나간다.
import { sendMail, mailConfigured } from './_mailer.js';
import { logEvent } from './_lib.js';

export function alimtalkConfigured(env) {
  return !!(env.ALIMTALK_API_KEY && env.ALIMTALK_SENDER_KEY);
}

/**
 * @param {object} n { customer, order, template, vars, subject, html }
 *   template: 알림톡 템플릿 코드 (승인받은 것)
 */
export async function notifyCustomer(env, n) {
  const { customer, order } = n;

  if (alimtalkConfigured(env) && customer?.phone) {
    const r = await sendAlimtalk(env, {
      to: String(customer.phone).replace(/[^0-9]/g, ''),
      template: n.template,
      text: n.text,
      buttons: n.buttons,
    });
    await logEvent(env, {
      order_id: order?.id, action: 'notify', channel: 'kakao', actor: 'system',
      to_addr: customer.phone, result: r.ok ? 'ok' : 'fail',
      detail: r.ok ? `알림톡 발송 (${n.template})` : `알림톡 실패: ${r.error}`,
    });
    if (r.ok) return r;
    // 알림톡 실패 시 이메일로 떨어뜨린다
  }

  if (mailConfigured(env) && customer?.email) {
    const r = await sendMail(env, { to: customer.email, subject: n.subject, html: n.html });
    await logEvent(env, {
      order_id: order?.id, action: 'notify', channel: 'email', actor: 'system',
      to_addr: customer.email, result: r.ok ? 'ok' : 'fail',
      detail: r.ok ? '이메일 알림 발송' : `이메일 알림 실패: ${r.error}`,
    });
    return r;
  }

  await logEvent(env, {
    order_id: order?.id, action: 'notify', actor: 'system', result: 'fail',
    detail: '알림 수단 없음 (알림톡·이메일 미설정)',
  });
  return { ok: false, error: '알림 수단 미설정' };
}

// 발송대행사 REST 호출 — 계약한 곳(솔라피·알리고·비즈엠 등)에 맞춰 URL/필드만 맞추면 된다.
async function sendAlimtalk(env, m) {
  try {
    const r = await fetch(env.ALIMTALK_ENDPOINT || 'https://api.solapi.com/messages/v4/send', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.ALIMTALK_API_KEY}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        message: {
          to: m.to,
          from: env.ALIMTALK_FROM || '',
          kakaoOptions: {
            pfId: env.ALIMTALK_SENDER_KEY,
            templateId: m.template,
            variables: m.vars || {},
            buttons: m.buttons || [],
          },
          text: m.text,
        },
      }),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) return { ok: false, error: j?.message || `HTTP ${r.status}` };
    return { ok: true, id: j.messageId };
  } catch (e) {
    return { ok: false, error: String(e?.message || e) };
  }
}

// 배송중 알림 본문
export function shipHtml({ orderNo, title, url }) {
  return `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;font-size:15px;color:#1a2332;line-height:1.65">
  <p><b>${title}</b> 주문이 발송되었습니다.</p>
  <p style="color:#5a6779;font-size:14px">주문번호 ${orderNo}</p>
  <p>물건을 받으시면 아래에서 <b>수령 확인</b>을 눌러주세요.</p>
  <p><a href="${url}" style="display:inline-block;background:#1a6e56;color:#fff;text-decoration:none;
     padding:12px 22px;border-radius:9px;font-weight:700">수령 확인하기</a></p>
  <p style="color:#5a6779;font-size:13px;margin-top:22px">문제가 있으면 같은 화면에서 "아직 못 받았어요"를 눌러주세요.<br>
  문의 070-8983-2600 · info@rndsetup.com</p>
</div>`;
}
