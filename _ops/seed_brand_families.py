# -*- coding: utf-8 -*-
"""_build/brands.json 의 families[].required_specs 를 실제 페이지에서 산출한다.

필수 사양을 사람이 추측하면 기존 페이지가 무더기로 걸린다.
그래서 "그 제품군에 속한 기존 페이지 전원이 갖고 있는 사양 라벨"을 필수로 삼는다.
= 기준선 위반 0, 앞으로 새 페이지가 빠뜨릴 때만 걸린다.

최초 1회 산출용. 이후에는 brands.json 을 손으로 관리한다
(재실행하면 잘못 만든 페이지 때문에 규칙이 약해질 수 있다).
사용: python _ops/seed_brand_families.py [--write]
"""
import json, os, re, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, '_build', 'brands.json')
SKIP_LABEL = re.compile(r'가격|정가|논문|저널|링크|^규격$|^모델$|^배합$|^포장$|^선택$|^배송$')

# 제품군 = 슬러그 접두. 실제 클러스터에 맞춰 좁게 잡는다.
FAMILIES = {
    'hench': ['cylindrical-die', 'opening-die-hmk-f', 'opening-die-hmk-y', 'square-die',
              'hot-die', 'hard-alloy-die', 'special-die', 'button-cell-die',
              'pellet-press-yp', 'digital-pellet-press', 'automatic-pellet-press',
              'electric-pellet-press', 'hot-pellet-press', 'isostatic-press', 'fluorometer-press'],
    'gaossunion': ['glass-cell', 'quartz-cell', 'membrane-cell', 'corrosion-cell', 'mea-cell',
                   'battery-cell', 'photo-cell', 'insitu-cell', 'high-pressure-cell',
                   'gas-diffusion-cell', 'special-cell'],
    'aida': ['photo-cell', 'h-cell', 'membrane-cell'],
}


def labels(path):
    s = open(path, encoding='utf-8').read()
    if 'class="dt-name"' not in s:
        return None
    body = s.split('<body>', 1)[-1]
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    out = set()
    for l in re.findall(r'<th[^>]*>([^<]{1,24})</th>', body):
        l = l.strip()
        if l and not SKIP_LABEL.search(l):
            out.add(l)
    return out


def main():
    data = json.load(open(BP, encoding='utf-8'))
    for brand, prefixes in FAMILIES.items():
        pages = {}
        for p in sorted(glob.glob(os.path.join(ROOT, 'brands', brand, '*', 'index.html'))):
            slug = os.path.basename(os.path.dirname(p))
            lab = labels(p)
            if lab is not None:
                pages[slug] = lab
        fams, used = {}, set()
        for pref in sorted(prefixes, key=len, reverse=True):   # 긴 접두 우선
            members = [s for s in pages if s.startswith(pref) and s not in used]
            if len(members) < 2:
                continue
            used.update(members)
            common = set.intersection(*[pages[s] for s in members])
            fams[pref] = {'match': [pref], 'required_specs': sorted(common)}
            print('  %-12s %-24s %3d장 → 필수 %d개 %s'
                  % (brand, pref, len(members), len(common), sorted(common)[:6]))
        # 긴 접두가 먼저 오도록 정렬해서 저장(런타임 match 는 첫 일치가 이긴다)
        data['brands'][brand]['families'] = {
            k: fams[k] for k in sorted(fams, key=len, reverse=True)}
    if '--write' in sys.argv:
        json.dump(data, open(BP, 'w', encoding='utf-8', newline='\n'),
                  ensure_ascii=False, indent=2)
        print('\n_build/brands.json 갱신')
    else:
        print('\n(--write 를 붙이면 저장)')


if __name__ == '__main__':
    main()
