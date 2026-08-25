// functions/admin/orders/index.js — 주문관리 (모바일 우선) · Basic Auth
// 폰에서 목록 확인 → 품목/단가 수정 → 상태 변경 → 이력 확인까지 한 화면에서.

const REALM = 'rndsetup-admin';

export async function onRequest({ request, env }) {
  const pw = env.ADMIN_PASSWORD || '';
  const auth = request.headers.get('Authorization') || '';
  let ok = false;
  if (pw && auth.startsWith('Basic ')) {
    try {
      const d = atob(auth.slice(6));
      const i = d.indexOf(':');
      ok = (i >= 0 ? d.slice(i + 1) : d) === pw;
    } catch { ok = false; }
  }
  if (!ok) {
    return new Response('인증이 필요합니다. (관리자)', {
      status: 401,
      headers: { 'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`, 'content-type': 'text/plain; charset=utf-8' },
    });
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
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0a2540">
<title>주문관리 — rndsetup</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#0a2540;--teal:#1a6e56;--ink:#1a2332;--mut:#5a6779;--line:#e3e8ef;--bg:#f4f6fa;--warn:#C2410C}
html,body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:var(--ink);background:var(--bg);line-height:1.5;-webkit-text-size-adjust:100%}
body{padding-bottom:env(safe-area-inset-bottom)}
button,input,select,textarea{font:inherit;color:inherit}
.top{position:sticky;top:0;z-index:20;background:var(--navy);color:#fff;padding:10px 14px calc(10px + env(safe-area-inset-top)) ;padding-top:calc(10px + env(safe-area-inset-top))}
.top h1{font-size:16px;font-weight:800;letter-spacing:-.2px;display:flex;align-items:center;gap:8px}
.top h1 a{color:#9fc3e8;text-decoration:none;font-size:12.5px;font-weight:600;margin-left:auto}
.chips{display:flex;gap:7px;overflow-x:auto;padding:9px 12px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:15;-webkit-overflow-scrolling:touch}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 13px;font-size:13px;font-weight:700;color:var(--mut);white-space:nowrap;cursor:pointer}
.chip.on{background:var(--navy);border-color:var(--navy);color:#fff}
.chip b{font-weight:800;margin-left:5px;opacity:.8}
.srch{padding:10px 12px;background:#fff;border-bottom:1px solid var(--line)}
.srch input{width:100%;border:1px solid var(--line);border-radius:10px;padding:11px 13px;font-size:15px;background:#fbfcfe}
.wrap{padding:12px 12px 90px}
.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:13px 14px;margin-bottom:9px;cursor:pointer}
.card:active{background:#fafbfd}
.card .r1{display:flex;align-items:center;gap:8px;margin-bottom:5px}
.no{font-size:12px;font-weight:800;color:var(--mut);font-variant-numeric:tabular-nums}
.st{margin-left:auto;font-size:11.5px;font-weight:800;padding:3px 9px;border-radius:999px;background:#eef2f7;color:var(--mut);white-space:nowrap}
.st.s0{background:#FEF3C7;color:#92400E}.st.s1{background:#DBEAFE;color:#1E40AF}.st.s2{background:#D1FAE5;color:#065F46}
.st.s3{background:#E0E7FF;color:#3730A3}.st.s4{background:#F3E8FF;color:#6B21A8}.st.s5{background:#CFFAFE;color:#155E75}
.st.s6{background:#DCFCE7;color:#166534}.st.s7{background:#F1F5F9;color:#475569}.st.s8{background:#FEE2E2;color:#991B1B}
.ttl{font-size:15px;font-weight:700;line-height:1.35;word-break:keep-all}
.sub{font-size:12.5px;color:var(--mut);margin-top:4px;display:flex;flex-wrap:wrap;gap:4px 10px}
.amt{margin-top:7px;font-size:15px;font-weight:800;color:var(--navy);font-variant-numeric:tabular-nums}
.empty{text-align:center;color:var(--mut);font-size:14px;padding:50px 20px}
.sheet{position:fixed;inset:0;z-index:40;background:rgba(10,37,64,.45);display:none}
.sheet.on{display:block}
.sbody{position:absolute;left:0;right:0;bottom:0;top:24px;background:var(--bg);border-radius:16px 16px 0 0;overflow-y:auto;-webkit-overflow-scrolling:touch}
.shead{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:13px 14px;display:flex;align-items:center;gap:10px;border-radius:16px 16px 0 0;z-index:5}
.shead .x{margin-left:auto;border:0;background:#eef2f7;border-radius:9px;width:34px;height:34px;font-size:19px;color:var(--mut);cursor:pointer}
.sec{background:#fff;border:1px solid var(--line);border-radius:13px;margin:11px 12px;padding:13px 14px}
.sec h3{font-size:12.5px;font-weight:800;color:var(--mut);letter-spacing:.3px;margin-bottom:10px}
.kv{display:flex;gap:10px;font-size:13.5px;padding:4px 0}
.kv span:first-child{color:var(--mut);flex:0 0 74px}
.kv span:last-child{flex:1;word-break:break-all}
.it{border:1px solid var(--line);border-radius:11px;padding:11px;margin-bottom:9px;background:#fbfcfe}
.it input{width:100%;border:1px solid var(--line);border-radius:8px;padding:9px 10px;font-size:15px;background:#fff;margin-bottom:6px}
.it .row{display:flex;gap:6px}
.it .row input{margin-bottom:0}
.it .qty{flex:0 0 68px;text-align:center}
.it .unit{flex:0 0 58px;text-align:center}
.it .price{flex:1;text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
.it .del{border:0;background:#fee2e2;color:#991B1B;border-radius:8px;padding:0 11px;font-size:13px;font-weight:700;cursor:pointer}
.it .amt2{text-align:right;font-size:12.5px;color:var(--mut);margin-top:6px;font-variant-numeric:tabular-nums}
.addbtn{width:100%;border:1px dashed #c3ccd8;background:#fff;border-radius:10px;padding:11px;font-size:13.5px;font-weight:700;color:var(--mut);cursor:pointer}
.sums{border-top:1px solid var(--line);margin-top:11px;padding-top:11px;font-size:14px}
.sums div{display:flex;justify-content:space-between;padding:3px 0;font-variant-numeric:tabular-nums}
.sums .tot{font-size:17px;font-weight:800;color:var(--navy);border-top:1px solid var(--line);margin-top:6px;padding-top:8px}
select,textarea{width:100%;border:1px solid var(--line);border-radius:9px;padding:11px;font-size:15px;background:#fff}
textarea{min-height:74px;resize:vertical}
.ev{font-size:12.5px;padding:8px 0;border-bottom:1px dashed var(--line);display:flex;gap:9px}
.ev:last-child{border-bottom:0}
.ev time{flex:0 0 92px;color:var(--mut);font-variant-numeric:tabular-nums}
.ev b{font-weight:700}
.bar{position:sticky;bottom:0;background:#fff;border-top:1px solid var(--line);padding:11px 12px calc(11px + env(safe-area-inset-bottom));display:flex;gap:8px}
.bar button{flex:1;border:0;border-radius:11px;padding:14px;font-size:15px;font-weight:800;cursor:pointer}
.bar .save{background:var(--teal);color:#fff}
.bar .save:disabled{opacity:.5}
.bar .doc{background:#eef2f7;color:var(--mut)}
.tag{display:inline-block;font-size:11px;font-weight:800;background:#FEF3C7;color:#92400E;border-radius:5px;padding:2px 6px;margin-left:6px}
.docrow{border:1px solid var(--line);border-radius:11px;padding:11px 12px;margin-bottom:8px;background:#fbfcfe}
.dr1{display:flex;align-items:center;gap:8px;font-size:14px}
.dr1 .dno{font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums}
.dr1 .dst{margin-left:auto;font-size:11.5px;font-weight:800;background:#DBEAFE;color:#1E40AF;border-radius:999px;padding:3px 9px}
.dr1 .dst.off{background:#FEE2E2;color:#991B1B}
.dr2{display:flex;gap:14px;margin-top:9px;font-size:13px}
.dr2 a,.lnk{color:var(--teal);font-weight:700;text-decoration:none;background:0;border:0;padding:0;cursor:pointer;font-size:13px}
.qrow{font-size:12.5px;color:#92400E;background:#FEF3C7;border-radius:9px;padding:8px 11px;margin-bottom:8px}
.mkbtns{display:flex;gap:8px;margin-top:4px}
.mkbtns .mk{flex:1;border:1px dashed #c3ccd8;background:#fff;border-radius:10px;padding:11px 6px;font-size:13px;font-weight:700;color:var(--mut);cursor:pointer}
.modal{position:fixed;inset:0;z-index:70;background:rgba(10,37,64,.5);display:flex;align-items:flex-end;justify-content:center}
.mbox{background:#fff;width:100%;max-width:520px;border-radius:16px 16px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom))}
.mbox h4{font-size:16px;font-weight:800;margin-bottom:12px}
.mbox label{display:block;font-size:12px;font-weight:700;color:var(--mut);margin:11px 0 5px}
.mbox input{width:100%;border:1px solid var(--line);border-radius:10px;padding:12px;font-size:15px;background:#fbfcfe}
.mrow{display:flex;gap:8px;margin-top:16px}
.mrow button{flex:1;border:0;border-radius:11px;padding:14px;font-size:15px;font-weight:800;cursor:pointer}
.mrow .mghost{background:#eef2f7;color:var(--mut)}
.mrow .mgo{background:var(--teal);color:#fff}
.mhint{font-size:12px;color:var(--mut);margin-top:10px;text-align:center}
@media(min-width:820px){.modal{align-items:center}.mbox{border-radius:16px}}
.toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:#0a2540;color:#fff;padding:11px 19px;border-radius:11px;font-size:14px;font-weight:700;z-index:60;opacity:0;transition:opacity .2s;pointer-events:none}
.toast.on{opacity:.95}
@media(min-width:820px){.wrap{max-width:900px;margin:0 auto}.sbody{left:50%;transform:translateX(-50%);max-width:720px;border-radius:16px;top:40px;bottom:40px}}
</style>
</head>
<body>
<div class="top"><h1>주문관리<a href="/admin">제품관리 →</a></h1></div>
<div class="chips" id="chips"></div>
<div class="srch"><input id="q" type="search" placeholder="주문번호 · 거래처 · 품명 검색" autocomplete="off"></div>
<div class="wrap" id="list"><div class="empty">불러오는 중…</div></div>

<div class="sheet" id="sheet"><div class="sbody" id="sbody"></div></div>
<div class="toast" id="toast"></div>

<script>
const TOKEN = ${JSON.stringify(token)};
const H = { 'Authorization': 'Basic ' + TOKEN, 'content-type': 'application/json' };
const STATUSES = ['요청접수','견적발송','견적승인','발주확정','납품완료','계산서발행','완료','보류','취소'];
const SIDX = {}; STATUSES.forEach((s,i)=>SIDX[s]=i);
let filter = '전체', kw = '', cur = null, items = [];

const won = n => Number(n||0).toLocaleString('ko-KR');
const esc = s => String(s==null?'':s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(m){ const t=document.getElementById('toast'); t.textContent=m; t.classList.add('on'); setTimeout(()=>t.classList.remove('on'),1800); }

async function loadChips(){
  const r = await fetch('/api/admin/orders?stats=1',{headers:H}).then(r=>r.json());
  const el = document.getElementById('chips');
  const all = [['전체', r.total]].concat(STATUSES.map(s=>[s, r.byStatus[s]||0]));
  el.innerHTML = all.map(([s,c])=>'<button class="chip'+(s===filter?' on':'')+'" data-s="'+esc(s)+'">'+esc(s)+'<b>'+c+'</b></button>').join('');
  el.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{ filter=b.dataset.s; loadChips(); loadList(); });
}

async function loadList(){
  const u = new URL('/api/admin/orders', location.origin);
  if (filter!=='전체') u.searchParams.set('status', filter);
  if (kw) u.searchParams.set('q', kw);
  const r = await fetch(u,{headers:H}).then(r=>r.json());
  const el = document.getElementById('list');
  if (!r.orders || !r.orders.length){ el.innerHTML='<div class="empty">해당 주문이 없습니다.</div>'; return; }
  el.innerHTML = r.orders.map(o=>
    '<div class="card" data-id="'+o.id+'">'
    +'<div class="r1"><span class="no">'+esc(o.order_no)+'</span><span class="st s'+(SIDX[o.status]??7)+'">'+esc(o.status)+'</span></div>'
    +'<div class="ttl">'+esc(o.title||'(제목 없음)')+'</div>'
    +'<div class="sub"><span>'+esc(o.company||o.contact||'-')+'</span>'
      +(o.want_date?'<span>납기 '+esc(o.want_date)+'</span>':'')
      +'<span>'+esc(String(o.created_at||'').slice(0,10))+'</span></div>'
    +'<div class="amt">'+won(o.total_amount)+'원</div></div>').join('');
  el.querySelectorAll('.card').forEach(c=>c.onclick=()=>openOrder(c.dataset.id));
}

async function openOrder(id){
  const d = await fetch('/api/admin/orders/'+id,{headers:H}).then(r=>r.json());
  cur = d; items = (d.items||[]).map(i=>({...i}));
  document.getElementById('sheet').classList.add('on');
  document.body.style.overflow='hidden';
  render();
}
function closeSheet(){ document.getElementById('sheet').classList.remove('on'); document.body.style.overflow=''; cur=null; }

function render(){
  const o = cur.order, c = cur.customer||{};
  const body = document.getElementById('sbody');
  body.innerHTML =
   '<div class="shead"><span class="no">'+esc(o.order_no)+'</span><span class="st s'+(SIDX[o.status]??7)+'">'+esc(o.status)+'</span><button class="x" id="closeBtn">×</button></div>'
  +'<div class="sec"><h3>거래처</h3>'
    +kv('상호', c.company)+kv('담당자',(c.name||'')+(c.phone?' · '+c.phone:''))+kv('사업자',c.biz_no)
    +kv('이메일',c.email)+kv('계산서',c.tax_email||c.email)+kv('납품지',o.ship_address)
  +'</div>'
  +'<div class="sec"><h3>요청내용</h3>'
    +kv('제목',o.title)+kv('희망납기',o.want_date)+kv('요청사항',o.request_note)
  +'</div>'
  +'<div class="sec"><h3>품목 · 단가</h3><div id="itemBox"></div>'
    +'<button class="addbtn" id="addItem">+ 품목 추가</button>'
    +'<div class="sums" id="sums"></div></div>'
  +'<div class="sec"><h3>상태</h3><select id="st">'+STATUSES.map(s=>'<option'+(s===o.status?' selected':'')+'>'+s+'</option>').join('')+'</select></div>'
  +'<div class="sec"><h3>내부 메모</h3><textarea id="memo" placeholder="고객에게 안 보입니다">'+esc(o.admin_memo||'')+'</textarea></div>'
  +'<div class="sec"><h3>문서</h3><div id="docBox">'+docBlock()+'</div></div>'
  +'<div class="sec"><h3>이력</h3>'+(cur.events||[]).map(e=>
      '<div class="ev"><time>'+esc(String(e.created_at||'').slice(5,16))+'</time><div><b>'+esc(e.action)+'</b> · '+esc(e.actor)+(e.detail?'<br>'+esc(e.detail):'')+'</div></div>').join('')
    +((cur.events||[]).length?'':'<div style="font-size:13px;color:var(--mut)">기록 없음</div>')
  +'</div>'
  +'<div class="bar"><button class="save" id="saveBtn">저장</button></div>';

  document.getElementById('closeBtn').onclick = closeSheet;
  document.getElementById('addItem').onclick = ()=>{ items.push({name:'',spec:'',unit:'EA',qty:1,unit_price:0}); renderItems(); };
  document.getElementById('saveBtn').onclick = save;
  bindDocs();
  renderItems();
}
function kv(k,v){ return '<div class="kv"><span>'+esc(k)+'</span><span>'+esc(v||'-')+'</span></div>'; }
const DT={quote:'견적서',statement:'거래명세서',taxinvoice:'세금계산서'};
function docBlock(){
  const d = cur.documents||[];
  const q = cur.queued||[];
  let h = '';
  if(!d.length) h += '<div style="font-size:13px;color:var(--mut);margin-bottom:10px">아직 발행된 문서가 없습니다.</div>';
  else h += d.map(function(x){
    return '<div class="docrow" data-id="'+x.id+'">'
      +'<div class="dr1"><b>'+esc(DT[x.type]||x.type)+'</b><span class="dno">'+esc(x.doc_no||'')+'</span>'
        +'<span class="dst'+(x.status==='취소됨'?' off':'')+'">'+esc(x.status)+'</span></div>'
      +'<div class="dr2">'
        +'<a href="/doc/'+x.id+'" target="_blank">미리보기</a>'
        +'<a href="/doc/'+x.id+'?f=pdf" target="_blank">PDF</a>'
        +(x.status==='취소됨'?'':'<button class="lnk send" data-id="'+x.id+'">이메일 발송</button>')
      +'</div></div>';
  }).join('');
  if(q.length) h += q.map(function(j){
    return '<div class="qrow">예약 '+esc(String(j.send_at).slice(0,16))+' → '+esc(j.to_addr)
      +' <button class="lnk qcancel" data-id="'+j.document_id+'">취소</button></div>';
  }).join('');
  h += '<div class="mkbtns"><button class="mk" data-t="quote">＋ 견적서 발행</button>'
     + '<button class="mk" data-t="statement">＋ 거래명세서 발행</button></div>';
  return h;
}

function bindDocs(){
  const box = document.getElementById('docBox');
  if(!box) return;
  box.querySelectorAll('.mk').forEach(function(b){ b.onclick=function(){ makeDoc(b.dataset.t); }; });
  box.querySelectorAll('.send').forEach(function(b){ b.onclick=function(){ sendSheet(b.dataset.id); }; });
  box.querySelectorAll('.qcancel').forEach(function(b){ b.onclick=function(){ cancelSchedule(b.dataset.id); }; });
}

async function makeDoc(type){
  toast(DT[type]+' 만드는 중…');
  const r = await fetch('/api/admin/docs',{method:'POST',headers:H,
    body:JSON.stringify({order_id:cur.order.id,type:type})}).then(function(r){return r.json();});
  if(r.ok){ toast(r.doc_no+' 생성됨'); await openOrder(cur.order.id); loadChips(); loadList(); }
  else toast('실패: '+(r.message||r.error||''));
}

async function cancelSchedule(docId){
  if(!confirm('예약 발송을 취소할까요?')) return;
  const r = await fetch('/api/admin/docs/'+docId,{method:'POST',headers:H,
    body:JSON.stringify({action:'cancel'})}).then(function(r){return r.json();});
  if(r.ok){ toast('예약 취소됨'); openOrder(cur.order.id); }
}

function sendSheet(docId){
  const c = cur.customer||{};
  const to = c.tax_email || c.email || '';
  const wrap = document.createElement('div');
  wrap.className='modal'; wrap.id='sendModal';
  wrap.innerHTML = '<div class="mbox">'
    +'<h4>이메일 발송</h4>'
    +'<label>받는 사람</label><input id="m-to" value="'+esc(to)+'" inputmode="email">'
    +'<label>참조 (선택)</label><input id="m-cc" placeholder="cc@example.com" inputmode="email">'
    +'<label>제목 (비워두면 기본 제목)</label><input id="m-sub" placeholder="[실험셋업연구소] 견적서 …">'
    +'<label>예약 발송 (비워두면 즉시)</label><input id="m-at" type="datetime-local">'
    +'<div class="mrow"><button class="mghost" id="m-x">닫기</button><button class="mgo" id="m-go">보내기</button></div>'
    +'<p class="mhint">PDF가 자동 첨부되고, 발송·열람 이력이 기록됩니다.</p>'
    +'</div>';
  document.body.appendChild(wrap);
  document.getElementById('m-x').onclick=function(){ wrap.remove(); };
  wrap.onclick=function(e){ if(e.target===wrap) wrap.remove(); };
  document.getElementById('m-go').onclick=async function(){
    const btn=document.getElementById('m-go'); btn.disabled=true; btn.textContent='처리 중…';
    const at=document.getElementById('m-at').value;
    const body={action:'send',to:document.getElementById('m-to').value.trim(),
      cc:document.getElementById('m-cc').value.trim()||undefined,
      subject:document.getElementById('m-sub').value.trim()||undefined};
    if(at) body.send_at = at.replace('T',' ')+':00';
    const r = await fetch('/api/admin/docs/'+docId,{method:'POST',headers:H,body:JSON.stringify(body)})
      .then(function(r){return r.json();});
    btn.disabled=false; btn.textContent='보내기';
    if(r.ok){ wrap.remove(); toast(r.scheduled? '예약 완료':'발송 완료'); await openOrder(cur.order.id); loadChips(); loadList(); }
    else toast('실패: '+(r.message||r.error||''));
  };
}
function renderItems(){
  const box = document.getElementById('itemBox');
  box.innerHTML = items.map((it,i)=>
    '<div class="it" data-i="'+i+'">'
    +'<input class="f-name" placeholder="품명" value="'+esc(it.name)+'">'
    +'<input class="f-spec" placeholder="규격 / 모델" value="'+esc(it.spec||'')+'">'
    +'<div class="row"><input class="unit f-unit" value="'+esc(it.unit||'EA')+'">'
      +'<input class="qty f-qty" type="number" inputmode="decimal" value="'+(it.qty||0)+'">'
      +'<input class="price f-price" type="number" inputmode="numeric" value="'+(it.unit_price||0)+'">'
      +'<button class="del">삭제</button></div>'
    +'<div class="amt2">'+won(Math.round((it.qty||0)*(it.unit_price||0)))+'원</div></div>').join('');
  box.querySelectorAll('.it').forEach(el=>{
    const i = +el.dataset.i;
    el.querySelector('.f-name').oninput = e=>items[i].name=e.target.value;
    el.querySelector('.f-spec').oninput = e=>items[i].spec=e.target.value;
    el.querySelector('.f-unit').oninput = e=>items[i].unit=e.target.value;
    el.querySelector('.f-qty').oninput  = e=>{ items[i].qty=+e.target.value; sums(); el.querySelector('.amt2').textContent=won(Math.round(items[i].qty*items[i].unit_price))+'원'; };
    el.querySelector('.f-price').oninput= e=>{ items[i].unit_price=+e.target.value; sums(); el.querySelector('.amt2').textContent=won(Math.round(items[i].qty*items[i].unit_price))+'원'; };
    el.querySelector('.del').onclick = ()=>{ items.splice(i,1); renderItems(); };
  });
  sums();
}
function sums(){
  const s = items.reduce((a,i)=>a+Math.round((i.qty||0)*(i.unit_price||0)),0);
  const v = Math.round(s*0.1);
  document.getElementById('sums').innerHTML =
    '<div><span>공급가액</span><span>'+won(s)+'원</span></div>'
   +'<div><span>부가세</span><span>'+won(v)+'원</span></div>'
   +'<div class="tot"><span>합계</span><span>'+won(s+v)+'원</span></div>';
}
async function save(){
  const btn = document.getElementById('saveBtn'); btn.disabled=true; btn.textContent='저장 중…';
  const payload = { items, status: document.getElementById('st').value, admin_memo: document.getElementById('memo').value };
  const r = await fetch('/api/admin/orders/'+cur.order.id, { method:'PUT', headers:H, body: JSON.stringify(payload) }).then(r=>r.json());
  btn.disabled=false; btn.textContent='저장';
  if (r.ok){ toast('저장했습니다'); await openOrder(cur.order.id); loadChips(); loadList(); }
  else toast('저장 실패: '+(r.message||r.error||''));
}

let t; document.getElementById('q').oninput = e=>{ clearTimeout(t); t=setTimeout(()=>{ kw=e.target.value.trim(); loadList(); },300); };
document.getElementById('sheet').onclick = e=>{ if(e.target.id==='sheet') closeSheet(); };
loadChips(); loadList();
fetch('/api/cron/outbox',{headers:H}).then(function(r){return r.json();})
  .then(function(r){ if(r && r.sent) toast('예약 발송 '+r.sent+'건 처리됨'); }).catch(function(){});
</` + `script>
</body>
</html>`;
}
