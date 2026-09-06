# -*- coding: utf-8 -*-
"""브로슈어 사양(_build/sh_brochure_specs.json)을 삼흥 상세페이지 사양표에 채운다.

원칙
  표의 열 머리(모델명)가 브로슈어 모델과 '전부' 맞는 표만 건드린다.
  하나라도 못 맞추면 그 페이지는 손대지 않는다 — 패키지 구성표(PK-F1/PK-F2)처럼
  열이 모델이 아닌 표에 사양을 밀어 넣으면 값이 엉뚱한 칸에 들어간다.
  페이지는 하나씩 열고, 검증을 통과할 때만 그 파일을 쓴다.

쓰기
  python _ops/sh_fill_specs.py --check            대상·추가될 행만 출력
  python _ops/sh_fill_specs.py --only <slug>      한 장만 적용
  python _ops/sh_fill_specs.py --write            전부 적용
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, 'brands', 'sh-scientific')
SPECS = os.path.join(ROOT, '_build', 'sh_brochure_specs.json')

# 파서가 표 밖의 글자를 라벨로 오인한 것들. 값이 아니라 모델명·각주·온도 표기다.
NOISE = re.compile(r'^[<*＊(]|^[-+]?\d|℃|℉|Ambient|^\s*$')

# 브로슈어 전체에서 이 수 이상의 모델이 쓴 라벨만 페이지에 넣는다.
# 1~2종에만 나오는 라벨은 거의 다 파서가 두 칸을 붙여 버린 찌꺼기다
# ('Heater Capa Dimension Internal 1300×1000×1200mm …' 같은 것).
MIN_MODELS = 5
# 빈도는 높지만 두 줄로 접힌 라벨의 조각이라 그대로 쓰면 뜻이 안 통하는 것들.
STOP = {'Gas', 'ballast close', 'ballast open', 'Dimension', 'Rang', 'Components',
        'Recommended for', 'Product Name'}

# 라벨은 표기가 제각각이다 — 'Internal Dim. (W×D×H)' 와 'Dimension Internal',
# 'Volume' 과 'Capa' 는 같은 항목이다. 글자를 비교하면 중복이 그대로 들어가므로
# 개념 하나로 접은 뒤에 비교한다.
def canon(lab):
    lab = lab.replace('₂', '2').replace('₃', '3').replace('²', '2')
    k = re.sub(r'[^0-9a-z가-힣]', '', lab.lower())
    if 'co2' in k:
        return 'CO2_RANGE' if ('range' in k or '범위' in k) else 'CO2'
    if 'steril' in k or '멸균' in k or '살균' in k:
        return 'STERILIZE'
    has = lambda *w: any(x in k for x in w)
    dim = has('dim', '치수', 'size', '크기')
    if has('material', '재질'):
        if has('internal', '내부'):
            return 'MAT_INT'
        if has('external', '외부'):
            return 'MAT_EXT'
        return 'MATERIAL'
    if dim and has('internal', '내부'):
        return 'INT_DIM'
    if dim and has('external', '외부', '외형'):
        return 'EXT_DIM'
    if k in ('외형', '외형치수', '외관치수', 'external'):
        return 'EXT_DIM'
    if dim and has('hotzone', '핫존'):
        return 'HOTZONE'
    if has('capa', '용량', '내용적') or k == 'volume':
        return 'CAPA'
    if has('chamber', '챔버'):
        return 'CHAMBER'
    if has('temp', '온도'):
        if has('controller', '컨트롤러', '제어'):
            return 'CONTROLLER'
        if has('max', '최고', '최대'):
            return 'MAX_TEMP'
        # 그냥 '온도' 도 실제로는 사용 범위를 적는 칸이다 — 범위와 같은 항목으로 본다
        return 'TEMP_RANGE'
    if has('controller', '컨트롤러', '제어'):
        return 'CONTROLLER'
    if has('heater', '히터', '발열'):
        return 'HEATER_EL' if has('element', '소재') else 'HEATER'
    if has('sensor', '센서'):
        return 'SENSOR'
    if has('tube', '튜브') and has('diameter', 'dia', '경'):
        return 'TUBE_DIA'
    if has('power', '전원', '소비전력'):
        return 'POWER'
    if has('weight', '무게', '중량'):
        return 'WEIGHT'
    if has('noise', '소음'):
        return 'NOISE'
    if has('display', '디스플레이', '표시'):
        return 'DISPLAY'
    if has('speed', '속도'):
        return 'SPEED'
    return k


def same_as(lab, have_can):
    return canon(lab) in have_can


def clean(v):
    """브로슈어 값에서 인치 환산분을 떼고 공백을 정리한다."""
    parts = [p.strip() for p in v.split(' / ')]
    keep = [p for p in parts if not re.search(r'(?:["″]|\'\')\s*$', p)]
    out = ' / '.join(keep or parts)
    out = re.sub(r'[Ø∅ø]{2,}', 'Ø', out)      # 표에서 지름 기호가 겹쳐 찍힌 것
    return re.sub(r'\s+', ' ', out).strip()


def load_models():
    d = json.load(io.open(SPECS, encoding='utf-8'))['models']
    idx = {}
    for k in d:
        idx[re.sub(r'[\s.]+$', '', k.strip().upper())] = k
    use = {}
    for v in d.values():
        for lab in v['specs']:
            use[lab] = use.get(lab, 0) + 1
    allow = {k for k, n in use.items() if n >= MIN_MODELS and k not in STOP and len(k) <= 32}
    return d, idx, allow


def _z(x):
    return re.sub(r'0+(\d)', r'\1', x)          # SH-RE-05L 과 RE-5L 을 같게 본다


def lookup(col, idx):
    """표의 열 머리(모델명)를 브로슈어 모델에 맞춘다.

    페이지가 모델명을 줄여 쓰거나(900B ⊂ SH-HD-900B), 온도를 붙여 쓰거나
    (SH-FU-4MS1700 ⊃ SH-FU-4MS), 공백을 넣어 쓴 경우를 모두 흡수한다.
    접미로 맞출 때는 바로 앞이 '-' 여야 한다 — 그렇지 않으면
    900B 가 SH-HD-1900B 에도 걸려 엉뚱한 모델을 집는다."""
    c = re.sub(r'\(.*?\)', '', col).upper()
    c = re.sub(r'\s+', '', c).strip(' .·')
    if not c or len(c) < 3:
        return None
    for cand in (c, 'SH-' + c, re.sub(r'(1[6-9]00|2400|3000)$', '', c)):
        if cand and cand in idx:
            return idx[cand]
    out = set()
    for k in idx:
        if k.endswith(c) and k[:-len(c)].endswith('-'):
            out.add(k)
        elif _z(k).endswith(_z(c)) and _z(k)[:-len(_z(c))].endswith('-'):
            out.add(k)
    return idx[out.pop()] if len(out) == 1 else None


def plan(html, models, idx, allow):
    """(표 원문, 추가할 <tr> 목록, 열 모델) — 못 채우면 (None, [], [])"""
    body = re.sub(r'<script.*?</script>', '', html.split('<body>', 1)[-1], flags=re.S)
    for m in re.finditer(r'<table[^>]*class="[^"]*pkg-tbl[^"]*"[^>]*>(.*?)</table>', body, re.S):
        tbl = m.group(1)
        th = re.search(r'<thead>(.*?)</thead>', tbl, re.S)
        if not th:
            continue
        cols = [re.sub(r'<[^>]+>', '', c).strip()
                for c in re.findall(r'<th[^>]*scope="col"[^>]*>(.*?)</th>', th.group(1), re.S)][1:]
        if not cols:
            continue
        hit = [lookup(c, idx) for c in cols]
        if not all(hit):
            continue
        have = {canon(x) for x in re.findall(r'<th[^>]*scope="row"[^>]*>([^<]{1,40})</th>', tbl)}
        labs = []
        for mdl in hit:
            for lab in models[mdl]['specs']:
                if lab not in labs:
                    labs.append(lab)
        rows = []
        for lab in labs:
            if lab not in allow or NOISE.match(lab) or same_as(lab, have):
                continue
            vals = [clean(models[mdl]['specs'].get(lab, '')) for mdl in hit]
            if not any(vals):
                continue
            # 'Temp Range = Max 130℃' 처럼 값이 최고온도인데 페이지에 이미 최고온도가
            # 있으면 같은 내용을 두 줄로 적게 된다.
            if canon(lab) == 'TEMP_RANGE' and 'MAX_TEMP' in have \
                    and all(v.lower().startswith('max') for v in vals if v):
                continue
            if len(set(vals)) == 1:
                cells = '<td colspan="%d">%s</td>' % (len(vals), vals[0])
            else:
                cells = ''.join('<td>%s</td>' % (v or '—') for v in vals)
            rows.append('<tr><th scope="row">%s</th>%s</tr>' % (lab, cells))
        return m.group(0), rows, hit
    return None, [], []


def apply(html, table, rows):
    i = html.find(table)
    new_tbl = table.replace('</tbody>', ''.join(rows) + '</tbody>', 1)
    if new_tbl == table:
        return None
    return html[:i] + new_tbl + html[i + len(table):]


def check(old, new, ntable):
    if not new.rstrip().endswith('</html>'):
        return '</html> 로 끝나지 않는다'
    if 'class="dt-name"' not in new:
        return 'dt-name 이 사라졌다'
    if new.count('<table') != ntable or new.count('</table>') != ntable:
        return '표 개수가 바뀌었다'
    if new.count('<tbody>') != old.count('<tbody>'):
        return 'tbody 개수가 바뀌었다'
    if len(new) <= len(old):
        return '내용이 늘지 않았다'
    if new.split('<body>', 1)[0] != old.split('<body>', 1)[0]:
        return 'head 가 바뀌었다'
    return ''


def main():
    models, idx, allow = load_models()
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    write = '--write' in sys.argv or only
    done = skipped = added = 0
    for slug in sorted(os.listdir(BRAND)):
        if only and slug != only:
            continue
        p = os.path.join(BRAND, slug, 'index.html')
        if not os.path.isfile(p):
            continue
        old = io.open(p, encoding='utf-8').read()
        if 'class="dt-name"' not in old:
            continue
        table, rows, hit = plan(old, models, idx, allow)
        if not table or not rows:
            skipped += 1
            continue
        new = apply(old, table, rows)
        bad = check(old, new, old.count('<table')) if new else '표에 </tbody> 가 없다'
        if bad:
            print('  [FAIL] %-28s %s' % (slug, bad))
            continue
        print('  [%s] %-28s 열 %s · %d행 추가: %s'
              % ('적용' if write else '예정', slug, '/'.join(hit)[:44], len(rows),
                 ' · '.join(re.search(r'row">([^<]*)', r).group(1) for r in rows)[:70]))
        if write:
            io.open(p, 'w', encoding='utf-8', newline='').write(new)
        done += 1
        added += len(rows)
    print('\n대상 %d장 · 추가 행 %d개 · 손대지 않음 %d장' % (done, added, skipped))
    return 0


if __name__ == '__main__':
    sys.exit(main())
