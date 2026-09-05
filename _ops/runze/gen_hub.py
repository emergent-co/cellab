# -*- coding: utf-8 -*-
"""_build/products/runze.json -> brands/runze/index.html (dscard 생성)"""
import json, re, os, html as H
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D=json.load(open(os.path.join(ROOT,'_build/products/runze.json'),encoding='utf8'))
def cat_of(p):
    c=p.get('category','')+' '+p.get('name','')
    if '밸브' in c and '헤드' not in c: return 'valve','밸브'
    if '밸브 헤드' in c or '밸브헤드' in c: return 'valve','밸브 부품'
    if '펌프' in c: return 'syr','펌프'
    if '튜브' in c or '튜빙' in c or '호스' in c: return 'tubing','튜빙'
    if '피팅' in c or '어댑터' in c or '커넥터' in c or '조인트' in c or '페럴' in c: return 'fitting','피팅'
    return 'fluidacc','액세서리'
def strip(s): return re.sub(r'<[^>]+>','',s or '')
cards=[]
for p in D['products']:
    cat,badge=cat_of(p)
    img=p['images'][0]
    nm=strip(p.get('sub',''))
    d=strip(p.get('answer',''))
    if len(d)>110: d=d[:108].rsplit(' ',1)[0]+'…'
    txt=' '.join([p['name'],p.get('name_en',''),nm,strip(p.get('category','')),
                  ' '.join(k[0].lstrip('#') for k in p.get('keywords',[]))]).lower()
    txt=re.sub(r'\s+',' ',txt).strip()
    cards.append('<article class="dscard" data-cat="%s" data-text="%s">\n'
      '  <div class="dscard-im"><img src="/img/runze/%s" alt="Runze Fluid %s" loading="lazy" width="800" height="600"><div class="dscard-bdg"><span class="b y">%s</span></div></div>\n'
      '  <div class="dscard-bd">\n'
      '    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/runze/%s/">%s</a></h3>\n'
      '    <div class="dscard-nm">%s</div>\n'
      '    <p class="dscard-d">%s</p>\n'
      '    <p class="dscard-p">가격 문의</p>\n'
      '  </div>\n</article>'%(cat,H.escape(txt,quote=True),img,H.escape(p['name']),badge,
                              p['slug'],H.escape(p['name']),H.escape(nm),H.escape(d)))
out=['<!DOCTYPE html>','<html lang="ko">','<head>','<meta charset="UTF-8">',
 '<meta name="robots" content="noindex">','<meta http-equiv="refresh" content="0;url=/product/">',
 '<title>Runze Fluid 제품 — 통합 카탈로그로 이동</title>','</head>','<body>',
 '<p><a href="/product/">전 제품 통합 카탈로그로 이동</a></p>']+cards+['</body>','</html>','']
open(os.path.join(ROOT,'brands/runze/index.html'),'w',encoding='utf8').write('\n'.join(out))
print('dscard',len(cards),'장 생성')
