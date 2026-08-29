# -*- coding: utf-8 -*-
"""gaossunion.com 기준 제품 페이지 생성기.
   웹 = 제품 정체·사양 / SQL = 가격.  한 제품 = 한 페이지."""
import io, os, re, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL  = io.open(os.path.join(ROOT,'_ops','tpl','product.html'), encoding='utf-8').read()
OUT  = os.path.join(ROOT,'brands','gaossunion')

def esc(t): return html.escape(t, quote=True)


# ---------- SQL 가격행 자동 추출 ----------
_SQLROWS=None
def sqlrows():
    global _SQLROWS
    if _SQLROWS is None:
        _SQLROWS=[]
        def fld(line):
            k=line.find('VALUES (')
            if k<0: return None
            b=line[k+8:].rstrip().rstrip(';').rstrip(')')
            out=[];cur='';q=False;i=0
            while i<len(b):
                c=b[i]
                if q:
                    if c=="'" and i+1<len(b) and b[i+1]=="'": cur+="'";i+=2;continue
                    if c=="'": q=False;i+=1;continue
                    cur+=c;i+=1;continue
                if c=="'": q=True;i+=1;continue
                if c==',': out.append(cur.strip());cur='';i+=1;continue
                cur+=c;i+=1
            out.append(cur.strip()); return out
        for l in io.open(os.path.join(ROOT,'rndsetup_products.sql'),encoding='utf-8'):
            f=fld(l)
            if f and f[0].startswith('GU-'):
                _SQLROWS.append(dict(sku=f[0],sobun=f[6],model=f[7],opt=f[9],name=f[10],
                                     price=int(f[15]) if f[15].isdigit() else 0))
    return _SQLROWS

def rows_by(sobun=None, name_has=None, model_re=None):
    """SQL에서 가격행을 통째로 뽑는다 — 손으로 옮겨 적지 않는다."""
    out=[]
    for r in sqlrows():
        if sobun and r['sobun']!=sobun: continue
        if name_has and name_has not in r['name']: continue
        if model_re and not re.search(model_re, r['model'] or ''): continue
        out.append((r['model'], r['opt'], r['price']))
    return out

# ---------- 조각 생성기 ----------
def autoimgs(slug):
    """img/gaossunion/<slug>-N.jpg 를 번호순으로 자동 수집 — cfg에 imgs를 적지 않아도 된다"""
    d=os.path.join(ROOT,'img','gaossunion')
    fs=[f for f in os.listdir(d) if re.match(r'^%s-\d+\.jpg$'%re.escape(slug), f)]
    return sorted(fs, key=lambda f:int(re.search(r'-(\d+)\.jpg$',f).group(1)))

def hero(slug, alt, imgs):
    """imgs: [파일명] — 첫 장이 대표. 비어 있으면 갤러리 자체를 넣지 않는다"""
    if not imgs:
        return ''
    h = ('<div class="dt-img"><img src="/img/gaossunion/%s" alt="%s 제품 사진 (가오스유니온 Gaoss Union)" '
         'loading="lazy" onerror="this.closest(\'.dt-img\').style.display=\'none\'"></div>\n'
         '<div class="dt-thumbs">' % (imgs[0], esc(alt)))
    for n,f in enumerate(imgs,1):
        h += ('<button type="button" data-src="/img/gaossunion/%s" onclick="agSwap(this)">'
              '<img src="/img/gaossunion/%s" alt="%s 제품 사진 %d" loading="lazy" '
              'onerror="this.parentElement.style.display=\'none\'"></button>' % (f,f,esc(alt),n))
    h += '</div>\n<script>function agSwap(b){var i=b.closest(".dt-col").querySelector(".dt-img img");if(i)i.src=b.dataset.src;}</script>\n'
    return h

def head(h1, sub, answer, summary, quote):
    return ('<h1 class="dt-name">%s <span style="font-size:.5em;color:#9A9A9A">%s</span></h1>\n'
            '<p class="dt-ans">%s</p>\n<p class="dt-sum">%s</p>\n'
            '<button type="button" class="qbtn" data-quote="%s">제품문의</button>\n'
            % (h1, sub, answer, summary, esc(quote)))

def buybox(h1, models_json):
    """3번째 그리드 열 — 제품문의 버튼 오른쪽"""
    return ('<div id="buybox" class="bb dt-buy" data-name="%s" data-models=\'%s\'></div>'
            % (esc(h1), models_json))

def spec_tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>'%r for r in rows)
            + '</tbody></table></div>')

def price_tbl(rows, headers=('모델','규격','정가(VAT 별도)')):
    h='<div class="pkg-tblwrap"><table class="pkg-tbl pkg-opt"><thead><tr>'+''.join('<th>%s</th>'%x for x in headers)+'</tr></thead><tbody>'
    for m,spec,p in rows:
        pr = ('<b>%s원</b>'%format(p,',')) if p else '<b>문의</b>'
        sp = '' if spec==m else spec          # 모델명과 규격이 같으면 규격칸을 비운다
        h+='<tr><td><b>%s</b></td><td>%s</td><td style="text-align:center">%s</td></tr>'%(m,sp,pr)
    return h+'</tbody></table></div>'

def feat(items):
    return '<ul class="pkg-feat">'+''.join('<li>%s</li>'%i for i in items)+'</ul>'

def body(cfg):
    s  = '<section class="pkg"><div class="wrap">\n<a class="ds-back" href="/brands/gaossunion/">← 가오스유니온 전기화학 전체</a>\n'
    s += '<h2 class="pkg-h">특징</h2>' + feat(cfg['feat'])
    s += '<h2 class="pkg-h">사양</h2>' + spec_tbl(cfg['spec'])
    if cfg.get('price'):
        s += '<h2 class="pkg-h">모델 · 규격 · 정가 (%d종)</h2>'%len(cfg['price']) + price_tbl(cfg['price'])
    if cfg.get('note'):
        s += '<p class="pkg-note" style="margin-top:16px">%s</p>' % cfg['note']
    if cfg.get('warn'):
        s += '<p class="pkg-note" style="background:#FDF6E9;border:1px solid #F3E0BC;border-radius:10px;padding:12px 14px;color:#3a3330">%s</p>'%cfg['warn']
    if cfg.get('cross'):
        s += '<p class="pkg-note" style="margin-top:14px">%s</p>'%cfg['cross']
    s += '<p style="margin-top:16px"><button type="button" class="qbtn" data-quote="%s">견적문의</button></p>\n</div></section>\n'%esc(cfg['quote'])
    return s

def faq_block(title, items):
    s='<section class="faq-sec"><div class="wrap"><h2 class="faq-h">%s</h2>'%title
    for q,a in items:
        s+='<div class="faq-item"><p class="faq-q">%s</p><p class="faq-a">%s</p></div>'%(q,a)
    return s+'</div>'

def ld(cfg, slug, faq):
    prices=[p for _,_,p in (cfg.get('price') or []) if p]
    prod={"@context":"https://schema.org","@type":"Product",
      "name":cfg['ldname'],
      "brand":{"@type":"Brand","name":"Gaoss Union","alternateName":"가오스유니온"},
      "category":"전기화학 · "+cfg['cat'],
      "url":"https://rndsetup.com/brands/gaossunion/%s/"%slug,
      "description":cfg['desc']}
    if cfg.get('imgs'):
        prod["image"]="https://rndsetup.com/img/gaossunion/%s"%cfg['imgs'][0]
    if cfg.get('models'): prod["model"]=cfg['models']
    if prices:
        prod["offers"]={"@type":"AggregateOffer","priceCurrency":"KRW",
          "lowPrice":min(prices),"highPrice":max(prices),
          "offerCount":len(cfg['price']),"availability":"https://schema.org/InStock",
          "seller":{"@id":"https://rndsetup.com/#org"}}
    fq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":re.sub('<[^>]+>','',q),
         "acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for q,a in faq]}
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"브랜드","item":"https://rndsetup.com/brands/"},
        {"@type":"ListItem","position":2,"name":"가오스유니온","item":"https://rndsetup.com/brands/gaossunion/"},
        {"@type":"ListItem","position":3,"name":cfg['h1'],"item":"https://rndsetup.com/brands/gaossunion/%s/"%slug}]}
    j=lambda d: '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>\n'
    return j(prod)+j(fq)+j(bc)

# ---------- 페이지 조립 ----------
def build(cfg):
    slug=cfg['slug']
    s=TPL
    if not cfg.get('imgs'): cfg['imgs']=autoimgs(slug)
    s=s.replace('{{HERO}}', hero(slug, cfg['h1'], cfg['imgs']))
    mj=json.dumps([{'m':m,'s':sp,'p':pr} for m,sp,pr in (cfg.get('price') or [])],ensure_ascii=False)
    if not (cfg.get('price') or []):
        mj=json.dumps([{'m':m,'s':'','p':0} for m in (cfg.get('models') or ['기본'])],ensure_ascii=False)
    mj=mj.replace("'",'&#39;')
    s=s.replace('{{HEAD}}', head(cfg['h1'], cfg['sub'], cfg['answer'], cfg['summary'], cfg['quote']))
    s=s.replace('{{BUY}}',  buybox(cfg['h1'], mj))
    s=s.replace('{{BODY}}', body(cfg))
    s=s.replace('{{FAQ}}',  faq_block(cfg['h1']+' FAQ', cfg['faq']))
    s=s.replace('{{LD}}',   ld(cfg, slug, cfg['faq']))
    # 헤드 메타
    s=re.sub(r'<title>[^<]*</title>', '<title>%s</title>'%esc(cfg['title']), s, count=1)
    s=re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['desc'])+m.group(2), s)
    s=re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['h1']+' — 가오스유니온 정품')+m.group(2), s)
    s=re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['desc'])+m.group(2), s)
    s=re.sub(r'(<link rel="canonical" href="https://rndsetup\.com/brands/gaossunion/)[a-z0-9-]+(/")',
             lambda m:m.group(1)+slug+m.group(2), s)
    s=re.sub(r'(<meta property="og:url" content="https://rndsetup\.com/brands/gaossunion/)[a-z0-9-]+(/")',
             lambda m:m.group(1)+slug+m.group(2), s)
    s=s.replace('{{CRUMB}}', cfg['h1'])
    # 아직 만들지 않은 슬러그로 가는 링크는 자동 해제 (죽은 내부 링크 0 규칙)
    have={d for d in os.listdir(OUT) if os.path.isdir(os.path.join(OUT,d))} | {slug}
    def _unlink(m):
        return m.group(0) if m.group(1) in have else m.group(2)
    s=re.sub(r'<a href="/brands/gaossunion/([a-z0-9-]+)/">([^<]*)</a>', _unlink, s)
    assert '{{' not in s, '치환 안 된 자리표시자'
    assert s.count('</html>')==1
    d=os.path.join(OUT,slug); os.makedirs(d,exist_ok=True)
    io.open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(s)
    return len(s), len([p for _,_,p in (cfg.get('price') or []) if p])
