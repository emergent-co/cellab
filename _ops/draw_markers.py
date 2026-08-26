#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""부위 넘버링 마커 — 좌표는 JSON에 두고 사람이 확인·수정한다.

왜 이렇게 하나: 마커 좌표를 모델이 사진을 보고 눈대중으로 찍으면 자주 틀린다
(실제로 C004에서 '염다리'로 단 번호가 F형 가스관 위에 찍혀 있었다). 좌표를 코드에서
분리해 JSON에 두면, 사람이 격자 이미지를 보고 숫자만 고쳐 다시 렌더할 수 있다.

작업 순서:
  1) grid   — 사진에 좌표 격자를 얹어 출력. 사람이 이걸 보고 부위별 (x,y)를 읽는다.
  2) JSON   — 읽은 좌표로 markers.json 작성/수정.
  3) render — JSON대로 마커를 그린다.
  4) proof  — 마커본을 한 장에 모아 검수용 시트로 만든다. 사람이 최종 확인.

사용:
  python draw_markers.py grid   IMGDIR/c001-1.jpg -o /tmp/c001-1_grid.jpg
  python draw_markers.py render markers.json IMGDIR
  python draw_markers.py proof  markers.json IMGDIR -o /tmp/proof.jpg

markers.json 형식:
{
  "c001-1": [
    {"n": 1, "x": 505, "y": 555, "kind": "b", "label": "내부 셀"},
    {"n": 7, "x": 598, "y":  88, "kind": "x", "label": "전극 3종(별매)"}
  ]
}
kind = 구매 범위. b=본체 / d=이 형식만 / o=옵션 / x=미포함·별매
label 은 검수 시트에만 쓰이고 이미지에는 번호만 찍힌다.
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont

COL = {'b': (30, 58, 95), 'd': (13, 110, 110),
       'o': (100, 100, 105), 'x': (178, 34, 34)}
KIND_KO = {'b': '본체 구성', 'd': '이 형식만', 'o': '주문 시 옵션', 'x': '미포함·별매'}
R = 24
# 번호는 숫자만이라 라틴 폰트로 충분하지만, 검수 시트의 라벨은 한글이라 CJK 폰트가 필요하다.
NUM_FONTS = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
KO_FONTS = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc',
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            'C:/Windows/Fonts/malgun.ttf']


def _pick(paths, size, index=None):
    for p in paths:
        if os.path.exists(p):
            try:
                return (ImageFont.truetype(p, size, index=index)
                        if index is not None else ImageFont.truetype(p, size))
            except Exception:
                continue
    return None


def font(size):
    return _pick(NUM_FONTS, size) or ImageFont.load_default()


def kfont(size):
    """한글 라벨용. CJK .ttc 는 한국어 서브폰트를 index 로 고르는데,
    배포판마다 순서가 달라 글리프가 실제로 있는 인덱스를 찾아 쓴다."""
    for p in KO_FONTS:
        if not os.path.exists(p):
            continue
        for idx in ([None] if not p.endswith('.ttc') else [1, 2, 0, 3, 4]):
            try:
                f = (ImageFont.truetype(p, size) if idx is None
                     else ImageFont.truetype(p, size, index=idx))
                if f.getmask('가').getbbox():   # 한글이 실제로 그려지는지 확인
                    return f
            except Exception:
                continue
    return font(size)


def cmd_grid(a):
    """좌표 격자 오버레이 — 사람이 부위별 (x,y)를 읽어내는 용도."""
    im = Image.open(a.image).convert('RGB')
    d = ImageDraw.Draw(im)
    f = font(15)
    step = a.step
    for x in range(0, im.width, step):
        major = (x % (step * 2) == 0)
        d.line([(x, 0), (x, im.height)], fill=(255, 120, 120) if major else (225, 225, 225), width=1)
        if major:
            d.text((x + 3, 3), str(x), font=f, fill=(200, 0, 0))
    for y in range(0, im.height, step):
        major = (y % (step * 2) == 0)
        d.line([(0, y), (im.width, y)], fill=(120, 150, 255) if major else (230, 230, 230), width=1)
        if major:
            d.text((3, y + 3), str(y), font=f, fill=(0, 0, 200))
    out = a.out or os.path.splitext(a.image)[0] + '_grid.jpg'
    im.save(out, 'JPEG', quality=92)
    print('격자 저장:', out)
    print('빨강=X, 파랑=Y (%dpx 간격, 굵은 선은 %dpx)' % (step, step * 2))
    print('이 이미지를 열어 각 부위의 좌표를 읽고 markers.json에 적으세요.')


def draw_one(src, dst, marks):
    im = Image.open(src).convert('RGB')
    d = ImageDraw.Draw(im)
    f = font(30)
    for m in marks:
        x, y, n = m['x'], m['y'], m['n']
        c = COL.get(m.get('kind', 'b'), COL['b'])
        d.ellipse([x - R - 3, y - R - 3, x + R + 3, y + R + 3], fill=(255, 255, 255))
        d.ellipse([x - R, y - R, x + R, y + R], fill=c)
        t = str(n)
        bb = d.textbbox((0, 0), t, font=f)
        d.text((x - (bb[2] - bb[0]) / 2, y - (bb[3] - bb[1]) / 2 - bb[1]),
               t, font=f, fill=(255, 255, 255))
    im.save(dst, 'JPEG', quality=88, optimize=True)
    return im


def check_sequence(marks, base):
    """번호가 1..N 연속인지. 사진에 없는 항목을 번호 목록에 섞으면 건너뛴다."""
    nums = sorted(m['n'] for m in marks)
    if nums != list(range(1, len(nums) + 1)):
        print('  ⚠ %s 번호 불연속: %s — 사진에 없는 항목이 번호 목록에 섞였는지 확인'
              % (base, nums))


def cmd_render(a):
    spec = json.load(open(a.json, encoding='utf-8'))
    for base, marks in spec.items():
        src = os.path.join(a.imgdir, base + '.jpg')
        if not os.path.exists(src):
            print('  [없음]', src); continue
        dst = os.path.join(a.imgdir, base + 'n.jpg')
        draw_one(src, dst, marks)
        check_sequence(marks, base)
        kinds = ''.join(m.get('kind', 'b') for m in sorted(marks, key=lambda z: z['n']))
        print('  %-16s → %-17s 마커 %d개 [%s]'
              % (base + '.jpg', base + 'n.jpg', len(marks), kinds))
    print('\n다음: proof 로 검수 시트를 만들어 사람이 확인하게 하세요.')


def cmd_proof(a):
    """마커본 + 범례 + 라벨을 한 장에 모은 검수 시트."""
    spec = json.load(open(a.json, encoding='utf-8'))
    items = []
    for base, marks in spec.items():
        p = os.path.join(a.imgdir, base + 'n.jpg')
        if os.path.exists(p):
            items.append((base, marks, p))
    if not items:
        print('마커본이 없습니다. render 를 먼저 실행하세요.'); return
    TW, TH, PAD = 460, 345, 14
    # 범례는 마커 수에 따라 늘어난다 (고정 150px 이면 8개짜리에서 마지막 줄이 잘렸다)
    LEG = max(m for m in [150] + [len(mk) * 19 + 34 for _, mk, _ in items])
    cols = min(2, len(items))
    rows = (len(items) + cols - 1) // cols
    Wd = cols * (TW + PAD) + PAD
    Hd = rows * (TH + LEG + PAD) + PAD + 40
    sheet = Image.new('RGB', (Wd, Hd), (250, 250, 249))
    d = ImageDraw.Draw(sheet)
    fh, ft, fs = kfont(19), font(15), kfont(13)
    d.text((PAD, 12), '부위 넘버링 검수 시트 — 번호가 실제 부위에 찍혔는지 확인하세요',
           font=fh, fill=(28, 25, 23))
    for i, (base, marks, path) in enumerate(items):
        cx = PAD + (i % cols) * (TW + PAD)
        cy = 44 + (i // cols) * (TH + LEG + PAD)
        th = Image.open(path).convert('RGB'); th.thumbnail((TW, TH))
        sheet.paste(th, (cx + (TW - th.width) // 2, cy))
        d.text((cx, cy + TH + 4), base + '.jpg', font=ft, fill=(60, 60, 60))
        yy = cy + TH + 26
        for m in sorted(marks, key=lambda z: z['n']):
            c = COL.get(m.get('kind', 'b'), COL['b'])
            d.ellipse([cx, yy, cx + 15, yy + 15], fill=c)
            t = str(m['n']); bb = d.textbbox((0, 0), t, font=fs)
            d.text((cx + 7 - (bb[2] - bb[0]) / 2, yy + 7 - (bb[3] - bb[1]) / 2 - bb[1]),
                   t, font=fs, fill=(255, 255, 255))
            d.text((cx + 21, yy + 1),
                   '%s  · %s' % (m.get('label', ''), KIND_KO.get(m.get('kind', 'b'), '')),
                   font=fs, fill=(55, 55, 55))
            yy += 19
    out = a.out or '/tmp/marker_proof.jpg'
    sheet.save(out, 'JPEG', quality=90)
    print('검수 시트 저장:', out)
    print('사람에게 이 파일을 보내 번호 위치를 확인받으세요. 틀린 건 JSON 좌표만 고쳐 render 재실행.')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('grid'); g.add_argument('image'); g.add_argument('-o', '--out')
    g.add_argument('--step', type=int, default=100); g.set_defaults(fn=cmd_grid)
    r = sub.add_parser('render'); r.add_argument('json'); r.add_argument('imgdir')
    r.set_defaults(fn=cmd_render)
    p = sub.add_parser('proof'); p.add_argument('json'); p.add_argument('imgdir')
    p.add_argument('-o', '--out'); p.set_defaults(fn=cmd_proof)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
