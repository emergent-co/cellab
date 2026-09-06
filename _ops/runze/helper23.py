# -*- coding: utf-8 -*-
import json,os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC={p['slug']:p for p in json.load(open(os.path.join(ROOT,'_ops/runze/runze_batch23.json'),encoding='utf8'))}
META=json.load(open(os.path.join(ROOT,'_ops/runze/img_meta23.json'),encoding='utf8'))
HEAD={'Model No.':'모델 번호 (Model No.)','Model':'모델 (Model)','Metric Size':'미터 사이즈 (Metric)',
 'Metric/Inch Size':'미터/인치 사이즈','Inch Size':'인치 사이즈','Metric size':'미터 사이즈',
 'Material':'재질 (Material)','Color':'색상 (Color)','Barbed End (mm)':'바브 끝단 (mm)',
 'Barbed End(mm)':'바브 끝단 (mm)','Barbed End       (∅3.5/2.4/1.6)':'바브 끝단 (mm)','Barbed End (∅3.5)':'바브 끝단 (mm)',
 'Soft Tubing ID (mm)':'연질 튜브 내경 (mm)','Soft Tubing ID(mm)':'연질 튜브 내경 (mm)',
 'Description':'설명 (Description)','Tube ID (mm)':'튜브 내경 (mm)','Male Thread':'수나사 (Male thread)',
 'Female Thread':'암나사 (Female thread)','Thread':'나사 (Thread)','Tube OD':'튜브 외경 (Tube OD)',
 'Female Tubing OD (mm)':'튜브 외경 (mm)','Size':'사이즈 (Size)','SKU':'SKU','Qty':'수량 (Qty)',
 'Product Name':'제품명 (Product name)','ID (mm)':'내경 ID (mm)','OD (mm)':'외경 OD (mm)','WT (mm)':'두께 WT (mm)',
 'Tube No.':'튜브 번호 (Tube No.)','Type':'형식 (Type)','Application':'용도 (Application)','Note':'비고 (Note)',
 'Pressure Rating Room Temp. (psi /MPa)':'상온 압력 정격 (psi / MPa)','Pressure Rating       Room Temp.     (psi /MPa)':'상온 압력 정격 (psi / MPa)',
 'Thread Type':'나사 형식 (Thread type)','Port':'포트 (Port)','Length':'길이 (Length)','Volume':'용량 (Volume)'}
def tbl(slug,idx,heading,note=None,head=None):
    t=SRC[slug]['tables'][idx]
    h=head or [HEAD.get(c.strip(),c.strip()) for c in t[0]]
    n=len(h)
    rows=[]
    for r in t[1:]:
        r=list(r)
        r=(r+['']*n)[:n]
        if any(str(c).strip() for c in r): rows.append(r)
    v={"heading":heading,"head":h,"rows":rows}
    if note: v["note"]=note
    return v
def gal(slug,n=None):
    g=META[slug]['gal']; return g[:n] if n else g
def figs(items):
    h='<div class="det-imgs">'
    for f,c in items: h+='<figure><img src="/img/runze/%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>'%(f,c.replace('"',''),c)
    return h+'</div>'
def dets(slug,label='제조사 상세 자료',cap=None):
    d=META[slug]['det']
    if not d: return ''
    n=len(d)
    return figs([(f,(cap[i] if cap and i<len(cap) else '%s (%d/%d)'%(label,i+1,n))) for i,f in enumerate(d)])
KW=[["#RunzeFluid","/brands/runze/"],["#실험장비카탈로그","/product/"]]
def SRCU(s): return {"url":"https://www.runzefluid.com/products/%s.html"%s,"label":"Runze Fluid 제품 페이지"}
def REL(e=''): return '유체 연결: <a href="/product/">전 제품 통합 카탈로그</a> · <a href="/brands/runze/">Runze Fluid 전체</a> · <a href="/contact/">견적·기술 문의</a>'+e
def add(products):
    p=os.path.join(ROOT,'_build/products/runze.json'); D=json.load(open(p,encoding='utf8'))
    have={x['slug'] for x in D['products']}
    n=0
    for x in products:
        if x['slug'] in have: continue
        D['products'].append(x); n+=1
    json.dump(D,open(p,'w',encoding='utf8'),ensure_ascii=False,indent=1)
    print('추가',n,'| 총',len(D['products']))
