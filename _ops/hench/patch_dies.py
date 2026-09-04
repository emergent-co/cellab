# -*- coding: utf-8 -*-
"""gen_models.py 의 원통형 다이(HMY) 부분을 중문 기준으로 정정한다.
- 재질/경도: 영문판 ASSAB+17·Cr12MoV / HRC68~70 -> 중문판 9Cr18 / HRC58
- Φ11–14 밴드: '복사 오류' 처리를 걷어낸다(중문은 Φ7–14가 한 밴드, Φ12.7·Φ13 명시)
- 시료 치수: 중문 밴드 전체 목록에서 이 페이지 밴드 구간만 남긴다
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'gen_models.py')
s = io.open(p, encoding='utf-8').read()

# 1) Φ11–14 밴드의 bad 처리 제거
s = re.sub(r"\s*bad='제조사 상세페이지의 사양표에[\s\S]*?추정값을 싣지 않습니다\.'\),",
           "),", s)

# 2) material_of: CSV(중문 반영본)에서 그대로 읽는다
s = s.replace('''def material_of(r):
    sp = json.loads(r['spec']); blob = ' '.join(list(sp.keys()) + list(sp.values()))
    if 'ASSAB' in blob: return '일본산 고속도 공구강 <b>ASSAB+17</b>', 'Japan High Speed Tool Steel ASSAB+17'
    if 'Cr12MoV' in blob: return '합금공구강 <b>Cr12MoV</b>', 'Alloy tool steel Cr12MoV'
    return '—', '' ''' .rstrip(), '''def material_of(r):
    """중문 제조사 표기를 그대로 쓴다. 영문판의 ASSAB+17/Cr12MoV·HRC68~70 표기는 중문판과 충돌해 채택하지 않는다."""
    m = S(r, 'Material')
    if m == '—':
        return '—', ''
    if '9Cr18' in m:
        return '마르텐사이트계 스테인리스 공구강 <b>9Cr18</b>', '9Cr18'
    return '<b>%s</b>' % m, m''')

# 3) 밴드 구간만 남기는 필터
s = s.replace('''def die_page(d):
    r = row_by_name(d['frag']); slug, band = d['slug'], d['band']
    ss = S(r, 'Sample size')''', '''def band_range(band):
    n = [float(x) for x in re.findall(r'(\\d+(?:\\.\\d+)?)', band)]
    return (min(n), max(n)) if n else (0.0, 1e9)


def narrow(ss, band):
    """중문은 밴드를 넓게 묶는다(예: HMY-B = Φ7–14). 이 페이지 밴드 구간만 남긴다."""
    lo, hi = band_range(band)
    parts = [x.strip() for x in re.split(r'[、,·]', ss.replace('mm', '')) if x.strip()]
    keep = []
    for x in parts:
        m = re.search(r'(\\d+(?:\\.\\d+)?)', x)
        if m and lo - 0.001 <= float(m.group(1)) <= hi + 0.001:
            keep.append('Φ' + m.group(1))
    return ' · '.join(keep) + ' mm' if keep else ss


def die_page(d):
    r = row_by_name(d['frag']); slug, band = d['slug'], d['band']
    ss = S(r, 'Sample size')
    if not d.get('multi'):
        ss = narrow(ss, band)''')

# 4) 밴드별 재질이 다르다는 FAQ -> 중문 기준으로 교체
s = s.replace('''      ('재질·경도', '밴드마다 재질이 다른가요?',
       '다릅니다. <b>Φ3–10 mm 소구경 밴드는 일본산 고속도 공구강 ASSAB+17 · HRC68~70</b>이고, '
       '<b>Φ15 mm 이상 밴드는 합금공구강 Cr12MoV · HRC68~62</b>입니다. 소구경일수록 단위면적당 압력이 높아 더 단단한 강재를 씁니다. '
       '카탈로그에 한 재질만 적힌 자료가 돌아다니니 밴드별로 확인하십시오.'),''',
'''      ('재질·경도', '밴드마다 재질이 다른가요?',
       '제조사 중문 사양서 기준으로 <b>HMY 전 밴드가 9Cr18 · 압두 경도 HRC58</b>로 동일합니다. '
       '제조사 영문 페이지에는 소구경 밴드가 ASSAB+17 · HRC68~70, 대구경 밴드가 Cr12MoV로 적혀 있으나 '
       '중문 사양서와 일치하지 않습니다. 더 높은 경도가 필요하면 '
       '<a href="/brands/hench/hard-alloy-die-hmw-a-7-10/">초경합금 다이(HMW)</a>를 고르십시오. '
       '재질 지정이 필요한 경우 발주 전에 제조사에 확인해 드립니다.'),''')

# 5) 경도 관련 서술 완화(HRC58 기준)
s = s.replace("'<b>인덴터 경도 %s</b> — GPa급 성형압에서도 인덴터 단면이 눌리지 않아 펠릿 표면이 평활하게 유지됩니다.' % hard",
              "'<b>압두 경도 %s</b> — 담금질된 스테인리스 공구강이라 반복 가압에서 캐비티 마모가 느립니다. 더 높은 경도가 필요하면 초경합금(HMW) 다이를 쓰십시오.' % hard")
s = s.replace('''       'KBr 펠릿 성형압은 통상 700 MPa 이상, 즉 <b>0.7 GPa 이상</b>입니다. 일반 공구강은 이 영역에서 인덴터 단면이 미세하게 눌려 '
       '펠릿 표면에 굴곡이 생기고 IR 베이스라인이 흔들립니다. 이 밴드는 <b>%s</b>를 <b>%s</b>로 열처리해 '
       '이 압력대에서 영구변형이 발생하지 않습니다.' % (mat_h.replace('<b>', '').replace('</b>', ''), hard)),''',
'''       'KBr 펠릿 성형압은 통상 700 MPa 이상, 즉 <b>0.7 GPa 이상</b>입니다. 압두 단면이 눌리면 그 굴곡이 펠릿 표면에 그대로 전사되어 '
       'IR 베이스라인이 흔들립니다. 이 다이는 <b>%s</b>를 <b>%s</b>로 열처리한 것으로, 표준 KBr 성형 조건을 전제로 설계돼 있습니다. '
       '초고압 반복 사용이 전제라면 초경합금(HMW) 다이를 권합니다.' % (mat_h.replace('<b>', '').replace('</b>', ''), hard)),''')

io.open(p, 'w', encoding='utf-8').write(s)
print('gen_models.py 정정 완료')
