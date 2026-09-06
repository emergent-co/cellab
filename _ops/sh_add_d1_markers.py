# -*- coding: utf-8 -*-
"""삼흥 상세페이지에 D1 가격 주입 마커(data-d1)를 심는다.

왜
  functions/brands/sh-scientific/_middleware.js 는 본문에서 data-d1 을 찾아
  D1 의 소비자가로 바꿔치기한다. 그런데 저장소 전체에 그 마커가 0개였다.
  D1 에 가격이 있는데도 전기로 계열 상세페이지에 «견적 문의» 만 뜨던 이유가 이것이다.

무엇을
  구매창(buybox)이 없고, 사양표 열 머리가 모델코드인 페이지에만
  사양표 맨 아래 «판매가» 행을 붙인다. 각 칸은 <td data-d1="모델">견적 문의</td> 다.
  D1 에 그 모델이 없거나 조회가 실패하면 미들웨어가 아무 것도 안 하므로
  원문 «견적 문의» 가 그대로 남는다 — 틀린 숫자가 뜨는 일은 없다.
  Product JSON-LD 에는 data-d1-ld 를 붙여 offers 를 AggregateOffer 로 승격시킨다.

쓰기
  python _ops/sh_add_d1_markers.py            검사만
  python _ops/sh_add_d1_markers.py --write    적용
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'brands', 'sh-scientific')
MODEL = re.compile(r'^[A-Za-z][A-Za-z0-9./\-]{4,}$')


def spec_table(body):
    """열 머리가 전부 모델코드인 사양표 하나를 고른다."""
    for m in re.finditer(r'<table[^>]*class="[^"]*pkg-tbl[^"]*"[^>]*>(.*?)</table>', body, re.S):
        th = re.search(r'<thead>(.*?)</thead>', m.group(1), re.S)
        if not th:
            continue
        cols = [re.sub(r'<[^>]+>', '', x).strip()
                for x in re.findall(r'<th[^>]*scope="col"[^>]*>(.*?)</th>', th.group(1), re.S)][1:]
        if cols and all(MODEL.match(c) for c in cols):
            return m.group(0), cols
    return None, []


def add_marker(html):
    body = re.sub(r'<script.*?</script>', '', html.split('<body>', 1)[-1], flags=re.S)
    tbl, cols = spec_table(body)
    if not tbl:
        return None, [], '사양표 열이 모델코드가 아니다'
    if 'data-d1' in html:
        return None, [], '이미 마커가 있다'
    row = ('<tr><th scope="row">판매가</th>'
           + ''.join('<td data-d1="%s">견적 문의</td>' % c for c in cols)
           + '</tr>')
    new_tbl = tbl.replace('</tbody>', row + '</tbody>', 1)
    if new_tbl == tbl:
        return None, [], '표에 </tbody> 가 없다'
    out = html.replace(tbl, new_tbl, 1)

    # Product JSON-LD 에 data-d1-ld — 미들웨어가 type= 뒤에서 찾는다
    def ld(m):
        if '"@type": "Product"' not in m.group(2) and '"@type":"Product"' not in m.group(2):
            return m.group(0)
        if 'data-d1-ld' in m.group(1):
            return m.group(0)
        return ('<script type="application/ld+json" data-d1-ld="%s"%s>%s</script>'
                % (','.join(cols), m.group(1), m.group(2)))

    out = re.sub(r'<script type="application/ld\+json"([^>]*)>(.*?)</script>', ld, out, flags=re.S)
    return out, cols, ''


def check(old, new):
    if not new.rstrip().endswith('</html>'):
        return '</html> 로 끝나지 않는다'
    if 'class="dt-name"' not in new:
        return 'dt-name 이 사라졌다'
    if new.count('<table') != old.count('<table') or new.count('</table>') != old.count('</table>'):
        return '표 개수가 바뀌었다'
    if len(re.findall(r'<tr[ >]', new)) != new.count('</tr>'):
        return 'tr 짝이 안 맞는다'
    if len(re.findall(r'<tr[ >]', new)) != len(re.findall(r'<tr[ >]', old)) + 1:
        return '행이 하나만 늘어야 한다'
    if new.count('<script') != old.count('<script'):
        return 'script 개수가 바뀌었다'
    if new.count('data-d1-ld') > 1:
        return 'data-d1-ld 가 여러 개'
    return ''


def main():
    write = '--write' in sys.argv
    done = skip = 0
    for slug in sorted(os.listdir(BRAND)):
        p = os.path.join(BRAND, slug, 'index.html')
        if not os.path.isfile(p):
            continue
        old = io.open(p, encoding='utf-8').read()
        if 'class="dt-name"' not in old or 'id="buybox"' in old:
            continue
        new, cols, why = add_marker(old)
        if new is None:
            print('  [건너뜀] %-28s %s' % (slug, why))
            skip += 1
            continue
        bad = check(old, new)
        if bad:
            print('  [FAIL]  %-28s %s' % (slug, bad))
            continue
        print('  [%s] %-28s %d모델 · LD %s'
              % ('적용' if write else '예정', slug, len(cols),
                 'O' if 'data-d1-ld' in new else '-'))
        if write:
            io.open(p, 'w', encoding='utf-8', newline='').write(new)
        done += 1
    print('\n마커 %d장 %s · 건너뜀 %d장' % (done, '적용' if write else '예정', skip))
    return 0


if __name__ == '__main__':
    sys.exit(main())
