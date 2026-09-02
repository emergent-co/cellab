# -*- coding: utf-8 -*-
"""Hench(henchld.com) 제품 페이지 생성기 — YP 수동 유압 펠릿 프레스 / HMY 원통형 다이.
양식 = 가오스유니온 glass-cell-c001 (CSS·ctbar 블록을 원본에서 추출해 재사용).
색 = 2026-08 머크풍 팔레트(var(--merck) / var(--merck-link)). 좌측 포인트 바 없음."""
import os, re, json, io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REF = os.path.join(ROOT, 'brands', 'gaossunion', 'glass-cell-c001', 'index.html')
ref = io.open(REF, encoding='utf-8').read()

# 1) head의 폰트+CSS 청크 (preconnect ~ site.css) 추출
i = ref.index('<link rel="preconnect"')
j = ref.index('<link rel="stylesheet" href="/assets/site.css">') + len('<link rel="stylesheet" href="/assets/site.css">')
HEADCSS = ref[i:j]

# 2) 문의블록(ctbar) 추출
m = re.search(r'<section class="ctbar-sec">.*?</section>', ref, re.S)
CTBAR = m.group(0)

# 3) 경고박스 팔레트 보정 (CLAUDE.md 2026-08: var(--warn-bg) + var(--warn-line))
EXTRA = ('<style>.warn{background:var(--warn-bg);border:1px solid var(--warn-line)}'
         '.warn-h{color:#B45309}.warn b{color:#B45309}'
         '.spec-ul{margin:2px 0 6px;padding-left:0;list-style:none;font-size:13.5px;line-height:1.7;color:#374151}'
         '.spec-ul li{margin:3px 0;padding-left:16px;position:relative}'
         '.spec-ul li:before{content:"·";position:absolute;left:4px;font-weight:900;color:#9ca3af}'
         '.dt-thumbs button{display:flex;flex-direction:column;align-items:center;width:auto;min-width:62px}'
         '.dt-thumbs button>img{width:58px;height:58px}'
         '.dt-thumbs .thlb{display:block;font-size:11px;line-height:1.35;color:#57534e;margin-top:4px;text-align:center;max-width:78px}'
         '.dt-thumbs .thlb b{display:block;color:#1c1917;font-size:11.5px}'
         '.hx-note{background:var(--merck-soft);border:1px solid var(--merck-line);border-radius:10px;padding:13px 16px;'
         'font-size:13.5px;line-height:1.75;color:#24303a;margin:14px 0 6px}.hx-note b{color:var(--merck-link)}</style>')

FOOT = ('<div id="pumplab-footer"><!--CNAV_START--><!--CNAV_END--></div>\n'
        '<script src="/assets/site.js" defer></script>\n</body>\n</html>\n')


def faq_html(items):
    out = []
    for tag, q, a in items:
        out.append('<div class="faq-item"><p class="faq-q"><span class="faq-tag">%s</span>%s</p>'
                   '<p class="faq-a">%s</p></div>' % (tag, q, a))
    return ''.join(out)


def faq_ld(items):
    def plain(s):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q),
         "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for _, q, a in items]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def page(*, slug, title, desc, ogimg, brandline, h1, variants, ans, summ, quote, kws,
         crumb_leaf, feats, spec_rows, model_tbl, price_p, pkg_notes, warn_h, warn_p,
         faq_title, faqs, product_ld, thumbs=(), figures=()):
    url = 'https://rndsetup.com/brands/hench/%s/' % slug
    head = (
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>%s</title>\n<meta name="description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<meta property="og:type" content="product"><meta property="og:title" content="%s">'
        '<meta property="og:description" content="%s"><meta property="og:url" content="%s">'
        '<meta property="og:image" content="%s"><meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s">'
        '<meta name="twitter:image" content="%s">\n' % (title, desc, url, h1, desc, url, ogimg, h1, desc, ogimg)
    ) + HEADCSS + EXTRA + '</head>\n'

    kwhtml = ''.join('<a href="%s">%s</a>' % (h, t) for h, t in kws)
    thumbs_html = ''
    if thumbs:
        _b = ''.join(
            '<button type="button" data-src="%s" onclick="agSwap(this)">'
            '<img src="%s" alt="%s" loading="lazy" onerror="this.parentElement.style.display=\'none\'">'
            '<span class="thlb"><b>%s</b>%s</span></button>' % (src, src, lab + ' ' + sub, lab, sub)
            for src, lab, sub in thumbs)
        thumbs_html = ('<div class="dt-thumbs">' + _b + '</div>'
                       '<script>function agSwap(b){document.querySelector(".dt-img img").src='
                       'b.getAttribute("data-src");}</script>')
    varhtml = ('<span style="font-size:.5em;color:#9A9A9A">%s</span>' % variants) if variants else ''
    body = (
        '<body>\n<div id="pumplab-header"></div>\n'
        '<section class="detail-top"><div class="wrap">'
        '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › %s</div>\n'
        '<div class="dt-grid">\n'
        '<div class="dt-col"><div class="dt-img"><img src="%s" alt="%s" loading="lazy" '
        'onerror="this.closest(\'.dt-img\').style.display=\'none\'"></div>%s</div>\n'
        '<div class="dt-info">\n<div class="dt-brand">%s</div>\n'
        '<h1 class="dt-name">%s%s</h1>\n'
        '<p class="dt-ans">%s</p>\n<p class="dt-sum">%s</p>\n'
        '<button type="button" class="qbtn" data-quote="%s">견적문의</button>\n'
        '<div class="dt-kw">%s</div>\n</div>\n</div></div></section>\n'
        % (crumb_leaf, ogimg.replace('https://rndsetup.com', ''), h1, thumbs_html, brandline, h1, varhtml,
           ans, summ, quote, kwhtml)
    )

    feathtml = ''.join('<li>%s</li>' % f for f in feats)
    spechtml = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (k, v) for k, v in spec_rows)
    notes = ''.join('<p class="pkg-note" style="margin-top:14px">%s</p>' % n for n in pkg_notes)
    figs_html = ''
    if figures:
        figs_html = ('<div class="det-imgs" style="margin:22px 0 4px">' + ''.join(
            '<figure><img src="%s" alt="%s" loading="lazy" '
            'onerror="this.parentElement.style.display=\'none\'">'
            '<figcaption>%s</figcaption></figure>' % (src, cap, cap) for src, cap in figures) + '</div>')

    body += (
        '<section class="pkg"><div class="wrap">'
        '<a class="ds-back" href="/product/">← 실험장비 통합 카탈로그</a>\n'
        '<h2 class="pkg-h">특징</h2>\n<ul class="pkg-feat" style="margin-bottom:20px">%s</ul>\n'
        '<h2 class="pkg-h">사양 요약</h2><div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>%s</tbody></table></div>\n'
        '%s\n%s'
        '<h2 class="pkg-h">가격</h2><p class="hx-note">%s</p>\n'
        '%s\n'
        '<div class="warn"><p class="warn-h">⚠ %s</p><p>%s</p></div>\n'
        '<p style="margin-top:16px"><button type="button" class="qbtn" data-quote="%s">견적문의</button></p>'
        '</div></section>\n' % (feathtml, spechtml, model_tbl, figs_html, price_p, notes, warn_h, warn_p, quote)
    )

    body += CTBAR + '\n'
    body += ('<script type="application/ld+json">'
             + json.dumps(product_ld, ensure_ascii=False).replace('</', '<\\/') + '</script>\n')
    body += ('<section class="faq-sec"><div class="wrap"><hr class="pkg-hr">'
             '<h2 class="faq-h">%s</h2>\n%s</div></section>\n' % (faq_title, faq_html(faqs)))
    body += faq_ld(faqs) + '\n'
    body += FOOT
    return head + body


def write(path, html):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(html)
    print('  written %s (%d bytes)' % (os.path.relpath(path, ROOT), len(html.encode('utf-8'))))


# ─────────────────────────── ① 수동 유압 펠릿 프레스 YP ───────────────────────────
YP_MODELS = [
    ('YP-3',   '3 T',  '30 MPa',   'Φ35', '1 MPa = 0.1 T',  '90×120 mm', '210×170×375 mm', '24 kg'),
    ('YP-5',   '5 T',  '31.5 MPa', 'Φ45', '1 MPa = 0.16 T', '90×120 mm', '210×170×375 mm', '24 kg'),
    ('YP-12',  '12 T', '32 MPa',   'Φ70', '1 MPa = 0.4 T',  '92×130 mm', '230×160×385 mm', '28 kg'),
    ('YP-15',  '15 T', '33 MPa',   'Φ75', '1 MPa = 0.5 T',  '92×130 mm', '230×160×385 mm', '28 kg'),
    ('YP-15B', '15 T', '33 MPa',   'Φ75', '1 MPa = 0.5 T',  '92×130 mm', '230×160×385 mm', '28 kg'),
    ('YP-15R', '15 T', '33 MPa',   'Φ75', '1 MPa = 0.5 T',  '92×130 mm', '문의 (4컬럼)',   '문의'),
]
yp_rows = ''.join(
    '<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % r
    for r in YP_MODELS)
YP_TBL = ('<h2 class="pkg-h">모델별 사양 (6종)</h2><div class="pkg-tblwrap">'
          '<table class="pkg-tbl pkg-opt" style="min-width:720px"><thead><tr>'
          '<th>모델</th><th>최대하중</th><th>압력</th><th>실린더</th><th>환산</th>'
          '<th>유효공간</th><th>외형(W×D×H)</th><th>무게</th></tr></thead><tbody>'
          + yp_rows + '</tbody></table></div>'
          '<p class="pkg-note">YP-15R은 컬럼 4본 구조입니다. 외형·무게는 제조사 공개 자료에 표기가 없어 확인 후 안내드립니다.</p>')

YP_FAQ = [
 ('톤수 선택', '우리 시료에 몇 톤짜리가 필요한가요?',
  '필요 하중 ≈ 목표 성형압 × 시료 단면적으로 계산합니다. IR용 KBr 펠릿의 표준인 <b>Φ13 mm</b>는 단면적 132.7 mm²이고, 통상 성형압 700 MPa를 적용하면 700 × 132.7 = 약 92.9 kN ≒ <b>9.5 T</b>입니다. 즉 Φ13 mm KBr 작업에는 12 T 또는 15 T 모델을 권합니다. Φ10 mm(78.5 mm²)라면 같은 700 MPa에서 약 5.6 T로 YP-12도 여유가 큽니다.'),
 ('톤수 선택', 'XRD 분말 시료도 15 T가 필요한가요?',
  '아닙니다. XRD 홀더용 분말 압축은 통상 수십 MPa 수준이면 충분해 Φ20~40 mm 대면적이라도 하중은 크지 않습니다. 반대로 Φ20 mm를 700 MPa로 성형하려면 314 mm² × 700 MPa = 약 22 T가 필요해 YP-15로는 부족합니다. <b>직경이 커질수록 필요 톤수는 제곱으로 늘어납니다.</b>'),
 ('압력 환산', '게이지의 MPa와 실제 톤(T)은 어떻게 다릅니까?',
  '게이지는 유압 회로 압력(MPa)을 표시하고, 실제 하중은 그 압력 × 실린더 단면적입니다. YP-15는 실린더 Φ75(4,418 mm²)이므로 33 MPa × 4,418 mm² ≒ 145.8 kN ≒ 14.9 T가 되어 <b>1 MPa ≈ 0.5 T</b> 눈금이 성립합니다. YP-12는 Φ70(3,848 mm²) × 32 MPa ≒ 12.6 T로 1 MPa ≈ 0.4 T입니다.'),
 ('압력 환산', '15 T를 Φ13 mm 다이에 걸면 시료가 받는 압력은 얼마인가요?',
  '147.1 kN ÷ 132.7 mm² ≒ <b>1,108 MPa (약 1.1 GPa)</b>입니다. KBr 표준 성형압의 1.5배가 넘으므로, 실무에서는 게이지 20 MPa 부근(≈10 T)에서 유지하는 것이 일반적입니다.'),
 ('운용', '압력 유지(hold)는 얼마나 되나요?',
  '압력 안정도 사양이 <b>&lt;1 MPa / 10 min</b>입니다. YP-15 기준으로 10분 동안 하중 감소가 0.5 T 이내라는 뜻이며, KBr 펠릿의 2~5분 유지 공정에서는 사실상 압력 강하가 무시할 수준입니다.'),
 ('구성', '다이(몰드)가 포함되나요?',
  '포함되지 않습니다(별매). 원형·사각·이형 몰드와 버튼셀 배터리 조립용 몰드가 모두 대응되며, 직경·형상을 알려주시면 <a href="/brands/hench/cylindrical-die-hmy/">원통형 다이 HMY</a>와 함께 구성해 견적해 드립니다.'),
 ('모델 차이', 'YP-15 / YP-15B / YP-15R은 무엇이 다릅니까?',
  '최대하중 15 T · 압력 33 MPa · 실린더 Φ75는 세 모델이 동일합니다. <b>YP-15R은 컬럼이 4본</b>이라 하중 편심에 강해 대구경·비대칭 다이에서 유리합니다. YP-15B는 YP-15의 구조 변형 모델로, 세부 차이는 제조사 자료에 명시가 없어 확인 후 안내드립니다.'),
 ('운용', '유압유는 무엇을 쓰나요?',
  '<b>No.68 내마모 유압유</b>를 사용합니다. 시판 규격품이라 국내 조달이 쉽고, 레벨이 내려가면 보충합니다.'),
]

YP = page(
 slug='manual-pellet-press-yp',
 title='Hench YP 시리즈 수동 유압 펠릿 프레스 — IR·XRD 시료 압편기 3·5·12·15톤 | 실험셋업연구소',
 desc='Hench YP 시리즈 수동 유압 펠릿 프레스 6종 — 최대하중 3·5·12·15 T, 압력 30~33 MPa, T/MPa 이중 눈금 게이지, 압력 안정도 <1 MPa/10min. IR(KBr)·XRD 시료 압편용. 다이 별매·구성별 견적.',
 ogimg='https://rndsetup.com/img/hench/yp-15-1.jpg',
 brandline='Hench · 天津恒创立达 (Tianjin Hengchuang Lida)',
 h1='수동 유압 펠릿 프레스 YP 시리즈',
 variants='YP-3 · YP-5 · YP-12 · YP-15 · YP-15B · YP-15R',
 ans='분말 시료를 IR·XRD로 측정할 수 있는 펠릿으로 눌러 만드는 수동 유압 프레스입니다. 전원 없이 레버만으로 최대 15톤을 걸고, 게이지가 톤과 MPa를 함께 보여 줍니다.',
 summ='6종 · 최대하중 <b>3 / 5 / 12 / 15 T</b> · 압력 30~33 MPa · 피스톤 스트로크 30~32 mm · 압력 안정도 &lt;1 MPa/10 min · 유효공간 90×120~92×130 mm · 무게 24~28 kg · <b>다이 별매</b>',
 quote='Hench 수동 유압 펠릿 프레스 YP 시리즈',
 kws=[('/brands/hench/cylindrical-die-hmy/', '#원통형다이'), ('/product/', '#실험장비카탈로그'),
      ('/brands/hench/manual-pellet-press-yp/', '#펠릿프레스'), ('/brands/hench/manual-pellet-press-yp/', '#KBr펠릿'),
      ('/brands/hench/manual-pellet-press-yp/', '#XRD분말성형')],
 crumb_leaf='수동 유압 펠릿 프레스',
 feats=[
  '<b>수동 유압 · 전원 불필요</b> — 레버 펌핑만으로 최대 15 T를 겁니다. 전기·에어 배관이 없어 후드 안이나 좁은 실험대에서 바로 씁니다.',
  '<b>단조 일체형 프레임</b> — 컬럼 2본 구조(YP-15R은 4본)로 하중 편심을 억제해, 반복 압착에서도 프레임 변형이 적습니다.',
  '<b>T / MPa 이중 눈금 게이지</b> — 유압 게이지 압력(MPa)과 실제 하중(T)을 한 화면에서 읽습니다. 환산은 YP-3 1 MPa=0.1 T · YP-5 0.16 T · YP-12 0.4 T · YP-15 0.5 T입니다.',
  '<b>압력 안정도 &lt;1 MPa / 10 min</b> — 유지(hold)가 필요한 KBr 펠릿 성형에서 압력 강하가 작아 투명도 재현성이 좋습니다.',
  '<b>넓은 유효공간</b> — 90×120 mm(YP-3·5), 92×130 mm(YP-12·15). Φ50~80 mm 테이블에 원형·사각·이형·버튼셀 배터리 몰드를 올려 사용합니다.',
  '<b>No.68 내마모 유압유</b> — 표준 규격 유압유라 보충·교환이 쉽습니다.',
 ],
 spec_rows=[
  ('구동 방식', '수동 유압 (레버 펌핑) · 전원 불필요'),
  ('프레임', '단조 일체형 · 컬럼 2본 (<b>YP-15R = 4본</b>)'),
  ('최대하중', '<b>3 / 5 / 12 / 15 T</b> (모델별)'),
  ('압력', '30 / 31.5 / 32 / 33 MPa (모델별)'),
  ('피스톤 스트로크', '30~32 mm'),
  ('압력 안정도', '<b>&lt; 1 MPa / 10 min</b>'),
  ('압반(테이블)', 'Φ50~80 mm'),
  ('게이지', '톤(T) / MPa <b>이중 눈금</b>'),
  ('유압유', 'No.68 내마모 유압유'),
  ('대응 몰드', '원형 · 사각 · 이형 · 버튼셀 배터리 (<b>다이 별매</b>)'),
 ],
 model_tbl=YP_TBL,
 price_p='전 모델 <b>구성별 견적(문의)</b>입니다. 본체 단품 / 본체 + 다이 세트 / 버튼셀 몰드 포함 등 구성에 따라 달라집니다. 필요하신 다이 직경과 시료 종류를 알려주시면 필요 톤수를 계산해 함께 견적해 드립니다.',
 pkg_notes=[
  '<b>다이(몰드)는 별매입니다.</b> 본체만으로는 시료를 성형할 수 없으며, 목표 펠릿 직경에 맞는 <a href="/brands/hench/cylindrical-die-hmy/">원통형 다이(HMY 시리즈)</a>를 함께 선택해야 합니다.',
  'YP-12는 제조사 상세페이지에 "0-15T"로 표기된 곳이 있으나 <b>실제 최대하중은 12 T</b>입니다. 실린더 Φ70 × 32 MPa 환산(≒12.6 T)과 1 MPa=0.4 T 눈금으로 확인했습니다.',
 ],
 warn_h='안전 — 다이 허용 하중을 넘기지 마십시오',
 warn_p='Φ13 mm 다이에 15 T를 전량 가하면 시료면 압력이 <b>약 1.1 GPa</b>에 달합니다. 압력 해제는 릴리즈 밸브를 천천히 열어 단계적으로 진행하고, 성형 중에는 다이 정면에 서지 마십시오. 압반과 다이 하면이 평행하지 않으면 편하중으로 다이가 파손될 수 있습니다.',
 faq_title='수동 유압 펠릿 프레스 YP 시리즈 FAQ',
 faqs=YP_FAQ,
 product_ld={"@context": "https://schema.org", "@type": "Product",
   "name": "수동 유압 펠릿 프레스 YP 시리즈 (Manual Hydraulic Pellet Press)",
   "brand": {"@type": "Brand", "name": "Hench", "alternateName": ["HENCH", "천진항창립달", "天津恒创立达"]},
   "category": "시료 전처리 · 펠릿 프레스",
   "url": "https://rndsetup.com/brands/hench/manual-pellet-press-yp/",
   "image": "https://rndsetup.com/img/hench/yp-15-1.jpg",
   "model": ["YP-3", "YP-5", "YP-12", "YP-15", "YP-15B", "YP-15R"]},
 thumbs=[('/img/hench/yp-15-1.jpg', 'YP-15', '본체 정면'),
         ('/img/hench/yp-15-3.jpg', 'YP-15', '측면·레버'),
         ('/img/hench/yp-15-2.jpg', 'YP-15', '부위 명칭')],
 figures=[('/img/hench/yp-15-2.jpg',
           '각 부 명칭 — Handwheel(핸들휠) · Screw(스크류) · Stand column(컬럼) · '
           'Workbench(작업 테이블) · Pressure handle(가압 레버) · Pointer pressure gauge(지침식 압력계) · '
           'Sump cover(오일 탱크 커버) · Drain valve stem(드레인 밸브) · Eccentric shaft(편심축)')],
)
write(os.path.join(ROOT, 'brands', 'hench', 'manual-pellet-press-yp', 'index.html'), YP)


# ─────────────────────────── ② 원통형 펠릿 다이 HMY ───────────────────────────
HMY_BANDS = [
    ('Φ2 – 6 mm',                       '20 mm', 'Φ43 × 78 mm', '0.55 kg'),
    ('Φ7 – 10 mm',                      '문의',  '문의',        '문의'),
    ('Φ11 – 14 mm <small>(IR 표준 Φ13 포함)</small>', '문의', '문의', '문의'),
    ('Φ15 – 19 mm',                     '문의',  '문의',        '문의'),
    ('Φ20 – 25 mm',                     '문의',  '문의',        '문의'),
]
hmy_rows = ''.join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>' % r for r in HMY_BANDS)
HMY_TBL = ('<h2 class="pkg-h">직경 밴드별 사양</h2><div class="pkg-tblwrap">'
           '<table class="pkg-tbl pkg-opt"><thead><tr>'
           '<th>직경 밴드</th><th>캐비티 깊이</th><th>외형(Φ × L)</th><th>무게</th>'
           '</tr></thead><tbody>' + hmy_rows + '</tbody></table></div>'
           '<p class="pkg-note">Φ7 mm 이상 밴드의 캐비티 깊이·외형·무게는 제조사 공개 자료에 수치 표기가 없어 '
           '추정하지 않고 <b>확인 후 안내</b>로 두었습니다. Φ25 mm를 넘는 대구경도 제작됩니다.</p>')

HMY_FAQ = [
 ('직경 선택', 'IR 분석용은 몇 mm를 골라야 하나요?',
  'FT-IR의 KBr 펠릿은 <b>Φ13 mm가 사실상 표준</b>이며, 대부분의 IR 펠릿 홀더가 Φ13 mm 기준입니다. 마이크로 샘플이나 시료량이 극히 적을 때 Φ5~7 mm를 씁니다. Φ13 mm는 Φ11–14 mm 밴드에 해당합니다.'),
 ('재질·경도', 'HRC 68~70 경도가 왜 중요한가요?',
  'KBr 펠릿 성형압은 통상 700 MPa 이상, 즉 <b>0.7 GPa 이상</b>입니다. 일반 공구강(HRC 55~60)은 이 영역에서 인덴터 단면이 미세하게 눌려 펠릿 표면에 굴곡이 생기고 IR 베이스라인이 흔들립니다. ASSAB+17을 HRC 68~70으로 열처리한 인덴터는 이 압력대에서 영구변형이 발생하지 않아 반복 사용에도 평활도가 유지됩니다.'),
 ('프레스 호환', 'YP 시리즈 프레스에 그대로 쓸 수 있나요?',
  '예. 다이 외형 Φ43 × 78 mm(Φ2–6 밴드)는 <a href="/brands/hench/manual-pellet-press-yp/">YP-3·5</a>의 유효공간 90×120 mm, YP-12·15의 92×130 mm에 모두 들어갑니다. 대구경 밴드는 외형이 커지므로 유효공간 대비 치수를 확인해 드립니다.'),
 ('프레스 호환', '다이 직경별로 필요한 프레스 톤수는 얼마인가요?',
  '성형압 700 MPa 기준으로 <b>Φ10 mm ≈ 5.6 T · Φ13 mm ≈ 9.5 T · Φ20 mm ≈ 22 T</b>입니다. 즉 Φ13 mm까지는 YP-12/15로 충분하지만, Φ20 mm 이상을 고압으로 성형하려면 15 T 수동기로는 부족합니다. XRD용 저압 성형(수십 MPa)이라면 대구경도 YP-15로 가능합니다.'),
 ('용도 구분', 'XRD용과 IR용 다이가 다른가요?',
  '원통형 HMY는 두 용도 모두 대응합니다. 차이는 운용 조건입니다 — IR은 투광이 목적이라 고압·유지 시간이 필요하고, XRD는 표면 평탄도가 목적이라 저압으로 충분합니다. 형광 분석용 등 특수 형상이 필요하면 별도 다이로 구분해 문의해 주십시오.'),
 ('관리', '청소와 보관은 어떻게 하나요?',
  'KBr은 흡습성이 강해 잔류 분말이 캐비티에 남으면 부식과 고착의 원인이 됩니다. 사용 후 무수 알코올로 닦고 완전히 건조한 뒤 데시케이터 또는 건조 보관하십시오. 인덴터 단면에 흠집이 생기면 펠릿 표면에 그대로 전사됩니다.'),
 ('구성', '프레스가 포함되나요?',
  '포함되지 않습니다. 다이는 단품이며, 프레스는 <a href="/brands/hench/manual-pellet-press-yp/">수동 유압 펠릿 프레스 YP 시리즈</a>에서 별도로 고르십시오. 다이와 프레스를 함께 구성해 견적하실 수 있습니다.'),
]

HMY = page(
 slug='cylindrical-die-hmy',
 title='Hench HMY 원통형 펠릿 다이 — KBr·XRD 시료 성형 몰드 Φ2~25 mm | 실험셋업연구소',
 desc='Hench HMY 원통형 펠릿 다이 — 일본산 고속도 공구강 ASSAB+17, 인덴터 경도 HRC 68~70, 성형 직경 Φ2~25 mm 밴드별. IR(KBr)·XRD 분말 시료 성형용, 유압 펠릿 프레스 호환. 구성별 견적.',
 ogimg='https://rndsetup.com/img/hench/hmy-1.jpg',
 brandline='Hench · 天津恒创立达 (Tianjin Hengchuang Lida)',
 h1='원통형 펠릿 다이 HMY 시리즈',
 variants='Φ2–6 · Φ7–10 · Φ11–14 · Φ15–19 · Φ20–25 mm',
 ans='분말 시료를 원판 펠릿으로 눌러 만드는 성형 몰드입니다. 인덴터를 HRC 68~70으로 잡아, KBr 펠릿에 필요한 GPa급 성형압에서도 눌리지 않습니다.',
 summ='재질 <b>일본산 고속도 공구강 ASSAB+17</b> · 인덴터 경도 <b>HRC 68~70</b> · 성형 직경 Φ2~25 mm 밴드별 · 캐비티 깊이 20 mm(Φ2–6 기준) · IR(KBr)·XRD 분말 시료 성형용',
 quote='Hench 원통형 펠릿 다이 HMY',
 kws=[('/brands/hench/manual-pellet-press-yp/', '#펠릿프레스'), ('/product/', '#실험장비카탈로그'),
      ('/brands/hench/cylindrical-die-hmy/', '#펠릿다이'), ('/brands/hench/cylindrical-die-hmy/', '#KBr다이'),
      ('/brands/hench/cylindrical-die-hmy/', '#XRD시료다이')],
 crumb_leaf='원통형 펠릿 다이',
 feats=[
  '<b>일본산 고속도 공구강 ASSAB+17</b> — 열처리 후 치수 안정성이 높아 캐비티와 인덴터의 클리어런스가 유지됩니다.',
  '<b>인덴터 경도 HRC 68~70</b> — GPa급 성형압에서도 인덴터 단면이 눌리지 않아 펠릿 표면이 평활하게 유지됩니다.',
  '<b>직경 밴드별 제작</b> — Φ2–6 / 7–10 / 11–14 / 15–19 / 20–25 mm 등 밴드 단위로 구성합니다. IR 표준인 Φ13 mm는 Φ11–14 밴드에 포함됩니다.',
  '<b>깊은 캐비티</b> — Φ2–6 mm 기준 캐비티 깊이 20 mm로, 분말 충전량에 여유가 크고 두꺼운 펠릿도 성형할 수 있습니다.',
  '<b>표준 유압 프레스 호환</b> — YP 시리즈를 비롯한 수동 유압 펠릿 프레스에 그대로 올려 씁니다.',
 ],
 spec_rows=[
  ('모델', 'HMY (원통형 · Cylindrical Dies)'),
  ('재질', '<b>Japan High Speed Tool Steel ASSAB+17</b>'),
  ('인덴터 경도', '<b>HRC 68~70</b>'),
  ('성형 직경', 'Φ2 ~ Φ25 mm (밴드별) · 대구경 별도 문의'),
  ('캐비티 깊이', '20 mm (Φ2–6 mm 밴드 기준)'),
  ('용도', 'IR(KBr) 펠릿 · XRD 분말 시료 성형'),
  ('호환', '유압 펠릿 프레스 (압력 범위 내)'),
 ],
 model_tbl=HMY_TBL,
 price_p='밴드·직경·수량에 따라 <b>구성별 견적(문의)</b>입니다. 시료 종류와 목표 펠릿 직경을 알려주시면 밴드와 프레스 톤수를 함께 잡아 견적해 드립니다.',
 pkg_notes=[
  '다이는 단품 판매되며 <b>프레스는 포함되지 않습니다.</b> 사용 전 프레스의 최대 하중이 목표 성형압 × 펠릿 단면적을 충족하는지 확인하십시오.',
 ],
 warn_h='안전 — 밴드별 허용 하중이 다릅니다',
 warn_p='소구경 다이에 프레스 최대 하중을 그대로 가하면 시료면 압력이 <b>수 GPa</b>에 달해 인덴터·캐비티가 손상될 수 있습니다. 인덴터와 캐비티 사이에 분말이 끼면 스커핑이 발생하므로 매 사용 후 청소하십시오.',
 faq_title='원통형 펠릿 다이 HMY FAQ',
 faqs=HMY_FAQ,
 product_ld={"@context": "https://schema.org", "@type": "Product",
   "name": "원통형 펠릿 다이 HMY (Cylindrical Pellet Dies)",
   "brand": {"@type": "Brand", "name": "Hench", "alternateName": ["HENCH", "천진항창립달", "天津恒创立达"]},
   "category": "시료 전처리 · 펠릿 다이",
   "url": "https://rndsetup.com/brands/hench/cylindrical-die-hmy/",
   "image": "https://rndsetup.com/img/hench/hmy-1.jpg",
   "model": ["HMY"],
   "material": "Japan High Speed Tool Steel ASSAB+17"},
 thumbs=[('/img/hench/hmy-1.jpg', 'HMY', '다이 세트'),
         ('/img/hench/hmy-2.jpg', 'HMY', '분해 구성'),
         ('/img/hench/hmy-3.jpg', 'HMY', '성형·탈형'),
         ('/img/hench/hmy-5.jpg', 'HMY', '직경 라인업')],
 figures=[('/img/hench/hmy-3.jpg',
           '사용 순서 — 왼쪽: 캐비티에 분말을 채우고 인덴터를 얹어 가압(시료 성형). '
           '오른쪽: 받침 링 위에 올려 반대로 밀어내 펠릿을 꺼냄(탈형).'),
          ('/img/hench/hmy-5.jpg',
           '직경별 다이 라인업 — Φ3부터 Φ100 mm까지 밴드 단위로 제작됩니다. '
           'IR(KBr) 표준은 Φ13 mm입니다.')],
)
write(os.path.join(ROOT, 'brands', 'hench', 'cylindrical-die-hmy', 'index.html'), HMY)


# ─────────────────────────── ③ 브랜드 허브 (비노출·카드 수집용) ───────────────────────────
HUB_STYLE = ('<style>\n'
 '.dsgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:22px 0 8px}\n'
 '@media(max-width:900px){.dsgrid{grid-template-columns:repeat(2,1fr)}}\n'
 '@media(max-width:560px){.dsgrid{grid-template-columns:1fr}}\n'
 '.dscard{border:1px solid #ECECEC;border-radius:14px;overflow:hidden;background:#fff}\n'
 '.dscard-im{position:relative;background:#F6F7F8}\n'
 '.dscard-im img{width:100%;height:auto;display:block}\n'
 '.dscard-bdg{position:absolute;left:10px;top:10px}\n'
 '.dscard-bdg .b{font-size:11.5px;font-weight:800;color:#fff;background:rgba(59,54,149,.9);border-radius:20px;padding:4px 11px}\n'
 '.dscard-bd{padding:14px 16px 16px}\n'
 '.dscard-mdl{font-size:16px;font-weight:800;margin:0 0 6px;line-height:1.35}\n'
 '.dscard-link{color:var(--merck);text-decoration:none}\n'
 '.dscard-link:hover{text-decoration:underline}\n'
 '.dscard-d{font-size:13px;color:#5a6570;line-height:1.6;margin:0}\n'
 '.dscard-p{font-size:12.5px;font-weight:800;color:var(--merck-link);margin:8px 0 0}\n'
 '.gu-links{margin:6px 0 0 18px}.gu-links li{font-size:14px;line-height:1.9}\n'
 '.gu-links a{color:var(--merck);font-weight:600}\n</style>')

CARDS = [
 dict(href='/brands/hench/manual-pellet-press-yp/', cat='pellet',
      text='수동 유압 펠릿 프레스 yp 시리즈 manual hydraulic pellet press yp-3 yp-5 yp-12 yp-15 yp-15b yp-15r '
           'manual-pellet-press-yp 펠릿프레스 압편기 시료 압편 kbr 펠릿 ir 시료 전처리 xrd 분말 성형 '
           '유압프레스 15톤 프레스 버튼셀 몰드 hench 헨치 천진항창립달',
      img='/img/hench/yp-15-1.jpg', bdg='펠릿 프레스',
      title='수동 유압 펠릿 프레스 YP 시리즈',
      nm='YP-3 · YP-5 · YP-12 · YP-15 · YP-15B · YP-15R',
      d='분말 시료를 IR·XRD 측정용 펠릿으로 눌러 만드는 수동 유압 프레스입니다. 전원 없이 레버만으로 최대 15 T를 걸고, 게이지가 톤과 MPa를 함께 보여 줍니다.',
      p='6종 · 구성별 견적'),
 dict(href='/brands/hench/cylindrical-die-hmy/', cat='die',
      text='원통형 펠릿 다이 hmy cylindrical dies 펠릿 다이 성형 몰드 kbr 다이 ir 펠릿 몰드 xrd 시료 다이 '
           'cylindrical-die-hmy assab+17 고속도 공구강 hrc68 인덴터 시료 전처리 hench 헨치 천진항창립달',
      img='/img/hench/hmy-1.jpg', bdg='펠릿 다이',
      title='원통형 펠릿 다이 HMY 시리즈',
      nm='HMY · Φ2~25 mm 밴드별',
      d='분말 시료를 원판 펠릿으로 눌러 만드는 성형 몰드입니다. 인덴터를 HRC 68~70으로 잡아 KBr 펠릿에 필요한 GPa급 성형압에서도 눌리지 않습니다.',
      p='5밴드 · 구성별 견적'),
]

cards_html = ''
for c in CARDS:
    cards_html += (
      '<article class="dscard" data-cat="%(cat)s" data-text="%(text)s">\n'
      '  <div class="dscard-im"><img src="%(img)s" alt="%(title)s — Hench" loading="lazy" width="760" height="570" '
      'onerror="this.closest(\'.dscard-im\').style.display=\'none\'"><div class="dscard-bdg">'
      '<span class="b">%(bdg)s</span></div></div>\n'
      '  <div class="dscard-bd">\n'
      '    <h3 class="dscard-mdl"><a class="dscard-link" href="%(href)s">%(title)s</a></h3>\n'
      '    <div class="dscard-nm">%(nm)s</div>\n'
      '    <p class="dscard-d">%(d)s</p>\n'
      '    <p class="dscard-p">%(p)s</p>\n'
      '  </div>\n</article>\n\n' % c)

HUB = (
 '<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
 '<meta http-equiv="refresh" content="0;url=/product/">\n'
 '<meta name="robots" content="noindex">\n'
 '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
 '<title>Hench(헨치) 펠릿 프레스·펠릿 다이 — IR·XRD 시료 압편 | 실험셋업연구소</title>\n'
 '<meta name="description" content="Hench(천진항창립달) 수동 유압 펠릿 프레스 YP 시리즈(3·5·12·15 T)와 원통형 펠릿 다이 HMY(ASSAB+17, HRC 68~70). IR(KBr)·XRD 분말 시료 압편 장비 국내 안내·견적.">\n'
 '<link rel="canonical" href="https://rndsetup.com/brands/hench/">\n'
 + HEADCSS + EXTRA + HUB_STYLE + '</head>\n'
 '<body>\n<div id="pumplab-header"></div>\n'
 '<section class="detail-top"><div class="wrap">'
 '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › Hench</div>\n'
 '<div class="dt-info" style="max-width:820px">\n'
 '<div class="dt-brand">Hench · 天津恒创立达 (Tianjin Hengchuang Lida)</div>\n'
 '<h1 class="dt-name">Hench — IR·XRD 시료 압편 장비</h1>\n'
 '<p class="dt-ans">Hench(헨치)는 분말 시료를 IR·XRD 측정용 펠릿으로 성형하는 유압 프레스와 다이를 만드는 제조사입니다. '
 '수동 유압 프레스 YP 시리즈와 원통형 다이 HMY를 한 세트로 구성해 씁니다.</p>\n'
 '<p class="dt-sum"><b>수동 유압 펠릿 프레스 YP</b> 3·5·12·15 T · <b>원통형 펠릿 다이 HMY</b> Φ2~25 mm · 구성별 견적</p>\n'
 '<button type="button" class="qbtn" data-quote="Hench 펠릿 프레스·다이">견적문의</button>\n'
 '</div>\n</div></section>\n'
 '<section class="pkg"><div class="wrap"><a class="ds-back" href="/product/">← 실험장비 통합 카탈로그</a>\n'
 '<h2 class="pkg-h">제품 계열</h2>\n'
 '<ul class="gu-links">'
 '<li><a href="/brands/hench/manual-pellet-press-yp/">수동 유압 펠릿 프레스 YP 시리즈 — 6종 · 3~15 T</a></li>'
 '<li><a href="/brands/hench/cylindrical-die-hmy/">원통형 펠릿 다이 HMY 시리즈 — Φ2~25 mm 밴드별</a></li>'
 '</ul>\n'
 '<div class="dsgrid">\n' + cards_html + '</div>\n'
 '<p class="pkg-note" style="margin-top:18px">표기 구성은 <b>부가세(VAT) 별도</b>이며, 홈페이지에 정가가 공개되지 않은 품목이라 '
 '<b>가격은 전부 구성별 견적</b>으로 안내합니다. 해외 발주 제품이라 해외배송비가 주문당 1회 더해집니다. 납기는 주문 확정 후 안내드립니다.</p>\n'
 '</div></section>\n'
 + CTBAR + '\n' + FOOT
)
write(os.path.join(ROOT, 'brands', 'hench', 'index.html'), HUB)
