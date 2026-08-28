# -*- coding: utf-8 -*-
"""웹 제품(gaossunion.com) ↔ SQL 가격행 매칭표 생성"""
import io, os, re, csv, collections

BASE = os.path.dirname(os.path.abspath(__file__))
SQL  = os.path.join(BASE, '..', '..', 'rndsetup_products.sql')

def fld(line):
    k = line.find('VALUES (')
    if k < 0: return None
    b = line[k+8:].rstrip().rstrip(';').rstrip(')')
    out=[];cur='';q=False;i=0
    while i < len(b):
        c=b[i]
        if q:
            if c=="'" and i+1<len(b) and b[i+1]=="'": cur+="'";i+=2;continue
            if c=="'": q=False;i+=1;continue
            cur+=c;i+=1;continue
        if c=="'": q=True;i+=1;continue
        if c==',': out.append(cur.strip());cur='';i+=1;continue
        cur+=c;i+=1
    out.append(cur.strip()); return out

# ---- SQL 838행
rows=[]
for l in io.open(SQL, encoding='utf-8'):
    f=fld(l)
    if f and f[0].startswith('GU-'):
        rows.append(dict(sku=f[0], sobun=f[6], model=f[7], opt=f[9], name=f[10],
                         price=int(f[15]) if f[15].isdigit() else 0, url=f[17]))

# ---- 웹 제품
web=[]
for fn in ('01_electrode.tsv','02_insitu.tsv','03_cell.tsv','04_rest.tsv'):
    p=os.path.join(BASE,fn)
    if not os.path.exists(p): continue
    for i,r in enumerate(csv.reader(io.open(p,encoding='utf-8'), delimiter='\t')):
        if i==0 or not r or not r[0].strip(): continue
        web.append(dict(id=r[0], cat=r[1], zh=r[2] if len(r)>2 else '',
                        ko=r[3] if len(r)>3 and fn=='04_rest.tsv' else '',
                        spec=r[3] if len(r)>3 and fn!='04_rest.tsv' else ''))

# ---- 모델코드 추출
CODE = re.compile(r'(?<![A-Za-z0-9])('
  r'C0\d{2}(?:-[0-9A-Za-z]+)*'      # C001, C007-10, C013-UV4000
  r'|P00\d(?:-\d+)?'                # P001 P002 P003
  r'|PB00\d|TB00\d|B00\d(?:-\d)?'   # 배터리
  r'|QG-20(?:-\d)?|MTR-[0-9A-Za-z-]+|XAFS-\d|UV2600(?:-\d)?|DQ-\d'
  r'|MEA-[0-9A-Za-z-]+|EC200-\d+|EC-MEA|ECstat-\w+|ECboost-\d+|ECR-\d+\w*'
  r'|N1\d{2}|IFA-[0-9A-Za-z]|PT-X|PT-\d|SUS-[0-9]|GC-\d|AU-X|TI-[0-9X]'
  r'|10101\d?|1010\d{2}|19008|R\d{4}\w*|PK-\d{4}|Hg-\d{4}|CP\d0/CP\d0'
  r')(?![A-Za-z0-9])')

def codes(s): return sorted(set(CODE.findall(s or '')))

# SQL 모델 → 행 인덱스
by_model=collections.defaultdict(list)
for r in rows:
    m=r['model'].strip()
    if m and m!='—': by_model[m].append(r)
    for c in codes(r['model']+' '+r['name']): by_model[c].append(r)

CATMAP={'작업전극':'작업전극','기준전극':'기준전극','상대전극':'상대전극','회전전극':'회전전극',
 '전극클램프':'전극 클램프·홀더','전기화학재료':'전기화학 재료','전극연마':'전극 연마용품',
 '일반셀':'단실 유리 전해셀','H형셀':'격막 교환형 전해셀','석영분광셀':'부식 시험·석영 전해셀',
 'CO2RR음극촉매':'CO2RR 촉매','CO2RR양극촉매':'CO2RR 촉매','CO2RR고체전해질':'CO2RR 촉매',
 'MEA막전극':'막전극(MEA) 전해셀','Flowcell':'가스확산 전해셀','PressureCell':'고압 전기화학 셀·계측 장비',
 '리튬전지in-situ':'배터리 테스트 셀','전기화학in-situ':'in-situ 분광전기화학 셀','계측장비':'전기화학 계측 · 주변 장비'}

out=[]; matched_sku=set()
for w in web:
    cs=codes(w['zh'])
    hits=[]
    for c in cs:
        for r in by_model.get(c,[]):
            if r['sku'] not in [h['sku'] for h in hits]: hits.append(r)
    if not hits:  # 코드가 없으면 분류로 후보 좁히기
        sob=CATMAP.get(w['cat'])
        if sob: hits=[r for r in rows if r['sobun']==sob][:0]
    for h in hits: matched_sku.add(h['sku'])
    pr=[h['price'] for h in hits if h['price']>0]
    out.append(dict(w=w, codes=cs, n=len(hits),
                    lo=min(pr) if pr else 0, hi=max(pr) if pr else 0,
                    skus=[h['sku'] for h in hits][:6]))

print('웹 제품 %d · SQL 행 %d' % (len(web), len(rows)))
print('가격행이 붙은 웹 제품 : %d' % sum(1 for o in out if o['n']))
print('가격행이 없는 웹 제품 : %d' % sum(1 for o in out if not o['n']))
print('어느 웹 제품에도 안 붙은 SQL 행 : %d' % sum(1 for r in rows if r['sku'] not in matched_sku))

with io.open(os.path.join(BASE,'05_매칭표.tsv'),'w',encoding='utf-8') as f:
    f.write('web_id\tcat\tname_zh\t추출코드\t매칭행수\t최저가\t최고가\t대표SKU\n')
    for o in out:
        w=o['w']
        f.write('\t'.join([w['id'],w['cat'],w['zh'],'|'.join(o['codes']),str(o['n']),
                           str(o['lo']),str(o['hi']),','.join(o['skus'])])+'\n')

with io.open(os.path.join(BASE,'06_미매칭_SQL.tsv'),'w',encoding='utf-8') as f:
    f.write('sku\t소분\t모델\t옵션\t정가\n')
    c=collections.Counter()
    for r in rows:
        if r['sku'] not in matched_sku:
            c[r['sobun']]+=1
            f.write('\t'.join([r['sku'],r['sobun'],r['model'],r['opt'][:40],str(r['price'])])+'\n')
    print('\n미매칭 SQL 행 — 소분별')
    for k,v in c.most_common(): print('  %-24s %3d' % (k,v))

print('\n가격행이 안 붙은 웹 제품 (분류별)')
cc=collections.Counter(o['w']['cat'] for o in out if not o['n'])
for k,v in cc.most_common(): print('  %-16s %3d' % (k,v))
