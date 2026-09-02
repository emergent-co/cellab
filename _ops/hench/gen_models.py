# -*- coding: utf-8 -*-
"""Hench 모델 단위 페이지 생성 — 프레스 YP 6종 + 원통형 다이 HMY 11밴드.
수치는 전부 hench_products.csv(제조사 수집본)에서 읽는다. 손으로 적지 않는다."""
import os, sys, csv, json, io, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hench_common as H

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(io.open(os.path.join(HERE, 'hench_products.csv'), encoding='utf-8-sig')))

def row_by_pg(pg):
    return next(r for r in ROWS if r['url'].endswith(pg))

def row_by_name(frag):
    return next(r for r in ROWS if frag in r['name'])

def U(v):
    """제조사 표기 단위 정규화: Mpa→MPa, Kg→kg, 숫자와 단위 사이 공백, 92x130→92×130."""
    if not v or v == '—': return v
    v = re.sub(r'Mpa', 'MPa', v).replace('Kg', 'kg').replace('KG', 'kg')
    v = re.sub(r'/\s*(\d+)\s*min', r' / \1 min', v)
    v = re.sub(r'(?<=\d)\s*[x×]\s*(?=\d)', '×', v)
    v = re.sub(r'(?<=\d)(mm|kg|MPa)\b', r' \1', v)
    v = re.sub(r'(?<=\d)T\b', ' T', v)
    v = re.sub(r'\s*[（(]\s*(?:M|N|D|d|T|L\s*[×x]\s*N|M\s*[×x]\s*N)\s*[）)]', '', v)  # 제조사 도면 기호 제거
    v = re.sub(r'\s*、\s*', ' · ', v)
    v = re.sub(r'\s{2,}', ' ', v).strip()
    return v


def S(r, *keys, **kw):
    sp = json.loads(r['spec'])
    for k in keys:
        for x in sp:
            if x.lower() == k.lower():
                v = re.sub(r'\s+', ' ', sp[x]).strip()
                if v: return U(v) if kw.get('raw') is None else v
    return kw.get('d', '—')

def conv_t(v):
    """'1 MPa=0.5 T' 같은 표기에서 계수(0.5)만 뽑는다."""
    m = re.search(r'=\s*([0-9.]+)', v or '')
    return m.group(1) if m else '—'


def ids(r): return r['ids'].split()
def fnum(s):
    m = re.search(r'(\d+(?:\.\d+)?)', s or '')
    return float(m.group(1)) if m else 0.0

MPA = 700.0
def t_for(d): return H.need_ton(d, MPA)

# ══════════════════════ 프레스 YP 6종 ══════════════════════
PRESS = [
    dict(pg='PG4264976', model='YP-3',   ton=3,  slug='pellet-press-yp-3'),
    dict(pg='PG4264977', model='YP-5',   ton=5,  slug='pellet-press-yp-5'),
    dict(pg='PG4264978', model='YP-12',  ton=12, slug='pellet-press-yp-12',
         fix='제조사 상세페이지에는 압력범위가 <b>0-15T</b>로 적혀 있으나 <b>실제 최대하중은 12 T</b>입니다. '
             '실린더 Φ70(3,848 mm²) × 32 MPa ≒ 12.6 T이고 게이지 환산도 1 MPa = 0.4 T라 12 T가 맞습니다.'),
    dict(pg='PG4264979', model='YP-15',  ton=15, slug='pellet-press-yp-15'),
    dict(pg='PG4264980', model='YP-15B', ton=15, slug='pellet-press-yp-15b'),
    dict(pg='PG4264981', model='YP-15R', ton=15, slug='pellet-press-yp-15r'),
]
PRESS_ALL = [(p['slug'], p['model']) for p in PRESS]

WHY = {
 'YP-3':   '가장 작은 3 T 기본기. 미량 시료·소구경 펠릿 전용이고 KBr 표준 Φ13 mm에는 하중이 모자랍니다.',
 'YP-5':   '3 T보다 한 단계 여유. 그래도 Φ13 mm KBr 표준 성형에는 부족해, 소구경 위주라면 고르는 모델입니다.',
 'YP-12':  'Φ13 mm KBr 펠릿(약 9.5 T)을 여유 있게 소화하는 최소 모델. IR 전처리 표준 작업에 가장 무난합니다.',
 'YP-15':  'IR·XRD 전처리의 사실상 표준기. Φ13 mm KBr에 여유가 있고 유효공간도 92×130 mm로 넉넉합니다.',
 'YP-15B': 'YP-15와 하중은 같지만 <b>프레임이 한 체급 큽니다.</b> 실린더 Φ80·스트로크 40 mm·유효공간 140×150 mm로, 키가 큰 다이나 부속을 함께 올릴 때 고릅니다.',
 'YP-15R': '<b>컬럼 4본</b> 구조. 하중 편심에 강해 대구경·비대칭 다이, 버튼셀 몰드처럼 편하중이 생기기 쉬운 작업에 유리합니다.',
}

def press_page(p):
    r = row_by_pg(p['pg']); m, T = p['model'], p['ton']
    cyl = S(r, 'Cylinder diameter', 'Piston diameter')
    cyl_d = fnum(cyl); area = math.pi * cyl_d ** 2 / 4.0
    conv = S(r, 'Pressure conversion'); stroke = S(r, 'Piston stroke', 'Max. piston stroke')
    stab = S(r, 'Pressure stability'); table = S(r, 'Table diameter')
    cols = S(r, 'Number of columns', 'Columns'); space = S(r, 'Valid space', 'Available space', 'Column spacing')
    dim = S(r, 'Dimensions', 'Size'); wt = S(r, 'Equipment weight', 'Weight')
    if wt != '—' and not re.search(r'kg', wt, re.I): wt = wt + ' kg'   # 라벨 파싱에서 단위가 잘린 경우 보정
    mpa_max = fnum(re.sub(r'^[^(]*\(', '', S(r, 'Pressure range', 'Pressure'))) or 0
    dmax = H.max_dia(T, MPA); p13 = H.sample_mpa(T, 13)
    slug = p['slug']
    img = '/img/hench/%s-1.jpg' % slug
    others = [(('/brands/hench/%s/' % s), n) for s, n in PRESS_ALL if s != slug]

    spec = [('구동 방식', '수동 유압 (레버 펌핑) · 전원 불필요'),
            ('최대하중', '<b>%d T</b>%s' % (T, ' (게이지 %.0f MPa 만점)' % mpa_max if mpa_max else '')),
            ('실린더', 'Φ%s' % cyl.replace('mm', '').strip() + ' mm' if cyl_d else cyl),
            ('압력 환산', '1 MPa = %s T' % (conv_t(conv) or '—')),
            ('피스톤 스트로크', stroke), ('압력 안정도', stab),
            ('압반(테이블)', table), ('컬럼', '%s 본' % cols if cols.isdigit() else cols),
            ('유효공간', space), ('외형(W×D×H)', dim), ('무게', wt if 'kg' in wt.lower() else wt + ' kg'),
            ('유압유', 'No.68 내마모 유압유'),
            ('대응 몰드', '원형 · 사각 · 이형 · 버튼셀 배터리 (<b>다이 별매</b>)')]

    feats = [
      '<b>%s — %s</b>' % (m, WHY[m]),
      '<b>수동 유압 · 전원 불필요</b> — 레버 펌핑만으로 최대 %d T를 겁니다. 전기·에어 배관이 없어 후드 안이나 좁은 실험대에서 바로 씁니다.' % T,
      '<b>T / MPa 이중 눈금 게이지</b> — 이 모델은 <b>1 MPa = %s T</b>로 환산됩니다. 실린더 Φ%.0f mm(%.0f mm²)에서 나온 값입니다.' % (
          conv_t(conv), cyl_d, area),
      '<b>압력 안정도 %s</b> — 유지(hold)가 필요한 KBr 펠릿 성형에서 압력 강하가 작아 투명도 재현성이 좋습니다.' % stab,
      '<b>단조 일체형 프레임 · 컬럼 %s본</b> — 하중 편심을 억제해 반복 압착에서도 프레임 변형이 적습니다.' % cols,
      '<b>유효공간 %s</b> — 압반 %s에 원형·사각·이형·버튼셀 몰드를 올려 사용합니다.' % (space, table),
    ]
    incl = [('본체 1대 (유압 실린더 · 게이지 · 레버 일체형)', 'in', '포함'),
            ('No.68 유압유 초기 주입', 'in', '포함'),
            ('다이(몰드) — 목표 펠릿 직경에 맞춰 별도 선택', 'ex', '미포함·별매'),
            ('사진 속 다이·시료는 연출용', 'ex', '미포함')]

    faqs = [
      ('톤수 선택', '%s로 만들 수 있는 펠릿 직경은 어디까지인가요?' % m,
       'IR용 KBr 펠릿의 통상 성형압 700 MPa를 기준으로 하면, 최대하중 %d T로 낼 수 있는 시료 지름은 <b>약 Φ%.1f mm</b>까지입니다. '
       '표준인 Φ13 mm(단면적 132.7 mm²)에는 700 × 132.7 = 약 92.9 kN ≒ <b>9.5 T</b>가 필요하므로, %s'
       % (T, dmax, '이 모델로 <b>여유 있게 가능합니다</b>.' if T >= 11 else
          '이 모델로는 <b>부족합니다</b> — Φ13 mm 표준 작업이 목적이라면 <a href="/brands/hench/pellet-press-yp-12/">YP-12</a> 이상을 권합니다.')),
      ('압력 환산', '게이지의 MPa를 톤으로 어떻게 읽나요?',
       '이 모델은 실린더 Φ%.0f mm이므로 단면적이 %.0f mm²입니다. 여기에 게이지 압력을 곱한 값이 실제 하중이라 '
       '<b>1 MPa ≈ %s T</b>가 됩니다. 게이지에 톤(T)과 MPa가 함께 새겨져 있어 환산 없이 바로 읽을 수 있습니다.'
       % (cyl_d, area, conv_t(conv))),
      ('압력 환산', '최대하중을 Φ13 mm 다이에 걸면 시료 압력은 얼마인가요?',
       '%d T = %.1f kN을 Φ13 mm(132.7 mm²)에 걸면 <b>약 %.0f MPa</b>입니다. %s'
       % (T, T * 9.80665, p13,
          'KBr 표준 성형압(700 MPa)의 %.1f배라 실무에서는 중간 눈금에서 멈춰 유지합니다.' % (p13 / 700)
          if p13 > 700 else '표준 성형압 700 MPa에는 못 미치므로 더 작은 직경을 쓰거나 상위 모델을 고려하십시오.')),
      ('운용', '압력 유지(hold)는 얼마나 되나요?',
       '압력 안정도 사양이 <b>%s</b>입니다. 이 모델 환산(1 MPa = %s T) 기준으로 10분 동안 하중 감소가 %s T 이내라는 뜻이며, '
       'KBr 펠릿의 2~5분 유지 공정에서는 압력 강하가 사실상 무시할 수준입니다.'
       % (stab, conv_t(conv), conv_t(conv))),
      ('구성', '다이(몰드)가 포함되나요?',
       '포함되지 않습니다(별매). 목표 펠릿 직경에 맞는 <a href="/brands/hench/cylindrical-die-hmy-7-10/">원통형 다이 HMY</a>를 함께 고르셔야 하며, '
       '원형·사각·이형과 버튼셀 배터리 몰드가 모두 대응됩니다. 시료 종류와 직경을 알려주시면 함께 구성해 견적해 드립니다.'),
      ('비교', '다른 YP 모델과 무엇이 다릅니까?',
       '%s YP 시리즈는 하중(3·5·12·15 T)과 프레임 크기로 갈립니다. 하중이 같은 15 T 안에서도 '
       '<b>YP-15</b>(실린더 Φ75·유효공간 92×130 mm·28 kg), <b>YP-15B</b>(Φ80·140×150 mm·52.9 kg), '
       '<b>YP-15R</b>(Φ80·컬럼 4본·80×80×150 mm·42.5 kg)로 구조가 다릅니다.' % WHY[m]),
      ('운용', '유압유는 무엇을 쓰나요?',
       '<b>No.68 내마모 유압유</b>를 사용합니다. 시판 규격품이라 국내 조달이 쉽고, 레벨이 내려가면 보충합니다. '
       '기름이 새거나 압력이 오르지 않으면 실링 점검이 필요합니다.'),
    ]
    notes = ['<b>다이(몰드)는 별매입니다.</b> 본체만으로는 시료를 성형할 수 없습니다. '
             '<a href="/brands/hench/cylindrical-die-hmy-7-10/">원통형 다이 HMY 밴드</a>에서 목표 직경을 고르십시오.']
    if p.get('fix'):
        notes.append('<b>제조사 표기 정정</b> — ' + p['fix'])

    models = [{"m": m, "s": '%d T · 실린더 Φ%.0f mm · 유효공간 %s' % (T, cyl_d, space)}]
    return dict(
      models=models,
      slug=slug, crumb='수동 유압 펠릿 프레스',
      title='Hench %s %dT 수동 유압 펠릿 프레스 — IR·XRD 시료 압편기 | 실험셋업연구소' % (m, T),
      desc='Hench %s 수동 유압 펠릿 프레스 — 최대하중 %d T, 실린더 Φ%.0f mm, 1 MPa=%s T 이중 눈금, 압력 안정도 %s, 유효공간 %s, 무게 %s. IR(KBr)·XRD 시료 압편용, 다이 별매·구성별 견적.'
           % (m, T, cyl_d, conv_t(conv), stab, space, wt),
      h1='%s 수동 유압 펠릿 프레스 %d T' % (m, T),
      ans='분말 시료를 IR·XRD로 측정할 수 있는 펠릿으로 눌러 만드는 수동 유압 프레스입니다. %s' % WHY[m].replace('<b>', '').replace('</b>', ''),
      summ='최대하중 <b>%d T</b> · 실린더 Φ%.0f mm · 1 MPa = %s T · 스트로크 %s · 안정도 %s · 유효공간 %s · 무게 %s · <b>다이 별매</b>'
           % (T, cyl_d, conv_t(conv), stroke, stab, space, wt),
      quote='Hench %s 수동 유압 펠릿 프레스 %dT' % (m, T),
      kws=[('/brands/hench/cylindrical-die-hmy-7-10/', '#원통형다이'), ('/product/', '#실험장비카탈로그'),
           ('/brands/hench/%s/' % slug, '#펠릿프레스'), ('/brands/hench/%s/' % slug, '#KBr펠릿'),
           ('/brands/hench/%s/' % slug, '#%dT프레스' % T)],
      img=img,
      thumbs=[(img, m, '본체 정면'), ('/img/hench/%s-2.jpg' % slug, m, '측면·레버'),
              ('/img/hench/%s-3.jpg' % slug, m, '부위 명칭')],
      feats=feats, incl=incl, spec=spec, figures=[], opt_tbl='',
      price='<b>구성별 견적(문의)</b>입니다. 본체 단품 / 본체 + 다이 세트 / 버튼셀 몰드 포함 등 구성에 따라 달라집니다. '
            '필요하신 다이 직경과 시료 종류를 알려주시면 필요 톤수를 계산해 함께 견적해 드립니다.',
      notes=notes,
      warn_h='안전 — 다이 허용 하중을 넘기지 마십시오',
      warn_p='이 모델의 최대하중 %d T를 Φ13 mm 다이에 전량 가하면 시료면 압력이 <b>약 %.0f MPa</b>에 달합니다. '
             '압력 해제는 릴리즈 밸브를 천천히 열어 단계적으로 진행하고, 성형 중에는 다이 정면에 서지 마십시오. '
             '압반과 다이 하면이 평행하지 않으면 편하중으로 다이가 파손될 수 있습니다.' % (T, p13),
      xlinks=others,
      faqs=faqs,
      ld={"@context": "https://schema.org", "@type": "Product",
          "name": "%s Manual Hydraulic Pellet Press %dT" % (m, T),
          "brand": {"@type": "Brand", "name": "Hench", "alternateName": ["HENCH", "天津恒创立达"]},
          "category": "시료 전처리 · 펠릿 프레스",
          "url": 'https://rndsetup.com/brands/hench/%s/' % slug,
          "image": 'https://rndsetup.com' + img, "model": m,
          "additionalProperty": [{"@type": "PropertyValue", "name": "Max load", "value": "%d T" % T},
                                 {"@type": "PropertyValue", "name": "Cylinder diameter", "value": "%.0f mm" % cyl_d}]},
      _ids=ids(r))


# ══════════════════════ 원통형 다이 HMY 11밴드 ══════════════════════
# slug·표시 밴드는 제조사 '제목'이 아니라 '스펙 Sample size'를 기준으로 잡는다 (제목/스펙이 어긋난 페이지가 있음).
DIES = [
    dict(frag='Φ2mmΦ3mmΦ4mmΦ5mmΦ6mm Cylindrical',      slug='cylindrical-die-hmy-3-6',     band='Φ3–6 mm'),
    dict(frag='Φ7mmΦ8mmΦ9mmΦ10mm Cylindrical',         slug='cylindrical-die-hmy-7-10',    band='Φ7–10 mm'),
    dict(frag='Φ11mmΦ12mmΦ13mmΦ14mm Cylindrical',      slug='cylindrical-die-hmy-11-14',   band='Φ11–14 mm',
         bad='제조사 상세페이지의 사양표에 <b>Φ7–10 밴드의 값이 그대로 복사</b>되어 있습니다(시료 치수·캐비티 깊이·외형·무게 전부 동일). '
             'Φ11–14 밴드의 실제 치수는 확인 후 안내드리며, 추정값을 싣지 않습니다.'),
    dict(frag='Φ15mmΦ16mm',  slug='cylindrical-die-hmy-15-19',  band='Φ15–19 mm'),
    dict(frag='Φ20mmΦ21mm',  slug='cylindrical-die-hmy-20-25',  band='Φ20–25 mm'),
    dict(frag='Φ26mmΦ27mm',  slug='cylindrical-die-hmy-26-30',  band='Φ26–30 mm'),
    dict(frag='Φ31mmΦ32mm',  slug='cylindrical-die-hmy-31-35',  band='Φ31–35 mm'),
    dict(frag='Φ36mmΦ37mm',  slug='cylindrical-die-hmy-36-40',  band='Φ36–40 mm'),
    dict(frag='Φ41-Φ70mm',   slug='cylindrical-die-hmy-41-70',  band='Φ41–70 mm', multi=True),
    dict(frag='Φ71-Φ100mm',  slug='cylindrical-die-hmy-71-100', band='Φ71–100 mm', multi=True),
    dict(frag='Φ101-Φ150mm', slug='cylindrical-die-hmy-101-150', band='Φ101–150 mm', multi=True),
]
DIE_ALL = [(d['slug'], d['band']) for d in DIES]

def material_of(r):
    sp = json.loads(r['spec']); blob = ' '.join(list(sp.keys()) + list(sp.values()))
    if 'ASSAB' in blob: return '일본산 고속도 공구강 <b>ASSAB+17</b>', 'Japan High Speed Tool Steel ASSAB+17'
    if 'Cr12MoV' in blob: return '합금공구강 <b>Cr12MoV</b>', 'Alloy tool steel Cr12MoV'
    return '—', ''

def die_page(d):
    r = row_by_name(d['frag']); slug, band = d['slug'], d['band']
    ss = S(r, 'Sample size'); depth = S(r, 'Cavity depth'); dim = S(r, 'Dimensions'); wt = S(r, 'Weight')
    hard = S(r, 'Indenter hardness').replace('HRC', '').replace('-', '~HRC').strip()
    hard = 'HRC' + hard if hard != '—' else '—'
    mat_h, mat_en = material_of(r)
    nums = [float(x) for x in re.findall(r'Φ?(\d+(?:\.\d+)?)', ss)] if ss != '—' else []
    dmin, dmax = (min(nums), max(nums)) if nums else (0, 0)
    img = '/img/hench/%s-1.jpg' % slug
    others = [(('/brands/hench/%s/' % s), b) for s, b in DIE_ALL if s != slug]
    bad = d.get('bad')
    has13 = 11 <= dmax and dmin <= 13 <= dmax

    spec = [('모델', 'HMY (원통형 · Cylindrical Dies)'),
            ('성형 직경', '<b>%s</b>' % (ss if not bad else '%s (확인 중)' % band)),
            ('재질', mat_h), ('인덴터 경도', '<b>%s</b>' % hard),
            ('캐비티 깊이', depth if not bad else '문의'),
            ('외형(Φ × L)', dim if not bad else '문의'),
            ('무게', wt if not bad else '문의'),
            ('용도', 'IR(KBr) 펠릿 · XRD 분말 시료 성형')]

    opt = ''
    if d.get('multi'):
        sizes = re.split(r'[、,]', ss.replace('(M)', ''))
        deps = re.split(r'[、,]', depth.replace('(N)', ''))
        dims = re.split(r'[、,]', dim.replace('(L×N)', ''))
        wts = re.split(r'[、,]', wt)
        n = max(len(sizes), len(dims))
        rows = ''.join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            sizes[i].strip() if i < len(sizes) else '—',
            (deps[i] if i < len(deps) else deps[-1]).strip(),
            dims[i].strip() if i < len(dims) else '—',
            wts[i].strip() if i < len(wts) else '—') for i in range(n))
        opt = ('<h2 class="pkg-h">이 밴드의 규격별 치수</h2><div class="pkg-tblwrap">'
               '<table class="pkg-tbl pkg-opt"><thead><tr><th>성형 직경</th><th>캐비티 깊이</th>'
               '<th>외형(Φ × L)</th><th>무게</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
               '<p class="pkg-note">이 밴드는 규격마다 몸통 치수와 무게가 다릅니다. 주문 시 성형 직경을 지정해 주십시오.</p>')

    need_max = t_for(dmax) if dmax else 0
    need_min = t_for(dmin) if dmin else 0
    feats = [
      '<b>%s 밴드</b> — 성형 직경 %s. %s' % (band, ss if not bad else '확인 중',
        'IR(KBr) 분석의 표준인 <b>Φ13 mm</b>가 이 밴드에 들어갑니다.' if has13 else
        ('소구경 미량 시료용입니다.' if dmax and dmax <= 10 else 'XRD 홀더용 대면적 시료에 씁니다.' if dmax >= 26 else '중간 직경대입니다.')),
      '<b>재질 %s</b> — 열처리 후 치수 안정성이 높아 캐비티와 인덴터의 클리어런스가 유지됩니다.' % mat_h.replace('<b>', '').replace('</b>', ''),
      '<b>인덴터 경도 %s</b> — GPa급 성형압에서도 인덴터 단면이 눌리지 않아 펠릿 표면이 평활하게 유지됩니다.' % hard,
      '<b>캐비티 깊이 %s</b> — 분말 충전량에 여유가 있어 두꺼운 펠릿도 성형할 수 있습니다.' % (depth if not bad else '확인 중'),
      '<b>표준 유압 프레스 호환</b> — <a href="/brands/hench/pellet-press-yp-15/">YP 시리즈</a>를 비롯한 수동 유압 펠릿 프레스에 그대로 올려 씁니다.',
    ]
    incl = [('다이 본체 1세트 (캐비티 · 인덴터 · 받침)', 'in', '포함'),
            ('프레스 본체 — 별도 선택', 'ex', '미포함·별매')]

    faqs = [
      ('직경 선택', '%s 밴드는 어떤 분석에 쓰나요?' % band,
       ('FT-IR의 KBr 펠릿은 <b>Φ13 mm가 사실상 표준</b>이며 대부분의 IR 펠릿 홀더가 Φ13 mm 기준입니다. 이 밴드에 Φ13 mm가 포함됩니다.'
        if has13 else
        ('시료량이 극히 적은 마이크로 샘플용입니다. IR 표준 Φ13 mm가 필요하면 '
         '<a href="/brands/hench/cylindrical-die-hmy-11-14/">Φ11–14 밴드</a>를 고르십시오.' if dmax and dmax <= 10 else
         'XRD 홀더용 대면적 분말 시료 성형에 적합합니다. 고압이 필요한 IR 투광용으로는 직경이 커 하중이 모자랍니다.'))),
      ('재질·경도', '재질과 경도가 왜 중요한가요?',
       'KBr 펠릿 성형압은 통상 700 MPa 이상, 즉 <b>0.7 GPa 이상</b>입니다. 일반 공구강은 이 영역에서 인덴터 단면이 미세하게 눌려 '
       '펠릿 표면에 굴곡이 생기고 IR 베이스라인이 흔들립니다. 이 밴드는 <b>%s</b>를 <b>%s</b>로 열처리해 '
       '이 압력대에서 영구변형이 발생하지 않습니다.' % (mat_h.replace('<b>', '').replace('</b>', ''), hard)),
      ('재질·경도', '밴드마다 재질이 다른가요?',
       '다릅니다. <b>Φ3–10 mm 소구경 밴드는 일본산 고속도 공구강 ASSAB+17 · HRC68~70</b>이고, '
       '<b>Φ15 mm 이상 밴드는 합금공구강 Cr12MoV · HRC68~62</b>입니다. 소구경일수록 단위면적당 압력이 높아 더 단단한 강재를 씁니다. '
       '카탈로그에 한 재질만 적힌 자료가 돌아다니니 밴드별로 확인하십시오.'),
      ('프레스 호환', '이 밴드를 쓰려면 몇 톤짜리 프레스가 필요한가요?',
       ('성형압 700 MPa 기준으로 이 밴드의 최소 직경 Φ%.0f mm에 <b>약 %.1f T</b>, 최대 직경 Φ%.0f mm에 <b>약 %.1f T</b>가 필요합니다. %s'
        % (dmin, need_min, dmax, need_max,
           ('<a href="/brands/hench/pellet-press-yp-15/">YP-15</a>(15 T)로 밴드 전체를 소화합니다.' if need_max <= 15 else
            'YP-15(15 T)로는 Φ%.0f mm까지가 한계이므로, 더 큰 직경은 상위 톤수 프레스가 필요하거나 저압(XRD용) 성형 전제로 쓰셔야 합니다.'
            % H.max_dia(15, MPA)))
        if nums else '이 밴드의 치수가 확정되면 필요 톤수를 계산해 안내드립니다.')),
      ('치수', '프레스 유효공간에 들어가나요?',
       ('외형이 <b>%s</b>입니다. YP-3·YP-5의 유효공간 90×120 mm, YP-12·YP-15의 92×130 mm, '
        'YP-15B의 140×150 mm와 대조해 확인하십시오.' % dim) if not bad and dim != '—'
       else '이 밴드의 외형 치수는 확인 후 안내드립니다.'),
      ('용도 구분', 'XRD용과 IR용 다이가 다른가요?',
       '원통형 HMY는 두 용도 모두 대응합니다. 차이는 운용 조건입니다 — IR은 투광이 목적이라 고압·유지 시간이 필요하고, '
       'XRD는 표면 평탄도가 목적이라 저압으로 충분합니다. 형광 분석용 등 특수 형상이 필요하면 별도 다이로 문의해 주십시오.'),
      ('관리', '청소와 보관은 어떻게 하나요?',
       'KBr은 흡습성이 강해 잔류 분말이 캐비티에 남으면 부식과 고착의 원인이 됩니다. 사용 후 무수 알코올로 닦고 완전히 건조한 뒤 '
       '데시케이터 또는 건조 보관하십시오. 인덴터 단면에 흠집이 생기면 펠릿 표면에 그대로 전사됩니다.'),
      ('구성', '프레스가 포함되나요?',
       '포함되지 않습니다. 다이는 단품이며 프레스는 <a href="/brands/hench/pellet-press-yp-15/">수동 유압 펠릿 프레스 YP 시리즈</a>에서 '
       '별도로 고르십시오. 다이와 프레스를 함께 구성해 견적하실 수 있습니다.'),
    ]
    notes = ['다이는 단품 판매되며 <b>프레스는 포함되지 않습니다.</b> 사용 전 프레스의 최대 하중이 목표 성형압 × 펠릿 단면적을 충족하는지 확인하십시오.']
    if bad: notes.append('<b>제조사 자료 이상</b> — ' + bad)

    if d.get('multi'):
        models = [{"m": 'HMY %s' % x.strip(), "s": band} for x in re.split(r'[·、,]', ss) if x.strip()]
    elif bad:
        models = [{"m": 'HMY %s' % band, "s": '치수 확인 중'}]
    else:
        models = [{"m": 'HMY %s' % x.strip(), "s": '캐비티 깊이 %s · 외형 %s' % (depth, dim)}
                  for x in re.split(r'[·、,]', ss.replace('mm', '')) if x.strip()]
    return dict(
      models=models,
      slug=slug, crumb='원통형 펠릿 다이',
      title='Hench HMY %s 원통형 펠릿 다이 — KBr·XRD 시료 성형 몰드 | 실험셋업연구소' % band,
      desc='Hench HMY 원통형 펠릿 다이 %s — 재질 %s, 인덴터 경도 %s, 캐비티 깊이 %s, 외형 %s. IR(KBr)·XRD 분말 시료 성형용, 유압 펠릿 프레스 호환. 구성별 견적.'
           % (band, mat_en or '문의', hard, depth if not bad else '문의', dim if not bad else '문의'),
      h1='원통형 펠릿 다이 HMY %s' % band,
      ans='분말 시료를 원판 펠릿으로 눌러 만드는 성형 몰드입니다. %s 밴드로, 인덴터를 %s로 잡아 KBr 펠릿에 필요한 GPa급 성형압에서도 눌리지 않습니다.' % (band, hard),
      summ='성형 직경 <b>%s</b> · 재질 %s · 인덴터 경도 <b>%s</b> · 캐비티 깊이 %s · 외형 %s · 무게 %s'
           % (ss if not bad else band + ' (치수 확인 중)', mat_h.replace('<b>', '').replace('</b>', ''),
              hard, depth if not bad else '문의', dim if not bad else '문의', wt if not bad else '문의'),
      quote='Hench 원통형 펠릿 다이 HMY %s' % band,
      kws=[('/brands/hench/pellet-press-yp-15/', '#펠릿프레스'), ('/product/', '#실험장비카탈로그'),
           ('/brands/hench/%s/' % slug, '#펠릿다이'), ('/brands/hench/%s/' % slug, '#KBr다이'),
           ('/brands/hench/%s/' % slug, '#XRD시료다이')],
      img=img,
      thumbs=[(img, 'HMY', '다이 세트'), ('/img/hench/%s-2.jpg' % slug, 'HMY', '분해 구성'),
              ('/img/hench/%s-3.jpg' % slug, 'HMY', '성형·탈형')],
      feats=feats, incl=incl, spec=spec, opt_tbl=opt, figures=[],
      price='밴드·직경·수량에 따라 <b>구성별 견적(문의)</b>입니다. 시료 종류와 목표 펠릿 직경을 알려주시면 '
            '밴드와 프레스 톤수를 함께 잡아 견적해 드립니다.',
      notes=notes,
      warn_h='안전 — 밴드별 허용 하중이 다릅니다',
      warn_p='소구경 다이에 프레스 최대 하중을 그대로 가하면 시료면 압력이 <b>수 GPa</b>에 달해 인덴터·캐비티가 손상될 수 있습니다. '
             '인덴터와 캐비티 사이에 분말이 끼면 스커핑이 발생하므로 매 사용 후 청소하십시오.',
      xlinks=others, faqs=faqs,
      ld={"@context": "https://schema.org", "@type": "Product",
          "name": "HMY Cylindrical Pellet Dies %s" % band.replace('–', '-'),
          "brand": {"@type": "Brand", "name": "Hench", "alternateName": ["HENCH", "天津恒创立达"]},
          "category": "시료 전처리 · 펠릿 다이",
          "url": 'https://rndsetup.com/brands/hench/%s/' % slug,
          "image": 'https://rndsetup.com' + img, "model": "HMY",
          "material": mat_en or None},
      _ids=ids(r))


# ══════════════════════ 브랜드 허브 (모델별 dscard) ══════════════════════
HUB_STYLE = ('<style>.dsgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:20px 0 8px}'
 '@media(max-width:900px){.dsgrid{grid-template-columns:repeat(2,1fr)}}'
 '@media(max-width:560px){.dsgrid{grid-template-columns:1fr}}'
 '.dscard{border:1px solid #ECECEC;border-radius:14px;overflow:hidden;background:#fff}'
 '.dscard-im{position:relative;background:#F6F7F8}.dscard-im img{width:100%;height:auto;display:block}'
 '.dscard-bdg{position:absolute;left:10px;top:10px}'
 '.dscard-bdg .b{font-size:11.5px;font-weight:800;color:#fff;background:rgba(59,54,149,.9);border-radius:20px;padding:4px 11px}'
 '.dscard-bd{padding:13px 15px 15px}.dscard-mdl{font-size:15.5px;font-weight:800;margin:0 0 5px;line-height:1.35}'
 '.dscard-link{color:#3B3695;text-decoration:none}.dscard-link:hover{text-decoration:underline}'
 '.dscard-nm{font-size:11.5px;color:#6B6B6B;margin:0 0 8px}'
 '.dscard-d{font-size:12.5px;color:#5a6570;line-height:1.6;margin:0}'
 '.dscard-p{font-size:12.5px;font-weight:800;color:#0F69AF;margin:8px 0 0}'
 '.gu-links{margin:6px 0 0 18px}.gu-links li{font-size:14px;line-height:1.9}'
 '.gu-links a{color:#3B3695;font-weight:600}</style>')


def hub(cards):
    body = ''
    for c in cards:
        body += ('<article class="dscard" data-cat="%(cat)s" data-text="%(text)s">\n'
          '  <div class="dscard-im"><img src="%(img)s" alt="%(title)s — Hench" loading="lazy" width="760" height="570" '
          'onerror="this.closest(\'.dscard-im\').style.display=\'none\'">'
          '<div class="dscard-bdg"><span class="b">%(bdg)s</span></div></div>\n'
          '  <div class="dscard-bd">\n'
          '    <h3 class="dscard-mdl"><a class="dscard-link" href="%(href)s">%(title)s</a></h3>\n'
          '    <div class="dscard-nm">%(nm)s</div>\n    <p class="dscard-d">%(d)s</p>\n'
          '    <p class="dscard-p">구성별 견적</p>\n  </div>\n</article>\n\n' % c)
    press_li = ''.join('<li><a href="/brands/hench/%s/">%s 수동 유압 펠릿 프레스</a></li>' % (s, n) for s, n in PRESS_ALL)
    die_li = ''.join('<li><a href="/brands/hench/%s/">원통형 다이 HMY %s</a></li>' % (s, b) for s, b in DIE_ALL)
    return ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
      '<meta http-equiv="refresh" content="0;url=/product/">\n<meta name="robots" content="noindex">\n'
      '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
      '<title>Hench(헨치) 펠릿 프레스·펠릿 다이 — IR·XRD 시료 압편 | 실험셋업연구소</title>\n'
      '<meta name="description" content="Hench(천진항창립달) 수동 유압 펠릿 프레스 YP 6종(3~15 T)과 원통형 펠릿 다이 HMY 11밴드(Φ3~150 mm). IR(KBr)·XRD 분말 시료 압편 장비 국내 안내·견적.">\n'
      '<link rel="canonical" href="https://rndsetup.com/brands/hench/">\n'
      + H.HEADCSS + H.EXTRA + HUB_STYLE + '</head>\n<body>\n<div id="pumplab-header"></div>\n'
      '<section class="detail-top"><div class="wrap">'
      '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › Hench</div>\n'
      '<div class="dt-info" style="max-width:820px">\n<div class="dt-brand">' + H.BRANDLINE + '</div>\n'
      '<h1 class="dt-name">Hench — IR·XRD 시료 압편 장비</h1>\n'
      '<p class="dt-ans">Hench(헨치)는 분말 시료를 IR·XRD 측정용 펠릿으로 성형하는 유압 프레스와 다이를 만드는 제조사입니다. '
      '프레스 1대 + 목표 직경의 다이 1개를 한 세트로 구성해 씁니다.</p>\n'
      '<p class="dt-sum"><b>수동 유압 펠릿 프레스 YP</b> 3·5·12·15 T 6종 · <b>원통형 펠릿 다이 HMY</b> Φ3~150 mm 11밴드 · 구성별 견적</p>\n'
      '<button type="button" class="qbtn" data-quote="Hench 펠릿 프레스·다이">견적문의</button>\n</div>\n</div></section>\n'
      '<section class="pkg"><div class="wrap"><a class="ds-back" href="/product/">← 실험장비 통합 카탈로그</a>\n'
      '<h2 class="pkg-h">수동 유압 펠릿 프레스 YP (6종)</h2><ul class="gu-links">' + press_li + '</ul>\n'
      '<h2 class="pkg-h">원통형 펠릿 다이 HMY (11밴드)</h2><ul class="gu-links">' + die_li + '</ul>\n'
      '<div class="dsgrid">\n' + body + '</div>\n'
      '<p class="pkg-note" style="margin-top:18px">표기 구성은 <b>부가세(VAT) 별도</b>이며, 제조사 홈페이지에 정가가 공개되지 않은 품목이라 '
      '<b>가격은 전부 구성별 견적</b>으로 안내합니다. 해외 발주 제품이라 해외배송비가 주문당 1회 더해집니다. 납기는 주문 확정 후 안내드립니다.</p>\n'
      '</div></section>\n' + H.CTBAR + '\n' + H.FOOT)


def main():
    cards, total = [], 0
    for p in PRESS:
        pg = press_page(p); n = H.write(pg['slug'], H.render(pg)); total += n
        cards.append(dict(cat='pellet', img=pg['img'], bdg='펠릿 프레스', href='/brands/hench/%s/' % pg['slug'],
            title=pg['h1'], nm=p['model'],
            d=re.sub(r'<[^>]+>', '', pg['ans'])[:110],
            text=('%s %s 수동 유압 펠릿 프레스 manual hydraulic pellet press %s 펠릿프레스 압편기 시료 압편 '
                  'kbr 펠릿 ir 시료 전처리 xrd 분말 성형 유압프레스 %dt 프레스 버튼셀 몰드 hench 헨치 천진항창립달'
                  % (pg['h1'], p['model'], pg['slug'], p['ton'])).lower()))
        print('  %-34s %6d bytes' % (pg['slug'], n))
    for d in DIES:
        pg = die_page(d); n = H.write(pg['slug'], H.render(pg)); total += n
        cards.append(dict(cat='die', img=pg['img'], bdg='펠릿 다이', href='/brands/hench/%s/' % pg['slug'],
            title=pg['h1'], nm='HMY · %s' % d['band'],
            d=re.sub(r'<[^>]+>', '', pg['ans'])[:110],
            text=('%s hmy 원통형 펠릿 다이 cylindrical dies %s 펠릿 다이 성형 몰드 kbr 다이 ir 펠릿 몰드 '
                  'xrd 시료 다이 시료 전처리 assab+17 cr12mov 인덴터 hench 헨치 천진항창립달'
                  % (pg['h1'], pg['slug'])).lower()))
        print('  %-34s %6d bytes' % (pg['slug'], n))
    hp = os.path.join(H.ROOT, 'brands', 'hench', 'index.html')
    io.open(hp, 'w', encoding='utf-8', newline='\n').write(hub(cards))
    print('  %-34s %6d bytes (dscard %d장)' % ('index.html(허브)', os.path.getsize(hp), len(cards)))
    print('총 %d장 · %.1f KB' % (len(cards), total / 1024))


if __name__ == '__main__':
    main()
