# 상세페이지 구매창(data-models)의 판매가를 지금 규칙으로 다시 계산한다.
#   국내(3% 할인) 항목 = 'd'(정가)가 있는 것만 손댄다. 해외 발주 항목은 건드리지 않는다.
#   판매가 = int(정가 * 0.97)      ← 2026-09-05 «만원 미만 버림» 제거
import glob, io, json, re, sys

def disc(p): return int(p * 0.97)

apply = '--apply' in sys.argv
changed = files = 0
for f in sorted(glob.glob('brands/**/index.html', recursive=True)):
    t = io.open(f, encoding='utf-8').read()
    out, hit = t, 0
    for m in re.finditer(r"data-models='(\[.*?\])'", t, re.S):
        try: rows = json.loads(m.group(1).replace('&#39;', "'"))
        except Exception: continue
        new = []
        for r in rows:
            d = r.get('d')
            if d:                                   # 국내 — 정가가 있는 항목만
                want = disc(d)
                if r.get('x') != want or r.get('p') != want:
                    r['x'] = want; r['p'] = want; hit += 1
            new.append(r)
        if hit:
            out = out.replace(m.group(0),
                "data-models='" + json.dumps(new, ensure_ascii=False).replace("'", '&#39;') + "'")
    if hit:
        files += 1; changed += hit
        if apply: io.open(f, 'w', encoding='utf-8', newline='').write(out)
print(('고침' if apply else '고칠 것') + f': 파일 {files}개 · 모델 {changed}개')
