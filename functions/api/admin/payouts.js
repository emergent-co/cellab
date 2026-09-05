// functions/api/admin/payouts.js — 용역비(사업소득) 지급내역
//   GET  ?ym=YYYY-MM        그 달 목록 + 합계 (주민번호는 «항상» 마스킹해서 내보낸다)
//   GET  ?id=<id>&full=1    한 건 (수정용 — 여기서만 전체 번호를 내보낸다)
//   POST {action:'save'|'delete'|'share'}
//
// 주민번호는 지급명세서 신고에 전체가 필요해 DB엔 전체를 두지만,
// 목록·메일처럼 «여러 곳으로 흘러가는» 경로에는 절대 전체를 싣지 않는다.
import { json, needAdmin, adminOK, kstISO, kstDate, randomToken, logEvent } from '../_lib.js';
import { sendMail, mailConfigured, mailBcc } from '../_mailer.js';
import { rrnEnc, rrnDec, rrnKeyOn, maskDigits } from '../_rrn.js';

const digits = (v) => String(v || '').replace(/[^0-9]/g, '');
const won = (n) => Number(n || 0).toLocaleString('ko-KR');

/** 저장값(암호문 또는 옛 평문) → 880101-1****** */
export async function maskStored(env, v) {
  return maskDigits(await rrnDec(env, v));
}

/** 3.3% 원천징수 — 소득세 3% + 지방소득세 0.3%, 각각 10원 미만 절사 */
export function withhold(gross, rate) {
  const g = Math.max(0, Math.round(Number(gross) || 0));
  const r = Number(rate) || 3;                     // 사업소득 3, 기타소득 20 등
  const inc = Math.floor((g * r) / 100 / 10) * 10;
  const loc = Math.floor(inc / 10 / 10) * 10;      // 소득세의 10%
  return { tax_income: inc, tax_local: loc, net: g - inc - loc };
}

const ymOf = (v) => {
  const m = String(v || '').match(/^(\d{4})-(\d{2})/);
  return m ? `${m[1]}-${m[2]}` : kstDate().slice(0, 7);
};

/* 용역처 명부.
   같은 사람에게 여러 번 주면서 이름·주민번호·계좌를 매번 다시 치는 건
   실수도 나고 시간도 든다. 한 번 등록해 두고 골라 쓴다.
   D1 에 마이그레이션 도구가 따로 없어 첫 호출 때 만든다 — 있으면 그냥 지나간다. */
let shareReady = false;
async function ensureShare(env) {
  if (shareReady) return;
  /* 링크만 알면 열리던 걸 막는다 — 확인번호를 맞춰야 전체 번호가 보인다.
     번호는 메일에 넣지 않는다. 넣으면 링크와 함께 유출되어 아무 소용이 없다. */
  await env.DB.prepare('ALTER TABLE payout_shares ADD COLUMN pin TEXT').run().catch(() => {});
  await env.DB.prepare('ALTER TABLE payout_shares ADD COLUMN fails INTEGER DEFAULT 0').run().catch(() => {});
  shareReady = true;
}

let payeeReady = false;
async function ensurePayees(env) {
  if (payeeReady) return;
  await env.DB.prepare(
    `CREATE TABLE IF NOT EXISTS payees (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL, rrn TEXT, bank TEXT, memo TEXT,
       created_at TEXT, updated_at TEXT)`).run().catch(() => {});
  payeeReady = true;
}

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  if (request.method === 'GET') return get(request, env);
  if (request.method === 'POST') return post(request, env);
  return json({ error: 'method_not_allowed' }, 405);
}

async function get(request, env) {
  const u = new URL(request.url).searchParams;

  // 용역처 한 명 — 채워 넣으려면 전체 번호가 필요하다. 열람 사실을 남긴다.
  if (u.get('payee')) {
    await ensurePayees(env);
    const r = await env.DB.prepare('SELECT * FROM payees WHERE id=?').bind(u.get('payee')).first();
    if (!r) return json({ error: 'not_found' }, 404);
    await logEvent(env, { action: 'payee_view', actor: 'admin', detail: `용역처 ${r.name} 주민번호 열람` });
    return json({ payee: { ...r, rrn: await rrnDec(env, r.rrn) } });
  }

  // 용역처 목록 — 고르는 데 쓰는 목록이라 주민번호는 «항상» 마스킹해서 내보낸다
  if (u.get('payees') != null) {
    await ensurePayees(env);
    const { results } = await env.DB.prepare(
      'SELECT id, name, rrn, bank, memo FROM payees ORDER BY name').all();
    return json({ payees: await Promise.all((results || []).map(async (r) =>
      ({ ...r, rrn: await maskStored(env, r.rrn) }))) });
  }

  if (u.get('id')) {
    const r = await env.DB.prepare('SELECT * FROM payouts WHERE id=?').bind(u.get('id')).first();
    if (!r) return json({ error: 'not_found' }, 404);
    // 수정 화면에서만 전체를 준다 — 열었다는 사실을 남긴다
    await logEvent(env, { action: 'payout_view', actor: 'admin', detail: `${r.name} 주민번호 열람` });
    return json({ payout: { ...r, rrn: await rrnDec(env, r.rrn) } });
  }

  const ym = ymOf(u.get('ym'));
  const { results } = await env.DB.prepare(
    'SELECT * FROM payouts WHERE substr(paid_at,1,7)=? ORDER BY paid_at, id').bind(ym).all();
  const rows = await Promise.all((results || []).map(async (r) =>
    ({ ...r, rrn: await maskStored(env, r.rrn) })));
  const sum = rows.reduce((a, r) => ({
    gross: a.gross + (r.gross || 0), tax: a.tax + (r.tax_income || 0) + (r.tax_local || 0),
    net: a.net + (r.net || 0),
  }), { gross: 0, tax: 0, net: 0 });

  // 달 고르기용 — 기록이 있는 달만
  const months = ((await env.DB.prepare(
    'SELECT DISTINCT substr(paid_at,1,7) AS ym FROM payouts ORDER BY ym DESC LIMIT 36').all()).results || [])
    .map((x) => x.ym);
  const share = await env.DB.prepare(
    'SELECT ym, to_addr, expires_at, opened_at, created_at FROM payout_shares WHERE ym=? ORDER BY id DESC LIMIT 1')
    .bind(ym).first();

  // 평문으로 남아 있는 건이 몇 개인지 — 화면에서 «암호화하기»를 띄우는 근거
  const plain = (await env.DB.prepare(
    "SELECT COUNT(*) n FROM payouts WHERE IFNULL(rrn,'') <> '' AND rrn NOT LIKE 'v1:%'").first()) || {};
  return json({ ym, rows, sum, months, share, tax_mail: env.TAX_MAIL || 'better304@naver.com',
    enc: rrnKeyOn(env), plain: plain.n || 0 });
}

/* 지급을 기록하면서 «다음에도 쓰게» 명부에 남긴다.
   이미 있는 이름이면 빈 칸만 채운다 — 이번에 계좌를 안 적었다고
   전에 등록해 둔 계좌가 지워지면 안 된다. */
async function savePayee(env, name, rrn, bank, now) {
  await ensurePayees(env);
  const hit = await env.DB.prepare('SELECT * FROM payees WHERE name=?').bind(name).first();
  if (!hit) {
    return env.DB.prepare(
      'INSERT INTO payees (name, rrn, bank, memo, created_at, updated_at) VALUES (?,?,?,?,?,?)')
      .bind(name, rrn || '', bank || '', '', now, now).run().catch(() => {});
  }
  return env.DB.prepare('UPDATE payees SET rrn=?, bank=?, updated_at=? WHERE id=?')
    .bind(rrn || hit.rrn || '', bank || hit.bank || '', now, hit.id).run().catch(() => {});
}

async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  const now = kstISO();

  // 용역처 등록·수정 — 이름이 같으면 덮어쓴다(같은 사람을 두 줄로 만들지 않으려고)
  if (b.action === 'payee_save') {
    await ensurePayees(env);
    const name = String(b.name || '').trim();
    if (!name) return json({ error: 'no_name', message: '이름을 입력해주세요.' }, 400);
    const rrnPlain = digits(b.rrn);
    if (rrnPlain && rrnPlain.length !== 13) {
      return json({ error: 'bad_rrn', message: '주민등록번호 13자리를 정확히 입력해주세요.' }, 400);
    }
    const rrn = await rrnEnc(env, rrnPlain);
    const bank = String(b.bank || '').trim();
    const memo = String(b.memo || '').trim();
    const hit = b.id
      ? await env.DB.prepare('SELECT id FROM payees WHERE id=?').bind(b.id).first()
      : await env.DB.prepare('SELECT id FROM payees WHERE name=?').bind(name).first();
    if (hit) {
      await env.DB.prepare(
        'UPDATE payees SET name=?, rrn=?, bank=?, memo=?, updated_at=? WHERE id=?')
        .bind(name, rrn, bank, memo, now, hit.id).run();
      await logEvent(env, { action: 'payee_edit', actor: 'admin', detail: `용역처 ${name} 수정` });
      return json({ ok: true, id: hit.id });
    }
    const r = await env.DB.prepare(
      'INSERT INTO payees (name, rrn, bank, memo, created_at, updated_at) VALUES (?,?,?,?,?,?)')
      .bind(name, rrn, bank, memo, now, now).run();
    await logEvent(env, { action: 'payee_add', actor: 'admin', detail: `용역처 ${name} 등록` });
    return json({ ok: true, id: r.meta.last_row_id });
  }

  if (b.action === 'payee_delete') {
    await ensurePayees(env);
    const r = await env.DB.prepare('SELECT name FROM payees WHERE id=?').bind(b.id).first();
    if (!r) return json({ error: 'not_found' }, 404);
    await env.DB.prepare('DELETE FROM payees WHERE id=?').bind(b.id).run();
    // 이미 기록한 지급 내역은 그대로 둔다 — 명부에서만 지운다
    await logEvent(env, { action: 'payee_delete', actor: 'admin', detail: `용역처 ${r.name} 삭제` });
    return json({ ok: true });
  }

  /* 이미 평문으로 들어가 있는 것을 한 번에 암호문으로 바꾼다.
     여러 번 눌러도 안전하다 — 이미 'v1:' 인 건 건드리지 않는다. */
  if (b.action === 'rrn_migrate') {
    if (!rrnKeyOn(env)) {
      return json({ error: 'no_key',
        message: 'RRN_KEY 를 먼저 Cloudflare Secret 에 넣어주세요.' }, 400);
    }
    await ensurePayees(env);
    let n = 0;
    for (const t of ['payouts', 'payees']) {
      const { results } = await env.DB.prepare(
        `SELECT id, rrn FROM ${t} WHERE IFNULL(rrn,'') <> '' AND rrn NOT LIKE 'v1:%'`).all();
      for (const r of results || []) {
        const enc = await rrnEnc(env, r.rrn);
        await env.DB.prepare(`UPDATE ${t} SET rrn=? WHERE id=?`).bind(enc, r.id).run();
        n += 1;
      }
    }
    await logEvent(env, { action: 'rrn_migrate', actor: 'admin', detail: `주민번호 ${n}건 암호화` });
    return json({ ok: true, count: n });
  }

  /* 보관기간이 지난 건의 주민번호만 지운다. 금액·사유는 장부라 남긴다.
     지급명세서 신고가 끝나고 5년이 지나면 번호를 들고 있을 이유가 없다. */
  if (b.action === 'rrn_purge') {
    const yrs = Math.max(1, Math.min(10, Number(b.years) || 5));
    const cut = new Date(Date.now() + 9 * 3600e3);
    cut.setFullYear(cut.getFullYear() - yrs);
    const day = cut.toISOString().slice(0, 10);
    const r = await env.DB.prepare(
      "UPDATE payouts SET rrn='' WHERE IFNULL(rrn,'') <> '' AND paid_at < ?").bind(day).run();
    const n = (r.meta && r.meta.changes) || 0;
    await logEvent(env, { action: 'rrn_purge', actor: 'admin',
      detail: `${day} 이전 지급건 주민번호 ${n}건 파기` });
    return json({ ok: true, count: n, before: day });
  }

  if (b.action === 'delete') {
    const r = await env.DB.prepare('SELECT name, paid_at FROM payouts WHERE id=?').bind(b.id).first();
    await env.DB.prepare('DELETE FROM payouts WHERE id=?').bind(b.id).run();
    await logEvent(env, { action: 'payout_delete', actor: 'admin',
      detail: `용역비 지급 삭제 ${r ? `${r.paid_at} ${r.name}` : b.id}` });
    return json({ ok: true });
  }

  if (b.action === 'save') {
    const name = String(b.name || '').trim();
    if (!name) return json({ error: 'no_name', message: '받는 분 이름을 입력해주세요.' }, 400);
    const day = String(b.paid_at || '').slice(0, 10);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
      return json({ error: 'bad_date', message: '지급일을 정확히 입력해주세요.' }, 400);
    }
    const rrnPlain = digits(b.rrn);
    if (rrnPlain && rrnPlain.length !== 13) {
      return json({ error: 'bad_rrn', message: '주민등록번호 13자리를 정확히 입력해주세요.' }, 400);
    }
    const rrn = await rrnEnc(env, rrnPlain);   // 저장은 «항상» 암호문으로
    const gross = Math.max(0, Math.round(Number(b.gross) || 0));
    if (!gross) return json({ error: 'no_amount', message: '지급액을 입력해주세요.' }, 400);

    // 자동 계산값을 기본으로 쓰되, 손으로 고친 값이 오면 그걸 따른다 (기타소득 등)
    const auto = withhold(gross, b.rate);
    const inc = b.tax_income == null ? auto.tax_income : Math.max(0, Math.round(Number(b.tax_income) || 0));
    const loc = b.tax_local == null ? auto.tax_local : Math.max(0, Math.round(Number(b.tax_local) || 0));
    const net = gross - inc - loc;

    const args = [day, name, rrn, String(b.reason || '').trim(), gross, inc, loc, net,
                  String(b.bank || '').trim(), String(b.memo || '').trim()];

    if (b.id) {
      await env.DB.prepare(
        `UPDATE payouts SET paid_at=?, name=?, rrn=?, reason=?, gross=?, tax_income=?, tax_local=?,
                net=?, bank=?, memo=?, updated_at=? WHERE id=?`
      ).bind(...args, now, b.id).run();
      await logEvent(env, { action: 'payout_edit', actor: 'admin', detail: `용역비 ${day} ${name} 수정` });
      if (b.remember) await savePayee(env, name, rrn, String(b.bank || '').trim(), now);
      return json({ ok: true, id: b.id });
    }
    const r = await env.DB.prepare(
      `INSERT INTO payouts (paid_at, name, rrn, reason, gross, tax_income, tax_local, net, bank, memo,
              created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
    ).bind(...args, now, now).run();
    await logEvent(env, { action: 'payout_add', actor: 'admin',
      detail: `용역비 ${day} ${name} ${won(gross)}원` });
    if (b.remember) await savePayee(env, name, rrn, String(b.bank || '').trim(), now);
    return json({ ok: true, id: r.meta.last_row_id });
  }

  /* ---- 세무사에게 보내기 ----
     메일 본문에는 마스킹한 표만 싣는다. 전체 번호는 토큰이 있어야 열리는 링크 뒤에 둔다.
     메일함에 주민번호가 평문으로 쌓이면, 그 메일함이 곧 유출 경로가 된다. */
  if (b.action === 'share') {
    const ym = ymOf(b.ym);
    const to = String(b.to || env.TAX_MAIL || 'better304@naver.com').trim();
    if (!mailConfigured(env)) return json({ error: 'no_mail', message: 'RESEND_API_KEY 미설정' }, 400);

    const { results } = await env.DB.prepare(
      'SELECT * FROM payouts WHERE substr(paid_at,1,7)=? ORDER BY paid_at, id').bind(ym).all();
    const rows = results || [];
    if (!rows.length) return json({ error: 'empty', message: `${ym} 에 기록된 지급이 없습니다.` }, 400);

    await ensureShare(env);
    const token = randomToken();
    // 4자리 확인번호 — 메일에는 넣지 않는다. 대표가 전화·문자로 따로 알려준다.
    const pin = String(Math.floor(1000 + Math.random() * 9000));
    const exp = new Date(Date.now() + 7 * 864e5 + 9 * 3600e3).toISOString().slice(0, 19).replace('T', ' ');
    await env.DB.prepare(
      'INSERT INTO payout_shares (ym, token, to_addr, expires_at, created_at, pin, fails) VALUES (?,?,?,?,?,?,0)')
      .bind(ym, token, to, exp, now, pin).run();

    const origin = new URL(request.url).origin;
    const link = `${origin}/payout/${token}`;
    const esc = (t) => String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    const sum = rows.reduce((a, r) => ({
      gross: a.gross + (r.gross || 0), tax: a.tax + (r.tax_income || 0) + (r.tax_local || 0),
      net: a.net + (r.net || 0) }), { gross: 0, tax: 0, net: 0 });

    const masked = await Promise.all(rows.map(async (r) =>
      ({ ...r, mask: await maskStored(env, r.rrn) })));
    const tr = masked.map((r) => `<tr>
      <td style="padding:8px 6px;border-bottom:1px solid #eee">${esc(r.paid_at)}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee">${esc(r.name)}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee;color:#6B6B6B">${esc(r.mask)}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee">${esc(r.reason || '')}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:right">${won(r.gross)}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:right">${won((r.tax_income||0)+(r.tax_local||0))}</td>
      <td style="padding:8px 6px;border-bottom:1px solid #eee;text-align:right">${won(r.net)}</td></tr>`).join('');

    const html = `<div style="font-family:-apple-system,'Malgun Gothic',sans-serif;color:#1A1A1A;
        max-width:720px;margin:0 auto;padding:26px 22px;line-height:1.6">
      <div style="font-size:18px;font-weight:800;margin-bottom:4px">${ym} 용역비 지급내역</div>
      <div style="font-size:13px;color:#6B6B6B;margin-bottom:18px">실험셋업연구소 (이머전트) · 사업자 328-03-02926</div>
      <table style="width:100%;border-collapse:collapse;font-size:12.5px">
        <thead><tr style="background:#F2F4F6">
          <th style="padding:8px 6px;text-align:left">지급일</th>
          <th style="padding:8px 6px;text-align:left">성명</th>
          <th style="padding:8px 6px;text-align:left">주민등록번호</th>
          <th style="padding:8px 6px;text-align:left">지급 사유</th>
          <th style="padding:8px 6px;text-align:right">지급액</th>
          <th style="padding:8px 6px;text-align:right">원천징수</th>
          <th style="padding:8px 6px;text-align:right">실지급액</th>
        </tr></thead>
        <tbody>${tr}</tbody>
        <tfoot><tr style="font-weight:800;background:#FAFBFC">
          <td colspan="4" style="padding:9px 6px">합계 ${rows.length}건</td>
          <td style="padding:9px 6px;text-align:right">${won(sum.gross)}</td>
          <td style="padding:9px 6px;text-align:right">${won(sum.tax)}</td>
          <td style="padding:9px 6px;text-align:right">${won(sum.net)}</td>
        </tr></tfoot>
      </table>
      <div style="margin:22px 0 8px;padding:14px 16px;background:#EAF4FB;border-radius:10px">
        <div style="font-size:13.5px;font-weight:700;margin-bottom:6px">주민등록번호 전체는 아래 링크에서 확인하실 수 있습니다</div>
        <a href="${link}" style="display:inline-block;background:#3B3695;color:#fff;text-decoration:none;
          padding:11px 18px;border-radius:9px;font-size:13.5px;font-weight:700">전체 내역 열기</a>
        <div style="font-size:11.5px;color:#6B6B6B;margin-top:8px">
          메일에 주민등록번호를 그대로 싣지 않으려고 링크로 나눠 보냅니다.<br>
          링크를 열면 <b>4자리 확인번호</b>를 물어봅니다 — 번호는 따로 알려드립니다.<br>
          이 링크는 <b>${exp.slice(0, 10)}</b> 까지만 열립니다. 필요하시면 다시 보내드리겠습니다.</div>
      </div>
      <div style="font-size:12px;color:#9AA1AD;margin-top:20px">
        문의 070-8983-2600 · info@rndsetup.com</div>
    </div>`;

    /* 내 메일에도 한 통 남긴다. «보냈는데 안 왔다»고 할 때
       실제로 나갔는지, 어떤 모습으로 나갔는지 확인할 데가 있어야 한다.
       본문에는 마스킹된 번호만 있고 전체 번호는 토큰 링크 뒤에 있다. */
    const r = await sendMail(env, { to, bcc: mailBcc(env),
      subject: `[실험셋업연구소] ${ym} 용역비 지급내역`, html });
    await logEvent(env, { action: 'payout_share', actor: 'admin', result: r.ok ? 'ok' : 'fail',
      to_addr: to, detail: r.ok ? `${ym} 지급내역 ${rows.length}건 발송` : `발송 실패: ${r.error}` });
    if (!r.ok) return json({ error: 'send', message: r.error }, 502);
    // 확인번호는 «응답으로만» 준다 — 대표가 화면에서 보고 세무사에게 직접 전달한다
    return json({ ok: true, to, count: rows.length, expires_at: exp, pin });
  }

  return json({ error: 'unknown_action' }, 400);
}
