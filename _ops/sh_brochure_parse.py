# -*- coding: utf-8 -*-
"""삼흥 2026 국문 브로슈어(PDF) → 모델별 사양 SSOT.

왜
  실험실닷컴 목록에서 긁은 것은 모델·이름·가격뿐이라 상세페이지 사양이 2~5행으로 비었다.
  제조사 브로슈어에는 같은 사양이 표로 다 들어 있다. 사람이 옮겨 적지 않는다.

방법
  pdftotext -layout 은 표의 칸 위치를 공백으로 보존한다. 그래서
  'Model' 행에서 각 모델이 시작하는 x 위치를 잡고, 그 아래 줄을 같은 위치로 잘라
  라벨 → 모델별 값으로 되돌린다. 한 칸을 여러 모델이 나눠 쓰는 경우(가운데 정렬된
  공통값)는 그 표의 모든 모델에 같은 값을 준다.

쓰기
  python _ops/sh_brochure_parse.py            # 요약만
  python _ops/sh_brochure_parse.py --write    # _build/sh_brochure_specs.json 저장
"""
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, '2026_SH Scientific brochure-KO.pdf')
OUT = os.path.join(ROOT, '_build', 'sh_brochure_specs.json')

# 표의 첫 행(=모델 이름 줄)을 여는 라벨들
HEAD = re.compile(r'^(Model(?:\s*No\.?)?|Package Model|Furnace Model|Model\([^)]*\)|Item)\b')
# 모델처럼 생긴 토큰 — 값 칸이 아니라 모델명인지 가르는 데 쓴다
MODELISH = re.compile(r'^(?:SH-|IS-|CI-|CG|PY|MS-|OS-|NS-|TR-|VM-|MLX-|WB-|DB-|SY-|RE-PK|VDO-PK|BL|Welch|no\.)', re.I)
# 값이 아니라 각주·페이지 꼬리인 줄
NOISE = re.compile(r'www\.silhumsil\.com|삼흥에너지 공식몰|1544-0351|^\s*\d{1,3}\s*$')


def groups(line):
    """공백 2칸 이상으로 갈라진 (시작위치, 텍스트) 목록."""
    return [(m.start(), m.group().strip())
            for m in re.finditer(r'\S(?:.*?\S)?(?=\s{2,}|$)', line) if m.group().strip()]


def parse_page(page, title_hint):
    """한 페이지에서 표들을 뽑는다 → [{'title':.., 'models':[..], 'specs':{라벨:[값..]}}]"""
    lines = page.split('\n')
    tables = []
    i = 0
    while i < len(lines):
        g = groups(lines[i])
        if not g or not HEAD.match(g[0][1]) or len(g) < 2:
            i += 1
            continue
        cols = g[1:]                       # (x, 모델명)
        models = [c[1] for c in cols]
        starts = [c[0] for c in cols]
        # 표 제목 = 위로 올라가며 만나는 첫 비들여쓰기 문장
        title = ''
        for k in range(i - 1, max(-1, i - 12), -1):
            s = lines[k].strip()
            if not s or NOISE.search(s):
                continue
            if len(lines[k]) - len(lines[k].lstrip()) <= 6 and not groups(lines[k])[1:]:
                title = s
                break
        specs, blanks, label = {}, 0, None
        labx = []                          # 라벨 칸의 x 위치 — 표 왼쪽 바깥 주석을 걸러낸다
        j = i + 1
        while j < len(lines):
            ln = lines[j]
            if not ln.strip():
                blanks += 1
                if blanks >= 3:
                    break
                j += 1
                continue
            blanks = 0
            gg = groups(ln)
            if gg and HEAD.match(gg[0][1]) and len(gg) > 1:
                break                      # 다음 표가 시작됐다
            if NOISE.search(ln):
                j += 1
                continue
            # 라벨 = 첫 칸이 첫 모델 x 위치보다 왼쪽에서 시작할 때
            if gg and gg[0][0] < starts[0] - 2:
                lab, vals = gg[0][1], gg[1:]
                # 표 왼쪽 바깥에 따로 적힌 주석("Option: Oil Mist Trap …")은 라벨이 아니다
                if labx and gg[0][0] < min(labx) - 12:
                    j += 1
                    continue
            else:
                lab, vals = None, gg        # 라벨 없는 줄 = 앞 라벨의 둘째 줄(인치 표기 등)
            lab = (lab or '').strip(' :·')
            if lab and (lab.startswith('(') or lab.startswith('*') or lab.startswith('＊')
                        or re.match(r'^[가-힣][가-힣 ,.·]*$', lab)):
                lab = None                 # 단위 설명 줄·각주·이어진 한글 문장은 라벨이 아니다
            key = lab or label
            if not key:
                j += 1
                continue
            row = [''] * len(models)
            if len(vals) == 1 and len(models) > 1:
                row = [vals[0][1]] * len(models)          # 가운데 정렬된 공통값
            else:
                for x, v in vals:
                    k = min(range(len(starts)), key=lambda n: abs(starts[n] - x))
                    row[k] = (row[k] + ' ' + v).strip()
            if lab and not any(row) and label and any(specs.get(label, [])):
                # 값 없이 라벨만 있는 줄 = 두 줄로 접힌 라벨의 아랫줄
                # ('Pumping' / 'Speed(50/60Hz)'). 앞 라벨 이름에 이어 붙인다.
                merged = (label + ' ' + lab).strip()
                specs[merged] = specs.pop(label)
                label = merged
                j += 1
                continue
            if lab:
                label = lab
                labx.append(gg[0][0])
                specs[lab] = row
            else:
                for n in range(len(models)):              # 둘째 줄은 이어 붙인다
                    if row[n]:
                        specs[key][n] = (specs[key][n] + ' / ' + row[n]).strip(' /')
            j += 1
        if specs:
            tables.append({'title': title or title_hint, 'models': models, 'specs': specs})
        i = j
    return tables


def main():
    if not os.path.exists(PDF):
        print('브로슈어 PDF 를 찾을 수 없다: %s' % PDF)
        return 1
    txt = subprocess.run(['pdftotext', '-layout', PDF, '-'],
                         capture_output=True).stdout.decode('utf-8', 'replace')
    pages = txt.split('\f')
    # 목차: '04. Furnace......20' → 20쪽부터 04번 섹션. 본문에서 제목을 다시 찾으면
    # 표만 있는 페이지에서 앞 섹션이 그대로 이어져 엉뚱한 이름이 붙는다.
    toc = sorted((int(pg), '%s. %s' % (no, name.strip()))
                 for no, name, pg in re.findall(
                     r'^\s*(\d{2})\.\s*([A-Za-z][A-Za-z &/배터리시험챔버]+?)\.{3,}(\d{1,3})\s*$',
                     txt, re.M))

    def sec_of(page):
        cur = ''
        for start, name in toc:
            if page >= start:
                cur = name
        return cur

    out = []
    for n, p in enumerate(pages):
        section = sec_of(n + 1)
        for t in parse_page(p, section):
            t['page'] = n + 1
            t['section'] = section
            out.append(t)
    models = {}
    for t in out:
        for k, mdl in enumerate(t['models']):
            if not MODELISH.match(mdl):
                continue
            d = models.setdefault(mdl, {'model': mdl, 'section': t['section'],
                                        'title': t['title'], 'page': t['page'], 'specs': {}})
            for lab, vals in t['specs'].items():
                v = vals[k].strip()
                if v and lab not in d['specs']:
                    d['specs'][lab] = v
    print('페이지 %d · 표 %d개 · 모델 %d종' % (len(pages), len(out), len(models)))
    cnt = {}
    for d in models.values():
        cnt[len(d['specs'])] = cnt.get(len(d['specs']), 0) + 1
    print('모델당 사양 항목 수 분포:', dict(sorted(cnt.items())))
    if '--write' in sys.argv:
        with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'_doc': ['삼흥 2026 국문 브로슈어에서 자동 추출한 모델별 사양.',
                                '생성: python _ops/sh_brochure_parse.py --write',
                                '원본: 2026_SH Scientific brochure-KO.pdf (실험실닷컴 웹카다로그)',
                                '손으로 고치지 말 것 — 원본이 바뀌면 다시 돌린다.'],
                       'models': models}, f, ensure_ascii=False, indent=1)
        print('저장: _build/sh_brochure_specs.json (%d종)' % len(models))
    return 0


if __name__ == '__main__':
    sys.exit(main())
