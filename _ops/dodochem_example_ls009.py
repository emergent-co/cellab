# DodoChem 예시 등록 1건: LS-009 리튬황 전해액 (소비자가 = CNY × 195 × 1.45, 100원 반올림 · 배송료 100,000원 별도)
import os, re

RATE = 195 * 1.45
def won(cny):
    return int(round(cny * RATE / 100.0)) * 100
SKUS = [(50, 360), (100, 500), (250, 1000), (500, 1700), (1000, 2400)]  # g, CNY
PRICES = [(g, c, won(c)) for g, c in SKUS]

# ── 1) SQL (가격 SSOT) ──
sql_rows = []
for g, cny, krw in PRICES:
    sql_rows.append(
        "INSERT INTO products (sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v,status) VALUES "
        f"('DD-LS009-{g}',910,'DodoChem','DodoChem(도도켐)','중국','배터리 소재','전해액','LS-009','규격','{g}g',"
        f"'도도켐 리튬황 전해액 LS-009 {g}g','1.배합 1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3 | 2.형식 리튬-황 전해액 | 3.규격 {g}g','','ea',0,{krw},"
        "'https://rndsetup.com/img/dodochem/ls-009-1.jpg','https://rndsetup.com/brands/dodochem/ls-009-lithium-sulfur-electrolyte/','','','',"
        f"'카탈로그가','CNY {cny}','계열','전해액','','','','','판매중');")
sql_block = ("\n-- 도도켐(DodoChem) 배터리 재료 — 소비자가 = 카탈로그가(CNY) x 195 x 1.45 (100원 반올림) · 국제 배송료 100,000원 별도 · 상시 할인 미적용\n"
             + "\n".join(sql_rows) + "\n")
p = 'rndsetup_products.sql'
s = open(p, encoding='utf-8').read()
if 'DD-LS009' not in s:
    fo = open(p, 'a', encoding='utf-8'); fo.write(sql_block); fo.flush(); os.fsync(fo.fileno()); fo.close()
    print('SQL +', len(sql_rows), '행')

# ── 2) build.py ALLPROD_BRANDS 등록 ──
p = '_build/build.py'
s = open(p, encoding='utf-8').read()
if "('dodochem'" not in s:
    s = s.replace("    ('hefei', '허페이 인시츄', 'echem'),",
                  "    ('hefei', '허페이 인시츄', 'echem'),\n    ('dodochem', '도도켐', 'echem'),")
    fo = open(p, 'w', encoding='utf-8'); fo.write(s); fo.flush(); os.fsync(fo.fileno()); fo.close()
    print('build.py 브랜드 등록')

# ── 3) 가오스 상세 <style> 이식 ──
src = open('brands/gaossunion/agcl-reference-electrode/index.html', encoding='utf-8').read()
m = re.search(r'<style>.*?</style>', src, re.S)
STYLE = m.group(0)

low = PRICES[0][2]
tbl = "\n".join(
    f"<tr><td><b>LS-009</b> · {g} g</td><td>1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3</td><td style=\"text-align:center\"><b>{krw:,}원</b></td></tr>"
    for g, cny, krw in PRICES)

DETAIL = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>도도켐 리튬황 전해액 LS-009 — 1M LiTFSI in DME:DOL 1:1 + 2% LiNO3 | 실험셋업연구소</title>
<meta name="description" content="도도켐(DodoChem) 리튬황 전해액 LS-009 — 배합 1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3. 리튬-황 전지 표준 전해액, 규격 50g~1kg. 소비자가 {low:,}원~, 국제 배송료 100,000원 별도.">
<link rel="canonical" href="https://rndsetup.com/brands/dodochem/ls-009-lithium-sulfur-electrolyte/">
<meta property="og:type" content="product"><meta property="og:title" content="리튬황 전해액 LS-009 — 도도켐 정품"><meta property="og:description" content="1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3 — 리튬-황 전지 표준 전해액. 50g~1kg."><meta property="og:url" content="https://rndsetup.com/brands/dodochem/ls-009-lithium-sulfur-electrolyte/"><meta property="og:image" content="https://rndsetup.com/img/dodochem/ls-009-1.jpg">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Product","name":"도도켐 리튬황 전해액 LS-009","sku":"LS-009","brand":{{"@type":"Brand","name":"DodoChem","alternateName":"도도켐"}},"image":"https://rndsetup.com/img/dodochem/ls-009-1.jpg","description":"리튬-황 전지 표준 전해액 — 1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3. 규격 50g~1kg.","offers":{{"@type":"AggregateOffer","priceCurrency":"KRW","lowPrice":{PRICES[0][2]},"highPrice":{PRICES[-1][2]},"offerCount":{len(PRICES)},"availability":"https://schema.org/InStock","seller":{{"@type":"Organization","name":"실험셋업연구소"}}}}}}
</script>
<link rel="stylesheet" href="/assets/site.css">
{STYLE}
</head>
<body>
<div id="pumplab-header"></div>

<main class="wrap" style="max-width:832px;margin:0 auto;padding:26px 18px 60px">
<nav style="font-size:12.5px;color:#8a8f98;margin-bottom:10px"><a href="/" style="color:inherit">홈</a> › <a href="/product/" style="color:inherit">제품</a> › 배터리 재료 · 전해액</nav>
<h1 style="font-family:var(--serif);font-size:clamp(21px,4vw,27px);color:#2A2570;margin:0 0 2px">도도켐 리튬황 전해액 LS-009</h1>
<div style="font-size:13px;color:#8a8f98;margin-bottom:14px">DodoChem Lithium-Sulfur Electrolyte LS-009</div>

<figure style="margin:0 0 14px"><img src="/img/dodochem/ls-009-1.jpg" alt="도도켐 리튬황 전해액 LS-009 제품 사진 — 알루미늄 병 포장" style="display:block;width:100%;max-width:360px;margin:0 auto;border:1px solid #D8E4F2;border-radius:12px;background:#fff"></figure>

<p class="dt-sum">리튬-황 전지의 <b>표준 전해액</b> — 배합 <b>1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3</b>. LiNO3 2%가 리튬 음극 표면을 보호해 셔틀 효과를 억제합니다. 규격 <b>50 g ~ 1 kg</b>, 소비자가 <b>{low:,}원~</b>.</p>

<h2 class="pkg-h">사양 요약</h2>
<div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>
<tr><th>배합</th><td><b>1M LiTFSI in DME:DOL=1:1 Vol% with 2%LiNO3</b></td></tr>
<tr><th>용도</th><td>리튬-황(Li-S) 전지 · Li–Li 대칭 셀 전해액</td></tr>
<tr><th>규격</th><td>50 / 100 / 250 / 500 / 1000 g (알루미늄 병)</td></tr>
<tr><th>보관·취급</th><td>Ar 글러브박스 취급 권장 · 수분 민감</td></tr>
<tr><th>브랜드</th><td>DodoChem(도도켐) · 원산지 중국</td></tr>
</tbody></table></div>

<h2 class="pkg-h">규격 · 소비자가</h2>
<div class="pkg-tblwrap"><table class="pkg-tbl"><thead><tr><th>규격</th><th>배합</th><th style="text-align:center">소비자가</th></tr></thead><tbody>
{tbl}
</tbody></table></div>
<p class="pkg-note" style="margin-top:14px">표기 가격은 소비자가(부가세 별도)이며 <b>국제 배송료 100,000원 별도</b>입니다. 해외 직수입 품목으로 상시 할인 대상이 아닙니다. 커스텀 배합(농도·용매비·첨가제)은 견적으로 안내합니다.</p>
<p style="margin-top:14px"><button type="button" class="qbtn" data-quote="도도켐 리튬황 전해액 LS-009 (규격·수량 문의)">견적문의</button></p>

<h2 class="pkg-h" style="margin-top:26px">자주 묻는 질문</h2>
<div class="faq-item"><p class="faq-q"><span class="faq-tag">배합</span>다른 배합도 주문할 수 있나요?</p><p class="faq-a">네. LiNO3 비율, 염 농도, 용매비를 바꾼 커스텀 배합이 가능합니다. 원하는 배합식을 견적 문의에 그대로 적어 주세요.</p></div>
<div class="faq-item"><p class="faq-q"><span class="faq-tag">취급</span>보관은 어떻게 하나요?</p><p class="faq-a">수분에 민감하므로 아르곤 글러브박스에서 개봉·취급하시길 권장합니다. 밀봉 알루미늄 병으로 배송됩니다.</p></div>
<div class="faq-item"><p class="faq-q"><span class="faq-tag">가격</span>표기 가격 기준이 어떻게 되나요?</p><p class="faq-a">표기 가격은 소비자가이며 부가세 별도입니다. 국제 배송료 100,000원이 별도이고, 해외 직수입 품목으로 상시 할인 대상이 아닙니다.</p></div>
</main>

<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''
os.makedirs('brands/dodochem/ls-009-lithium-sulfur-electrolyte', exist_ok=True)
fo = open('brands/dodochem/ls-009-lithium-sulfur-electrolyte/index.html', 'w', encoding='utf-8')
fo.write(DETAIL); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('상세페이지 생성')

# ── 4) 브랜드 허브 (비노출 · 카드 수집용) ──
HUB = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url=/product/">
<title>도도켐 제품 — 통합 카탈로그로 이동</title>
</head>
<body>
<p><a href="/product/">전 제품 통합 카탈로그로 이동</a></p>
<article class="dscard" data-cat="material">
  <a href="/brands/dodochem/ls-009-lithium-sulfur-electrolyte/">
    <img src="/img/dodochem/ls-009-1.jpg" alt="도도켐 리튬황 전해액 LS-009">
    <h3>리튬황 전해액 LS-009</h3>
    <p class="ds-model">LS-009</p>
    <ul>
      <li>배합 1M LiTFSI in DME:DOL=1:1 Vol% + 2%LiNO3</li>
      <li>규격 50 g ~ 1 kg (알루미늄 병)</li>
      <li>리튬-황 전지 · Li–Li 대칭 셀 전해액</li>
    </ul>
    <p class="ds-price">{low:,}원~</p>
  </a>
</article>
</body>
</html>
'''
os.makedirs('brands/dodochem', exist_ok=True)
fo = open('brands/dodochem/index.html', 'w', encoding='utf-8')
fo.write(HUB); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('허브 생성 — 완료')
