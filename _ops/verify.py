#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""등록 산출물 검증 — 변경할 때마다 돌린다.

빌드가 성공해도 페이지는 깨질 수 있다. 여기서 잡는 것들은 전부 실제로 라이브에
나갔던 사고다: 잘린 HTML, 표와 어긋난 JSON-LD 가격, 건너뛴 번호, 이름을 바꾼 뒤
남은 옛 이미지 참조(썸네일만 옛 색으로 보이는 원인), 문의 처리했는데 0원으로 뜨는 카드.

사용:
  python verify.py REPO_ROOT
  python verify.py REPO_ROOT --scope brands/gaossunion
  python verify.py REPO_ROOT --stale c001-1.jpg glass-cell/   # 없어야 할 참조 지정
"""
import argparse, glob, io, json, os, re, sys

PRICE = re.compile(r'<b>([\d,]+)원</b>')


def load(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def check_html_tail(files):
    bad = []
    for f in files:
        if '/_build/partial_' in f.replace(os.sep, '/'):
            continue  # 조각 파일은 </html> 로 끝나지 않는 게 정상
        if not load(f).rstrip().endswith('</html>'):
            bad.append(f)
    return bad


def check_jsonld(files):
    bad = []
    for f in files:
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                             load(f), re.S):
            try:
                json.loads(m.group(1))
            except Exception as e:
                bad.append((f, str(e)[:70]))
    return bad


def check_price_match(files):
    """Product JSON-LD 의 lowPrice/highPrice 가 표의 실제 min/max 와 같은지."""
    bad = []
    for f in files:
        s = load(f)
        rows = [l for l in s.split('\n') if l.lstrip().startswith('<tr>')]
        pr = [int(x.replace(',', '')) for l in rows for x in PRICE.findall(l)]
        m = re.search(r'"lowPrice": (\d+), "highPrice": (\d+)', s)
        if not pr or not m:
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo != min(pr) or hi != max(pr):
            bad.append((f, lo, hi, min(pr), max(pr)))
    return bad


def check_numbering(files):
    """번호 목록이 1..N 연속인지. 사진에 없는 항목을 섞으면 건너뛴다."""
    bad = []
    for f in files:
        for ol in re.findall(r'<ul class="spec-ol">([\s\S]*?)</ul>', load(f)):
            nums = [int(n) for n in re.findall(r'<span class="sn[^"]*">(\d+)</span>', ol)]
            if nums and nums != list(range(1, len(nums) + 1)):
                bad.append((f, nums))
    return bad


def check_stale(files, needles):
    hits = []
    for f in files:
        s = load(f)
        for nd in needles:
            if nd in s:
                hits.append((f, nd))
    return hits


def check_zero_price(files):
    bad = []
    for f in files:
        s = load(f)
        if re.search(r'<b>0원</b>|>0원<|최소 0원', s):
            bad.append(f)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--scope', default='', help='하위 경로로 한정 (예: brands/gaossunion)')
    ap.add_argument('--stale', nargs='*', default=[], help='남아 있으면 안 되는 문자열')
    a = ap.parse_args()

    base = os.path.join(a.root, a.scope) if a.scope else a.root
    files = [f for f in glob.glob(os.path.join(base, '**', '*.html'), recursive=True)
             if '_to_delete' not in f.replace(os.sep, '/')]
    if not files:
        print('HTML 없음:', base); sys.exit(1)

    fails = 0
    print('검사 대상 %d개 파일 (%s)\n' % (len(files), base))

    for label, res, fmt in [
        ('HTML </html> 종결', check_html_tail(files), lambda x: x),
        ('JSON-LD 파싱', check_jsonld(files), lambda x: '%s — %s' % x),
        ('JSON-LD 가격 = 표 min/max', check_price_match(files),
         lambda x: '%s  JSON %s~%s / 표 %s~%s' % x),
        ('번호 목록 1..N 연속', check_numbering(files), lambda x: '%s  %s' % x),
        ('0원 노출', check_zero_price(files), lambda x: x),
    ]:
        if res:
            fails += len(res)
            print('✗ %s — %d건' % (label, len(res)))
            for r in res[:10]:
                print('    ', fmt(r))
            if len(res) > 10:
                print('     ... 외 %d건' % (len(res) - 10))
        else:
            print('✓ %s' % label)

    if a.stale:
        res = check_stale(files, a.stale)
        if res:
            fails += len(res)
            print('✗ 옛 참조 잔존 — %d건' % len(res))
            for f, nd in res[:10]:
                print('     %s  ←  %s' % (f, nd))
        else:
            print('✓ 옛 참조 잔존 0 (%s)' % ', '.join(a.stale))

    print('\n%s' % ('통과' if fails == 0 else '실패 %d건 — 배포 전 수정' % fails))
    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    main()
