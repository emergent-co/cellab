// functions/admin/settlement/index.js — 후불 거래처 정산 (모바일 우선) · Basic Auth

import { adminOK, REALM } from '../../api/_lib.js';
import { SHELL_CSS, shellTop, SHELL_END } from '../_shell.js';

export async function onRequest({ request, env }) {
  // 카카오 세션이 관리자면 비밀번호를 다시 묻지 않는다.
  // ADMIN_PASSWORD Basic Auth 도 그대로 통한다 — 카카오가 막혔을 때의 비상구.
  const auth = request.headers.get('Authorization') || '';
  if (!(await adminOK(request, env))) {
    return new Response('인증이 필요합니다. (관리자)', {
      status: 401,
      headers: { 'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
                 'content-type': 'text/plain; charset=utf-8' },
    });
  }
  return new Response(page(auth.startsWith('Basic ') ? auth.slice(6) : ''), {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
}

function page(token) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0a2540">
<title>정산 관리 — rndsetup</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
${SHELL_CSS}
button,input,select{font:inherit;color:inherit}
.wrap{padding:12px 12px 90px;max-width:900px;margin:0 auto}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:14px 15px;margin-bottom:9px;cursor:pointer}
.r1{display:flex;align-items:center;gap:8px}
.nm{font-size:15px;font-weight:700}
.tag{font-size:11px;font-weight:800;border-radius:999px;padding:3px 9px;background:#eef2f7;color:var(--mut)}
.tag.post{background:#FEF3C7;color:#92400E}
.due{margin-left:auto;font-size:16px;font-weight:800;font-variant-numeric:tabular-nums}
.due.z{color:var(--mut);font-weight:700}
.sub{font-size:12.5px;color:var(--mut);margin-top:4px;display:flex;gap:12px;flex-wrap:wrap;font-variant-numeric:tabular-nums}
.empty{text-align:center;color:var(--mut);font-size:14px;padding:50px 20px}
.sheet{position:fixed;inset:0;z-index:40;background:rgba(10,37,64,.45);display:none}
.sheet.on{display:block}
.sbody{position:absolute;left:0;right:0;bottom:0;top:24px;background:var(--bg);border-radius:16px 16px 0 0;overflow-y:auto}
.shead{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:13px 14px;display:flex;align-items:center;gap:10px;border-radius:16px 16px 0 0;z-index:5}
.shead .x{margin-left:auto;border:0;background:#eef2f7;border-radius:9px;width:34px;height:34px;font-size:19px;color:var(--mut);cursor:pointer}
.sec{background:#fff;border:1px solid var(--line);border-radius:13px;margin:11px 12px;padding:14px 15px}
.sec h3{font-size:12.5px;font-weight:800;color:var(--mut);margin-bottom:11px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:11px;padding:12px}
.kpi span{font-size:11.5px;color:var(--mut);font-weight:600}
.kpi b{display:block;font-size:16px;font-weight:800;margin-top:6px;text-align:right;font-variant-numeric:tabular-nums}
.kpi.hi{border-color:#f0c98a;background:#FFFBF3}
.lg{display:flex;gap:10px;font-size:13px;padding:9px 0;border-bottom:1px dashed var(--line);align-items:center}
.lg:last-child{border-bottom:0}
.lg time{flex:0 0 74px;color:var(--mut);font-size:12px;font-variant-numeric:tabular-nums}
.lg .t{flex:1;min-width:0}
.lg .t b{display:block;font-weight:700}
.lg .t small{color:var(--mut);font-size:11.5px}
.lg .a{font-weight:800;font-variant-numeric:tabular-nums;white-space:nowrap}
.lg .a.m{color:#166534}
label{display:block;font-size:12px;font-weight:700;color:var(--mut);margin:11px 0 5px}
input,select{width:100%;border:1px solid var(--line);border-radius:9px;padding:12px;font-size:15px;background:#fbfcfe}
.two{display:flex;gap:8px}.two>div{flex:1}
.bar{position:sticky;bottom:0;background:#fff;border-top:1px solid var(--line);padding:11px 12px calc(11px + env(safe-area-inset-bottom));display:flex;gap:8px}
.bar button{flex:1;border:0;border-radius:11px;padding:14px;font-size:15px;font-weight:800;cursor:pointer}
.bar .pay{background:var(--teal);color:#fff}
.bar .mode{background:#eef2f7;color:var(--mut)}
.modal{position:fixed;inset:0;z-index:70;background:rgba(10,37,64,.5);display:flex;align-items:flex-end;justify-content:center}
.mbox{background:#fff;width:100%;max-width:520px;border-radius:16px 16px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom))}
.mbox h4{font-size:16px;font-weight:800}
.mrow{display:flex;gap:8px;margin-top:16px}
.mrow button{flex:1;border:0;border-radius:11px;padding:14px;font-size:15px;font-weight:800;cursor:pointer}
.mrow .g{background:#eef2f7;color:var(--mut)}.mrow .o{background:var(--teal);color:#fff}
.toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0a2540;color:#fff;padding:11px 19px;border-radius:11px;font-size:14px;font-weight:700;z-index:80;opacity:0;transition:opacity .2s;pointer-events:none}
.toast.on{opacity:.95}
@media(min-width:820px){.sbody{left:50%;transform:translateX(-50%);max-width:720px;border-radius:16px;top:40px;bottom:40px}.modal{align-items:center}.mbox{border-radius:16px}}
</style>
</head>
<body>
${shellTop("정산 관리", "settle")}
<div class="wrap" id="list"><div class="empty">불러오는 중…</div></div>
<div class="sheet" id="sheet"><div class="sbody" id="sbody"></div></div>
<div class="toast" id="toast"></div>
<script>
const TOKEN = ${JSON.stringify(token)};
const H = TOKEN ? { 'Authorization':'Basic '+TOKEN, 'content-type':'application/json' }
                : { 'content-type':'application/json' };
const won = function(n){ return Number(n||0).toLocaleString('ko-KR'); };
const esc = function(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
function toast(m){ var t=document.getElementById('toast'); t.textContent=m; t.classList.add('on'); setTimeout(function(){t.classList.remove('on');},1800); }
let cur=null;

async function load(){
  var r = await fetch('/api/admin/settlement',{headers:H}).then(function(r){return r.json();});
  var el = document.getElementById('list');
  var cs = r.customers||[];
  if(!cs.length){ el.innerHTML='<div class="empty">거래처가 없습니다.</div>'; return; }
  el.innerHTML = cs.map(function(c){
    return '<div class="card" data-id="'+c.id+'">'
      +'<div class="r1"><span class="nm">'+esc(c.company||c.name||'—')+'</span>'
        +'<span class="tag'+(c.billing_mode==='후불'?' post':'')+'">'+esc(c.billing_mode||'선불')+'</span>'
        +'<span class="due'+(c.due?'':' z')+'">'+won(c.due)+'원</span></div>'
      +'<div class="sub"><span>지출 '+won(c.spent)+'</span><span>정산 '+won(c.paid)+'</span>'
        +'<span>'+esc(c.name||'')+'</span></div></div>';
  }).join('');
  el.querySelectorAll('.card').forEach(function(x){ x.onclick=function(){ open(x.dataset.id); }; });
}

async function open(id){
  var d = await fetch('/api/admin/settlement?customer_id='+id,{headers:H}).then(function(r){return r.json();});
  cur = d;
  document.getElementById('sheet').classList.add('on');
  document.body.style.overflow='hidden';
  var c = d.customer;
  document.getElementById('sbody').innerHTML =
    '<div class="shead"><span class="nm">'+esc(c.company||c.name)+'</span>'
      +'<span class="tag'+(c.billing_mode==='후불'?' post':'')+'">'+esc(c.billing_mode||'선불')+'</span>'
      +'<button class="x" id="cx">×</button></div>'
   +'<div class="sec"><div class="kpis">'
     +'<div class="kpi"><span>지출금</span><b>'+won(d.spent)+'</b></div>'
     +'<div class="kpi"><span>중간정산금</span><b>'+won(d.paid)+'</b></div>'
     +'<div class="kpi hi"><span>정산금 잔여</span><b>'+won(d.due)+'</b></div>'
   +'</div></div>'
   +'<div class="sec"><h3>거래 내역</h3>'
     +((d.ledger||[]).length ? d.ledger.map(function(r){
        var neg = r.amount<0;
        return '<div class="lg"><time>'+esc(r.at)+'</time>'
          +'<div class="t"><b>'+esc(r.label)+'</b><small>'+esc(r.kind)+(r.ref?' · '+esc(r.ref):'')
            +' · 잔액 '+won(r.balance)+'</small></div>'
          +'<div class="a'+(neg?' m':'')+'">'+(neg?'−':'+')+won(Math.abs(r.amount))+'</div>'
          +(r.payment_id?'<button class="x" style="width:28px;height:28px;font-size:15px" data-pd="'+r.payment_id+'">×</button>':'')
          +'</div>'; }).join('') : '<div style="font-size:13px;color:var(--mut)">내역 없음</div>')
   +'</div>'
   +'<div class="bar"><button class="mode" id="mode">'+(c.billing_mode==='후불'?'선불로 전환':'후불(멤버십)로 전환')+'</button>'
     +'<button class="pay" id="pay">입금 기록</button></div>';

  document.getElementById('cx').onclick = close;
  document.getElementById('pay').onclick = payForm;
  document.getElementById('mode').onclick = async function(){
    var next = c.billing_mode==='후불' ? '선불' : '후불';
    if(!confirm(next+'로 바꿀까요?')) return;
    await fetch('/api/admin/settlement',{method:'POST',headers:H,
      body:JSON.stringify({action:'mode',customer_id:c.id,billing_mode:next})});
    toast(next+'로 전환됨'); open(c.id); load();
  };
  document.querySelectorAll('[data-pd]').forEach(function(b){
    b.onclick = async function(){
      if(!confirm('이 입금 기록을 삭제할까요?')) return;
      await fetch('/api/admin/settlement',{method:'POST',headers:H,
        body:JSON.stringify({action:'delete_pay',payment_id:Number(b.dataset.pd)})});
      toast('삭제됨'); open(c.id); load();
    };
  });
}
function close(){ document.getElementById('sheet').classList.remove('on'); document.body.style.overflow=''; cur=null; }
document.getElementById('sheet').onclick = function(e){ if(e.target.id==='sheet') close(); };

function payForm(){
  var w = document.createElement('div'); w.className='modal';
  var today = new Date(Date.now()+9*3600000).toISOString().slice(0,10);
  w.innerHTML = '<div class="mbox"><h4>입금 · 조정 기록</h4>'
    +'<label>구분</label><select id="p-kind"><option>입금</option><option>조정</option></select>'
    +'<label>금액 (조정은 음수 입력 가능)</label><input id="p-amt" type="number" inputmode="numeric" placeholder="0">'
    +'<div class="two"><div><label>방식</label><select id="p-m"><option>통장</option><option>카드</option><option>기타</option></select></div>'
      +'<div><label>일자</label><input id="p-at" type="date" value="'+today+'"></div></div>'
    +'<label>메모</label><input id="p-memo" placeholder="예) 8월분 중간정산">'
    +'<div class="mrow"><button class="g" id="p-x">닫기</button><button class="o" id="p-go">저장</button></div></div>';
  document.body.appendChild(w);
  document.getElementById('p-x').onclick=function(){ w.remove(); };
  w.onclick=function(e){ if(e.target===w) w.remove(); };
  document.getElementById('p-go').onclick = async function(){
    var amt = Number(document.getElementById('p-amt').value);
    if(!amt) return alert('금액을 입력해주세요.');
    var r = await fetch('/api/admin/settlement',{method:'POST',headers:H,body:JSON.stringify({
      action:'pay', customer_id:cur.customer.id, kind:document.getElementById('p-kind').value,
      amount:amt, method:document.getElementById('p-m').value,
      paid_at:document.getElementById('p-at').value, memo:document.getElementById('p-memo').value })})
      .then(function(r){return r.json();});
    if(!r.ok) return alert(r.message||'실패');
    w.remove(); toast('기록되었습니다'); open(cur.customer.id); load();
  };
}
load();
</` + `script>
${SHELL_END}
</body>
</html>`;
}
