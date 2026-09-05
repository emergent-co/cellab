// functions/api/_notify.js — 고객 알림 (카카오 알림톡 → 없으면 이메일)
//
// 알림톡은 발신프로필 등록 + 템플릿 사전승인 + 발송대행사 계약이 있어야 쓸 수 있다.
// 준비되면 ALIMTALK_* 환경변수만 채우면 이쪽으로 나가고, 그 전에는 이메일로 나간다.
import { sendMail, mailConfigured } from './_mailer.js';
import { logEvent, kstISO } from './_lib.js';

export function alimtalkConfigured(env) {
  return !!(env.ALIMTALK_API_KEY && env.ALIMTALK_SENDER_KEY);
}

/**
 * @param {object} n { customer, order, template, vars, subject, html }
 *   template: 알림톡 템플릿 코드 (승인받은 것)
 */
export async function notifyCustomer(env, n) {
  const { customer, order } = n;
  const phone = order?.orderer_phone || customer?.phone || '';

  if (alimtalkConfigured(env) && phone) {
    const r = await sendAlimtalk(env, {
      to: String(phone).replace(/[^0-9]/g, ''),
      template: n.template,
      text: n.text,
      buttons: n.buttons,
    });
    await logEvent(env, {
      order_id: order?.id, action: 'notify', channel: 'kakao', actor: 'system',
      to_addr: phone, result: r.ok ? 'ok' : 'fail',
      detail: r.ok ? `알림톡 발송 (${n.template})` : `알림톡 실패: ${r.error}`,
    });
    if (r.ok) return r;
    // 알림톡 실패 시 이메일로 떨어뜨린다
  }

  const to = order?.orderer_email || customer?.work_email || customer?.email || '';
  if (mailConfigured(env) && to) {
    const r = await sendMail(env, { to, subject: n.subject, html: n.html });
    await logEvent(env, {
      order_id: order?.id, action: 'notify', channel: 'email', actor: 'system',
      to_addr: to, result: r.ok ? 'ok' : 'fail',
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

function e(v){ return String(v == null ? '' : v)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function itemRows(items) {
  return (items || []).map((i, n) => `<tr>
    <td style="padding:7px 8px;border-bottom:1px solid #eee;color:#8a94a6">${n + 1}</td>
    <td style="padding:7px 8px;border-bottom:1px solid #eee">${e(i.name)}
      ${i.spec ? `<br><small style="color:#8a94a6">${e(i.spec)}</small>` : ''}
      ${i.link ? `<br><a href="${e(i.link)}" style="font-size:12px;color:#3b3695">${e(String(i.link).slice(0, 60))}</a>` : ''}</td>
    <td style="padding:7px 8px;border-bottom:1px solid #eee;text-align:right;white-space:nowrap">${e(i.qty)}</td>
  </tr>`).join('');
}

const TABLE = (items) => `<table style="border-collapse:collapse;width:100%;margin-top:12px;font-size:14px">
  <thead><tr style="background:#f6f7fa">
    <th style="text-align:left;padding:7px 8px;width:28px">#</th>
    <th style="text-align:left;padding:7px 8px">품목 · 규격</th>
    <th style="text-align:right;padding:7px 8px;width:52px">수량</th>
  </tr></thead><tbody>${itemRows(items)}</tbody></table>`;

// 주문 접수 확인 — 고객에게
export function orderReceivedHtml({ orderNo, title, items, ship, url }) {
  return `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;font-size:15px;color:#1a2332;line-height:1.65">
  <p><b>${e(title)}</b> 주문이 접수되었습니다.</p>
  <p style="color:#5a6779;font-size:14px">주문번호 ${e(orderNo)}</p>
  ${TABLE(items)}
  ${ship ? `<p style="color:#5a6779;font-size:13.5px;margin-top:12px">납품지 · ${e(ship)}</p>` : ''}
  <p style="margin-top:16px">단가와 납기를 확인해 <b>견적서를 보내드립니다.</b> 아래에서 접수 내용을 다시 볼 수 있습니다.</p>
  <p><a href="${e(url)}" style="display:inline-block;background:#1a6e56;color:#fff;text-decoration:none;
     padding:12px 22px;border-radius:9px;font-weight:700">주문 내용 보기</a></p>
  <p style="color:#5a6779;font-size:13px;margin-top:22px">내용이 다르면 답장 주시거나 070-8983-2600 으로 알려주세요.</p>
</div>`;
}

// 새 주문 알림 — 관리자에게
export function newOrderAdminHtml({ orderNo, company, orderer, items, ship, note, url }) {
  return `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;font-size:14px;color:#1a2332;line-height:1.6">
  <h2 style="font-size:17px;margin:0 0 6px">새 주문이 들어왔습니다</h2>
  <p style="margin:0"><b>${e(company || '—')}</b><br>
     <span style="color:#5a6779">${e(orderer)}</span></p>
  ${TABLE(items)}
  ${ship ? `<p style="color:#5a6779;margin-top:10px">납품지 · ${e(ship)}</p>` : ''}
  ${note ? `<p style="margin-top:10px;white-space:pre-wrap">${e(note)}</p>` : ''}
  <p style="margin-top:16px"><a href="${e(url)}" style="display:inline-block;background:#3b3695;color:#fff;
     text-decoration:none;padding:11px 20px;border-radius:9px;font-weight:700">주문 열기</a></p>
  <p style="color:#8a94a6;font-size:12px;margin-top:18px">${e(orderNo)}</p>
</div>`;
}

// 배송중 알림 본문
/* 주문이 «배송중» 이 되는 순간 해야 할 일 — 발송시각 기록 + 고객에게 «수령 확인» 안내.
   주문 화면에서 상태를 바꿀 때만 돌던 것을, 거래명세서 발송 경로에서도 쓰려고 여기로 옮겼다. */
export async function notifyShipped(env, origin, order) {
  await env.DB.prepare('UPDATE orders SET shipped_at=? WHERE id=?').bind(kstISO(), order.id).run();
  const customer = order.customer_id
    ? await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(order.customer_id).first()
    : null;
  if (!customer) return;
  const url = `${origin}/member/#orders`;
  await notifyCustomer(env, {
    customer, order,
    template: env.ALIMTALK_TPL_SHIP || 'rndsetup_ship',
    text: `[실험셋업연구소] ${order.title || ''} 주문이 발송되었습니다.\n받으시면 수령 확인을 눌러주세요.\n${url}`,
    buttons: [{ buttonType: 'WL', buttonName: '수령 확인하기', linkMo: url, linkPc: url }],
    subject: `[실험셋업연구소] ${order.title || order.order_no} 발송 안내`,
    html: shipHtml({ orderNo: order.order_no, title: order.title || '', url }),
  });
}

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
