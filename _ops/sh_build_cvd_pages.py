# -*- coding: utf-8 -*-
"""삼흥 CVD 튜브로 시리즈 페이지 생성 (2026-09-06).

배경
  CVD 31모델이 D1 에는 있는데(가격·매입가·사진까지) 사이트에는 페이지가 없었다.
  브로슈어 사양(_build/sh_brochure_specs.json)은 CVD 를 '패키지 구성' 으로 싣는다 —
  퍼니스 본체 + 유량계 + 배관 + 실링마스크 + 석영관 + 칠러 + 진공펌프 + 오일미스트 트랩.
  그래서 사양표도 치수가 아니라 '무엇이 들어 있는가' 를 축으로 세웠다.

가격
  페이지에 숫자를 박지 않는다. <td data-d1="모델"> 마커만 두고
  functions/brands/sh-scientific/_middleware.js 가 D1 소비자가를 주입한다.
  D1 에 없거나 조회 실패면 «견적 문의» 가 그대로 남는다.

쓰기
  python _ops/sh_build_cvd_pages.py            검사만
  python _ops/sh_build_cvd_pages.py --write    생성
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'brands', 'sh-scientific')
SPECS = os.path.join(ROOT, '_build', 'sh_brochure_specs.json')

IMG = '/api/img/web/product/big/%s'          # 실험실닷컴 이미지 프록시

PAGES = [
    dict(slug='cvd-1200-300mm', temp='1200', zone='300mm 1존', heater='Kanthal A-1',
         img='202606/45ac09673f84a1d96f2dcb3a4680db00.jpg',
         ko='1200℃ CVD 튜브로 (300mm 핫존)', en='CVD Tube Furnace',
         models=['SH-CVD-30TG150', 'SH-CVD-50TG300', 'SH-CVD-80TG300', 'SH-CVD-100TG300',
                 'SH-CVD-120TG300', 'SH-CVD-200TG300', 'SH-CVD-250TG300'],
         zone_of={'SH-CVD-30TG150': '150mm'},
         ans='삼흥에너지 <b>1200℃ CVD 튜브로</b>는 퍼니스 본체에 <b>가스 유량계·배관·실링마스크·석영관·칠러·진공펌프·오일미스트 트랩</b>을 한 벌로 묶은 패키지입니다. 튜브경 Φ30~250, 핫존 300mm.',
         sum='CVD 는 퍼니스만 있어서는 돌지 않습니다. 가스를 넣고(유량계·배관·실링마스크), 반응 뒤 배기를 받아내고(진공펌프·오일미스트 트랩), 배기부 온도를 잡아 주는(칠러) 구성이 함께 있어야 합니다. 삼흥 CVD 패키지는 이 구성을 <b>제조사가 미리 맞춰 놓은 한 벌</b>로 공급합니다. 1200℃ 등급은 발열체가 <b>Kanthal A-1</b> 이고, 석영관을 씁니다.'),
    dict(slug='cvd-1200-600mm', temp='1200', zone='600mm 1존', heater='Kanthal A-1',
         img='202606/d06312af6a1dfc2caf85812fd5fe64b9.jpg',
         ko='1200℃ CVD 튜브로 (600mm 핫존)', en='CVD Tube Furnace',
         models=['SH-CVD-50TG600', 'SH-CVD-80TG600', 'SH-CVD-100TG600',
                 'SH-CVD-120TG600', 'SH-CVD-200TG600', 'SH-CVD-250TG600'],
         zone_of={},
         ans='삼흥에너지 <b>1200℃ CVD 튜브로 600mm 핫존</b> 판입니다. 균일 구간이 길어 <b>시료를 여러 개 나란히 놓거나 긴 기판</b>을 처리할 때 씁니다. 튜브경 Φ50~250.',
         sum='핫존이 300mm 에서 <b>600mm</b> 로 길어지면 균일 온도 구간이 두 배가 됩니다. 한 번에 올리는 시료 수를 늘리거나, 긴 기판·튜브 형상을 통째로 넣을 때 이 판을 씁니다. 나머지 구성(유량계·배관·실링마스크·석영관·칠러·진공펌프·오일미스트 트랩)은 300mm 판과 같습니다.'),
    dict(slug='cvd-1200-3zone', temp='1200', zone='200mm × 3존', heater='Kanthal A-1',
         img='202606/b6224868ba5a0bbb2e24e667564a0c85.jpg',
         ko='1200℃ 3존 CVD 튜브로', en='3-Zone CVD Tube Furnace',
         models=['SH-CVD-50TG200-3', 'SH-CVD-80TG200-3', 'SH-CVD-100TG200-3',
                 'SH-CVD-120TG200-3', 'SH-CVD-200TG200-3', 'SH-CVD-250TG200-3'],
         zone_of={},
         ans='삼흥에너지 <b>1200℃ 3존 CVD 튜브로</b>는 200mm 발열 구간 <b>세 개를 따로 제어</b>합니다. 전구체 기화부와 반응부의 온도를 다르게 잡아야 하는 공정에 씁니다.',
         sum='존이 하나면 튜브 전체가 같은 온도입니다. <b>3존</b>은 앞·가운데·뒤를 각각 다른 온도로 잡을 수 있어, <b>전구체를 앞쪽에서 기화시키고 가운데에서 반응</b>시키는 식의 공정이 됩니다. 온도 구배를 의도적으로 만들어야 하는 CVD·기상수송 성장에 맞습니다. 컨트롤러도 존 수만큼 들어갑니다.'),
    dict(slug='cvd-1500', temp='1500', zone='300mm 1존', heater='SiC',
         img='202606/985a3b0fa4a69d0a439ae0cc6524d807.jpg',
         ko='1500℃ CVD 튜브로', en='1500℃ CVD Tube Furnace',
         models=['SH-CVD-50TH300', 'SH-CVD-80TH300', 'SH-CVD-100TH300', 'SH-CVD-120TH300'],
         zone_of={},
         ans='삼흥에너지 <b>1500℃ CVD 튜브로</b>는 발열체가 <b>SiC</b> 로 올라간 등급입니다. 1200℃ 판으로 안 되는 세라믹·탄화물 계열 공정에 씁니다. 튜브경 Φ50~120.',
         sum='1200℃ 와 1500℃ 를 가르는 것은 <b>발열체</b>입니다. Kanthal A-1 은 1200℃ 근처가 한계라 그 위는 <b>SiC</b> 로 갑니다. 튜브도 석영에서 <b>고순도 알루미나</b>로 바뀝니다. 실사용에서는 정격보다 <b>200℃ 낮게</b> 상시 운전하는 것을 권합니다 — 발열체와 내화재는 소모품이고, 정격 온도를 계속 쓰면 수명이 빠르게 깎입니다.'),
    dict(slug='cvd-1700', temp='1700', zone='300mm 1존', heater='MoSi2',
         img='202606/a2d37cc0f187d510b8445490552402d4.jpg',
         ko='1700℃ CVD 튜브로', en='1700℃ CVD Tube Furnace',
         models=['SH-CVD-50TS300/17', 'SH-CVD-80TS300/17', 'SH-CVD-100TS300/17',
                 'SH-CVD-120TS300/17'],
         zone_of={},
         ans='삼흥에너지 <b>1700℃ CVD 튜브로</b>는 발열체가 <b>MoSi2</b> 인 고온 등급입니다. 고온 세라믹 합성·탄화 공정에 씁니다. 튜브경 Φ50~120.',
         sum='<b>MoSi2</b> 발열체가 들어가는 등급입니다. 1500℃ SiC 판보다 한 단계 위이고, 같은 몸체로 <b>1800℃ 판</b>도 있습니다. 고온에서는 튜브·실링·가스켓이 먼저 한계에 닿으므로, 목표 온도와 분위기(진공·불활성·환원)를 같이 알려주시면 구성을 맞춰 드립니다.'),
    dict(slug='cvd-1800', temp='1800', zone='300mm 1존', heater='MoSi2',
         img='202606/8ec74a740815f9d59d5e784f31e8632d.jpg',
         ko='1800℃ CVD 튜브로', en='1800℃ CVD Tube Furnace',
         models=['SH-CVD-50TS300/18', 'SH-CVD-80TS300/18', 'SH-CVD-100TS300/18',
                 'SH-CVD-120TS300/18'],
         zone_of={},
         ans='삼흥에너지 <b>1800℃ CVD 튜브로</b>는 삼흥 CVD 라인의 <b>최고온 등급</b>입니다. 발열체 MoSi2, 튜브경 Φ50~120.',
         sum='CVD 라인에서 가장 높은 등급입니다. 1700℃ 판과 몸체가 같고 발열체·내화재 사양이 올라갑니다. 이 온도대에서는 <b>스펙상 최고온도를 상시 사용 온도로 잡지 마십시오</b> — 실사용 최대치는 정격보다 200℃ 낮게 두는 것을 권합니다. 발열체와 내화재는 소모품입니다.'),
]

FAQ = [
    ('구성', 'CVD 패키지에는 무엇이 들어 있나요?',
     '퍼니스 본체, 가스 유량계, 스테인리스 배관·커넥터, 가스 실링 마스크, 반응관(석영 또는 알루미나), 칠러, 진공펌프, 오일미스트 트랩이 한 벌입니다. 칠러와 진공펌프 모델은 튜브경에 따라 달라집니다.'),
    ('선택', '핫존 300mm 와 600mm, 3존은 어떻게 고르나요?',
     '시료가 한두 개면 300mm, 여러 개를 나란히 놓거나 긴 기판이면 600mm 입니다. 전구체 기화부와 반응부의 온도를 다르게 잡아야 하면 3존입니다.'),
    ('온도', '정격 온도로 계속 돌려도 되나요?',
     '권하지 않습니다. 실사용 최대치는 정격보다 200℃ 낮게 잡는 것을 권합니다. 목표 온도에는 도달하지만 발열체와 내화재가 빠르게 소모됩니다 — 둘 다 소모품입니다.'),
    ('튜브', '튜브경은 어떻게 정하나요?',
     '시료 크기와 보트·캐리어 폭으로 정합니다. 튜브가 굵을수록 히터 용량과 가격이 올라가고 승온·냉각이 느려집니다. 시료 치수를 알려주시면 맞는 관경을 골라 드립니다.'),
    ('A/S', '설치와 A/S는 어디서 하나요?',
     '삼흥에너지는 국내 제조사입니다. 부품 수급과 수리가 빠르고, 구매·설치·국내 A/S는 이머전트(Emergent co)가 맡습니다.'),
    ('제어', '가스 유량과 온도를 하나로 제어할 수 있나요?',
     '가능합니다. 질량유량계(MFC)·압력컨트롤러(BPR)를 붙여 온도·유량·압력을 한 화면에서 잡는 통합 제어까지 셋업해 드립니다. 필요한 조건을 알려주십시오.'),
]


def spec_rows(models, page, bro):
    """모델별 사양 행 — 브로슈어 패키지 구성 + 모델명에서 읽는 관경·핫존."""
    def dia(m):
        g = re.search(r'-(\d+)T[GHS]', m)
        return 'Φ%s' % g.group(1) if g else '—'

    rows = [('튜브경', [dia(m) for m in models]),
            ('핫존', [page['zone_of'].get(m, page['zone'].split()[0]) for m in models]),
            ('최고온도', ['%s℃' % page['temp']] * len(models)),
            ('발열체', [page['heater']] * len(models))]
    for lab, key in (('칠러', 'Chiller'), ('진공펌프', 'Vacuum Pump'), ('오일미스트 트랩', 'Oil Mist Trap')):
        vals = []
        for m in models:
            d = bro.get(m, {}).get('specs', {})
            v = d.get(key) or d.get(key + ' Dimension') or ''
            vals.append(re.split(r'\s*/\s*', v)[0] if v else '—')
        if any(v != '—' for v in vals):
            rows.append((lab, vals))
    rows.append(('판매가', None))          # data-d1 마커 행
    return rows


def build(page, bro):
    ms = page['models']
    esc = lambda s: s.replace('&', '&amp;')
    head_title = '%s %s — 구성·모델별 사양 | 실험셋업연구소' % (page['ko'], page['en'])
    desc = ('삼흥에너지(SH Scientific) %s — %s. 퍼니스 본체·가스 유량계·배관·실링마스크·반응관·'
            '칠러·진공펌프·오일미스트 트랩 한 벌 구성. 구매·국내 A/S는 이머전트(Emergent co).'
            % (page['ko'], ' · '.join(ms[:3]) + (' 외' if len(ms) > 3 else '')))
    url = 'https://rndsetup.com/brands/sh-scientific/%s/' % page['slug']
    img = IMG % page['img']

    th = ''.join('<th scope="col">%s</th>' % esc(m) for m in ms)
    body_rows = []
    for lab, vals in spec_rows(ms, page, bro):
        if vals is None:
            tds = ''.join('<td data-d1="%s">견적 문의</td>' % esc(m) for m in ms)
        elif len(set(vals)) == 1:
            tds = '<td colspan="%d">%s</td>' % (len(ms), esc(vals[0]))
        else:
            tds = ''.join('<td>%s</td>' % esc(v) for v in vals)
        body_rows.append('<tr><th scope="row">%s</th>%s</tr>' % (lab, tds))

    ld = {
        '@context': 'https://schema.org', '@type': 'Product',
        'name': '삼흥에너지 %s' % page['ko'],
        'brand': {'@type': 'Brand', 'name': 'SH Scientific'},
        'manufacturer': {'@type': 'Organization', 'name': 'SH Scientific(삼흥에너지)'},
        'category': '전기로 · CVD 튜브로',
        'image': 'https://rndsetup.com' + img,
        'description': re.sub(r'<[^>]+>', '', page['sum'])[:300],
        'offers': {'@type': 'Offer', 'url': url, 'priceCurrency': 'KRW',
                   'availability': 'https://schema.org/InStock',
                   'seller': {'@type': 'Organization', 'name': '실험셋업연구소'}},
    }
    bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': '홈', 'item': 'https://rndsetup.com/'},
        {'@type': 'ListItem', 'position': 2, 'name': '제품', 'item': 'https://rndsetup.com/product/'},
        {'@type': 'ListItem', 'position': 3, 'name': page['ko'], 'item': url}]}

    faq = ''.join(
        '<div class="faq-item"><p class="faq-q"><span class="faq-tag">%s</span>%s</p>'
        '<p class="faq-a">%s</p></div>' % (t, q, a) for t, q, a in FAQ)

    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="keywords" content="삼흥에너지, SH Scientific, CVD, CVD 퍼니스, CVD 튜브로, %(temp)s도 전기로, 화학기상증착, %(m0)s">
<link rel="canonical" href="%(url)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap" rel="stylesheet">
<meta property="og:type" content="product">
<meta property="og:title" content="%(ko)s %(en)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="https://rndsetup.com%(img)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(ko)s — 실험셋업연구소">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="https://rndsetup.com%(img)s">
<link rel="stylesheet" href="/assets/detail.css">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div id="pumplab-header"></div>
<section class="detail-top">
  <div class="wrap">
    <div class="crumb"><a href="/">홈</a> › <a href="/brands/sh-scientific/guide/">삼흥에너지</a> › <a href="/brands/sh-scientific/">제품 카탈로그</a> › %(ko)s</div>
    <div class="dt-grid">
      <div class="dt-img"><img src="%(img)s" alt="삼흥에너지 %(ko)s 제품 사진" loading="lazy" onerror="this.closest('.dt-img').style.display='none'"></div>
      <div class="dt-info">
        <div class="dt-brand">삼흥에너지 · SH Scientific</div>
        <h1 class="dt-name">%(ko)s <span style="font-size:.62em;color:#9A9A9A">%(en)s</span></h1>
        <p class="dt-ans">%(ans)s</p>
        <p class="dt-sum">%(sum)s</p>
        <button type="button" class="qbtn" data-quote="%(ko)s (%(m0)s 외)">견적문의</button>
        <div class="dt-kw"><a href="/brands/sh-scientific/">#CVD</a><a href="/brands/sh-scientific/">#CVD퍼니스</a><a href="/brands/sh-scientific/?tier=%(temp)s">#%(temp)s℃</a><a href="/brands/sh-scientific/">#화학기상증착</a><a href="/brands/sh-scientific/">#튜브전기로</a><a href="/brands/sh-scientific/">#삼흥에너지</a></div>
      </div>
    </div>
  </div>
</section>
<section class="pkg">
  <div class="wrap">
    <a class="ds-back" href="/brands/sh-scientific/">← 삼흥 퍼니스 카탈로그</a>
    <h2 class="pkg-h">패키지 기본 구성</h2>
    <ul class="pkg-feat">
      <li><b>퍼니스 본체</b> — %(temp)s℃ · 핫존 %(zone)s · 발열체 %(heater)s · 프로그램 컨트롤러</li>
      <li><b>가스 유량계 1EA</b> · <b>스테인리스 배관·커넥터</b> · <b>가스 실링 마스크</b></li>
      <li><b>반응관</b> — 1200℃ 등급은 석영관, 1500℃ 이상은 고순도 알루미나관</li>
      <li><b>칠러 · 진공펌프 · 오일미스트 트랩</b> — 배기부 냉각과 반응 부산물 포집</li>
    </ul>
    <h2 class="pkg-h">모델별 사양</h2>
    <div class="pkg-tblwrap"><table class="pkg-tbl"><thead><tr><th scope="col">Model</th>%(th)s</tr></thead><tbody>%(rows)s</tbody></table></div>
    <p class="pkg-note"><b>구성에 따라 사양·총액이 크게 달라집니다.</b> 질량유량계(MFC)·압력컨트롤러(BPR)·추가 존 제어 등 필요한 것만 골라 넣을 수 있습니다. <b>실험셋업연구소</b> 매거진 — 구매·국내 A/S는 이머전트(Emergent co). <b>조건만 남겨주시면 맞는 구성과 견적으로 회신드립니다.</b></p>
    <p style="margin-top:18px"><button type="button" class="qbtn" data-quote="%(ko)s (%(m0)s 외)">견적문의</button></p>
  </div>
</section>
<section class="faq-sec"><div class="wrap"><hr class="pkg-hr">
<h2 class="faq-h">%(ko)s FAQ</h2>
%(faq)s
</div></section>
<script type="application/ld+json" data-d1-ld="%(mall)s">%(ld)s</script>
<script type="application/ld+json">%(bc)s</script>
<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
""" % dict(title=head_title, desc=desc, url=url, img=img, ko=page['ko'], en=page['en'],
           temp=page['temp'], zone=page['zone'], heater=page['heater'],
           ans=page['ans'], sum=page['sum'], m0=ms[0], th=th,
           rows=''.join(body_rows), faq=faq, mall=','.join(ms),
           ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'),
           bc=json.dumps(bc, ensure_ascii=False).replace('</', '<\\/'))


def main():
    write = '--write' in sys.argv
    bro = json.load(io.open(SPECS, encoding='utf-8'))['models']
    for page in PAGES:
        html = build(page, bro)
        bad = ''
        if not html.rstrip().endswith('</html>'):
            bad = '</html> 누락'
        elif 'class="dt-name"' not in html:
            bad = 'dt-name 없음'
        elif len(re.findall(r'<tr[ >]', html)) != html.count('</tr>'):
            bad = 'tr 짝'
        elif html.count('<table') != html.count('</table>'):
            bad = 'table 짝'
        elif '<style' in html:
            bad = 'style 금지'
        for s in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
            try:
                json.loads(s.replace('<\\/', '</'))
            except Exception as e:
                bad = 'JSON-LD 깨짐: %s' % e
        if bad:
            print('  [FAIL] %-18s %s' % (page['slug'], bad))
            continue
        d = os.path.join(BRAND, page['slug'])
        exists = os.path.isdir(d)
        print('  [%s] %-18s 모델 %d · %d bytes%s'
              % ('생성' if write else '예정', page['slug'], len(page['models']), len(html),
                 ' (이미 있음 — 덮어씀)' if exists else ''))
        if write:
            os.makedirs(d, exist_ok=True)
            io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='').write(html)
    return 0


if __name__ == '__main__':
    sys.exit(main())
