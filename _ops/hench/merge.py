# -*- coding: utf-8 -*-
"""EN 119종(hench_products.csv) x CN 155종(hench_cn.json) 병합 -> hench_master.json
- 슬러그: 이미 배포된 119종은 fam.py 결과 그대로 고정(URL 불변)
- 사양: 중문 우선(자기정합·최신 리비전), 중문에 없는 항목만 영문 보충
- 번역 안 되는 값은 싣지 않는다(추정 금지)
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cn_ko

# 재실행 대비: fam 이 항상 영문 원본을 보게 되돌린다
_src = os.path.join(HERE, 'hench_products.csv')
_bak = os.path.join(HERE, 'hench_products_en.csv')
if os.path.exists(_bak):
    io.open(_src, 'w', encoding='utf-8-sig', newline='').write(
        io.open(_bak, encoding='utf-8-sig').read())

import fam as FAM

CN = json.load(io.open(os.path.join(HERE, 'hench_cn.json'), encoding='utf-8'))


def cn_model(o):
    m = (o['kv'].get('仪器型号') or o['kv'].get('型号') or '').strip()
    m = re.split(r'[\s一-鿿]', m)[0].strip()
    if not m:
        g = re.search(r'([A-Z]{2,5}[A-Z0-9]*(?:-[A-Z0-9/\.]+)?)\s*$', o.get('title') or '')
        m = g.group(1) if g else ''
    return m


def norm(m):
    return re.sub(r'[\s]', '', (m or '')).upper()


CNBY = {}
for o in CN:
    o['m'] = cn_model(o)
    if o['m']:
        CNBY.setdefault(norm(o['m']), o)
        CNBY.setdefault(norm(o['m'].split('/')[0]), o)
        g = re.match(r'^([A-Z]{2,4}-[A-Z0-9]{1,4}?)(?:\d{3})?$', norm(o['m'].split('/')[0]))
        if g:
            CNBY.setdefault(g.group(1), o)

# 영문 모델 표기 -> 중문 모델 (수동 대응표)
ALIAS = {
    'YP-12J/ S': 'YP-12J/S', 'YP-40J/ S': 'YP-40J/S',
    'YP-60J/ S': 'YP-60J/S', 'YP-30J/ S': 'YP-30J/S',
    'HPC-800D1/D2/DG1/DG2': 'HPC-800DG', 'HPC-800E/F/EG/FG': 'HPC-800E/F',
    'YPH-800D1/D2': 'YPH-800D1/D2/YPH-800DG1/DG2',
    'YPH-800DG1/DG2': 'YPH-800D1/D2/YPH-800DG1/DG2',
    'YPH-800C': 'YPH-800B/C/YPH-800CG', 'YPH-800CG': 'YPH-800B/C/YPH-800CG',
    'YPH-800EYPH-800F': 'YPH-800E/F',
    'HZT-800D1/HZT-800D2': 'HZT-800D1/HZT-800D2',
    'HZT-800DG/HZT-800DG2': 'HZT-800DG/HZT-800DG2',
    'HZT-800E/HZT-800EG': 'HZT-800E', 'HZT-800F/HZT-800FG': 'HZT-800F',
    'HM-2': 'HMB-B', 'HM-12': 'HMB-B',
    'HMS': 'PMS',
    'HPC-800D1/D2/DG1/DG2 ': 'HPC-800DG',
}
# 슬러그 -> 중문 모델(수동)
SLUG_CN = {
    'opening-die-hmk-f-3-10': 'HMK-FA', 'opening-die-hmk-f-11-20': 'HMK-FB',
    'opening-die-hmk-f-21-40': 'HMK-FC', 'opening-die-hmk-f-41-60': 'HMK-FD',
    'opening-die-hmk-f-61-80': 'HMK-FE',
    'special-die-ring-hmo': 'HMO-A', 'special-die-ring-large-hmo': 'HMO-B',
    'special-die-spherical-hmq': 'HMQ-A', 'special-die-spherical-large-hmq': 'HMQ-B',
    'hot-pellet-press-hpc-800d': 'HPC-800DG',
    'hot-die-hch-pb-300': 'HCH-PD', 'hot-die-hch-gb-500-300': 'HCH-GA',
    'button-cell-die-solid-state-hmn-pg': '#9490484',
    'button-cell-die-hmn-c': '#4237125',
    'hard-alloy-die-hmw-a-7-10': 'HMW-A',
    'hard-alloy-die-hmw-a-11-20': 'HMW-B',
    'hard-alloy-die-hmw-a-21-30': 'HMW-C',
    'square-die-hmf-21-40': 'HMF-C',
    'square-die-hmf-41-70': 'HMF-E',
    'square-die-hmf-71-100': 'HMF-G',
    'hot-die-hch-gb-500-300': 'HCH-GD',
    'hot-die-hch-pb-300': 'HCH-PD',
}

# 다이: 영문 밴드 슬러그 -> 중문 모델(모밴드)
DIE_BAND = {
    'cylindrical-die-hmy-3-6': 'HMY-A', 'cylindrical-die-hmy-7-10': 'HMY-B',
    'cylindrical-die-hmy-11-14': 'HMY-B', 'cylindrical-die-hmy-15-19': 'HMY-C',
    'cylindrical-die-hmy-20-25': 'HMY-C', 'cylindrical-die-hmy-26-30': 'HMY-D',
    'cylindrical-die-hmy-31-35': 'HMY-D', 'cylindrical-die-hmy-36-40': 'HMY-D',
    'cylindrical-die-hmy-41-70': 'HMY-E', 'cylindrical-die-hmy-71-100': 'HMY-F',
    'cylindrical-die-hmy-101-150': 'HMY-G',
}
DIE_PREFIX = [
    ('opening-die-hmk-y-3-10', 'HMK-YA'), ('opening-die-hmk-y-11-20', 'HMK-YB'),
    ('opening-die-hmk-yc-21-40', 'HMK-YC'), ('opening-die-hmk-y-41-60', 'HMK-YD'),
    ('opening-die-hmk-y-61-80', 'HMK-YE'),
    ('square-die-hmf-3-10', 'HMF-A'), ('square-die-hmf-11-20', 'HMF-B'),
    ('square-die-hmf-21-30', 'HMF-C'), ('square-die-hmf-31-40', 'HMF-D'),
    ('square-die-hmf-41-80', 'HMF-E'),
    ('hard-alloy-die-hmw-3-10', 'HMW-A'), ('hard-alloy-die-hmw-11-20', 'HMW-B'),
    ('hard-alloy-die-hmw-21-30', 'HMW-C'),
]


def find_cn(o):
    """fam.py 산출 dict 하나에 대응하는 중문 레코드."""
    slug, model, name = o['slug'], (o['model'] or '').strip(), o['name']
    if slug in SLUG_CN:
        t = SLUG_CN[slug]
        if t.startswith('#'):
            for x in CN:
                if x['id'] == t[1:]:
                    return x
            return None
        return CNBY.get(norm(t))
    if slug in DIE_BAND:
        return CNBY.get(norm(DIE_BAND[slug]))
    for pre, cm in DIE_PREFIX:
        if slug.startswith(pre):
            return CNBY.get(norm(cm))
    if slug == 'pellet-press-yp-40' or name.startswith('40T Manual Pellet Press'):
        return CNBY.get('YP-40')   # 영문판이 모델명을 YP-30으로 오기
    if model in ALIAS:
        r = CNBY.get(norm(ALIAS[model]))
        if r:
            return r
    r = CNBY.get(norm(model))
    if r:
        return r
    r = CNBY.get(norm(model.split('/')[0]))
    if r:
        return r
    # 40T Manual Pellet Press -> 중문 YP-40 (영문 표기가 YP-30으로 오기)
    m = re.match(r'(\d+)T Manual Pellet Press$', name)
    if m:
        return CNBY.get('YP-' + m.group(1))
    return None


def ko_spec(cn, en_spec):
    """중문 우선 한국어 사양. 라벨/값 어느 한쪽이라도 번역 불가면 제외."""
    out = []
    seen = set()
    if cn:
        for k, v in cn['kv'].items():
            kk, vv = cn_ko.lab(k), cn_ko.val(v)
            if kk and vv and kk not in seen:
                seen.add(kk)
                out.append((kk, vv))
    return out, seen


def main():
    rows = []
    for o in FAM.out:
        cn = find_cn(o)
        spec, seen = ko_spec(cn, o['row']['spec'])
        rows.append({
            'slug': o['slug'], 'fam': o['fam'], 'name_en': o['name'],
            'model_en': o['model'], 'deployed': True,
            'cn_id': cn['id'] if cn else None,
            'cn_model': cn['m'] if cn else None,
            'cn_title': (cn.get('title') if cn else '') or '',
            'spec_ko': spec,
            'cn_imgs': (cn.get('imgs') if cn else []) or [],
            'en_spec': json.loads(o['row']['spec']),
            'en_imgs': (o['row']['ids'] or '').split(),
        })
    used = {r['cn_id'] for r in rows if r['cn_id']}
    extra = []
    for o in CN:
        if o['id'] in used or not o['m']:
            continue
        spec, _ = ko_spec(o, '{}')
        extra.append({'slug': None, 'fam': None, 'name_en': '', 'model_en': o['m'],
                      'deployed': False, 'cn_id': o['id'], 'cn_model': o['m'],
                      'cn_title': o.get('title') or '', 'spec_ko': spec,
                      'cn_imgs': o.get('imgs') or [], 'en_spec': {}, 'en_imgs': []})
    io.open(os.path.join(HERE, 'hench_master.json'), 'w', encoding='utf-8').write(
        json.dumps({'deployed': rows, 'new': extra}, ensure_ascii=False, indent=1))
    nom = sum(1 for r in rows if not r['cn_id'])
    print('배포 %d종 (중문 미매칭 %d) · 중문 전용 신규 %d종' % (len(rows), nom, len(extra)))
    for r in rows:
        if not r['cn_id']:
            print('  미매칭 %-40s %s' % (r['slug'], r['name_en'][:40]))


if __name__ == '__main__':
    main()
