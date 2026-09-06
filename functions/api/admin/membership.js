// GET  /api/admin/membership                 → 멤버십 요청 목록 + 발급한 코드 목록
// POST /api/admin/membership {action:'issue', id}        → 요청에 코드 발급 + 메일 회신
// POST /api/admin/membership {action:'create', note, email?} → 요청 없이 코드만 생성
// POST /api/admin/membership {action:'status', id, status}   → 요청 상태 변경
// POST /api/admin/membership {action:'revoke', code}         → 미사용 코드 폐기
// POST /api/admin/membership {action:'demote', customer_id}  → 멤버십 해제(일반회원으로)
import { json, adminOK, needAdmin, kstISO, esc, logEvent, plusDays, kstDate } from '../_lib.js';
import { sendMail, mailConfigured, mailReplyTo } from '../_mailer.js';

// 사람이 메일에서 옮겨 적는 코드다 — 헷갈리는 글자(O/0, I/1)를 뺀다
const ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
function makeCode() {
  const b = new Uint8Array(8);
  crypto.getRandomValues(b);
  return [...b].map((x) => ALPHABET[x % ALPHABET.length]).join('');   // 8글자
}

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();

  if (request.method === 'GET') {
    const { results: reqs } = await env.DB.prepare(
      `SELECT r.*, c.name AS joined_name
         FROM membership_requests r LEFT JOIN customers c ON c.id = r.customer_id
        ORDER BY (r.status='접수') DESC, r.id DESC LIMIT 200`
    ).all();
    const { results: codes } = await env.DB.prepare(
      `SELECT m.*, c.name AS used_name, c.company AS used_company
         FROM member_codes m LEFT JOIN customers c ON c.id = m.used_by
        ORDER BY (m.used_by IS NULL) DESC, m.rowid DESC LIMIT 200`
    ).all();
    return json({ requests: reqs || [], codes: codes || [] });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);
  const b = await request.json().catch(() => ({}));
  const now = kstISO();

  if (b.action === 'status') {
    const st = ['접수', '코드발급', '가입완료', '거절'].includes(b.status) ? b.status : null;
    if (!b.id || !st) return json({ error: 'bad_request' }, 400);
    await env.DB.prepare('UPDATE membership_requests SET status=?, updated_at=? WHERE id=?')
      .bind(st, now, b.id).run();
    await logEvent(env, { action: 'membership_status', actor: 'admin', detail: `멤버십 요청 #${b.id} → ${st}` });
    return json({ ok: true, status: st });
  }

  if (b.action === 'revoke') {
    const code = String(b.code || '').trim().toUpperCase();
    if (!code) return json({ error: 'bad_request' }, 400);
    const r = await env.DB.prepare('DELETE FROM member_codes WHERE code=? AND used_by IS NULL').bind(code).run();
    if (!r.meta.changes) return json({ error: 'used_or_missing', message: '이미 사용됐거나 없는 코드입니다.' }, 400);
    await logEvent(env, { action: 'membership_code_revoke', actor: 'admin', detail: `가입코드 ${code} 폐기` });
    return json({ ok: true });
  }

  /* 멤버십 해제 — 후불 장부에서 내리고 일반회원으로 되돌린다.
     계정을 지우지 않는다. 지난 주문·서류는 그대로 남아야 한다. */
  if (b.action === 'demote') {
    const cid = Number(b.customer_id);
    if (!cid) return json({ error: 'bad_request' }, 400);
    const c = await env.DB.prepare('SELECT id,name,company FROM customers WHERE id=?').bind(cid).first();
    if (!c) return json({ error: 'not_found' }, 404);
    await env.DB.prepare("UPDATE customers SET access='일반', billing_mode='선불', updated_at=? WHERE id=?")
      .bind(now, cid).run();
    await logEvent(env, { action: 'membership_demote', actor: 'admin',
      detail: `${c.name || ''}${c.company ? ` (${c.company})` : ''} 멤버십 해제 → 일반회원` });
    return json({ ok: true });
  }

  // ---- 코드 발급 ----
  let reqRow = null, to = '', who = '';
  if (b.action === 'issue') {
    const id = Number(b.id);
    if (!id) return json({ error: 'bad_request' }, 400);
    reqRow = await env.DB.prepare('SELECT * FROM membership_requests WHERE id=?').bind(id).first();
    if (!reqRow) return json({ error: 'not_found' }, 404);
    to = reqRow.email || '';
    who = `${reqRow.name || ''}${reqRow.org_name ? ` (${reqRow.org_name})` : ''}`;
  } else if (b.action === 'create') {
    to = String(b.email || '').trim();
    who = String(b.note || '').trim();
    if (!who) return json({ error: 'no_note', message: '누구에게 주는 코드인지 적어주세요.' }, 400);
  } else {
    return json({ error: 'bad_action' }, 400);
  }

  // 유효기간 기본 30일. 오래 굴러다니는 코드는 누가 가졌는지 알 수 없게 된다.
  const days = Number(b.days) > 0 ? Math.min(365, Number(b.days)) : 30;
  const expires = plusDays(kstDate(), days) + ' 23:59:59';

  let code = '';
  for (let i = 0; i < 5 && !code; i++) {
    const c = makeCode();
    const hit = await env.DB.prepare('SELECT code FROM member_codes WHERE code=?').bind(c).first();
    if (!hit) code = c;
  }
  if (!code) return json({ error: 'code_gen_failed' }, 500);

  await env.DB.prepare(
    `INSERT INTO member_codes (code, request_id, note, expires_at, created_at, created_by)
     VALUES (?,?,?,?,?,'admin')`
  ).bind(code, reqRow ? reqRow.id : null, who, expires, now).run();

  if (reqRow) {
    await env.DB.prepare(
      "UPDATE membership_requests SET status='코드발급', code=?, code_issued_at=?, updated_at=? WHERE id=?"
    ).bind(code, now, now, reqRow.id).run();
  }

  let mailed = false;
  if (to && mailConfigured(env)) {
    const r = await sendMail(env, {
      to,
      subject: '[실험셋업연구소] 멤버십 가입코드를 보내드립니다',
      html:
        `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;color:#1A1A1A;line-height:1.7">
          <p><b>${esc(reqRow ? (reqRow.name || '') : who)}</b> 님, 멤버십 가입코드를 보내드립니다.</p>
          <p style="margin:22px 0;text-align:center">
            <span style="display:inline-block;background:#EAF4FB;border:1px solid #D8E4F2;border-radius:12px;
                         padding:16px 28px;font-size:26px;font-weight:800;letter-spacing:.18em;color:#3B3695">${esc(code)}</span>
          </p>
          <p><b>이용 방법</b><br>
            1. <a href="https://rndsetup.com/login/" style="color:#0F69AF">rndsetup.com/login</a> 에서 카카오로 로그인<br>
            2. <b>가입코드 입력</b>란에 위 코드를 넣으면 멤버십(후불 거래)이 바로 열립니다.</p>
          <p style="font-size:13px;color:#6B6B6B">유효기간 ${esc(expires.slice(0, 10))} · 1회용 코드입니다.</p>
          <hr style="border:0;border-top:1px solid #EAEAEA;margin:20px 0">
          <p style="font-size:12.5px;color:#9A9A9A">실험셋업연구소(이머전트) · 070-8983-2600 · info@rndsetup.com</p>
        </div>`,
    }).catch(() => ({ ok: false }));
    mailed = !!(r && r.ok);
  }

  await logEvent(env, {
    action: 'membership_code_issue', actor: 'admin',
    detail: `가입코드 ${code} 발급 → ${who}${to ? ` <${to}>` : ''}${mailed ? ' (메일 발송)' : ' (메일 미발송)'}`,
  });

  return json({ ok: true, code, expires_at: expires, mailed, to });
}
