// GET /payout/:token — 세무사에게 보낸 «전체 주민번호 포함» 열람 페이지.
// 메일 본문에는 마스킹만 싣고, 전체는 이 토큰 뒤에 둔다. 토큰은 7일이면 죽는다.
import { kstISO } from '../api/_lib.js';
import { rrnDec } from '../api/_rrn.js';

const esc = (t) => String(t == null ? '' : t)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const won = (n) => Number(n || 0).toLocaleString('ko-KR');
const rrnFmt = (v) => {
  const d = String(v || '').replace(/[^0-9]/g, '');
  return d.length === 13 ? `${d.slice(0, 6)}-${d.slice(6)}` : d;
};
const page = (body) => new Response(
  `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>용역비 지급내역</title><style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,'Malgun Gothic',sans-serif;color:#1A1A1A;background:#F2F4F6;
  line-height:1.6;padding:26px 16px}
.wrap{max-width:860px;margin:0 auto;background:#fff;border-radius:14px;padding:26px 24px}
h1{font-size:19px;font-weight:800;margin-bottom:3px}
.sub{font-size:12.5px;color:#6B6B6B;margin-bottom:18px}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:700px}
th{background:#F2F4F6;padding:9px 7px;text-align:left;font-size:12px;font-weight:800;white-space:nowrap}
td{padding:9px 7px;border-bottom:1px solid #EAEAEA;white-space:nowrap}
td.n,th.n{text-align:right}
tfoot td{font-weight:800;background:#FAFBFC;border:0}
.note{margin-top:18px;font-size:12px;color:#6B6B6B;background:#FFF7ED;border:1px solid #FED7AA;
  border-radius:10px;padding:12px 14px}
.err{text-align:center;padding:40px 10px;color:#6B6B6B}
.gate{max-width:340px;margin:24px auto;text-align:center}
.gate p{font-size:13.5px;color:#6B6B6B;margin-bottom:16px}
.gate input{width:100%;border:1px solid #EAEAEA;border-radius:10px;padding:13px;font-size:20px;
  text-align:center;letter-spacing:.4em;font-weight:700}
.gate button{width:100%;margin-top:10px;background:#3B3695;color:#fff;border:0;border-radius:10px;
  padding:13px;font-size:14.5px;font-weight:700;cursor:pointer}
.gate .bad{color:#B42318;font-size:13px;margin-top:12px;font-weight:700}
</style></head><body><div class="wrap">${body}</div></body></html>`,
  { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });

/* 확인번호를 묻는 화면. 링크만 알아서는 전체 번호를 볼 수 없게 한다 —
   메일이 전달되거나 링크가 새어도 번호는 그대로 지켜진다. */
const gate = (bad) => page(`<h1>용역비 지급내역</h1>
  <div class="sub">실험셋업연구소 (이머전트)</div>
  <form class="gate" method="post">
    <p>확인번호 <b>4자리</b>를 입력해주세요.<br>번호는 실험셋업연구소에서 따로 알려드립니다.</p>
    <input name="pin" inputmode="numeric" maxlength="4" autocomplete="off" autofocus placeholder="0000">
    <button type="submit">열기</button>
    ${bad ? `<div class="bad">${bad}</div>` : ''}
  </form>`);

async function load(env, token) {
  const sh = await env.DB.prepare('SELECT * FROM payout_shares WHERE token=?').bind(token).first();
  if (!sh) return { err: page('<div class="err">링크가 올바르지 않습니다.</div>') };
  if (sh.expires_at && sh.expires_at < kstISO()) {
    return { err: page('<div class="err"><b>링크가 만료되었습니다.</b><br>'
      + '실험셋업연구소(070-8983-2600)로 알려주시면 다시 보내드리겠습니다.</div>') };
  }
  if ((sh.fails || 0) >= 5) {
    return { err: page('<div class="err"><b>확인번호를 여러 번 틀려 잠겼습니다.</b><br>'
      + '실험셋업연구소(070-8983-2600)로 알려주시면 새 링크를 보내드리겠습니다.</div>') };
  }
  return { sh };
}

// 확인번호 입력 — 맞으면 그 자리에서 내역을 그린다
export async function onRequestPost({ env, params, request }) {
  const { sh, err } = await load(env, params.token);
  if (err) return err;
  const fd = await request.formData().catch(() => null);
  const pin = String((fd && fd.get('pin')) || '').replace(/[^0-9]/g, '');
  if (sh.pin && pin !== sh.pin) {
    await env.DB.prepare('UPDATE payout_shares SET fails=IFNULL(fails,0)+1 WHERE id=?').bind(sh.id).run();
    const left = 5 - ((sh.fails || 0) + 1);
    return gate(left > 0 ? `확인번호가 다릅니다 — ${left}번 더 시도할 수 있습니다.` : '확인번호를 여러 번 틀려 잠겼습니다.');
  }
  return render(env, sh);
}

export async function onRequestGet({ env, params }) {
  const { sh, err } = await load(env, params.token);
  if (err) return err;
  // 예전에 보낸(확인번호 없는) 링크는 그대로 열어 준다
  if (sh.pin) return gate('');
  return render(env, sh);
}

async function render(env, sh) {
  if (!sh.opened_at) {
    await env.DB.prepare('UPDATE payout_shares SET opened_at=?, fails=0 WHERE id=?').bind(kstISO(), sh.id).run();
  }

  const { results } = await env.DB.prepare(
    'SELECT * FROM payouts WHERE substr(paid_at,1,7)=? ORDER BY paid_at, id').bind(sh.ym).all();
  const rows = await Promise.all((results || []).map(async (r) =>
    ({ ...r, rrn: await rrnDec(env, r.rrn) })));
  const sum = rows.reduce((a, r) => ({
    gross: a.gross + (r.gross || 0), tax: a.tax + (r.tax_income || 0) + (r.tax_local || 0),
    net: a.net + (r.net || 0) }), { gross: 0, tax: 0, net: 0 });

  return page(
    `<h1>${esc(sh.ym)} 용역비 지급내역</h1>
     <div class="sub">실험셋업연구소 (이머전트) · 사업자 328-03-02926 · 이영현</div>
     <div class="scroll"><table>
       <thead><tr><th>지급일</th><th>성명</th><th>주민등록번호</th><th>지급 사유</th>
         <th class="n">지급액</th><th class="n">소득세</th><th class="n">지방소득세</th>
         <th class="n">실지급액</th><th>계좌</th></tr></thead>
       <tbody>${rows.map((r) => `<tr>
         <td>${esc(r.paid_at)}</td><td>${esc(r.name)}</td><td>${esc(rrnFmt(r.rrn))}</td>
         <td>${esc(r.reason || '')}</td>
         <td class="n">${won(r.gross)}</td><td class="n">${won(r.tax_income)}</td>
         <td class="n">${won(r.tax_local)}</td><td class="n">${won(r.net)}</td>
         <td>${esc(r.bank || '')}</td></tr>`).join('')}</tbody>
       <tfoot><tr><td colspan="4">합계 ${rows.length}건</td>
         <td class="n">${won(sum.gross)}</td><td class="n" colspan="2">${won(sum.tax)}</td>
         <td class="n">${won(sum.net)}</td><td></td></tr></tfoot>
     </table></div>
     <div class="note">이 화면에는 <b>주민등록번호 전체</b>가 들어 있습니다. 내려받거나 옮겨 적으신 뒤에는
       화면을 닫아주세요. 이 링크는 <b>${esc(String(sh.expires_at || '').slice(0, 10))}</b> 까지만 열립니다.</div>`);
}
