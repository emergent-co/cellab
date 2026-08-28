# -*- coding: utf-8 -*-
# 홈 BB(Beyond Battery)식 구성 개편 — 색은 머크 퍼플 유지
import io, os, re
here = os.path.dirname(os.path.abspath(__file__))
fp = os.path.join(here, '..', 'index.html')
h = io.open(fp, encoding='utf-8').read()
orig_divs = (h.count('<div'), h.count('</div>'))

def block(start_pat, kind='div'):
    a = h.find(start_pat)
    assert a >= 0, start_pat[:50]
    d = 0
    for m in re.finditer(r'<' + kind + r'\b|</' + kind + '>', h[a:]):
        d += 1 if not m.group(0).startswith('</') else -1
        if d == 0:
            return a, a + m.end()
    raise RuntimeError(start_pat)

# ---------- 기존 블록 추출 ----------
# 1) 공정 스트립 (헤더+그리드+캡션)
sh_a = h.find('<div class="brand-head"><div class="t">배터리 공정으로 찾기')
assert sh_a > 0
_, sh_he = block(h[sh_a:sh_a+80])
a2, sh_ge = block('<div class="bw-strip">')
cap_a = h.find('<p style="text-align:center;font-size:12.5px', sh_ge)
cap_e = h.find('</p>', cap_a) + 4
strip_html = h[sh_a:cap_e]
h = h[:sh_a] + h[cap_e:]

# 2) 실험 용도 (헤더+그리드)
uh_a = h.find('<div class="brand-head"><div class="t">실험 용도로 찾기')
assert uh_a > 0
_, ug_e = block('<div class="app-grid">')
use_html = h[uh_a:ug_e]
h = h[:uh_a] + h[ug_e:]

# 3) 이용 후기 (brand-head(rv-head) + rv-band)
rv_a = h.find('<div class="brand-head">\n      <div class="rv-head">')
assert rv_a > 0
_, rvh_e = block('<div class="brand-head">\n      <div class="rv-head">')
_, rvb_e = block('<div class="rv-band"')
rv_html = h[rv_a:rvb_e]
h = h[:rv_a] + h[rvb_e:]

# 4) 최신연구 (brand-head + prod-rail-wrap + 처음이라면 박스)
nr_a = h.find('<div class="brand-head">\n      <div class="t">최신연구</div>')
assert nr_a > 0
_, nrw_e = block('<div class="prod-rail-wrap">')
fb_a = h.find('<div style="margin:18px 0 6px;', nrw_e)
if 0 < fb_a < nrw_e + 300:
    _, fb_e = block('<div style="margin:18px 0 6px;')
else:
    fb_e = nrw_e
news_inner_a = h.find('<div class="prod-rail" id="prodRail">', nr_a)
news_inner_e = block('<div class="prod-rail" id="prodRail">')[1]
news_rail = h[news_inner_a:news_inner_e]
first_box = h[fb_a:fb_e] if fb_e > nrw_e else ''
h = h[:nr_a] + h[fb_e:]

# 5) PRO 하이라이트 + 가격각주 문단? (hl-card는 제자리 유지 — 남은 위치 확인용)
hl_a = h.find('<a class="hl-card"')
assert hl_a > 0

# ---------- 새 CSS ----------
css = '''      .bb-sec{padding:56px 0 8px}
      .bb-eyebrow{text-align:center;font-size:11.5px;font-weight:800;letter-spacing:.2em;color:#E8632C}
      .bb-title{text-align:center;font-family:var(--serif);font-size:clamp(22px,2.8vw,31px);font-weight:800;letter-spacing:.02em;color:#222;margin:6px 0 8px}
      .bb-va{display:block;text-align:center;font-size:13px;color:#6b7280;text-decoration:underline;margin:0 0 26px}
      .pop-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
      @media(max-width:820px){.pop-grid{grid-template-columns:repeat(2,1fr);gap:14px}}
      .pop-card{display:block;text-decoration:none;color:inherit;text-align:center}
      .pop-card .im{border:1px solid #eee;background:#fff center/contain no-repeat;background-origin:content-box;padding:14px;aspect-ratio:1/1}
      .pop-card:hover .im{border-color:#3B3695}
      .pop-card .nm{font-size:14px;font-weight:700;color:#1A1A1A;margin-top:10px;line-height:1.45}
      .pop-card .pr{font-size:13px;color:#555;margin-top:3px}
      .bb-btnrow{text-align:center;margin:28px 0 0}
      .bb-btn{display:inline-block;background:#3B3695;color:#fff;font-size:12.5px;font-weight:800;letter-spacing:.14em;padding:13px 28px;text-decoration:none}
      .bb-btn:hover{background:#2A2570}
      .band{width:100vw;margin:56px calc(50% - 50vw) 0;padding:62px 20px}
      .band.dk{background:#3a3a3a}
      .band .bwrap{max-width:1080px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:46px;align-items:center}
      @media(max-width:820px){.band .bwrap{grid-template-columns:1fr;gap:26px}}
      .band .be{font-size:11px;font-weight:800;letter-spacing:.22em;color:#E8632C;text-align:center}
      .band .bt{font-size:clamp(23px,2.8vw,34px);font-weight:800;letter-spacing:.03em;line-height:1.3;margin-top:8px;text-align:center;color:#222}
      .band.dk .bt{color:#fff}
      .band .bd{font-size:14.5px;line-height:1.85;margin:14px auto 0;color:#4a5560;max-width:430px;text-align:center}
      .band.dk .bd{color:#d6d6d6}
      .band .bcta{text-align:center;margin-top:22px}
      .band .bim{display:grid;grid-template-columns:1fr 1fr;gap:12px}
      .band .bim div{aspect-ratio:1/1;background:#fff center/cover no-repeat}
      .band .bim div.ct{background-size:contain;background-origin:content-box;padding:10px}
      .cat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
      @media(max-width:820px){.cat-grid{grid-template-columns:repeat(2,1fr);gap:12px}}
      .cat-tile{position:relative;display:flex;align-items:center;justify-content:center;aspect-ratio:1/1;background:#f0f0f0 center/cover no-repeat;text-decoration:none;overflow:hidden}
      .cat-tile::after{content:"";position:absolute;inset:0;background:rgba(18,18,26,.30)}
      .cat-tile span{position:relative;z-index:1;color:#fff;font-size:clamp(14px,1.6vw,19px);font-weight:800;letter-spacing:.08em;text-align:center;text-shadow:0 2px 10px rgba(0,0,0,.6);padding:0 10px;line-height:1.4}
      .cat-tile.ct{background-size:contain;background-origin:content-box;background-color:#eef0f3;padding:16px}
      .news-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
      @media(max-width:820px){.news-grid{grid-template-columns:1fr}}
      .news-grid .prod-card.nc{flex-basis:auto}
'''
anchor_css = '      .hero-search{position:relative;display:flex;max-width:540px;margin:22px auto 0}'
assert anchor_css in h
h = h.replace(anchor_css, css + anchor_css, 1)

# ---------- 새 섹션 조립 ----------
pop = '''
    <section class="bb-sec">
      <div class="bb-eyebrow">BEST SELLERS</div>
      <h2 class="bb-title">인기 제품</h2>
      <div class="pop-grid">
        <a class="pop-card" href="/brands/leadfluid/bt101s/"><div class="im" style="background-image:url('/img/leadfluid/official/bt101s-1.jpg')"></div><div class="nm">BT101S 연동펌프</div><div class="pr">972,900원~</div></a>
        <a class="pop-card" href="/product/?q=%ED%8A%9C%EB%B8%8C%ED%8D%BC%EB%8B%88%EC%8A%A4"><div class="im" style="background-image:url('/img/product/sh/tube-1500.jpg')"></div><div class="nm">튜브전기로 1200~1800℃</div><div class="pr">2,980,000원~</div></a>
        <a class="pop-card" href="/brands/gaossunion/reference-electrode/"><div class="im" style="background-image:url('/img/gaossunion/reference-electrode-1.jpg')"></div><div class="nm">Ag/AgCl 기준전극 R1038</div><div class="pr">70,000원~</div></a>
        <a class="pop-card" href="/product/?q=MFC"><div class="im" style="background-image:url('/img/product/alicat/mc.webp')"></div><div class="nm">Alicat 질량유량계 MC</div><div class="pr">견적 문의</div></a>
      </div>
      <div class="bb-btnrow"><a class="bb-btn" href="/product/">VIEW ALL</a></div>
    </section>
'''

band_heat = '''
    <div class="band dk">
      <div class="bwrap">
        <div>
          <div class="be">HEAT TREATMENT</div>
          <div class="bt">열처리 · 소성</div>
          <p class="bd">소성·소결·하소·어닐링 — 1050~1900℃ 박스·튜브·진공·회전 퍼니스와 가스 분위기 제어(MFC)를 한 구성으로 준비합니다.</p>
          <div class="bcta"><a class="bb-btn" href="/product/?q=%ED%8D%BC%EB%8B%88%EC%8A%A4">퍼니스 보러가기</a></div>
        </div>
        <div class="bim"><div class="ct" style="background-image:url('/img/product/sh/tube-1500.jpg')"></div><div class="ct" style="background-image:url('/img/product/sh/muffle-1500.jpg')"></div></div>
      </div>
    </div>
'''

band_echem = '''
    <div class="band">
      <div class="bwrap">
        <div class="bim"><div class="ct" style="background-image:url('/img/gaossunion/glass-cell-1.jpg')"></div><div class="ct" style="background-image:url('/img/gaossunion/battery-cell-1.jpg')"></div></div>
        <div>
          <div class="be">ELECTROCHEMISTRY</div>
          <div class="bt">전기화학 · 수전해</div>
          <p class="bd">기준·작업·상대전극부터 H셀·GDE 유동셀·MEA 전해조까지 838종 — 촉매 스크리닝에서 실용 전류밀도 검증까지 한곳에서.</p>
          <div class="bcta"><a class="bb-btn" href="/product/?q=%EC%A0%84%ED%95%B4%EC%85%80">전해셀 보러가기</a></div>
        </div>
      </div>
    </div>
'''

band_fluid = '''
    <div class="band dk">
      <div class="bwrap">
        <div>
          <div class="be">FLUID &amp; GAS CONTROL</div>
          <div class="bt">유체 · 가스 제어</div>
          <p class="bd">전해액 순환·전구체 정량 공급은 연동·기어펌프로, 분위기·CVD 가스는 질량유량계(MFC)로 — 재현성 있는 공급 셋업을 만듭니다.</p>
          <div class="bcta"><a class="bb-btn" href="/product/?q=%EC%97%B0%EB%8F%99%ED%8E%8C%ED%94%84">펌프 보러가기</a></div>
        </div>
        <div class="bim"><div class="ct" style="background-image:url('/img/leadfluid/official/bt600s-1.jpg')"></div><div class="ct" style="background-image:url('/img/product/alicat/mc.webp')"></div></div>
      </div>
    </div>
'''

cats = '''
    <section class="bb-sec">
      <h2 class="bb-title">카테고리 브라우즈</h2>
      <div class="cat-grid">
        <a class="cat-tile ct" href="/product/?q=%EC%97%B0%EB%8F%99%ED%8E%8C%ED%94%84" style="background-image:url('/img/leadfluid/official/bt600s-1.jpg')"><span>정량 · 연동펌프</span></a>
        <a class="cat-tile ct" href="/product/?q=%ED%8D%BC%EB%8B%88%EC%8A%A4" style="background-image:url('/img/product/sh/muffle-1500.jpg')"><span>퍼니스 · 전기로</span></a>
        <a class="cat-tile ct" href="/product/?q=MFC" style="background-image:url('/img/product/alicat/group-all.webp')"><span>질량유량계 MFC</span></a>
        <a class="cat-tile ct" href="/product/?q=%EC%A0%84%ED%95%B4%EC%85%80" style="background-image:url('/img/gaossunion/glass-cell-1.jpg')"><span>전해셀</span></a>
        <a class="cat-tile ct" href="/product/?q=%EA%B8%B0%EC%A4%80%EC%A0%84%EA%B7%B9" style="background-image:url('/img/gaossunion/rde-rrde-1.jpg')"><span>전극</span></a>
        <a class="cat-tile ct" href="/brands/gaossunion/battery-test-cell/" style="background-image:url('/img/gaossunion/battery-cell-1.jpg')"><span>배터리 테스트 셀</span></a>
        <a class="cat-tile ct" href="/product/?q=%EC%A7%84%EA%B3%B5" style="background-image:url('/img/product/sh/vacuum-muffle-1500.jpg')"><span>진공 · 건조</span></a>
        <a class="cat-tile ct" href="/brands/gaossunion/echem-materials/" style="background-image:url('/img/gaossunion/echem-materials-1.jpg')"><span>재료 · 소모품</span></a>
      </div>
    </section>
'''

news = ('''
    <section class="bb-sec">
      <div class="bb-eyebrow">SETUP &amp; RESEARCH</div>
      <h2 class="bb-title">최신연구</h2>
      <a class="bb-va" href="/magazine/">View all</a>
      <div class="news-grid">''' + news_rail.replace('<div class="prod-rail" id="prodRail">', '', 1).rsplit('</div>', 1)[0] + '''</div>
''' + (('      ' + first_box.strip() + '\n') if first_box else '') + '''    </section>
''')

strip_bb = strip_html.replace(
    '<div class="brand-head"><div class="t">배터리 공정으로 찾기</div><div class="en">BATTERY WORKFLOW</div></div>',
    '<section class="bb-sec"><div class="bb-eyebrow">BATTERY WORKFLOW</div><h2 class="bb-title">배터리 공정으로 찾기</h2>', 1)
strip_bb = '    ' + strip_bb.strip() + '\n    </section>\n'

use_bb = use_html.replace(
    '<div class="brand-head"><div class="t">실험 용도로 찾기</div><div class="en">SHOP BY APPLICATION</div></div>',
    '<section class="bb-sec"><div class="bb-eyebrow">SHOP BY APPLICATION</div><h2 class="bb-title">실험 용도로 찾기</h2>', 1)
use_bb = '    ' + use_bb.strip() + '\n    </section>\n'

rv_bb = '    <section class="bb-sec">\n    ' + rv_html.strip() + '\n    </section>\n'

# ---------- 삽입: 히어로 섹션 뒤 ----------
hero_end = h.find('</section>', h.find('<section class="lp-hero"')) + len('</section>')
assembly = pop + strip_bb + band_heat + use_bb + band_echem + band_fluid + cats + news + rv_bb
h = h[:hero_end] + '\n' + assembly + h[hero_end:]

io.open(fp, 'w', encoding='utf-8').write(h)
assert h.rstrip().endswith('</html>')
d = (h.count('<div'), h.count('</div>'))
print('divs', orig_divs, '->', d, '| balanced:', d[0] == d[1])
print('order ok:', 0 < h.find('인기 제품') < h.find('배터리 공정으로 찾기') < h.find('열처리 · 소성') < h.find('실험 용도로 찾기') < h.find('전기화학 · 수전해') < h.find('카테고리 브라우즈') < h.find('최신연구') < h.find('이용 후기') < h.find('hl-card'))
