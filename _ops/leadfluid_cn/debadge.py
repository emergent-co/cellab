# -*- coding: utf-8 -*-
"""제조사 제품 사진 좌상단에 합성된 중국어 빨간 배지를 지운다.
배지는 흰 배경 위 고정 위치(대략 x 0.21~0.33W, y 0.14~0.25H)에 있다.
주변이 흰색일 때만 지운다 — 제품 위에 걸치면 건드리지 않는다.
"""
import os, sys
from PIL import Image, ImageDraw
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else '_ops/leadfluid_cn/phase2_raw'
def run(src, dst=None, report=True):
    dst = dst or src
    hit = skip = 0
    for f in sorted(os.listdir(src)):
        if not f.endswith('.jpg'):
            continue
        im = Image.open(os.path.join(src, f)).convert('RGB')
        a = np.asarray(im).astype(int)
        H, W, _ = a.shape
        x0, x1 = int(W*0.19), int(W*0.35)
        y0, y1 = int(H*0.12), int(H*0.27)
        sub = a[y0:y1, x0:x1]
        R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
        m = (R > 140) & (G < 95) & (B < 95)
        if m.sum() < 50:
            skip += 1
            continue
        ys, xs = np.nonzero(m)
        bx0, bx1 = x0 + int(xs.min()) - 12, x0 + int(xs.max()) + 12
        by0, by1 = y0 + int(ys.min()) - 12, y0 + int(ys.max()) + 12
        # 주변 테두리가 흰색인지 확인 (제품 위면 건드리지 않는다)
        ring = []
        if by0-8 >= 0: ring.append(a[by0-8:by0, bx0:bx1].reshape(-1, 3))
        if by1+8 < H:  ring.append(a[by1:by1+8, bx0:bx1].reshape(-1, 3))
        if bx1+8 < W:  ring.append(a[by0:by1, bx1:bx1+8].reshape(-1, 3))
        if not ring:
            skip += 1; continue
        rr = np.concatenate(ring)
        if rr.mean() < 232:
            skip += 1; continue
        ImageDraw.Draw(im).rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255))
        im.save(os.path.join(dst, f), quality=90)
        hit += 1
    if report:
        print('배지 제거 %d장 · 건드리지 않음 %d장' % (hit, skip))
    return hit, skip

if __name__ == '__main__':
    run(SRC)
