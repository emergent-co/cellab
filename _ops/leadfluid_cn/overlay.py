# -*- coding: utf-8 -*-
"""제조사 도판의 중국어를 한글로 덮어쓰는 합성기.
원본은 _ops/leadfluid_cn/img_clean2/ 에 그대로 있으므로 언제든 되돌릴 수 있다.
spec: _ops/leadfluid_cn/overlay_spec.json
  "<file>": {"items":[{"box":[x0,y0,x1,y1],"text":"한글","size":20,
                       "align":"center|left","color":"#222","bg":"auto|#fff","rot":0}]}
bg "auto" = 박스 바깥 테두리 색을 표본으로 채운다(회색 패널·빨간 밴드 자동 대응).
"""
import json, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC  = os.path.join(ROOT, '_ops/leadfluid_cn/img_clean2')
DST  = os.path.join(ROOT, 'img/leadfluid')
SPEC = os.path.join(ROOT, '_ops/leadfluid_cn/overlay_spec.json')
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'

def font(sz):
    for idx in (2, 1, 0):
        try:
            return ImageFont.truetype(FONT, sz, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()

def ring_color(a, box, pad=6):
    x0, y0, x1, y1 = box
    H, W, _ = a.shape
    px = []
    if y0 - pad >= 0:  px.append(a[max(0,y0-pad):y0, x0:x1].reshape(-1,3))
    if y1 + pad < H:   px.append(a[y1:y1+pad, x0:x1].reshape(-1,3))
    if x0 - pad >= 0:  px.append(a[y0:y1, max(0,x0-pad):x0].reshape(-1,3))
    if x1 + pad < W:   px.append(a[y0:y1, x1:x1+pad].reshape(-1,3))
    if not px: return (255,255,255)
    p = np.concatenate(px)
    med = np.median(p, axis=0).astype(int)
    return tuple(int(v) for v in med)

def draw_block(im, box, text, size, align, color, rot):
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    if rot:
        tmp = Image.new('RGBA', (h, w), (0,0,0,0))
        d2 = ImageDraw.Draw(tmp)
        f = font(size)
        bb = f.getbbox(text)
        d2.text(((h-(bb[2]-bb[0]))//2 - bb[0], (w-(bb[3]-bb[1]))//2 - bb[1]), text, font=f, fill=color)
        im.paste(tmp.rotate(rot, expand=True), (x0, y0), tmp.rotate(rot, expand=True))
        return
    dr = ImageDraw.Draw(im)
    f = font(size)
    lines = text.split('\n')
    hs = [f.getbbox(l)[3]-f.getbbox(l)[1] for l in lines]
    gap = max(4, size//4)
    th = sum(hs) + gap*(len(lines)-1)
    cy = y0 + max(0, (h-th)//2)
    for l, lh in zip(lines, hs):
        bb = f.getbbox(l); lw = bb[2]-bb[0]
        x = x0 if align == 'left' else (x1-lw if align == 'right' else x0+(w-lw)//2)
        dr.text((x, cy-bb[1]), l, font=f, fill=color)
        cy += lh + gap

def run():
    spec = json.load(open(SPEC, encoding='utf-8'))
    n = 0
    for fn, cfg in spec.items():
        if fn.startswith('_'): continue
        im = Image.open(os.path.join(SRC, fn)).convert('RGB')
        a = np.asarray(im).astype(int)
        dr = ImageDraw.Draw(im)
        for it in cfg['items']:
            box = it['box']
            bg = it.get('bg', 'auto')
            fill = ring_color(a, box) if bg == 'auto' else bg
            dr.rectangle(box, fill=fill)
        a2 = np.asarray(im).astype(int)
        for it in cfg['items']:
            if not it.get('text'): continue
            draw_block(im, it['box'], it['text'], it.get('size', 20),
                       it.get('align', 'center'), it.get('color', '#222222'), it.get('rot', 0))
        im.save(os.path.join(DST, fn), quality=90)
        n += 1
    print('오버레이 합성:', n, '장')

run()
