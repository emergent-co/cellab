# DodoChem 단독 상세 63종 → _build/products/dodochem.json 이관 (§4.6 파이프라인)
# 가격: overseas-pricing 공식① CNY×210×1.45, 1,000원 반올림 · buybox p = 제품가+배송료 100,000
import os, re, json, shutil, collections

FX, K, SHIP = 210, 1.45, 100000
def won(c): return int(round(c * FX * K / 1000.0)) * 1000

data = json.load(open('/tmp/dodo/all.json', encoding='utf-8'))
prices = json.load(open('/tmp/dodo/prices.json', encoding='utf-8'))
pmap = collections.defaultdict(list)
for pid, val, pname, price in prices: pmap[pid].append((pname, val, float(price)))
top50 = set(json.load(open('/tmp/dodo/top50_ids.json')))
byid = {r[1]: r for r in data}

KO = {'리튬황':'리튬황 전해액','리튬2차':'리튬이온 전해액','리튬1차':'리튬 1차 전해액','리튬공기':'리튬-공기 전해액',
 'NaClO4':'나트륨이온 전해액','NaPF6':'나트륨이온 전해액','NaCF3SO3':'나트륨이온 전해액','KPF6':'칼륨이온 전해액',
 'Mg':'마그네슘이온 전해액','Al':'알루미늄이온 전해액','Zn':'아연이온 전해액','Ca':'칼슘이온 전해액',
 '슈퍼커패시터':'슈퍼커패시터 전해액','혼합용매':'혼합 용매','커스텀':'커스텀 전해액','용질염':'전해질 염',
 '고순도용매':'고순도 용매','첨가제':'전해액 첨가제','기타':'시약','전지케이스':'코인셀 케이스','케이스304':'SUS304 코인셀 케이스',
 '케이스316':'SUS316 코인셀 케이스','분리막':'분리막','Whatman':'Whatman 유리섬유 분리막','Celgard':'Celgard 분리막',
 '재단분리막':'재단 분리막 원판','바인더':'바인더','도전재':'도전재','집전체':'집전체','음극재':'음극재','양극재':'양극재','고체전해질':'고체전해질'}
USE = {'리튬황':'리튬-황(Li-S) 전지 · Li–Li 대칭 셀','리튬2차':'리튬이온 2차전지','리튬1차':'리튬 1차전지','리튬공기':'리튬-공기 전지',
 'NaClO4':'나트륨이온 전지','NaPF6':'나트륨이온 전지','NaCF3SO3':'나트륨이온 전지','KPF6':'칼륨이온 전지','Mg':'마그네슘 전지',
 '슈퍼커패시터':'슈퍼커패시터','용질염':'전해액 조액용 용질 염','고순도용매':'전해액 조액용 무수 용매','첨가제':'전해액 첨가제',
 '전지케이스':'코인셀 조립','케이스304':'코인셀 조립(SUS304)','Whatman':'코인셀·가시화 셀 분리막(재단용)','Celgard':'코인셀 분리막',
 '재단분리막':'코인셀 조립','바인더':'전극 슬러리 바인더'}

# 기존 13종 (slug·이미지·이름 유지)
OLD = {
 'LS-009': ('ls-009-lithium-sulfur-electrolyte','ls-009-1.jpg','리튬황 전해액 LS-009','Lithium-Sulfur Electrolyte LS-009'),
 'LS-002': ('ls-002-lithium-sulfur-electrolyte','ls-002-1.jpg','리튬황 전해액 LS-002','Lithium-Sulfur Electrolyte LS-002'),
 'LB-002': ('lb-002-lithium-ion-electrolyte','lb-002-1.jpg','리튬이온 전해액 LB-002','Lithium-ion Electrolyte LB-002'),
 'LB-008': ('lb-008-lithium-ion-electrolyte','lb-008-1.jpg','리튬이온 전해액 LB-008','Lithium-ion Electrolyte LB-008'),
 'NC-004': ('nc-004-naclo4-electrolyte','nc-004-1.jpg','나트륨이온 전해액 NC-004','NaClO4 Electrolyte NC-004'),
 'NP-005': ('np-005-napf6-electrolyte','np-005-1.jpg','나트륨이온 전해액 NP-005','NaPF6 Electrolyte NP-005'),
 'NE-000027': ('lifsi-battery-grade','lifsi-1.jpg','LiFSI 전해질 염','LiFSI — Lithium bis(fluorosulfonyl)imide'),
 'NE-000014': ('litfsi-battery-grade','litfsi-1.jpg','LiTFSI 전해질 염','LiTFSI — Lithium bis(trifluoromethanesulfonyl)imide'),
 'NE-000063': ('dme-anhydrous-solvent','dme-1.jpg','DME 고순도 용매','DME — 1,2-Dimethoxyethane (anhydrous)'),
 'NE-000061': ('dmc-anhydrous-solvent','dmc-1.jpg','DMC 고순도 용매','DMC — Dimethyl carbonate (anhydrous)'),
 'NE-000675': ('whatman-gfd-125mm','whatman-gfd-1.jpg','Whatman GF/D 유리섬유 분리막 125mm','Whatman GF/D Glass Fiber Separator 1823-125mm'),
 'NE-000608': ('ceramic-disc-18mm','ceramic-disc-18-1.jpg','단면 세라믹 분리막 원형 18mm','Ceramic-coated Separator Disc Φ18 mm'),
 'NE-000183': ('pvdf-hsv900-binder','pvdf-hsv900-1.jpg','PVDF 바인더 HSV900','PVDF Binder HSV900 (Arkema)'),
}

def parse(r):
    sub = r[0].split('|')[1]
    m = re.search(r'配方[：:]\s*(.+?)\s*$', r[4])
    formula = m.group(1).strip() if m else ''
    ab = re.search(r'简称[：:]\s*([A-Za-z0-9\-]+)', r[4])
    ch = re.search(r'化学式[：:]\s*([A-Za-z0-9\.\·]+)', r[4])
    wm = re.search(r'(Whatman\s*[A-Z/]+\s*[0-9\-]+[a-z]*mm?)', r[2], re.I)
    return sub, formula, (ab.group(1) if ab else ''), (ch.group(1) if ch else ''), (wm.group(1) if wm else '')

def visible(pid):
    return [(v, c, won(c)) for _, v, c in sorted(pmap.get(pid, []), key=lambda x: x[2]) if won(c) >= 50000]

def mkname(r):
    code = r[3]
    if code in OLD: return OLD[code][2], OLD[code][3], OLD[code][0], OLD[code][1]
    sub, formula, abbr, chem, wm = parse(r)
    if formula: nm = f"{KO.get(sub, sub)} {code}"; en = f"Electrolyte {code}"
    elif abbr: nm = f"{abbr} ({KO.get(sub, sub)})"; en = abbr
    elif wm: nm = f"유리섬유 분리막 {wm}"; en = wm
    else: nm = f"{KO.get(sub, sub)} {code}"; en = code
    return nm, en, 'p-' + code.lower(), f"{code.lower()}-1.jpg"

products = []
count = 0
for r in data:
    code = r[3]
    if not (code in OLD or r[1] in top50): continue
    vis = visible(r[1])
    if not vis: continue
    sub, formula, abbr, chem, wm = parse(r)
    unit = r[6] or 'g'
    nm, en, slug, imgfile = mkname(r)
    cat = KO.get(sub, sub)
    use = USE.get(sub, '배터리 실험')
    desc_core = formula or (f"CAS {r[5]}" if r[5] else re.sub(r'\s+', ' ', r[4])[:70])
    low, high = vis[0][2], vis[-1][2]
    rng = f"{vis[0][1]}{unit}~{vis[-1][1]}{unit}"
    is_elec = bool(formula)
    is_chem = sub in ('용질염', '고순도용매', '첨가제', '기타')
    answer = (f"{nm}는 <b>{desc_core}</b> 배합의 {use}용 전해액입니다. 규격 {rng}를 밀봉 포장으로 공급합니다." if is_elec
              else f"{nm}는 {use}용 배터리 등급 제품입니다. {desc_core}, 규격 {rng}를 밀봉 포장으로 공급합니다.")
    features = ([f"배합 <b>{formula}</b> — 전 규격 동일 배합", f"{use} 실험에 바로 쓰는 조액 완제품",
                 f"<b>{rng}</b> {len(vis)}규격 — 소량 스크리닝부터 다량 조립까지", "농도·용매비·첨가제를 바꾼 <b>커스텀 배합</b>은 견적으로 안내"] if is_elec else
                [f"{use}용 배터리 등급", (f"CAS <b>{r[5]}</b>" + (f" · 화학식 {chem}" if chem else '')) if r[5] else f"<b>{desc_core}</b>",
                 f"<b>{rng}</b> {len(vis)}규격", "규격·수량 커스텀은 견적으로 안내"])
    specs = [["용도", use], ["보관·취급", "Ar 글러브박스 취급 권장 · 수분 민감" if (is_elec or is_chem) else "건조 보관"],
             ["브랜드", "DodoChem · 원산지 중국"], ["가격 조건", "VAT 별도 · 국제 배송료 100,000원 (주문당 1회)"]]
    if r[5]: specs.insert(1, ["CAS", r[5] + (f" · 화학식 {chem}" if chem else '')])
    variants = {"heading": "규격 비교", "head": ["규격", "배합" if is_elec else "설명", "포장"],
                "rows": [[f"{v} {unit}", desc_core, "알루미늄 병" if is_elec else "밀봉 포장"] for v, c, w in vis]}
    buybox = [{"m": f"{v} {unit}", "s": code, "p": w + SHIP, "x": w} for v, c, w in vis]
    faq = ([{"tag": "배합", "q": "다른 배합도 주문할 수 있나요?", "a": "네. 염 농도·용매비·첨가제를 바꾼 커스텀 배합이 가능합니다. 원하는 배합식을 견적 문의에 그대로 적어 주세요."}] if is_elec else
           [{"tag": "커스텀", "q": "규격·수량 커스텀이 되나요?", "a": "네. 원하는 조건(규격·수량)을 견적 문의에 적어 주시면 맞춰 안내합니다."}])
    faq += [{"tag": "취급", "q": "보관은 어떻게 하나요?", "a": "수분에 민감한 품목은 아르곤 글러브박스에서 개봉·취급하시길 권장합니다. 밀봉 포장으로 배송됩니다."},
            {"tag": "가격", "q": "표기 가격 기준이 어떻게 되나요?", "a": "표기 가격은 소비자가이며 부가세 별도입니다. 국제 배송료 100,000원(주문당 1회)이 별도이고, 해외 직수입 품목으로 상시 할인 대상이 아닙니다."}]
    entry = {
        "slug": slug, "name": nm, "name_en": f"DodoChem {en}",
        "sub": desc_core[:80], "category": f"배터리 재료 · {cat}",
        "buybox": buybox, "images": [imgfile], "image_alt": f"DodoChem {nm} 제품 사진",
        "answer": answer,
        "summary": f"{use}용 {'전해액' if is_elec else cat}입니다. <b>{desc_core}</b>, 규격 <b>{rng}</b> {len(vis)}종을 공급합니다.",
        "features": features, "specs": specs, "variants": variants,
        "related": "배터리 재료: <a href=\"/materials/\">전기화학 재료·소모품</a> · <a href=\"/brands/dodochem/\">DodoChem 전체</a> · <a href=\"/wiki/\">배터리 사전</a>",
        "keywords": [["#DodoChem", "/brands/dodochem/"], [f"#{cat.replace(' ', '')}", "/materials/"], ["#배터리재료", "/materials/"], ["#실험장비카탈로그", "/product/"]],
        "faq": faq,
        "ld": {"name": f"DodoChem {nm}", "sku": code, "category": f"배터리 재료 · {cat}",
               "description": f"{desc_core} — {use}. 규격 {rng}.", "low": low, "high": high, "count": len(vis)},
        "source": {"url": f"https://www.dodochem.com/product?id={r[1]}", "label": "DodoChem 제품 페이지"},
    }
    products.append(entry)
    count += 1

# LS-009: 기존 이관본 필드(문안·papers 등) 보존 + 가격만 갱신
J = '_build/products/dodochem.json'
doc = json.load(open(J, encoding='utf-8'))
old_by_slug = {p['slug']: p for p in doc['products']}
merged = []
for e in products:
    o = old_by_slug.get(e['slug'])
    if o:
        o['buybox'] = e['buybox']
        o['ld']['low'], o['ld']['high'], o['ld']['count'] = e['ld']['low'], e['ld']['high'], e['ld']['count']
        o.setdefault('source', e['source'])
        merged.append(o)
    else:
        merged.append(e)
doc['products'] = merged
json.dump(doc, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json products:', len(merged))

# 손 HTML 단독 페이지 삭제(빌드가 재생성) — 계열 series-* 및 허브 index는 유지
kept, removed = 0, 0
for d in os.listdir('brands/dodochem'):
    full = os.path.join('brands/dodochem', d)
    if not os.path.isdir(full): continue
    if d.startswith('series-'): kept += 1; continue
    if d in [p['slug'] for p in merged]:
        shutil.rmtree(full); removed += 1
print('hand pages removed:', removed, '| series kept:', kept)
