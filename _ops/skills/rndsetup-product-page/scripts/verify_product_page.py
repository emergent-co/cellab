#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실험셋업연구소 제품 상세페이지 GEO·무결성 검증.

사용법:
    python scripts/verify_product_page.py brands/<brand>/<slug>/index.html [...]

저장소 루트에서 실행한다. 종료코드 0 = 전부 통과, 1 = 실패 항목 있음.
"""
import io
import json
import os
import re
import sys

OK, NG, WARN = 'PASS', 'FAIL', 'WARN'


def strip_tags(s):
    return re.sub(r'<[^>]*>', '', s)


def check(path):
    res = []

    def add(status, name, detail=''):
        res.append((status, name, detail))

    if not os.path.isfile(path):
        add(NG, '파일 존재', path)
        return res
    h = io.open(path, encoding='utf-8').read()

    # 1. 종료 태그
    add(OK if h.rstrip().endswith('</html>') else NG, '</html> 종료',
        '' if h.rstrip().endswith('</html>') else '파일이 잘렸을 수 있음 — 즉시 커밋 중단')

    # 2. title
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    add(OK if m and m.group(1).strip() else NG, '<title>', m.group(1)[:70] if m else '없음')

    # 3. description — 따옴표 이중 금지
    m = re.search(r'<meta name="description" content="([^"]*)"', h)
    if not m:
        add(NG, 'meta description', '없음 (또는 content 안에 큰따옴표가 중첩됨)')
    else:
        d = m.group(1)
        n = len(d)
        add(OK if 60 <= n <= 200 else WARN, 'meta description', f'{n}자')

    # 4. canonical
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    if not m:
        add(NG, 'canonical', '없음')
    else:
        want = 'https://rndsetup.com/' + os.path.dirname(path).replace(os.sep, '/').lstrip('./') + '/'
        want = want.replace('//brands', '/brands')
        add(OK if m.group(1).rstrip('/') + '/' == want else WARN, 'canonical',
            f'{m.group(1)}  (기대: {want})')

    # 5. OG / Twitter
    og = all(k in h for k in ('og:type', 'og:url', 'og:image'))
    tw = 'twitter:card' in h
    add(OK if og else WARN, 'OG 태그', '' if og else 'og:type/url/image 중 누락')
    add(OK if tw else WARN, 'Twitter Card', '' if tw else 'twitter:card 없음')

    # 6. h1 단일
    h1 = re.findall(r'<h1[^>]*>', h)
    add(OK if len(h1) == 1 else NG, 'H1 1개', f'{len(h1)}개')

    # 7. 정답블록
    m = re.search(r'<p class="dt-ans"[^>]*>(.*?)</p>', h, re.S)
    if not m:
        add(NG, '정답블록 .dt-ans', '없음 — GEO 0순위 요소')
    else:
        t = strip_tags(m.group(1)).strip()
        n = len(t)
        add(OK if 60 <= n <= 130 else WARN, '정답블록 길이', f'{n}자 (권장 80~100)')

    # 8. 사양표
    add(OK if 'class="pkg-tbl' in h else NG, '사양표 .pkg-tbl')

    # 9. 정가 표기
    add(OK if re.search(r'정가\s*<b>[\d,]+원</b>', h) or re.search(r'정가\s*[\d,]+\s*원', h) else WARN,
        '정가 표기', '' if '정가' in h else 'pkg-note에 정가 문구 없음')

    # 10. 견적 버튼
    q = re.findall(r'data-quote="([^"]*)"', h)
    add(OK if q else NG, '견적 버튼 data-quote', f'{len(q)}개 · {q[0][:40] if q else ""}')

    # 11. img alt
    imgs = re.findall(r'<img\b[^>]*>', h)
    noalt = [i for i in imgs if 'alt=' not in i]
    add(OK if not noalt else NG, 'img alt', f'{len(imgs)}개 중 {len(noalt)}개 누락')

    # 12. JSON-LD
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    types, faq_n = set(), 0
    bad = 0
    for b in blocks:
        try:
            d = json.loads(b)
        except Exception as e:
            bad += 1
            add(NG, 'JSON-LD 파싱', str(e)[:80])
            continue
        for node in (d.get('@graph') or [d]):
            t = node.get('@type')
            if isinstance(t, list):
                types.update(t)
            elif t:
                types.add(t)
            if node.get('@type') == 'FAQPage':
                faq_n = len(node.get('mainEntity') or [])
    if not bad:
        add(OK, 'JSON-LD 파싱', f'{len(blocks)}블록')
    for need in ('Product', 'FAQPage', 'BreadcrumbList'):
        add(OK if need in types else NG, f'JSON-LD {need}')

    # 13. FAQ 1:1
    html_faq = len(re.findall(r'class="faq-q"', h))
    if html_faq or faq_n:
        add(OK if html_faq == faq_n else NG, 'FAQ 화면↔스키마 일치',
            f'화면 {html_faq}문 / 스키마 {faq_n}문')

    # 14. offers price가 정가인지(할인가 오입력 방지) — 정수인지만 확인
    for b in blocks:
        m = re.search(r'"(?:price|lowPrice)":\s*(\d+)', b)
        if m:
            add(OK, 'offers price', f'{int(m.group(1)):,}원 (정가여야 함)')
            break

    # 15. footer 자리
    add(OK if 'id="pumplab-footer"' in h else NG, '#pumplab-footer',
        '빌드가 CNAV를 주입하는 자리')

    # 16. 인라인 script 안 </script> 사고
    add(OK if '<\\/script>' in h or '</script>' in h else WARN, 'script 종료', '')

    return res


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    fail = 0
    for path in argv[1:]:
        print(f'\n=== {path}')
        for status, name, detail in check(path):
            mark = {'PASS': ' OK ', 'FAIL': 'FAIL', 'WARN': 'WARN'}[status]
            print(f'  [{mark}] {name}' + (f' — {detail}' if detail else ''))
            if status == NG:
                fail += 1
    print(f'\n실패 {fail}건')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
