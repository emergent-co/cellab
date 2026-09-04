# -*- coding: utf-8 -*-
"""반영 결과 검산: 압력범위(T·MPa)와 실린더/피스톤 지름이 물리적으로 맞물리는지 본다.
T = MPa x pi d^2/4 / 9806.65
"""
import csv, io, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(io.open(os.path.join(HERE, 'hench_products.csv'), encoding='utf-8-sig')))

def num(s):
    m = re.search(r'(\d+(?:\.\d+)?)', s or '')
    return float(m.group(1)) if m else None

ok = bad = skip = 0
out = []
for r in rows:
    sp = json.loads(r['spec'])
    pr = sp.get('Pressure range') or ''
    d = sp.get('Cylinder diameter') or sp.get('Piston diameter') or ''
    mt = re.search(r'(\d+(?:\.\d+)?)\s*T', pr)
    mp = re.search(r'(\d+(?:\.\d+)?)\s*MPa', pr, re.I)
    dd = num(d)
    if 'Sealing pressure' in sp or 'N' == (r['model'] or '')[-1:] or (r['model'] or '').endswith(('2N', '2NS')):
        skip += 1        # 버튼셀 실링기: 표기 T 는 실링 정격이지 실린더 최대치가 아니다
        continue
    if not (mt and mp and dd):
        skip += 1
        continue
    t, p = float(mt.group(1)), float(mp.group(1))
    calc = p * math.pi * dd ** 2 / 4.0 / 9806.65
    err = abs(calc - t) / t
    if err <= 0.15:
        ok += 1
    else:
        bad += 1
        out.append('  %-12s %-20s Φ%-6s 표기 %.1fT vs 계산 %.1fT (%.0f%% 차)'
                   % (r['model'], pr, d, t, calc, err * 100))
print('압력×실린더 검산: 일치 %d · 불일치 %d · 대상아님 %d' % (ok, bad, skip))
for x in out:
    print(x)

# 페이지 대비 사양표 필드 수
thin = [r['model'] for r in rows if len(json.loads(r['spec'])) < 3]
print('사양 3항목 미만:', thin)
