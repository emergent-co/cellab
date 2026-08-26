#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카탈로그 PDF → 제품 이미지 추출 (SMask 합성 · 트림 · 4:3 패딩 · 오염 검사)

PDF 제품 이미지는 대개 [본체 + SMask(알파)] 쌍이다. 본체만 뽑으면 투명 영역의
밑색(주로 노랑)이 그대로 드러나 유리 제품이 형광색이 된다. 반드시 합성해야 한다.

사용:
  python extract_images.py CATALOG.pdf OUTDIR --pages 4:c001 5:c002-1 6:c002-2
  python extract_images.py CATALOG.pdf OUTDIR --pages 8-14:c007   # 연속 페이지 한 슬러그
옵션:
  --min-size 120   이보다 작은 이미지는 로고로 보고 건너뜀
  --quality 88
"""
import argparse, io, os, sys, colorsys
import pymupdf
from PIL import Image

W, H, MARGIN_RATIO = 1200, 900, 0.07


def chroma_report(im):
    """유채색 픽셀 수와 노랑 비중. 정상 추출이면 유채색이 수십 px,
    SMask를 놓치면 수천 px가 나온다."""
    t = im.convert('RGB').copy()
    t.thumbnail((160, 120))
    y = n = 0
    for r, g, b in t.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if v > 0.35 and s > 0.18:
            n += 1
            if 0.09 <= h <= 0.19:
                y += 1
    return n, (round(100 * y / n, 1) if n else 0.0)


def normalize(im, max_upscale=3.0):
    """비백색 영역으로 트림 후 흰 4:3 캔버스 중앙 배치.

    PIL 의 thumbnail() 은 축소만 하고 확대는 하지 않는다. 카탈로그 렌더는 원본이
    작은 경우가 많아 thumbnail 을 쓰면 큰 캔버스에 제품이 조그맣게 박힌다(실측 채움률 8~21%).
    그래서 축소·확대를 모두 하는 resize 를 쓰되, 과확대로 뭉개지지 않게 상한을 둔다."""
    g = im.convert('L').point(lambda v: 0 if v > 250 else 255)
    bb = g.getbbox()
    if bb:
        im = im.crop(bb)
    m = int(min(W, H) * MARGIN_RATIO)
    bw, bh = W - 2 * m, H - 2 * m
    sc = min(bw / im.width, bh / im.height, max_upscale)
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    cv = Image.new('RGB', (W, H), (255, 255, 255))
    cv.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return cv


def parse_pages(specs):
    """'4:c001' 또는 '8-14:c007' → {페이지번호(1-base): 슬러그}"""
    out = {}
    for spec in specs:
        rng, slug = spec.split(':', 1)
        if '-' in rng:
            a, b = rng.split('-')
            for p in range(int(a), int(b) + 1):
                out[p] = slug
        else:
            out[int(rng)] = slug
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('outdir')
    ap.add_argument('--pages', nargs='+', required=True)
    ap.add_argument('--min-size', type=int, default=120)
    ap.add_argument('--quality', type=int, default=88)
    a = ap.parse_args()

    pages = parse_pages(a.pages)
    os.makedirs(a.outdir, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    counter, warned = {}, []

    for pno in sorted(pages):
        slug = pages[pno]
        page = doc[pno - 1]
        for info in page.get_images(full=True):
            xref, smask = info[0], info[1]
            if smask == 0:
                continue  # 마스크 자체 또는 알파 없는 배경 이미지
            try:
                base = pymupdf.Pixmap(doc, xref)
                # 본체가 이미 알파를 갖고 있으면 Pixmap(base, smask) 가 거부한다
                # (code=4: color pixmap must not have an alpha channel).
                # 알파를 떼고 SMask 를 씌워야 한다. 이걸 놓치면 그 페이지가 통째로 건너뛰어진다.
                if base.alpha:
                    base = pymupdf.Pixmap(base, 0)
                merged = pymupdf.Pixmap(base, pymupdf.Pixmap(doc, smask))
                im = Image.open(io.BytesIO(merged.tobytes('png'))).convert('RGBA')
            except Exception as e:
                print('  [skip] p%d xref%d — %s' % (pno, xref, e))
                continue
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            im = bg.convert('RGB')

            gg = im.convert('L').point(lambda v: 0 if v > 246 else 255)
            bb = gg.getbbox()
            if bb and (bb[2] - bb[0] < a.min_size or bb[3] - bb[1] < a.min_size):
                continue

            im = normalize(im)
            counter[slug] = counter.get(slug, 0) + 1
            fn = os.path.join(a.outdir, '%s-%d.jpg' % (slug, counter[slug]))
            im.save(fn, 'JPEG', quality=a.quality, optimize=True)
            n, ypct = chroma_report(im)
            gg2 = im.convert('L').point(lambda v: 0 if v > 250 else 255).getbbox()
            fill = (100.0 * (gg2[2]-gg2[0]) * (gg2[3]-gg2[1]) / (W*H)) if gg2 else 0
            flag = ''
            if fill < 30:
                flag += '  ← 여백 과다(원본이 작음)'
            if n > 800:
                flag = '  ← 오염 의심(SMask 확인)'
                warned.append(fn)
            print('  p%-3d %-18s 유채색 %4d px · 노랑 %4.1f%% · 채움 %2.0f%%%s'
                  % (pno, os.path.basename(fn), n, ypct, fill, flag))

    print('\n총 %d장' % sum(counter.values()))
    if warned:
        print('⚠ 오염 의심 %d장 — 반드시 눈으로 확인:' % len(warned))
        for w in warned:
            print('   ', w)
    print('\n다음: 추출본을 device_stage_files(Windows 경로)로 가져와 직접 볼 것.')
    print('      워터마크가 있으면 remove_watermark.py, 부위 표시는 draw_markers.py.')


if __name__ == '__main__':
    main()
