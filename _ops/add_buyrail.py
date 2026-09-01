# -*- coding: utf-8 -*-
"""구 상세페이지에 오른쪽 구매창(buyrail)을 심는다 — 파일 하나씩, 매번 검증.

일괄 정규식 치환이 아니다. 파일마다 (1) 가격표를 읽고 (2) 조각을 끼우고
(3) </html> 종료·JSON-LD 파싱·마커 수를 검사해 통과한 것만 저장한다.

현재 대상: 가오스유니온 구 페이지 (해외 발주 — 표시가는 이미 ×1.45 적용됨).
  data-models 의 x = 표에 찍힌 제품가격, p = x + 145,000(해외배송비)

브랜드별 값 규칙
  · 가오스유니온 / 허페이 : 해외 발주. 표시가가 이미 제품가격, 합계 = 제품가격 + 145,000
  · 삼흥에너지 / 리드플루이드 : 국내. 정가 대비 3% 상시 할인가를 제품가격으로 쓰고
    정가는 취소선으로 함께 보여준다(site.js 의 o.d). 배송료는 붙이지 않는다.
"""
import io, os, re, sys, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIP = 145000
MODE = {
  'gaossunion':    dict(parse=None, ship=True),   # 해외 발주
  'leadfluid':     dict(parse=None, ship=False),  # 국내 — 3% 할인
  'sh-scientific': dict(parse=None, ship=False),
}
WRAP = 832                      # 구 페이지 본문 폭
RAIL = WRAP // 2 + 22           # 438 — 본문 오른쪽 끝
BP   = (RAIL + 250 + 20) * 2    # 1416 → 사이드레일이 켜지는 최소 뷰포트

CSS = ('\n/* 오른쪽 구매창 — 본문 밖 여백에 붙는 sticky 레일 */\n'
       'body{position:relative}\n'
       '.buyrail{display:none}\n'
       '@media(min-width:%dpx){\n'
       '  .buyrail{display:block;position:absolute;left:calc(50%% + %dpx);width:250px;pointer-events:none}\n'
       '  .buyrail .dt-buy{position:sticky;top:86px;pointer-events:auto}\n'
       '}\n'
       '.dt-info .dt-buy{margin:16px 0 0;max-width:420px}\n') % (BP, RAIL)

def disc(p):
    """정가 대비 3% 상시 할인 — 만원 미만 버림 (build.py 와 같은 식)"""
    return int(p * 0.97) // 10000 * 10000

def rows_leadfluid(t):
    """table.price-tbl — <td>모델</td> … <td class="krw">가격원</td>"""
    m = re.search(r'<table class="price-tbl">([\s\S]*?)</table>', t)
    if not m: return []
    out = []
    for tr in re.findall(r'<tr>([\s\S]*?)</tr>', m.group(1)):
        if '<th' in tr: continue
        tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', tr)
        krw = re.search(r'<td[^>]*class="krw"[^>]*>([\s\S]*?)</td>', tr)
        if not tds or not krw: continue
        pm = re.search(r'([\d,]{5,})\s*원', re.sub('<[^>]+>', '', krw.group(1)))
        if not pm: continue
        model = re.sub('<[^>]+>', '', tds[0]).strip()
        out.append((model, '', int(pm.group(1).replace(',', ''))))
    return out

def rows_sh(t):
    """<p class="pkg-note">정가: 18B <b>3,290,000</b> · 23B <b>6,900,000원</b> …"""
    m = re.search(r'<p class="pkg-note"[^>]*>\s*정가[:\s]([\s\S]{0,600}?)</p>', t)
    if not m: return []
    seg = m.group(1)
    # 사양표 열머리 = 정식 모델명
    heads = re.findall(r'<th scope="col">([^<]+)</th>', t)
    heads = [h.strip() for h in heads if h.strip() and h.strip() != '사양']
    out = []
    for chunk in seg.split('·'):
        pm = re.search(r'<b>([\d,]{5,})', chunk)
        if not pm: continue
        label = re.sub('<[^>]+>', '', chunk[:pm.start()]).strip(' :·')
        full = [h for h in heads if label and h.endswith(label)]
        model = full[0] if len(full) == 1 else (label or (heads[0] if heads else '기본'))
        out.append((model, '', int(pm.group(1).replace(',', ''))))
    return out

def price_rows(t):
    """table.pkg-tbl.pkg-opt 의 (모델, 규격, 가격) 행"""
    m = re.search(r'<table class="pkg-tbl pkg-opt">([\s\S]*?)</table>', t)
    if not m: return []
    out = []
    for tr in re.findall(r'<tr>([\s\S]*?)</tr>', m.group(1)):
        if '<th' in tr: continue
        tds = re.findall(r'<td[^>]*>([\s\S]*?)</td>', tr)
        if len(tds) < 2: continue
        txt = [re.sub(r'<[^>]+>', '', x).strip() for x in tds]
        pm = re.search(r'([\d,]{5,})\s*원', txt[-1])
        p = int(pm.group(1).replace(',', '')) if pm else 0
        model = txt[0]
        spec = txt[1] if len(txt) > 2 else ''
        out.append((model, spec, p))
    return out

def convert(path, brand, apply=False):
    t0 = io.open(path, encoding='utf-8').read()
    name = os.path.basename(os.path.dirname(path))
    if 'buyrail' in t0:            return name, 'skip', '이미 적용'
    rows = MODE[brand]['parse'](t0)
    if not rows:                   return name, 'skip', '가격 표기를 찾지 못함'
    if '<div id="pumplab-header"></div>' not in t0: return name, 'skip', '헤더 마커 없음'
    if '</style>' not in t0:       return name, 'skip', 'style 블록 없음'

    t = t0
    # 1) CSS
    i = t.rindex('</style>')
    t = t[:i] + CSS + t[i:]

    # 2) buybox 마크업
    h1 = re.search(r'<h1 class="dt-name">(.*?)(?:<span|</h1>)', t, re.S)
    h1 = re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else name
    if MODE[brand]['ship']:                       # 해외 발주 — 표시가가 곧 제품가격
        mods = [{'m': m, 's': s if s != m else '', 'x': p, 'p': (p + SHIP) if p else 0}
                for m, s, p in rows]
    else:                                         # 국내 — 3% 상시 할인가 + 정가 취소선
        mods = [{'m': m, 's': s if s != m else '', 'x': disc(p), 'p': disc(p), 'd': p}
                for m, s, p in rows]
    mj = json.dumps(mods, ensure_ascii=False).replace("'", '&#39;')
    box = ('<div id="buybox" class="bb dt-buy" data-name="%s" data-models=\'%s\'></div>'
           % (html.escape(h1, quote=True), mj))
    t = t.replace('<div id="pumplab-header"></div>',
                  '<div id="pumplab-header"></div>\n<div class="buyrail">%s</div>' % box, 1)

    # 3) 팔레트 — 주황 글씨 금지(2026-08-29 확정)
    t = t.replace('#E8632C', '#0F69AF')

    # 4) JSON-LD 가격 — 해외 발주만 화면 표시가와 맞춘다.
    #    국내 브랜드는 LD에 정가를 남겨야 한다. build.py 가 /product/ 카드에서
    #    3% 할인을 다시 적용하므로, 할인가를 넣으면 이중 할인이 된다.
    ps = sorted(x['x'] for x in mods if x['x'])
    if ps and MODE[brand]['ship']:
        t = re.sub(r'"lowPrice":\s*"?[\d.]+"?',  '"lowPrice": %d'  % ps[0], t)
        t = re.sub(r'"highPrice":\s*"?[\d.]+"?', '"highPrice": %d' % ps[-1], t)
        t = re.sub(r'"price":\s*"?[\d.]+"?',     '"price": %d'     % ps[0], t)

    # ── 검증 (실패하면 저장하지 않는다)
    assert t.count('</html>') == 1,            '%s: </html> 개수' % name
    assert t.count('class="buyrail"') == 1,    '%s: buyrail 중복' % name
    assert t.count('id="buybox"') == 1,        '%s: buybox 중복' % name
    assert '#E8632C' not in t,                 '%s: 주황 잔존' % name
    json.loads(re.search(r"data-models='(.*?)'></div>", t).group(1).replace('&#39;', "'"))
    for j in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', t):
        json.loads(j)
    assert len(t) > len(t0), '%s: 길이 감소' % name

    if apply:
        io.open(path, 'w', encoding='utf-8').write(t)
    return name, 'ok', '%d종 · %s원~' % (len(rows), format(ps[0], ',') if ps else '문의')

MODE['gaossunion']['parse']    = price_rows
MODE['leadfluid']['parse']     = rows_leadfluid
MODE['sh-scientific']['parse'] = rows_sh

def main():
    apply = '--apply' in sys.argv
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--only='): only = set(a.split('=', 1)[1].split(','))
    want = [a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--brand=')]
    brands = want or list(MODE)
    tot_ok = tot_skip = 0
    for brand in brands:
        d = os.path.join(ROOT, 'brands', brand)
        if not os.path.isdir(d): continue
        ok = skip = 0
        print('== %s' % brand)
        for s in sorted(os.listdir(d)):
            f = os.path.join(d, s, 'index.html')
            if not os.path.isfile(f): continue
            if only and s not in only: continue
            n, st, msg = convert(f, brand, apply)
            if st == 'ok': ok += 1;   print('  [OK]   %-34s %s' % (n, msg))
            else:          skip += 1
            if st != 'ok' and msg not in ('이미 적용',): print('  [skip] %-34s %s' % (n, msg))
        print('   → 적용 %d / 건너뜀 %d\n' % (ok, skip))
        tot_ok += ok; tot_skip += skip
    print('합계 적용 %d장 / 건너뜀 %d장 %s' % (tot_ok, tot_skip, '(저장함)' if apply else '(드라이런)'))

main()
