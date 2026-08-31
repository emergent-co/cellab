// functions/api/_viewtpl.js — 고객에게 링크로 보여줄 '내용 확인' 페이지
//   승인받는 화면이 아니다. 우리가 적어둔 내용을 그대로 보여주고,
//   다르면 연락 달라고 말하는 것이 전부다.
import { ISSUER } from './_doctpl.js';

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
));
const won = (n) => Number(n || 0).toLocaleString('ko-KR');

function shell(title, badge, meta, body) {
  return `<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(title)} — 실험셋업연구소</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;background:#eceef1;color:#1a2332;
       line-height:1.6;padding:18px 14px 60px}
  .wrap{max-width:760px;margin:0 auto}
  .card{background:#fff;border:1px solid #e3e6ea;border-radius:14px;padding:26px;
        box-shadow:0 2px 14px rgba(15,23,42,.06)}
  .top{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px}
  h1{font-size:21px;font-weight:800;letter-spacing:-.02em}
  .bd{font-size:12px;font-weight:800;background:#eef1f6;color:#5a6779;border-radius:999px;padding:4px 11px}
  .meta{font-size:13px;color:#5a6779;margin-bottom:22px}
  .note{background:#F0F6FB;border:1px solid #cfe1f0;border-radius:11px;padding:13px 15px;
        font-size:13.5px;color:#1f4b6e;margin-bottom:22px}
  h2{font-size:12px;font-weight:800;color:#8a94a3;letter-spacing:.04em;margin:24px 0 9px}
  table{width:100%;border-collapse:collapse;font-size:13.5px}
  th,td{border:1px solid #e3e6ea;padding:9px 11px;text-align:center}
  th{background:#f6f7f9;font-weight:700;color:#5a6779;font-size:12.5px}
  td.l{text-align:left}
  td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
  td.l{word-break:keep-all}
  .mob{display:none}
  .kv{display:flex;gap:12px;font-size:13.5px;padding:7px 0;border-bottom:1px solid #f1f3f6}
  .kv:last-child{border-bottom:0}
  .kv span:first-child{flex:0 0 108px;color:#8a94a3}
  .kv span:last-child{flex:1;font-weight:600;word-break:break-all}
  .sum{margin-top:16px;margin-left:auto;width:min(340px,100%)}
  .sum td{padding:10px 12px}
  .sum td:first-child{background:#f6f7f9;color:#5a6779;font-weight:700;width:45%}
  .sum tr:last-child td{font-weight:800;font-size:15px}
  .foot{margin-top:26px;padding-top:18px;border-top:1px solid #e3e6ea;font-size:12.5px;color:#8a94a3;line-height:1.75}
  .foot b{color:#1a2332}
  @media(max-width:560px){.card{padding:18px 15px}h1{font-size:18px}
    th,td{padding:7px 6px;font-size:12.5px}.kv span:first-child{flex:0 0 82px}
    /* 좁은 화면에서는 칸이 모자라 품명이 한 글자씩 쪼개진다.
       번호·단가 칸을 접고 단가는 품명 아래에 적는다. */
    .no,.up{display:none}
    .mob{display:block;color:#8a94a3;font-size:11.5px;margin-top:2px}
  }
</style></head><body><div class="wrap"><div class="card">
  <div class="top"><h1>${esc(title)}</h1>${badge ? `<span class="bd">${esc(badge)}</span>` : ''}</div>
  <div class="meta">${esc(meta)}</div>
  <div class="note">아래 내용이 맞는지 확인해주세요. <b>다른 점이 있으면 알려주시면 바로 고쳐드립니다.</b><br>
    이 화면은 확인용이며, 따로 눌러야 할 버튼은 없습니다.</div>
  ${body}
  <div class="foot">
    <b>${esc(ISSUER.company)}</b> · 대표 ${esc(ISSUER.ceo)} · 사업자등록번호 ${esc(ISSUER.reg_no)}<br>
    ${esc(ISSUER.tel)} · info@rndsetup.com<br>
    ${esc(ISSUER.address)}
  </div>
</div></div></body></html>`;
}

export function orderViewHTML(o, items, customer) {
  const rows = (items || []).map((i, n) => {
    const qty = Number(i.qty) || 0;
    const up = Math.round(Number(i.unit_price) || 0);
    return `<tr><td class="no">${n + 1}</td>
      <td class="l">${esc(i.name)}${i.spec ? ` <small>(${esc(i.spec)})</small>` : ''}
        ${up ? `<small class="mob">단가 ${won(up)}원</small>` : ''}</td>
      <td>${qty}</td><td class="n up">${up ? won(up) : '—'}</td>
      <td class="n">${up ? won(Math.round(qty * up)) : '—'}</td></tr>`;
  }).join('');

  const supply = Number(o.supply_amount) || 0;
  const vat = Number(o.vat_amount) || 0;
  const total = Number(o.total_amount) || 0;

  const body = `
  <h2>주문 정보</h2>
  <div>
    <div class="kv"><span>주문번호</span><span>${esc(o.order_no || '')}</span></div>
    <div class="kv"><span>일자</span><span>${esc(String(o.created_at || '').slice(0, 10))}</span></div>
    <div class="kv"><span>소속</span><span>${esc(o.org_name || (customer && customer.company) || '')}</span></div>
    <div class="kv"><span>담당자</span><span>${esc(o.orderer_name || (customer && customer.name) || '')}</span></div>
    ${o.ship_address ? `<div class="kv"><span>납품지</span><span>${esc(o.ship_address)}</span></div>` : ''}
    ${o.request_note ? `<div class="kv"><span>요청사항</span><span>${esc(o.request_note)}</span></div>` : ''}
  </div>
  <h2>품목</h2>
  <table><thead><tr><th class="no" style="width:44px">No</th><th>품명</th>
    <th style="width:52px">수량</th><th class="up" style="width:96px">단가</th>
    <th style="width:104px">금액</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="5">품목이 없습니다.</td></tr>'}</tbody></table>
  ${total ? `<table class="sum">
    <tr><td>공급가액</td><td class="n">${won(supply)} 원</td></tr>
    <tr><td>부가세</td><td class="n">${won(vat)} 원</td></tr>
    <tr><td>합계</td><td class="n">${won(total)} 원</td></tr></table>` : ''}`;

  return shell(o.title || '주문 내용', o.status,
    `${esc(o.order_no || '')} · ${esc(String(o.created_at || '').slice(0, 10))}`, body);
}

export function settleViewHTML(s, items, customer, bill) {
  const r10 = (n) => Math.round(Number(n || 0) / 10) * 10;
  const rows = (items || []).map((i, n) => `<tr><td class="no">${n + 1}</td>
      <td class="l">${esc(i.name)}<small class="mob">단가 ${won(Math.round(i.price))}원</small></td>
      <td>${Number(i.qty) || 1}</td>
      <td class="n up">${won(Math.round(i.price))}</td>
      <td class="n">${won(r10((Number(i.qty) || 1) * Math.round(i.price)))}</td></tr>`).join('');

  const docs = [['견적서', s.quote_date], ['거래명세서', s.statement_date], ['세금계산서', s.taxinvoice_date]]
    .filter((d) => d[1]);

  const body = `
  <h2>정산 정보</h2>
  <div>
    <div class="kv"><span>요청일</span><span>${esc(String(s.created_at || '').slice(0, 10))}</span></div>
    <div class="kv"><span>거래처</span><span>${esc((customer && (customer.company || customer.name)) || '')}</span></div>
    <div class="kv"><span>결제 방식</span><span>${esc(s.method || '통장')}</span></div>
    <div class="kv"><span>진행 상태</span><span>${esc(s.status || '')}</span></div>
    ${bill ? `<div class="kv"><span>계산서 발행</span><span>${esc(bill.company || '')}${bill.biz_no ? ` · ${esc(bill.biz_no)}` : ''}</span></div>` : ''}
  </div>
  <h2>항목 <small style="font-weight:400;color:#8a94a3">단가·금액은 부가세 포함입니다</small></h2>
  <table><thead><tr><th class="no" style="width:44px">No</th><th>항목</th>
    <th style="width:52px">수량</th><th class="up" style="width:104px">단가</th>
    <th style="width:112px">금액</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="5">항목이 없습니다.</td></tr>'}</tbody></table>
  <table class="sum">
    <tr><td>공급가액</td><td class="n">${won(s.supply)} 원</td></tr>
    <tr><td>부가세</td><td class="n">${won(s.vat)} 원</td></tr>
    <tr><td>총계</td><td class="n">${won(s.total)} 원 (VAT 포함)</td></tr></table>
  ${docs.length ? `<h2>서류 발행 예정일</h2><div>${docs.map((d) =>
      `<div class="kv"><span>${esc(d[0])}</span><span>${esc(d[1])}</span></div>`).join('')}</div>` : ''}`;

  const first = (items || [])[0];
  const title = first ? `${first.name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''}` : '정산 내용';
  return shell(title, s.status, `정산 내용 · ${esc(String(s.created_at || '').slice(0, 10))}`, body);
}
