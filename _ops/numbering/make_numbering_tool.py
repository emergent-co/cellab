#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""부위 넘버링 입력기(HTML) 생성 — 사람이 사진을 클릭해 번호를 찍는 도구.

왜 필요한가: 마커 좌표를 모델이 눈대중으로 찍으면 자주 틀린다. 그렇다고 사람에게
격자 이미지를 주고 x·y 를 손으로 읽게 하면 사진 80장 × 번호 5~8개를 감당할 수 없다.
그래서 "무엇을 찍을지"는 카탈로그를 읽은 쪽(모델)이 정하고, "어디에 찍을지"만
사람이 클릭으로 입력하게 나눈다.

사용:
  python make_numbering_tool.py spec.json -o 넘버링_입력기.html

spec.json:
{
  "_batch": "1차 — ...",
  "models": {"C001": {"title": "...", "items": [{"n":1,"kind":"b","label":"..."}]}},
  "images": {"c001-1": "C001", "c001-2": "C001"}
}
kind = b 본체 구성 / d 이 형식만 / o 주문 시 옵션 / x 미포함·별매

결과 JSON:
{"markers": {"c001-1": [{n,x,y,kind,label}]}, "notes": {"c001-1": {"none":[6], "memo":""}}}
→ markers 부분만 떼어 draw_markers.py render 에 넣으면 된다.
"""
import argparse, json, io, os

HTML = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>부위 넘버링 입력기 — __BATCH__</title>
<style>
:root{--b:#1E3A5F;--d:#0D6E6E;--o:#646469;--x:#B22222;--line:#e3e1dd;--ink:#1c1917}
*{box-sizing:border-box}
body{margin:0;font:14px/1.55 "Malgun Gothic","맑은 고딕",system-ui,sans-serif;color:var(--ink);background:#f6f5f3}
header{background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;position:sticky;top:0;z-index:20}
header h1{font-size:15px;margin:0 12px 0 0;white-space:nowrap}
.btn{border:1px solid var(--line);background:#fff;border-radius:6px;padding:6px 12px;font:inherit;cursor:pointer}
.btn:hover{background:#f0efec}
.btn.pri{background:var(--b);color:#fff;border-color:var(--b)}
.prog{flex:1;min-width:140px;height:8px;background:#e8e6e2;border-radius:4px;overflow:hidden}
.prog i{display:block;height:100%;background:#2f7d5f;width:0}
main{display:grid;grid-template-columns:1fr 380px;gap:14px;padding:14px;align-items:start}
@media(max-width:1000px){main{grid-template-columns:1fr}}
.stage{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px}
.imgwrap{position:relative;display:inline-block;max-width:100%;line-height:0;cursor:crosshair;user-select:none}
.imgwrap img{max-width:100%;height:auto;display:block}
.mk{position:absolute;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;
    color:#fff;font-weight:700;font-size:19px;display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 0 3px #fff;cursor:grab;line-height:1}
.mk.sel{outline:3px solid #f0a500;outline-offset:3px}
.side{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;position:sticky;top:64px;max-height:calc(100vh - 80px);overflow:auto}
.mt{font-size:15px;font-weight:700;margin:0 0 2px}
.mf{color:#78716c;font-size:12px;margin:0 0 10px}
ul.items{list-style:none;margin:0;padding:0}
ul.items li{display:flex;gap:8px;align-items:flex-start;padding:7px 6px;border-radius:7px;cursor:pointer;border:1px solid transparent}
ul.items li:hover{background:#f6f5f3}
ul.items li.cur{background:#fff8e8;border-color:#f0a500}
ul.items li.done{opacity:.62}
ul.items li.none{opacity:.5;text-decoration:line-through}
.bdg{flex:none;width:24px;height:24px;border-radius:50%;color:#fff;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center}
.lb{flex:1}
.kd{display:block;font-size:11px;color:#78716c}
.acts{flex:none;display:flex;gap:4px}
.acts button{border:1px solid var(--line);background:#fff;border-radius:5px;font-size:11px;padding:2px 6px;cursor:pointer}
.nav{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.nav select{font:inherit;padding:5px;border:1px solid var(--line);border-radius:6px;max-width:220px}
textarea{width:100%;min-height:54px;font:inherit;border:1px solid var(--line);border-radius:6px;padding:7px;resize:vertical}
.rules{background:#fffdf6;border:1px solid #f0e3bf;border-radius:8px;padding:10px 12px;margin:0 14px 0;font-size:13px}
.rules ol{margin:6px 0 0;padding-left:20px}
.rules b{color:#8a5a00}
.empty{padding:60px 20px;text-align:center;color:#78716c}
.drop{border:2px dashed #cfcbc4;border-radius:10px;padding:34px;text-align:center;color:#78716c;margin-top:10px}
.drop.on{border-color:var(--b);background:#f0f5fb}
.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:20px;background:#efeeea;color:#57534e;margin-left:6px}
</style></head><body>
<header>
  <h1>부위 넘버링 입력기</h1>
  <span class="tag">__BATCH__</span>
  <div class="prog"><i id="pbar"></i></div>
  <span id="pnum" style="font-size:12px;color:#57534e;white-space:nowrap">0 / 0</span>
  <button class="btn" id="bOpen">사진 폴더 열기</button>
  <button class="btn" id="bLoad">이어하기</button>
  <button class="btn pri" id="bSave">JSON 내보내기</button>
  <input type="file" id="fDir" webkitdirectory directory multiple hidden>
  <input type="file" id="fJson" accept="application/json" hidden>
</header>

<div class="rules">
  <b>작업 규칙</b>
  <ol>
    <li>목록의 부위가 <b>사진에 안 보이면 “없음”</b>을 누르세요. 비슷한 데 찍지 마세요.</li>
    <li>같은 부위가 여러 개 보이면 <b>가장 잘 보이는 하나만</b> 찍습니다.</li>
    <li>번호끼리 겹치지 않게, 제품 형상을 가리지 않는 자리에.</li>
    <li>유리 안쪽이 비쳐 보이는 부위는 <b>바깥 윤곽 쪽</b>에 찍습니다.</li>
    <li>애매하면 찍지 말고 <b>메모에 “잘 모르겠음”</b>이라고 적어 주세요.</li>
  </ol>
  <p style="margin:8px 0 0;color:#8a5a00"><b>중요:</b> 브라우저를 닫기 전에 반드시 <b>JSON 내보내기</b>를 누르세요. 자동 저장되지 않습니다. 다음에 이어서 할 때는 <b>이어하기</b>로 그 파일을 불러오면 됩니다.</p>
</div>

<main>
  <div class="stage">
    <div class="nav">
      <button class="btn" id="bPrev">◀ 이전</button>
      <select id="sel"></select>
      <button class="btn" id="bNext">다음 ▶</button>
      <span id="fname" style="font-size:12px;color:#78716c"></span>
    </div>
    <div id="host"><div class="empty">위의 <b>사진 폴더 열기</b>를 눌러 <code>img/gaossunion</code> 폴더를 통째로 고르거나,<br>아래 상자에 폴더를 끌어다 놓으세요.
      <div class="drop" id="drop">여기에 폴더를 끌어다 놓기</div></div></div>
  </div>
  <div class="side">
    <p class="mt" id="mt">—</p>
    <p class="mf" id="mf"></p>
    <ul class="items" id="items"></ul>
    <p style="margin:14px 0 4px;font-weight:700;font-size:13px">메모 (애매한 것 적어주세요)</p>
    <textarea id="memo" placeholder="예) 3번 루긴 모세관이 어느 관인지 잘 모르겠음"></textarea>
  </div>
</main>

<script>
const SPEC = __SPEC__;
const KIND = {b:['본체 구성','#1E3A5F'], d:['이 형식만','#0D6E6E'], o:['주문 시 옵션','#646469'], x:['미포함 · 별매','#B22222']};
const ORDER = Object.keys(SPEC.images);
const state = {};   // base -> {marks:{n:{x,y}}, none:[n], memo:''}
const urls = {};    // base -> objectURL
let cur = 0, selN = null, imgEl = null;

ORDER.forEach(b => state[b] = {marks:{}, none:[], memo:''});

function items(base){ return SPEC.models[SPEC.images[base]].items; }
function doneCount(base){ const s=state[base]; return Object.keys(s.marks).length + s.none.length; }
function isDone(base){ return doneCount(base) >= items(base).length; }

function updateProgress(){
  const tot = ORDER.length, dn = ORDER.filter(isDone).length;
  document.getElementById('pbar').style.width = (100*dn/tot)+'%';
  document.getElementById('pnum').textContent = dn+' / '+tot+' 장';
  const s = document.getElementById('sel');
  [...s.options].forEach((o,i)=>{ const b=ORDER[i];
    o.textContent = (isDone(b)?'✔ ':'') + b + '  ('+doneCount(b)+'/'+items(b).length+')'; });
}

function buildSelect(){
  const s = document.getElementById('sel'); s.innerHTML='';
  ORDER.forEach(b => { const o=document.createElement('option'); o.value=b; s.appendChild(o); });
  s.onchange = () => { cur = ORDER.indexOf(s.value); render(); };
}

function firstPending(base){
  const s = state[base];
  for(const it of items(base)) if(!(it.n in s.marks) && !s.none.includes(it.n)) return it.n;
  return null;
}

function render(){
  const base = ORDER[cur], mdl = SPEC.models[SPEC.images[base]], s = state[base];
  document.getElementById('sel').value = base;
  document.getElementById('mt').textContent = mdl.title;
  document.getElementById('mf').textContent = base + '.jpg' + (urls[base] ? '' : '  — 사진 없음');
  document.getElementById('fname').textContent = (cur+1)+' / '+ORDER.length;
  document.getElementById('memo').value = s.memo;
  selN = selN && (items(base).some(i=>i.n===selN)) ? selN : firstPending(base);

  // 사진
  const host = document.getElementById('host');
  if(!urls[base]){ host.innerHTML = '<div class="empty">'+base+'.jpg 를 폴더에서 찾지 못했습니다.<br>사진 폴더를 다시 골라 주세요.</div>'; }
  else {
    host.innerHTML = '';
    const w = document.createElement('div'); w.className='imgwrap'; w.id='iw';
    const im = document.createElement('img'); im.src = urls[base]; im.alt = base;
    w.appendChild(im); host.appendChild(w); imgEl = im;
    im.onload = drawMarks;
    if(im.complete) drawMarks();
    w.addEventListener('click', ev => {
      if(ev.target !== im) return;
      if(selN == null){ return; }
      const r = im.getBoundingClientRect();
      const x = Math.round((ev.clientX-r.left)/r.width*im.naturalWidth);
      const y = Math.round((ev.clientY-r.top)/r.height*im.naturalHeight);
      s.marks[selN] = {x,y};
      s.none = s.none.filter(n=>n!==selN);
      selN = firstPending(base);
      render();
    });
  }
  // 목록
  const ul = document.getElementById('items'); ul.innerHTML='';
  items(base).forEach(it => {
    const li = document.createElement('li');
    const placed = it.n in s.marks, none = s.none.includes(it.n);
    li.className = (it.n===selN?'cur ':'') + (placed?'done ':'') + (none?'none':'');
    li.onclick = e => { if(e.target.tagName==='BUTTON') return; selN = it.n; render(); };
    const b = document.createElement('span'); b.className='bdg';
    b.style.background = KIND[it.kind][1]; b.textContent = it.n;
    const lb = document.createElement('span'); lb.className='lb';
    lb.innerHTML = it.label + '<span class="kd">'+KIND[it.kind][0]+(placed?' · 찍음':none?' · 사진에 없음':'')+'</span>';
    const ac = document.createElement('span'); ac.className='acts';
    const bn = document.createElement('button'); bn.textContent = none?'되돌리기':'없음';
    bn.onclick = () => { if(none){ s.none = s.none.filter(n=>n!==it.n); }
                         else { delete s.marks[it.n]; s.none.push(it.n); }
                         selN = firstPending(base); render(); };
    ac.appendChild(bn);
    if(placed){ const bd=document.createElement('button'); bd.textContent='지우기';
      bd.onclick=()=>{ delete s.marks[it.n]; selN=it.n; render(); }; ac.appendChild(bd); }
    li.append(b, lb, ac); ul.appendChild(li);
  });
  updateProgress();
}

function drawMarks(){
  const base = ORDER[cur], s = state[base], w = document.getElementById('iw');
  if(!w || !imgEl) return;
  [...w.querySelectorAll('.mk')].forEach(e=>e.remove());
  const map = {}; items(base).forEach(i=>map[i.n]=i);
  Object.entries(s.marks).forEach(([n, p]) => {
    const it = map[n]; if(!it) return;
    const d = document.createElement('div');
    d.className = 'mk' + (String(selN)===String(n)?' sel':'');
    d.style.background = KIND[it.kind][1];
    d.style.left = (100*p.x/imgEl.naturalWidth)+'%';
    d.style.top  = (100*p.y/imgEl.naturalHeight)+'%';
    d.textContent = n; d.title = it.label;
    d.onmousedown = ev => {
      ev.preventDefault(); ev.stopPropagation(); selN = Number(n); d.style.cursor='grabbing';
      const move = e2 => { const r = imgEl.getBoundingClientRect();
        p.x = Math.max(0, Math.min(imgEl.naturalWidth,  Math.round((e2.clientX-r.left)/r.width*imgEl.naturalWidth)));
        p.y = Math.max(0, Math.min(imgEl.naturalHeight, Math.round((e2.clientY-r.top)/r.height*imgEl.naturalHeight)));
        d.style.left=(100*p.x/imgEl.naturalWidth)+'%'; d.style.top=(100*p.y/imgEl.naturalHeight)+'%'; };
      const up = () => { document.removeEventListener('mousemove',move);
        document.removeEventListener('mouseup',up); d.style.cursor='grab'; render(); };
      document.addEventListener('mousemove',move); document.addEventListener('mouseup',up);
    };
    w.appendChild(d);
  });
}

function takeFiles(list){
  let hit = 0;
  for(const f of list){
    if(!/\.jpe?g$/i.test(f.name)) continue;
    const base = f.name.replace(/\.jpe?g$/i,'');
    if(base in state){ if(urls[base]) URL.revokeObjectURL(urls[base]);
      urls[base] = URL.createObjectURL(f); hit++; }
  }
  const miss = ORDER.filter(b=>!urls[b]);
  alert('사진 '+hit+'장을 찾았습니다.' + (miss.length ? '\n못 찾은 것 '+miss.length+'장: '+miss.join(', ') : ''));
  render();
}

document.getElementById('bOpen').onclick = () => document.getElementById('fDir').click();
document.getElementById('fDir').onchange = e => takeFiles(e.target.files);
document.getElementById('bLoad').onclick = () => document.getElementById('fJson').click();
document.getElementById('fJson').onchange = e => {
  const f = e.target.files[0]; if(!f) return;
  const r = new FileReader();
  r.onload = () => { try{
      const d = JSON.parse(r.result);
      ORDER.forEach(b => {
        const mk = (d.markers||{})[b] || [];
        state[b].marks = {}; mk.forEach(m => state[b].marks[m.n] = {x:m.x, y:m.y});
        const nt = (d.notes||{})[b] || {};
        state[b].none = nt.none || []; state[b].memo = nt.memo || '';
      });
      selN = null; render(); alert('불러왔습니다.');
    } catch(err){ alert('JSON 을 읽지 못했습니다: '+err); } };
  r.readAsText(f);
};
document.getElementById('memo').oninput = e => { state[ORDER[cur]].memo = e.target.value; };
document.getElementById('bPrev').onclick = () => { cur=(cur-1+ORDER.length)%ORDER.length; selN=null; render(); };
document.getElementById('bNext').onclick = () => { cur=(cur+1)%ORDER.length; selN=null; render(); };
document.getElementById('bSave').onclick = () => {
  const out = {_batch: SPEC._batch, markers:{}, notes:{}};
  ORDER.forEach(b => {
    const s = state[b], map = {}; items(b).forEach(i=>map[i.n]=i);
    const arr = Object.entries(s.marks).map(([n,p]) => ({n:Number(n), x:p.x, y:p.y,
      kind: map[n].kind, label: map[n].label})).sort((a,c)=>a.n-c.n);
    if(arr.length) out.markers[b] = arr;
    if(s.none.length || s.memo) out.notes[b] = {none:s.none.slice().sort((a,c)=>a-c), memo:s.memo};
  });
  const blob = new Blob([JSON.stringify(out,null,1)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'numbering___SLUG__.json';
  document.body.appendChild(a); a.click(); a.remove();
};
const drop = document.getElementById('drop');
document.addEventListener('dragover', e => { e.preventDefault(); if(drop) drop.classList.add('on'); });
document.addEventListener('dragleave', () => { if(drop) drop.classList.remove('on'); });
document.addEventListener('drop', e => { e.preventDefault();
  if(drop) drop.classList.remove('on');
  if(e.dataTransfer.files && e.dataTransfer.files.length) takeFiles(e.dataTransfer.files); });
window.addEventListener('keydown', e => {
  if(e.target.tagName === 'TEXTAREA') return;
  if(e.key === 'ArrowRight') document.getElementById('bNext').click();
  if(e.key === 'ArrowLeft')  document.getElementById('bPrev').click();
  if(/^[1-9]$/.test(e.key)){ const n=Number(e.key);
    if(items(ORDER[cur]).some(i=>i.n===n)){ selN=n; render(); } }
});
buildSelect(); render();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('-o', '--out', default='넘버링_입력기.html')
    ap.add_argument('--slug', default='batch')
    a = ap.parse_args()
    spec = json.load(io.open(a.spec, encoding='utf-8'))
    bad = [b for b, m in spec['images'].items() if m not in spec['models']]
    assert not bad, '모델 정의 없음: %s' % bad
    for m, d in spec['models'].items():
        ns = sorted(i['n'] for i in d['items'])
        assert ns == list(range(1, len(ns) + 1)), '%s 번호 불연속 %s' % (m, ns)
    html = (HTML.replace('__SPEC__', json.dumps(spec, ensure_ascii=False))
                .replace('__BATCH__', spec.get('_batch', ''))
                .replace('__SLUG__', a.slug))
    io.open(a.out, 'w', encoding='utf-8').write(html)
    print('생성:', a.out)
    print('사진 %d장 · 모델 %d개 · 번호 %d개'
          % (len(spec['images']), len(spec['models']),
             sum(len(spec['models'][m]['items']) for m in spec['images'].values())))
    print('진영님께: 이 파일 + img/gaossunion 폴더를 주고, 결과 JSON 을 돌려받으면 됩니다.')


if __name__ == '__main__':
    main()
