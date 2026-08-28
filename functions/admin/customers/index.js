// functions/admin/customers/index.js — 거래처 승인 · 견적 문의 (모바일 우선) · Basic Auth
//   주문·정산 페이지는 '승인'된 거래처만 열린다. 여기서 승인/대기/거절을 정한다.

const REALM = 'rndsetup-admin';

export async function onRequest({ request, env }) {
  const pw = env.ADMIN_PASSWORD || '';
  const auth = request.headers.get('Authorization') || '';
  let ok = false;
  if (pw && auth.startsWith('Basic ')) {
    try { const d = atob(auth.slice(6)); const i = d.indexOf(':');
      ok = (i >= 0 ? d.slice(i + 1) : d) === pw; } catch { ok = false; }
  }
  if (!ok) {
    return new Response('인증이 필요합니다. (관리자)', { status: 401,
      headers: { 'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
                 'content-type': 'text/plain; charset=utf-8' } });
  }
  return new Response(page(auth.slice(6)), {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' },
  });
}

function page(token) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>거래처 승인 — rndsetup</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#0a2540;--teal:#1a6e56;--ink:#1a2332;--mut:#5a6779;--line:#e3e8ef;--bg:#f4f6fa}
html,body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Apple SD Gothic Neo','Malgun Gothic',sans-serif;
  color:var(--ink);background:var(--bg);line-height:1.5;-webkit-text-size-adjust:100%}
button,input,select{font:inherit;color:inherit}
.top{position:sticky;top:0;z-index:20;background:var(--navy);color:#fff;padding:calc(10px + env(safe-area-inset-top)) 14px 10px}
.top h1{font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px}
.top h1 a{color:#9fc3e8;text-decoration:none;font-size:12.5px;font-weight:600}
.top h1 a.r{margin-left:auto}
.tabs{display:flex;gap:6px;padding:11px 12px 0;max-width:900px;margin:0 auto}
.tabs button{flex:1;border:1px solid var(--line);background:#fff;border-radius:10px;padding:10px;
  font-size:13.5px;font-weight:700;color:var(--mut);cursor:pointer}
.tabs button.on{background:var(--navy);border-color:var(--navy);color:#fff}
.tabs button i{font-style:normal;background:#FEE2E2;color:#991B1B;border-radius:9px;padding:1px 6px;font-size:11px;margin-left:5px}
.tabs button.on i{background:rgba(255,255,255,.2);color:#fff}
.wrap{padding:12px 12px 90px;max-width:900px;margin:0 auto}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:14px 15px;margin-bottom:9px}
.card.wait{border-color:#f0c98a;background:#FFFBF3}
.r1{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.nm{font-size:15px;font-weight:700}
.tag{font-size:11px;font-weight:800;border-radius:999px;padding:3px 9px;background:#eef2f7;color:var(--mut)}
.tag.w{background:#FEF3C7;color:#92400E}.tag.o{background:#D1FAE5;color:#065F46}.tag.x{background:#FEE2E2;color:#991B1B}
.sub{font-size:12.5px;color:var(--mut);margin-top:5px;display:flex;gap:10px;flex-wrap:wrap;word-break:break-all}
.acts{display:flex;gap:7px;margin-top:11px}
.acts button{flex:1;border:0;border-radius:10px;padding:11px;font-size:13.5px;font-weight:800;cursor:pointer}
.acts .ok{background:var(--teal);color:#fff}
.acts .no{background:#eef2f7;color:var(--mut)}
.acts .rv{background:#FEE2E2;color:#991B1B}
.items{margin-top:9px;border-top:1px dashed var(--line);padding-top:9px}
.it{display:flex;gap:9px;font-size:13px;padding:4px 0}
.it .q{margin-left:auto;font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap}
.it a{color:var(--teal);font-size:11.5px;text-decoration:none}
.note{margin-top:8px;font-size:13px;background:#f7f9fc;border-radius:9px;padding:10px;white-space:pre-wrap}
.empty{text-align:center;color:var(--mut);font-size:14px;padding:50px 20px}
.toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0a2540;color:#fff;
  padding:11px 19px;border-radius:11px;font-size:14px;font-weight:700;z-index:80;opacity:0;
  transition:opacity .2s;pointer-events:none}
.toast.on{opacity:.95}
</style>
</head>
<body>
<div class="top"><h1>거래처 승인<a class="r" href="/admin/orders/">주문관리 →</a><a href="/admin/settlement/">정산 →</a></h1></div>
<div class="tabs" id="tabs">
  <button data-t="cust" class="on">거래처 <i id="nWait" hidden>0</i></button>
  <button data-t="inq">견적 문의 <i id="nInq" hidden>0</i></button>
</div>
<div class="wrap" id="list"><div class="empty">불러오는 중…</div></div>
<div class="toast" id="toast"></div>

<script>
var TOKEN = ${JSON.stringify(token)};
var H = { 'Authorization': 'Basic ' + TOKEN, 'content-type': 'application/json' };
var $ = function(s){ return document.querySelector(s); };
var esc = function(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
function toast(m){ var t=$('#toast'); t.textContent=m; t.classList.add('on');
  setTimeout(function(){ t.classList.remove('on'); },1800); }

var tab='cust', custs=[], inqs=[];

$('#tabs').onclick=function(e){ var b=e.target.closest('button[data-t]'); if(!b) return;
  tab=b.dataset.t; document.querySelectorAll('#tabs button').forEach(function(x){x.classList.toggle('on',x===b);});
  paint(); };

async function load(){
  var a = await fetch('/api/admin/customers',{headers:H}).then(function(r){return r.json();}).catch(function(){return{};});
  custs = a.customers||[];
  var b = await fetch('/api/admin/customers?inquiries=1',{headers:H}).then(function(r){return r.json();}).catch(function(){return{};});
  inqs = b.inquiries||[];
  var w = custs.filter(function(c){return c.access==='대기';}).length;
  var n = inqs.filter(function(x){return x.status==='접수';}).length;
  $('#nWait').textContent=w; $('#nWait').hidden=!w;
  $('#nInq').textContent=n; $('#nInq').hidden=!n;
  paint();
}

function paint(){ tab==='cust' ? paintCust() : paintInq(); }

var TAGC={'대기':'w','승인':'o','거절':'x'};
function paintCust(){
  if(!custs.length) return $('#list').innerHTML='<div class="empty">거래처가 없습니다.</div>';
  $('#list').innerHTML = custs.map(function(c){
    var wait = c.access==='대기';
    return '<div class="card'+(wait?' wait':'')+'">'
      +'<div class="r1"><span class="nm">'+esc(c.company||c.name||'—')+'</span>'
        +'<span class="tag '+(TAGC[c.access]||'')+'">'+esc(c.access||'대기')+'</span>'
        +(c.n_orders?'<span class="tag">주문 '+c.n_orders+'</span>':'')+'</div>'
      +'<div class="sub"><span>'+esc(c.name||'—')+'</span>'
        +'<span>'+esc(c.work_email||c.email||'—')+'</span>'
        +(c.phone?'<span>'+esc(c.phone)+'</span>':'')
        +(c.lab_name?'<span>실험실 '+esc(c.lab_name)+' ('+esc(c.lab_code||'')+')</span>':'')
        +'<span>'+esc(String(c.created_at||'').slice(0,10))+'</span></div>'
      +'<div class="acts">'
        +(c.access!=='승인'?'<button class="ok" data-id="'+c.id+'" data-a="승인">승인</button>':'')
        +(c.access!=='대기'?'<button class="no" data-id="'+c.id+'" data-a="대기">대기로</button>':'')
        +(c.access!=='거절'?'<button class="rv" data-id="'+c.id+'" data-a="거절">거절</button>':'')
      +'</div></div>';
  }).join('');
  document.querySelectorAll('.acts button').forEach(function(b){
    b.onclick = async function(){
      var a=b.dataset.a;
      if(a!=='승인' && !confirm('이 거래처를 "'+a+'" 상태로 바꿀까요?')) return;
      b.disabled=true;
      var r = await fetch('/api/admin/customers',{method:'POST',headers:H,
        body:JSON.stringify({id:Number(b.dataset.id),access:a})}).then(function(x){return x.json();});
      if(r.ok){ toast(a+' 처리했습니다'); load(); } else { b.disabled=false; alert(r.message||'실패'); }
    };
  });
}

function paintInq(){
  if(!inqs.length) return $('#list').innerHTML='<div class="empty">들어온 문의가 없습니다.</div>';
  $('#list').innerHTML = inqs.map(function(q){
    var items=(q.items||[]);
    return '<div class="card">'
      +'<div class="r1"><span class="nm">'+esc(q.name||'—')+'</span>'
        +(q.org_name?'<span class="tag">'+esc(q.org_name)+'</span>':'')
        +'<span class="tag">'+items.length+'건</span></div>'
      +'<div class="sub">'+(q.email?'<span>'+esc(q.email)+'</span>':'')
        +(q.phone?'<span>'+esc(q.phone)+'</span>':'')
        +'<span>'+esc(String(q.created_at||'').slice(0,16))+'</span></div>'
      +(items.length?'<div class="items">'+items.map(function(i){
          return '<div class="it"><div>'+esc(i.name)
            +(i.spec?'<br><small style="color:var(--mut)">'+esc(i.spec)+'</small>':'')
            +(i.link?'<br><a href="'+esc(i.link)+'" target="_blank">링크</a>':'')
            +'</div><span class="q">'+(i.qty||1)+'개</span></div>'; }).join('')+'</div>':'')
      +(q.note?'<div class="note">'+esc(q.note)+'</div>':'')
      +'</div>';
  }).join('');
}

load();
</script>
</body>
</html>`;
}
