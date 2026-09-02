# -*- coding: utf-8 -*-
"""Hench 119종 군 분류 + 슬러그 확정. 슬러그는 모델코드가 아니라 제품명(톤수·직경밴드)에서 만든다."""
import csv, json, io, re, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(io.open(os.path.join(HERE, 'hench_products.csv'), encoding='utf-8-sig')))

DONE = {  # 1차로 이미 올린 17장
 'pellet-press-yp-3','pellet-press-yp-5','pellet-press-yp-12','pellet-press-yp-15',
 'pellet-press-yp-15b','pellet-press-yp-15r',
 'cylindrical-die-hmy-3-6','cylindrical-die-hmy-7-10','cylindrical-die-hmy-11-14',
 'cylindrical-die-hmy-15-19','cylindrical-die-hmy-20-25','cylindrical-die-hmy-26-30',
 'cylindrical-die-hmy-31-35','cylindrical-die-hmy-36-40','cylindrical-die-hmy-41-70',
 'cylindrical-die-hmy-71-100','cylindrical-die-hmy-101-150'}

def famof(r):
    n = r['name']; nl = n.lower()
    if r['cat'] == '기타': return 'Z-slicer'
    if r['cat'] == '프레스':
        if 'isostatic' in nl:  return 'P5-isostatic'
        if 'hot' in nl or '°c' in nl or '℃' in nl: return 'P6-hot'
        if 'fluorometer' in nl: return 'P7-fluoro'
        if 'battery sealing' in nl: return 'P8-cellseal'
        if 'digital' in nl:    return 'P2-digital'
        if 'automatic' in nl:  return 'P4-auto'
        if 'electric' in nl:   return 'P3-electric'
        return 'P1-manual'
    if 'hot dies' in nl or ('°c' in nl and 'die' in nl): return 'D6-hotdie'
    if 'battery' in nl or 'solid state' in nl: return 'D7-cellmold'
    if 'fluorometer' in nl: return 'D8-fluorodie'
    if 'hard alloy' in nl:  return 'D5-carbide'
    if 'opening' in nl:     return 'D2-opening'
    if 'square' in nl:      return 'D3-square'
    if 'cylindrical dies' in nl: return 'D1-cylindrical'
    return 'D4-special'

PREFIX = {'P1-manual':'pellet-press','P2-digital':'digital-pellet-press','P3-electric':'electric-pellet-press',
 'P4-auto':'automatic-pellet-press','P5-isostatic':'isostatic-press','P6-hot':'hot-pellet-press',
 'P7-fluoro':'fluorometer-press','P8-cellseal':'button-cell-sealer','Z-slicer':'electrode-slicer',
 'D1-cylindrical':'cylindrical-die','D2-opening':'opening-die','D3-square':'square-die',
 'D4-special':'special-die','D5-carbide':'hard-alloy-die','D6-hotdie':'hot-die',
 'D7-cellmold':'button-cell-die','D8-fluorodie':'fluorometer-die'}

# ── 이미 배포된 페이지: 슬러그 고정. 바꾸면 301이 필요해지므로 절대 재작명 금지 ──
FIXED = {
 '3T Manual Pellet Press':'pellet-press-yp-3','5T Manual Pellet Press':'pellet-press-yp-5',
 '12T Manual Pellet Press':'pellet-press-yp-12',
 'Φ2mmΦ3mmΦ4mmΦ5mmΦ6mm Cylindrical Dies':'cylindrical-die-hmy-3-6',
 'Φ7mmΦ8mmΦ9mmΦ10mm Cylindrical Dies':'cylindrical-die-hmy-7-10',
 'Φ11mmΦ12mmΦ13mmΦ14mm Cylindrical Dies':'cylindrical-die-hmy-11-14',
 'Φ15mmΦ16mmΦ17mmΦ18mmΦ19mm Cylindrical Dies':'cylindrical-die-hmy-15-19',
 'Φ20mmΦ21mmΦ22mmΦ23mmΦ24mmΦ25mm Cylindrical Dies':'cylindrical-die-hmy-20-25',
 'Φ26mmΦ27mmΦ28mmΦ29mmΦ30mm Cylindrical Dies':'cylindrical-die-hmy-26-30',
 'Φ31mmΦ32mmΦ33mmΦ34mmΦ35mm Cylindrical Dies':'cylindrical-die-hmy-31-35',
 'Φ36mmΦ37mmΦ38mmΦ39mmΦ40mm Cylindrical Dies':'cylindrical-die-hmy-36-40',
 'Φ41-Φ70mm Cylindrical Dies':'cylindrical-die-hmy-41-70',
 'Φ71-Φ100mm Cylindrical Dies':'cylindrical-die-hmy-71-100',
 'Φ101-Φ150mm Cylindrical Dies':'cylindrical-die-hmy-101-150',
}
# 15T 3종은 이름이 같아 모델로 구분한다
FIXED_BY_MODEL = {'YP-15':'pellet-press-yp-15','YP-15B':'pellet-press-yp-15b','YP-15R':'pellet-press-yp-15r'}

SPECIAL = {  # D4 이름 → 슬러그 꼬리
 'Ring Dies':'ring-hmo','Bigger Ring Dies':'ring-large-hmo','Spherical Dies':'spherical-hmq',
 'Bigger Spherical Dies':'spherical-large-hmq','Polygon Dies':'polygon-hmd','Anti-cracking Dies':'anti-crack-hml',
 'Bidirectional Press Opening Dies':'bidirectional-hms','Special Shape Dies':'shape-hmt',
 'Cylindrical Dies with Scale':'scale-hmc','13mm IR Dies（No demoulding required）':'ir-hm-2',
 'IR Dies（demoulding）':'ir-hm-12','Boric Acid Dies for Fluorometer':'boric-hmp',
 'Steel Ring Dies for Fluorometer':'steel-ring-hmg','Manual battery slicer':'cms-10',
 'Button Battery Removal Dies':'removal-hmn-b','Solid state battery mold set':'solid-state-hmn-pg'}

def code_of(m, name=''):
    """모델 문자열에서 첫 코드만 뽑는다. 제조사가 2열 표를 한 칸에 붙여 놓은 경우 대비."""
    lead = re.match(r'([A-Z]{2,4}-\d{2,4}[A-Z]?)\s', name or '')
    if lead: return lead.group(1)
    mm = re.match(r'([A-Za-z]{2,4}-?\d{1,4}[A-Za-z]{0,3})', (m or '').strip())
    return mm.group(1) if mm else (m or '')


def tail(r, fam):
    n = r['name']; m = code_of(r['model'], n)
    if n in SPECIAL: return SPECIAL[n]
    if fam.startswith('P'):
        t = re.match(r'(\d+)\s*T', n)
        base = (m or '').lower().replace('（','').replace('）','').replace(' ','')
        base = re.sub(r'[^a-z0-9-]', '', base) or ('t%s' % (t.group(1) if t else 'x'))
        if '4 Columns' in n or '4columns' in n.lower(): base += '-4col'
        if 'Protection' in n: base += '-protection'
        return base
    # 다이: 직경/치수 밴드
    nums = re.findall(r'(\d+)', n.split('(')[0])
    if nums:
        band = '%s-%s' % (nums[0], nums[-1]) if len(nums) > 1 else nums[0]
        code = re.sub(r'[^a-z0-9-]', '', (m or '').lower())
        return '%s-%s' % (code, band) if code else band
    return re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')[:28]

out, seen = [], {}
for r in ROWS:
    f = famof(r)
    fx = FIXED.get(r['name']) or (FIXED_BY_MODEL.get(r['model']) if 'Manual Pellet Press' in r['name'] or '4 Columns' in r['name'] else None)
    s = fx or ('%s-%s' % (PREFIX[f], tail(r, f)))
    s = re.sub(r'-+', '-', s).strip('-')
    if s in seen:
        s2 = s
        k = 2
        while s2 in seen: s2 = '%s-%d' % (s, k); k += 1
        s = s2
    seen[s] = r['name']
    out.append(dict(fam=f, slug=s, name=r['name'], model=r['model'], done=(s in DONE), row=r))

if __name__ == '__main__':
    g = collections.defaultdict(list)
    for o in out: g[o['fam']].append(o)
    tot = new = 0
    for f in sorted(g):
        v = g[f]; nd = [x for x in v if not x['done']]
        tot += len(v); new += len(nd)
        print('\n=== %s  (%d종, 신규 %d) ===' % (f, len(v), len(nd)))
        for x in v[:40]:
            print('   %s %-42s %s' % ('✔' if x['done'] else ' ', x['slug'], x['name'][:44]))
    print('\n총 %d종 · 신규 %d종 · 슬러그 중복 0(자동 회피 포함)' % (tot, new))
