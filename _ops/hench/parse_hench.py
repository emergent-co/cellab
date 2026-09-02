# -*- coding: utf-8 -*-
"""hench_scrape2.json → 구조화 (CSV + MD). 두 가지 스펙 표기(콜론형/무콜론형) 모두 처리."""
import json, re, csv, collections, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(HERE, 'hench_scrape2.json'), encoding='utf-8'))

CAT = {'/en/Product/377918.html': '프레스', '/en/Product/377919.html': '다이/몰드',
       '/en/Product/610213.html': '기타'}

def body_of(d):
    t = d['intro']
    for cut in ('Inquiry now', '\nshare'):
        i = t.find(cut)
        if i > 0: t = t[:i]
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    name = lines[0] if lines else ''
    model_line = lines[1] if len(lines) > 1 else ''
    body = '\n'.join(lines[2:]).strip() or (model_line if len(lines) <= 2 else '')
    return name, model_line, body

def norm(s):
    return re.sub(r'\s+', ' ', s.replace('：', ':').replace('（', '(').replace('）', ')')).strip(' :·')

# 1) 콜론형에서 라벨 어휘 수집
COLON = re.compile(r'([A-Za-z][A-Za-z.\s/()\-]{1,34}?)\s*[:：]\s*')
vocab = collections.Counter()
for d in D:
    _, _, b = body_of(d)
    if ':' in b or '：' in b:
        for lab in COLON.findall(b):
            vocab[norm(lab)] += 1

EXTRA = ['Model', 'Material', 'Indenter hardness', 'Sample size', 'Cavity depth', 'Dimensions',
         'Weight', 'Pressure', 'Piston diameter', 'Cylinder diameter', 'Construction',
         'Pressure display', 'Max. piston stroke', 'Piston stroke', 'Pressure stability',
         'Press process', 'Pressure holding time', 'Pressure holding', 'Dies heating temperature',
         'Temperature control accuracy', 'Temperature control by thermostat', 'Table diameter',
         'Number of columns', 'Valid space', 'Equipment weight', 'Overall structure',
         'Configuration description', 'Pressure range', 'Pressure conversion', 'Pressure gauge',
         'Instrument model', 'Punching pressure', 'Punch stroke', 'Receiving box', 'Slice size',
         'Suitable material', 'Standard tool head', 'Mold material', 'Applicable model',
         'Heating temperature', 'Power', 'Voltage', 'Vacuum degree', 'Sample thickness',
         'Effective space', 'Motor power', 'Control mode', 'Display', 'Accuracy', 'Size',
         'Product name', 'Specification', 'Feature', 'Application', 'Note']
LABELS = sorted(set(list(vocab.keys()) + EXTRA), key=len, reverse=True)
LAB_RX = re.compile('(' + '|'.join(re.escape(l) for l in LABELS) + ')')

def parse(body):
    b = body.replace('：', ':')
    if re.search(r'[A-Za-z]\s*:\s*\S', b):
        parts = re.split(r'(?=[A-Z][A-Za-z.\s/()\-]{1,34}?\s*:)', b)
        out = []
        for p in parts:
            if ':' not in p: continue
            k, v = p.split(':', 1)
            k, v = norm(k), norm(v)
            if k and v: out.append((k, v))
        if out: return out, ''
    # 무콜론형 — 라벨 어휘로 절단
    idx = [(m.start(), m.end(), m.group(1)) for m in LAB_RX.finditer(b)]
    keep, last = [], -1
    for s, e, g in idx:
        if s >= last: keep.append((s, e, g)); last = e
    out = []
    for i, (s, e, g) in enumerate(keep):
        nxt = keep[i + 1][0] if i + 1 < len(keep) else len(b)
        v = norm(b[e:nxt])
        if v: out.append((norm(g), v))
    covered = sum(e - s for s, e, _ in keep) + sum(len(v) for _, v in out)
    return out, ('' if covered >= len(b) * 0.7 else b)

rows = []
for d in D:
    name, model_line, body = body_of(d)
    kv, raw = parse(body)
    model = model_line
    for k, v in kv:
        if k.lower() in ('model', 'instrument model', 'product name'):
            model = v; break
    rows.append(dict(cat=CAT.get(d['cat'], d['cat']), name=name, model=model,
                     url='http://www.henchld.com' + d['url'], imgs=len(d['ids']),
                     nkv=len(kv), spec=json.dumps(dict(kv), ensure_ascii=False),
                     unparsed=raw[:400], ids=' '.join(d['ids'])))

with io.open(os.path.join(HERE, 'hench_products.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['cat', 'name', 'model', 'url', 'imgs', 'nkv', 'spec', 'unparsed', 'ids'])
    w.writeheader(); w.writerows(rows)

print('총', len(rows), '항목 · 미파싱', sum(1 for r in rows if r['unparsed']))
for c, n in collections.Counter(r['cat'] for r in rows).items(): print(' ', c, n)
