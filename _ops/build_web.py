# -*- coding: utf-8 -*-
"""gaossunion.com 기준 제품 페이지 생성기.
   웹 = 제품 정체·사양 / SQL = 가격.  한 제품 = 한 페이지."""
import io, os, re, json, html
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import shipping as _ship   # 브랜드별 배송비 SSOT — overseas-pricing §3.5

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL  = io.open(os.path.join(ROOT,'_ops','tpl','product.html'), encoding='utf-8').read()
OUT  = os.path.join(ROOT,'brands','gaossunion')

# ══ 브랜드 정의 — cfg에 brand='hefei' 를 주면 그 브랜드로 찍는다 ══
BRANDS = {
 'gaossunion': dict(slug='gaossunion', ko='가오스유니온', en='Gaoss Union',
                    hub='가오스유니온 전기화학 전체', imgdir='gaossunion',
                    kw=['가오스유니온','전기화학']),
 'hefei':      dict(slug='hefei', ko='허페이 인시츄', en='Hefei In-Situ Technology',
                    hub='허페이 인시츄 전체', imgdir='hefei',
                    kw=['허페이인시츄','인시츄셀']),
 'aida':       dict(slug='aida', ko='아이다', en='TianJin AIDA Science-Technology',
                    hub='아이다 전기화학 전체', imgdir='aida',
                    kw=['아이다','전기화학']),
 'neware':     dict(slug='neware', ko='뉴웨어', en='NEWARE',
                    hub='뉴웨어 배터리 시험장비 전체', imgdir='neware',
                    kw=['뉴웨어','배터리테스터']),
}
_B = BRANDS['gaossunion']          # 현재 빌드 중인 브랜드
def _use(name):
    global _B, OUT
    _B = BRANDS[name]
    OUT = os.path.join(ROOT,'brands',_B['slug'])
    SHIP_SHOWN[0] = _ship.s_in(name)      # None = "주문 시 안내"
    os.makedirs(OUT, exist_ok=True)

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
    """img/<브랜드>/<slug>-N.jpg 를 번호순으로 자동 수집 — cfg에 imgs를 적지 않아도 된다"""
    d=os.path.join(ROOT,'img',_B['imgdir'])
    fs=[f for f in os.listdir(d) if re.match(r'^%s-\d+\.jpg$'%re.escape(slug), f)]
    return sorted(fs, key=lambda f:int(re.search(r'-(\d+)\.jpg$',f).group(1)))

def hero(slug, alt, imgs):
    """imgs: [파일명] — 첫 장이 대표. 비어 있으면 갤러리 자체를 넣지 않는다"""
    if not imgs:
        return ''
    D = _B['imgdir']; BR = _B['ko'] + ' ' + _B['en']
    h = ('<div class="dt-img"><img src="/img/%s/%s" alt="%s 제품 사진 (%s)" '
         'loading="lazy" onerror="this.closest(\'.dt-img\').style.display=\'none\'"></div>\n'
         '<div class="dt-thumbs">' % (D, imgs[0], esc(alt), esc(BR)))
    for n,f in enumerate(imgs,1):
        h += ('<button type="button" data-src="/img/%s/%s" onclick="agSwap(this)">'
              '<img src="/img/%s/%s" alt="%s 제품 사진 %d" loading="lazy" '
              'onerror="this.parentElement.style.display=\'none\'"></button>' % (D,f,D,f,esc(alt),n))
    h += '</div>\n<script>function agSwap(b){var i=b.closest(".dt-col").querySelector(".dt-img img");if(i)i.src=b.dataset.src;}</script>\n'
    return h

def head(h1, sub, answer, summary, quote):
    return ('<h1 class="dt-name">%s <span style="font-size:.5em;color:#9A9A9A">%s</span></h1>\n'
            '<p class="dt-ans">%s</p>\n<p class="dt-sum">%s</p>\n'
            '<button type="button" class="qbtn" data-quote="%s">제품문의</button>\n'
            % (h1, sub, answer, summary, esc(quote)))

# ══ 해외 발주 판매가 산식 (2026-08-29 확정) ══
#   판매가 = (정가 + 배송료) × 관세 × 수수료      ※ 부가세는 계수 1 (VAT 별도 표기 유지)
#   배송료는 주문당 1회 성격이라 수량에 비례시키지 않는다.
#     · 제품가격(1개 표시)  = P × K
#     · 배송 표시           = 브랜드별 해외배송비 (_ops/shipping.py)
#     · 10개 이상은 배송료 문의
K    = 1.45        # 관세·수수료 등 일괄 계수 (2026-08-29 확정) — 부가세는 별도 표기
QTY_ASK = 10       # 이 수량 이상이면 배송료 문의
#   합계(수량 1) = 제품가격 + 배송비

# 표시 배송비는 브랜드마다 다르다. 숫자를 여기에 적지 않는다 — _use() 가 SSOT에서 채운다.
SHIP_SHOWN = [_ship.s_in('gaossunion')]             # None 이면 "주문 시 안내" 

_KOFF = [False]   # True면 cfg['price']가 이미 판매가라 K를 곱하지 않는다

def landed_extra(p):
    """제품가격 1개 (배송 제외) — 1,000원 단위 반올림"""
    if not p: return 0
    k = 1.0 if _KOFF[0] else K
    return int(round(p * k / 1000.0)) * 1000

def landed(p):
    """1개 주문 시 합계 = 제품가격 + 배송비. 두 값을 각각 반올림한 뒤 더해
       화면의 '제품가격 + 배송 = 합계'가 항상 정확히 맞아떨어지게 한다."""
    return landed_extra(p) + (SHIP_SHOWN[0] or 0) if p else 0

PRICE_NOTE = '제품가격 1개 기준입니다. <b>해외배송비는 주문당 1회</b> 별도로 더해지며, <b>VAT는 별도</b>입니다. <b>10개 이상</b>은 따로 안내드립니다.'

def buybox(h1, models_json):
    """3번째 그리드 열 — 제품문의 버튼 오른쪽"""
    return ('<div id="buybox" class="bb dt-buy" data-name="%s" data-models=\'%s\'></div>'
            % (esc(h1), models_json))

def spec_tbl(rows):
    return ('<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>'
            + ''.join('<tr><th>%s</th><td>%s</td></tr>'%r for r in rows)
            + '</tbody></table></div>')

_UNIT = re.compile(r'(mL|\u33c6|L\b|mm|cm|\u03a6|\u03c6|\u03bcL|uL|g\b|kg|\u2103|W\b|inch)')

def split_axis(rows):
    """규격이 '형식 · 수치' 꼴로 일관되면 형식을 별도 열로 뺀다.
    한 페이지에 모델이 여럿일 때 무엇이 다른지 한눈에 보이게 하려는 것이다.
    형식이 없거나 전부 형식이거나 형식이 한 가지뿐이면 쪼개지 않는다(억지 분할 방지)."""
    out = []
    for m, sp, p in rows:
        seg = [x.strip() for x in str(sp).split('\u00b7')]
        i = 0
        while i < len(seg) and not _UNIT.search(seg[i]) and not re.fullmatch(r'[\d.~\s]+', seg[i]):
            i += 1
        if i == 0 or i == len(seg):
            return None
        out.append((' \u00b7 '.join(seg[:i]), ' \u00b7 '.join(seg[i:])))
    return out if len({a for a, _ in out}) >= 2 else None


def price_tbl(rows, headers=('모델','규격','제품가격 1개 (VAT 별도)')):
    """모델별 한 줄 — 모델명·형식·규격·가격을 모두 보여 준다.
    mdl-tbl 클래스는 '모델별 내용이 페이지에 있다'는 표시로, 빌드 린터가 이걸 본다."""
    ax = split_axis(rows) if len(rows) > 2 else None
    if ax:
        headers = (headers[0], '형식', headers[1], headers[2])
    h='<div class="pkg-tblwrap"><table class="pkg-tbl pkg-opt mdl-tbl"><thead><tr>'+''.join('<th>%s</th>'%x for x in headers)+'</tr></thead><tbody>'
    for i,(m,spec,p) in enumerate(rows):
        pr = ('<b>%s원</b>'%format(landed_extra(p),',')) if p else '<b>문의</b>'
        sp = '' if spec==m else spec          # 모델명과 규격이 같으면 규격칸을 비운다
        if ax:
            h+='<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td style="text-align:center">%s</td></tr>'%(m,ax[i][0],ax[i][1],pr)
        else:
            h+='<tr><td><b>%s</b></td><td>%s</td><td style="text-align:center">%s</td></tr>'%(m,sp,pr)
    h+='</tbody></table></div>'
    if any(p for _,_,p in rows):
        h+='<p class="pkg-note">%s</p>'%PRICE_NOTE
    return h

def feat(items):
    return '<ul class="pkg-feat">'+''.join('<li>%s</li>'%i for i in items)+'</ul>'

def body(cfg):
    s  = '<section class="pkg"><div class="wrap">\n<a class="ds-back" href="/brands/%s/">← %s</a>\n'%(_B['slug'],_B['hub'])
    s += '<h2 class="pkg-h">특징</h2>' + feat(cfg['feat'])
    s += '<h2 class="pkg-h">사양</h2>' + spec_tbl(cfg['spec'])
    s += cfg.get('spec_extra','')          # 모델별 사양표 등 — 사양 요약표 바로 뒤
    if cfg.get('price'):
        s += '<h2 class="pkg-h">모델 · 규격 · 정가 (%d종)</h2>'%len(cfg['price']) + price_tbl(cfg['price'])
    if cfg.get('note'):
        s += '<p class="pkg-note" style="margin-top:16px">%s</p>' % cfg['note']
    if cfg.get('warn'):
        s += '<p class="pkg-note" style="background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:10px;padding:12px 14px;color:#3a3330">%s</p>'%cfg['warn']
    if cfg.get('extra'):
        s += cfg['extra']
    if cfg.get('cross'):
        s += '<p class="pkg-note" style="margin-top:14px">%s</p>'%cfg['cross']
    s += '<p style="margin-top:16px"><button type="button" class="qbtn" data-quote="%s">견적문의</button></p>\n</div></section>\n'%esc(cfg['quote'])
    return s

def fq3(items):
    """FAQ 항목 정규화 — (질문,답) 또는 (카테고리칩,질문,답) 둘 다 허용."""
    return [(i[0],i[1],i[2]) if len(i)==3 else ('',i[0],i[1]) for i in items]

def faq_block(title, items):
    s='<section class="faq-sec"><div class="wrap"><h2 class="faq-h">%s</h2>'%title
    for tag,q,a in fq3(items):
        chip='<span class="faq-tag">%s</span>'%tag if tag else ''
        s+='<div class="faq-item"><p class="faq-q">%s%s</p><p class="faq-a">%s</p></div>'%(chip,q,a)
    return s+'</div>'

def ld(cfg, slug, faq):
    prices=[landed_extra(p) for _,_,p in (cfg.get('price') or []) if p]   # LD 가격 = 제품가격(배송 별도)
    prod={"@context":"https://schema.org","@type":"Product",
      "name":cfg['ldname'],
      "brand":{"@type":"Brand","name":_B['en'],"alternateName":_B['ko']},
      "category":"전기화학 · "+cfg['cat'],
      "url":"https://rndsetup.com/brands/%s/%s/"%(_B['slug'],slug),
      "description":cfg['desc']}
    if cfg.get('imgs'):
        prod["image"]="https://rndsetup.com/img/%s/%s"%(_B['imgdir'],cfg['imgs'][0])
    if cfg.get('models'): prod["model"]=cfg['models']
    if len(prices)==1 and len(cfg.get('price') or [])==1:
        prod["offers"]={"@type":"Offer","priceCurrency":"KRW","price":prices[0],
          "availability":"https://schema.org/InStock","seller":{"@id":"https://rndsetup.com/#org"}}
    elif prices:
        prod["offers"]={"@type":"AggregateOffer","priceCurrency":"KRW",
          "lowPrice":min(prices),"highPrice":max(prices),
          "offerCount":len(cfg['price']),"availability":"https://schema.org/InStock",
          "seller":{"@id":"https://rndsetup.com/#org"}}
    fq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":re.sub('<[^>]+>','',q),
         "acceptedAnswer":{"@type":"Answer","text":re.sub('<[^>]+>','',a)}} for _t,q,a in fq3(faq)]}
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"브랜드","item":"https://rndsetup.com/brands/"},
        {"@type":"ListItem","position":2,"name":_B['ko'],"item":"https://rndsetup.com/brands/%s/"%_B['slug']},
        {"@type":"ListItem","position":3,"name":cfg['h1'],"item":"https://rndsetup.com/brands/%s/%s/"%(_B['slug'],slug)}]}
    j=lambda d: '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>\n'
    return j(prod)+j(fq)+j(bc)

# ---------- 페이지 조립 ----------
def build(cfg):
    _use(cfg.get('brand','gaossunion'))
    _KOFF[0]=bool(cfg.get('landed'))
    slug=cfg['slug']
    s=TPL
    if not cfg.get('imgs'): cfg['imgs']=autoimgs(slug)
    s=s.replace('{{HERO}}', hero(slug, cfg['h1'], cfg['imgs']))
    mj=json.dumps([{'m':m,'s':sp,'p':landed(pr),'x':landed_extra(pr)} for m,sp,pr in (cfg.get('price') or [])],ensure_ascii=False)
    if not (cfg.get('price') or []):
        mj=json.dumps([{'m':m,'s':'','p':0,'x':0} for m in (cfg.get('models') or ['기본'])],ensure_ascii=False)
    mj=mj.replace("'",'&#39;')
    s=s.replace('{{HEAD}}', head(cfg['h1'], cfg['sub'], cfg['answer'], cfg['summary'], cfg['quote']))
    s=s.replace('{{BUY}}',  buybox(cfg['h1'], mj))
    s=s.replace('{{BODY}}', body(cfg))
    s=s.replace('{{FAQ}}',  faq_block(cfg['h1']+' FAQ', cfg['faq']))
    s=s.replace('{{LD}}',   ld(cfg, slug, cfg['faq']))
    # 헤드 메타
    s=re.sub(r'<title>[^<]*</title>', '<title>%s</title>'%esc(cfg['title']), s, count=1)
    s=re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['desc'])+m.group(2), s)
    s=re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['h1']+' — '+_B['ko']+' 정품')+m.group(2), s)
    s=re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m:m.group(1)+esc(cfg['desc'])+m.group(2), s)
    s=re.sub(r'(<link rel="canonical" href="https://rndsetup\.com/brands/)[a-z0-9-]+/[a-z0-9-]+(/")',
             lambda m:m.group(1)+_B['slug']+'/'+slug+m.group(2), s)
    s=re.sub(r'(<meta property="og:url" content="https://rndsetup\.com/brands/)[a-z0-9-]+/[a-z0-9-]+(/")',
             lambda m:m.group(1)+_B['slug']+'/'+slug+m.group(2), s)
    s=s.replace('<a href="/brands/gaossunion/">가오스유니온</a>',
                '<a href="/brands/%s/">%s</a>'%(_B['slug'],_B['ko']))
    # 브랜드 표기·해시태그·트위터 카드
    s=s.replace('<div class="dt-brand">가오스유니온 · Gaoss Union</div>',
                '<div class="dt-brand">%s · %s</div>'%(esc(_B['ko']),esc(_B['en'])))
    s=re.sub(r'<div class="dt-kw">.*?</div>',
             '<div class="dt-kw">%s<a href="/product/">#실험장비카탈로그</a></div>'
             % ''.join('<a href="/brands/%s/">#%s</a>'%(_B['slug'],esc(k)) for k in _B['kw']),
             s, count=1, flags=re.S)
    s=re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
             lambda m:m.group(1)+esc(cfg['h1']+' — '+_B['ko'])+m.group(2), s)
    s=re.sub(r'(<meta name="twitter:description" content=")[^"]*(")',
             lambda m:m.group(1)+esc(cfg['desc'])+m.group(2), s)
    _og=('https://rndsetup.com/img/%s/%s'%(_B['imgdir'],cfg['imgs'][0])) if cfg.get('imgs') else ''
    if _og:
        s=re.sub(r'((?:og:image|twitter:image)" content=")[^"]*(")', lambda m:m.group(1)+_og+m.group(2), s)
    s=s.replace('{{CRUMB}}', cfg['h1'])
    # 아직 만들지 않은 슬러그로 가는 링크는 자동 해제 (죽은 내부 링크 0 규칙)
    have={d for d in os.listdir(OUT) if os.path.isdir(os.path.join(OUT,d))} | {slug}
    def _unlink(m):
        return m.group(0) if m.group(1) in have else m.group(2)
    s=re.sub(r'<a href="/brands/'+_B['slug']+r'/([a-z0-9-]+)/">([^<]*)</a>', _unlink, s)
    assert '{{' not in s, '치환 안 된 자리표시자'
    assert s.count('</html>')==1
    d=os.path.join(OUT,slug); os.makedirs(d,exist_ok=True)
    io.open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(s)
    return len(s), len([p for _,_,p in (cfg.get('price') or []) if p])
