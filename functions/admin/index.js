// functions/admin/index.js — 관리자 페이지 (/admin) · Basic Auth
//   · 본 사이트 헤더/사이드바 공유(site.css + site.js + #pumplab-header) → admin↔사이트 왕복
//   · 상태별 개수 대시보드 · 브랜드/상태/소분류/검색 필터
//   · 표에서 공급가·소비자가·이미지URL·상태 인라인 수정 → PUT /api/admin/products
//   · "사이트 반영" 버튼 → POST /api/admin/publish (삼흥 데이터시트 발행)
// 비밀번호는 코드에 없음: Cloudflare 환경변수 ADMIN_PASSWORD 사용.

const REALM = 'rndsetup-admin';

export async function onRequest(context) {
  const { request, env } = context;
  const auth = request.headers.get('Authorization') || '';
  if (!checkAuth(auth, env)) {
    return new Response('인증이 필요합니다. (관리자)', {
      status: 401,
      headers: { 'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`, 'content-type': 'text/plain; charset=utf-8' },
    });
  }
  return new Response(renderHTML(auth.slice(6)), {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' },
  });
}

function checkAuth(auth, env) {
  const pw = env.ADMIN_PASSWORD || '';
  if (!pw) return false;
  if (!auth.startsWith('Basic ')) return false;
  let d = ''; try { d = atob(auth.slice(6)); } catch { return false; }
  const i = d.indexOf(':');
  return (i >= 0 ? d.slice(i + 1) : d) === pw;
}

function renderHTML(token) {
  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>rndsetup 관리자</title>
<link rel="stylesheet" href="/assets/site.css">
<style>
  .adm-main{ padding:22px 26px 80px; }
  .adm-main *{ box-sizing:border-box; }
  .adm-bar{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom:6px; }
  .adm-title{ font-family:var(--serif,Georgia); font-size:22px; font-weight:700; color:var(--ink,#1a1a1a); }
  .adm-actions{ margin-left:auto; display:flex; align-items:center; gap:10px; }
  .adm-link{ font-size:13.5px; font-weight:700; text-decoration:none; color:var(--ink,#1a1a1a); border:1px solid var(--line,#e5e5e5); padding:9px 13px; border-radius:9px; }
  .adm-link:hover{ border-color:#c3ccd8; }
  .adm-publish{ font-size:14px; font-weight:800; color:#fff; background:#C2410C; border:0; padding:10px 18px; border-radius:9px; cursor:pointer; }
  .adm-publish:hover{ background:#9A3412; }
  .adm-publish:disabled{ opacity:.55; cursor:default; }
  .adm-pubinfo{ font-size:12.5px; color:#6B6B6B; margin:2px 2px 16px; }
  .adm-pubinfo b{ color:#9A3412; }
  .adm-pubinfo .dirty{ color:#C2410C; font-weight:700; }

  .adm-cards{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin-bottom:18px; }
  .adm-card{ background:#fff; border:1px solid var(--line,#e5e5e5); border-radius:12px; padding:15px 16px; cursor:pointer; }
  .adm-card:hover{ border-color:#c3ccd8; }
  .adm-card.on{ border-color:#1A6E56; box-shadow:0 0 0 2px rgba(26,110,86,.14); }
  .adm-card .n{ font-size:25px; font-weight:800; }
  .adm-card .l{ font-size:12.5px; color:#6B6B6B; margin-top:2px; }
  .adm-card.total .n{ color:#1E3A5F; } .adm-card.ok .n{ color:#1A6E56; }
  .adm-card.price .n{ color:#c47f16; } .adm-card.img .n{ color:#b4453a; }

  .adm-filters{ background:#fff; border:1px solid var(--line,#e5e5e5); border-radius:12px; padding:13px 15px; display:flex; flex-wrap:wrap; gap:9px; align-items:center; margin-bottom:14px; }
  .adm-filters select, .adm-filters input{ height:36px; border:1px solid var(--line,#e5e5e5); border-radius:8px; padding:0 10px; font-size:13.5px; background:#fff; font-family:inherit; }
  .adm-filters input[type=text]{ min-width:200px; }
  .adm-filters button{ height:36px; padding:0 15px; border-radius:8px; border:0; font-size:13.5px; font-weight:700; cursor:pointer; }
  .adm-go{ background:#1A6E56; color:#fff; } .adm-reset{ background:#eef1f5; color:#1a1a1a; }
  .adm-filters .sp{ flex:1; } .adm-hint{ font-size:12px; color:#6B6B6B; }

  .adm-tablewrap{ background:#fff; border:1px solid var(--line,#e5e5e5); border-radius:12px; overflow:auto; }
  .adm-main table{ border-collapse:collapse; width:100%; font-size:13px; }
  .adm-main th, .adm-main td{ padding:8px 10px; border-bottom:1px solid #eef1f5; text-align:left; vertical-align:middle; white-space:nowrap; }
  .adm-main th{ background:#fafbfc; font-weight:700; color:#6B6B6B; position:sticky; top:0; z-index:1; font-size:12px; }
  .adm-main tr.dirty td{ background:#fffbe9; }
  .adm-main td .nm{ white-space:normal; min-width:210px; max-width:320px; display:inline-block; line-height:1.35; }
  .adm-main td.sku{ font-family:ui-monospace,monospace; font-size:12px; color:#6B6B6B; }
  .adm-thumb{ width:44px; height:44px; object-fit:contain; border:1px solid var(--line,#e5e5e5); border-radius:6px; background:#fff; }
  .adm-thumb.none{ display:flex; align-items:center; justify-content:center; font-size:10px; color:#b4453a; }
  .adm-main input.p{ width:100px; height:32px; border:1px solid var(--line,#e5e5e5); border-radius:6px; padding:0 8px; font-size:13px; text-align:right; }
  .adm-main input.url{ width:200px; height:32px; border:1px solid var(--line,#e5e5e5); border-radius:6px; padding:0 8px; font-size:12px; }
  .adm-main select.st{ height:32px; border:1px solid var(--line,#e5e5e5); border-radius:6px; padding:0 6px; font-size:13px; }
  .adm-save{ height:32px; padding:0 12px; border-radius:6px; border:0; background:#1A6E56; color:#fff; font-weight:700; font-size:12.5px; cursor:pointer; }
  .adm-save:disabled{ opacity:.4; cursor:default; }

  .adm-pager{ display:flex; justify-content:center; gap:6px; margin:18px 0 4px; flex-wrap:wrap; }
  .adm-pager button{ min-width:34px; height:34px; padding:0 10px; border:1px solid var(--line,#e5e5e5); background:#fff; border-radius:8px; font-size:13px; font-weight:700; cursor:pointer; }
  .adm-pager button.on{ background:#1A6E56; color:#fff; border-color:#1A6E56; }
  .adm-pager button:disabled{ opacity:.4; cursor:default; }
  .adm-meta{ font-size:12.5px; color:#6B6B6B; margin:10px 2px; }

  #toast{ position:fixed; left:50%; bottom:26px; transform:translateX(-50%); background:#1a2430; color:#fff; padding:11px 20px; border-radius:9px; font-size:14px; opacity:0; pointer-events:none; transition:opacity .2s; z-index:200; }
  #toast.on{ opacity:1; } #toast.err{ background:#b4453a; }
</style>
</head>
<body>
<div id="pumplab-header"></div>

<main class="adm-main">
  <div class="adm-bar">
    <div class="adm-title">제품 관리자</div>
    <div class="adm-actions">
      <a class="adm-link" href="/brands/sh-scientific/" target="_blank" rel="noopener">삼흥 퍼니스 페이지 ↗</a>
      <button class="adm-publish" id="btnPublish">사이트 반영</button>
    </div>
  </div>
  <div class="adm-pubinfo" id="pubinfo">발행 상태 확인 중…</div>

  <div class="adm-cards" id="cards"></div>

  <div class="adm-filters">
    <select id="f-brand">
      <option value="">전체 브랜드</option>
      <option>SH Scientific</option><option>Leadfluid</option><option>RUNZE</option><option>Alicat</option>
    </select>
    <select id="f-status">
      <option value="">전체 상태</option>
      <option>등록가능</option><option>가격대기</option><option>이미지대기</option>
    </select>
    <input type="text" id="f-sobun" placeholder="소분류(정확히 일치)">
    <input type="text" id="f-q" placeholder="상품명 / 모델 / SKU 검색">
    <button class="adm-go" id="btn-go">검색</button>
    <button class="adm-reset" id="btn-reset">초기화</button>
    <span class="sp"></span>
    <span class="adm-hint" id="count-hint"></span>
  </div>

  <div class="adm-meta" id="meta"></div>

  <div class="adm-tablewrap">
    <table>
      <thead><tr>
        <th>ID</th><th>브랜드</th><th>소분류</th><th>모델</th><th>상품명</th>
        <th>이미지</th><th>이미지 URL</th><th>공급가</th><th>소비자가</th><th>상태</th><th></th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>

  <div class="adm-pager" id="pager"></div>
</main>

<div id="toast"></div>

<script src="/assets/site.js" defer></script>
<script>try{localStorage.setItem('rnd_admin','1');}catch(e){}</script>
<script>
const AUTH = "Basic ${token}";
const SIZE = 50;
const state = { page:1, total:0 };
const el = (id)=>document.getElementById(id);
function esc(s){ return (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function toast(m,e){ const t=el('toast'); t.textContent=m; t.className='on'+(e?' err':''); setTimeout(()=>t.className='',2400); }
async function api(path, opts){
  const o = Object.assign({ headers:{} }, opts||{});
  o.headers['Authorization'] = AUTH;
  if (o.body) o.headers['content-type'] = 'application/json';
  const r = await fetch(path, o);
  if (!r.ok){ let m=''; try{ m=(await r.json()).error||''; }catch{} throw new Error(m||('HTTP '+r.status)); }
  return r.json();
}

// ---- 발행(사이트 반영) ----
async function loadPubInfo(){
  try{
    const d = await api('/api/admin/publish');
    const p = d.published;
    el('pubinfo').innerHTML = p
      ? '마지막 사이트 반영: <b>'+fmt(p.updated_at)+'</b> · '+p.count+'종 발행됨. <span class="dirty">가격·상태를 바꾼 뒤에는 [사이트 반영]을 눌러야 사이트에 나타납니다.</span>'
      : '<span class="dirty">아직 사이트에 반영된 적이 없습니다. [사이트 반영]을 누르면 삼흥 데이터시트가 사이트에 게시됩니다.</span>';
  }catch(e){ el('pubinfo').textContent = '발행 상태를 불러오지 못했습니다: '+e.message; }
}
function fmt(iso){ try{ return new Date(iso).toLocaleString('ko-KR',{timeZone:'Asia/Seoul'}); }catch{ return iso; } }
async function publish(){
  const b = el('btnPublish'); const t=b.textContent;
  if(!confirm('현재 등록가능한 삼흥 퍼니스를 사이트(/brands/sh-scientific/)에 반영합니다. 진행할까요?')) return;
  b.disabled=true; b.textContent='반영 중…';
  try{
    const d = await api('/api/admin/publish', { method:'POST' });
    toast('사이트 반영 완료 · '+d.count+'종');
    loadPubInfo();
  }catch(e){ toast('반영 실패: '+e.message, true); }
  finally{ b.disabled=false; b.textContent=t; }
}

// ---- 대시보드 ----
async function loadStats(){
  try{
    const s = await api('/api/admin/products?stats=1');
    const by = s.byStatus||{};
    const defs = [
      { k:'', l:'전체', n:s.total||0, cls:'total' },
      { k:'등록가능', l:'등록가능', n:by['등록가능']||0, cls:'ok' },
      { k:'가격대기', l:'가격대기', n:by['가격대기']||0, cls:'price' },
      { k:'이미지대기', l:'이미지대기', n:by['이미지대기']||0, cls:'img' },
    ];
    el('cards').innerHTML = defs.map(d=>'<div class="adm-card '+d.cls+'" data-status="'+d.k+'"><div class="n">'+d.n.toLocaleString()+'</div><div class="l">'+d.l+'</div></div>').join('');
    document.querySelectorAll('.adm-card').forEach(c=>c.addEventListener('click',()=>{ el('f-status').value=c.dataset.status; state.page=1; load(); }));
  }catch(e){ toast('통계 로드 실패: '+e.message, true); }
}
function markCard(){ const cur=el('f-status').value; document.querySelectorAll('.adm-card').forEach(c=>c.classList.toggle('on', c.dataset.status===cur)); }

// ---- 목록 ----
async function load(){
  markCard();
  const p = new URLSearchParams();
  if (el('f-brand').value)  p.set('brand', el('f-brand').value);
  if (el('f-status').value) p.set('status', el('f-status').value);
  if (el('f-sobun').value.trim()) p.set('sobun', el('f-sobun').value.trim());
  if (el('f-q').value.trim())     p.set('q', el('f-q').value.trim());
  p.set('page', state.page); p.set('size', SIZE);
  el('tbody').innerHTML = '<tr><td colspan="11" style="padding:24px;text-align:center;color:#6B6B6B">불러오는 중…</td></tr>';
  try{
    const d = await api('/api/admin/products?'+p.toString());
    state.total = d.total;
    el('count-hint').textContent = '총 '+d.total.toLocaleString()+'건';
    el('meta').textContent = '페이지 '+d.page+' · '+d.count+'건 표시';
    renderRows(d.items); renderPager();
  }catch(e){ el('tbody').innerHTML = '<tr><td colspan="11" style="padding:24px;text-align:center;color:#b4453a">로드 실패: '+esc(e.message)+'</td></tr>'; }
}
function renderRows(items){
  if(!items.length){ el('tbody').innerHTML='<tr><td colspan="11" style="padding:24px;text-align:center;color:#6B6B6B">결과 없음</td></tr>'; return; }
  el('tbody').innerHTML = items.map(it=>{
    const img = it.image_url ? '<img class="adm-thumb" src="'+esc(it.image_url)+'" onerror="this.style.display=\\'none\\'">' : '<div class="adm-thumb none">없음</div>';
    const opt = ['등록가능','가격대기','이미지대기'].map(s=>'<option'+(it.status===s?' selected':'')+'>'+s+'</option>').join('');
    return '<tr data-id="'+esc(it.id)+'">'
      + '<td class="sku">'+esc(it.id)+'</td><td>'+esc(it.brand)+'</td><td>'+esc(it.sobun)+'</td><td>'+esc(it.model)+'</td>'
      + '<td><span class="nm">'+esc(it.name)+'</span></td>'
      + '<td>'+img+'</td>'
      + '<td><input class="url" data-f="image_url" value="'+esc(it.image_url)+'" placeholder="https://…"></td>'
      + '<td><input class="p" data-f="supply_price" value="'+esc(it.supply_price)+'"></td>'
      + '<td><input class="p" data-f="retail_price" value="'+esc(it.retail_price)+'"></td>'
      + '<td><select class="st" data-f="status">'+opt+'</select></td>'
      + '<td><button class="adm-save" disabled>저장</button></td></tr>';
  }).join('');
  el('tbody').querySelectorAll('tr[data-id]').forEach(tr=>{
    const btn = tr.querySelector('.adm-save');
    tr.querySelectorAll('[data-f]').forEach(inp=>{
      const mark=()=>{ tr.classList.add('dirty'); btn.disabled=false; };
      inp.addEventListener('input', mark); inp.addEventListener('change', mark);
    });
    btn.addEventListener('click', ()=>saveRow(tr, btn));
  });
}
async function saveRow(tr, btn){
  const payload = { id: tr.dataset.id };
  tr.querySelectorAll('[data-f]').forEach(inp=>{ payload[inp.dataset.f] = inp.value; });
  btn.disabled=true; btn.textContent='저장중…';
  try{
    const r = await api('/api/admin/products', { method:'PUT', body: JSON.stringify(payload) });
    tr.classList.remove('dirty'); btn.textContent='저장';
    const cell = tr.children[5], url = payload.image_url;
    cell.innerHTML = url ? '<img class="adm-thumb" src="'+esc(url)+'" onerror="this.style.display=\\'none\\'">' : '<div class="adm-thumb none">없음</div>';
    toast('저장됨 · '+(r.item? r.item.model : tr.dataset.id));
    loadStats();
  }catch(e){ btn.disabled=false; btn.textContent='저장'; toast('저장 실패: '+e.message, true); }
}
function renderPager(){
  const pages = Math.max(1, Math.ceil(state.total/SIZE)), cur = state.page;
  if(pages<=1){ el('pager').innerHTML=''; return; }
  let start=Math.max(1,cur-4), end=Math.min(pages,start+9); start=Math.max(1,end-9);
  let h = '<button '+(cur<=1?'disabled':'')+' data-p="'+(cur-1)+'">‹</button>';
  if(start>1) h+='<button data-p="1">1</button><span style="align-self:center">…</span>';
  for(let i=start;i<=end;i++) h+='<button class="'+(i===cur?'on':'')+'" data-p="'+i+'">'+i+'</button>';
  if(end<pages) h+='<span style="align-self:center">…</span><button data-p="'+pages+'">'+pages+'</button>';
  h += '<button '+(cur>=pages?'disabled':'')+' data-p="'+(cur+1)+'">›</button>';
  el('pager').innerHTML=h;
  el('pager').querySelectorAll('button[data-p]').forEach(b=>b.addEventListener('click',()=>{ state.page=parseInt(b.dataset.p,10); load(); window.scrollTo(0,0); }));
}

el('btnPublish').addEventListener('click', publish);
el('btn-go').addEventListener('click', ()=>{ state.page=1; load(); });
el('btn-reset').addEventListener('click', ()=>{ el('f-brand').value=''; el('f-status').value=''; el('f-sobun').value=''; el('f-q').value=''; state.page=1; load(); });
el('f-q').addEventListener('keydown', e=>{ if(e.key==='Enter'){ state.page=1; load(); } });
el('f-sobun').addEventListener('keydown', e=>{ if(e.key==='Enter'){ state.page=1; load(); } });

loadPubInfo(); loadStats(); load();
</script>
</body>
</html>`;
}
