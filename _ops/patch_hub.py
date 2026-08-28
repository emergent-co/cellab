# -*- coding: utf-8 -*-
"""가오스유니온 허브 재배선 — 전극 계열 옛 6장을 새 52장으로 교체.

허브(brands/gaossunion/index.html)의
  · <ul class="gu-links"> 안 <li>
  · <div class="dsgrid"> 안 <article class="dscard">
두 곳만 손댄다. 다른 계열(셀·in-situ·재료 등) 카드는 건드리지 않는다.
/product/ 통합 카탈로그는 build.py가 이 허브의 dscard를 읽어 재생성한다.
"""
import io, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if __file__.startswith('/mnt') else os.getcwd()
HUB  = os.path.join(ROOT, 'brands', 'gaossunion', 'index.html')
PAGE = os.path.join(ROOT, 'brands', 'gaossunion')

OLD = ['reference-electrode', 'counter-electrode', 'working-electrode',
       'rde-rrde', 'rhe', 'electrode-holder']

# 슬러그 → (배지, 정렬순서)  · 홈페이지 카테고리 순서를 그대로 따른다
CATS = [
 ('작업전극', ['gc-disc-working-electrode','pt-disc-working-electrode','au-disc-working-electrode',
              'custom-material-working-electrode','carbon-paste-electrode','sem-working-electrode',
              'magnetic-working-electrode','multifunction-working-electrode','l-type-working-electrode',
              't-type-working-electrode','array-working-electrode']),
 ('기준전극', ['agcl-reference-electrode','agcl-double-salt-bridge','sce-reference-electrode',
              'mercury-sulfate-reference-electrode','mercury-oxide-reference-electrode',
              'ag-ion-reference-electrode','rhe-reference-electrode','luggin-capillary','frit-salt-bridge']),
 ('상대전극', ['pt-plate-counter-electrode','pt-mesh-counter-electrode','pt-wire-counter-electrode',
              'pt-rod-counter-electrode','spiral-pt-wire-counter-electrode','pt-wire-with-salt-bridge',
              'au-plate-counter-electrode','spiral-au-wire-counter-electrode','graphite-rod-counter-electrode']),
 ('회전전극', ['rde-external-thread','rde-internal-thread','rrde-external-thread','rde-rrde3a','rrde-3a',
              'high-temp-rde','sem-rde-external-thread','sem-rde-rrde3a','rotating-ag-ion-electrode',
              'rde-coating-jig']),
 ('전극 클램프', ['pt-clamp-ptfe','pt-clamp-peek','gc-electrode-clamp','au-electrode-clamp',
                'sus-clamp-sus1','sus-clamp-sus2','ti-electrode-clamp','gc-sheet-clamp',
                'thick-sample-clamp','sample-holder-1cm2','custom-sample-clamp']),
 ('전극 부속', ['simple-electrode-holder','electrode-drying-rack']),
]

def strip(s):
    return re.sub(r'<[^>]+>', '', s).strip()

def read(slug):
    p = os.path.join(PAGE, slug, 'index.html')
    t = io.open(p, encoding='utf-8').read()
    h1 = re.search(r'<h1 class="dt-name">(.*?)(?:<span|</h1>)', t, re.S).group(1)
    sub = re.search(r'<h1 class="dt-name">.*?<span[^>]*>(.*?)</span>', t, re.S)
    ans = strip(re.search(r'<p class="dt-ans">(.*?)</p>', t, re.S).group(1))
    prices = [int(x.replace(',', '')) for x in re.findall(r'<td[^>]*>\s*<b>([\d,]+)원</b>', t)]
    nask = len(re.findall(r'<td[^>]*>\s*<b>문의</b>', t))
    models = re.search(r"data-models='(\[.*?\])'", t)
    nmod = models.group(1).count('"m"') if models else 0
    img = re.search(r'<div class="dt-img"><img src="([^"]+)"', t)
    return dict(slug=slug, h1=strip(h1), sub=strip(sub.group(1)) if sub else '',
                ans=ans, prices=prices, nask=nask, nmod=nmod,
                img=img.group(1) if img else '/img/gaossunion/_photo-pending.svg')

def pricetxt(d):
    n = d['nmod'] or (len(d['prices']) + d['nask'])
    if not d['prices']:
        return '%d종 · 가격 문의' % n
    lo = min(d['prices'])
    return '%d종 · %s원%s' % (n, format(lo, ','), '부터' if len(d['prices']) > 1 else '')

def li(d, cat):
    return ('<li><a href="/brands/gaossunion/%s/">%s — %s</a></li>'
            % (d['slug'], html.escape(d['h1']), html.escape(pricetxt(d))))

def card(d, cat):
    kw = ' '.join([d['h1'], d['sub'], d['slug'], cat, '가오스유니온 gaoss union 전기화학']).lower()
    return (
      '<article class="dscard" data-cat="electrode" data-text="%s">\n'
      '  <div class="dscard-im"><img src="%s" alt="%s — 가오스유니온" loading="lazy" width="760" height="570">'
      '<div class="dscard-bdg"><span class="b y">%s</span></div></div>\n'
      '  <div class="dscard-bd">\n'
      '    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/gaossunion/%s/">%s</a></h3>\n'
      '    <p class="dscard-d">%s</p>\n'
      '    <p class="dscard-p">%s</p>\n'
      '  </div>\n'
      '</article>' % (html.escape(kw, quote=True), d['img'], html.escape(d['h1'], quote=True),
                      html.escape(cat), d['slug'], html.escape(d['h1']),
                      html.escape(d['ans']), html.escape(pricetxt(d))))

def main():
    t = io.open(HUB, encoding='utf-8').read()
    orig = t

    lis, cards, DATA = [], [], []
    for cat, slugs in CATS:
        for s in slugs:
            d = read(s); DATA.append(d)
            lis.append(li(d, cat)); cards.append(card(d, cat))
    print('새 항목 %d개' % len(lis))

    # ── 1. 옛 6장의 <li> 제거, 첫 번째가 있던 자리에 새 <li> 삽입
    anchor = None
    for s in OLD:
        m = re.search(r'<li><a href="/brands/gaossunion/%s/">[^<]*</a></li>' % s, t)
        if not m:
            print('  [!] li 없음:', s); continue
        if anchor is None: anchor = s
        t = t[:m.start()] + ('@@NEWLIS@@' if s == anchor else '') + t[m.end():]
    assert '@@NEWLIS@@' in t
    t = t.replace('@@NEWLIS@@', ''.join(lis))

    # ── 2. 옛 6장의 <article> 제거, 첫 번째가 있던 자리에 새 카드 삽입
    anchor = None
    for s in OLD:
        m = re.search(r'<article class="dscard"(?:(?!</article>).)*?/brands/gaossunion/%s/(?:(?!</article>).)*?</article>\n?' % s, t, re.S)
        if not m:
            print('  [!] card 없음:', s); continue
        if anchor is None: anchor = s
        t = t[:m.start()] + ('@@NEWCARDS@@' if s == anchor else '') + t[m.end():]
    assert '@@NEWCARDS@@' in t
    t = t.replace('@@NEWCARDS@@', '\n'.join(cards) + '\n')

    # ── 3. ItemList JSON-LD 재작성 (옛 6계열 → 새 52제품, position 재번호)
    m = re.search(r'<script type="application/ld\+json">(\{"@context"[^\n]*?"@type": "ItemList".*?)</script>', t, re.S)
    assert m, 'ItemList 못 찾음'
    import json as _json
    j = _json.loads(m.group(1))
    keep = [it for it in j['itemListElement']
            if not any(it['url'].endswith('/brands/gaossunion/%s/' % s) for s in OLD)]
    assert len(keep) == len(j['itemListElement']) - len(OLD), '옛 계열 제거 수 불일치'
    newitems = [{'@type': 'ListItem', 'name': d['h1'],
                 'url': 'https://rndsetup.com/brands/gaossunion/%s/' % d['slug']} for d in DATA]
    items = newitems + keep
    for i, it in enumerate(items, 1):
        it['position'] = i
        # 키 순서를 원본과 맞춘다
    j['itemListElement'] = [{'@type': 'ListItem', 'position': it['position'],
                             'name': it['name'], 'url': it['url']} for it in items]
    t = t[:m.start(1)] + _json.dumps(j, ensure_ascii=False) + t[m.end(1):]

    # ── 4. 남은 옛 슬러그 참조 0 확인 (부분일치 주의: reference-electrode ⊂ agcl-reference-electrode)
    for s in OLD:
        bad = re.findall(r'(?<![a-z0-9-])' + re.escape(s) + r'/', t)
        left = [x for x in re.findall(r'/brands/gaossunion/([a-z0-9-]+)/', t) if x == s]
        assert not left, '허브에 %s 참조 %d건 남음' % (s, len(left))

    assert t != orig
    assert t.count('</article>') == t.count('<article class="dscard"')
    io.open(HUB, 'w', encoding='utf-8').write(t)
    print('허브 카드 수', t.count('<article class="dscard"'))
    print('허브 gu-links li 수', re.search(r'<ul class="gu-links">(.*?)</ul>', t, re.S).group(1).count('<li>'))

main()
