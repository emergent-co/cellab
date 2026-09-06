# -*- coding: utf-8 -*-
"""삼흥 상세페이지의 줄여 쓴 모델명을 실제 판매 모델명으로 되돌린다.

왜
  표 열 머리와 구매창(data-models)에 '900B' · 'PK-G1' · 'BL220' 처럼 접두를 뗀 이름이
  들어가 있다. 고객이 검색하는 이름(SH-HD-900B)과 달라 유입을 놓치고, 브로슈어·D1 과도
  매칭이 안 된다. 공식 가격표(실험실닷컴) 표기로 맞춘다.

무엇을
  <th scope="col"> 의 열 머리와 data-models 의 m 값만 바꾼다. 본문 문장은 건드리지 않는다.
  매핑은 아래 표에 손으로 적었다 — 기계가 접미로 추측하면 900B 가 1900B 에 걸린다.

쓰기
  python _ops/sh_normalize_models.py            검사만
  python _ops/sh_normalize_models.py --write    적용
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'brands', 'sh-scientific')

MAP = {
    'fume-hood-b':            {'900B': 'SH-HD-900B', '1500B': 'SH-HD-1500B', '1900B': 'SH-HD-1900B'},
    'fume-hood-v':            {'900V': 'SH-HD-900V', '1500V': 'SH-HD-1500V', '1900V': 'SH-HD-1900V'},
    'fume-hood-up':           {'1200UP': 'SH-HD-1200UP', '1500UP': 'SH-HD-1500UP',
                               '1800UP': 'SH-HD-1800UP', '1200': 'SH-HD-1200UP',
                               '1500': 'SH-HD-1500UP', '1800': 'SH-HD-1800UP'},
    'incubator-ds':           {'DS-10': 'SH-DS-10', 'DS-12': 'SH-DS-12',
                               'DS-20': 'SH-DS-20', 'DS-40': 'SH-DS-40'},
    'vacuum-pump-v':          {'V10': 'SH-V10', 'V20': 'SH-V20', 'V40': 'SH-V40',
                               'V60': 'SH-V60', 'V100': 'SH-V100', 'V170': 'SH-V170'},
    'measuring-instrument-bl': {'BL220': 'SH-BL220', 'BL220S': 'SH-BL220S',
                                'BL310': 'SH-BL310', 'BL610': 'SH-BL610'},
    'rotary-evaporator-la':   {'RE-5L': 'SH-RE-05L', 'RE-10L': 'SH-RE-10L',
                               'RE-20L': 'SH-RE-20L', 'RE-50L': 'SH-RE-50L'},
    'vacuum-drying-oven-g':   {'PK-G1': 'VDO-PK-G1', 'PK-G2': 'VDO-PK-G2',
                               'PK-G3': 'VDO-PK-G3', 'PK-G4': 'VDO-PK-G4'},
    'vacuum-drying-oven-gce': {'PK-G1CE': 'VDO-PK-G1CE', 'PK-G2CE': 'VDO-PK-G2CE',
                               'PK-G3CE': 'VDO-PK-G3CE', 'PK-G4CE': 'VDO-PK-G4CE'},
    'sh-peristaltic-pump-pp': {'PP100': 'SH-PP100', 'PP200': 'SH-PP200', 'PP600': 'SH-PP600'},
}


def swap(html, pairs):
    """열 머리와 data-models 의 m 값만 바꾼다."""
    n = [0]

    def th(m):
        v = m.group(1).strip()
        if v in pairs:
            n[0] += 1
            return m.group(0).replace('>' + m.group(1) + '<', '>' + pairs[v] + '<')
        return m.group(0)

    out = re.sub(r'<th scope="col">([^<]+)</th>', th, html)

    def dm(m):
        body = m.group(1)

        def one(x):
            v = x.group(1)
            if v in pairs:
                n[0] += 1
                return '"m": "%s"' % pairs[v]
            return x.group(0)
        return "data-models='" + re.sub(r'"m":\s*"([^"]+)"', one, body) + "'"

    out = re.sub(r"data-models='(\[.*?\])'", dm, out, flags=re.S)
    return out, n[0]


def main():
    write = '--write' in sys.argv
    tot = 0
    for slug, pairs in sorted(MAP.items()):
        p = os.path.join(BRAND, slug, 'index.html')
        if not os.path.isfile(p):
            print('  [없음] %s' % slug)
            continue
        s = io.open(p, encoding='utf-8').read()
        t, n = swap(s, pairs)
        if not n:
            print('  [변화없음] %s' % slug)
            continue
        ok = (t.rstrip().endswith('</html>') and 'class="dt-name"' in t and '<style' not in t
              and len(re.findall(r'<tr[ >]', t)) == t.count('</tr>')
              and t.count('<table') == s.count('<table')
              and t.count('data-models') == s.count('data-models'))
        if not ok:
            print('  [FAIL] %s — 검증 실패' % slug)
            continue
        print('  [%s] %-24s %d곳' % ('적용' if write else '예정', slug, n))
        if write:
            io.open(p, 'w', encoding='utf-8', newline='').write(t)
        tot += n
    print('\n%d곳 %s' % (tot, '적용' if write else '예정'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
