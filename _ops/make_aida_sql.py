# -*- coding: utf-8 -*-
"""AIDA 248종을 rndsetup_products.sql 에 반영한다.

원장(SSOT)은 SQL 이라는 원칙에 따라, 이미 만들어진 brands/aida/*/index.html 의
data-models(제품가격 1개, VAT 별도)를 읽어 INSERT 행을 만든다.

· sku          AD-<모델> (비영숫자는 -, 중복 시 -2, -3 …)
· retail_price 페이지의 제품가격 = (Ex-factory USD × 1,400) × 1.45, 1,000원 반올림
               가오스 −5,000 하한이 걸린 행은 그 값이 그대로 들어간다
· supply_price NULL — 매입 조건 미확정. 확정되면 이 스크립트를 고쳐 채운다
· 0원 행은 넣지 않는다 (근거 없는 가격 금지 원칙)

기존 AD- 행이 있으면 전부 지우고 다시 넣는다 (멱등).
"""
import io, os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL  = os.path.join(ROOT, 'rndsetup_products.sql')
COLS = ("sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,"
        "supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,"
        "attr3_n,attr3_v,attr4_n,attr4_v,status")

def q(v):
    if v is None: return 'NULL'
    if isinstance(v, int): return str(v)
    return "'" + str(v).replace("'", "''") + "'"

def strip(s): return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', s)).strip()

def pages():
    d = os.path.join(ROOT, 'brands', 'aida')
    for s in sorted(os.listdir(d)):
        f = os.path.join(d, s, 'index.html')
        if not os.path.isfile(f): continue
        t = io.open(f, encoding='utf-8').read()
        h1  = strip(re.search(r'<h1 class="dt-name">(.*?)(?:<span|</h1>)', t, re.S).group(1))
        ans = strip(re.search(r'<p class="dt-ans">(.*?)</p>', t, re.S).group(1))
        cat = re.search(r'"category":\s*"전기화학 · ([^"]+)"', t)
        img = re.search(r'<div class="dt-img"><img src="([^"]+)"', t)
        spec = re.findall(r'<tr><th>(.*?)</th><td>(.*?)</td></tr>', t, re.S)[:4]
        mods = json.loads(re.search(r"data-models='(.*?)'></div>", t).group(1).replace('&#39;', "'"))
        yield dict(slug=s, h1=h1, ans=ans, cat=cat.group(1) if cat else '전기화학',
                   img=img.group(1) if img else '',
                   spec=[(strip(a), strip(b)) for a, b in spec], mods=mods)

def main(apply=False):
    src = io.open(SQL, encoding='utf-8').read()
    lines = src.split('\n')
    before = len(lines)
    lines = [l for l in lines if "VALUES ('AD-" not in l]
    removed = before - len(lines)

    gmax = max([int(m) for m in re.findall(r"VALUES \('[^']*',(\d+),", src)] or [0])
    rows, seen = [], {}
    g = gmax
    for p in pages():
        g += 1
        for m in p['mods']:
            if not m.get('x'): continue
            base = 'AD-' + re.sub(r'[^A-Za-z0-9]+', '-', m['m']).strip('-').upper()
            sku = base
            if sku in seen:
                seen[base] += 1; sku = '%s-%d' % (base, seen[base])
            else:
                seen[base] = 1
            spec = m.get('s') or ''
            attrs = []
            for k, v in p['spec']:
                attrs += [k[:20], v[:60]]
            attrs += [None] * (8 - len(attrs))
            vals = [sku, g, 'AIDA', 'TianJin AIDA Science-Technology(天津艾达恒晟)', '중국',
                    '전기화학', p['cat'], m['m'], '규격', spec or m['m'],
                    '아이다 %s %s' % (p['h1'], m['m']),
                    p['ans'][:300], None, 'ea',
                    None,                    # supply_price — 매입 조건 미확정
                    m['x'],
                    ('https://rndsetup.com' + p['img']) if p['img'] else None,
                    'https://rndsetup.com/brands/aida/%s/' % p['slug'],
                    None, None, None] + attrs[:8] + ['등록가능']
            rows.append('INSERT INTO products (%s) VALUES (%s);' % (COLS, ','.join(q(v) for v in vals)))

    out = '\n'.join(lines).rstrip('\n') + '\n' + '\n'.join(rows) + '\n'
    print('기존 AD- 행 제거 %d / 새로 %d행 (%d그룹)' % (removed, len(rows), g - gmax))
    # 검증
    assert all(r.count('INSERT INTO products') == 1 for r in rows)
    assert len({r.split("VALUES ('")[1].split("'")[0] for r in rows}) == len(rows), 'SKU 중복'
    assert not [r for r in rows if re.search(r',NULL,0,', r)], '0원 행 존재'
    if apply:
        io.open(SQL, 'w', encoding='utf-8').write(out)
        print('SQL 저장 —', len(out.split('\n')), '줄')
    else:
        print('(드라이런)')

main('--apply' in sys.argv)
