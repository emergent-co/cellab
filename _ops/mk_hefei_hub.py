# -*- coding: utf-8 -*-
"""허페이 인시츄 브랜드 허브 생성 — brands/hefei/index.html
가오스유니온 허브와 같은 골격(detail-top + gu-links + dsgrid dscard)을 쓴다.
/product/ 통합 카탈로그는 build.py가 이 허브의 dscard를 읽어 재생성한다."""
import io, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'brands', 'gaossunion', 'index.html')
OUT  = os.path.join(ROOT, 'brands', 'hefei', 'index.html')
PAGE = os.path.join(ROOT, 'brands', 'hefei')

ITEMS = [('om003-microscope-cell', '인시츄 관찰 셀')]
NM = {'om003-microscope-cell': 'CIS-OM-003 · CIS-OM-003-1'}

def strip(s): return re.sub(r'<[^>]+>', '', s).strip()

def read(slug):
    t = io.open(os.path.join(PAGE, slug, 'index.html'), encoding='utf-8').read()
    h1  = strip(re.search(r'<h1 class="dt-name">(.*?)(?:<span|</h1>)', t, re.S).group(1))
    sub = re.search(r'<h1 class="dt-name">.*?<span[^>]*>(.*?)</span>', t, re.S)
    ans = strip(re.search(r'<p class="dt-ans">(.*?)</p>', t, re.S).group(1))
    prices = [int(x.replace(',', '')) for x in re.findall(r'<td[^>]*>\s*<b>([\d,]+)원</b>', t)]
    nask = len(re.findall(r'<td[^>]*>\s*<b>문의</b>', t))
    mm = re.search(r"data-models='(\[.*?\])'", t)
    nmod = mm.group(1).count('"m"') if mm else 0
    img = re.search(r'<div class="dt-img"><img src="([^"]+)"', t)
    return dict(slug=slug, h1=h1, sub=strip(sub.group(1)) if sub else '', ans=ans,
                prices=prices, nask=nask, nmod=nmod,
                img=img.group(1) if img else '/img/hefei/_photo-pending.svg')

def pricetxt(d):
    n = d['nmod'] or (len(d['prices']) + d['nask'])
    if not d['prices']: return '%d종 · 가격 문의' % n
    lo = min(d['prices'])
    return '%d종 · %s원%s' % (n, format(lo, ','), '부터' if len(d['prices']) > 1 else '')

def li(d):
    return '<li><a href="/brands/hefei/%s/">%s — %s</a></li>' % (
        d['slug'], html.escape(d['h1']), html.escape(pricetxt(d)))

def card(d, cat):
    kw = ' '.join([d['h1'], d['sub'], d['slug'], cat,
                   '허페이 인시츄 hefei in-situ 원위 인시츄 전기화학 관찰셀']).lower()
    return ('<article class="dscard" data-cat="echem" data-text="%s">\n'
            '  <div class="dscard-im"><img src="%s" alt="%s — 허페이 인시츄" loading="lazy" width="760" height="570">'
            '<div class="dscard-bdg"><span class="b y">%s</span></div></div>\n'
            '  <div class="dscard-bd">\n'
            '    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/hefei/%s/">%s</a></h3>\n'
            '    <div class="dscard-nm">%s</div>\n'
            '    <p class="dscard-d">%s</p>\n'
            '    <p class="dscard-p">%s</p>\n'
            '  </div>\n</article>' % (
            html.escape(kw, quote=True), d['img'], html.escape(d['h1'], quote=True),
            html.escape(cat), d['slug'], html.escape(d['h1']),
            html.escape(NM.get(d['slug'], '')),
            html.escape(d['ans']), html.escape(pricetxt(d))))

def main():
    src = io.open(SRC, encoding='utf-8').read()
    ds = [read(s) for s, _ in ITEMS]

    H1  = '허페이 인시츄 — 인시츄 광학·분광 관찰 셀'
    ANS = ('허페이 인시츄(Hefei In-situ Technology Co., Ltd.)는 충·방전 중인 전지 내부를 '
           '현미경·라만·XRD로 그대로 들여다보는 인시츄 관찰 셀을 만드는 제조사입니다. '
           '사양을 공개하고 회신이 빠른 곳이라 셋업 설계 단계에서 다루기 좋습니다.')
    SUM = ('<b>리튬 덴드라이트 광학관찰 셀 CIS-OM-003</b> · PEEK 본체 · 석영창 0.05 mm · '
           '시료 10 × 10 mm · 5,000,000원')
    DESC= ('허페이 인시츄(Hefei In-situ) 인시츄 관찰 셀 — CIS-OM-003 리튬 덴드라이트 광학관찰 셀. '
           'PEEK 본체, 고순도 티타늄 전극, 용융 석영창 0.05 mm, 시료 10×10 mm, 최소 작동거리 1 mm, '
           '헬륨 리크 밀봉. 국내 정품 안내·견적.')
    TITLE='허페이 인시츄(Hefei In-situ) 인시츄 관찰 셀 — 리튬 덴드라이트 광학관찰 CIS-OM-003 | 실험셋업연구소'

    t = src
    # ── 헤드
    t = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % html.escape(TITLE), t, count=1)
    t = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(DESC, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com/brands/hefei/' + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(H1, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(H1, quote=True) + m.group(2), t, count=1)
    for k in ('og:description', 'twitter:description'):
        t = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k,
                   lambda m: m.group(1) + html.escape(DESC, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com/brands/hefei/' + m.group(2), t, count=1)
    for k in ('og:image', 'twitter:image'):
        t = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k,
                   lambda m: m.group(1) + 'https://rndsetup.com' + ds[0]['img'] + m.group(2), t, count=1)

    # ── 히어로
    t = re.sub(r'<div class="crumb">.*?</div>',
               '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › 허페이 인시츄</div>',
               t, count=1, flags=re.S)
    t = re.sub(r'<div class="dt-brand">.*?</div>',
               '<div class="dt-brand">허페이 인시츄 · Hefei In-situ Technology</div>', t, count=1, flags=re.S)
    t = re.sub(r'<h1 class="dt-name">.*?</h1>', '<h1 class="dt-name">%s</h1>' % html.escape(H1),
               t, count=1, flags=re.S)
    t = re.sub(r'<p class="dt-ans">.*?</p>', '<p class="dt-ans">%s</p>' % ANS, t, count=1, flags=re.S)
    t = re.sub(r'<p class="dt-sum">.*?</p>', '<p class="dt-sum">%s</p>' % SUM, t, count=1, flags=re.S)
    t = re.sub(r'<button type="button" class="qbtn" data-quote="[^"]*">',
               '<button type="button" class="qbtn" data-quote="허페이 인시츄 인시츄 관찰 셀">', t, count=1)

    # ── 제품 계열 목록
    t = re.sub(r'<ul class="gu-links">.*?</ul>',
               '<ul class="gu-links">%s</ul>' % ''.join(li(d) for d in ds), t, count=1, flags=re.S)

    # ── dscard 전체 교체
    a = t.find('<div class="dsgrid">')
    b = t.rfind('</article>') + len('</article>')
    assert 0 < a < b
    t = t[:a] + '<div class="dsgrid">\n' + '\n'.join(card(d, c) for d, (_, c) in zip(ds, ITEMS)) + '\n' + t[b:]

    # ── 가격 안내문 (해외 발주 산식)
    t = re.sub(r'<p class="pkg-note" style="margin-top:18px">.*?</p>',
               '<p class="pkg-note" style="margin-top:18px">표기 금액은 <b>제품가격 1개 기준</b>이며 '
               '<b>부가세(VAT) 별도</b>입니다. 해외 발주 제품이라 <b>해외배송비 145,000원</b>이 '
               '주문당 1회 더해집니다. <b>10개 이상</b>은 배송료를 따로 안내드립니다. '
               '납기는 주문 확정 후 안내드립니다.</p>', t, count=1, flags=re.S)

    # ── 잔여 가오스 흔적 정리(본문 영역만) · FAQ/LD 블록 제거
    for pat in (r'<section class="faq-sec">.*?</section>\s*(?=<script|</div>|<div id="pumplab-footer")',):
        t = re.sub(pat, '', t, flags=re.S)
    t = re.sub(r'<script type="application/ld\+json">(?!\{"@context": "https://schema\.org", "@graph").*?</script>\s*', '', t, flags=re.S)

    body_a = t.find('<body>'); body_b = t.find('<!--CNAV_START-->')
    seg = t[body_a:body_b]
    hit = re.findall(r'.{0,60}(?:가오스|gaossunion).{0,60}', seg)
    assert not hit, '허브 본문에 가오스 흔적 %d건:\n  ' % len(hit) + '\n  '.join(hit[:6])

    io.open(OUT, 'w', encoding='utf-8').write(t)
    print('허브 생성', len(t), 'bytes / 카드', t.count('<article class="dscard"'),
          '/ li', t.count('<li><a href="/brands/hefei/'))

main()
