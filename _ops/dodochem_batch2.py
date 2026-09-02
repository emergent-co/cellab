# DodoChem 전체 등록: 단독 상세 +50종, 계열 통합 15페이지, 전 품목 SQL
# 가격 = CNY × 210 × 1.45, 1,000원 반올림 · 5만 미만 SKU는 SQL 제외·표에는 '소액(문의)'
import os, re, json, collections

FX, K = 210, 1.45
def won(c): return int(round(c * FX * K / 1000.0)) * 1000

data = json.load(open('/tmp/dodo/all.json', encoding='utf-8'))
prices = json.load(open('/tmp/dodo/prices.json', encoding='utf-8'))
pmap = collections.defaultdict(list)
for pid, val, pname, price in prices: pmap[pid].append((pname, val, float(price)))
top50 = set(json.load(open('/tmp/dodo/top50_ids.json')))
DONE13 = {'LS-009','LS-002','LB-002','LB-008','NC-004','NP-005','NE-000027','NE-000014','NE-000063','NE-000061','NE-000675','NE-000608','NE-000183'}
DONE_SLUG = {'LS-009':'ls-009-lithium-sulfur-electrolyte','LS-002':'ls-002-lithium-sulfur-electrolyte','LB-002':'lb-002-lithium-ion-electrolyte','LB-008':'lb-008-lithium-ion-electrolyte','NC-004':'nc-004-naclo4-electrolyte','NP-005':'np-005-napf6-electrolyte','NE-000027':'lifsi-battery-grade','NE-000014':'litfsi-battery-grade','NE-000063':'dme-anhydrous-solvent','NE-000061':'dmc-anhydrous-solvent','NE-000675':'whatman-gfd-125mm','NE-000608':'ceramic-disc-18mm','NE-000183':'pvdf-hsv900-binder'}

KO = {'리튬황':'리튬황 전해액','리튬2차':'리튬이온 전해액','리튬1차':'리튬 1차 전해액','리튬공기':'리튬-공기 전해액',
 'NaClO4':'나트륨이온 전해액(NaClO4)','NaPF6':'나트륨이온 전해액(NaPF6)','NaCF3SO3':'나트륨이온 전해액(NaCF3SO3)',
 'KPF6':'칼륨이온 전해액','Mg':'마그네슘이온 전해액','Al':'알루미늄이온 전해액','Zn':'아연이온 전해액','Ca':'칼슘이온 전해액',
 '슈퍼커패시터':'슈퍼커패시터 전해액','혼합용매':'혼합 용매','커스텀':'커스텀 전해액',
 '용질염':'전해질 염','고순도용매':'고순도 용매','첨가제':'전해액 첨가제','기타':'기타',
 '전지케이스':'코인셀 케이스','케이스304':'SUS304 코인셀 케이스','케이스316':'SUS316 코인셀 케이스',
 '분리막':'분리막','Whatman':'Whatman 유리섬유 분리막','Celgard':'Celgard 분리막','재단분리막':'재단 분리막 원판',
 '셀룰로오스막':'셀룰로오스 분리막','세라믹막':'세라믹 분리막','아라미드막':'아라미드 분리막',
 '바인더':'바인더','음극재':'음극재','음극편':'음극 극판','양극재':'양극재','양극편':'양극 극판',
 '도전재':'도전재','집전체':'집전체','고체전해질':'고체전해질','건전지':'드라이 셀'}

def parse(r):
    """제품 표시명·설명 자동화"""
    cat, pid, name, code, brief, cas, unit = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
    sub = cat.split('|')[1]
    m = re.search(r'配方[：:]\s*(.+?)(?:$|\s*$)', brief)
    formula = m.group(1).strip() if m else ''
    ab = re.search(r'简称[：:]\s*([A-Za-z0-9\-]+)', brief)
    abbr = ab.group(1) if ab else ''
    wm = re.search(r'(Whatman\s*[A-Z/]+\s*[0-9\-]+[a-z]*mm?)', name, re.I)
    if formula:
        disp = f"{KO.get(sub, sub)} {code}"; desc = formula
    elif abbr:
        disp = f"{abbr} ({KO.get(sub, sub)})"; desc = (f"CAS {cas}" if cas else brief[:60])
    elif wm:
        disp = f"유리섬유 분리막 {wm.group(1)}"; desc = 'Whatman 유리섬유 여과지'
    else:
        disp = f"{KO.get(sub, sub)} {code}"; desc = re.sub(r'\s+', ' ', brief)[:70]
    return disp, desc, formula or desc

def visible(pid):
    return [(v, c, won(c)) for _, v, c in sorted(pmap.get(pid, []), key=lambda x: x[2]) if won(c) >= 50000]

STYLE = '<link rel="stylesheet" href="/assets/detail.css">'
def esc(s): return s.replace("'", '').replace('"', '')

sql_rows, hub_cards = [], []
made_pages = 0

# ── A. 단독 상세 50종 ──
GROUP_USE = {'리튬황':'리튬-황(Li-S) 전지 · Li–Li 대칭 셀','리튬2차':'리튬이온 2차전지','리튬1차':'리튬 1차전지','리튬공기':'리튬-공기 전지',
 'NaClO4':'나트륨이온 전지','NaPF6':'나트륨이온 전지','NaCF3SO3':'나트륨이온 전지','KPF6':'칼륨이온 전지','Mg':'마그네슘 전지','Al':'알루미늄 전지','Zn':'아연 전지','Ca':'칼슘 전지','슈퍼커패시터':'슈퍼커패시터','혼합용매':'전해액 조액용 혼합 용매','커스텀':'커스텀 배합 전해액',
 '용질염':'전해액 조액용 용질 염','고순도용매':'전해액 조액용 고순도 용매','첨가제':'전해액 첨가제',
 '전지케이스':'코인셀 조립','케이스304':'코인셀 조립(SUS304)','케이스316':'코인셀 조립(SUS316)','Whatman':'코인셀·가시화 셀 분리막(재단용)','Celgard':'코인셀 분리막','재단분리막':'코인셀 조립','분리막':'전지 분리막','바인더':'전극 슬러리 바인더','도전재':'전극 도전재','집전체':'전극 집전체','음극재':'음극 소재','양극재':'양극 소재','고체전해질':'전고체 전지'}

std_products = []  # (r, slug, disp)
for r in data:
    if r[1] not in top50: continue
    sub = r[0].split('|')[1]
    disp, desc, formula = parse(r)
    slug = 'p-' + r[3].lower()
    std_products.append((r, slug, disp, desc, formula, sub))

for r, slug, disp, desc, formula, sub in std_products:
    code = r[3]; unit = r[6] or 'g'
    vis = visible(r[1]); assert vis, code
    low = vis[0][2]; use = GROUP_USE.get(sub, '배터리 실험')
    img = f'/img/dodochem/{code.lower()}-1.jpg'
    kname = f'DodoChem {disp}'
    typ = 'elec' if formula and '전해액' in KO.get(sub, '') else 'mat'
    tbl = '\n'.join(f'<tr><td><b>{code}</b> · {v} {unit}</td><td>{desc}</td><td style="text-align:center"><b>{w:,}원</b></td></tr>' for v, c, w in vis)
    faq = '''<div class="faq-item"><p class="faq-q"><span class="faq-tag">가격</span>표기 가격 기준이 어떻게 되나요?</p><p class="faq-a">표기 가격은 소비자가이며 부가세 별도입니다. 해외배송비 100,000원(주문당 1회)이 별도이고, 해외 직수입 품목으로 상시 할인 대상이 아닙니다.</p></div>
<div class="faq-item"><p class="faq-q"><span class="faq-tag">커스텀</span>규격·배합 커스텀이 되나요?</p><p class="faq-a">네. 원하는 조건(배합식·규격·수량)을 견적 문의에 적어 주시면 맞춰 안내합니다.</p></div>'''
    page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{kname} | 실험셋업연구소</title>
<meta name="description" content="{kname} — {desc}. {use}. 소비자가 {low:,}원~, 해외배송비 100,000원(주문당 1회) 별도.">
<link rel="canonical" href="https://rndsetup.com/brands/dodochem/{slug}/">
<meta property="og:type" content="product"><meta property="og:title" content="{kname}"><meta property="og:description" content="{desc} — {use}."><meta property="og:url" content="https://rndsetup.com/brands/dodochem/{slug}/"><meta property="og:image" content="https://rndsetup.com{img}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Product","name":"{kname}","sku":"{code}","brand":{{"@type":"Brand","name":"DodoChem"}},"image":"https://rndsetup.com{img}","description":"{desc} — {use}.","offers":{{"@type":"AggregateOffer","priceCurrency":"KRW","lowPrice":{vis[0][2]},"highPrice":{vis[-1][2]},"offerCount":{len(vis)},"availability":"https://schema.org/InStock","seller":{{"@type":"Organization","name":"실험셋업연구소"}}}}}}
</script>
<link rel="stylesheet" href="/assets/site.css">
{STYLE}
</head>
<body>
<div id="pumplab-header"></div>

<main class="wrap" style="max-width:832px;margin:0 auto;padding:26px 18px 60px">
<nav style="font-size:12.5px;color:#8a8f98;margin-bottom:10px"><a href="/" style="color:inherit">홈</a> › <a href="/product/" style="color:inherit">제품</a> › 배터리 재료 · {KO.get(sub, sub)}</nav>
<h1 style="font-family:var(--serif);font-size:clamp(21px,4vw,27px);color:#2A2570;margin:0 0 2px">{kname}</h1>
<div style="font-size:13px;color:#8a8f98;margin-bottom:14px">DodoChem {code}</div>

<figure style="margin:0 0 14px"><img src="{img}" alt="{kname} 제품 사진" style="display:block;width:100%;max-width:360px;margin:0 auto;border:1px solid #D8E4F2;border-radius:12px;background:#fff"></figure>

<p class="dt-sum"><b>{desc}</b> — {use}. 규격 <b>{vis[0][1]}{unit} ~ {vis[-1][1]}{unit}</b>, 소비자가 <b>{low:,}원~</b>.</p>

<h2 class="pkg-h">규격 · 소비자가</h2>
<div class="pkg-tblwrap"><table class="pkg-tbl"><thead><tr><th>규격</th><th>{'배합' if typ == 'elec' else '설명'}</th><th style="text-align:center">소비자가</th></tr></thead><tbody>
{tbl}
</tbody></table></div>
<p class="pkg-note" style="margin-top:14px">표기 가격은 소비자가(부가세 별도)이며 <b>해외배송비 100,000원(주문당 1회) 별도</b>입니다. 해외 직수입 품목으로 상시 할인 대상이 아닙니다.{' 30만원 미만 소액 품목은 다른 품목과 합산 주문을 권장합니다.' if low < 300000 else ''}</p>
<p style="margin-top:14px"><button type="button" class="qbtn" data-quote="{esc(kname)} (규격·수량 문의)">견적문의</button></p>

<h2 class="pkg-h" style="margin-top:26px">자주 묻는 질문</h2>
{faq}
</main>

<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''
    d = f'brands/dodochem/{slug}'
    os.makedirs(d, exist_ok=True)
    fo = open(d + '/index.html', 'w', encoding='utf-8'); fo.write(page); fo.flush(); os.fsync(fo.fileno()); fo.close()
    made_pages += 1
    txt = esc(f"{kname} {code} {desc} {use} {KO.get(sub, sub)} dodochem 배터리 재료").lower()
    hub_cards.append(f'''<article class="dscard" data-cat="material" data-text="{txt}">
  <div class="dscard-im"><img src="{img}" alt="{esc(kname)}" loading="lazy" width="760" height="760"><div class="dscard-bdg"><span class="b y">{KO.get(sub, sub)}</span></div></div>
  <div class="dscard-bd">
    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/dodochem/{slug}/">{esc(disp)}</a></h3>
    <div class="dscard-nm">{code} · {vis[0][1]}{unit}~{vis[-1][1]}{unit}</div>
    <p class="dscard-d">{esc(desc)} — {use}.</p>
    <p class="dscard-p">{len(vis)}규격 · {low:,}원부터</p>
  </div>
</article>''')

# ── B. 계열 통합 15페이지 ──
GROUPS = [
 ('series-lithium-sulfur','리튬황 전해액','Lithium-Sulfur Electrolytes',['전해액|리튬황'],'리튬-황 전지용 표준·커스텀 전해액입니다. LiTFSI/LiFSI 염과 DME:DOL 계 용매, LiNO3·폴리설파이드 첨가 배합까지 코드로 선택합니다.'),
 ('series-lithium-ion','리튬이온 전해액','Lithium-ion Electrolytes',['전해액|리튬2차','전해액|리튬1차','전해액|리튬공기'],'리튬이온 2차·1차·리튬-공기 전지용 전해액입니다. LiPF6 카보네이트계 표준 배합부터 커스텀까지 코드로 선택합니다.'),
 ('series-sodium','나트륨이온 전해액','Sodium-ion Electrolytes',['전해액|NaClO4','전해액|NaPF6','전해액|NaCF3SO3'],'나트륨이온 전지용 NaClO4·NaPF6·NaCF3SO3 전해액입니다.'),
 ('series-other-ion','기타 이온 전해액','K·Mg·Al·Zn·Ca / Supercapacitor Electrolytes',['전해액|KPF6','전해액|Mg','전해액|Al','전해액|Zn','전해액|Ca','전해액|슈퍼커패시터'],'칼륨·마그네슘·알루미늄·아연·칼슘 이온 전지와 슈퍼커패시터용 전해액입니다.'),
 ('series-custom-solvent','커스텀 전해액·혼합 용매','Custom Electrolytes & Solvent Blends',['전해액|커스텀','전해액|혼합용매'],'원하는 배합식 그대로 조액하는 커스텀 전해액과 혼합 용매입니다. 표의 기존 배합 코드로 주문하거나, 새 배합식을 견적으로 요청하세요.'),
 ('series-salts','전해질 염','Electrolyte Salts',['시약|용질염'],'전해액 조액용 배터리 등급 용질 염입니다. LiPF6·LiTFSI·LiFSI·나트륨염 등.'),
 ('series-solvents','고순도 용매','High-purity Solvents',['시약|고순도용매'],'전해액 조액용 무수 고순도 용매입니다. DME·DOL·EC·DMC·EMC 등.'),
 ('series-additives','전해액 첨가제·기타 시약','Electrolyte Additives',['시약|첨가제','시약|기타'],'FEC·VC 등 전해액 첨가제와 기타 시약입니다.'),
 ('series-separators','분리막','Separators',['소재|분리막','소재|Whatman','소재|Celgard','소재|재단분리막','소재|셀룰로오스막','소재|세라믹막','소재|아라미드막'],'Whatman 유리섬유·Celgard·세라믹·셀룰로오스·아라미드 분리막과 재단 원판입니다.'),
 ('series-cases','코인셀 케이스','Coin Cell Cases',['소재|전지케이스','소재|케이스304','소재|케이스316'],'SUS304·SUS316 코인셀 케이스·부속입니다.'),
 ('series-binder-conductive','바인더·도전재','Binders & Conductive Agents',['소재|바인더','소재|도전재'],'PVDF 바인더와 도전재입니다.'),
 ('series-electrode-materials','전극 소재·극판','Electrode Materials & Sheets',['소재|음극재','소재|음극편','소재|양극재','소재|양극편'],'양극·음극 활물질과 코팅 완료 극판입니다.'),
 ('series-current-collectors','집전체','Current Collectors',['소재|집전체'],'알루미늄·구리 집전체입니다.'),
 ('series-solid-electrolyte','고체전해질','Solid Electrolytes',['소재|고체전해질'],'전고체 전지용 고체전해질입니다.'),
 ('series-drycell-etc','드라이 셀·기타 소재','Dry Cells & Others',['소재|건전지','소재|기타'],'드라이 셀과 기타 전지 소재입니다.'),
]
bycat = collections.defaultdict(list)
for r in data: bycat[r[0]].append(r)

std_slug = {r[3]: slug for r, slug, *_ in std_products}
std_slug.update(DONE_SLUG)

for gslug, gname, gen, cats, intro in GROUPS:
    rows_html, n_all, n_priced = [], 0, 0
    items = []
    for c in cats: items += bycat.get(c, [])
    items.sort(key=lambda r: -r[7])
    rep_img = '/img/dodochem/ls-009-1.jpg'
    for r in items:
        n_all += 1
        disp, desc, formula = parse(r)
        vis = visible(r[1])
        code = r[3]
        link = std_slug.get(code)
        namecell = f'<a href="/brands/dodochem/{link}/" style="color:#0F69AF;font-weight:700">{esc(disp)}</a>' if link else esc(disp)
        if vis:
            n_priced += 1
            pr = f'{vis[0][2]:,}원~'
            rng = f'{vis[0][1]}~{vis[-1][1]}{r[6] or ""}'
        else:
            pr = '소액·문의'; rng = ', '.join(v for _, v, _ in sorted(pmap.get(r[1], []), key=lambda x: x[2])[:3]) or '-'
        rows_html.append(f'<tr><td><b>{code}</b></td><td>{namecell}<div style="font-size:12px;color:#7a828c">{esc(desc)[:90]}</div></td><td style="white-space:nowrap">{rng}</td><td style="text-align:right;white-space:nowrap"><b>{pr}</b></td></tr>')
        if link and rep_img == '/img/dodochem/ls-009-1.jpg':
            rep_img = f'/img/dodochem/{code.lower()}-1.jpg' if not code in DONE13 else rep_img
    low_min = min((visible(r[1])[0][2] for r in items if visible(r[1])), default=0)
    page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DodoChem {gname} {n_all}종 — {gen} | 실험셋업연구소</title>
<meta name="description" content="DodoChem {gname} {n_all}종 통합 카탈로그. {intro} 소비자가 기준, 해외배송비 100,000원(주문당 1회) 별도.">
<link rel="canonical" href="https://rndsetup.com/brands/dodochem/{gslug}/">
<meta property="og:type" content="website"><meta property="og:title" content="DodoChem {gname} {n_all}종"><meta property="og:description" content="{intro}"><meta property="og:url" content="https://rndsetup.com/brands/dodochem/{gslug}/">
<link rel="stylesheet" href="/assets/site.css">
{STYLE}
</head>
<body>
<div id="pumplab-header"></div>

<main class="wrap" style="max-width:832px;margin:0 auto;padding:26px 18px 60px">
<nav style="font-size:12.5px;color:#8a8f98;margin-bottom:10px"><a href="/" style="color:inherit">홈</a> › <a href="/product/" style="color:inherit">제품</a> › 배터리 재료 · {gname}</nav>
<h1 style="font-family:var(--serif);font-size:clamp(21px,4vw,27px);color:#2A2570;margin:0 0 2px">DodoChem {gname} <span style="font-size:16px;color:#8a8f98">{n_all}종</span></h1>
<div style="font-size:13px;color:#8a8f98;margin-bottom:14px">{gen}</div>

<p class="dt-sum">{intro} 아래 표에서 코드·배합으로 검색해 견적을 요청하세요.</p>

<p style="margin:14px 0 8px"><input type="search" id="gq" placeholder="코드·배합·키워드 검색 — 예: LiFSI, DME, 2032" style="width:100%;max-width:420px;height:40px;border:1px solid #C9D6E6;border-radius:9px;padding:0 12px;font-size:14px"></p>
<div class="pkg-tblwrap"><table class="pkg-tbl" id="gtbl"><thead><tr><th>코드</th><th>품명 · 배합</th><th>규격</th><th style="text-align:right">소비자가</th></tr></thead><tbody>
{''.join(rows_html)}
</tbody></table></div>
<p class="pkg-note" style="margin-top:14px">표기 가격은 소비자가(부가세 별도) · <b>해외배송비 100,000원(주문당 1회) 별도</b> · 해외 직수입 품목으로 상시 할인 대상이 아닙니다. '소액·문의' 표기 품목과 30만원 미만 품목은 타 품목과 합산 주문을 권장합니다. 표에 없는 배합은 커스텀 조액으로 견적 요청하세요.</p>
<p style="margin-top:14px"><button type="button" class="qbtn" data-quote="DodoChem {gname} (코드·수량 기재)">견적문의</button></p>
</main>

<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
<script>
(function(){{var q=document.getElementById('gq'),rows=Array.prototype.slice.call(document.querySelectorAll('#gtbl tbody tr'));
q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase();rows.forEach(function(tr){{tr.style.display=(!v||tr.textContent.toLowerCase().indexOf(v)>-1)?'':'none';}});}});}})();
</script>
</body>
</html>
'''
    d = f'brands/dodochem/{gslug}'
    os.makedirs(d, exist_ok=True)
    fo = open(d + '/index.html', 'w', encoding='utf-8'); fo.write(page); fo.flush(); os.fsync(fo.fileno()); fo.close()
    made_pages += 1
    txt = esc(f"dodochem {gname} {gen} 배터리 재료 통합 {n_all}종").lower()
    pricecell = f'{low_min:,}원부터' if low_min else '견적 문의'
    hub_cards.append(f'''<article class="dscard" data-cat="material" data-text="{txt}">
  <div class="dscard-im"><img src="{rep_img}" alt="DodoChem {gname}" loading="lazy" width="760" height="760"><div class="dscard-bdg"><span class="b y">계열</span></div></div>
  <div class="dscard-bd">
    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/dodochem/{gslug}/">{gname} 통합 {n_all}종</a></h3>
    <div class="dscard-nm">DodoChem · {n_priced}종 가격 게시</div>
    <p class="dscard-d">{intro[:80]}</p>
    <p class="dscard-p">{n_all}종 · {pricecell}</p>
  </div>
</article>''')

# ── C. SQL: 전 품목 (기존 DodoChem 블록 대체) ──
for r in data:
    vis = visible(r[1])
    if not vis: continue
    sub = r[0].split('|')[1]
    disp, desc, formula = parse(r)
    code = r[3] or r[1]; unit = r[6] or 'g'
    slug = std_slug.get(code)
    url = f'https://rndsetup.com/brands/dodochem/{slug}/' if slug else 'https://rndsetup.com/product/?q=' + code
    sobun = KO.get(sub, sub)
    for v, c, w in vis:
        vv = esc(str(v))[:24]
        sku = 'DD-' + re.sub(r'[^A-Z0-9]', '', code.upper())[:14] + '-' + re.sub(r'[^A-Za-z0-9\.]', '', vv)[:12]
        sql_rows.append(
            "INSERT INTO products (sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v,status) VALUES "
            f"('{sku}',910,'DodoChem','DodoChem','중국','배터리 소재','{esc(sobun)}','{esc(code)}','규격','{vv}{unit}',"
            f"'DodoChem {esc(disp)} {vv}{unit}','1.{esc(desc)[:120]} | 2.규격 {vv}{unit}','','ea',0,{w},"
            f"'','{url}','','','','카탈로그가','CNY {c}','계열','{esc(sobun)}','','','','','판매중');")

p = 'rndsetup_products.sql'
s = open(p, encoding='utf-8').read()
s = re.sub(r"\n-- DodoChem.*$", "", s, flags=re.S)
block = ("\n-- DodoChem 배터리 재료 (전 품목) — 판매가 = CNY 소비자가 x 환율계수 210(=올림10(스팟 204.46 x 1.02), 2026-09-02) x 1.45, 1,000원 반올림"
         "\n-- 해외배송비(고객) 100,000원/주문 별도 · 상시 3% 할인 미적용 · 5만원 미만 SKU 미등록(합산 견적)\n"
         + "\n".join(sql_rows) + "\n")
fo = open(p, 'w', encoding='utf-8'); fo.write(s + block); fo.flush(); os.fsync(fo.fileno()); fo.close()

# ── D. 허브에 카드 추가(기존 13 유지 + 신규 65) ──
p = 'brands/dodochem/index.html'
h = open(p, encoding='utf-8').read()
h = h.replace('</body>', '\n'.join(hub_cards) + '\n</body>')
fo = open(p, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()

# SKU 중복 검사
skus = re.findall(r"'(DD-[^']+)'", "\n".join(sql_rows))
dup = [k for k, n in collections.Counter(skus).items() if n > 1]
print('pages:', made_pages, '| sql rows:', len(sql_rows), '| hub cards +', len(hub_cards), '| sku dup:', len(dup), dup[:5])
