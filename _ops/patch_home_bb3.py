# -*- coding: utf-8 -*-
# 홈 정리: 공정 스트립·용도 카드 삭제, 밴드 2개(재료·소모품/툴·장비)로 축소, 최신연구 3개씩 슬라이드
import io, os, re
here = os.path.dirname(os.path.abspath(__file__))
fp = os.path.join(here, '..', 'index.html')
h = io.open(fp, encoding='utf-8').read()

def cut(start_pat, kind):
    global h
    a = h.find(start_pat)
    assert a >= 0, start_pat[:60]
    d = 0
    for m in re.finditer(r'<' + kind + r'\b|</' + kind + '>', h[a:]):
        d += 1 if not m.group(0).startswith('</') else -1
        if d == 0:
            end = a + m.end()
            seg = h[a:end]
            h = h[:a] + h[end:]
            return seg
    raise RuntimeError(start_pat)

# 1) 공정 스트립·용도 카드 섹션 삭제
cut('<section class="bb-sec"><div class="bb-eyebrow">BATTERY WORKFLOW</div>', 'section')
cut('<section class="bb-sec"><div class="bb-eyebrow">SHOP BY APPLICATION</div>', 'section')

# 2) 밴드 3개 → 2개 교체
cut('<div class="band dk">\n      <div class="bwrap">\n        <div>\n          <div class="be">HEAT TREATMENT</div>', 'div')
cut('<div class="band">\n      <div class="bwrap">\n        <div class="bim">', 'div')
cut('<div class="band dk">\n      <div class="bwrap">\n        <div>\n          <div class="be">FLUID', 'div')

bands = '''
    <div class="band dk">
      <div class="bwrap">
        <div>
          <div class="be">BATTERY RESEARCH</div>
          <div class="bt">재료 · 소모품</div>
          <p class="bd">이온교환막·카본페이퍼(GDL)·CO&#8322;RR 촉매·전극 연마용품까지 — 실험을 멈추지 않게 하는 소모품을 소량 단위로 공급합니다.</p>
          <div class="bcta"><a class="bb-btn" href="/brands/gaossunion/echem-materials/">재료 · 소모품 보기</a></div>
        </div>
        <div class="bim"><div class="ct" style="background-image:url('/img/gaossunion/echem-materials-1.jpg')"></div><div class="ct" style="background-image:url('/img/gaossunion/co2rr-catalyst-1.jpg')"></div></div>
      </div>
    </div>

    <div class="band">
      <div class="bwrap">
        <div class="bim"><div class="ct" style="background-image:url('/img/product/sh/tube-1500.jpg')"></div><div class="ct" style="background-image:url('/img/leadfluid/official/bt600s-1.jpg')"></div></div>
        <div>
          <div class="be">BATTERY RESEARCH</div>
          <div class="bt">툴 · 장비</div>
          <p class="bd">퍼니스·정량펌프·질량유량계(MFC)·전해셀 — 논문 셋업으로 검증된 장비를 조건에 맞게 구성해 드립니다. 국내에서 직접 수리합니다.</p>
          <div class="bcta"><a class="bb-btn" href="/product/">장비 보러가기</a></div>
        </div>
      </div>
    </div>
'''

# 카테고리 섹션 끝 뒤에 밴드 2개 삽입
ca = h.find('<h2 class="bb-title">카테고리 브라우즈</h2>')
assert ca > 0
ce = h.find('</section>', ca) + len('</section>')
h = h[:ce] + '\n' + bands + h[ce:]

# 3) 최신연구 → 3개씩 슬라이드
old_grid = '<div class="news-grid">'
assert old_grid in h
h = h.replace(old_grid, '''<div class="news-wrap">
        <button class="rail-btn prev" type="button" id="newsPrev" aria-label="이전">&#8249;</button>
        <div class="news-grid" id="newsRail">''', 1)
# news-grid 닫힘 뒤에 next 버튼 — news-grid의 닫는 </div> 위치 탐색
ga = h.find('<div class="news-grid" id="newsRail">')
d = 0
for m in re.finditer(r'<div\b|</div>', h[ga:]):
    d += 1 if m.group(0) == '<div' else -1
    if d == 0:
        ge = ga + m.end()
        break
h = h[:ge] + '\n        <button class="rail-btn next" type="button" id="newsNext" aria-label="다음">&#8250;</button>\n      </div>' + h[ge:]

# CSS: grid → 슬라이드형
h = h.replace('''      .news-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
      @media(max-width:820px){.news-grid{grid-template-columns:1fr}}
      .news-grid .prod-card.nc{flex-basis:auto}''',
'''      .news-wrap{position:relative}
      .news-grid{display:flex;gap:22px;overflow-x:hidden;scroll-behavior:smooth}
      .news-grid .prod-card.nc{flex:0 0 calc((100% - 44px)/3)}
      @media(max-width:820px){.news-grid .prod-card.nc{flex:0 0 100%}}''', 1)

# JS: 슬라이드 (한 화면 폭씩 이동, 끝↔처음 순환)
js = '''<script>
(function(){
  var r=document.getElementById('newsRail');
  if(!r) return;
  function go(dir){
    var w=r.clientWidth+22, max=r.scrollWidth-r.clientWidth;
    var next=r.scrollLeft+dir*w;
    if(next>max+5) next=0;
    if(next<-5) next=max;
    r.scrollTo({left:next,behavior:'smooth'});
  }
  var p=document.getElementById('newsPrev'), n=document.getElementById('newsNext');
  if(p) p.addEventListener('click',function(){go(-1);});
  if(n) n.addEventListener('click',function(){go(1);});
})();
</script>
'''
h = h.replace('<script src="/assets/site.js" defer></script>', js + '<script src="/assets/site.js" defer></script>', 1)

io.open(fp, 'w', encoding='utf-8').write(h)
assert h.rstrip().endswith('</html>')
assert h.count('<div') == h.count('</div>') and h.count('<section') == h.count('</section>')
o = [h.find(x) for x in ['인기 제품</h2>', '카테고리 브라우즈', '재료 · 소모품', '툴 · 장비', '최신연구</h2>', '이용 후기']]
print('order:', o, 'asc:', o == sorted(o))
print('strip 제거:', '배터리 공정으로 찾기' not in h, '| 용도 제거:', '실험 용도로 찾기' not in h)
