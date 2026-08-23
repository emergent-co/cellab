"""
sitemap.xml 빌드 스크립트 (카테고리 페이지는 2026-05-15에 폐기)
============================================================
사용법: GitHub Actions가 _build/ 변경 시 자동 실행

입력:
  _build/categories.json            (카테고리 빈 dict — 폐기 표시)
  _build/posts.json                 블로그 글 메타

출력 (워크스페이스 루트):
  sitemap.xml

카테고리 페이지 폐기 이력:
  2026-05-15  pump.html / tubing.html / syringe.html / pumphead.html / fitting.html / other.html
              모두 leadfluid.html redirect 1장으로 교체. STRATEGY.md § 5 참조.
============================================================
"""

import json
import os
import re
from html import escape
from urllib.parse import quote


# 80% 마켓 송출 / 20% 자사몰 (PSYS 카드결제 = 견적 후 안내)
KAKAO_INQUIRY_URL = 'http://pf.kakao.com/_GCsjX'


def append_utm(url, source_campaign):
    if not url:
        return url
    sep = '&' if '?' in url else '?'
    return url + sep + 'utm_source=pumplab&utm_medium=catalog&utm_campaign=' + source_campaign


# 올포랩 시리즈 페이지 매핑 — 모델명 패턴으로 자동 매핑
# admin에서 buy_allforlab_url 직접 입력 안 한 모델도 정확한 시리즈 페이지로 송출
ALLFORLAB_BASE_URL = 'https://www.allforlab.com/pdt/'
SERIES_S = ALLFORLAB_BASE_URL + 'PDNN26050200003?keywords='   # BT*S, BQ*
SERIES_FL = ALLFORLAB_BASE_URL + 'PDNN26050200005?keywords='  # BT*F, BT*L, BT600P, BT*-2J
SERIES_CT = ALLFORLAB_BASE_URL + 'PDNN26050200006?keywords='  # CT*
SERIES_TYD = ALLFORLAB_BASE_URL + 'PDNN26050200007?keywords=' # TYD*, TYS*
SERIES_TFD = ALLFORLAB_BASE_URL + 'PDNN26050200008?keywords=' # TFD*


def map_to_allforlab_series(model):
    """모델명을 보고 해당 올포랩 시리즈 페이지 URL 반환. 매칭 안 되면 None."""
    if not model:
        return None
    m = model.upper().strip()
    if m.startswith('CT'):
        return SERIES_CT
    if m.startswith('TFD'):
        return SERIES_TFD
    if m.startswith('TYD') or m.startswith('TYS'):
        return SERIES_TYD
    if m.startswith('BQ'):
        return SERIES_S
    if m.startswith('BT'):
        if '-2J' in m:
            return SERIES_FL
        if m.endswith('P'):
            return SERIES_FL
        if m.endswith('F') or m.endswith('L') or m.endswith('F-1') or m.endswith('L-1'):
            return SERIES_FL
        if m.endswith('S') or m.endswith('S-1'):
            return SERIES_S
    return None


def build_market_urls(p):
    cat = p.get('category', 'pump')
    model = p.get('code') or p.get('id') or ''
    buy_a = (p.get('buy_allforlab_url') or '').strip()
    buy_n = (p.get('buy_navimro_url') or '').strip()
    if not buy_a:
        buy_a = map_to_allforlab_series(model)
    if not buy_a:
        buy_a = 'https://www.allforlab.com/search?k=' + quote(model)
    if not buy_n:
        buy_n = 'https://www.navimro.com/search?q=' + quote(model)
    return append_utm(buy_a, 'allforlab_' + cat), append_utm(buy_n, 'navimro_' + cat)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)


def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(path, content):
    """변경된 경우에만 파일 쓰기 (OneDrive 동기화 부담 감소)."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing = f.read()
            if existing == content:
                return False  # 변경 없음 → 안 씀
        except Exception:
            pass
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def build_seo_intro(h1_text, intro_text):
    return (
        '<div class="seo-intro">\n'
        f'      <h1>{escape(h1_text)}</h1>\n'
        f'      <p>{escape(intro_text)}</p>\n'
        '    </div>'
    )


def render_product_card(p, spec_labels):
    """단일 제품 → 카드 HTML. 스펙 라벨은 카테고리별로 다름."""
    if p.get('visible') is False:
        return ''
    cat = p.get('category', 'pump')
    labels = spec_labels.get(cat, ['스펙1','스펙2','스펙3','스펙4'])
    name = escape(p['name'])
    code = escape(p.get('code', p.get('id', '')))
    spec1 = escape(p.get('spec1', ''))
    spec2 = escape(p.get('spec2', ''))
    spec3 = escape(p.get('spec3', ''))
    spec4 = escape(p.get('spec4', ''))
    price = p.get('price', 0)
    price_text = p.get('price_text') or (f'{price:,}원' if price > 0 else '견적 문의')
    cat_page = p.get('catalog_page', 1)
    pid = escape(p['id'])
    keywords = p.get('keywords', [])
    kw_html = ''.join(f'              <span class="prod-kw">{escape(k)}</span>\n' for k in keywords[:3])

    # 이미지: image_url 있으면 <img>, 없으면 placeholder (코드 + 시리즈)
    image_url = (p.get('image_url') or '').strip()
    if image_url:
        img_html = f'<img src="{escape(image_url)}" alt="{name}" loading="lazy" style="width:100%;height:100%;object-fit:contain">'
    else:
        img_html = f'<span class="ph-code">{code}</span><span class="ph-series">{escape(spec1)}</span>'

    # 마켓 송출 URL (메인) — buy URL 우선, 없으면 검색 URL fallback. UTM 자동.
    buy_a, buy_n = build_market_urls(p)

    return f'''<div class="prod-card">
        <a class="prod" href="Leadfluid-2025-Catalog.pdf#page={cat_page}" target="_blank" rel="noopener">
          <div class="prod-img">{img_html}</div>
          <div class="prod-body">
            <div class="prod-name">{name}</div>
            <div class="prod-spec"><span class="label">{escape(labels[0])}</span><span class="val">{spec1}</span></div>
            <div class="prod-spec"><span class="label">{escape(labels[1])}</span><span class="val">{spec2}</span></div>
            <div class="prod-spec"><span class="label">{escape(labels[2])}</span><span class="val">{spec3}</span></div>
            <div class="prod-spec"><span class="label">{escape(labels[3])}</span><span class="val">{spec4}</span></div>
            <div class="prod-spec"><span class="label">가격</span><span class="val price">{escape(price_text)}</span></div>
            <div class="prod-tags">
{kw_html.rstrip()}
            </div>
          </div>
        </a>
        <div class="prod-actions">
          <a href="{escape(buy_a)}" target="_blank" rel="noopener" class="btn-buy btn-buy-primary">올포랩에서 구매</a>
          <a href="{escape(buy_n)}" target="_blank" rel="noopener" class="btn-buy btn-buy-secondary">나비엠알오</a>
        </div>
        <div class="prod-actions-inquiry">
          <a href="{KAKAO_INQUIRY_URL}" target="_blank" rel="noopener" class="btn-inquiry">견적·직접문의 (카카오톡)</a>
        </div>
      </div>'''


def render_category_jsonld(cat_id, cat_data, products, base_url, page_url):
    """카테고리별 BreadcrumbList + ItemList JSON-LD."""
    visible = [p for p in products if p.get('visible') is not False]
    label = cat_data.get('breadcrumb_label', cat_id)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": f"{base_url}index.html"},
            {"@type": "ListItem", "position": 2, "name": "카탈로그", "item": page_url},
            {"@type": "ListItem", "position": 3, "name": label}
        ]
    }

    product_items = []
    for p in visible:
        kw = p.get('keywords', [])
        desc = ' · '.join([p.get('spec1',''), p.get('spec2',''), p.get('spec3',''), p.get('spec4','')] + [', '.join(kw)] if kw else [p.get('spec1',''), p.get('spec2',''), p.get('spec3',''), p.get('spec4','')])
        product_items.append({
            "@type": "Product",
            "name": p['name'],
            "description": desc,
            "category": cat_data.get('h1', label),
            "brand": {"@type": "Brand", "name": "Lead Fluid"},
            "manufacturer": {"@type": "Organization", "name": "Lead Fluid"},
            "offers": {
                "@type": "Offer",
                "priceCurrency": "KRW",
                "price": p.get('price', 0),
                "availability": "https://schema.org/InStock",
                "seller": {"@type": "Organization", "name": "실험셋업연구소"},
                "url": f"{base_url}Leadfluid-2025-Catalog.pdf#page={p.get('catalog_page', 1)}"
            }
        })

    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"실험셋업연구소 {label} 카탈로그",
        "numberOfItems": len(product_items),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": pi}
            for i, pi in enumerate(product_items)
        ]
    }

    bc = json.dumps(breadcrumb, ensure_ascii=False, indent=2)
    il = json.dumps(itemlist, ensure_ascii=False, indent=2)
    return (
        '<script type="application/ld+json">\n' + bc + '\n</script>\n'
        '<script type="application/ld+json">\n' + il + '\n</script>'
    )


def render_page(cat_id, cat_data, template, partial_full, partial_preparing,
                base_url, products_by_cat, spec_labels):
    if cat_data.get('content') == 'full':
        content_block = partial_full
    else:
        content_block = partial_preparing.replace('{{CAT_LABEL}}', cat_data['breadcrumb_label'])

    seo_intro = build_seo_intro(cat_data['h1'], cat_data['intro'])
    content_block = content_block.replace('{{SEO_INTRO_BLOCK}}', seo_intro)

    canonical = base_url.rstrip('/') + '/' + cat_id + '.html'

    # PRODUCTS_OR_PREPARING — preparing partial 안의 분기 placeholder
    # 제품이 있으면 grid, 없으면 cat-prep(준비중) 패널
    if '{{PRODUCTS_OR_PREPARING}}' in content_block:
        cat_products = [p for p in products_by_cat.get(cat_id, []) if p.get('visible') is not False]
        label = cat_data['breadcrumb_label']
        if cat_products:
            cards = '\n\n      '.join(render_product_card(p, spec_labels) for p in cat_products)
            block = (
                '<div style="background:#e6f1fb;border:1px solid #b5d4ee;color:#1a4d7a;'
                'padding:12px 16px;border-radius:8px;margin-bottom:14px;font-size:12.5px">'
                '이 카테고리는 정식 카탈로그 준비 중입니다. 아래 제품은 임시 등록 항목으로, '
                '카테고리별 정식 분류·필터는 곧 추가됩니다.'
                '</div>\n'
                '<div class="products" style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">\n'
                + cards +
                '\n</div>'
            )
        else:
            block = (
                '<div class="cat-prep">\n'
                f'  <h2>{escape(label)} 카탈로그 준비중</h2>\n'
                f'  <p>곧 {escape(label)} 큐레이션 카탈로그를 공개합니다.<br>\n'
                '  먼저 필요한 사양이 있으시면 카톡·이메일로 견적 문의 부탁드립니다.</p>\n'
                '  <div class="cta-row">\n'
                '    <a class="primary" href="index.html#contact">상담 문의 →</a>\n'
                '    <a class="secondary" href="Leadfluid-2025-Catalog.pdf" target="_blank">카탈로그 PDF 보기</a>\n'
                '    <a class="secondary" href="tubing.html">튜브 카탈로그로 이동</a>\n'
                '  </div>\n'
                '</div>'
            )
        content_block = content_block.replace('{{PRODUCTS_OR_PREPARING}}', block)

    # PRODUCTS_HTML — 해당 카테고리 제품만
    if '{{PRODUCTS_HTML}}' in content_block:
        cat_products = products_by_cat.get(cat_id, [])
        cards = '\n\n      '.join(
            render_product_card(p, spec_labels)
            for p in cat_products
            if p.get('visible') is not False
        )
        content_block = content_block.replace('{{PRODUCTS_HTML}}', cards or '<div style="grid-column:1/-1;text-align:center;padding:40px;color:#888">아직 등록된 제품이 없습니다.</div>')

    # JSON_LD — 카테고리별 BreadcrumbList + ItemList
    if '{{JSON_LD_PUMP}}' in content_block:
        cat_products = products_by_cat.get(cat_id, [])
        if cat_products:
            jsonld = render_category_jsonld(cat_id, cat_data, cat_products, base_url, canonical)
            content_block = content_block.replace('{{JSON_LD_PUMP}}', jsonld)
        else:
            content_block = content_block.replace('{{JSON_LD_PUMP}}', '')

    html = template
    html = html.replace('{{TITLE}}', cat_data['title'])
    html = html.replace('{{META_DESC}}', cat_data['meta_description'])
    html = html.replace('{{BREADCRUMB_LABEL}}', cat_data['breadcrumb_label'])
    html = html.replace('{{CANONICAL_URL}}', canonical)
    html = html.replace('{{CONTENT_BLOCK}}', content_block)

    intro_css = (
        '<style>\n'
        '.seo-intro{background:#fff;border:1px solid #e3e8ef;border-radius:8px;padding:18px 22px;margin-bottom:14px}\n'
        '.seo-intro h1{font-size:20px;font-weight:700;color:#0a2540;margin:0 0 8px;letter-spacing:-.01em}\n'
        '.seo-intro p{font-size:13px;color:#5a6779;line-height:1.65;margin:0}\n'
        '</style>\n</head>'
    )
    if '.seo-intro' not in html:
        html = html.replace('</head>', intro_css)

    return html


REQ_LABEL = {'req': '요청됨', 'rev': '검토중', 'dev': '개발중', 'done': '완료'}
REQ_CLS = {'req': 's-req', 'rev': 's-rev', 'dev': 's-dev', 'done': 's-done'}
REQ_ORDER = {'req': 0, 'rev': 1, 'dev': 2, 'done': 3}


def _inject_between(html, start, end, content):
    """start~end 마커 사이를 content로 교체 (마커 유지, 정규식 미사용). 성공 여부 반환."""
    i = html.find(start)
    j = html.find(end)
    if i == -1 or j == -1 or j < i:
        return html, False
    i += len(start)
    return html[:i] + content + html[j:], True


def build_requests():
    """_build/requests.json → requests/index.html 에 정적 카드 + JSON 주입 (색인 가능, SSOT)."""
    req_path = os.path.join(SCRIPT_DIR, 'requests.json')
    html_path = os.path.join(ROOT_DIR, 'requests', 'index.html')
    if not os.path.exists(req_path) or not os.path.exists(html_path):
        print('  [skip] requests.json 또는 requests/index.html 없음')
        return
    with open(req_path, 'r', encoding='utf-8') as f:
        items = json.load(f).get('requests', [])

    # 표시 정렬: 상태순(req→rev→dev→done) → 날짜 내림차순. 원본 인덱스(openReq용) 유지.
    indexed = list(enumerate(items))
    indexed.sort(key=lambda t: t[1].get('date', ''), reverse=True)
    indexed.sort(key=lambda t: REQ_ORDER.get(t[1].get('status'), 9))

    cards = []
    for orig_i, r in indexed:
        status = r.get('status', 'req')
        cls = REQ_CLS.get(status, 's-req')
        label = REQ_LABEL.get(status, '요청됨')
        title = escape(r.get('title', ''))
        desc = escape(r.get('desc', ''))
        date = escape(r.get('date', ''))
        note = r.get('note', '')
        meta = '요청일 ' + date + (' · ' + escape(note) if note else '')
        image = (r.get('image') or '').strip()
        img = f'<img src="{escape(image)}" alt="{title}">' if image else '이미지 준비중'
        cards.append(
            f'<div class="req" onclick="openReq({orig_i})">'
            f'<div class="req-img">{img}</div>'
            f'<div class="req-bd"><div class="req-top"><h3>{title}</h3>'
            f'<span class="badge {cls}">{label}</span></div>'
            f'<p class="desc">{desc}</p>'
            f'<div class="meta">{meta}</div></div></div>'
        )
    cards_html = '\n'.join(cards)
    # JSON-in-HTML 안전: </script> 등 닫힘 방지
    json_str = json.dumps(items, ensure_ascii=False).replace('</', '<\\/')

    html = read(html_path)
    html, ok1 = _inject_between(html, '<!--REQ_CARDS_START-->', '<!--REQ_CARDS_END-->', cards_html)
    html, ok2 = _inject_between(html, '<!--REQ_JSON_START-->', '<!--REQ_JSON_END-->', json_str)
    if ok1 and ok2:
        write(html_path, html)
        print(f'  requests/index.html: {len(items)}개 요청 정적 렌더 + JSON 주입')
    else:
        print('  [warn] requests 마커를 찾지 못함 — 주입 생략 (카드/JSON 마커 확인)')


# ============================================================
# GEO: 크롤러가 raw HTML로 읽는 정적 링크·목록 주입
#   site.js는 JS 주입이라 AI 크롤러(GPTBot·ClaudeBot·PerplexityBot)에 안 보임.
#   빌드 시 내부 링크·논문 목록을 정적 HTML로 심어 크롤러 가시화. site.js가 런타임에 대체.
# ============================================================

# 크롤러용 사이트 전체 링크(푸터 div에 정적 주입 → site.js가 런타임에 대체)
CRAWLER_LINKS = [
    ('/', '홈'),
    ('/about/', '실험셋업연구소 회사소개 — 실험 셋업 매거진·논문 셋업·장비 안내'),
    ('/brands/sh-scientific/guide/', '삼흥에너지(SH-Scientific) 전기로·튜브퍼니스 — 제품 선택·견적·열처리 셋업'),
    ('/brands/sh-scientific/manual/', '삼흥에너지 전기로·튜브퍼니스 메뉴얼 — 사용법·승온 프로그램·안전'),
    ('/brands/sh-scientific/blog/', '삼흥에너지 전기로·튜브퍼니스 설치·A/S 블로그'),
    ('/brands/alicat/', 'ALICAT 질량유량계(MFC) — 정밀 가스 유량 제어'),
    ('/product/', '제품 통합 카탈로그 — 전기로·펌프·질량유량계(MFC)·전기화학 241종 (삼흥에너지·리드플루이드·Alicat·가오스유니온)'),
    ('/brands/gaossunion/', '가오스유니온 전기화학 전극·재료·CO₂ 환원 촉매 — 기준·상대·작업전극, RDE, GDE 캐소드'),
    ('/brands/gaossunion/co2rr-catalyst/', 'CO₂ 환원(CO₂RR) 촉매·전극 — Ag·Sn·Bi₂O₃·Cu 분말과 GDE 캐소드, IrO₂ 애노드'),
    ('/manuals/', '메뉴얼 모음 — 전기로·온도컨트롤러·펌프·MFC 사용 메뉴얼'),
    ('/requests/', '소프트웨어 제어'),
    ('/application/', '실험 가이드'),
    ('/application/biopharmaceutical.html', '바이오의약 — 발효·세포배양·정제·충전'),
    ('/application/analytical-instrument.html', '분석기기 — 컬럼 주입·시료 정량 주입'),
    ('/application/environmental.html', '환경 — 수질·폐수 정량 투입'),
    ('/application/flow-chemistry.html', 'flow chemistry 연속흐름 반응'),
    ('/brands/leadfluid/blog/', '펌프 셋업 사례 — 실제 도입·제어·유량 보정 셋업'),
    ('/pump/atoz/', '펌프 문제해결 — 유량 이상·튜빙 파손·멈춤 증상별 해결'),
    ('/magazine/pump-selection-wizard/', '펌프 선택 위저드 — 종류·유량·용도로 고르기'),
    ('/brands/leadfluid/', '리드플루이드 펌프 전체 제품 — 연동·시린지·기어·방폭'),
    ('/pump/atoz/peristaltic-flow-setpoint-mismatch/', '연동펌프 유량이 설정값과 다른 이유'),
    ('/pump/atoz/tubing-crush-tear-causes/', '연동펌프 튜빙 씹힘·찢어짐 원인·해결'),
    ('/pump/atoz/flow-calibration/', '연동펌프 유량 캘리브레이션 방법 — 설정값·실제 유량 보정'),
    ('/pump/atoz/tube-size-guide/', '연동펌프 튜브 규격·펌프헤드 가이드 — 번호별 내경(mm)·유량'),
    ('/pump/setups/plating-flow-calibration/', '도금 라인 유량 보정 셋업 — BT101L 2대 다펌프 제어(도입 스토리)'),
    ('/magazine/', '셋업 사례 — 논문 셋업·가이드·용어사전·도입 사례 (에너지·소재 공정)'),
    ('/magazine/battery/', '배터리 랩 A to Z — 전구체 공침부터 소성·코팅·셀 평가까지 배터리 소재 실험 셋업 커리큘럼'),
    ('/magazine/deposition/', '증착 공정 셋업 — CVD·ALD·MOCVD 박막 성장'),
    ('/magazine/heat-treatment/', '열처리 공정 셋업 — 하소·소둔·소결·경화·리플로우'),
    ('/magazine/oxidation/', '산화·확산 공정 셋업 — 건식/습식 산화·불순물 확산'),
    ('/magazine/sodium-cathode-atmosphere-dca/', '소듐 양극재 상순도 합성 — 소성 동적 분위기 제어(DCA) 셋업 (Nature Communications 2025)'),
    ('/magazine/aorfb-flowfield-electrolyte-pump/', '레독스흐름전지 전해액 순환 셋업 — 유로 설계 + 연동펌프 140 mL/min (PNAS 2024)'),
    ('/magazine/nickel-hydroxide-coprecipitation-cstr/', '배터리 양극재 전구체 공침 셋업 — CSTR + 연동펌프 3채널 정량 공급 (Chem. Eng. Technol. 2023)'),
    ('/magazine/sofc-hcl-syngas/', '석탄 합성가스 HCl이 SOFC 성능에 미치는 영향 — 가스 분위기·온도 제어 셋업 (J. Power Sources 2007)'),
    ('/magazine/guide-calcination-furnace-atmosphere/', '소성·하소용 튜브퍼니스·가스 분위기 선정 가이드 — 배터리 양극재·세라믹·촉매·분말 소재 공통'),
    ('/magazine/troubleshooting-calcination-batch-variation/', '소성 배치마다 결과가 다른 7가지 이유 — 양극재·세라믹·촉매·분말 소재 공통 트러블슈팅'),
    ('/magazine/glossary-heat-gas-terms/', '하소 vs 소성 vs 소결, sccm이란 — 열처리·가스 유량 용어사전 (에너지·소재 공정)'),
    ('/magazine/guide-pump-selection-energy-fluids/', '전해액·전구체·부식성 유체 펌프 선정 가이드 — 연동 vs 시린지 vs 기어 (에너지·소재 공정)'),
    ('/magazine/glossary-pump-fluid-terms/', 'mL/min과 rpm, 맥동, 접액부란 — 펌프·유체 용어사전 (에너지·소재 공정)'),
    ('/magazine/si-anode-cvd-carbon-coating/', '실리콘 음극 아세틸렌 CVD 탄소 코팅 셋업 — 튜브퍼니스+MFC (Nature Communications 2018)'),
    ('/magazine/electrode-slurry-mixing-thick-cathode/', '초후막 양극 슬러리 믹싱·전극 코팅 셋업 — 믹싱 궤적과 굴곡도 (Energy Technology 2023)'),
    ('/magazine/cuo-nanowire-thermal-oxidation/', '구리 열산화 CuO 나노와이어 성장 셋업 — 공기 450℃ (Scientific Reports 2019)'),
    ('/setups/damo-recirculation-bt600s.html', '혐기성 메탄산화 반응기 순환 — BT600S 연동펌프 (Environ. Sci. Technol. 2021)'),
    ('/setups/nitrification-ph-bq50s.html', '폐수 질산화 pH 제어 — BQ50S 정량펌프 (Bioresource Technology 2017)'),
    ('/setups/co2-capture-ct3001f.html', '연속 CO₂ 포집 — CT3001F PEEK 기어펌프 (Nature Communications 2024)'),
    ('/furnace/setups/', '퍼니스 셋업 사례 — 튜브퍼니스·전기로 가스·온도 제어 도입 사례'),
    ('/furnace/setups/alicat-mfc-tubefurnace/', '1500℃ 튜브퍼니스 가스 분위기 제어 — Alicat MFC 도입 사례'),
    ('/compare/imported-peristaltic-alternative/', 'Masterflex·Watson-Marlow 연동펌프 국내 대안'),
    ('/trust/', '믿고 도입할 때 (국내 A/S·정품·보증)'),
    ('/contact/', '문의하기 · 자주 묻는 질문(FAQ) — 견적·수리 A/S·제어 소프트웨어'),
]


def _crawler_nav_html():
    def grp(h):
        if h.startswith('/setups/') or h.startswith('/magazine/') or h.startswith('/compare/') or h in ('/', '/trust/', '/contact/'):
            return '사례·신뢰'
        if h.startswith('/pumps/') or h.startswith('/pump/') or h.startswith('/brands/leadfluid/') or h.startswith('/troubleshooting/') or h in ('/requests/', '/application/pump-selection.html', '/application/tube-selection.html', '/application/pump-pc-control-modbus-rs485.html', '/application/pump-flow-schedule-ramp.html', '/application/multi-pump-sync-unattended.html', '/application/pump-run-log-csv-reproducibility.html'):
            return '펌프·제어'
        if h in ('/application/cell-culture-perfusion.html', '/application/chemostat-continuous-culture.html', '/application/photobioreactor-microalgae.html', '/application/flow-chemistry.html', '/application/organ-on-chip-perfusion.html'):
            return '실험 기법'
        return '산업 분야'
    order = ['펌프·제어', '실험 기법', '산업 분야', '사례·신뢰']
    buckets = {g: [] for g in order}
    for href, label in CRAWLER_LINKS:
        buckets[grp(href)].append(f'<li><a href="{href}">{escape(label)}</a></li>')
    groups = ''.join(
        f'<div class="cn-group"><h5>{g}</h5><ul>{"".join(buckets[g])}</ul></div>'
        for g in order if buckets[g]
    )
    return '<nav class="crawler-nav" aria-label="사이트 전체 링크">' + groups + '</nav>'


def inject_setup_cta():
    """논문 셋업 글 하단에 '이 셋업 구성 그대로 견적·솔루션' CTA를 정적 주입(마커 기반 idempotent).
    셋업명을 ?setup=로 문의폼에 전달해 자동 채움. setups/·furnace/setups/·pump/setups/ 개별 글과
    magazine 논문글만 대상(허브 index·카테고리 허브 제외). </article> 포함 + h1 존재 조건."""
    from urllib.parse import quote
    START, END = '<!--SETUPCTA_START-->', '<!--SETUPCTA_END-->'
    HUB = {'setups/index.html', 'furnace/setups/index.html', 'pump/setups/index.html'}
    EXTRA = {
        'magazine/sofc-hcl-syngas/index.html',
        'magazine/sodium-cathode-atmosphere-dca/index.html',
        'magazine/aorfb-flowfield-electrolyte-pump/index.html',
        'magazine/nickel-hydroxide-coprecipitation-cstr/index.html',
        'magazine/si-anode-cvd-carbon-coating/index.html',
        'magazine/cuo-nanowire-thermal-oxidation/index.html',
        'magazine/electrode-slurry-mixing-thick-cathode/index.html',
    }  # 매거진 논문글(명시적으로만)
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if set(dirpath.split(os.sep)) & {'_build', '_to_delete'}:
            continue
        rel_dir = os.path.relpath(dirpath, ROOT_DIR).replace(os.sep, '/')
        in_setup_dir = rel_dir in ('setups', 'furnace/setups', 'pump/setups') or \
            rel_dir.startswith('setups/') or rel_dir.startswith('furnace/setups/') or rel_dir.startswith('pump/setups/')
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            rel = (rel_dir + '/' + fn) if rel_dir != '.' else fn
            if rel in HUB:
                continue
            if not (in_setup_dir or rel in EXTRA):
                continue
            p = os.path.join(dirpath, fn)
            html = read(p)
            if 'http-equiv="refresh"' in html or '</article>' not in html:
                continue
            m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
            if not m:
                continue
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if not title:
                continue
            block = (
                '<section class="setup-cta" style="margin:26px 0 8px;border:1px solid #d6e0ee;border-radius:14px;padding:22px 22px;background:#EDF1F8">'
                '<div style="font-size:12px;font-weight:800;letter-spacing:.04em;color:#1E3A5F;margin-bottom:7px">솔루션 패키지</div>'
                '<h3 style="font-size:18px;font-weight:700;color:#1E3A5F;margin:0 0 8px;line-height:1.4">이 셋업 구성 그대로 견적·솔루션 문의</h3>'
                '<p style="font-size:14px;color:#3a4650;line-height:1.75;margin:0 0 14px">위에 정리한 장비·모듈 구성을 기준으로 견적과 통합 셋업(구성·제어·연동·설치)을 안내해 드립니다. 다른 브랜드·조건도 함께 맞춰 드립니다.</p>'
                '<a href="/contact/?setup=' + quote(title) + '#general" style="display:inline-block;background:#1E3A5F;color:#fff;font-weight:800;font-size:14px;padding:11px 20px;border-radius:9px;text-decoration:none">이 셋업으로 문의하기 &rarr;</a>'
                '</section>'
            )
            if START in html:
                html2, ok = _inject_between(html, START, END, block)
            else:
                idx = html.rfind('</article>')
                html2 = html[:idx] + START + block + END + html[idx:]
                ok = True
            if ok and html2 != html:
                write(p, html2)
                count += 1
    print(f'  셋업 CTA 주입: {count}개 페이지')


def inject_static_nav():
    """모든 콘텐츠 페이지의 #pumplab-footer div에 정적 링크 nav 주입(크롤러 가시화, 마커 기반 idempotent).
    리다이렉트 페이지(meta refresh)는 건드리지 않음."""
    nav = _crawler_nav_html()
    START, END = '<!--CNAV_START-->', '<!--CNAV_END-->'
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if set(dirpath.split(os.sep)) & {'_build', '_to_delete'}:
            continue
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            html = read(p)
            if 'http-equiv="refresh"' in html:
                continue  # 리다이렉트 스텁은 제외
            if START in html:
                html2, ok = _inject_between(html, START, END, nav)
            elif '<div id="pumplab-footer"></div>' in html:
                html2 = html.replace('<div id="pumplab-footer"></div>',
                                     '<div id="pumplab-footer">' + START + nav + END + '</div>')
                ok = True
            else:
                continue
            if ok and html2 != html:
                write(p, html2)
                count += 1
    print(f'  정적 크롤러 nav 주입: {count}개 페이지')


SETUP_SECTIONS = [
    ('ENERGY', {'co2-capture-ct3001f', 'alicat-mfc-tubefurnace', 'leadfluid-bt101l-plating'}),
    ('ENV',    {'damo-recirculation-bt600s', 'nitrification-ph-bq50s'}),
]

def _setup_slug(url):
    return url.rstrip('/').split('/')[-1].replace('.html', '')

def _setup_card(p):
    tags = (p.get('tags') or [])[:2]
    cat = ' '.join('#' + t for t in tags)
    return (
        f'<a class="st-row" href="{escape(p.get("url",""))}">'
        f'<div class="st-badge">{escape(p.get("journal",""))}</div>'
        f'<div class="st-bd">'
        f'<div class="st-cat">{escape(cat)}</div>'
        f'<div class="st-t">{escape(p.get("title",""))}</div>'
        f'<div class="st-sum">셋업 — <b>{escape(p.get("model_focus",""))}</b> · {escape(p.get("summary",""))}</div>'
        f'<div class="st-date">{escape(p.get("date",""))} · {escape(p.get("journal",""))}</div>'
        f'</div></a>'
    )

def build_rss():
    """_build/posts.json → feed.xml(RSS 2.0) 생성. 매거진 구독·AI 애그리게이터용.
    최신순, 최대 30편. 콘텐츠(magazine·setup·guide) 포함."""
    from datetime import datetime, timezone, timedelta
    posts_path = os.path.join(SCRIPT_DIR, 'posts.json')
    if not os.path.exists(posts_path):
        print('  [skip] rss: posts.json 없음')
        return
    with open(posts_path, 'r', encoding='utf-8') as f:
        posts = [p for p in json.load(f).get('posts', []) if p.get('url') and not p.get('noindex')]
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    posts = posts[:30]
    KST = timezone(timedelta(hours=9))

    def rfc822(d):
        try:
            return datetime.strptime(d, '%Y-%m-%d').replace(hour=9, tzinfo=KST).strftime('%a, %d %b %Y %H:%M:%S %z')
        except Exception:
            return datetime.now(KST).strftime('%a, %d %b %Y %H:%M:%S %z')

    now822 = datetime.now(KST).strftime('%a, %d %b %Y %H:%M:%S %z')
    items = []
    for p in posts:
        link = BASE_URL_LD + p['url'].rstrip('.html') if p['url'].endswith('.html') else BASE_URL_LD + p['url']
        desc = p.get('summary', '')
        cats = ''.join(f'<category>{escape(t)}</category>' for t in (p.get('tags') or [])[:5])
        items.append(
            '    <item>\n'
            f'      <title>{escape(p.get("title",""))}</title>\n'
            f'      <link>{escape(link)}</link>\n'
            f'      <guid isPermaLink="true">{escape(link)}</guid>\n'
            f'      <pubDate>{rfc822(p.get("date",""))}</pubDate>\n'
            f'      <description><![CDATA[{desc}]]></description>\n'
            f'      {cats}\n'
            '    </item>'
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>실험셋업연구소 — 실험 셋업 매거진</title>\n'
        f'    <link>{BASE_URL_LD}/magazine/</link>\n'
        '    <atom:link href="' + BASE_URL_LD + '/feed.xml" rel="self" type="application/rss+xml"/>\n'
        '    <description>논문이 실제로 쓴 실험 셋업을 공정·조건·필요 장비 순으로 분석해 공유하는 실험 셋업 매거진.</description>\n'
        '    <language>ko</language>\n'
        f'    <lastBuildDate>{now822}</lastBuildDate>\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>\n'
    )
    write(os.path.join(ROOT_DIR, 'feed.xml'), rss)
    print(f'  feed.xml: RSS {len(posts)}편 생성')


def build_home_paper_cases():
    """_build/paper_cases.json → index.html '논문 사례' 섹션을 정적 렌더(GEO: raw HTML, SSOT).
    process=공정 변수(2키워드)는 데이터에서만 관리. 마커 <!--PAPERCASES_START/END--> 사이 교체."""
    data_path = os.path.join(SCRIPT_DIR, 'paper_cases.json')
    html_path = os.path.join(ROOT_DIR, 'index.html')
    if not os.path.exists(data_path) or not os.path.exists(html_path):
        print('  [skip] paper_cases.json 또는 index.html 없음')
        return
    with open(data_path, 'r', encoding='utf-8') as f:
        groups = json.load(f).get('groups', [])

    # 그룹 구분 없이 하나의 뉴스 매거진 모자이크로 — heat/fluid를 교차 배치
    lists = [list(g.get('cards', [])) for g in groups]
    fls = [bool(g.get('fl')) for g in groups]
    merged = []
    depth = max((len(l) for l in lists), default=0)
    for i in range(depth):
        for li, l in enumerate(lists):
            if i < len(l):
                merged.append((l[i], fls[li]))

    # 좌측 사진 · 우측 제목·내용의 가로형 카드 리스트 (2열)
    parts = ['<div class="mag-list" id="magMosaic">']
    total_cards = 0
    for c, fl in merged:
        flc = ' fl' if fl else ''
        proc = [k for k in c.get('process', []) if k]
        chips = ''.join(f'<span class="mr-chip">{escape(k)}</span>' for k in proc)
        img = escape(c.get('img', ''))
        style = f' style="background-image:url(\'{img}\')"' if img else ''
        dproc = escape(c.get('proc', '')) if c.get('proc') else ''
        dattr = f' data-proc="{dproc}"' if dproc else ''
        parts.append(
            f'<a class="m-row{flc}" href="{escape(c.get("url",""))}"{dattr}>'
            f'<span class="mr-img"{style}></span>'
            f'<span class="mr-bd">'
            f'<span class="mr-chips">{chips}</span>'
            f'<h3>{escape(c.get("title",""))}</h3>'
            f'<p>{escape(c.get("desc",""))}</p>'
            f'<span class="mr-mt">{escape(c.get("meta",""))}</span>'
            f'</span></a>'
        )
        total_cards += 1
    parts.append('</div>')
    parts.append('<a class="mag-all" href="/magazine/">셋업 사례 전체 &rarr;</a>')
    section = '\n    '.join(parts)

    html = read(html_path)
    html, ok = _inject_between(html, '<!--PAPERCASES_START-->', '<!--PAPERCASES_END-->', section)
    if ok:
        write(html_path, html)
        print(f'  index.html: 논문 사례 {total_cards}개 카드 정적 렌더(paper_cases.json · 공정 변수)')
    else:
        print('  [warn] PAPERCASES 마커 못 찾음 — 주입 생략 (index.html 마커 확인)')


def build_setups():
    """_build/posts.json → setups/index.html을 연구 분야(바이오/환경/에너지)로 그룹 정적 렌더(크롤러 가시화, SSOT)."""
    posts_path = os.path.join(SCRIPT_DIR, 'posts.json')
    html_path = os.path.join(ROOT_DIR, 'setups', 'index.html')
    if not os.path.exists(posts_path) or not os.path.exists(html_path):
        print('  [skip] setups: posts.json 또는 setups/index.html 없음')
        return
    with open(posts_path, 'r', encoding='utf-8') as f:
        posts = json.load(f).get('posts', [])
    setups = [p for p in posts if p.get('type') in ('setup', 'case')]
    setups.sort(key=lambda p: p.get('date', ''), reverse=True)
    papers = [p for p in setups if p.get('type') == 'setup']

    html = read(html_path)
    total_ok = True
    for const, slugs in SETUP_SECTIONS:
        group = [p for p in setups if _setup_slug(p.get('url', '')) in slugs]
        cards_html = '\n'.join(_setup_card(p) for p in group) or '<div class="st-empty">준비 중입니다.</div>'
        html, ok = _inject_between(html, f'<!--SEC_{const}_START-->', f'<!--SEC_{const}_END-->', cards_html)
        total_ok = total_ok and ok

    count_html = f'셋업 <b>{len(setups)}</b> · 분야 {len(SETUP_SECTIONS)}'
    parts = ', '.join(f'{escape(p.get("model_focus",""))}({escape(p.get("summary",""))})' for p in papers)
    answer_html = (
        f'<b>에너지·재료·수처리 공정 셋업 {len(papers)}편을 공정 → 조건 → 필요 장비 순으로 정리했습니다.</b> '
        f'{parts} 등. 각 셋업의 논문·저널·펌프 모델·DOI를 아래에서 확인하세요.'
    )
    html, okc = _inject_between(html, '<!--ST_COUNT_START-->', '<!--ST_COUNT_END-->', count_html)
    html, oka = _inject_between(html, '<!--ST_ANSWER_START-->', '<!--ST_ANSWER_END-->', answer_html)
    html, _oks = _inject_between(html, '<!--ST_CARDS_START-->', '<!--ST_CARDS_END-->', '')

    if total_ok and okc and oka:
        write(html_path, html)
        print(f'  setups/index.html: {len(setups)}개 셋업 · 3개 연구 분야 그룹 정적 렌더')
    else:
        print('  [warn] setups 마커 못 찾음 — 주입 생략 (SEC_*/ST_COUNT/ST_ANSWER 마커 확인)')


BASE_URL_LD = 'https://rndsetup.com'

# NOTE(엔티티): sameAs는 실제 공식 프로필 URL 확보 시 각 노드에 추가할 것
#   Org: GBP(구글 지도 CID)·유튜브(@rndsetuplab)·링크드인(company/rndsetup)·위키데이터(Q140603002) 반영됨.
#        네이버 플레이스·나비엠알오 URL 확보 시 추가.
#   Brand(리드플루이드): leadfluid.com·위키데이터(Q140602893) 반영됨.
#   (가짜/추정 URL 금지: 확인된 것만 넣는다)
ORG_WEBSITE_GRAPH = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": "https://rndsetup.com/#org",
            "name": "실험셋업연구소",
            "alternateName": ["정량펌프연구소", "rndsetup", "이머전트", "Emergent", "emergent co."],
            "legalName": "이머전트",
            "taxID": "328-03-02926",
            "url": "https://rndsetup.com/",
            "email": "info@rndsetup.com",
            "telephone": "+82-70-8983-2600",
            "founder": {"@type": "Person", "name": "이영현"},
            "sameAs": ["https://www.google.com/maps?cid=4429951187161412134", "https://www.youtube.com/@rndsetuplab", "https://www.linkedin.com/company/rndsetup/", "https://www.wikidata.org/wiki/Q140603002"],
            "slogan": "셋업으로 읽는 에너지·소재 공정 매거진",
            "description": "논문과 현장이 실제로 쓴 에너지·소재 공정 셋업을 공정 → 조건 → 필요 장비 순으로 분석해 공유하는 매거진. 소성·증착(퍼니스)·가스 분위기·유량 제어와 유체·펌프 조건을 셋업 단위로 정리하고, 배터리 소재 R&D·파일럿 라인 등 제조사가 완제품으로 다루지 않는 통합·특수 셋업은 직접 설계·공급한다. 매거진에서 다룬 장비는 정가 대비 3% 상시 할인가로 안내하며, 구매·수리·국내 A/S(구매 시 3년 무상보증)는 실험 장비 수리 전문 업체 이머전트(Emergent co)가 맡는다. 리드플루이드(LeadFluid)·삼흥에너지(SH Scientific)·Alicat 질량유량계(MFC) 등을 정품으로 안내한다.",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "부산광역시",
                "addressCountry": "KR"
            },
            "areaServed": {"@type": "Country", "name": "대한민국"},
            "knowsAbout": ["실험 장비 시스템 통합", "실험 기기 통합 제어", "온도 제어", "진공 제어", "유량 제어", "측정 기기 연동", "Modbus·RS-485 통합 제어", "실험실 정량펌프", "연동펌프(페리스탈틱 펌프)", "시린지펌프", "기어펌프", "마그네틱 펌프", "질량유량계(MFC)", "질량유량계 다기체 보정", "sccm·slm 가스 유량 제어", "압력 컨트롤러", "배압 레귤레이터(BPR)", "관류배양", "연속배양(chemostat)", "flow chemistry 연속흐름 반응", "열처리로(전기로·튜브퍼니스)", "튜브퍼니스(관상로)", "머플로(박스형 전기로)", "진공 전기로", "회전 튜브로(로터리 킬른)", "엘리베이터 전기로", "3존 튜브퍼니스", "소성(firing)", "하소(calcination)", "소결(sintering)", "어닐링(소둔)", "가스 분위기 제어", "산소 분압(pO2) 제어", "동적 분위기 제어(DCA)", "CVD 탄소 코팅", "열산화", "배터리 양극재 전구체 공침", "전해액 순환", "수전해·전기화학 셋업", "리드플루이드(LeadFluid) 펌프", "리드플루이드 펌프 국내 직접 A/S", "Alicat 질량유량계", "삼흥에너지(SH Scientific) 튜브퍼니스·전기로", "실험 셋업 정보"],
            "contactPoint": {"@type": "ContactPoint", "telephone": "+82-70-8983-2600", "email": "info@rndsetup.com", "contactType": "customer support", "areaServed": "KR", "availableLanguage": "Korean"},
            "makesOffer": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "LeadFluid 정량·연동·시린지펌프 정품 안내·국내 A/S(이머전트)", "serviceType": "실험실 펌프 정품 안내 및 소프트웨어 제어", "brand": {"@type": "Brand", "name": "LeadFluid", "alternateName": "리드플루이드"}}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Alicat 질량유량계(MFC) 정품 안내·시스템 연동", "serviceType": "질량유량계 정품 안내 및 제어 연동", "brand": {"@type": "Brand", "name": "Alicat Scientific"}}}
            ]
        },
        {
            "@type": "WebSite",
            "@id": "https://rndsetup.com/#website",
            "name": "실험셋업연구소",
            "url": "https://rndsetup.com/",
            "publisher": {"@id": "https://rndsetup.com/#org"},
            "inLanguage": "ko"
        },
        {
            "@type": "Brand",
            "@id": "https://rndsetup.com/#leadfluid",
            "name": "리드플루이드",
            "alternateName": ["LeadFluid", "Lead Fluid", "리드플루이드"],
            "sameAs": ["https://www.leadfluid.com/", "https://www.leadfluid.com.cn/", "https://www.wikidata.org/wiki/Q140602893"]
        }
    ]
}

BREADCRUMB_SECTIONS = {
    'magazine': ('셋업 사례', '/magazine/'),
    'application': ('실험 가이드', '/application/'),
    'pumps': ('펌프 종류', '/pumps/'),
    'setups': ('셋업 사례', '/magazine/'),
    'requests': ('소프트웨어 제어', '/requests/'),
    'trust': ('믿고 도입할 때', '/trust/'),
    'contact': ('문의하기', '/contact/'),
    'gas': ('기체', '/gas/'),
    'alicat': ('ALICAT', '/brands/alicat/'),
    'sh-scientific': ('삼흥에너지', '/brands/sh-scientific/guide/'),
    'guide': ('실험 셋업 가이드', '/guide/'),
}

# /application/ 내 페이지 중 섹션을 다르게 잡을 것 (펌프 가이드 / 소프트웨어 제어)
PUMP_GUIDE_FILES = {'pump-selection.html', 'tube-selection.html'}
SW_GUIDE_FILES = {'pump-flow-schedule-ramp.html', 'multi-pump-sync-unattended.html', 'pump-run-log-csv-reproducibility.html', 'pump-pc-control-modbus-rs485.html'}


def _page_title_short(html):
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    if not m:
        return None
    t = m.group(1).strip()
    for sep in ('—', '|'):
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    return t or None


def _breadcrumb_ld(rel, html):
    rel = rel.replace(os.sep, '/')
    parts = rel.split('/')
    if rel == 'index.html':
        return None
    if len(parts) == 3 and parts[2] == 'index.html':
        # 클린 URL 글 페이지: <section>/<slug>/index.html (예: magazine/<slug>/)
        seg, fn = parts[0], parts[1] + '/'
    elif len(parts) == 2:
        seg, fn = parts[0], parts[1]
    else:
        return None
    if seg == 'application':
        if fn in PUMP_GUIDE_FILES:
            sec_name, sec_url = '펌프 종류', '/pumps/'
        elif fn in SW_GUIDE_FILES:
            sec_name, sec_url = '소프트웨어 제어', '/requests/'
        else:
            sec_name, sec_url = BREADCRUMB_SECTIONS['application']
    elif seg in BREADCRUMB_SECTIONS:
        sec_name, sec_url = BREADCRUMB_SECTIONS[seg]
    else:
        return None
    items = [
        {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE_URL_LD + "/"},
        {"@type": "ListItem", "position": 2, "name": sec_name, "item": BASE_URL_LD + sec_url},
    ]
    rel_url = '/' + (rel[:-len('index.html')] if rel.endswith('/index.html') else rel)
    if fn != 'index.html' and rel_url != sec_url:
        leaf = _page_title_short(html) or fn
        items.append({"@type": "ListItem", "position": 3, "name": leaf, "item": BASE_URL_LD + rel_url})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def inject_head_schema():
    """모든 색인 콘텐츠 페이지 <head>에 Organization/WebSite + 페이지별 BreadcrumbList JSON-LD 정적 주입(크롤러 가시화).
    리다이렉트(meta refresh)·noindex 페이지는 제외."""
    START, END = '<!--HEADLD_START-->', '<!--HEADLD_END-->'
    org_json = json.dumps(ORG_WEBSITE_GRAPH, ensure_ascii=False).replace('</', '<\\/')
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if set(dirpath.split(os.sep)) & {'_build', '_to_delete'}:
            continue
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            html = read(p)
            if 'http-equiv="refresh"' in html or 'noindex' in html:
                continue
            rel = os.path.relpath(p, ROOT_DIR)
            blocks = [org_json]
            bc = _breadcrumb_ld(rel, html)
            if bc:
                blocks.append(json.dumps(bc, ensure_ascii=False).replace('</', '<\\/'))
            payload = ''.join('<script type="application/ld+json">' + b + '</script>' for b in blocks)
            if START in html:
                html2, ok = _inject_between(html, START, END, payload)
            elif '</head>' in html:
                html2 = html.replace('</head>', START + payload + END + '</head>', 1)
                ok = True
            else:
                continue
            if ok and html2 != html:
                write(p, html2)
                count += 1
    print(f'  head JSON-LD(Org·WebSite·Breadcrumb) 주입: {count}개 페이지')


def normalize_html_urls():
    """Cloudflare Pages는 /x.html을 /x로 서빙하고 /x.html은 /x로 리다이렉트한다.
    내부 링크(href·src)·canonical·og·JSON-LD의 .html을 제거해 리다이렉트 홉을 없앤다.
    리다이렉트 스텁(meta refresh)은 제외(그 자체가 옛 .html URL을 처리)."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if set(dirpath.split(os.sep)) & {'_build', '_to_delete'}:
            continue
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            html = read(p)
            if 'http-equiv="refresh"' in html:
                continue
            new = re.sub(r'((?:href|src)=")(/[^"\s]*)\.html(?=["#?])', r'\1\2', html)
            new = re.sub(r'(https://rndsetup\.com/[^"\s]*)\.html(?=["#?])', r'\1', new)
            if new != html:
                write(p, new)
                count += 1
    print(f'  URL 정규화(.html 제거): {count}개 페이지')


def _redirect_sources():
    """_redirects의 소스 경로 집합 — 검색 인덱스·내부 배선에서 제외용."""
    path = os.path.join(ROOT_DIR, '_redirects')
    srcs = set()
    if os.path.exists(path):
        for line in read(path).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                srcs.add(parts[0].rstrip('/'))
    return srcs


def build_prices():
    """가격 SSOT: rndsetup_products.sql(정가)에서 카테고리별 최저가를 계산해
    index.html의 data-price="key" 스팬과 assets/site.js의 /*P:key*/'...' 마커에 주입.
    가격 개정 = SQL만 갱신하면 사이트 전체 반영."""
    sql_path = os.path.join(ROOT_DIR, 'rndsetup_products.sql')
    if not os.path.exists(sql_path):
        print('  [skip] rndsetup_products.sql 없음 — 가격 주입 생략')
        return
    t = read(sql_path)
    rows = []
    for line in t.splitlines():
        if not line.startswith('INSERT INTO products'):
            continue
        m = re.search(r"VALUES \('([^']*)',\d+,'[^']*','[^']*','[^']*','([^']*)','([^']*)','([^']*)'", line)
        p = re.search(r"'ea',(\d+),(\d+),", line)
        if m and p:
            rows.append({'sku': m.group(1), 'daebun': m.group(2), 'sobun': m.group(3),
                         'model': m.group(4), 'retail': int(p.group(2)), 'line': line})

    def min_by(pred, floor=0):
        vals = [r['retail'] for r in rows if r['retail'] > floor and pred(r)]
        return min(vals) if vals else None

    prices = {
        'muffle1050': min_by(lambda r: r['sobun'].startswith('ECO 1050')),
        'cvdpkg': min_by(lambda r: 'Gas Flow Package' in r['sobun'] and '1200' in r['sobun']),
        'tube1500': min_by(lambda r: '1500' in r['sobun'] and '튜브전기로' in r['sobun']),
        'muffle1500': min_by(lambda r: r['sobun'].replace(' ', '').startswith('1500℃전기로') and '진공' not in r['sobun']),
        'vacmuffle1200': min_by(lambda r: '1200' in r['sobun'] and '진공' in r['sobun'] and '석영' not in r['sobun']),
        'rotary': min_by(lambda r: '회전튜브' in r['sobun'].replace(' ', '')),
        'elevator1200': min_by(lambda r: '1200' in r['sobun'] and 'Elevator' in r['sobun']),
        'bt101s': min_by(lambda r: 'BT101S' in r['sku'], floor=800000),
        'bt300s': min_by(lambda r: 'BT300S' in r['sku'], floor=800000),
        'bt600s': min_by(lambda r: 'BT600S' in r['sku'], floor=800000),
        'ct3001': min_by(lambda r: 'CT3001' in r['sku'] or 'CT3001' in r['model'], floor=800000),
        'tyd01': min_by(lambda r: 'TYD01' in r['sku'], floor=800000),
        'pumplab': min_by(lambda r: r['sobun'] == '연동펌프', floor=800000),
    }

    # 정가 대비 3% 상시 할인 — 사이트 노출 가격은 모두 할인가 기준(만원 미만 버림)
    DISCOUNT_RATE = 0.97

    def fmt(v):
        sale = int(v * DISCOUNT_RATE)
        man = sale // 10000
        return f'{man:,}만 원'

    # index.html data-price 스팬 주입
    hp = os.path.join(ROOT_DIR, 'index.html')
    h = read(hp)
    n1 = 0
    for key, v in prices.items():
        if not v:
            continue
        pat = re.compile(r'(data-price="' + key + r'"[^>]*>)[^<]*(</span>)')
        h, c = pat.subn(lambda m: m.group(1) + fmt(v) + m.group(2), h)
        n1 += c
    write(hp, h)

    # site.js /*P:key*/'...' 마커 주입
    sp = os.path.join(ROOT_DIR, 'assets', 'site.js')
    s = read(sp)
    n2 = 0
    for key, v in prices.items():
        if not v:
            continue
        pat = re.compile(r"(/\*P:" + key + r"\*/)'[^']*'")
        s, c = pat.subn(lambda m: m.group(1) + f"'{fmt(v)}~'", s)
        n2 += c
    write(sp, s)
    print(f'  가격 SSOT 주입: index.html {n1}곳 · site.js {n2}곳 (SQL 최저 정가 기준)')


# 전 제품 통합 카탈로그 — brands/<brand>/index.html 의 dscard를 수집해 brands/index.html에 정적 주입.
# 갱신 1곳 원칙: 브랜드 허브에 카드를 추가하면 빌드만으로 통합 카탈로그에 자동 반영된다.
ALLPROD_BRANDS = [
    ('sh-scientific', '삼흥에너지', ''),
    ('leadfluid', '리드플루이드', 'pump'),
    ('alicat', 'Alicat', 'gas'),
    ('gaossunion', '가오스유니온', 'echem'),
]  # (슬러그, 표기명, 매핑 실패 시 기본 카테고리)
# 브랜드별 data-cat 어휘 → 통합 카테고리
ALLPROD_CATMAP = {
    'furnace': 'heat',
    'drying': 'dry', 'distill': 'dry',
    'incubator': 'culture', 'waterbath': 'culture', 'chamber': 'culture', 'sterilizer': 'culture',
    'mixing': 'mix',
    'vacuumpump': 'vacuum', 'vac': 'vacuum',
    'pump': 'pump', 'peri': 'pump', 'syr': 'pump', 'gear': 'pump', 'ex': 'pump', 'head': 'pump',
    'mfc': 'gas', 'std': 'gas', 'hp': 'gas', 'bio': 'gas', 'corr': 'gas', 'dual': 'gas', 'press': 'gas',
    'electrode': 'echem', 'catalyst': 'echem', 'material': 'echem', 'accessory': 'echem',
    'fumehood': 'safety', 'measuring': 'safety',
}


def build_all_products():
    """전 제품 통합 카탈로그 — 브랜드 허브 dscard에서 데이터만 추출해 표준 카드로 정규화 주입.
    카드 표준(고정): 대표사진 / 브랜드 / 제목 / 모델명 / 스펙3행 / 정가·할인가 / 키워드 해시태그 / 더보기."""
    START, END = '<!--ALLPROD_START-->', '<!--ALLPROD_END-->'
    target = os.path.join(ROOT_DIR, 'product', 'index.html')
    if not os.path.exists(target):
        return
    page = read(target)
    if START not in page:
        return

    def clean(s):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()

    def detail_of(href):
        p = os.path.join(ROOT_DIR, href.strip('/').replace('/', os.sep), 'index.html')
        return read(p) if os.path.isfile(p) else ''

    def get_price(detail):
        """상세페이지에서 최저 정가 추출 — JSON-LD offers.price 전부의 최솟값(옵션 다수 대응)."""
        vals = []
        for x in re.findall(r'"price"\s*:\s*"?([0-9][0-9,]{3,})"?', detail):
            try:
                v = int(x.replace(',', ''))
                if v >= 10000:
                    vals.append(v)
            except ValueError:
                pass
        if not vals:
            mm = re.search(r'정가\s*([0-9][0-9,]{3,})\s*원', detail)
            if mm:
                try:
                    v = int(mm.group(1).replace(',', ''))
                    if v >= 10000:
                        vals.append(v)
                except ValueError:
                    pass
        return min(vals) if vals else None
        try:
            v = int(m.group(1).replace(',', ''))
            return v if v >= 10000 else None
        except ValueError:
            return None

    # ── 제품군별 표준 스펙 스키마: (표준 라벨, [소스 키 부분일치 토큰]) × 3 ──
    # 같은 제품군이면 브랜드가 달라도 같은 라벨·같은 순서를 쓴다. 값이 없으면 '상세 참조'.
    SPEC_SCHEMA = {
        'furnace':    [('최고온도', ['최고온도', '온도']), ('튜브·챔버', ['튜브경', '튜브', '챔버', '크기']), ('발열체', ['발열체', '히터'])],
        'drying':     [('온도범위', ['온도']), ('내부크기', ['내부', '크기', '챔버']), ('용량·히터', ['용량', '히터'])],
        'distill':    [('용량', ['용량']), ('회전', ['회전']), ('진공·온도', ['진공', '온도'])],
        'incubator':  [('온도범위', ['온도']), ('내부·용량', ['용량', '내부', '크기']), ('CO₂·습도', ['CO', '습도', '센서'])],
        'waterbath':  [('온도범위', ['온도']), ('용량', ['용량']), ('안정도', ['안정', '균일', '냉각'])],
        'chamber':    [('온도범위', ['온도']), ('습도범위', ['습도']), ('내부크기', ['내부', '크기', '용량'])],
        'sterilizer': [('온도', ['온도']), ('용량·챔버', ['용량', '챔버']), ('방식', ['방식', '진공', '멸균', '제어'])],
        'mixing':     [('회전수', ['회전']), ('용량·용기', ['용량', '용기']), ('방식', ['방식', '분쇄', '믹서', '모터'])],
        'vacuumpump': [('도달압력', ['도달', '진공도']), ('배기속도', ['배기', '펌핑']), ('구성', ['플랜지', '모터', '소음', '오일'])],
        'fumehood':   [('크기', ['크기', '폭', '치수']), ('풍속', ['풍속', '배기']), ('구성', ['필터', '구성', '용도', '재질'])],
        'measuring':  [('측정범위', ['측정', '범위', '최대']), ('정밀도', ['정밀', '분해능', '정확']), ('구성', ['플랫폼', '팬', '크기', '표시'])],
        'peri':  [('유량', ['유량']), ('회전수', ['회전']), ('채널', ['채널'])],
        'syr':   [('유량', ['유량']), ('시린지', ['시린지']), ('채널', ['채널'])],
        'gear':  [('유량', ['유량']), ('압력', ['압력']), ('접액부', ['접액', '재질'])],
        'ex':    [('유량', ['유량']), ('회전수', ['회전']), ('방폭등급', ['방폭', '등급'])],
        'pump':  [('유량', ['유량']), ('회전수', ['회전']), ('채널', ['채널'])],
        'head':  [('적용 튜브', ['튜브']), ('유량', ['유량']), ('채널·롤러', ['채널', '롤러'])],
        'oem':   [('유량', ['유량']), ('크기', ['크기', '치수']), ('제어', ['제어', '통신'])],
        'mfc':   [('유량범위', ['유량']), ('가스', ['가스']), ('정확도·응답', ['정확', '응답'])],
        'std':   [('유량범위', ['유량']), ('가스', ['가스']), ('정확도·응답', ['정확', '응답'])],
        'hp':    [('유량범위', ['유량']), ('압력', ['압력']), ('가스', ['가스'])],
        'corr':  [('유량범위', ['유량']), ('가스', ['가스']), ('재질', ['재질', '내부식'])],
        'dual':  [('유량범위', ['유량']), ('가스', ['가스']), ('제어', ['제어', '방향'])],
        'press': [('압력범위', ['압력']), ('제어', ['제어', '방향']), ('통신', ['통신', 'RS'])],
        'vac':   [('압력범위', ['압력', '진공']), ('유량', ['유량']), ('용도', ['용도', '공정'])],
    }
    SPEC_LOWVALUE = ('중량', '무게', '전원', '전압', '소비전력', '외형', '외부', '포장', '인증', '옵션', '보증', '납기')

    def get_specs(block, detail, subcat=''):
        cand = []
        for k, v in re.findall(r'<span class="k">([\s\S]*?)</span>\s*<span class="v">([\s\S]*?)</span>', block):
            k, v = clean(k), clean(v)
            if k and v and len(k) <= 12:
                cand.append((k, v))
        tb = re.search(r'<table class="pkg-tbl">([\s\S]*?)</table>', detail)
        if tb:
            for th, td in re.findall(r'<th[^>]*>([\s\S]*?)</th>\s*<td[^>]*>([\s\S]*?)</td>', tb.group(1)):
                k, v = clean(th), clean(td)
                if not k or not v or len(k) > 12 or any(h in k for h in ('사양', '품목', '정가', '모델명')):
                    continue
                if all(k != ek for ek, _ in cand):
                    cand.append((k, v))
        schema = SPEC_SCHEMA.get(subcat)
        if schema and cand:
            rows, used = [], set()
            for lab, toks in schema[:3]:
                val = None
                for k, v in cand:
                    if k in used:
                        continue
                    if any(tk.lower() in k.lower() for tk in toks):
                        val = v; used.add(k); break
                rows.append((lab, val if val else '상세 참조'))
            return rows
        # 스키마 없는 군: 저가치 제외 상위 3
        rows = []
        for k, v in cand:
            if len(rows) >= 3:
                break
            if any(lv in k for lv in SPEC_LOWVALUE):
                continue
            rows.append((k, v))
        for k, v in cand:
            if len(rows) >= 3:
                break
            if all(k != rk for rk, _ in rows):
                rows.append((k, v))
        # 옵션형(가오스유니온): 구성 옵션 수 + 대표 모델 — 이 군의 표준 라벨
        if len(rows) < 3:
            opts = re.findall(r'<tr>\s*<t[hd][^>]*>([\s\S]*?)</t[hd]>\s*<td[^>]*>([\s\S]*?)</td>', detail)
            opts = [(clean(a), clean(b)) for a, b in opts]
            opts = [(a, b) for a, b in opts if a and b and len(a) <= 14 and not any(h in a for h in ('사양', '품목', '정가', '모델'))]
            if opts:
                rows = [('구성 옵션', f'{len(opts)}종')]
                for a, b in opts:
                    if len(rows) >= 3:
                        break
                    rows.append(('대표 모델', b))
        # 그룹 표준 라벨로 3행 패딩 (군 내 라벨 통일 보장)
        if len(rows) < 3:
            schema2 = SPEC_SCHEMA.get(subcat)
            if schema2:
                have = {rk for rk, _ in rows}
                for lab, _tk in schema2[:3]:
                    if len(rows) >= 3:
                        break
                    if lab not in have:
                        rows.append((lab, '상세 참조'))
            elif subcat in ('electrode', 'catalyst', 'material', 'accessory'):
                pads = [('구성 옵션', '상세 참조'), ('대표 모델', '상세 참조'), ('대표 모델', '상세 참조')]
                for p in pads[len(rows):3]:
                    rows.append(p)
        return rows

    KW_STOP = {'및', '또는', '기타', 'the', 'and', 'for', 'with', 'series', 'type'}
    # 제품군별 GEO 연관검색어 사전 — 실제 검색 어휘(동의어·연관어) 우선 노출
    KW_BY_SUBCAT = {
        'furnace':    ['튜브퍼니스', '전기로', '소성로', '열처리로', '관상로', '하소', '소결'],
        'drying':     ['건조기', '열풍건조기', '드라이오븐', '실험실 오븐', '건조 챔버'],
        'distill':    ['회전증발농축기', '로터리 evaporator', '감압농축', '증류'],
        'incubator':  ['인큐베이터', '배양기', 'CO2 배양기', '세포배양', '진탕배양기'],
        'waterbath':  ['항온수조', '워터배스', '칠러', '순환수조'],
        'chamber':    ['항온항습기', '환경챔버', '신뢰성시험', '온습도 챔버'],
        'sterilizer': ['오토클레이브', '멸균기', '고압증기멸균', '실험실 멸균'],
        'mixing':     ['교반기', '믹서', '볼밀', '분쇄기', '호모게나이저'],
        'vacuumpump': ['진공펌프', '로터리 펌프', '다이어프램 펌프', '진공도', '실험실 진공'],
        'fumehood':   ['흄후드', '클린벤치', '무균작업대', '실험실 안전'],
        'measuring':  ['전자저울', '수분측정기', '측정기기', '정밀저울'],
        'peri':  ['연동펌프', '페리스탈틱펌프', '정량펌프', '튜빙펌프', '실험실 펌프'],
        'syr':   ['시린지펌프', '미량주입', '정량주입', '실험실 펌프'],
        'gear':  ['기어펌프', '정량이송', '무맥동 펌프', '실험실 펌프'],
        'ex':    ['방폭펌프', '연동펌프', '방폭 인증', '정량펌프'],
        'head':  ['펌프헤드', '연동펌프 헤드', '튜브 카세트'],
        'oem':   ['OEM 펌프', '펌프 모듈', '장비 내장 펌프'],
        'mfc':   ['질량유량계', 'MFC', '유량컨트롤러', '가스 유량 제어', 'sccm'],
        'std':   ['질량유량계', 'MFC', '유량컨트롤러', '가스 유량 제어', 'sccm'],
        'hp':    ['고압 MFC', '질량유량계', '가스 유량 제어'],
        'corr':  ['내부식 MFC', '부식성 가스', '질량유량계'],
        'dual':  ['양방향 MFC', '질량유량계', '유량 제어'],
        'press': ['압력 컨트롤러', '배압 레귤레이터', 'BPR', '압력 제어'],
        'vac':   ['진공 공정', '질량유량계', '반도체 공정 가스'],
        'electrode': ['전기화학', '기준전극', '수전해', '전극', '전기화학 셀'],
        'catalyst':  ['CO2 환원', 'CO2RR', '전기화학 촉매', 'GDE'],
        'material':  ['전기화학 재료', '이온교환막', '카본페이퍼', '수전해'],
        'accessory': ['전극 홀더', '전극 연마', '전기화학 소모품'],
    }

    def get_keywords(block, title, subcat, cat_label):
        out, seen = [], set()
        def push(w):
            wl = w.lower()
            if wl in seen or len(out) >= 7:
                return
            seen.add(wl); out.append(w)
        # 1) 제품군 연관검색어 사전
        for w in KW_BY_SUBCAT.get(subcat, []):
            push(w)
        if cat_label:
            push(cat_label)
        # 2) 카드 데이터 토큰 (한글·의미 있는 영문 단어)
        toks = []
        for attr in ('data-use', 'data-text'):
            mm = re.search(attr + r'="([^"]*)"', block)
            if mm:
                toks += mm.group(1).split()
        for w in toks:
            if len(out) >= 7:
                break
            w = w.strip('·,()[]/#').strip()
            if not (2 <= len(w) <= 14) or w.lower() in KW_STOP:
                continue
            if re.search(r'\d', w):
                continue  # 숫자 포함(모델코드·치수) 제외
            if not re.search(r'[가-힣]', w) and not re.fullmatch(r'[A-Za-z][A-Za-z\- ]{2,13}', w):
                continue
            push(w)
        return out

    CAT_LABEL = {'heat': '열처리', 'dry': '건조·농축', 'culture': '배양·항온', 'mix': '교반·분쇄',
                 'vacuum': '진공', 'pump': '펌프', 'gas': '가스유량 MFC', 'echem': '전기화학', 'safety': '안전·측정'}

    cards = []
    for slug, label, default_cat in ALLPROD_BRANDS:
        hub = os.path.join(ROOT_DIR, 'brands', slug, 'index.html')
        if not os.path.exists(hub):
            continue
        h = read(hub)
        for m in re.finditer(r'<article class="dscard"(.*?)</article>', h, re.S):
            block = m.group(1)
            a = re.search(r'<a class="dscard-link" href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
            if not a:
                continue
            href = a.group(1)
            title = clean(a.group(2))
            img = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', block)
            src = img.group(1) if img else ''
            alt = img.group(2) if img else title
            kw_raw = re.search(r'data-text="([^"]*)"', block)
            nm = re.search(r'<div class="dscard-nm">([\s\S]*?)</div>', block)
            model = clean(nm.group(1)) if nm else ''
            # 모델명 줄의 가격·요약 표기 정리 (예: "200℃ · 864~3,612L · 정가 11,400,000~25,700,000원")
            _nm_price = re.search(r'정가\s*([0-9][0-9,]{3,})', model)
            model = re.sub(r'\s*·?\s*정가[\s0-9,~원]+', '', model).strip(' ·')
            if not model:
                _code = re.search(r'\b(sh-[a-z0-9][a-z0-9\-~/]+)\b', (kw_raw.group(1) if kw_raw else '').lower())
                model = _code.group(1).upper() if _code else ''

            cat_raw = re.search(r'data-cat="([^"]*)"', block)
            cat = default_cat
            if cat_raw:
                for tok in cat_raw.group(1).split():
                    if tok in ALLPROD_CATMAP:
                        cat = ALLPROD_CATMAP[tok]
                        break
            sub_tokens = []
            if cat_raw:
                sub_tokens += cat_raw.group(1).split()
            for attr, prefix in (('tier', 'tier:'), ('type', 'ty:')):
                mm = re.search(r'data-%s="([^"]*)"' % attr, block)
                if mm and mm.group(1).strip():
                    sub_tokens.append(prefix + mm.group(1).strip())
            for attr in ('f2', 'flow', 'proc'):
                mm = re.search(r'data-%s="([^"]*)"' % attr, block)
                if mm:
                    sub_tokens += mm.group(1).split()
            if slug == 'gaossunion':
                seg = [x for x in href.strip('/').split('/') if x]
                if len(seg) >= 3:
                    sub_tokens.append('gu:' + seg[2])
            keys = ' '.join([title, model, label, slug, kw_raw.group(1) if kw_raw else '']).lower()

            detail = detail_of(href)
            _sub1 = (cat_raw.group(1).split()[0] if cat_raw and cat_raw.group(1).split() else '')
            specs = get_specs(block, detail, _sub1 or cat)
            price = get_price(detail)
            if price is None and _nm_price:
                try:
                    _v = int(_nm_price.group(1).replace(',', ''))
                    if _v >= 10000:
                        price = _v
                except ValueError:
                    pass
            kws = get_keywords(block, title, _sub1 or cat, CAT_LABEL.get(cat, ''))
            if not model:
                _rep = next((v for k, v in specs if k == '대표 모델'), '')
                model = _rep or '옵션 구성 · 상세 참조'

            sp_html = ''.join(
                f'<div class="r"><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></div>'
                for k, v in (specs + [('사양', '상세 참조')] * 3)[:3])
            if price:
                sale = int(price * 0.97) // 10000 * 10000
                pr_html = (f'<div class="pc-pr"><span class="o">정가 {{:,}}원~</span>'
                           f'<span class="s">최소 {{:,}}원부터 <em>3%↓</em> <i class="vat">VAT 별도</i></span></div>').format(price, sale)
            else:
                pr_html = '<div class="pc-pr"><span class="q">가격 견적 문의 <i class="vat">VAT 별도</i></span></div>'
            kw_html = ('<div class="pc-kw">' + ' '.join('#' + escape(w) for w in kws) + '</div>') if kws else '<div class="pc-kw"></div>'

            cards.append(
                f'<article class="ap-card pcard" data-b="{slug}" data-c="{cat}"'
                f' data-s="{escape(" ".join(dict.fromkeys(sub_tokens)), quote=True)}" data-k="{escape(keys, quote=True)}">'
                f'<a class="pc-im" href="{href}" aria-label="{escape(title, quote=True)}">'
                f'<img src="{src}" alt="{escape(alt, quote=True)}" loading="lazy" width="760" height="570"></a>'
                f'<div class="pc-bd">'
                f'<div class="pc-br">{escape(label)}</div>'
                f'<h3 class="pc-t"><a href="{href}">{escape(title)}</a></h3>'
                f'<div class="pc-nm">{escape(model)}</div>'
                f'<div class="pc-sp">{sp_html}</div>'
                f'{pr_html}'
                f'{kw_html}'
                f'<a class="pc-more" href="{href}">더보기 →</a>'
                f'</div></article>'
            )
    payload = ''.join(cards)
    page2, ok = _inject_between(page, START, END, payload)
    if ok:
        write(target, page2)
        print(f'  전 제품 통합 카탈로그: {{}}개 표준 카드 주입 (product/index.html)'.format(len(cards)))

def build_new_research():
    """홈 '최신연구' 레일 — posts.json 최신 6편 자동 렌더 (수동 HTML 유지보수 제거)."""
    posts_path = os.path.join(SCRIPT_DIR, 'posts.json')
    hp = os.path.join(ROOT_DIR, 'index.html')
    if not os.path.exists(posts_path) or not os.path.exists(hp):
        return
    posts = json.load(open(posts_path, encoding='utf-8')).get('posts', [])
    posts = sorted(posts, key=lambda p: p.get('date', ''), reverse=True)[:6]
    TYPE_LABEL = {'magazine': '논문 셋업', 'setup': '논문 셋업', 'blog': '블로그'}
    cards = []
    for p in posts:
        badge = TYPE_LABEL.get(p.get('type', ''), '글')
        title = p.get('title', '')
        # 제목에 유형 힌트가 있으면 유지
        if '가이드' in title:
            badge = '가이드'
        elif '용어사전' in title:
            badge = '용어사전'
        img = p.get('image') or '/img/product/sh/tube-1500.jpg'
        sub = ' · '.join(x for x in (p.get('journal', ''), p.get('model_focus', '')) if x)[:46]
        cards.append(
            f'<a class="prod-card nc" href="{escape(p.get("url",""))}">'
            f'<div class="pimg" style="background-image:url(\'{escape(img)}\')"></div>'
            f'<div class="pbd"><div class="ps">{escape(badge)}{(" · " + escape(p.get("journal",""))) if p.get("journal") else ""}</div>'
            f'<div class="pn">{escape(title)}</div>'
            f'<div class="nd">{escape(p.get("date",""))}{(" · " + escape(p.get("model_focus",""))) if p.get("model_focus") else ""}</div></div></a>'
        )
    h = read(hp)
    h, ok = _inject_between(h, '<!--NEWRESEARCH_START-->', '<!--NEWRESEARCH_END-->', '\n        '.join(cards))
    if ok:
        write(hp, h)
        print(f'  최신연구 레일: posts.json 최신 {len(cards)}편 자동 렌더')
    else:
        print('  [warn] NEWRESEARCH 마커 못 찾음')


def build_search_index():
    """전 페이지를 스캔해 사이트 검색 인덱스(/search-index.json)를 생성.
    site.js가 fetch해 수동 SEARCH_INDEX와 병합한다. 새 페이지는 빌드만 하면 검색에 잡힘."""
    SKIP_DIRS = {'_build', '_to_delete', '.git', 'admin', 'api', 'functions', 'node_modules'}
    redirected = _redirect_sources()
    entries = []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT_DIR).replace('\\', '/')
            if rel in ('404.html', 'inquiry.html', 'recommend.html') or rel.startswith('_'):
                continue
            _u = ('/' + rel).replace('/index.html', '').replace('.html', '')
            if _u.rstrip('/') in redirected or (_u + '/').rstrip('/') in redirected:
                continue  # 301 처리된 URL은 검색 인덱스에서 제외
            url = '/' + rel
            if url.endswith('/index.html'):
                url = url[:-10]
            elif url.endswith('.html'):
                url = url[:-5]
            try:
                t = read(path)
            except Exception:
                continue
            def _m(pat):
                m = re.search(pat, t, re.S)
                return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
            title = _m(r'<title>(.*?)</title>')
            if not title:
                continue
            title = title.split('|')[0].strip()
            desc = _m(r'<meta name="description" content="([^"]*)"')
            kw = _m(r'<meta name="keywords" content="([^"]*)"')
            h1 = re.sub(r'<[^>]+>', ' ', _m(r'<h1[^>]*>(.*?)</h1>'))
            # 카테고리 라벨
            if url.startswith('/brands/sh-scientific/'):
                cat = '삼흥 장비'
            elif url.startswith('/brands/leadfluid/'):
                cat = '리드플루이드 펌프'
            elif url.startswith('/brands/alicat'):
                cat = 'Alicat MFC'
            elif url.startswith('/brands'):
                cat = '장비 카탈로그'
            elif url.startswith('/magazine/battery'):
                cat = '배터리 랩 A to Z'
            elif url.startswith('/magazine'):
                cat = '매거진'
            elif url.startswith('/setups') or url.startswith('/furnace/setups') or url.startswith('/pump/setups'):
                cat = '셋업 사례'
            elif url.startswith('/pump/atoz'):
                cat = '펌프 문제해결'
            elif url.startswith('/manuals') or url.startswith('/temp-controller'):
                cat = '메뉴얼'
            elif url.startswith('/application'):
                cat = '실험 가이드'
            elif url.startswith('/pumps') or url.startswith('/pump'):
                cat = '펌프'
            else:
                cat = '페이지'
            k = ' '.join(x for x in (h1, desc, kw) if x)[:400]
            entries.append({'t': title[:90], 'u': url, 'k': k, 'c': cat})
    entries.sort(key=lambda e: e['u'])
    write(os.path.join(ROOT_DIR, 'search-index.json'),
          json.dumps({'v': 1, 'items': entries}, ensure_ascii=False))
    print(f'  search-index.json: {len(entries)}개 페이지 인덱싱')


def main():
    print('=' * 60)
    print('  실험셋업연구소 카테고리 페이지 빌드')
    print('=' * 60)

    template = read(os.path.join(SCRIPT_DIR, 'template.html'))
    partial_tubing = read(os.path.join(SCRIPT_DIR, 'partial_tubing.html'))
    partial_preparing = read(os.path.join(SCRIPT_DIR, 'partial_preparing.html'))

    with open(os.path.join(SCRIPT_DIR, 'categories.json'), 'r', encoding='utf-8') as f:
        cats_config = json.load(f)

    # products.json (통합) 또는 fallback pumps.json (구버전)
    products = []
    spec_labels = {}
    products_path = os.path.join(SCRIPT_DIR, 'products.json')
    pumps_path = os.path.join(SCRIPT_DIR, 'pumps.json')
    if os.path.exists(products_path):
        with open(products_path, 'r', encoding='utf-8') as f:
            pdata = json.load(f)
        products = pdata.get('products', [])
        spec_labels = pdata.get('_spec_labels', {})
        print(f'  products.json: {len(products)}개 제품')
    elif os.path.exists(pumps_path):
        with open(pumps_path, 'r', encoding='utf-8') as f:
            pdata = json.load(f)
        for p in pdata.get('pumps', []):
            p2 = dict(p)
            p2['category'] = 'pump'
            # 옛 필드명 → spec1~4
            p2['spec1'] = p.get('series', '')
            p2['spec2'] = p.get('flow', '')
            p2['spec3'] = p.get('heads', '')
            p2['spec4'] = p.get('control', '')
            products.append(p2)
        spec_labels = {'pump': ['시리즈','유량','헤드','제어']}
        print(f'  pumps.json (legacy): {len(products)}개 펌프 (products.json으로 마이그레이션 권장)')

    # 카테고리별 그룹화
    products_by_cat = {}
    for p in products:
        cat = p.get('category', 'pump')
        products_by_cat.setdefault(cat, []).append(p)

    base_url = cats_config.get('_base_url', 'https://rndsetup.com/')
    cats = cats_config['categories']
    partials_full = {'tubing': partial_tubing}

    print(f'\n카테고리 {len(cats)}개:\n')
    for cat_id, n in [(c, len(products_by_cat.get(c, []))) for c in cats]:
        print(f'  {cat_id}: {n}개 제품')
    print()

    written = []
    for cat_id, cat_data in cats.items():
        partial_full = partials_full.get(cat_id, partial_tubing)
        html = render_page(cat_id, cat_data, template, partial_full, partial_preparing,
                          base_url, products_by_cat, spec_labels)
        out_path = os.path.join(ROOT_DIR, f'{cat_id}.html')
        write(out_path, html)
        size_kb = len(html.encode('utf-8')) / 1024
        kind = '전체 카탈로그' if cat_data['content'] == 'full' else '준비중'
        n_prod = len(products_by_cat.get(cat_id, []))
        print(f'  [{cat_id:<10}] {cat_id}.html  ({size_kb:5.1f} KB · {kind} · {n_prod}개)')
        written.append(cat_id)

    # sitemap.xml 생성 — 상업 funnel(공급) 페이지 우선 + 논문 리뷰 블로그
    # posts.json에서 블로그 글 자동 합산(단, noindex=true 글은 제외). deprecated 카테고리도 제외.
    from datetime import datetime
    build_date = datetime.now().strftime('%Y-%m-%d')
    sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # 메인 + 상업 funnel 페이지 (loc 경로, priority, changefreq)
    static_pages = [
        ('',              '1.0', 'weekly'),   # 홈
        ('magazine/',     '0.9', 'weekly'),   # 실험 셋업 매거진 허브
        ('magazine/battery/',        '0.9', 'weekly'),   # 배터리 랩 A to Z 커리큘럼 허브
        ('magazine/deposition/',     '0.8', 'monthly'),  # 증착 허브
        ('magazine/heat-treatment/', '0.8', 'monthly'),  # 열처리 허브
        ('magazine/oxidation/',      '0.8', 'monthly'),  # 산화·확산 허브
        ('manuals/',      '0.6', 'monthly'),  # 메뉴얼 모음 허브
        ('manuals/furnace/', '0.6', 'monthly'),  # 퍼니스·온도컨트롤러 메뉴얼
        ('manuals/furnace-mg/', '0.6', 'monthly'),  # 칸탈 머플전기로(MG·MGE) 메뉴얼
        ('manuals/mfc/',     '0.6', 'monthly'),  # MFC 메뉴얼
        ('manuals/pump/',    '0.6', 'monthly'),  # 펌프 메뉴얼
        ('product/',      '0.8', 'weekly'),   # 제품 통합 카탈로그 허브
        ('brands/leadfluid/manuals/',    '0.6', 'monthly'),  # 모델별 사용 메뉴얼 목록
        ('compare/imported-peristaltic-alternative/', '0.7', 'monthly'),  # 갈아타기 비교
        ('requests/',     '0.6', 'weekly'),   # 소프트웨어(개발 요청)
        ('contact/',      '0.8', 'monthly'),  # 문의하기
        ('trust/',        '0.8', 'monthly'),  # 믿고 도입할 때 (신뢰·A/S)
        ('about/',        '0.8', 'monthly'),  # 회사소개 (엔티티 앵커)
        ('pump/setups/plating-flow-calibration/', '0.8', 'monthly'),  # 도입 스토리 (도금 유량 보정)
        ('furnace/setups/', '0.8', 'monthly'),  # 퍼니스 셋업 사례 허브
        ('furnace/setups/alicat-mfc-tubefurnace/', '0.7', 'monthly'),  # 도입 스토리 (튜브퍼니스 MFC)
        ('brands/leadfluid/blog/', '0.8', 'weekly'),
        ('pump/atoz/', '0.8', 'weekly'),
        ('magazine/pump-selection-wizard/', '0.7', 'monthly'),   # 펌프·튜브 선택 위저드   # 트러블슈팅 허브
        ('brands/leadfluid/','0.9', 'weekly'),
        ('brands/leadfluid/pump-heads/','0.8', 'monthly'),
        ('brands/leadfluid/bq80s/','0.8', 'monthly'),
        ('brands/leadfluid/bt100f/','0.8', 'monthly'),
        ('brands/leadfluid/bt100f-1/','0.8', 'monthly'),
        ('brands/leadfluid/bt100l/','0.8', 'monthly'),
        ('brands/leadfluid/bt100s/','0.8', 'monthly'),
        ('brands/leadfluid/bt100s-1/','0.8', 'monthly'),
        ('brands/leadfluid/bt101f/','0.8', 'monthly'),
        ('brands/leadfluid/bt101l/','0.8', 'monthly'),
        ('brands/leadfluid/bt101s/','0.8', 'monthly'),
        ('brands/leadfluid/bt103s/','0.8', 'monthly'),
        ('brands/leadfluid/bt300f/','0.8', 'monthly'),
        ('brands/leadfluid/bt300l/','0.8', 'monthly'),
        ('brands/leadfluid/bt300s/','0.8', 'monthly'),
        ('brands/leadfluid/bt301f/','0.8', 'monthly'),
        ('brands/leadfluid/bt301l/','0.8', 'monthly'),
        ('brands/leadfluid/bt301s/','0.8', 'monthly'),
        ('brands/leadfluid/bt600f/','0.8', 'monthly'),
        ('brands/leadfluid/bt600l/','0.8', 'monthly'),
        ('brands/leadfluid/bt600p-c/','0.8', 'monthly'),
        ('brands/leadfluid/bt600s/','0.8', 'monthly'),
        ('brands/leadfluid/bt601f/','0.8', 'monthly'),
        ('brands/leadfluid/bt601l/','0.8', 'monthly'),
        ('brands/leadfluid/bt601s/','0.8', 'monthly'),
        ('brands/leadfluid/bx600s/','0.8', 'monthly'),
        ('brands/leadfluid/jp300s/','0.8', 'monthly'),
        ('brands/leadfluid/jp301s/','0.8', 'monthly'),
        ('brands/leadfluid/mf103/','0.8', 'monthly'),
        ('brands/leadfluid/mf106/','0.8', 'monthly'),
        ('brands/leadfluid/mf118/','0.8', 'monthly'),
        ('brands/leadfluid/mf133/','0.8', 'monthly'),
        ('brands/leadfluid/wg600f/','0.8', 'monthly'),
        ('brands/leadfluid/wg600s/','0.8', 'monthly'),
        ('brands/leadfluid/wt300f/','0.8', 'monthly'),
        ('brands/leadfluid/wt300s/','0.8', 'monthly'),
        ('brands/leadfluid/wt600f/','0.8', 'monthly'),
        ('brands/leadfluid/wt600f-65/','0.8', 'monthly'),
        ('brands/leadfluid/wt600s/','0.8', 'monthly'),
        ('brands/leadfluid/wt600s-65/','0.8', 'monthly'),
        ('brands/leadfluid/g3030-1s/','0.8', 'monthly'),
        ('brands/leadfluid/g6060-1s/','0.8', 'monthly'),
        ('brands/leadfluid/tfd/','0.8', 'monthly'),
        ('brands/leadfluid/tfd02-01/','0.8', 'monthly'),
        ('brands/leadfluid/tfd03-01/','0.8', 'monthly'),
        ('brands/leadfluid/tfd04/','0.8', 'monthly'),
        ('brands/leadfluid/tgd01-01/','0.8', 'monthly'),
        ('brands/leadfluid/tsd01-01/','0.8', 'monthly'),
        ('brands/leadfluid/tyd01-01/','0.8', 'monthly'),
        ('brands/leadfluid/tyd01-02/','0.8', 'monthly'),
        ('brands/leadfluid/tyd02-01/','0.8', 'monthly'),
        ('brands/leadfluid/tyd02-02/','0.8', 'monthly'),
        ('brands/leadfluid/tyd02-04/','0.8', 'monthly'),
        ('brands/leadfluid/tyd02-06/','0.8', 'monthly'),
        ('brands/leadfluid/tyd02-10/','0.8', 'monthly'),
        ('brands/leadfluid/tyd03-01/','0.8', 'monthly'),
        ('brands/leadfluid/ct3001f/','0.8', 'monthly'),
        ('brands/leadfluid/af9a-b/','0.8', 'monthly'),
        ('brands/leadfluid/ef803/','0.8', 'monthly'),
        ('brands/leadfluid/ef806/','0.8', 'monthly'),
        ('brands/leadfluid/ef900/','0.8', 'monthly'),
        ('brands/leadfluid/ef903/','0.8', 'monthly'),
        ('brands/leadfluid/ef906/','0.8', 'monthly'),
        ('brands/leadfluid/ef918/','0.8', 'monthly'),
        ('brands/leadfluid/ef933/','0.8', 'monthly'),
        ('brands/leadfluid/fg600s-a3/','0.8', 'monthly'),
        ('brands/leadfluid/fg600s-q/','0.8', 'monthly'),
        ('brands/leadfluid/fg600s-w3/','0.8', 'monthly'),
        ('brands/leadfluid/fg601s-q/','0.8', 'monthly'),
        ('brands/leadfluid/fg601s-w3/','0.8', 'monthly'),
        ('brands/leadfluid/fg604s-a/','0.8', 'monthly'),
        ('brands/leadfluid/fp300s-a3/','0.8', 'monthly'),
        ('brands/leadfluid/mc10/','0.8', 'monthly'),
        ('brands/leadfluid/mm10/','0.8', 'monthly'),
        ('pump/atoz/peristaltic-flow-setpoint-mismatch/', '0.7', 'monthly'),
        ('pump/atoz/tubing-crush-tear-causes/', '0.7', 'monthly'),
        ('pump/atoz/flow-calibration/', '0.7', 'monthly'),  # 유량 캘리브레이션 (무주공산)
        ('pump/atoz/tube-size-guide/', '0.7', 'monthly'),  # 튜브 규격·펌프헤드 (무주공산)
        ('application/',  '0.7', 'monthly'),  # 실험 가이드 (목록)
        ('brands/alicat/',       '0.9', 'weekly'),   # Alicat 제품 카탈로그(카드)
        ('brands/alicat/mc-series/','0.8', 'monthly'),
        ('brands/alicat/mfc-guide/','0.7', 'monthly'),
        ('brands/alicat/manual/','0.7', 'monthly'),
        ('brands/sh-scientific/guide/','0.9', 'monthly'),  # 삼흥 허브 = 제품 선택 가이드(견적 funnel)
        ('brands/sh-scientific/manual/','0.7', 'monthly'),  # 삼흥 메뉴얼
        ('brands/sh-scientific/','0.9', 'weekly'),  # 삼흥 제품 카탈로그(사양·가격 — D1 주입)
        ('brands/sh-scientific/gas-flow-package/','0.8', 'monthly'),  # 가스플로 패키지 300mm
        ('brands/sh-scientific/gas-flow-package-600mm/','0.8', 'monthly'),  # 가스플로 패키지 600mm
        ('brands/sh-scientific/rotary-tube-furnace/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-tube-furnace-pro/','0.8', 'monthly'),
        ('brands/sh-scientific/gas-flow-3zone/','0.8', 'monthly'),
        ('brands/sh-scientific/tube-1500/','0.8', 'monthly'),
        ('brands/sh-scientific/tube-1800/','0.8', 'monthly'),
        ('brands/sh-scientific/vacuum-tube-turnkey/','0.8', 'monthly'),
        ('brands/sh-scientific/vacuum-muffle-1200/','0.8', 'monthly'),
        ('brands/sh-scientific/vacuum-muffle-1200-quartz/','0.8', 'monthly'),
        ('brands/sh-scientific/vacuum-muffle-1500/','0.8', 'monthly'),
        ('brands/sh-scientific/vacuum-muffle-1900/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1050/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1200/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1500/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1700/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1800/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1900/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-kiln-1200-2zone/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-kiln-1200-3zone/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-kiln-1500-2zone/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-kiln-1500-3zone/','0.8', 'monthly'),
        ('brands/sh-scientific/muffle-1200-quartz/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-batch-300/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-batch-3zone/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1200/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1500/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1700/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1800/','0.8', 'monthly'),
        ('brands/sh-scientific/blog/','0.7', 'weekly'),  # 삼흥 설치·A/S 블로그
        ('brands/sh-scientific/blog/furnace-install-checklist/','0.6', 'monthly'),  # 설치 체크리스트
        ('brands/sh-scientific/blog/furnace-temperature-selection/','0.6', 'monthly'),
        ('brands/sh-scientific/blog/furnace-types-overview/','0.6', 'monthly'),
        ('brands/sh-scientific/blog/heating-ramp-profile/','0.6', 'monthly'),
        ('brands/sh-scientific/blog/muffle-furnace-how-to/','0.6', 'monthly'),
        ('brands/sh-scientific/blog/tube-furnace-atmosphere-control/','0.6', 'monthly'),
        ('brands/sh-scientific/blog/tube-vs-muffle-furnace/','0.6', 'monthly'),
        ('application/biopharmaceutical.html', '0.8', 'monthly'),        # 응용분야 클러스터(통합 후 생존)
        ('application/analytical-instrument.html', '0.8', 'monthly'),
        ('application/environmental.html', '0.8', 'monthly'),
        # 응용 가이드 6편(관류·연속배양·광배양·flowchem·장기칩·PC제어)은 posts.json(type=guide) 루프가 추가 — 중복 방지
    ]
    # 브랜드 상세페이지 자동 등재(갱신 1곳 원칙) — brands/<brand>/<slug>/index.html 를 스캔해
    # static_pages에 없는 것만 추가한다. 새 제품페이지를 만들면 빌드만으로 sitemap에 들어간다.
    # 제외: 리다이렉트 스텁(meta refresh)·noindex·_redirects 301 소스.
    _known = {p.rstrip('/') + '/' for p, _, _ in static_pages}
    _red_srcs = _redirect_sources()
    _auto = []
    _bdir = os.path.join(ROOT_DIR, 'brands')
    if os.path.isdir(_bdir):
        for brand in sorted(os.listdir(_bdir)):
            bpath = os.path.join(_bdir, brand)
            if not os.path.isdir(bpath):
                continue
            _cands = [None] + sorted(os.listdir(bpath))  # None = 브랜드 허브 자체
            for slug in _cands:
                idx = os.path.join(bpath, 'index.html') if slug is None else os.path.join(bpath, slug, 'index.html')
                if not os.path.isfile(idx):
                    continue
                rel = f'brands/{brand}/' if slug is None else f'brands/{brand}/{slug}/'
                if rel in _known:
                    continue
                if ('/' + rel) in _red_srcs or ('/' + rel).rstrip('/') in _red_srcs:
                    continue
                head = read(idx)[:4000]
                if 'http-equiv="refresh"' in head or 'noindex' in head:
                    continue
                _auto.append((rel, '0.8', 'monthly'))
    if _auto:
        print(f'  sitemap 자동 등재(브랜드 상세): {len(_auto)}개')
    for path, prio, freq in list(static_pages) + _auto:
        loc = (base_url + path).replace('.html', '')  # CF 클린 URL(.html 없이 서빙)에 맞춤
        sitemap_lines.append(
            f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{build_date}</lastmod>\n    <priority>{prio}</priority>\n    <changefreq>{freq}</changefreq>\n  </url>'
        )

    # posts.json에서 콘텐츠(셋업사례) 합산 (noindex=true 글은 sitemap 제외)
    posts_json = os.path.join(SCRIPT_DIR, 'posts.json')
    if os.path.exists(posts_json):
        try:
            with open(posts_json, 'r', encoding='utf-8') as f:
                posts_data = json.load(f)
            for p in posts_data.get('posts', []):
                if p.get('noindex'):
                    continue
                url = p.get('url', '')
                date = p.get('date', '')
                if url:
                    full_url = (base_url.rstrip('/') + url).replace('.html', '')  # CF 클린 URL에 맞춤
                    lastmod_line = f'\n    <lastmod>{date}</lastmod>' if date else ''
                    sitemap_lines.append(
                        f'  <url>\n    <loc>{full_url}</loc>{lastmod_line}\n    <priority>0.9</priority>\n    <changefreq>monthly</changefreq>\n  </url>'
                    )
        except Exception as e:
            print(f'  [warn] posts.json 읽기 실패 (블로그 글 sitemap 누락): {e}')

    sitemap_lines.append('</urlset>')
    write(os.path.join(ROOT_DIR, 'sitemap.xml'), '\n'.join(sitemap_lines) + '\n')

    # 개발 요청 게시판 정적 렌더 (SSOT: _build/requests.json)
    build_requests()

    # GEO: 도입·논문 사례 목록 정적 렌더 + 전 페이지 크롤러 nav 주입
    build_setups()  # /setups/index.html 논문 셋업 6편 정적 렌더 (posts.json type=setup)
    build_home_paper_cases()  # 홈 '논문 사례' 카드 정적 렌더 (paper_cases.json · 공정 변수 SSOT)
    build_rss()  # feed.xml (RSS 2.0) — 매거진 구독·애그리게이터
    inject_setup_cta()  # 논문 셋업 글 하단 '이 셋업 그대로 견적·솔루션' CTA(?setup= 전달)
    build_all_products()  # 전 제품 통합 카탈로그 (브랜드 허브 카드 자동 수집)
    inject_static_nav()
    inject_head_schema()
    normalize_html_urls()
    build_new_research()  # 홈 최신연구 레일 — posts.json 자동 렌더
    build_prices()        # 가격 SSOT — SQL 최저가를 index.html·site.js 마커에 주입
    build_search_index()  # 사이트 검색 인덱스(/search-index.json) — 전 페이지 자동 스캔 (301 소스 제외)

    print('\n' + '=' * 60)
    print(f'  완료: {len(written)}개 페이지 + sitemap.xml')
    print('=' * 60)


if __name__ == '__main__':
    main()
# pumps pillar wired: peristaltic/syringe/metering/gear + hub (2026-07)
