# -*- coding: utf-8 -*-
"""뉴웨어 브랜드 허브 생성 — brands/neware/index.html
가오스유니온 허브와 같은 골격(detail-top + gu-links + dsgrid dscard).
/product/ 통합 카탈로그는 _build/build.py 가 이 허브의 dscard 를 읽어 재생성한다."""
import io, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'brands', 'gaossunion', 'index.html')
PAGE = os.path.join(ROOT, 'brands', 'neware')
OUT  = os.path.join(PAGE, 'index.html')

ITEMS = [('ct-4008q', '배터리 테스터 · 충방전'), ('wgdw-chamber', '환경 시험 챔버 · 고저온')]
NM = {'ct-4008q': 'CT-4008Q · CT/CE-4000 Series',
      'wgdw-chamber': 'WGDW-150 · 225 · 408 · 800'}

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
                img=img.group(1) if img else '/img/neware/_photo-pending.svg')

def pricetxt(d):
    n = d['nmod'] or (len(d['prices']) + d['nask'])
    if not d['prices']:
        return '%d종 · 구성별 견적(문의)' % n
    return '%d종 · %s원%s' % (n, format(min(d['prices']), ','), '부터' if len(d['prices']) > 1 else '')

def li(d):
    return '<li><a href="/brands/neware/%s/">%s — %s</a></li>' % (
        d['slug'], html.escape(d['h1']), html.escape(pricetxt(d)))

def card(d, cat):
    kw = ' '.join([d['h1'], d['sub'], d['slug'], cat,
                   '뉴웨어 NEWARE 배터리 테스터 사이클러 충방전기 고저온 챔버 배터리시험']).lower()
    return ('<article class="dscard" data-cat="echem" data-text="%s">\n'
            '  <div class="dscard-im"><img src="%s" alt="%s — 뉴웨어 NEWARE" loading="lazy" width="760" height="570">'
            '<div class="dscard-bdg"><span class="b y">%s</span></div></div>\n'
            '  <div class="dscard-bd">\n'
            '    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/neware/%s/">%s</a></h3>\n'
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

    H1  = '뉴웨어(NEWARE) — 배터리 충·방전 시험 시스템과 고저온 챔버'
    ANS = ('뉴웨어(NEWARE)는 1998년 설립된 배터리 시험장비 제조사로, 배터리 충·방전 테스터(CT/CE 4000~9000)와 '
           '환경 시험 챔버를 함께 만듭니다. 사이클러와 챔버를 한 계열로 묶어 고저온 사이클 시험을 구성할 수 있는 것이 강점입니다.')
    SUM = ('<b>CT-4008Q</b> 8채널 5V/12A · 정확도 ±0.02% F.S. · 전류 4구간 &nbsp;/&nbsp; '
           '<b>WGDW</b> -70℃~150℃ · ±2℃ · 150~800 L — <b>구성별 견적(문의)</b>')
    DESC = ('뉴웨어(NEWARE) 배터리 시험장비 — CT-4008Q 정밀 충·방전 시험 시스템(8채널, 5V/12A, ±0.02% F.S., '
            '전류 4구간, 10Hz 수집, 오프라인 1GB)과 WGDW 고온·저온 시험 챔버(-20/-40/-70℃~150℃, ±2℃, '
            '150~800L). 국내 정품 안내·구성별 견적.')
    TITLE = '뉴웨어(NEWARE) 배터리 충방전 테스터·고저온 챔버 — CT-4008Q · WGDW | 실험셋업연구소'

    t = src
    rep = lambda pat, val, s, **kw: re.sub(pat, lambda m: m.group(1) + val + m.group(2), s, count=1, **kw)
    t = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % html.escape(TITLE), t, count=1)
    t = rep(r'(<meta name="description" content=")[^"]*(")', html.escape(DESC, quote=True), t)
    t = rep(r'(<link rel="canonical" href=")[^"]*(")', 'https://rndsetup.com/brands/neware/', t)
    t = rep(r'(<meta property="og:title" content=")[^"]*(")', html.escape(H1, quote=True), t)
    t = rep(r'(<meta name="twitter:title" content=")[^"]*(")', html.escape(H1, quote=True), t)
    for k in ('og:description', 'twitter:description'):
        t = rep(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k, html.escape(DESC, quote=True), t)
    t = rep(r'(<meta property="og:url" content=")[^"]*(")', 'https://rndsetup.com/brands/neware/', t)
    for k in ('og:image', 'twitter:image'):
        t = rep(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k, 'https://rndsetup.com' + ds[0]['img'], t)

    t = re.sub(r'<div class="crumb">.*?</div>',
               '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › 뉴웨어</div>',
               t, count=1, flags=re.S)
    t = re.sub(r'<div class="dt-brand">.*?</div>',
               '<div class="dt-brand">뉴웨어 · NEWARE</div>', t, count=1, flags=re.S)
    t = re.sub(r'<h1 class="dt-name">.*?</h1>', '<h1 class="dt-name">%s</h1>' % html.escape(H1),
               t, count=1, flags=re.S)
    t = re.sub(r'<p class="dt-ans">.*?</p>', '<p class="dt-ans">%s</p>' % ANS, t, count=1, flags=re.S)
    t = re.sub(r'<p class="dt-sum">.*?</p>', '<p class="dt-sum">%s</p>' % SUM, t, count=1, flags=re.S)
    t = re.sub(r'<button type="button" class="qbtn" data-quote="[^"]*">',
               '<button type="button" class="qbtn" data-quote="뉴웨어 배터리 시험장비">', t, count=1)

    t = re.sub(r'<ul class="gu-links">.*?</ul>',
               '<ul class="gu-links">%s</ul>' % ''.join(li(d) for d in ds), t, count=1, flags=re.S)

    a = t.find('<div class="dsgrid">')
    b = t.rfind('</article>') + len('</article>')
    assert 0 < a < b
    t = t[:a] + '<div class="dsgrid">\n' + '\n'.join(card(d, c) for d, (_, c) in zip(ds, ITEMS)) + '\n' + t[b:]

    t = re.sub(r'<p class="pkg-note" style="margin-top:18px">.*?</p>',
               '<p class="pkg-note" style="margin-top:18px">뉴웨어는 공개 가격이 없는 제품이라 '
               '<b>구성(채널 수 · 전압/전류 · 챔버 용량 · 통합 여부)에 따라 견적</b>으로 안내드립니다. '
               '표기 사양은 뉴웨어 공식 자료 기준이며, <b>부가세(VAT) 별도</b>입니다. '
               '납기는 주문 확정 후 안내드립니다.</p>', t, count=1, flags=re.S)

    t = re.sub(r'<section class="faq-sec">.*?</section>\s*(?=<script|</div>|<div id="pumplab-footer")',
               '', t, flags=re.S)
    t = re.sub(r'<script type="application/ld\+json">(?!\{"@context": "https://schema\.org", "@graph").*?</script>\s*',
               '', t, flags=re.S)

    body_a = t.find('<body>'); body_b = t.find('<!--CNAV_START-->')
    hit = re.findall(r'.{0,60}(?:가오스|gaossunion).{0,60}', t[body_a:body_b])
    assert not hit, '허브 본문에 가오스 흔적 %d건:\n  ' % len(hit) + '\n  '.join(hit[:6])
    assert t.rstrip().endswith('</html>')

    os.makedirs(PAGE, exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8').write(t)
    print('허브 생성', len(t), 'bytes / 카드', t.count('<article class="dscard"'),
          '/ li', t.count('<li><a href="/brands/neware/'))

main()
