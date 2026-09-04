# -*- coding: utf-8 -*-
"""제조사 도판의 빨간 제목 밴드와 '单位：mm' 라벨을 자동 검출해 한글로 바꾼다.
좌표를 손으로 찍지 않는다 — 밴드는 색으로, 단위 라벨은 밴드 근처 작은 글자덩이로 찾는다.
overlay_spec.json 으로 이미 손본 파일은 건너뛴다(그쪽이 우선).
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC  = os.path.join(ROOT, '_ops/leadfluid_cn/img_clean2')
DST  = os.path.join(ROOT, 'img/leadfluid')
BODY = json.load(open(os.path.join(ROOT, '_ops/leadfluid_cn/img_body.json'), encoding='utf-8'))
SPEC = json.load(open(os.path.join(ROOT, '_ops/leadfluid_cn/overlay_spec.json'), encoding='utf-8'))
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'

def font(sz):
    for i in (2, 1, 0):
        try: return ImageFont.truetype(FONT, sz, index=i)
        except Exception: pass
    return ImageFont.load_default()

def band_box(a):
    R, G, B = a[...,0], a[...,1], a[...,2]
    red = (R > 150) & (G < 110) & (B < 110)
    frac = red.mean(axis=1)
    rows = np.where(frac > 0.30)[0]
    if len(rows) == 0: return None
    y0, y1 = rows.min(), rows.max()
    if y1 - y0 < 8 or y1 - y0 > 70: return None
    cols = np.where(red[y0:y1+1].mean(axis=0) > 0.5)[0]
    if len(cols) < 40: return None
    return [int(cols.min()), int(y0), int(cols.max())+1, int(y1)+1]

def unit_box(a, band):
    """밴드 아래 상단 우측에서 '单位：mm' 같은 작은 글자덩이를 찾는다."""
    H, W, _ = a.shape
    g = a.mean(axis=2)
    y0 = (band[3] + 4) if band else 0
    y1 = min(H, y0 + int(H * 0.16))
    x0 = int(W * 0.52)
    dark = (g[y0:y1, x0:] < 150)
    if dark.sum() < 40: return None
    ys, xs = np.nonzero(dark)
    if len(xs) == 0: return None
    bx0, bx1 = xs.min(), xs.max(); by0, by1 = ys.min(), ys.max()
    w, h = bx1-bx0, by1-by0
    if not (35 < w < 260 and 8 < h < 40): return None
    return [x0+int(bx0)-8, y0+int(by0)-6, x0+int(bx1)+8, y0+int(by1)+6]

TITLE = {'dim': '치수도 · 단위 mm (Dimensions)', 'photo': None, 'diagram': None, 'chart': None}

def run():
    n_b = n_u = 0
    for slug, d in BODY.items():
        if slug == '_doc': continue
        for i, (kind, cap) in d.items():
            if kind == 'table' or not cap: continue
            fn = '%s-%s.jpg' % (slug, i)
            if fn in SPEC: continue
            p = os.path.join(SRC, fn)
            if not os.path.exists(p): continue
            im = Image.open(p).convert('RGB')
            a = np.asarray(im).astype(int)
            bb = band_box(a)
            changed = False
            if bb:
                title = TITLE.get(kind) or re.split(r'\s+—\s+|\s+\(', cap)[0]
                dr = ImageDraw.Draw(im)
                dr.rectangle(bb, fill=(226, 0, 26))
                f = font(max(14, min(20, (bb[3]-bb[1]) - 8)))
                g = f.getbbox(title)
                dr.text((bb[0]+14, bb[1] + ((bb[3]-bb[1]) - (g[3]-g[1]))//2 - g[1]), title, font=f, fill='#FFFFFF')
                changed = True; n_b += 1
            ub = unit_box(np.asarray(im).astype(int), bb)
            if ub and kind == 'dim':
                dr = ImageDraw.Draw(im)
                dr.rectangle(ub, fill=(255,255,255))
                f = font(17)
                g = f.getbbox('단위: mm')
                dr.text((ub[0]+4, ub[1] + ((ub[3]-ub[1])-(g[3]-g[1]))//2 - g[1]), '단위: mm', font=f, fill='#333333')
                changed = True; n_u += 1
            if changed:
                im.save(os.path.join(DST, fn), quality=90)
    print('빨간 밴드 한글화 %d장 · 단위 라벨 %d장' % (n_b, n_u))

run()
