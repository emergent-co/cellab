// functions/api/_doctpl.js — 견적서 / 거래명세서 HTML 템플릿 (이머전트 기존 양식 재현)
// A4 세로 1장. Browser Rendering으로 PDF 변환하거나 브라우저에서 그대로 인쇄 가능.
import { STAMP_PNG } from './_docassets.js';

export const ISSUER = {
  company: '이머전트',
  ceo: '이영현',
  reg_no: '3280302926',
  tel: '070-8983-2600',
  address: '부산시 북구 화명신도시로219, 화명뜨란채 107-1703',
  biz_type: '서비스 | 도소매',
  biz_item: '정밀기기 수리업 | 화학물질 및 과학 기기 도매업',
  bank: '신한 | 이영현(이머전트) | 110-273-881229',
};

const TITLE = { quote: '견적서', statement: '거래명세서' };

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
const won = (n) => Number(n || 0).toLocaleString('ko-KR');

// 값이 한 줄에 들어가도록 폰트 크기를 자동으로 줄인다 (행 높이 균일화).
// 한글·전각 = 1.0폭, 그 외 = 0.5폭 기준. 반환값 pt.
function fitPt(text, boxMm, maxPt = 9.1, minPt = 6.6) {
  const t = String(text == null ? '' : text);
  let u = 0;
  for (const ch of t) u += /[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF\u3000-\u303F\uFF00-\uFFEF]/.test(ch) ? 1 : 0.5;
  if (!u) return maxPt;
  const pt = boxMm / (u * 0.3528);
  return Math.max(minPt, Math.min(maxPt, Math.floor(pt * 10) / 10));
}

/**
 * @param {object} d
 *   type: 'quote' | 'statement'
 *   doc_no, issue_date(YYYY-MM-DD), valid_until, title
 *   client: { company, contact, email }
 *   items: [{ name, spec, qty, unit_price, note }]
 *   note: 하단 비고(기본 계좌)
 */
export function renderDocHTML(d) {
  const LW = 47, RW = 74;   // 좌/우 박스의 값 영역 폭(mm)
  const L = (v) => `<span class="pv" style="font-size:${fitPt(v, LW)}pt">${esc(v || '')}</span>`;
  const R = (v) => `<span class="pv" style="font-size:${fitPt(v, RW)}pt">${esc(v || '')}</span>`;
  const type = d.type === 'statement' ? 'statement' : 'quote';
  const items = (d.items || []).filter((i) => String(i.name || '').trim());

  let supply = 0;
  const rows = items.map((it, i) => {
    const qty = Number(it.qty) || 0;
    const up = Math.round(Number(it.unit_price) || 0);
    const line = Math.round(qty * up);
    supply += line;
    const spec = String(it.spec || '').trim();
    return `<tr>
      <td class="c">${i + 1}</td>
      <td class="c">${esc(it.name)}${spec ? ` (${esc(spec)})` : ''}</td>
      <td class="c">${qty}</td>
      <td class="c">${won(up)}</td>
      <td class="c">${won(it.amount != null ? Math.round(Number(it.amount) || 0) : Math.round(line * 1.1))}</td>
      <td class="c">${esc(it.note || '')}</td>
    </tr>`;
  }).join('');

  // 정산 요청처럼 '부가세 포함 총액'이 먼저 정해진 경우, 그 값을 그대로 쓴다.
  // 1.1을 다시 곱해 1원이 어긋나는 것을 막는다.
  const fx = d.totals && Number(d.totals.total) ? d.totals : null;
  if (fx) supply = Math.round(Number(fx.supply) || 0);
  const vat = fx ? Math.round(Number(fx.vat) || 0) : Math.round(supply * 0.1);
  const total = fx ? Math.round(Number(fx.total) || 0) : supply + vat;

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>${esc(TITLE[type])} ${esc(d.doc_no || '')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  @page{ size:A4; margin:0; }
  *{ box-sizing:border-box; margin:0; padding:0; }
  body{ font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;
        color:#111; background:#fff; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .page{ width:210mm; min-height:297mm; padding:20mm 17mm; margin:0 auto; background:#fff;
         display:flex; flex-direction:column; }
  h1{ text-align:center; font-size:25pt; font-weight:500; letter-spacing:.22em;
      text-indent:.22em; margin:6mm 0 10mm; }
  table{ width:100%; border-collapse:collapse; font-size:9.6pt; }
  td,th{ border:.6pt solid #4a4a4a; padding:2.4mm 2.6mm; vertical-align:middle; line-height:1.35; }
  th{ font-weight:500; background:#f2f2f2; text-align:center; }
  .lb{ background:#f2f2f2; text-align:center; font-weight:500; white-space:nowrap; }
  .c{ text-align:center; }
  .blk{ margin-bottom:3.4mm; }
  .parties{ display:flex; gap:5mm; margin-bottom:1mm; align-items:stretch; }
  .party{ flex:42 1 0; border:.6pt solid #4a4a4a; position:relative; display:flex; flex-direction:column; }
  .ph{ background:#f2f2f2; border-bottom:.6pt solid #4a4a4a; text-align:center;
       font-size:9.4pt; font-weight:500; padding:1.7mm 0; letter-spacing:.04em; }
  .plist{ flex:1; display:flex; flex-direction:column; padding:1.4mm 3mm; }
  .prow{ flex:1 0 auto; display:flex; align-items:center; min-height:6.4mm; font-size:9.1pt; }
  .pk{ flex:0 0 19mm; color:#555; }
  .pv{ flex:1; line-height:1.3; white-space:nowrap; overflow:hidden; }
  .party.issuer{ flex:58 1 0; }
  .stamp{ position:absolute; right:3mm; top:8.5mm; width:17mm; height:17mm; opacity:.9; }
  .items{ margin-top:5mm; }
  .items th{ font-size:9.6pt; }
  .items td{ height:9mm; }
  .sm{ font-size:7.6pt; }
  .bottom{ margin-top:auto; padding-top:8mm; }
  .sumwrap{ display:flex; justify-content:flex-end; }
  .sum{ width:56%; border-collapse:collapse; }
  .sum td{ padding:2.6mm 3mm; }
  .sum .lb{ width:42%; }
  .sum .v{ text-align:left; }
  .foot{ margin-top:5mm; }
  .foot .lb{ width:14.5%; }
</style>
</head>
<body>
<div class="page">
  <h1>${esc(TITLE[type])}</h1>

  <table class="blk">
    <tr><td class="lb" style="width:14.5%">견적명</td><td style="width:37%">${esc(d.title || '')}</td>
        <td class="lb" style="width:14.5%">견적번호</td><td>${esc(d.doc_no || '')}</td></tr>
    <tr><td class="lb">발행일자</td><td>${esc(d.issue_date || '')}</td>
        <td class="lb">유효기간</td><td>${esc(d.valid_until || '')}</td></tr>
  </table>

  <div class="parties">
    <div class="party">
      <div class="ph">공급받는자</div>
      <div class="plist">
        <div class="prow"><span class="pk">상호</span>${L(d.client?.company)}</div>
        <div class="prow"><span class="pk">사업자번호</span>${L(d.client?.biz_no)}</div>
        <div class="prow"><span class="pk">대표자명</span>${L(d.client?.ceo)}</div>
        <div class="prow"><span class="pk">담당자</span>${L(d.client?.contact)}</div>
        <div class="prow"><span class="pk">이메일</span>${L(d.client?.email)}</div>
        <div class="prow"><span class="pk">주소</span>${L(d.client?.address)}</div>
      </div>
    </div>
    <div class="party issuer">
      <img class="stamp" src="${STAMP_PNG}" alt="">
      <div class="ph">공급자</div>
      <div class="plist">
        <div class="prow"><span class="pk">상호</span>${R(ISSUER.company)}</div>
        <div class="prow"><span class="pk">사업자번호</span>${R(ISSUER.reg_no)}</div>
        <div class="prow"><span class="pk">대표자명</span>${R(ISSUER.ceo)}</div>
        <div class="prow"><span class="pk">전화</span>${R(ISSUER.tel)}</div>
        <div class="prow"><span class="pk">주소</span>${R(ISSUER.address)}</div>
        <div class="prow"><span class="pk">업태/업종</span>${R(ISSUER.biz_type + ' / ' + ISSUER.biz_item)}</div>
      </div>
    </div>
  </div>

  <table class="items">
    <thead><tr>
      <th style="width:7%">No</th><th style="width:38%">품명(규격)</th>
      <th style="width:9%">수량</th><th style="width:16%">단가</th>
      <th style="width:20%">금액<span class="sm">(부가세포함)</span></th><th style="width:10%">비고</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>

  <div class="bottom">
    <div class="sumwrap">
      <table class="sum">
        <tr><td class="lb">공급가액</td><td class="v">${won(supply)} 원</td></tr>
        <tr><td class="lb">부가세</td><td class="v">${won(vat)} 원</td></tr>
        <tr><td class="lb">합계</td><td class="v">${won(total)} 원 (VAT 포함)</td></tr>
      </table>
    </div>
    <table class="foot">
      <tr><td class="lb">비고</td><td>${esc(d.note || ISSUER.bank)}</td></tr>
    </table>
  </div>
</div>
</body>
</html>`;
}

export function docTotals(items, fixed) {
  if (fixed && Number(fixed.total)) {
    return { supply: Math.round(Number(fixed.supply) || 0),
             vat: Math.round(Number(fixed.vat) || 0),
             total: Math.round(Number(fixed.total) || 0) };
  }
  const supply = (items || []).reduce((s, i) => s + Math.round((Number(i.qty) || 0) * (Number(i.unit_price) || 0)), 0);
  const vat = Math.round(supply * 0.1);
  return { supply, vat, total: supply + vat };
}
