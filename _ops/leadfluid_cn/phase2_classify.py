# -*- coding: utf-8 -*-
"""기존 62종 보강용 CN 이미지 자동 분류.
제품컷(썸네일 후보) vs 도판(본문 후보) 을 나누고, 도판은 종류를 추정한다.
판정 근거를 함께 출력해 사람이 컨택트시트로 검수할 수 있게 한다.
출력: _ops/leadfluid_cn/phase2_class.json
"""
import os, json, collections
from PIL import Image
import numpy as np

RAW = '_ops/leadfluid_cn/phase2_raw'
OUT = '_ops/leadfluid_cn/phase2_class.json'

def feats(p):
    im = Image.open(p).convert('RGB')
    a = np.asarray(im).astype(int)
    H, W, _ = a.shape
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    red = (R > 150) & (G < 110) & (B < 110)
    band = int((red.mean(axis=1) > 0.30).sum())          # 빨간 제목 밴드 줄 수
    g = a.mean(axis=2)
    core = g[int(H*.06):int(H*.94), int(W*.06):int(W*.94)]
    dark = core < 150
    trans = 0
    for y in range(0, core.shape[0], 3):
        trans += int((np.diff(dark[y].astype(int)) == 1).sum() >= 6)   # 글자줄
    white = float((g > 235).mean())
    ink = float(dark.mean())
    return band, trans, white, ink

def main():
    rows = []
    for f in sorted(os.listdir(RAW)):
        if not f.endswith('.jpg'):
            continue
        band, trans, white, ink = feats(os.path.join(RAW, f))
        if band >= 8 or trans >= 20:
            kind = 'fig'                      # 표·도해·치수도 (제목 밴드 또는 글자줄 많음)
        elif ink < 0.004 and trans < 6:
            kind = 'product'                  # 흰 배경에 피사체 하나
        else:
            kind = 'product' if trans < 12 else 'fig'
        rows.append({'file': f, 'slug': f.split('__')[0], 'kind': kind,
                     'band': band, 'textrows': trans, 'white': round(white, 3), 'ink': round(ink, 4)})
    json.dump(rows, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = collections.Counter(r['kind'] for r in rows)
    print('분류:', dict(c), '/ 총', len(rows))
    per = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        per[r['slug']][0 if r['kind'] == 'product' else 1] += 1
    noprod = [s for s, v in per.items() if v[0] == 0]
    print('제품컷 0장인 모델:', len(noprod), noprod[:10])
    print('제품당 평균 제품컷 %.1f · 도판 %.1f'
          % (sum(v[0] for v in per.values())/len(per), sum(v[1] for v in per.values())/len(per)))

main()
