# -*- coding: utf-8 -*-
"""leadfluid.com.cn 원문 HTML -> 구조화 JSON. 결측률 리포트 포함."""
import gzip, json, re
from bs4 import BeautifulSoup
from collections import Counter, defaultdict

SRC = '_ops/leadfluid_cn/leadfluid_cn_rawhtml_170.json.gz'
OUT = '_ops/leadfluid_cn/parsed_170.json'
CATKO = {'rdb':'연동펌프','wsrdb':'마이크로펌프','odm':'ODM연동펌프','zsb':'시린지펌프',
         'jyb':'스퀴즈펌프','clb':'기어펌프','rdbbt':'펌프헤드','rdbrg':'펌프튜브','rdbpj':'부속품'}

def cl(s): return re.sub(r'\s+',' ',(s or '')).strip()

def parse(key, html):
    cat, path = key.split('|',1)
    s = BeautifulSoup(html, 'html.parser')
    title = cl(s.title.get_text() if s.title else '')
    model = cl(re.split(r'-雷弗|_雷弗', title)[0])
    box = s.select_one('.text.wow') or s.select_one('.text')
    h2 = cl(box.h2.get_text()) if box and box.h2 else ''
    tips = [cl(x.get_text()) for x in box.select('.tips span')] if box else []
    desc = cl(' '.join(p.get_text() for p in box.find_all('p'))) if box else ''
    secs = []
    for div in s.select('div[class*=section]'):
        t = div.select_one('.title')
        if not t: continue
        h = cl(t.get_text())
        if not h: continue
        body = {'h': h, 'items': [], 'tables': [], 'imgs': []}
        for li in div.select('.box li'):
            v = cl(li.get_text())
            if v: body['items'].append(v)
        for tb in div.select('table'):
            rows = []
            for tr in tb.select('tr'):
                cells = [cl(td.get_text()) for td in tr.find_all(['td','th'])]
                if any(cells): rows.append(cells)
            if rows: body['tables'].append(rows)
        for im in div.select('img'):
            u = im.get('src') or im.get('data-src') or ''
            if 'res.leadfluid' in u: body['imgs'].append(u)
        if body['items'] or body['tables'] or body['imgs']: secs.append(body)
    imgs, seen = [], set()
    for im in s.select('img'):
        u = im.get('src') or im.get('data-src') or ''
        if 'res.leadfluid' in u and re.search(r'(productCatPic|richText|videoCover)', u):
            if u not in seen: seen.add(u); imgs.append(u)
    pdfs = []
    for a in s.select('a[href]'):
        hh = a['href']
        if re.search(r'\.pdf', hh, re.I) and hh not in pdfs: pdfs.append(hh)
    return {'cat':cat,'cat_ko':CATKO.get(cat,cat),'url':'https://www.leadfluid.com.cn'+path,
            'model':model,'h2':h2,'tips':tips,'desc':desc,'sections':secs,'imgs':imgs,'pdfs':pdfs}

def main():
    R = json.loads(gzip.open(SRC,'rt',encoding='utf-8').read())
    out = [parse(k,v) for k,v in R.items()]
    json.dump({'count':len(out),'items':out}, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    miss = defaultdict(Counter); tot = Counter()
    for x in out:
        c = x['cat_ko']; tot[c] += 1
        feats = sum((sec['items'] for sec in x['sections']), [])
        specrows = sum(len(t) for sec in x['sections'] for t in sec['tables'])
        if not x['model']: miss['model'][c]+=1
        if len(x['desc'])<10: miss['desc'][c]+=1
        if len(feats)<2: miss['feat'][c]+=1
        if specrows<3: miss['spec'][c]+=1
        if not x['imgs']: miss['img'][c]+=1
    print('%-13s %4s %5s %5s %5s %5s %5s' % ('카테고리','건수','모델','설명','특징','사양','사진'))
    for c in sorted(tot, key=lambda k:-tot[k]):
        print('%-13s %4d %5d %5d %5d %5d %5d' % (c,tot[c],miss['model'][c],miss['desc'][c],
              miss['feat'][c],miss['spec'][c],miss['img'][c]))
    n=len(out)
    print('%-13s %4d %5d %5d %5d %5d %5d' % ('합계',n,sum(miss['model'].values()),
          sum(miss['desc'].values()),sum(miss['feat'].values()),
          sum(miss['spec'].values()),sum(miss['img'].values())))
    print('\n결측률: 설명 %.1f%% / 특징 %.1f%% / 사양 %.1f%%' % (
        100*sum(miss['desc'].values())/n, 100*sum(miss['feat'].values())/n,
        100*sum(miss['spec'].values())/n))

main()
