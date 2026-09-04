# -*- coding: utf-8 -*-
"""삼흥(SH Scientific) 상세페이지 — 인라인 <style> 제거 + /assets/detail.css 링크.

왜 스크립트인가
  150장이 같은 구조다. 손으로 고치면 잘림 사고가 난다(CRITICAL_RULES §1).
  이 스크립트는 여러 파일을 한 번에 정규식으로 밀지 않는다 — 파일을 하나씩 열어
  검증 6종을 모두 통과할 때만 그 파일을 쓴다. 하나라도 걸리면 그 파일은 건드리지 않는다.

무엇을 지우나
  <head> 안의 <style> 블록 전부. 삼흥 인라인 CSS 는 detail.css 의 옛 스냅샷이라
  (134개 중 105개가 문자열까지 동일) 지우면 detail.css 의 최신판을 그대로 받는다.
  detail.css·site.css 어디에도 없던 9개 블록은 2026-09-04 에 detail.css 로 옮겼다.

쓰기
  python _ops/sh_to_detailcss.py --check     검사만 (파일 안 씀)
  python _ops/sh_to_detailcss.py             적용
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'brands', 'sh-scientific')
LINK = '<link rel="stylesheet" href="/assets/detail.css">'
SITE = re.compile(r'<link rel="stylesheet" href="/assets/site\.css(?:\?v=[0-9a-f]+)?">')

# 페이지 고유 CSS 가 124블록 — 위저드(qsel-*)·비교표(vs-*)·도해(svg) 전용.
# 일괄 처리하면 페이지가 깨진다. 따로 옮긴다.
SKIP = set()   # 2026-09-04 PRO 고유 CSS 를 detail.css '회전 튜브로 PRO 상세' 절로 옮겨 해제

# 계열 — 보고·배포를 쪼개는 단위. 먼저 맞는 것이 이긴다.
FAMILIES = [
    ('퍼니스',   ('muffle', 'tube-furnace', 'rotary-kiln', 'elevator', 'gas-flow', 'furnace')),
    ('오븐·건조', ('drying-oven', 'oven', 'vacuum-oven', 'dry')),
    ('챔버·인큐베이터', ('incubator', 'climate-chamber', 'chamber', 'shaker')),
    ('흄후드',   ('fume-hood',)),
    ('멸균·수처리', ('autoclave', 'distillation', 'water', 'steam')),
]


def family(slug):
    for name, keys in FAMILIES:
        if any(k in slug for k in keys):
            return name
    return '기타'


def convert(html):
    """(새 html, 지운 style 블록 수, 사유) — 못 고치면 새 html 이 None."""
    if '<style' not in html:
        return None, 0, '인라인 style 없음(이미 이관됨)'
    body_at = html.find('<body')
    styles = list(re.finditer(r'<style[^>]*>.*?</style>', html, re.S))
    if not styles:
        return None, 0, '<style> 는 있는데 닫는 </style> 를 못 찾음'
    if styles[-1].end() > body_at:
        return None, 0, '<body> 뒤에 <style> 이 있음 — 손으로 확인할 것'
    if not SITE.search(html):
        return None, 0, 'site.css 링크가 없음 — 붙일 자리를 못 정함'

    out = html
    for m in reversed(styles):
        out = out[:m.start()] + out[m.end():]
    out = out.replace('\n\n\n', '\n\n')
    m = SITE.search(out)
    out = out[:m.start()] + LINK + '\n' + out[m.start():]
    return out, len(styles), ''


def check(old, new):
    """쓰기 전 검증. 하나라도 실패하면 그 파일은 안 쓴다."""
    if '<style' in new:
        return '<style> 가 남았다'
    if new.count(LINK) != 1:
        return 'detail.css 링크가 %d개' % new.count(LINK)
    if not SITE.search(new):
        return 'site.css 링크가 사라졌다'
    if not new.rstrip().endswith('</html>'):
        return '</html> 로 끝나지 않는다'
    if 'class="dt-name"' not in new:
        return 'dt-name 이 사라졌다 — 본문 손상'
    if old.split('<body', 1)[1] != new.split('<body', 1)[1]:
        return '<body> 이후 본문이 바뀌었다'
    if new.count('</head>') != 1 or new.count('<body') != old.count('<body'):
        return '태그 개수가 맞지 않는다'
    return ''


def main():
    dry = '--check' in sys.argv
    rows = []
    for slug in sorted(os.listdir(BRAND)):
        p = os.path.join(BRAND, slug, 'index.html')
        if not os.path.isfile(p):
            continue
        with open(p, encoding='utf-8') as f:
            old = f.read()
        if 'class="dt-name"' not in old:
            continue
        if slug in SKIP:
            rows.append((family(slug), slug, 'SKIP', '페이지 고유 CSS — 따로 이관'))
            continue
        new, n, why = convert(old)
        if new is None:
            rows.append((family(slug), slug, 'SKIP', why))
            continue
        bad = check(old, new)
        if bad:
            rows.append((family(slug), slug, 'FAIL', bad))
            continue
        if not dry:
            with open(p, 'w', encoding='utf-8', newline='') as f:
                f.write(new)
        rows.append((family(slug), slug, 'OK',
                     'style %d블록 %d bytes 제거' % (n, len(old) - len(new))))

    fams = {}
    for fam, slug, st, msg in rows:
        fams.setdefault(fam, []).append((st, slug, msg))
    print('%s — 삼흥 %d장' % ('검사' if dry else '적용', len(rows)))
    for fam in sorted(fams):
        v = fams[fam]
        ok = sum(1 for s, _, _ in v if s == 'OK')
        print('  %-14s %3d장 중 OK %3d' % (fam, len(v), ok))
        for st, slug, msg in v:
            if st != 'OK':
                print('      [%s] %s — %s' % (st, slug, msg))
    fail = [r for r in rows if r[2] == 'FAIL']
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
