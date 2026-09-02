# -*- coding: utf-8 -*-
"""hench_scrape2.json → hench_products.csv (라벨사전 기반 재파싱)
콜론 유무로 형식을 판별하지 않는다. 제조사가 값 안에도 전각 콜론을 쓰기 때문(Alloy tool steel：Cr12MoV).
알려진 라벨 어휘로만 절단하고, 커버리지가 낮으면 그 제품을 리포트한다."""
import json, re, csv, io, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(HERE, 'hench_scrape2.json'), encoding='utf-8'))
CAT = {'/en/Product/377918.html': '프레스', '/en/Product/377919.html': '다이/몰드',
       '/en/Product/610213.html': '기타'}

LABELS = [
 # 공통
 'Instrument model','Product name','Model','Material','Dimensions','Size','Weight','Equipment weight',
 'Overall structure','Design structure','Construction','Configuration description','Power supply',
 'Equipment power','Ambient temperature','Effective space','Valid space','Available space',
 # 프레스 압력계
 'Pressure range','Pressure limit','Maximum pressure','Pressure conversion','Pressure gauge','Pressure gage',
 'Pressure display','Pressure stability','Pressure mode','Pressure die','Pressure holding time','Pressure holding',
 'Accuracy range','Demoulding pressure','Sealing pressure','Opening pressure',
 # 실린더·구조
 'Cylinder diameter','Piston diameter','Cylinder stroke','Piston stroke','Max. piston stroke','Travel of piston',
 'Table diameter','Working table diameter','Number of columns','Column spacing','Columns',
 # 제어·표시
 'Automatic control','After compaction way','Aftercompaction way','Screen display','Display mode','Display die',
 'Setting method','Passive safety','Safety configuration','Press process',
 # 가열
 'Heating range','Heating plate type','Heating core material','Heat insulation method','Cooling method',
 'Dies heating temperature','Temperature control accuracy','Temperature control by thermostat','Temperature',
 # 다이
 'Indenter hardness','Indenter material','Sample size','Sample thickness','Cavity depth','Cavity material',
 'Mold specifications','Mold material','Die material','Die size','Chamber size','Shelf material',
 'Insulating material','Sealing die','Disconnecting die','Diameter',
 # 슬라이서
 'Punching pressure','Punch stroke','Receiving box','Slice size','Suitable material','Standard tool head',
 # 제조사 표기 변형·누락분 (원문 그대로)
 'Travel ofpiston','Travel of piston','Work space','Working space','Device power supply','Host size',
 'Controller size','Intelligent temperature controller temperature range',
 'Pressure and temperature control accuracy','Temperature control range','Heating temperature',
 'Sealing method','Safety protection','Machine size','Net weight','Gross weight','Voltage','Frequency',
 'Motor power','Control mode','Operation mode','Applicable model','Applicable mold','Note','Remark',
 'Mould material','Punch material','Base material','Surface treatment','Precision','Accuracy',
]
LABELS = sorted(set(LABELS), key=len, reverse=True)
RX = re.compile('(' + '|'.join(re.escape(l) for l in LABELS) + r')\s*[:：]?\s*', re.I)

def body_of(d):
    t = d['intro']
    for cut in ('Inquiry now', '\nshare'):
        i = t.find(cut)
        if i > 0: t = t[:i]
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    name = lines[0] if lines else ''
    model_line = lines[1] if len(lines) > 1 else ''
    body = ' '.join(lines[2:]).strip() or (model_line if len(lines) <= 2 else '')
    return name, model_line, body

def norm(v):
    v = re.sub(r'\s+', ' ', v).strip(' :：·、,')
    return v

def is_label_pos(body, m):
    """라벨로 인정하는 위치: 문두 / 값에 붙어있음(앞이 공백 아님) / 바로 뒤에 콜론.
    문장 한가운데의 일반 낱말(예: 'The size of ...', 'die temperature exceeds')을 거른다."""
    s = m.start()
    if s == 0:
        return True
    if body[s - 1] not in ' \t':
        return True
    tail = body[m.end(1):m.end(1) + 2]
    return tail[:1] in (':', '：') or tail[:2].strip()[:1] in (':', '：')


def parse(body):
    hits = [(m.start(), m.end(), m.group(1)) for m in RX.finditer(body) if is_label_pos(body, m)]
    keep, last = [], -1
    for s, e, g in hits:
        if s >= last:
            keep.append((s, e, g)); last = e
    out, used = [], 0
    for i, (s, e, g) in enumerate(keep):
        nxt = keep[i + 1][0] if i + 1 < len(keep) else len(body)
        v = norm(body[e:nxt])
        if v:
            out.append((g, v)); used += (nxt - s)
    head = keep[0][0] if keep else len(body)
    cov = used / len(body) if body else 1.0
    return out, cov, norm(body[:head])

rows, low = [], []
famcov = collections.defaultdict(list)
for d in D:
    name, model_line, body = body_of(d)
    kv, cov, pre = parse(body)
    model = model_line
    for k, v in kv:
        if k.lower() in ('instrument model', 'model', 'product name'):
            model = v; break
    cat = CAT.get(d['cat'], d['cat'])
    famcov[cat].append(cov)
    if cov < 0.9: low.append((round(cov, 2), name[:44], pre[:40]))
    rows.append(dict(cat=cat, name=name, model=model, url='http://www.henchld.com' + d['url'],
                     imgs=len(d['ids']), nkv=len(kv), cov=round(cov, 3),
                     spec=json.dumps(dict(kv), ensure_ascii=False), ids=' '.join(d['ids'])))

with io.open(os.path.join(HERE, 'hench_products.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['cat','name','model','url','imgs','nkv','cov','spec','ids'])
    w.writeheader(); w.writerows(rows)

print('총 %d종' % len(rows))
for c, v in famcov.items():
    print('  %-8s 평균 커버리지 %.3f · 0.9미만 %d건' % (c, sum(v)/len(v), sum(1 for x in v if x < 0.9)))
print('\n커버리지 0.9 미만 (%d건):' % len(low))
for c, n, pre in sorted(low)[:12]: print('  %.2f  %-44s  앞잔여="%s"' % (c, n, pre))
