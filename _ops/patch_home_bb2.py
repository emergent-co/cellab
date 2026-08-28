# -*- coding: utf-8 -*-
# 홈 순서 재배치: 인기 제품 → 카테고리 12타일 → 밴드 3종 → 공정/용도 → 최신연구 → 후기
import io, os, re
here = os.path.dirname(os.path.abspath(__file__))
fp = os.path.join(here, '..', 'index.html')
h = io.open(fp, encoding='utf-8').read()

def cut(start_pat, kind):
    global h
    a = h.find(start_pat)
    assert a >= 0, start_pat[:60]
    d = 0
    end = None
    for m in re.finditer(r'<' + kind + r'\b|</' + kind + '>', h[a:]):
        d += 1 if not m.group(0).startswith('</') else -1
        if d == 0:
            end = a + m.end()
            break
    assert end
    seg = h[a:end]
    h = h[:a] + h[end:]
    return seg

# 기존 카테고리 섹션·밴드 3종 추출(제거)
cats_old = cut('<section class="bb-sec">\n      <h2 class="bb-title">카테고리 브라우즈', 'section')
band_heat = cut('<div class="band dk">\n      <div class="bwrap">\n        <div>\n          <div class="be">HEAT TREATMENT</div>', 'div')
band_echem = cut('<div class="band">\n      <div class="bwrap">\n        <div class="bim">', 'div')
band_fluid = cut('<div class="band dk">\n      <div class="bwrap">\n        <div>\n          <div class="be">FLUID', 'div')

# 새 12타일 카테고리 섹션
T = [
    ('정량 · 연동펌프', '/product/?q=%EC%97%B0%EB%8F%99%ED%8E%8C%ED%94%84', '/img/leadfluid/official/bt600s-1.jpg'),
    ('시린지 · 기어펌프', '/product/?q=%EA%B8%B0%EC%96%B4%ED%8E%8C%ED%94%84', '/img/leadfluid/official/ct3001f-1.jpg'),
    ('머플로 · 전기로', '/product/?q=%EB%A8%B8%ED%94%8C%EB%A1%9C', '/img/product/sh/muffle-1500.jpg'),
    ('튜브퍼니스', '/product/?q=%ED%8A%9C%EB%B8%8C%ED%8D%BC%EB%8B%88%EC%8A%A4', '/img/product/sh/tube-1500.jpg'),
    ('질량유량계 MFC', '/product/?q=MFC', '/img/product/alicat/group-all.webp'),
    ('전해셀', '/product/?q=%EC%A0%84%ED%95%B4%EC%85%80', '/img/gaossunion/glass-cell-1.jpg'),
    ('전극', '/product/?q=%EA%B8%B0%EC%A4%80%EC%A0%84%EA%B7%B9', '/img/gaossunion/rde-rrde-1.jpg'),
    ('In-situ · 유동셀', '/brands/gaossunion/gas-diffusion-cell/', '/img/gaossunion/gdcell-1.jpg'),
    ('배터리 테스트 셀', '/brands/gaossunion/battery-test-cell/', '/img/gaossunion/battery-cell-1.jpg'),
    ('진공 · 건조', '/product/?q=%EC%A7%84%EA%B3%B5', '/img/product/sh/vacuum-muffle-1500.jpg'),
    ('회전 튜브로', '/brands/sh-scientific/rotary-tube-furnace-pro/', '/img/product/sh/rotary-tube-furnace-pro.jpg'),
    ('재료 · 소모품', '/brands/gaossunion/echem-materials/', '/img/gaossunion/echem-materials-1.jpg'),
]
tiles = '\n'.join(
    '        <a class="cat-tile ct" href="%s" style="background-image:url(\'%s\')"><span>%s</span></a>' % (u, i, n)
    for n, u, i in T)
cats_new = '''
    <section class="bb-sec">
      <h2 class="bb-title">카테고리 브라우즈</h2>
      <div class="cat-grid">
''' + tiles + '''
      </div>
    </section>
'''

# 인기 제품 섹션 끝 찾기 (VIEW ALL 버튼 포함 섹션)
pa = h.find('<h2 class="bb-title">인기 제품</h2>')
assert pa > 0
pe = h.find('</section>', pa) + len('</section>')
h = h[:pe] + '\n' + cats_new + band_heat + '\n' + band_echem + '\n' + band_fluid + '\n' + h[pe:]

# 타일 스타일 BB풍 미세조정 (회색 바탕 + 옅은 오버레이)
h = h.replace('.cat-tile.ct{background-size:contain;background-origin:content-box;background-color:#eef0f3;padding:16px}',
              '.cat-tile.ct{background-size:contain;background-origin:content-box;background-color:#e9e9e9;padding:18px}', 1)
h = h.replace('.cat-tile::after{content:"";position:absolute;inset:0;background:rgba(18,18,26,.30)}',
              '.cat-tile::after{content:"";position:absolute;inset:0;background:rgba(18,18,26,.22)}', 1)

io.open(fp, 'w', encoding='utf-8').write(h)
assert h.rstrip().endswith('</html>')
assert h.count('<div') == h.count('</div>') and h.count('<section') == h.count('</section>')
o = [h.find(x) for x in ['인기 제품</h2>', '카테고리 브라우즈', 'HEAT TREATMENT', 'ELECTROCHEMISTRY', 'FLUID', '배터리 공정으로 찾기', '실험 용도로 찾기', '최신연구</h2>', '이용 후기']]
print('order:', o, '| ascending:', o == sorted(o), '| tiles:', h.count('cat-tile ct') )
