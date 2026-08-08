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
    ('/requests/', '소프트웨어 제어'),
    ('/application/', '실험 가이드'),
    ('/application/biopharmaceutical.html', '바이오의약 — 발효·세포배양·정제·충전'),
    ('/application/analytical-instrument.html', '분석기기 — 컬럼 주입·시료 정량 주입'),
    ('/application/environmental.html', '환경 — 수질·폐수 정량 투입'),
    ('/application/flow-chemistry.html', 'flow chemistry 연속흐름 반응'),
    ('/brands/leadfluid/blog/', '펌프 셋업 사례 — 실제 도입·제어·유량 보정 셋업'),
    ('/pump/atoz/', '펌프 문제해결 — 유량 이상·튜빙 파손·멈춤 증상별 해결'),
    ('/brands/leadfluid/guide/', '펌프·튜브 선택 가이드 — 조건 입력하면 추천'),
    ('/pump/atoz/peristaltic-flow-setpoint-mismatch/', '연동펌프 유량이 설정값과 다른 이유'),
    ('/pump/atoz/tubing-crush-tear-causes/', '연동펌프 튜빙 씹힘·찢어짐 원인·해결'),
    ('/pump/atoz/flow-calibration/', '연동펌프 유량 캘리브레이션 방법 — 설정값·실제 유량 보정'),
    ('/pump/atoz/tube-size-guide/', '연동펌프 튜브 규격·펌프헤드 가이드 — 번호별 내경(mm)·유량'),
    ('/pump/setups/plating-flow-calibration/', '도금 라인 유량 보정 셋업 — BT101L 2대 다펌프 제어(도입 스토리)'),
    ('/magazine/', '실험 셋업 매거진 — 논문 셋업으로 배우는 실험 장비 구성'),
    ('/magazine/sofc-hcl-syngas/', '석탄 합성가스 HCl이 SOFC 성능에 미치는 영향 — 가스 분위기·온도 제어 셋업 (J. Power Sources 2007)'),
    ('/setups/', '도입·논문 사례 — LeadFluid 펌프가 쓰인 연구 셋업'),
    ('/setups/heart-eshp-bt101l.html', '심장 체외 관류(ESHP) — BT101L 연동펌프 (Frontiers 2021)'),
    ('/setups/damo-recirculation-bt600s.html', '혐기성 메탄산화 반응기 순환 — BT600S 연동펌프 (Environ. Sci. Technol. 2021)'),
    ('/setups/nitrification-ph-bq50s.html', '폐수 질산화 pH 제어 — BQ50S 정량펌프 (Bioresource Technology 2017)'),
    ('/setups/brain-electrode-tyd01.html', '뇌 피질 인터페이싱 — TYD01-01 시린지펌프 (Nature Electronics 2024)'),
    ('/setups/catheter-heparin-bt101.html', '혈관내 카테터 헤파린 코팅 — BT101 L 연동펌프 (Nature Communications 2024)'),
    ('/setups/co2-capture-ct3001f.html', '연속 CO₂ 포집 — CT3001F PEEK 기어펌프 (Nature Communications 2024)'),
    ('/furnace/setups/', '퍼니스 셋업 사례 — 튜브퍼니스·전기로 가스·온도 제어 도입 사례'),
    ('/furnace/setups/alicat-mfc-tubefurnace/', '1500℃ 튜브퍼니스 가스 분위기 제어 — Alicat MFC 도입 사례'),
    ('/compare/imported-peristaltic-alternative/', 'Masterflex·Watson-Marlow 연동펌프 국내 대안'),
    ('/trust/', '믿고 도입할 때 (국내 A/S·정품·보증)'),
    ('/faq/', '자주 묻는 질문(FAQ)'),
    ('/contact/', '문의하기'),
]


def _crawler_nav_html():
    def grp(h):
        if h.startswith('/setups/') or h.startswith('/magazine/') or h.startswith('/compare/') or h in ('/', '/trust/', '/faq/', '/contact/'):
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


def inject_static_nav():
    """모든 콘텐츠 페이지의 #pumplab-footer div에 정적 링크 nav 주입(크롤러 가시화, 마커 기반 idempotent).
    리다이렉트 페이지(meta refresh)는 건드리지 않음."""
    nav = _crawler_nav_html()
    START, END = '<!--CNAV_START-->', '<!--CNAV_END-->'
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if '_build' in dirpath.split(os.sep):
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
    ('BIO',    {'brain-electrode-tyd01', 'catheter-heparin-bt101', 'heart-eshp-bt101l'}),
    ('ENV',    {'damo-recirculation-bt600s', 'nitrification-ph-bq50s'}),
    ('ENERGY', {'co2-capture-ct3001f', 'alicat-mfc-tubefurnace', 'leadfluid-bt101l-plating'}),
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

    parts = []
    total_cards = 0
    for g in groups:
        flc = ' fl' if g.get('fl') else ''
        parts.append(
            f'<div class="mag-cat-t{flc}">{escape(g.get("title",""))}'
            f'<span class="c">{escape(g.get("caption",""))}</span></div>'
        )
        parts.append('<div class="mag-arts">')
        for c in g.get('cards', []):
            proc = [k for k in c.get('process', []) if k]
            kws = ''.join(f'<span class="ma-hero-kw">{escape(k)}</span>' for k in proc)
            img = escape(c.get('img', ''))
            style = f' style="background-image:url(\'{img}\')"' if img else ''
            hero = f'<div class="ma-hero"{style}>{kws}</div>' if (kws or img) else ''
            parts.append(
                f'<a class="m-art{flc}" href="{escape(c.get("url",""))}">'
                f'{hero}'
                f'<h3>{escape(c.get("title",""))}</h3>'
                f'<p>{escape(c.get("desc",""))}</p>'
                f'<div class="mt">{escape(c.get("meta",""))}</div></a>'
            )
            total_cards += 1
        parts.append('</div>')
        parts.append(
            f'<a class="mag-all" href="{escape(g.get("all_url",""))}">'
            f'{escape(g.get("all_label",""))} &rarr;</a>'
        )
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

    count_html = f'셋업 <b>{len(setups)}</b> · 연구 분야 3'
    parts = ', '.join(f'{escape(p.get("model_focus",""))}({escape(p.get("summary",""))})' for p in papers)
    answer_html = (
        f'<b>LeadFluid(리드플루이드) 펌프는 Nature 등 국제 학술지 연구 {len(papers)}편의 실험 셋업에 사용됐습니다.</b> '
        f'바이오·의료, 환경·수처리, 에너지·재료·열처리 분야별로 정리했습니다 — {parts} 등. '
        f'각 셋업의 논문·저널·펌프 모델·DOI를 아래에서 확인하세요.'
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
            "slogan": "논문 실험 셋업을 분석해 공유하는 실험 셋업 매거진",
            "description": "논문이 실제로 쓴 실험 셋업을 공정 → 조건 → 필요 장비 순으로 분석해 공유하는 실험 셋업 매거진. 열처리·증착(퍼니스)과 유체·펌프 두 갈래로 온도·가스 분위기·진공·유량 제어 조건과 장비 구성을 셋업 단위로 정리한다. 매거진에서 다룬 장비가 필요하면 문의 시 할인가로 안내하며, 구매·수리·국내 A/S(구매 시 3년 무상보증)는 실험 장비 수리 전문 업체 이머전트(Emergent co)가 맡는다. 리드플루이드(LeadFluid)·삼흥에너지(SH Scientific)·Alicat 질량유량계(MFC) 등을 정품으로 안내한다.",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "부산광역시",
                "addressCountry": "KR"
            },
            "areaServed": {"@type": "Country", "name": "대한민국"},
            "knowsAbout": ["실험 장비 시스템 통합", "실험 기기 통합 제어", "온도 제어", "진공 제어", "유량 제어", "측정 기기 연동", "Modbus·RS-485 통합 제어", "실험실 정량펌프", "연동펌프(페리스탈틱 펌프)", "시린지펌프", "기어펌프", "질량유량계(MFC)", "관류배양", "연속배양(chemostat)", "리드플루이드(LeadFluid) 펌프", "리드플루이드 펌프 국내 직접 A/S", "실험 셋업 정보", "Alicat 질량유량계", "삼흥에너지(SH Scientific) 튜브퍼니스·전기로", "열처리로(전기로·튜브퍼니스)"],
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
    'magazine': ('매거진', '/magazine/'),
    'application': ('실험 가이드', '/application/'),
    'pumps': ('펌프 종류', '/pumps/'),
    'setups': ('연구별 셋업', '/setups/'),
    'requests': ('소프트웨어 제어', '/requests/'),
    'trust': ('믿고 도입할 때', '/trust/'),
    'contact': ('문의하기', '/contact/'),
    'faq': ('자주 묻는 질문(FAQ)', '/faq/'),
    'gas': ('기체', '/gas/'),
    'vacuum': ('진공', '/vacuum/'),
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
    if rel == 'index.html' or len(parts) != 2:
        return None
    seg, fn = parts[0], parts[1]
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
    if fn != 'index.html' and ('/' + rel) != sec_url:
        leaf = _page_title_short(html) or fn
        items.append({"@type": "ListItem", "position": 3, "name": leaf, "item": BASE_URL_LD + '/' + rel})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def inject_head_schema():
    """모든 색인 콘텐츠 페이지 <head>에 Organization/WebSite + 페이지별 BreadcrumbList JSON-LD 정적 주입(크롤러 가시화).
    리다이렉트(meta refresh)·noindex 페이지는 제외."""
    START, END = '<!--HEADLD_START-->', '<!--HEADLD_END-->'
    org_json = json.dumps(ORG_WEBSITE_GRAPH, ensure_ascii=False).replace('</', '<\\/')
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        if '_build' in dirpath.split(os.sep):
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
        if '_build' in dirpath.split(os.sep):
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
        ('manuals/',      '0.6', 'monthly'),  # 메뉴얼 모음 허브
        ('brands/',       '0.6', 'monthly'),  # 브랜드 소개 허브
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
        ('brands/leadfluid/guide/', '0.7', 'monthly'),   # 펌프·튜브 선택 위저드   # 트러블슈팅 허브
        ('pump/atoz/peristaltic-flow-setpoint-mismatch/', '0.7', 'monthly'),
        ('pump/atoz/tubing-crush-tear-causes/', '0.7', 'monthly'),
        ('pump/atoz/flow-calibration/', '0.7', 'monthly'),  # 유량 캘리브레이션 (무주공산)
        ('pump/atoz/tube-size-guide/', '0.7', 'monthly'),  # 튜브 규격·펌프헤드 (무주공산)
        ('faq/',          '0.7', 'monthly'),  # FAQ
        ('application/',  '0.7', 'monthly'),  # 실험 가이드 (목록)
        ('brands/alicat/',       '0.8', 'monthly'),  # 소프트웨어 호환 장비 — ALICAT
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
        ('brands/sh-scientific/rotary-batch-300/','0.8', 'monthly'),
        ('brands/sh-scientific/rotary-batch-3zone/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1200/','0.8', 'monthly'),
        ('brands/sh-scientific/elevator-1500/','0.8', 'monthly'),
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
    for path, prio, freq in static_pages:
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
    inject_static_nav()
    inject_head_schema()
    normalize_html_urls()

    print('\n' + '=' * 60)
    print(f'  완료: {len(written)}개 페이지 + sitemap.xml')
    print('=' * 60)


if __name__ == '__main__':
    main()
# pumps pillar wired: peristaltic/syringe/metering/gear + hub (2026-07)
