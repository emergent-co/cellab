# DodoChem 1차 일괄 등록 13종 — overseas-pricing 스킬 공식 ①
# 판매가 = CNY 소비자가 × 환율계수 210(=올림10(스팟204.46×1.02)) × 1.45, 1,000원 반올림
# 해외배송비(고객) 100,000원/주문 별도 · 상시 3% 할인 제외 · 5만원 미만 SKU 제외(문의)
import os, re, json

FX = 210; K = 1.45
def won(cny): return int(round(cny * FX * K / 1000.0)) * 1000

sel = {s['code']: s for s in json.load(open('/tmp/dodo/sel.json', encoding='utf-8'))}

# (코드, slug, 한글명, 영문명, 유형, 배합/설명, 규격단위, 사양행 추가, FAQ유형, 소분류)
META = [
 ('LS-009','ls-009-lithium-sulfur-electrolyte','DodoChem 리튬황 전해액 LS-009','Lithium-Sulfur Electrolyte LS-009','elec','1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3','g','리튬-황(Li-S) 전지 · Li–Li 대칭 셀','전해액'),
 ('LS-002','ls-002-lithium-sulfur-electrolyte','DodoChem 리튬황 전해액 LS-002','Lithium-Sulfur Electrolyte LS-002','elec','1M LiTFSI in DME:DOL=1:1 Vol% with 1%LiNO3','g','리튬-황(Li-S) 전지 · Li–Li 대칭 셀','전해액'),
 ('LB-002','lb-002-lithium-ion-electrolyte','DodoChem 리튬이온 전해액 LB-002','Lithium-ion Electrolyte LB-002','elec','1M LiPF6 in DMC:EC:EMC=1:1:1 Vol%','g','리튬이온 2차전지 표준(카보네이트계)','전해액'),
 ('LB-008','lb-008-lithium-ion-electrolyte','DodoChem 리튬이온 전해액 LB-008','Lithium-ion Electrolyte LB-008','elec','1M LiPF6 in DEC:EC=1:1 Vol%','g','리튬이온 2차전지(카보네이트계)','전해액'),
 ('NC-004','nc-004-naclo4-electrolyte','DodoChem 나트륨이온 전해액 NC-004','NaClO4 Electrolyte NC-004','elec','1M NaClO4 in EC:PC=1:1 Vol% with 5%FEC','g','나트륨이온 전지 · FEC 5% 첨가','전해액'),
 ('NP-005','np-005-napf6-electrolyte','DodoChem 나트륨이온 전해액 NP-005','NaPF6 Electrolyte NP-005','elec','1M NaPF6 in DIGLYME=100 Vol%','g','나트륨이온 전지(에테르계)','전해액'),
 ('NE-000027','lifsi-battery-grade','DodoChem LiFSI 전해질 염 (배터리 등급)','LiFSI — Lithium bis(fluorosulfonyl)imide','salt','리튬 비스(플루오로설포닐)이미드 · 화학식 F2NO4S2·Li · CAS 171611-11-3','g','전해액 용질 염 — 고농도·에테르계 전해액 조액','용질 염'),
 ('NE-000014','litfsi-battery-grade','DodoChem LiTFSI 전해질 염 (배터리 등급)','LiTFSI — Lithium bis(trifluoromethanesulfonyl)imide','salt','리튬 비스(트리플루오로메탄설포닐)이미드 · 화학식 C2F6LiNO4S2 · CAS 90076-65-6','g','전해액 용질 염 — Li-S·에테르계 전해액 조액','용질 염'),
 ('NE-000063','dme-anhydrous-solvent','DodoChem DME 고순도 용매','DME — 1,2-Dimethoxyethane (anhydrous)','salt','에틸렌글리콜 디메틸에테르 · 화학식 C4H10O2 · CAS 110-71-4','g','에테르계 전해액 용매(DOL과 병용)','고순도 용매'),
 ('NE-000061','dmc-anhydrous-solvent','DodoChem DMC 고순도 용매','DMC — Dimethyl carbonate (anhydrous)','salt','탄산 디메틸 · 화학식 C3H6O3 · CAS 616-38-6','g','카보네이트계 전해액 용매','고순도 용매'),
 ('NE-000675','whatman-gfd-125mm','DodoChem Whatman GF/D 유리섬유 분리막 125mm','Whatman GF/D Glass Fiber Separator 1823-125mm','sep','Whatman GF/D 1823-125 · 유리섬유 여과지 원단','장','코인셀·가시화 셀 분리막(재단용)','분리막'),
 ('NE-000608','ceramic-disc-18mm','DodoChem 단면 세라믹 분리막 원형 18mm','Ceramic-coated Separator Disc Φ18 mm (16+2+2)','sep','단면 세라믹 코팅(16+2+2 µm) · Φ18 mm 재단 원판','장','코인셀(CR2032 등) 조립용','분리막'),
 ('NE-000183','pvdf-hsv900-binder','DodoChem PVDF 바인더 HSV900','PVDF Binder HSV900 (Arkema)','mat','폴리불화비닐리덴(PVDF) · Arkema HSV900 · 전극 슬러리 바인더','g','양극 슬러리 바인더(NMP 용해)','바인더'),
]

STYLE = '<link rel="stylesheet" href="/assets/detail.css">'

FAQS = {
 'elec': [('배합','다른 배합도 주문할 수 있나요?','네. 염 농도·용매비·첨가제를 바꾼 커스텀 배합이 가능합니다. 원하는 배합식을 견적 문의에 그대로 적어 주세요.'),
          ('취급','보관은 어떻게 하나요?','수분에 민감하므로 아르곤 글러브박스에서 개봉·취급하시길 권장합니다. 밀봉 알루미늄 병으로 배송됩니다.')],
 'salt': [('등급','배터리 실험에 바로 쓸 수 있는 등급인가요?','네. 전해액 조액용 배터리 등급이며 수분 관리 포장으로 배송됩니다. 개봉·계량은 글러브박스에서 하시길 권장합니다.'),
          ('조액','전해액 조액도 대신 해주나요?','네. 원하는 배합식을 주시면 조액 완제품(커스텀 전해액)으로도 공급합니다. 견적 문의에 배합식을 적어 주세요.')],
 'sep':  [('규격','다른 지름으로 재단해 주나요?','네. 재단 지름(Φ16/18/19 mm 등)·수량을 견적 문의에 적어 주시면 맞춰 드립니다.'),
          ('보관','보관 시 주의사항이 있나요?','건조한 곳에 보관하고, 조립 전 이물·습기를 피해 주세요.')],
 'mat':  [('용해','어떤 용매에 녹여 쓰나요?','일반적으로 NMP에 용해해 전극 슬러리 바인더로 사용합니다. 배합 관련 문의는 견적 문의로 남겨 주세요.'),
          ('보관','보관은 어떻게 하나요?','밀봉 상태로 건조한 곳에 보관하세요.')],
}
PRICE_FAQ = ('가격','표기 가격 기준이 어떻게 되나요?','표기 가격은 소비자가이며 부가세 별도입니다. 해외배송비 100,000원(주문당 1회)이 별도이고, 해외 직수입 품목으로 상시 할인 대상이 아닙니다.')

def spec_rows(m, s):
    t = m[4]
    rows = [('배합' if t == 'elec' else '명칭·규격', f'<b>{m[5]}</b>'),
            ('용도', m[7]),
            ('규격', ' / '.join(f'{v}{m[6]}' for _, v, _ in s['skus'])),
            ('보관·취급', 'Ar 글러브박스 취급 권장 · 수분 민감' if t in ('elec', 'salt') else '건조 보관'),
            ('브랜드', 'DodoChem · 원산지 중국')]
    return '\n'.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in rows)

sql_rows, hub_cards, pages = [], [], 0
lows = {}
for m in META:
    code, slug, kname, ename, typ, desc, u, use, sobun = m
    s = sel[code]
    skus = [(v, c, won(c)) for _, v, c in s['skus']]
    vis = [x for x in skus if x[2] >= 50000]
    drop = [x for x in skus if x[2] < 50000]
    assert vis, code
    lows[code] = vis[0][2]
    imgslug = {'LS-009':'ls-009','LS-002':'ls-002','LB-002':'lb-002','LB-008':'lb-008','NC-004':'nc-004','NP-005':'np-005','NE-000027':'lifsi','NE-000014':'litfsi','NE-000063':'dme','NE-000061':'dmc','NE-000675':'whatman-gfd','NE-000608':'ceramic-disc-18','NE-000183':'pvdf-hsv900'}[code]
    img = f'/img/dodochem/{imgslug}-1.jpg'
    # SQL
    for v, c, w in vis:
        vv = v.replace("'", '')
        sql_rows.append(
            "INSERT INTO products (sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v,status) VALUES "
            f"('DD-{code.replace('NE-','NE').replace('-','')}-{vv}',910,'DodoChem','DodoChem','중국','배터리 소재','{sobun}','{code}','규격','{vv}{u}',"
            f"'{kname} {vv}{u}','1.{desc.split('·')[0].strip()} | 2.용도 {use} | 3.규격 {vv}{u}','','ea',0,{w},"
            f"'https://rndsetup.com{img}','https://rndsetup.com/brands/dodochem/{slug}/',"
            f"'','','','카탈로그가','CNY {c}','계열','{sobun}','','','','','판매중');")
    tbl = '\n'.join(f'<tr><td><b>{code}</b> · {v} {u}</td><td>{desc if typ=="elec" else use}</td><td style="text-align:center"><b>{w:,}원</b></td></tr>' for v, c, w in vis)
    dropnote = (f' {len(drop)}개 소액 규격({", ".join(v+u for v,_,_ in drop)})은 단품 판매가 어려워 본체·타 품목과 합산 견적으로 안내합니다.' if drop else '')
    smallnote = ' 30만원 미만 소액 품목은 다른 품목과 합산 주문을 권장합니다.' if lows[code] < 300000 else ''
    faqs = FAQS[typ] + [PRICE_FAQ]
    faq_html = '\n'.join(f'<div class="faq-item"><p class="faq-q"><span class="faq-tag">{t}</span>{q}</p><p class="faq-a">{a}</p></div>' for t, q, a in faqs)
    papers = ''
    if code == 'LS-009':
        old = open(f'brands/dodochem/ls-009-lithium-sulfur-electrolyte/index.html', encoding='utf-8').read()
        mm = re.search(r'<h2 class="pkg-h" style="margin-top:26px">이 배합을 쓴 대표 논문</h2>.*?</p>\n', old, re.S)
        papers = mm.group(0) if mm else ''
    page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{kname} — {ename} | 실험셋업연구소</title>
<meta name="description" content="{kname} — {desc}. {use}. 규격 {' / '.join(v+u for v,_,_ in vis)}, 소비자가 {lows[code]:,}원~, 해외배송비 100,000원(주문당 1회) 별도.">
<link rel="canonical" href="https://rndsetup.com/brands/dodochem/{slug}/">
<meta property="og:type" content="product"><meta property="og:title" content="{kname} — DodoChem 정품"><meta property="og:description" content="{desc} — {use}."><meta property="og:url" content="https://rndsetup.com/brands/dodochem/{slug}/"><meta property="og:image" content="https://rndsetup.com{img}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Product","name":"{kname}","sku":"{code}","brand":{{"@type":"Brand","name":"DodoChem"}},"image":"https://rndsetup.com{img}","description":"{desc} — {use}.","offers":{{"@type":"AggregateOffer","priceCurrency":"KRW","lowPrice":{vis[0][2]},"highPrice":{vis[-1][2]},"offerCount":{len(vis)},"availability":"https://schema.org/InStock","seller":{{"@type":"Organization","name":"실험셋업연구소"}}}}}}
</script>
<link rel="stylesheet" href="/assets/site.css">
{STYLE}
</head>
<body>
<div id="pumplab-header"></div>

<main class="wrap" style="max-width:832px;margin:0 auto;padding:26px 18px 60px">
<nav style="font-size:12.5px;color:#8a8f98;margin-bottom:10px"><a href="/" style="color:inherit">홈</a> › <a href="/product/" style="color:inherit">제품</a> › 배터리 재료 · {sobun}</nav>
<h1 style="font-family:var(--serif);font-size:clamp(21px,4vw,27px);color:#2A2570;margin:0 0 2px">{kname}</h1>
<div style="font-size:13px;color:#8a8f98;margin-bottom:14px">{ename}</div>

<figure style="margin:0 0 14px"><img src="{img}" alt="{kname} 제품 사진" style="display:block;width:100%;max-width:360px;margin:0 auto;border:1px solid #D8E4F2;border-radius:12px;background:#fff"></figure>

<p class="dt-sum"><b>{desc}</b> — {use}. 규격 <b>{vis[0][1]}{u} ~ {vis[-1][1]}{u}</b>, 소비자가 <b>{lows[code]:,}원~</b>.</p>

<h2 class="pkg-h">사양 요약</h2>
<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>
{spec_rows(m, s)}
</tbody></table></div>

<h2 class="pkg-h">규격 · 소비자가</h2>
<div class="pkg-tblwrap"><table class="pkg-tbl"><thead><tr><th>규격</th><th>{'배합' if typ=='elec' else '설명'}</th><th style="text-align:center">소비자가</th></tr></thead><tbody>
{tbl}
</tbody></table></div>
<p class="pkg-note" style="margin-top:14px">표기 가격은 소비자가(부가세 별도)이며 <b>해외배송비 100,000원(주문당 1회) 별도</b>입니다. 해외 직수입 품목으로 상시 할인 대상이 아닙니다.{dropnote}{smallnote}</p>
<p style="margin-top:14px"><button type="button" class="qbtn" data-quote="{kname} (규격·수량 문의)">견적문의</button></p>

{papers}<h2 class="pkg-h" style="margin-top:26px">자주 묻는 질문</h2>
{faq_html}
</main>

<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''
    d = f'brands/dodochem/{slug}'
    os.makedirs(d, exist_ok=True)
    fo = open(d + '/index.html', 'w', encoding='utf-8'); fo.write(page); fo.flush(); os.fsync(fo.fileno()); fo.close()
    pages += 1
    # 허브 카드
    txt = f"{kname} {code} {desc} {use} {sobun} dodochem 배터리 재료".lower().replace('"', '')
    hub_cards.append(f'''<article class="dscard" data-cat="material" data-text="{txt}">
  <div class="dscard-im"><img src="{img}" alt="{kname}" loading="lazy" width="760" height="760"><div class="dscard-bdg"><span class="b y">{sobun}</span></div></div>
  <div class="dscard-bd">
    <h3 class="dscard-mdl"><a class="dscard-link" href="/brands/dodochem/{slug}/">{kname.replace('DodoChem ','')}</a></h3>
    <div class="dscard-nm">{code} · {vis[0][1]}{u}~{vis[-1][1]}{u}</div>
    <p class="dscard-d">{desc} — {use}.</p>
    <p class="dscard-p">{len(vis)}규격 · {lows[code]:,}원부터</p>
  </div>
</article>''')

# 허브 재작성 (13카드)
HUB = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url=/product/">
<title>DodoChem 제품 — 통합 카탈로그로 이동</title>
</head>
<body>
<p><a href="/product/">전 제품 통합 카탈로그로 이동</a></p>
''' + '\n'.join(hub_cards) + '''
</body>
</html>
'''
fo = open('brands/dodochem/index.html', 'w', encoding='utf-8'); fo.write(HUB); fo.flush(); os.fsync(fo.fileno()); fo.close()

# SQL: 기존 DodoChem 블록 교체
p = 'rndsetup_products.sql'
s = open(p, encoding='utf-8').read()
s = re.sub(r"\n-- 도도켐\(DodoChem\).*$", "", s, flags=re.S)
s = re.sub(r"\n-- DodoChem.*$", "", s, flags=re.S)
block = ("\n-- DodoChem 배터리 재료 — 판매가 = CNY 소비자가 x 환율계수 210(=올림10(스팟 204.46 x 1.02), 2026-09-02) x 1.45, 1,000원 반올림"
         "\n-- 해외배송비(고객) 100,000원/주문 별도 · 상시 3% 할인 미적용 · 5만원 미만 SKU 미등록(합산 견적)\n"
         + "\n".join(sql_rows) + "\n")
fo = open(p, 'w', encoding='utf-8'); fo.write(s + block); fo.flush(); os.fsync(fo.fileno()); fo.close()

print('pages:', pages, '| sql rows:', len(sql_rows), '| lows:', {k: f'{v:,}' for k, v in lows.items()})
