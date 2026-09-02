# -*- coding: utf-8 -*-
"""아이다(AIDA) 브랜드 허브 생성 — brands/aida/index.html
가오스유니온 허브와 같은 골격(detail-top + gu-links + dsgrid dscard)을 쓴다.
/product/ 통합 카탈로그는 build.py가 이 허브의 dscard를 읽어 재생성한다."""
import io, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'brands', 'gaossunion', 'index.html')
OUT  = os.path.join(ROOT, 'brands', 'aida', 'index.html')
PAGE = os.path.join(ROOT, 'brands', 'aida')

ITEMS = [('gc-disc-working-electrode', '작업전극'),
         ('pt-disc-working-electrode', '작업전극'),
         ('reference-electrode',       '기준전극'),
         ('pt-sheet-counter-electrode','상대전극'),
         ('rde-rrde',                  '회전전극')]
NM = {'gc-disc-working-electrode': 'GC120 ~ GC321',
      'pt-disc-working-electrode': 'Pt105~Pt160 · Au105~Au160 · Ag120~Ag150',
      'reference-electrode':       'R0201 ~ R0501',
      'pt-sheet-counter-electrode':'Pt213 ~ Pt262',
      'rde-rrde':                  'E3 · E5 · RRDE · Change-Disk'}

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
                img=img.group(1) if img else '/img/aida/_photo-pending.svg')

def pricetxt(d):
    n = d['nmod'] or (len(d['prices']) + d['nask'])
    if not d['prices']: return '%d종 · 가격 문의' % n
    lo = min(d['prices'])
    return '%d종 · %s원%s' % (n, format(lo, ','), '부터' if len(d['prices']) > 1 else '')

def li(d):
    return '<li><a href="/brands/aida/%s/">%s — %s</a></li>' % (
        d['slug'], html.escape(d['h1']), html.escape(pricetxt(d)))

def card(d, cat):
    kw = ' '.join([d['h1'], d['sub'], d['slug'], cat,
                   '허페이 인시츄 aida in-situ 원위 인시츄 전기화학 관찰셀']).lower()
    return ('<article class="dscard" data-cat="electrode" data-text="%s">\n'
            '  <div class="dscard-im"><img src="%s" alt="%s — 허페이 인시츄" loading="lazy" width="760" height="570">'
            '<div class="dscard-bdg"><span class="b y">%s</span></div></div>\n'
            '  <div class="dscard-bd">\n'
            '    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/aida/%s/">%s</a></h3>\n'
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

    H1  = '아이다 — 전기화학 전극 · 전해셀'
    ANS = ('아이다(天津艾达恒晟 · TianJin AIDA Science-Technology)는 전기화학 실험용 전극과 '
           '전해셀을 만드는 제조사입니다. 작업전극·기준전극·상대전극·회전전극부터 '
           '라만·적외 인시츄 셀, 광전기화학 셀, 부식 시험 셀까지 다룹니다.')
    SUM = ('<b>유리탄소·백금·금·은 디스크 작업전극 · 기준전극 · 백금판 상대전극 · '
           'RDE/RRDE 회전전극</b> · 28,000원부터')
    DESC= ('아이다(TianJin AIDA) 전기화학 전극 — 유리탄소(GC) 디스크 작업전극, 백금·금·은 디스크 '
           '작업전극, 염화은·칼로멜·산화수은·은이온 기준전극, 백금판 상대전극, PINE 호환 '
           'RDE·RRDE 회전전극. 모델별 정가와 선택 기준을 정리했습니다.')
    TITLE='아이다(TianJin AIDA) 전기화학 전극 — 작업전극·기준전극·상대전극·RDE/RRDE 정가 | 실험셋업연구소'

    t = src
    # ── 헤드
    t = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % html.escape(TITLE), t, count=1)
    t = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(DESC, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com/brands/aida/' + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(H1, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
               lambda m: m.group(1) + html.escape(H1, quote=True) + m.group(2), t, count=1)
    for k in ('og:description', 'twitter:description'):
        t = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k,
                   lambda m: m.group(1) + html.escape(DESC, quote=True) + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com/brands/aida/' + m.group(2), t, count=1)
    for k in ('og:image', 'twitter:image'):
        t = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*(")' % k,
                   lambda m: m.group(1) + 'https://rndsetup.com' + ds[0]['img'] + m.group(2), t, count=1)

    # ── 히어로
    t = re.sub(r'<div class="crumb">.*?</div>',
               '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › 허페이 인시츄</div>',
               t, count=1, flags=re.S)
    t = re.sub(r'<div class="dt-brand">.*?</div>',
               '<div class="dt-brand">아이다 · TianJin AIDA Science-Technology</div>', t, count=1, flags=re.S)
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
          '/ li', t.count('<li><a href="/brands/aida/'))

main()
