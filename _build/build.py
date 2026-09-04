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
import sys
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


# os.walk 는 continue 로 가지치기가 안 된다 — dirnames 를 직접 잘라야 그 아래로 안 내려간다.
# .git 만 3만 5천 개, img 는 1천 개가 넘는데 HTML 은 한 장도 없다. 훑을 이유가 없다.
WALK_SKIP = {'.git', '.wrangler', '_build', '_to_delete', 'node_modules', 'img', 'assets', 'out'}

def prune(dirnames):
    dirnames[:] = [d for d in dirnames if d not in WALK_SKIP and not d.startswith('.')]


# 파일은 한 번만 읽고 한 번만 쓴다.
#   전에는 주입 단계마다 같은 HTML 을 다시 열었고(단계당 486개), write() 는 비교하려고
#   또 한 번 열었다. 486개 × 9번 ≈ 4,400 번의 파일 열기 — 윈도우에서는 이게 빌드 시간의 대부분이다.
#   이제 읽은 것은 메모리에 두고, 바뀐 것만 마지막에 한 번 디스크로 내린다.
_FCACHE = {}      # 절대경로 -> 현재 내용
_DIRTY = set()    # 아직 디스크에 안 내려간 것


def read(path):
    key = os.path.abspath(path)
    if key not in _FCACHE:
        with open(path, 'r', encoding='utf-8') as f:
            _FCACHE[key] = f.read()
    return _FCACHE[key]


def write(path, content):
    """바뀐 것만 기록해 둔다 (실제 쓰기는 flush_writes 에서 한꺼번에)."""
    global _TREE
    key = os.path.abspath(path)
    if key not in _FCACHE:
        if os.path.exists(path):
            try:
                read(path)
            except Exception:
                _FCACHE[key] = None
        else:
            _TREE = None      # 새 페이지가 생겼다 — 훑어둔 목록을 다시 만든다
    if _FCACHE.get(key) == content:
        return False          # 변경 없음
    _FCACHE[key] = content
    _DIRTY.add(key)
    return True


def flush_writes():
    """모아둔 변경분을 디스크에 내린다. 안 바뀐 파일은 건드리지 않는다(OneDrive 동기화 부담)."""
    n = 0
    for key in sorted(_DIRTY):
        d = os.path.dirname(key)
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        # newline='\n' 이 없으면 윈도우에서 \n 이 \r\n 으로 바뀐다.
        # 저장소는 .gitattributes 로 LF 를 쓰기로 했으므로, 커밋할 때마다 git 이
        # 700개 넘는 파일에 «CRLF will be replaced by LF» 경고를 쏟고 되돌리는 일을 한다.
        with open(key, 'w', encoding='utf-8', newline='\n') as f:
            f.write(_FCACHE[key])
        n += 1
    _DIRTY.clear()
    return n


_TREE = None


def html_tree():
    """트리는 빌드당 한 번만 훑는다 — 같은 목록을 네 번 다시 만들 이유가 없다."""
    global _TREE
    if _TREE is None:
        t = []
        for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
            prune(dirnames)
            if set(dirpath.split(os.sep)) & {'_build', '_to_delete'}:
                continue
            hs = [f for f in filenames if f.endswith('.html')]
            if hs:
                t.append((dirpath, hs))
        _TREE = t
    return _TREE


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
    ('/product/', '제품 통합 카탈로그 — 전기로·펌프·질량유량계(MFC)·전기화학 (삼흥에너지·리드플루이드·Alicat·가오스유니온)'),
    ('/brands/gaossunion/co2rr-catalyst/', 'CO₂ 환원(CO₂RR) 촉매·전극 — Ag·Sn·Bi₂O₃·Cu 분말과 GDE 캐소드, IrO₂ 애노드'),
    ('/brands/hench/pellet-press-yp-15/', 'Hench YP-15 수동 유압 펠릿 프레스 15T — IR(KBr)·XRD 시료 압편기'),
    ('/brands/hench/cylindrical-die-hmy-11-14/', 'Hench HMY 원통형 펠릿 다이 Φ11–14mm — KBr 펠릿·XRD 분말 시료 성형 몰드'),
    ('/manuals/', '메뉴얼 모음 — 전기로·온도컨트롤러·펌프·MFC 사용 메뉴얼'),
    ('/guides/', '선택 가이드 — 퍼니스·펌프·질량유량계(MFC)·전기화학 장비 고르는 법'),
    ('/requests/', '소프트웨어 제어'),
    ('/application/', '실험 가이드'),
    ('/application/biopharmaceutical.html', '바이오의약 — 발효·세포배양·정제·충전'),
    ('/application/analytical-instrument.html', '분석기기 — 컬럼 주입·시료 정량 주입'),
    ('/application/environmental.html', '환경 — 수질·폐수 정량 투입'),
    ('/application/flow-chemistry.html', 'flow chemistry 연속흐름 반응'),
    ('/brands/leadfluid/blog/', '펌프 셋업 사례 — 실제 도입·제어·유량 보정 셋업'),
    ('/pump/atoz/', '펌프 문제해결 — 유량 이상·튜빙 파손·멈춤 증상별 해결'),
    ('/magazine/pump-selection-wizard/', '펌프 선택 위저드 — 종류·유량·용도로 고르기'),
    ('/pump/atoz/peristaltic-flow-setpoint-mismatch/', '연동펌프 유량이 설정값과 다른 이유'),
    ('/pump/atoz/tubing-crush-tear-causes/', '연동펌프 튜빙 씹힘·찢어짐 원인·해결'),
    ('/pump/atoz/flow-calibration/', '연동펌프 유량 캘리브레이션 방법 — 설정값·실제 유량 보정'),
    ('/pump/atoz/tube-size-guide/', '연동펌프 튜브 규격·펌프헤드 가이드 — 번호별 내경(mm)·유량'),
    ('/pump/setups/plating-flow-calibration/', '도금 라인 유량 보정 셋업 — BT101L 2대 다펌프 제어(도입 스토리)'),
    ('/magazine/', '셋업 사례 — 논문 셋업·가이드·용어사전·도입 사례 (에너지·소재 공정)'),
    ('/materials/', '소재 — 전기화학 재료·소모품, CO2RR 촉매, 멤브레인, 연마용품'),
    ('/info/', '제품 정보 — 부품·장비 소개, 브랜드별 장비 비교, FAQ·제품상담'),
    ('/wiki/', '배터리 사전 — 공정·재료·전기화학·장비 용어를 위키형으로 설명'),
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
    ('/magazine/electrode-vacuum-post-drying-moisture/', '전극 진공 후건조·잔류 수분 관리 셋업 — 압력 사이클과 노점 (Batteries & Supercaps 2021)'),
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
        'magazine/electrode-vacuum-post-drying-moisture/index.html',
    }  # 매거진 논문글(명시적으로만)
    count = 0
    for dirpath, filenames in html_tree():
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
                '<section class="setup-cta" style="margin:26px 0 8px;border:1px solid #d6e0ee;border-radius:14px;padding:22px 22px;background:#EAF4FB">'
                '<div style="font-size:12px;font-weight:800;letter-spacing:.04em;color:#3B3695;margin-bottom:7px">솔루션 패키지</div>'
                '<h3 style="font-size:18px;font-weight:700;color:#3B3695;margin:0 0 8px;line-height:1.4">이 셋업 구성 그대로 견적·솔루션 문의</h3>'
                '<p style="font-size:14px;color:#3a4650;line-height:1.75;margin:0 0 14px">위에 정리한 장비·모듈 구성을 기준으로 견적과 통합 셋업(구성·제어·연동·설치)을 안내해 드립니다. 다른 브랜드·조건도 함께 맞춰 드립니다.</p>'
                '<a href="/contact/?setup=' + quote(title) + '#general" style="display:inline-block;background:#3B3695;color:#fff;font-weight:800;font-size:14px;padding:11px 20px;border-radius:9px;text-decoration:none">이 셋업으로 문의하기 &rarr;</a>'
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
    for dirpath, filenames in html_tree():
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
            "slogan": "에너지·배터리·수전해 실험장비 원스톱 스토어 + 셋업 매거진",
            "description": "에너지·배터리·수전해 실험장비 원스톱 스토어이자 셋업 매거진. 튜브퍼니스·전기로, 정량·연동펌프, 전기화학 셀·전극(가오스유니온 838종), 질량유량계(MFC) 등 1,700여 SKU를 정품 공급한다. 논문과 현장이 실제로 쓴 에너지·소재 공정 셋업을 공정 → 조건 → 필요 장비 순으로 분석해 공유하는 매거진을 함께 운영한다. 소성·증착(퍼니스)·가스 분위기·유량 제어와 유체·펌프 조건을 셋업 단위로 정리하고, 배터리 소재 R&D·파일럿 라인 등 제조사가 완제품으로 다루지 않는 통합·특수 셋업은 직접 설계·공급한다. 매거진에서 다룬 장비는 정가 대비 3% 상시 할인가로 안내하며, 구매·수리·국내 A/S(구매 시 3년 무상보증)는 실험 장비 수리 전문 업체 이머전트(Emergent co)가 맡는다. 리드플루이드(LeadFluid)·삼흥에너지(SH Scientific)·Alicat 질량유량계(MFC) 등을 정품으로 안내한다.",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "부산광역시",
                "addressCountry": "KR"
            },
            "areaServed": {"@type": "Country", "name": "대한민국"},
            "knowsAbout": ["실험 장비 시스템 통합", "실험 기기 통합 제어", "온도 제어", "진공 제어", "유량 제어", "측정 기기 연동", "Modbus·RS-485 통합 제어", "실험실 정량펌프", "연동펌프(페리스탈틱 펌프)", "시린지펌프", "기어펌프", "마그네틱 펌프", "질량유량계(MFC)", "질량유량계 다기체 보정", "sccm·slm 가스 유량 제어", "압력 컨트롤러", "배압 레귤레이터(BPR)", "관류배양", "연속배양(chemostat)", "flow chemistry 연속흐름 반응", "열처리로(전기로·튜브퍼니스)", "튜브퍼니스(관상로)", "머플로(박스형 전기로)", "진공 전기로", "회전 튜브로(로터리 킬른)", "엘리베이터 전기로", "3존 튜브퍼니스", "소성(firing)", "하소(calcination)", "소결(sintering)", "어닐링(소둔)", "가스 분위기 제어", "산소 분압(pO2) 제어", "동적 분위기 제어(DCA)", "CVD 탄소 코팅", "열산화", "배터리 양극재 전구체 공침", "전해액 순환", "수전해·전기화학 셋업", "전기화학 셀(H셀·GDE·MEA)", "기준전극·작업전극·상대전극", "CO2 환원(CO2RR) 촉매", "배터리 테스트 셀(코인·in-situ)", "배터리 용어 사전", "리드플루이드(LeadFluid) 펌프", "리드플루이드 펌프 국내 직접 A/S", "Alicat 질량유량계", "삼흥에너지(SH Scientific) 튜브퍼니스·전기로", "실험 셋업 정보"],
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
    for dirpath, filenames in html_tree():
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


def stamp_assets():
    """자산 URL 뒤에 내용 해시를 붙인다 — /assets/site.js?v=ab12cd34

    Cloudflare 가 /assets/*.js·css 를 4시간(max-age=14400) 캐시한다.
    그래서 JS 를 고쳐 배포해도 재방문자에게는 옛 파일이 그대로 갔다
    (2026-09-03 제품문의 모달 수정이 배포 직후 사이트에 안 먹힌 원인).
    내용이 바뀔 때만 ?v= 값이 바뀌므로 캐시 이득은 그대로 두고 갱신만 즉시 된다.
    site.js 는 build_prices() 가 고치므로 반드시 그 뒤에 부른다."""
    import hashlib
    ver = {}
    for rel in ('assets/site.js', 'assets/site.css', 'assets/detail.css'):
        fp = os.path.join(ROOT_DIR, rel)
        if os.path.exists(fp):
            ver['/' + rel] = hashlib.md5(read(fp).encode('utf-8')).hexdigest()[:8]
    if not ver:
        return
    pat = re.compile(r'((?:src|href)=")(/assets/(?:site\.js|site\.css|detail\.css))(?:\?v=[0-9a-f]+)?(")')

    def sub(m):
        return m.group(1) + m.group(2) + '?v=' + ver.get(m.group(2), '') + m.group(3)

    count = 0
    for dirpath, filenames in html_tree():
        for fn_ in filenames:
            if not fn_.endswith('.html'):
                continue
            fp = os.path.join(dirpath, fn_)
            html = read(fp)
            new = pat.sub(sub, html)
            if new != html:
                write(fp, new)
                count += 1
    print('  자산 캐시 무효화(?v=): %d개 페이지 · %s'
          % (count, ' · '.join('%s %s' % (k.split('/')[-1], v) for k, v in sorted(ver.items()))))


def normalize_html_urls():
    """Cloudflare Pages는 /x.html을 /x로 서빙하고 /x.html은 /x로 리다이렉트한다.
    내부 링크(href·src)·canonical·og·JSON-LD의 .html을 제거해 리다이렉트 홉을 없앤다.
    리다이렉트 스텁(meta refresh)은 제외(그 자체가 옛 .html URL을 처리)."""
    count = 0
    for dirpath, filenames in html_tree():
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
    ('hefei', '허페이 인시츄', 'echem'),
    ('aida', '아이다', 'echem'),
    ('dodochem', 'DodoChem', 'echem'),
    ('hench', 'Hench', 'prep'),
    ('neware', '뉴웨어', 'echem'),
]  # (슬러그, 표기명, 매핑 실패 시 기본 카테고리)
# 브랜드별 data-cat 어휘 → 통합 카테고리
ALLPROD_CATMAP = {
    'furnace': 'heat',
    'drying': 'dry', 'distill': 'dry',
    'incubator': 'culture', 'waterbath': 'culture', 'chamber': 'culture', 'sterilizer': 'culture',
    'mixing': 'mix',
    'pellet': 'prep', 'die': 'prep', 'slicer': 'prep',   # 시료 전처리(펠릿 프레스·다이·슬라이서)
    'vacuumpump': 'vacuum', 'vac': 'vacuum',
    'pump': 'pump', 'peri': 'pump', 'syr': 'pump', 'gear': 'pump', 'ex': 'pump', 'head': 'pump',
    'mfc': 'gas', 'std': 'gas', 'hp': 'gas', 'bio': 'gas', 'corr': 'gas', 'dual': 'gas', 'press': 'gas',
    'electrode': 'echem', 'catalyst': 'echem', 'material': 'echem', 'accessory': 'echem',
    'fumehood': 'safety', 'measuring': 'safety',
}

# ── 통합 카탈로그 상세필터: 브랜드 무관 '계열' 토큰(fam:*) ────────────────────
# 기존 gu:* 는 가오스유니온 URL 전용이라 AIDA·허페이·DodoChem 카드가 필터에서 통째로
# 사라졌다. URL 마지막 세그먼트로 브랜드와 무관하게 계열을 판정한다. 먼저 맞는 규칙이 이긴다.
ALLPROD_FAM_RULES = [
    ('fam:rde',       r'(^|-)r?rde($|[-0-9])'),
    ('fam:rhe',       r'(^|-)rhe($|-)'),
    ('fam:ref',       r'reference-electrode|salt-bridge|luggin|rotating-ag-ion'),
    ('fam:counter',   r'counter-electrode'),
    ('fam:working',   r'working-electrode|carbon-paste|dual-electrode|electrode-drying'),
    ('fam:holder',    r'clamp|holder|electrode-stand|sample-holder'),
    ('fam:polish',    r'polish'),
    ('fam:catalyst',  r'catalyst'),
    ('fam:insitu',    r'(^|-)(insitu|in-situ|afm|raman|xrd|xafs|uv|sfg|ir|ms|om\d*)($|-)'
                      r'|spectro|imaging|observation|microscope'),
    ('fam:material',  r'(^|-)series-|(^|-)p-|electrolyte|solvent|(^|-)salts($|-)|binder|separator'
                      r'|current-collector|lifsi|litfsi|pvdf|ceramic-disc|whatman|additive'
                      r'|(^|-)cases($|-)|anhydrous|battery-grade|echem-materials'),
    ('fam:cell',      r'cell|reactor'),
    ('fam:die',       r'(^|-)die($|-)|cylindrical-die'),
    ('fam:press',     r'press'),
]
ALLPROD_FAM_RX = [(k, re.compile(rx)) for k, rx in ALLPROD_FAM_RULES]


def allprod_fam(href, cat):
    """URL 슬러그로 계열(fam:*) 판정. echem/mix 카테고리에만 붙인다."""
    if cat not in ('echem', 'mix'):
        return ''
    seg = [x for x in href.strip('/').split('/') if x]
    slug = seg[-1] if seg else ''
    for key, rx in ALLPROD_FAM_RX:
        if rx.search(slug):
            return key
    return 'fam:instrument' if cat == 'echem' else ''


# ── 검색 색인(data-k) 한글·별칭 보강 ─────────────────────────────────────────
# 표기명이 영문뿐인 브랜드(DodoChem 등)와 한글 일반명이 없는 품목(금형·펠릿프레스 등)이
# 검색되지 않던 문제. href 에 매칭되면 해당 어휘를 data-k 에 덧붙인다(화면 노출 없음).
ALLPROD_KEY_ALIASES = [
    (r'/brands/dodochem/',   '도도켐 도도캠 dodochem 배터리소재 전지소재 시약 케미컬'),
    (r'/brands/hefei/',      '허페이 허페이인시츄 hefei 인시츄 in-situ operando 오퍼란도 원위관찰'),
    (r'/brands/aida/',       '아이다 aida'),
    (r'/brands/hench/',      '헨치 hench 시료성형 분말성형'),
    (r'/brands/gaossunion/', '가오스유니온 gaossunion'),
    (r'cylindrical-die',     '금형 몰드 다이 원통금형 펠릿금형 압축금형 tablet die'),
    (r'pellet-press',        '펠릿프레스 펠릿메이커 분말압축기 유압프레스 정제성형기'),
    (r'electrolyte',         '전해액 전해질'),
    (r'anhydrous|solvent',   '무수용매 용매'),
    (r'separator',           '분리막 세퍼레이터'),
    (r'binder',              '바인더 결착제'),
    (r'current-collector',   '집전체 집전판'),
    (r'series-salts|lifsi|litfsi', '리튬염 전해질염'),
]
ALLPROD_KEY_ALIASES_RX = [(re.compile(rx), w) for rx, w in ALLPROD_KEY_ALIASES]


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
        'pellet':     [('최대하중', ['최대하중', '압력범위', '하중']), ('실린더', ['실린더', '피스톤']), ('유효공간', ['유효공간', '챔버'])],
        'slicer':     [('펀칭 하중', ['펀칭']), ('슬라이스 규격', ['슬라이스']), ('적용 시료', ['적용 시료'])],
        'die':        [('성형 규격', ['성형 규격', '성형 직경', '직경']), ('재질', ['재질']), ('경도', ['경도'])],
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
    '전해액': ['전해액', '전해질', 'electrolyte', '리튬황 전해액', '리튬이온 전해액', '나트륨 전해액', 'LiPF6', 'LiTFSI', 'LiFSI', '커스텀 전해액', '배터리 재료'],
    '배터리 소재': ['배터리 재료', '분리막', 'Whatman', 'Celgard', '코인셀 케이스', '바인더', 'PVDF', '도전재', '집전체', '전해질 염', '고순도 용매'],
        'furnace':    ['전기로', '소성로', '열처리로', '하소', '소결', '어닐링', '실험실 퍼니스', '고온로', '열처리 장비', 'furnace'],
        'drying':     ['건조기', '실험실 오븐', '드라이오븐', '시료 건조', '랩 오븐', '건조 장비', 'oven'],
        'distill':    ['증류', '농축', '용매 회수', '증류·농축 장비'],
        'incubator':  ['인큐베이터', '배양기', '항온배양기', '세포배양', '미생물 배양', 'incubator', '배양 장비'],
        'waterbath':  ['항온수조', '워터배스', '항온조', '실험실 수조', 'bath'],
        'chamber':    ['항온항습기', '환경챔버', '온습도 챔버', '신뢰성시험', '환경시험기', '시험 챔버'],
        'sterilizer': ['오토클레이브', '멸균기', '고압증기멸균', '실험실 멸균', '스팀멸균기', 'autoclave', '배지 멸균', '기구 멸균'],
        'mixing':     ['믹싱', '교반·분쇄', '실험실 교반·분쇄 장비'],
        'pellet':     ['펠릿프레스', '압편기', '시료 압편', 'KBr 펠릿', 'IR 시료 전처리', 'XRD 분말 성형', '유압프레스', '시료 전처리 장비', '분말 성형', 'pellet press'],
        'die':        ['펠릿 다이', '성형 몰드', 'KBr 다이', 'IR 펠릿 몰드', 'XRD 시료 다이', '분말 성형 다이', '압편 몰드', '시료 전처리', '다이 세트', 'pellet die'],
        'slicer':     ['전극 슬라이서', '극편 펀칭', '코인셀 전극', '분리막 타발', '전극 타발기', '시료 전처리', 'electrode slicer', '전극 커터'],
        'vacuumpump': ['진공펌프', '진공도', '실험실 진공', '진공 배기', '도달압력', 'vacuum pump'],
        'fumehood':   ['실험실 안전 장비', '실험실 환기·안전'],
        'measuring':  ['측정기기', '계측기', '실험실 측정', '정밀 측정'],
        'peri':  ['연동펌프', '페리스탈틱펌프', '정량펌프', '튜빙펌프', '실험실 펌프', '호스펌프', '이송펌프', '도징펌프', '유량 펌프', '무오염 이송'],
        'syr':   ['시린지펌프', '미량주입', '정량주입', '실험실 펌프', '주사기펌프', '마이크로 유량', '정밀주입', '미세유체', '인퓨전 펌프', '약액 주입'],
        'gear':  ['기어펌프', '정량이송', '무맥동 펌프', '실험실 펌프', '마이크로 기어펌프', '고점도 이송', '케미컬 이송', '정밀 이송', '연속 이송', '소형 정량펌프'],
        'ex':    ['방폭펌프', '연동펌프', '방폭 인증', '정량펌프', 'ATEX', '방폭 모터', '위험물 이송', '용제 이송', '방폭형 펌프', '산업 방폭'],
        'head':  ['펌프헤드', '연동펌프 헤드', '튜브 카세트', '멀티채널 헤드', '교체 헤드', '실리콘 튜브', '펌프 부속', '카트리지 헤드', '이지로드 헤드', '헤드 교환'],
        'oem':   ['OEM 펌프', '펌프 모듈', '장비 내장 펌프', '소형 펌프', '임베디드 펌프', '모듈형 펌프', '장비 조립용 펌프', '스텝모터 펌프', '커스텀 펌프', '내장형 정량펌프'],
        'mfc':   ['질량유량계', 'MFC', '유량컨트롤러', '가스 유량 제어', 'sccm', '매스플로우', '유량 측정', '가스 혼합', '유량 셋포인트', '가스 컨트롤러'],
        'std':   ['질량유량계', 'MFC', '유량컨트롤러', '가스 유량 제어', 'sccm', '매스플로우', '유량 측정', '가스 혼합', '질소 유량', '아르곤 유량'],
        'hp':    ['고압 MFC', '질량유량계', '가스 유량 제어', '고압 가스', '매스플로우', '고압 유량', '수소 유량', '고압 배관', 'sccm', '유량컨트롤러'],
        'corr':  ['내부식 MFC', '부식성 가스', '질량유량계', '특수가스 MFC', '반도체 특수가스', '내화학 유량계', '매스플로우', '염소 가스', 'sccm', '유량컨트롤러'],
        'dual':  ['양방향 MFC', '질량유량계', '유량 제어', '매스플로우', '압력 겸용', '유량 압력 동시', 'sccm', '가스 제어', '유량컨트롤러', '듀얼밸브 MFC'],
        'press': ['압력 컨트롤러', '배압 레귤레이터', 'BPR', '압력 제어', '전자식 압력', '압력 조절기', '진공 압력', '레귤레이터', '압력 셋포인트', '가스 압력 제어'],
        'vac':   ['진공 공정', '질량유량계', '반도체 공정 가스', '진공 유량', 'CVD 가스', '공정 가스 제어', '매스플로우', '저압 유량', 'sccm', '유량컨트롤러'],
        'electrode': ['전기화학', '전극', '수전해', '전기화학 셀'],
        'catalyst':  ['CO2 환원', 'CO2RR', '전기화학 촉매', 'GDE', '가스확산전극', '촉매 잉크', '수전해 촉매', '전극 촉매'],
        'material':  ['전기화학 재료', '수전해', '전해조 소재'],
        'accessory': ['전기화학 소모품', '셀 부속', '셀 액세서리'],
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
                 'prep': '시료 전처리',
                 'vacuum': '진공', 'pump': '펌프', 'gas': '가스유량 MFC', 'echem': '전기화학', 'safety': '안전·측정'}

    # 네거티브 규칙 — 제목이 왼쪽 패턴이면 오른쪽 어휘(소문자 부분일치)를 검색 텍스트·키워드에서 제거
    NEG_RULES = [
        (re.compile(r'데시케이터|Desiccator', re.I),
         ['인큐베이터', '배양', 'incubator', '세포', '미생물']),
        (re.compile(r'클린벤치|크린벤치|무균|Biosafety|Clean\s*Bench|Laminar', re.I),
         ['흄후드', '퓸후드', 'fume', '배기', '국소배기']),
        (re.compile(r'흄\s*후드|흄후드|암후드|Fume\s*Hood|Lab\s*Hood', re.I),
         ['클린벤치', '크린벤치', '무균', 'bsc', 'laminar']),
        (re.compile(r'콜로니|Colony|라이트\s*박스|확대경', re.I),
         ['흄후드', '퓸후드', 'fume', '클린벤치', '크린벤치', '무균', 'bsc', '배기']),
    ]

    # 검색 동의어 그룹 — 그룹 내 단어가 하나라도 있으면 나머지도 data-k에 추가 (검색 리콜 확대)
    SYN_GROUPS = [
        ['퍼니스', '전기로', '소성로', '열처리로', '소결로', '하소로', 'furnace'],
        ['튜브퍼니스', '관상로', '튜브 퍼니스', 'tube furnace'],
        ['머플로', '박스퍼니스', '박스로', '머플 퍼니스'],
        ['건조기', '오븐', '드라이오븐', 'oven'],
        ['진공건조기', '진공오븐', '진공 건조'],
        ['열풍건조기', '열풍 오븐', '강제순환 건조기', '컨벡션 오븐'],
        ['항온수조', '워터배스', '항온조'],
        ['칠러', '냉각순환수조', '저온순환수조', 'chiller'],
        ['인큐베이터', '배양기', 'incubator'],
        ['진탕배양기', '쉐이킹 인큐베이터', '셰이킹 인큐베이터', '진탕 배양'],
        ['오토클레이브', '멸균기', 'autoclave', '고압증기멸균'],
        ['흄후드', '퓸후드', 'fume hood', '배기 후드', '국소배기'],
        ['클린벤치', '무균작업대', 'BSC', '무균 벤치'],
        ['교반기', '스터러', 'stirrer'],
        ['오버헤드 교반기', '임펠러 교반기', 'overhead stirrer'],
        ['마그네틱 교반기', '자석 교반기', 'magnetic stirrer'],
        ['핫플레이트', '가열교반기', 'hotplate'],
        ['볼밀', '분쇄기', '밀링', '그라인더', 'ball mill'],
        ['호모게나이저', '균질기', 'homogenizer'],
        ['회전증발농축기', '로터리증발기', '에바포레이터', 'evaporator', '감압농축'],
        ['로터리베인', '유회전 펌프', '오일 진공펌프'],
        ['다이어프램 펌프', '다이아프램 펌프', '무오일 펌프', '오일프리 펌프'],
        ['연동펌프', '페리스탈틱펌프', '튜빙펌프', '호스펌프', '정량펌프', 'peristaltic'],
        ['시린지펌프', '주사기펌프', '실린지펌프', 'syringe'],
        ['기어펌프', '마이크로기어펌프'],
        ['질량유량계', 'mfc', '유량컨트롤러', '매스플로우', 'mass flow'],
        ['압력컨트롤러', '배압레귤레이터', 'bpr', '압력제어'],
        ['전자저울', '분석저울', '정밀저울', '실험실 저울', 'balance'],
        ['수분측정기', '수분계', '수분 분석'],
        ['초음파세척기', '소니케이터', 'sonicator'],
        ['원심분리기', 'centrifuge'],
        ['기준전극', 'reference electrode'],
        ['상대전극', 'counter electrode', '백금전극'],
        ['작업전극', 'working electrode', '유리탄소전극'],
        ['이온교환막', '나피온', '멤브레인', 'nafion'],
        ['카본페이퍼', '가스확산층', 'gdl', '카본펠트'],
        ['전극 홀더', '전극 클램프'],
        ['전극 연마', '연마 패드', '알루미나 분말'],
    ]


    # ---- SQL(SSOT) 가격 폴백: 상세페이지에 가격이 없는 카드용 ----
    def _sql_price_rows():
        txt = read(os.path.join(ROOT_DIR, 'rndsetup_products.sql'))
        out = []
        for mm in re.finditer(r"VALUES \('([^']*)',\d+,'([^']*)','[^']*','[^']*','([^']*)','([^']*)','([^']*)',", txt):
            sku, brand, daebun, sobun, model = mm.groups()
            pm = re.search(r"'ea',(?:\d+|NULL),(\d+)", txt[mm.end():mm.end() + 500])
            if pm:
                out.append((sku.upper(), brand, sobun, model.upper(), int(pm.group(1))))
        return out

    SQL_ROWS = _sql_price_rows()

    def _sql_min(pred):
        vals = [r[4] for r in SQL_ROWS if pred(r) and r[4] >= 10000]
        return min(vals) if vals else None

    # 슬러그 → SQL 매핑 (SH=sobun 정규식, Alicat=model 프리픽스, Gaoss=sobun 일치)
    SLUG_SQL = {
        'rotary-batch-300':      ('SH Scientific', 'sobun', r'회전튜브전기로 300mm \(Rotation'),
        'rotary-batch-3zone':    ('SH Scientific', 'sobun', r'300mm x 3zone'),
        'rotary-kiln-1200-2zone':('SH Scientific', 'sobun', r'1200°C 2 zone 연속식'),
        'rotary-kiln-1200-3zone':('SH Scientific', 'sobun', r'1200°C 3 zone 연속식'),
        'elevator-1200':         ('SH Scientific', 'sobun', r'1200℃ 전기로 , Elevator'),
        'elevator-1500':         ('SH Scientific', 'sobun', r'1500℃ 전기로 , Elevator'),
        'elevator-1800':         ('SH Scientific', 'sobun', r'1800℃ 전기로 , Elevator'),
        'gas-flow-package':      ('SH Scientific', 'sobun', r'1200°C Gas Flow Package'),
        'gas-flow-package-600mm':('SH Scientific', 'model', r'^SH-CVD-\d+TG600'),
        'tube-1500':             ('SH Scientific', 'sobun', r'1500°C Gas Flow Package'),
        'tube-1800':             ('SH Scientific', 'sobun', r'1800°C Gas Flow Package'),
        'vacuum-muffle-1200-quartz': ('SH Scientific', 'sobun', r'석영챔버'),
        'vacuum-muffle-1500':    ('SH Scientific', 'sobun', r'1500℃ 전기로 with 진공'),
        'vacuum-muffle-1900':    ('SH Scientific', 'sobun', r'1900 ?℃ 전기로 with 진공'),
        'muffle-1050':           ('SH Scientific', 'sobun', r'ECO 1050'),
        'steam-generator':       ('SH Scientific', 'sobun', r'스팀제너레이터'),
        'distillation':          ('SH Scientific', 'sobun', r'숏패스'),
        'gas-flow-3zone':        ('SH Scientific', 'model', r'^SH-CVD-\d+TG200-3'),
        'muffle-1200':           ('SH Scientific', 'sobun', r'^1200℃ 전기로$'),
        'muffle-1500':           ('SH Scientific', 'sobun', r'^1500 ?℃ 전기로$'),
        'muffle-1700':           ('SH Scientific', 'sobun', r'^1700 ?℃ 전기로$'),
        'muffle-1800':           ('SH Scientific', 'sobun', r'^1800 ?℃ 전기로$'),
        'muffle-1900':           ('SH Scientific', 'sobun', r'^1900 ?℃ 전기로$'),
        'mc-series':   ('Alicat', 'model', r'^MC\b'),
        'mcs-series':  ('Alicat', 'model', r'^MCS'),
        'mcq-series':  ('Alicat', 'model', r'^MCQ'),
        'mcd-series':  ('Alicat', 'model', r'^MCD'),
        'mct-series':  ('Alicat', 'model', r'^MCT'),
        'bioc-series': ('Alicat', 'model', r'^BIOC'),
        'mcv-sff-series': ('Alicat', 'model', r'^(MCV|MCE)'),
        'pc-series':   ('Alicat', 'model', r'^PC\b'),
        'pcd-series':  ('Alicat', 'model', r'^PCD'),
        'bpr':         ('Alicat', 'model', r'^BPR|BPR'),
        'basis-series':('Alicat', 'model', r'^BASIS'),
        'reference-electrode': ('Gaoss Union', 'sobun', r'^기준전극$'),
        'rhe':                 ('Gaoss Union', 'sobun', r'^가역수소전극$'),
        'counter-electrode':   ('Gaoss Union', 'sobun', r'^상대전극$'),
        'working-electrode':   ('Gaoss Union', 'sobun', r'^작업전극$'),
        'rde-rrde':            ('Gaoss Union', 'sobun', r'^회전전극$'),
        'electrode-holder':    ('Gaoss Union', 'sobun', r'클램프·홀더'),
        'electrode-polishing': ('Gaoss Union', 'sobun', r'연마용품'),
        'echem-materials':     ('Gaoss Union', 'sobun', r'^전기화학 재료$'),
        'co2rr-catalyst':      ('Gaoss Union', 'sobun', r'^CO2RR 촉매$'),
        'battery-test-cell':   ('Gaoss Union', 'sobun', r'배터리 테스트 셀'),
        'glass-cell':          ('Gaoss Union', 'sobun', r'^단실 유리 전해셀$'),
        'membrane-cell':       ('Gaoss Union', 'sobun', r'^격막 교환형 전해셀$'),
        'quartz-cell':         ('Gaoss Union', 'sobun', r'부식 시험·석영 전해셀'),
    }

    def sql_price_for(href, model_txt, data_text):
        seg = [x for x in href.strip('/').split('/') if x]
        page_slug = seg[-1] if seg else ''
        # SQL에 대응 상품이 없는 페이지: 잘못된 근사 매칭 방지 (견적 유지)
        if page_slug in ('rotary-tube-furnace', 'rotary-tube-furnace-pro', 'vacuum-tube-turnkey') \
                or page_slug.startswith(('pellet-press-yp', 'cylindrical-die-hmy')):
            return None
        rule = SLUG_SQL.get(page_slug)
        if rule:
            b, field, rx = rule
            fi = 2 if field == 'sobun' else 3
            crx = re.compile(rx)
            v = _sql_min(lambda r: r[1] == b and crx.search(r[fi]))
            if v:
                return v
        # 코드 프리픽스 매칭 (SH-FU-…, SH-CVD-…, JP300S 등)
        cand = set()
        for src in (model_txt or '', data_text or ''):
            for tok in re.findall(r"[A-Za-z]{1,4}[A-Za-z0-9]*-[A-Za-z0-9.\-]{2,}|[A-Za-z]{2,5}\d{2,4}[A-Za-z]*", src.upper()):
                if len(tok) >= 5:
                    cand.add(tok)
        for c in sorted(cand, key=len, reverse=True):
            v = _sql_min(lambda r: r[0].startswith(c) or r[3].startswith(c))
            if v:
                return v
        return None
    # ---- SQL 가격 폴백 끝 ----

    cards = []
    all_keys, all_kws = [], set()
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
            # 카탈로그 제외 목록 — 중복 카드 (연속식 회전킬른 RKG600/900과 동일 제품군, 구 모델명 페이지)
            if href in ('/brands/sh-scientific/rotary-tube-furnace/', '/brands/sh-scientific/rotary-tube-furnace-pro/'):
                continue
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
            _fam = allprod_fam(href, cat)
            if _fam:
                sub_tokens.append(_fam)
            keys = ' '.join([title, model, label, slug, kw_raw.group(1) if kw_raw else '']).lower()
            for _rx, _al in ALLPROD_KEY_ALIASES_RX:
                if _rx.search(href):
                    keys += ' ' + _al.lower()

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
            if price is None:
                price = sql_price_for(href, model, kw_raw.group(1) if kw_raw else '')
            kws = get_keywords(block, title, _sub1 or cat, CAT_LABEL.get(cat, ''))
            # 네거티브 규칙: 제목 기준으로 명백히 다른 유형의 어휘 제거 (원본 data-use/text가 제품군 공통 어휘를 달고 있는 경우)
            _bans = []
            for _rx, _bl in NEG_RULES:
                if _rx.search(title):
                    _bans += _bl
            if _bans:
                kws = [w for w in kws if not any(b in w.lower() for b in _bans)]
            # 동의어 그룹 확장 — 방아쇠는 카드 "원본" 텍스트(제목·모델·data-text·스펙)만.
            # 사전이 추가한 일반어가 다른 그룹을 연쇄 발화시키는 2차 오염을 막는다.
            _syn_src = (keys + ' ' + ' '.join((k + ' ' + v) for k, v in specs if v and v != '상세 참조')).lower()
            _extra = []
            for _grp in SYN_GROUPS:
                if any(g.lower() in _syn_src for g in _grp):
                    _extra += [g for g in _grp if g.lower() not in _syn_src]
            # data-k(검색 텍스트) 최종 조립: 원본 + #키워드 + 제품군 사전 전체 + 카테고리명 + 스펙 + 동의어
            _dict_kw = KW_BY_SUBCAT.get(_sub1 or cat, [])
            if _bans:
                _dict_kw = [w for w in _dict_kw if not any(b in w.lower() for b in _bans)]
                _extra = [w for w in _extra if not any(b in w.lower() for b in _bans)]
            keys = ' '.join(dict.fromkeys(' '.join(
                [keys]
                + [w.lower() for w in kws]
                + [w.lower() for w in _dict_kw]
                + [CAT_LABEL.get(cat, '').lower()]
                + [(k + ' ' + v).lower() for k, v in specs if v and v != '상세 참조']
                + [w.lower() for w in _extra]
            ).replace('\u00b7', ' ').split()))
            if _bans:
                keys = ' '.join(w for w in keys.split() if not any(b in w for b in _bans))
            if not model:
                _rep = next((v for k, v in specs if k == '대표 모델'), '')
                model = _rep or '옵션 구성 · 상세 참조'

            sp_html = ''.join(
                f'<div class="r"><span class="k">{escape(k)}</span><span class="v">{escape(v)}</span></div>'
                for k, v in (specs + [('사양', '상세 참조')] * 3)[:3])
            if price and slug in ('gaossunion', 'hefei', 'aida'):   # 해외 발주 — 3% 상시 할인 대상 아님
                pr_html = (f'<div class="pc-pr">'
                           f'<span class="s">최소 {{:,}}원부터 <i class="vat">VAT 별도</i></span></div>').format(price)
            elif price:
                sale = int(price * 0.97) // 10000 * 10000
                pr_html = (f'<div class="pc-pr"><span class="o">정가 {{:,}}원~</span>'
                           f'<span class="s">최소 {{:,}}원부터 <i class="vat">VAT 별도</i></span></div>').format(price, sale)
            else:
                pr_html = '<div class="pc-pr"><span class="q">가격 견적 문의 <i class="vat">VAT 별도</i></span></div>'
            kw_html = ('<div class="pc-kw">' + ' '.join('#' + escape(w) for w in kws) + '</div>') if kws else '<div class="pc-kw"></div>'

            all_keys.append(keys)
            all_kws.update(kws)
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
        # h1 결과 헤드의 정적 카드 수 자동 갱신 (크롤러용 기본값 — JS가 런타임 갱신)
        page2 = re.sub(r'(실험장비 통합 카탈로그 — 전체 제품 <b>총 )\d+(개</b>)',
                       r'\g<1>%d\g<2>' % len(cards), page2)
        page2 = re.sub(r'(통합 카탈로그(?: —)? )\d+(종)', r'\g<1>%d\g<2>' % len(cards), page2)
        write(target, page2)
        # 홈 신뢰 밴드 자동 갱신 — 카탈로그 종수 + 취급 SKU(SQL 행 수, 백 단위 버림)
        home_p = os.path.join(ROOT_DIR, 'index.html')
        if os.path.exists(home_p):
            hh = read(home_p)
            h2 = re.sub(r'(<div class="v">)[\d,]+(종</div><div class="l">통합 카탈로그)',
                        r'\g<1>%d\g<2>' % len(cards), hh)
            sku = sum(1 for _ln in open(os.path.join(ROOT_DIR, 'rndsetup_products.sql'), encoding='utf-8') if 'INSERT INTO' in _ln)
            h2 = re.sub(r'(<div class="v">)[\d,]+\+(</div><div class="l">취급 SKU)',
                        r'\g<1>{:,}+\g<2>'.format(sku // 100 * 100), h2)
            if h2 != hh:
                write(home_p, h2)
        # 검색 자동완성 어휘 — 제품군을 명확히 구분하는 대표 키워드만 (동의어·중복 배제)
        CANON_TERMS = [
            # (대표 키워드, [동의어·별칭]) — 별칭 입력 시에도 대표 키워드를 제안
            ('튜브퍼니스', ['관상로', '튜브로', 'tube furnace', '퍼니스', '전기로']),
            ('머플로', ['박스퍼니스', '박스로', '회화로', 'muffle', '전기로', '퍼니스']),
            ('진공 전기로', ['진공로', 'vacuum furnace', '진공퍼니스']),
            ('회전킬른', ['로터리킬른', '회전 튜브로', 'rotary kiln', '킬른']),
            ('엘리베이터 전기로', ['엘레베이터', '승강로', 'lift furnace']),
            ('CVD', ['증착', '화학기상증착', '씨브이디']),
            ('스팀 제너레이터', ['수증기 발생기', 'steam', '스팀발생기']),
            ('열풍건조기', ['건조오븐', '오븐', 'dry oven', '드라이오븐']),
            ('진공건조기', ['진공오븐', 'vacuum oven', '진공 건조 오븐']),
            ('회전증발농축기', ['로터리 증발기', 'rotary evaporator', '에바포레이터', '증발농축기']),
            ('숏패스 증류', ['분자증류', 'short path', '증류장치']),
            ('인큐베이터', ['배양기', 'incubator']),
            ('CO2 배양기', ['이산화탄소 배양기', 'CO2 인큐베이터', '세포배양기']),
            ('진탕배양기', ['쉐이킹 인큐베이터', 'shaker', '진탕기', '쉐이커']),
            ('데시케이터', ['desiccator', '건조 보관함', '제습보관함']),
            ('항온수조', ['워터배스', 'water bath', '수조', '배스']),
            ('칠러', ['냉각수 순환장치', 'chiller', '냉각기', '순환냉각기']),
            ('항온항습기', ['항온항습 챔버', 'chamber', '챔버']),
            ('오토클레이브', ['멸균기', '고압멸균기', 'autoclave']),
            ('교반기', ['스터러', 'stirrer', '오버헤드 교반기', '임펠러']),
            ('핫플레이트', ['가열판', 'hot plate', '마그네틱 스터러', '히팅플레이트']),
            ('볼밀', ['ball mill', '분쇄기', '유성밀', '볼 밀']),
            ('행성믹서', ['플래니터리 믹서', 'planetary mixer', '탈포믹서', '자전공전 믹서']),
            ('3롤밀', ['삼롤밀', 'three roll mill', '롤밀']),
            ('펠릿프레스', ['압편기', 'pellet press', '펠릿 프레스', '유압프레스', '시료 압편기']),
            ('펠릿 다이', ['성형 몰드', 'pellet die', 'KBr 다이', '펠릿몰드', '압편 몰드']),
            ('제트밀', ['jet mill', '기류분쇄기']),
            ('진공펌프', ['vacuum pump', '로터리펌프', '진공 펌프']),
            ('흄후드', ['흄 후드', 'fume hood', '배기후드', '후드']),
            ('클린벤치', ['무균작업대', 'clean bench', '크린벤치']),
            ('전자저울', ['저울', 'balance', '정밀저울', '분석저울']),
            ('수분측정기', ['수분계', 'moisture analyzer', '수분 분석기']),
            ('정량펌프', ['연동펌프', '페리스탈틱 펌프', 'peristaltic', '도징펌프', '튜브펌프']),
            ('시린지펌프', ['실린지펌프', 'syringe pump', '주사기펌프', '시린지 펌프']),
            ('기어펌프', ['gear pump', '기어 펌프', '마이크로 기어펌프']),
            ('방폭펌프', ['방폭', 'explosion proof', 'ATEX']),
            ('펌프헤드', ['pump head', '펌프 헤드', '헤드']),
            ('OEM 펌프', ['오이엠 펌프', '내장형 펌프']),
            ('질량유량계', ['유량계', '유량 컨트롤러', 'mass flow', '가스유량계']),
            ('MFC', ['질량유량계', 'mass flow controller', '엠에프씨']),
            ('압력 컨트롤러', ['압력 조절기', 'pressure controller', '압력계']),
            ('BPR', ['배압 레귤레이터', 'back pressure', '배압']),
            ('기준전극', ['레퍼런스 전극', 'reference electrode', 'Ag/AgCl', '은염화은', '칼로멜']),
            ('상대전극', ['카운터 전극', 'counter electrode', '백금 전극', '백금선']),
            ('작업전극', ['working electrode', 'GC 전극', '유리탄소 전극', '글래시카본']),
            ('RHE', ['수소 기준전극', '가역수소전극']),
            ('RDE', ['회전 디스크 전극', 'RRDE', '회전전극', '회전 원판 전극']),
            ('전해셀', ['전기화학 셀', 'H셀', 'H-셀', '전해조', 'electrochemical cell', '3전극 셀']),
            ('CO2RR 촉매', ['CO2 환원 촉매', '이산화탄소 환원', 'CO2RR']),
            ('이온교환막', ['나피온', 'Nafion', '멤브레인', '분리막', '양성자교환막']),
            ('카본페이퍼', ['탄소종이', 'carbon paper', 'GDL', '가스확산층', '카본클로스']),
            ('배터리 테스트 셀', ['코인셀', '배터리셀', '테스트셀', 'in-situ 셀', '광학창 셀']),
            ('삼흥에너지', ['삼흥', 'SH Scientific']),
            ('리드플루이드', ['LeadFluid', '리드 플루이드']),
            ('Alicat', ['알리캣', '앨리캣', '알리캇']),
            ('가오스유니온', ['Gaoss', '가오스', 'Gaoss Union']),
        ]
        _sug = []
        for _item in CANON_TERMS:
            _w, _al = (_item if isinstance(_item, tuple) else (_item, []))
            _ws = _w.lower().split()
            _n = sum(1 for _k in all_keys if all(x in _k for x in _ws))
            if _n > 0:
                _sug.append([_w, _n, _al] if _al else [_w, _n])
        _sug.sort(key=lambda x: (-x[1], x[0]))
        write(os.path.join(ROOT_DIR, 'assets', 'search-terms.json'),
              json.dumps(_sug, ensure_ascii=False, separators=(',', ':')))
        print(f'  검색 자동완성 어휘: {{}}개 (assets/search-terms.json)'.format(min(len(_sug), 200)))
        print(f'  전 제품 통합 카탈로그: {{}}개 표준 카드 주입 (product/index.html)'.format(len(cards)))

# ============================================================================
# 제품 상세페이지 데이터 주도 생성 — SSOT = _build/products/<brand>.json
# ----------------------------------------------------------------------------
# 신규 상세페이지 = JSON 1건 추가 + 빌드. 손 HTML 작성 금지.
# 디자인 수정 = assets/detail.css 또는 아래 _pp_render() 템플릿 1곳.
# 레이아웃 표준(CLAUDE.md 4.5):
#   크럼 -> h1+영문명 -> 대표사진 -> 정답블록 -> 모델별 가격표 -> 상세 -> 관련링크/CTA
# ============================================================================

PP_DIR = 'products'          # _build/products/
PP_CSS = '<link rel="stylesheet" href="/assets/detail.css">'


def _pp_text(s):
    """마크업 허용 필드에서 순수 텍스트만 뽑는다(메타·JSON-LD용)."""
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def _pp_ctbar():
    p = os.path.join(SCRIPT_DIR, 'partial_ctbar.html')
    return read(p).strip() if os.path.exists(p) else ''


def _pp_img(brand, fn):
    if fn.startswith('/') or fn.startswith('http'):
        return fn
    return brand.get('img_dir', '/img/%s/' % brand['slug']).rstrip('/') + '/' + fn


def _pp_collapse(head, rows):
    """모든 행에서 값이 같은 열은 표에서 빼고 '공통' 줄로 접는다(동일 내용 표 합치기).
    반환: (남은 head, 남은 rows, [(열이름, 공통값), ...])"""
    if not head or len(rows) < 2:
        return head, rows, []
    same = []
    for c in range(1, len(head)):          # 0열(식별자)은 항상 남긴다
        vals = {r[c] for r in rows if c < len(r)}
        if len(vals) == 1:
            same.append(c)
    if not same:
        return head, rows, []
    common = [(head[c], rows[0][c]) for c in sorted(same)]
    keep = [c for c in range(len(head)) if c not in same]
    return ([head[c] for c in keep],
            [[r[c] for c in keep if c < len(r)] for r in rows],
            common)


def _pp_table(rows, head=None, cls='pkg-tbl', minw=None):
    """rows = [[셀, 셀, ...], ...] — 셀 안 마크업은 그대로 통과(작성자 책임)."""
    st = ' style="min-width:%dpx"' % minw if minw else ''
    out = ['<div class="pkg-tblwrap"><table class="%s"%s>' % (cls, st)]
    if head:
        out.append('<thead><tr>' + ''.join('<th>%s</th>' % h for h in head) + '</tr></thead>')
    out.append('<tbody>')
    for r in rows:
        if head:
            out.append('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>')
        else:                                    # 2열 = 라벨/값 사양표
            out.append('<tr><th>%s</th><td>%s</td></tr>' % (r[0], r[1]))
    out.append('</tbody></table></div>')
    return ''.join(out)


# 제조사 제품 페이지에서 반드시 옮겨 담아야 하는 항목 (원문 수집 체크리스트).
# (JSON 키, 사람이 읽는 이름, 화학품 전용인가)
PP_REQUIRED = [
    ('answer',   '정답블록',        False),
    ('images',   '대표사진',        False),
    ('features', '특징',            False),
    ('specs',    '사양(물성)',      False),
    ('variants', '규격 비교표',      False),
    ('buybox',   '주문정보(가격)',  False),
    ('faq',      'FAQ',            False),
    ('source',   '제조사 원문 출처', False),
    ('safety',   '안전정보(GHS)',   True),
]
# 이 낱말이 카테고리·이름에 있으면 화학품으로 보고 안전정보를 필수로 요구한다
# 화학물질 판정 — 안전 정보(GHS)를 요구할 대상인지 가른다.
# category 는 "배터리 재료 · 리튬이온 전해액" 처럼 대분류·소분류가 붙어 있어서
# 소분류(· 뒤)만 본다. 대분류의 '재료' 때문에 분리막·케이스까지 걸리던 것을 막는다.
PP_CHEM_HINTS = ('전해액', '용액', '시약', '촉매', '분말', '슬러리',
                 '바인더', '용매', '염', '첨가제', '전구체', '활물질')
PP_NONCHEM_HINTS = ('분리막', '케이스', '원판', '부품', '지그', '장비', '치구',
                    '집전체', '테이프', '펀치', '몰드')


def _pp_is_chem(p):
    cat = p.get('category', '')
    sub = (cat.split('·')[-1] if '·' in cat else cat).replace(' ', '')
    t = (sub + p.get('name', '')).replace(' ', '')
    if any(k in t for k in PP_NONCHEM_HINTS):
        return False
    return any(k in t for k in PP_CHEM_HINTS)


def _pp_audit(bslug, p):
    """제조사 원문에서 안 옮긴 항목을 찾아 이름 목록으로 돌려준다."""
    chem = _pp_is_chem(p)
    miss = []
    for key, label, chem_only in PP_REQUIRED:
        if chem_only and not chem:
            continue
        v = p.get(key)
        if key == 'buybox':
            # "buybox": []  = 가격 미공개(견적 전용)를 의도적으로 표시한 것 -> 통과
            if key not in p:
                miss.append(label + ' — 가격을 넣거나 "buybox": [] 로 견적 전용 표시')
            continue
        if not v:
            miss.append(label)
        elif key == 'specs' and len(v) < 3:
            miss.append(label + '(3행 미만)')
        elif key == 'features' and len(v) < 2:
            miss.append(label + '(2개 미만)')
        elif key == 'faq' and len(v) < 2:
            miss.append(label + '(2개 미만)')
    return miss


# GHS 그림문자 — 코드는 UN GHS 표준 번호, 이름은 KOSHA 표기.
# 아이콘은 /img/ghs/<code>.png 한 벌만 두고 전 브랜드가 같이 쓴다.
PP_GHS = {
    'ghs01': '폭발성', 'ghs02': '인화성', 'ghs03': '산화성',
    'ghs04': '고압가스', 'ghs05': '부식성', 'ghs06': '급성 독성',
    'ghs07': '경고', 'ghs08': '건강 유해성', 'ghs09': '수생환경 유해성',
}


def _pp_safety(sf):
    """안전 정보 — 제조사 표를 라벨·값 그대로 옮겨 싣는 자리.
    번역·요약·경고문 추가 금지. rows 는 제조사 표기 순서·문구 그대로 둔다."""
    out = ['<h2 class="pkg-h" style="margin-top:26px">%s</h2>'
           % escape(sf.get('heading', '안전 정보'))]
    if sf.get('lead'):
        out.append('<p class="pkg-note" style="margin:0 0 10px">%s</p>' % sf['lead'])
    rows = list(sf.get('rows') or [])
    pics = sf.get('pictograms') or []
    if pics:
        cells = ''.join(
            '<figure class="ghs"><img src="/img/ghs/%s.png" alt="%s" loading="lazy">'
            '<figcaption>%s</figcaption></figure>' % (c, escape(PP_GHS.get(c, c)), escape(PP_GHS.get(c, c)))
            for c in pics)
        rows = [[lb, '<div class="ghs-row">%s</div>' % cells if v == '@image' else v]
                for lb, v in rows]
    elif sf.get('image'):
        rows = [[lb, ('<img src="%s" alt="%s" style="max-width:100%%;display:block">'
                      % (sf['image'], escape(sf.get('image_alt', '제조사 표기 그림문자'))))
                 if v == '@image' else v] for lb, v in rows]
    if rows:
        out.append(_pp_table(rows))
    if sf.get('note'):
        out.append('<p class="pkg-note">%s</p>' % sf['note'])
    return ''.join(out)


PP_PAPER_MAX = 3          # 논문은 최대 3편. 없으면 섹션을 아예 내지 않는다.

# 저널 등급 — 논문은 유명 저널 위주로만 싣는다.
#   T1 = 최상위(우선 수록) · T2 = 허용 · 그 외 = 제외
#   (T1/T2가 하나도 없을 때만 등급 밖 저널을 쓰고, 빌드가 교체하라고 warn 한다)
# 정식명과 표준 약어를 함께 적는다. 판정은 부분일치가 아니라 정규화 후 완전일치다
#   ("chem" 이 "electrochem" 에 걸리는 사고를 막기 위함).
# 저널 이름은 JSON 의 journal 값에서 <i>…</i> 안에 적는다.
PP_JOURNAL_T1 = {
    'nature', 'science', 'science advances', 'sci adv',
    'nature energy', 'nat energy', 'nature materials', 'nat mater',
    'nature nanotechnology', 'nat nanotechnol', 'nature catalysis', 'nat catal',
    'nature communications', 'nat commun', 'nature chemistry', 'nat chem',
    'joule', 'chem', 'matter', 'pnas', 'proc natl acad sci',
    'proceedings of the national academy of sciences',
    'journal of the american chemical society', 'j am chem soc', 'jacs',
    'angewandte chemie', 'angewandte chemie international edition', 'angew chem int ed',
    'advanced materials', 'adv mater', 'advanced energy materials', 'adv energy mater',
    'energy and environmental science', 'energy environ sci',
    'acs energy letters', 'acs energy lett', 'nano letters', 'nano lett', 'acs nano',
    'acs central science', 'acs cent sci', 'acs catalysis', 'acs catal',
    'chemical science', 'chem sci', 'national science review', 'natl sci rev',
    'research',
}
PP_JOURNAL_T2 = {
    'journal of power sources', 'j power sources',
    'electrochimica acta', 'electrochim acta',
    'journal of materials chemistry a', 'j mater chem a',
    'acs applied materials and interfaces', 'acs appl mater interfaces',
    'chemical engineering journal', 'chem eng j',
    'energy storage materials', 'energy storage mater',
    'small', 'carbon',
    'journal of the electrochemical society', 'j electrochem soc',
    'batteries and supercaps', 'chemsuschem',
    'scientific reports', 'sci rep',
    'journal of energy chemistry', 'j energy chem',
    'nano energy', 'advanced functional materials', 'adv funct mater',
    'advanced science', 'adv sci', 'green chemistry', 'green chem',
    'cell reports physical science', 'cell rep phys sci', 'infomat', 'ecomat',
    'journal of materials chemistry', 'j mater chem',
    'materials',
}


def _pp_journal_name(journal):
    """journal 값에서 저널명만 뽑아 정규화한다. <i>…</i> 우선, 없으면 첫 숫자 앞까지."""
    m = re.search(r'<i>(.*?)</i>', journal or '', re.S)
    t = m.group(1) if m else re.split(r'\d', re.sub(r'<[^>]+>', ' ', journal or ''))[0]
    t = t.replace('&amp;', '&').lower().replace('&', ' and ').replace('.', ' ')
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def _pp_journal_tier(journal):
    n = _pp_journal_name(journal)
    if n in PP_JOURNAL_T1:
        return 1
    if n in PP_JOURNAL_T2:
        return 2
    return 9


def _pp_pick_papers(items):
    """유명 저널 위주로 고른다. T1 -> T2 순, 최대 3편.
    T1/T2가 하나도 없을 때만 등급 밖 저널을 그대로 쓴다. (버린 목록, 등급밖 사용 여부) 함께 반환."""
    ranked = sorted(((_pp_journal_tier(it.get('journal', '')), i, it)
                     for i, it in enumerate(items)), key=lambda x: (x[0], x[1]))
    ok = [it for tier, _, it in ranked if tier <= 2]
    fallback = not ok
    keep = (ok if ok else [it for _, _, it in ranked])[:PP_PAPER_MAX]
    dropped = [it for it in items if it not in keep]
    return keep, dropped, fallback


def _pp_papers(pp):
    """관련 논문 — 논문 / 저널 / 링크 3열 고정. 최대 3편.
    근거(제품 코드가 논문에 나온 것)가 있으면 그 논문만 싣고, 하나도 없을 때에만
    같은 배합·같은 사양의 대표 논문으로 채운다."""
    items, _dropped, _fb = _pp_pick_papers(pp.get('items') or [])
    if not items:
        return ''
    rows = [[
        escape(it['title']),
        ' · '.join(x for x in [it.get('journal', ''), escape(it.get('authors', ''))] if x),
        ('<a href="https://doi.org/%s" target="_blank" rel="noopener">DOI ↗</a>' % it['doi'])
        if it.get('doi') else it.get('link', ''),
    ] for it in items]
    out = ['<h2 class="pkg-h" style="margin-top:26px">%s</h2>' % escape(pp.get('heading', '관련 논문')),
           _pp_table(rows, head=['논문', '저널', '링크'])]
    if pp.get('note'):
        out.append('<p class="pkg-note">%s</p>' % pp['note'])
    return ''.join(out)


def _pp_render(brand, p):
    """제품 1건 -> 상세페이지 HTML 전문."""
    bslug, bko = brand['slug'], brand.get('name_ko', brand['slug'])
    ben = brand.get('name_en', bko)
    hub = brand.get('hub', '/brands/%s/' % bslug)
    url = '/brands/%s/%s/' % (bslug, p['slug'])
    full = 'https://rndsetup.com' + url

    name, name_en = p['name'], p.get('name_en', '')
    cat = p.get('category', name)
    title = p.get('title') or '%s %s%s | 실험셋업연구소' % (
        bko, name, (' — ' + p['sub']) if p.get('sub') else '')
    desc = p.get('desc') or _pp_text(p.get('summary', ''))[:155]
    ogt = p.get('og_title') or '%s — %s 정품' % (name, bko)
    ogd = p.get('og_desc') or desc
    imgs = p.get('images', [])
    img1 = _pp_img(brand, imgs[0]) if imgs else ''
    ialt = p.get('image_alt') or '%s 제품 사진 (%s %s)' % (name, bko, ben)

    # ---------- head ----------
    h = ['<!DOCTYPE html>', '<html lang="ko">', '<head>',
         '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         '<title>%s</title>' % escape(title),
         '<meta name="description" content="%s">' % escape(desc),
         '<link rel="canonical" href="%s">' % full,
         '<meta property="og:type" content="product">',
         '<meta property="og:title" content="%s">' % escape(ogt),
         '<meta property="og:description" content="%s">' % escape(ogd),
         '<meta property="og:url" content="%s">' % full]
    if img1:
        h.append('<meta property="og:image" content="https://rndsetup.com%s">' % img1)
        h.append('<meta name="twitter:card" content="summary_large_image">')
        h.append('<meta name="twitter:image" content="https://rndsetup.com%s">' % img1)
    h.append('<meta name="twitter:title" content="%s">' % escape(ogt))
    h.append('<meta name="twitter:description" content="%s">' % escape(ogd))
    h.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    h.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    h.append('<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap" rel="stylesheet">')
    h.append('<link rel="stylesheet" href="/assets/site.css">')
    h.append(PP_CSS)
    h.append('</head>')

    # ---------- body ----------
    b = ['<body>', '<div id="pumplab-header"></div>']

    # 오른쪽 주문정보는 항상 낸다. 가격이 없으면 site.js 가 견적문의 창으로 렌더한다.
    b.append('<div class="buyrail"><div id="buybox" class="bb dt-buy" data-name="%s" data-models=\'%s\'></div></div>'
             % (escape(name), json.dumps(p.get('buybox') or [], ensure_ascii=False)))

    b.append('<section class="detail-top"><div class="wrap">')
    # 1. 크럼
    b.append('<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › <a href="%s">%s</a> › %s</div>'
             % (hub, escape(bko), escape(cat)))
    b.append('<div class="dt-grid">')
    # 3. 대표사진 (+썸네일)
    b.append('<div class="dt-col">')
    if img1:
        b.append('<div class="dt-img"><img src="%s" alt="%s" loading="lazy" '
                 'onerror="this.closest(\'.dt-img\').style.display=\'none\'"></div>' % (img1, escape(ialt)))
        if len(imgs) > 1:
            th = ['<div class="dt-thumbs">']
            for i, fn in enumerate(imgs, 1):
                src = _pp_img(brand, fn)
                th.append('<button type="button" data-src="%s" onclick="ppSwap(this)">'
                          '<img src="%s" alt="%s %d" loading="lazy" '
                          'onerror="this.parentElement.style.display=\'none\'"></button>'
                          % (src, src, escape('%s 제품 사진' % name), i))
            th.append('</div>')
            b.append(''.join(th))
            b.append('<script>function ppSwap(b){var i=b.closest(".dt-col").querySelector(".dt-img img");if(i)i.src=b.dataset.src;}</script>')
    b.append('</div>')
    # 2. h1 + 영문명 / 4. 정답블록
    b.append('<div class="dt-info">')
    b.append('<div class="dt-brand">%s</div>'
             % escape(bko if bko == ben else '%s · %s' % (bko, ben)))
    b.append('<h1 class="dt-name">%s</h1>' % escape(name))
    if name_en:
        b.append('<div class="dt-en">%s</div>' % escape(name_en))
    if p.get('sub'):
        b.append('<div class="dt-sub">%s</div>' % escape(p['sub']))
    if p.get('answer'):
        b.append('<p class="dt-ans">%s</p>' % p['answer'])
    if p.get('summary'):
        b.append('<p class="dt-sum">%s</p>' % p['summary'])
    b.append('<button type="button" class="qbtn" data-quote="%s %s">제품문의</button>' % (escape(bko), escape(name)))
    kw = p.get('keywords') or [['#' + bko, hub], ['#실험장비카탈로그', '/product/']]
    b.append('<div class="dt-kw">%s</div>' % ''.join('<a href="%s">%s</a>' % (hrf, escape(lb)) for lb, hrf in kw))
    b.append('</div></div></div></section>')

    # ---------- 본문 ----------
    b.append('<section class="pkg"><div class="wrap">')
    b.append('<a class="ds-back" href="%s">← %s</a>' % (hub, escape(brand.get('hub_label', bko + ' 전체'))))

    # 5. 상세 — 특징 -> 사양
    if p.get('features'):
        b.append('<h2 class="pkg-h">특징</h2><ul class="pkg-feat">%s</ul>'
                 % ''.join('<li>%s</li>' % f for f in p['features']))
    if p.get('specs'):
        b.append('<h2 class="pkg-h">사양</h2>' + _pp_table(p['specs']))
        if p.get('specs_note'):
            b.append('<p class="pkg-note">%s</p>' % p['specs_note'])

    # 6. 규격 비교표 — 값이 전부 같은 열은 '모든 규격 공통' 한 줄로 접는다.
    #    소비자가는 표에 적지 않는다(가격 = 우측 주문정보 buybox 한 곳).
    va = p.get('variants') or p.get('price')
    if va:
        b.append('<h2 class="pkg-h">%s</h2>' % escape(va.get('heading', '규격 비교')))
        head, rows, common = _pp_collapse(va.get('head'), va['rows'])
        if head and len(head) == 1:
            # 구분되는 열이 하나뿐 — 표를 쪼개지 말고 라벨/값 한 표로 합친다
            merged = [[head[0], ' · '.join(r[0] for r in rows)]]
            merged += [[k, v] for k, v in common]
            b.append(_pp_table(merged, cls='pkg-tbl pkg-opt'))
        else:
            b.append(_pp_table(rows, head=head, cls='pkg-tbl pkg-opt'))
            if common:
                b.append('<p class="pkg-common"><b>모든 규격 공통</b> — %s</p>'
                         % ' · '.join('%s %s' % (escape(k), v) for k, v in common))
        if va.get('note'):
            b.append('<p class="pkg-note">%s</p>' % va['note'])
    if p.get('safety'):
        b.append(_pp_safety(p['safety']))
    if p.get('papers'):
        b.append(_pp_papers(p['papers']))

    for sec in p.get('sections', []):
        b.append('<h2 class="pkg-h" style="margin-top:26px">%s</h2>' % escape(sec['h']))
        if sec.get('rows'):
            b.append(_pp_table(sec['rows'], head=sec.get('head')))
        if sec.get('html'):
            b.append(sec['html'])
        if sec.get('note'):
            b.append('<p class="pkg-note">%s</p>' % sec['note'])

    # 7. 제조사 원문 출처 + 관련 링크 + 문의 CTA
    src = p.get('source')
    if src:
        b.append('<p class="pkg-note" style="margin-top:18px">자료 출처 — %s</p>'
                 % (('<a href="%s" target="_blank" rel="noopener">%s</a>' % (src['url'], escape(src.get('label', src['url']))))
                    if isinstance(src, dict) and src.get('url') else escape(str(src))))
    if p.get('related'):
        b.append('<p class="pkg-note" style="margin-top:14px">%s</p>' % p['related'])
    b.append('<p style="margin-top:16px"><button type="button" class="qbtn" data-quote="%s %s">견적문의</button></p>'
             % (escape(bko), escape(name)))
    b.append('</div></section>')
    b.append(_pp_ctbar())

    # FAQ
    faq = p.get('faq') or []
    if faq:
        b.append('<section class="faq-sec"><div class="wrap"><h2 class="faq-h">%s FAQ</h2>' % escape(name))
        for f in faq:
            tag = '<span class="faq-tag">%s</span>' % escape(f['tag']) if f.get('tag') else ''
            b.append('<div class="faq-item"><p class="faq-q">%s%s</p><p class="faq-a">%s</p></div>'
                     % (tag, escape(f['q']), f['a']))
        b.append('</div></section>')

    # ---------- JSON-LD ----------
    ld = p.get('ld', {})
    prod = {"@context": "https://schema.org", "@type": "Product",
            "name": ld.get('name') or '%s %s' % (bko, name),
            "brand": {"@type": "Brand", "name": ben, "alternateName": bko},
            "url": full,
            "description": _pp_text(ld.get('description') or desc)}
    if ld.get('sku'):
        prod['sku'] = ld['sku']
    if ld.get('category'):
        prod['category'] = ld['category']
    if img1:
        prod['image'] = 'https://rndsetup.com' + img1
    if ld.get('models'):
        prod['model'] = ld['models']
    if ld.get('low'):
        prod['offers'] = {"@type": "AggregateOffer", "priceCurrency": "KRW",
                          "lowPrice": ld['low'], "highPrice": ld.get('high', ld['low']),
                          "offerCount": ld.get('count', 1),
                          "availability": "https://schema.org/InStock",
                          "seller": {"@id": "https://rndsetup.com/#org"}}
    b.append('<script type="application/ld+json">%s</script>'
             % json.dumps(prod, ensure_ascii=False).replace('</', '<\\/'))
    if faq:
        fp = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": _pp_text(f['q']),
             "acceptedAnswer": {"@type": "Answer", "text": _pp_text(f['a'])}} for f in faq]}
        b.append('<script type="application/ld+json">%s</script>'
                 % json.dumps(fp, ensure_ascii=False).replace('</', '<\\/'))
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "브랜드", "item": "https://rndsetup.com/brands/"},
        {"@type": "ListItem", "position": 2, "name": bko, "item": "https://rndsetup.com" + hub},
        {"@type": "ListItem", "position": 3, "name": name, "item": full}]}
    b.append('<script type="application/ld+json">%s</script>'
             % json.dumps(bc, ensure_ascii=False).replace('</', '<\\/'))

    b.append('<div id="pumplab-footer"></div>')
    b.append('<script src="/assets/site.js" defer></script>')
    b.append('</body>')
    b.append('</html>')
    return '\n'.join(h) + '\n' + '\n'.join(b) + '\n'


def build_product_pages():
    """_build/products/<brand>.json (SSOT) -> brands/<brand>/<slug>/index.html 생성.
    신규 상세페이지 = JSON 1건 추가 + 빌드. 페이지 HTML을 손으로 만들지 않는다."""
    pdir = os.path.join(SCRIPT_DIR, PP_DIR)
    if not os.path.isdir(pdir):
        print('  [skip] _build/products/ 없음')
        return
    total, audit = 0, []
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith('.json') or fn.startswith('_'):
            continue
        data = json.load(open(os.path.join(pdir, fn), encoding='utf-8'))
        brand = data['brand']
        for p in data.get('products', []):
            html = _pp_render(brand, p)
            if not html.rstrip().endswith('</html>'):
                print('  [ERR] %s/%s: </html> 누락 — 쓰기 중단' % (brand['slug'], p['slug']))
                continue
            out = os.path.join(ROOT_DIR, 'brands', brand['slug'], p['slug'], 'index.html')
            write(out, html)
            total += 1
            miss = _pp_audit(brand['slug'], p)
            if miss:
                audit.append('%s/%s — 원문 미수집: %s' % (brand['slug'], p['slug'], ' · '.join(miss)))
            if p.get('papers'):
                _k, _d, _fb = _pp_pick_papers(p['papers'].get('items') or [])
                if _d:
                    audit.append('%s/%s — 논문 제외(등급 밖 저널): %s'
                                 % (brand['slug'], p['slug'],
                                    ' · '.join(_pp_text(x.get('journal', ''))[:40] for x in _d)))
                if _fb:
                    audit.append('%s/%s — 논문 저널이 전부 등급 밖. 유명 저널 논문을 찾아 교체할 것'
                                 % (brand['slug'], p['slug']))
    print('  제품 상세페이지 생성: %d개 (_build/products/*.json SSOT)' % total)
    for a in audit:
        print('    [warn] %s' % a)


# ============================================================================
# 상세페이지 빌드 린터 — 디자인 표준(CLAUDE.md 4.5) 위반을 warn 으로 검출
# 검사만 하고 빌드를 중단하지 않는다. 구형 브랜드는 순차 이관 부채이므로 제외.
# ============================================================================

def _brand_profiles():
    """_build/brands.json — 브랜드 프로파일 SSOT. 제품군별 필수 사양·수집 함정·기준 통과본."""
    bp = os.path.join(SCRIPT_DIR, 'brands.json')
    if not os.path.exists(bp):
        return {}
    try:
        return json.loads(read(bp)).get('brands', {})
    except Exception as e:
        print('  [warn] brands.json 읽기 실패: %s' % e)
        return {}


PP_MODEL_BLOCK_MIN = 3      # 모델 이 수 이상이면 모델별 내용 블록을 요구한다


def _brand_family(prof, slug):
    """슬러그에 맞는 제품군을 찾아 (이름, 필수사양) 반환. 없으면 브랜드 기본값."""
    for name, fam in (prof.get('families') or {}).items():
        for m in fam.get('match', []):
            if m in slug:
                return name, fam.get('required_specs') or []
    return None, prof.get('default_required_specs') or []


def _pp_pack_variant(models):
    """규격 변형 페이지인가 — 같은 물건을 용량·치수만 바꿔 파는 경우.
    50 g / 100 g / 250 g, 두께 0.1mm / 0.2mm 처럼 라벨에서 숫자를 빼면 같아지고
    사양(s)이 하나뿐이면 모델별 블록이 필요 없다. 규격 비교표가 그 역할을 한다.
    재질이 다른 것(GC / Pt / Au)은 숫자를 빼도 달라지므로 여기서 걸리지 않는다."""
    if not models:
        return False
    if len({(m.get('s') or '') for m in models}) != 1:
        return False
    keys = {re.sub(r'[\d.]+', '', (m.get('m') or '')).strip() for m in models}
    return len(keys) == 1


LINT_SKIP_BRANDS = {'sh-scientific', 'leadfluid', 'alicat'}   # 구형 레이아웃 — 이관 대기
LINT_BAD_COLORS = ['#1E3A5F', '#1a6e56', '#C2410C', '#E8632C']  # 구 네이비·틸·테라코타·오렌지
# 페이지가 자기 자신을 설명하는 메타 문구 — 데이터는 표로, 안내 문장은 쓰지 않는다
# 본문에 남은 중국어 간체 — 제조사 원문을 안 옮기고 그대로 붙인 흔적.
# 제조사 상호(로마자 병기)와 한국어 한자어는 예외로 둔다.
LINT_CJK_OK = ('天津恒创立达', '合肥原位科技', '純水', '濃酸', '常温', '眞空')
# 제조사 카탈로그가(CNY)를 규격으로 잘못 실은 흔적. CNY 값은 늘 정수+.0 이고
# 판매 단위가 붙는다. 0.4~0.6m/s 같은 실제 사양과 헷갈리지 않게 좁혀 둔다.
LINT_CNY_LEAK = r'\d{2,}\.0\s*~\s*\d{2,}\.0\s*(?:g|장|세트|롤|개|㎡|박스|팩|m)(?![/\w])'

LINT_BAD_PHRASES = ['옮긴 것입니다', '옮겼습니다', '확인하실 수 있습니다', '보실 수 있습니다',
                    '바로 나옵니다', '아래 표', '위 표', '다음과 같습니다']

# 블록 탐지 정규식. 표준 순서 = 크럼 -> h1+영문명 -> 대표사진 -> 정답블록 -> 특징 -> 사양 -> 규격표.
# 2단 레이아웃(.dt-grid)에서는 사진 칼럼이 DOM상 h1보다 앞에 오는 것이 정상이므로,
# 사진/h1/정답블록이 모두 상단 블록(.detail-top) 안에 있으면 그 셋의 앞뒤는 따지지 않는다.
LINT_PAT = {
    '크럼':     r'class="crumb"',
    'h1':       r'<h1[\s>]',
    '대표사진': r'class="dt-img"|<figure[^>]*>\s*<img',
    '정답블록': r'class="dt-ans"|class="dt-sum"|class="pkg-ans"',
    '규격표':   r'class="pkg-tbl pkg-opt"|class="pkg-opt',
}


def _lint_body(html):
    """<body> 이후 본문만. JSON-LD·script 는 제외해 오탐을 줄인다."""
    body = html.split('<body>', 1)[-1]
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    return body


def lint_detail_pages():
    root = os.path.join(ROOT_DIR, 'brands')
    if not os.path.isdir(root):
        return
    profiles = _brand_profiles()
    warns, checked = [], 0
    for brand in sorted(os.listdir(root)):
        bdir = os.path.join(root, brand)
        if not os.path.isdir(bdir) or brand in LINT_SKIP_BRANDS:
            continue
        prof = profiles.get(brand)
        if prof is None:
            warns.append(('brands/%s/' % brand, 'NO_BRAND_PROFILE',
                          '_build/brands.json 에 브랜드 프로파일이 없다 — 수집 방법·기준 통과본·제품군 필수사양을 먼저 적을 것'))
            prof = {}
        for slug in sorted(os.listdir(bdir)):
            p = os.path.join(bdir, slug, 'index.html')
            if not os.path.isfile(p):
                continue
            html = read(p)
            if 'http-equiv="refresh"' in html or 'class="dt-name"' not in html:
                continue          # 리다이렉트 스텁·허브·비상세 페이지는 제외
            checked += 1
            rel = 'brands/%s/%s/' % (brand, slug)
            body = _lint_body(html)

            # 1) </html> 누락
            if not html.rstrip().endswith('</html>'):
                warns.append((rel, 'HTML_END', '</html> 누락 — 파일 잘림 의심'))

            # 2) 필수 블록 존재·순서
            at = {}
            for label, pat in LINT_PAT.items():
                m = re.search(pat, body)
                if m:
                    at[label] = m.start()
            missing = [k for k in ('크럼', 'h1', '대표사진', '정답블록') if k not in at]
            if missing:
                warns.append((rel, 'MISSING_BLOCK', '필수 블록 없음: ' + ' · '.join(missing)))
            if '규격표' not in at and 'class="qbtn"' not in body:
                warns.append((rel, 'NO_SPEC_CTA', '규격표도 견적 CTA도 없음'))
            if '규격표' in at and 'id="buybox"' not in body:
                warns.append((rel, 'NO_BUYBOX', '오른쪽 주문정보(#buybox) 없음 — 규격표만 있고 주문 경로가 없다'))

            twocol = 'class="dt-grid"' in body      # 2단 레이아웃이면 상단 3블록은 순서 자유
            seq = ['크럼', 'h1', '정답블록', '규격표'] if twocol \
                else ['크럼', 'h1', '대표사진', '정답블록', '규격표']
            seq = [k for k in seq if k in at]
            for i in range(1, len(seq)):
                if at[seq[i]] < at[seq[i - 1]]:
                    warns.append((rel, 'ORDER', '블록 순서 어긋남: %s 가 %s 보다 앞에 있음 '
                                       '(표준=크럼→h1+영문명→대표사진→정답블록→특징→사양→규격표)'
                                  % (seq[i], seq[i - 1])))
                    break
            if twocol and '대표사진' in at and 'class="detail-top"' in body:
                top = body.split('class="detail-top"', 1)[1].split('</section>', 1)[0]
                if not re.search(LINT_PAT['대표사진'], top):
                    warns.append((rel, 'IMG_OUTSIDE', '대표사진이 상단 블록(.detail-top) 밖에 있음'))

            # 2-1) 제품군 필수 사양 (brands.json)
            fam, req = _brand_family(prof, slug)
            if req:
                have = set(x.strip() for x in re.findall(r'<th[^>]*>([^<]{1,24})</th>', body))
                miss_spec = [r for r in req if r not in have]
                if miss_spec:
                    warns.append((rel, 'REQ_SPEC', '%s 제품군 필수 사양 누락: %s'
                                  % (fam or '브랜드 기본', ' · '.join(miss_spec))))

            # 2-2) 시리즈 페이지인데 모델별 내용이 없다
            mm = re.search(r"data-models='(\[.*?\])'", html, re.S)
            try:
                models = json.loads(mm.group(1)) if mm else []
            except Exception:
                models = []
            nmodel = len(models)
            need = prof.get('model_block_min', PP_MODEL_BLOCK_MIN)
            if (nmodel >= need and not _pp_pack_variant(models)
                    and not re.search(r'class="mdl-hd"|class="thlb"|mdl-im|mdl-tbl', body)):
                warns.append((rel, 'NO_MODEL_BLOCK',
                              '모델 %d종을 한 페이지에 담았는데 모델별 사진·사양 블록이 없다 '
                              '— 고객이 대표 모델 말고는 내용을 볼 수 없다 (.mdl-hd 또는 썸네일 라벨 .thlb)'
                              % nmodel))

            # 2-3) 본문에 중국어 원문이 남았다
            txt = re.sub(r'<[^>]+>', ' ', body)
            for ok in LINT_CJK_OK:
                txt = txt.replace(ok, '')
            cjk = re.findall(r'[\u4e00-\u9fff]+', txt)
            if cjk:
                warns.append((rel, 'CJK_BODY',
                              '본문에 중국어 원문이 남았다 — 한글로 옮길 것: '
                              + ' · '.join(dict.fromkeys(cjk))[:80]))

            # 2-4) 규격 자리에 제조사 매입가(CNY)가 들어갔다
            if re.search(LINT_CNY_LEAK, body):
                warns.append((rel, 'CNY_LEAK',
                              '규격 표기에 제조사 카탈로그가(CNY) 범위가 들어갔다 — 실제 규격으로 바꿀 것'))

            # 3) 금지 색상
            low = body.lower()
            bad = [c for c in LINT_BAD_COLORS if c.lower() in low]
            if bad:
                warns.append((rel, 'BAD_COLOR', '금지 색상 사용: ' + ' · '.join(bad)))

            # 3-1) 페이지 자기설명 메타 문구
            bad_ph = [x for x in LINT_BAD_PHRASES if x in body]
            if bad_ph:
                warns.append((rel, 'BAD_PHRASE', '안내 문장(메타 문구) 사용: ' + ' · '.join(bad_ph)))

            # 4) border-left 3~4px 색 바
            for m in re.finditer(r'border-left(?:-width)?\s*:\s*([^;"}]*)', body, re.I):
                v = m.group(1)
                if re.search(r'\b[34]px\b', v):
                    warns.append((rel, 'BORDER_LEFT', '좌측 포인트 바 금지: border-left:%s' % v.strip()))
                    break

            # 5) 인라인 <style> 스냅샷 재발
            if '<style' in html:
                warns.append((rel, 'STYLE_INLINE', '인라인 <style> 잔존 — /assets/detail.css 로 옮길 것'))
            elif '/assets/detail.css' not in html:
                warns.append((rel, 'NO_DETAIL_CSS', '/assets/detail.css 링크 없음'))

    # 유예 목록(_build/lint_allow.txt) 에 있는 기존 부채는 경고만, 새 위반은 빌드를 세운다.
    allow = set()
    ap = os.path.join(SCRIPT_DIR, 'lint_allow.txt')
    if os.path.exists(ap):
        for line in read(ap).splitlines():
            line = line.split('#')[0].strip()
            if line:
                allow.add(' '.join(line.split()))
    old_w = [w for w in warns if '%s %s' % (w[0], w[1]) in allow]
    new_w = [w for w in warns if '%s %s' % (w[0], w[1]) not in allow]
    if old_w:
        print('  [warn] 이관 대기 부채 %d건 (유예 목록)' % len(old_w))
        for rel, code, msg in old_w[:40]:
            print('    - %s : %s' % (rel, msg))
    if new_w:
        print('')
        print('  [X] 상세페이지 표준 위반(신규) %d건 — 커밋할 수 없습니다' % len(new_w))
        for rel, code, msg in new_w:
            print('    - %s [%s] : %s' % (rel, code, msg))
        print('')
        print('  고치거나, 의도한 예외라면 _build/lint_allow.txt 에 아래 줄을 추가하십시오:')
        for rel, code, msg in new_w:
            print('    %s %s' % (rel, code))
        return len(new_w)
    if not warns:
        print('  상세페이지 린터: %d개 검사, 위반 0건' % checked)
    return 0


def build_wiki():
    """배터리 사전 — _build/wiki.json(SSOT) → /wiki/ 인덱스 + 항목 페이지 정적 생성.
    항목 추가 = wiki.json 1건. 인덱스·항목·sitemap·검색 인덱스 전부 빌드 자동."""
    wp = os.path.join(SCRIPT_DIR, 'wiki.json')
    if not os.path.exists(wp):
        print('  [skip] wiki.json 없음')
        return
    terms = json.load(open(wp, encoding='utf-8'))['terms']
    by = {t['slug']: t for t in terms}
    cats = ['공정', '재료', '전기화학', '장비', '단위']
    outdir = os.path.join(ROOT_DIR, 'wiki')
    os.makedirs(outdir, exist_ok=True)

    HEAD = (
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>{title}</title>\n<meta name="description" content="{desc}">\n'
        '<link rel="canonical" href="https://rndsetup.com{url}">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="{title}">\n'
        '<meta property="og:description" content="{desc}">\n'
        '<meta property="og:url" content="https://rndsetup.com{url}">\n'
        '<meta property="og:image" content="https://rndsetup.com/img/og-cover.png">\n'
        '{ld}'
        '<link rel="stylesheet" href="/assets/site.css">\n'
        '<style>\n'
        '.wk-wrap{{max-width:860px;margin:0 auto;padding:26px 18px 70px}}\n'
        '.wk-crumb{{font-size:12.5px;color:#9aa3ad;margin-bottom:14px}}\n'
        '.wk-crumb a{{color:#9aa3ad;text-decoration:none}}\n'
        '.wk-wrap h1{{font-family:"Noto Serif KR",Georgia,serif;font-size:clamp(23px,3vw,32px);font-weight:800;color:#1A1A1A;letter-spacing:-.02em;line-height:1.35}}\n'
        '.wk-en{{font-size:13px;color:#9aa3ad;font-weight:700;margin-top:4px}}\n'
        '.wk-cat{{display:inline-block;font-size:11.5px;font-weight:800;color:#3B3695;background:#EAF4FB;border-radius:999px;padding:4px 12px;margin-top:10px}}\n'
        '.wk-def{{margin:16px 0 26px;padding:14px 18px;background:#EAF4FB;border-radius:10px;font-size:14.5px;line-height:1.75;color:#26313c}}\n'
        '.wk-wrap h2{{font-size:18px;font-weight:800;color:#1A1A1A;margin:30px 0 10px;padding-bottom:7px;border-bottom:2px solid #3B3695}}\n'
        '.wk-wrap p{{font-size:14.5px;color:#3a4550;line-height:1.85;margin:10px 0}}\n'
        '.wk-see{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}\n'
        '.wk-see a{{font-size:13px;font-weight:700;color:#3B3695;background:#fff;border:1px solid #d9e2ec;border-radius:999px;padding:6px 14px;text-decoration:none}}\n'
        '.wk-see a:hover{{background:#EAF4FB}}\n'
        '.wk-prod{{margin-top:8px}}\n'
        '.wk-prod a{{display:inline-block;font-size:13px;font-weight:800;color:#fff;background:#3B3695;border-radius:9px;padding:9px 16px;text-decoration:none;margin:4px 8px 0 0}}\n'
        '</style>\n</head>\n<body>\n<div id="pumplab-header"></div>\n<main>\n'
    )
    FOOT = '\n</main>\n<div id="pumplab-footer"></div>\n<script src="/assets/site.js" defer></script>\n</body>\n</html>\n'

    # ---------- 항목 페이지 ----------
    for t in terms:
        url = '/wiki/%s/' % t['slug']
        title = '%s — 배터리 사전 | 실험셋업연구소' % t['term']
        desc = t['d'][:150]
        ld = ('<script type="application/ld+json">'
              + json.dumps({
                  "@context": "https://schema.org",
                  "@type": "DefinedTerm",
                  "name": t['term'],
                  "alternateName": t['en'],
                  "description": t['d'],
                  "url": "https://rndsetup.com" + url,
                  "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "실험셋업연구소 배터리 사전", "url": "https://rndsetup.com/wiki/"}
                }, ensure_ascii=False)
              + '</script>\n')
        body = ['  <div class="wk-wrap">']
        body.append('    <div class="wk-crumb"><a href="/">홈</a> › <a href="/wiki/">배터리 사전</a> › %s</div>' % escape(t['term']))
        body.append('    <h1>%s</h1>' % escape(t['term']))
        body.append('    <div class="wk-en">%s</div>' % escape(t['en']))
        body.append('    <span class="wk-cat">%s</span>' % t['cat'])
        body.append('    <div class="wk-def">%s</div>' % escape(t['d']))
        for s in t['sections']:
            body.append('    <h2>%s</h2>' % escape(s['h']))
            body.append('    <p>%s</p>' % escape(s['b']))
        if t.get('see'):
            body.append('    <h2>같이 보기</h2>')
            links = ''.join('<a href="/wiki/%s/">%s</a>' % (s, escape(by[s]['term'])) for s in t['see'] if s in by)
            body.append('    <div class="wk-see">%s</div>' % links)
        if t.get('products'):
            body.append('    <h2>관련 제품</h2>')
            pl = ''.join('<a href="%s">%s →</a>' % (h, escape(l)) for l, h in t['products'])
            body.append('    <div class="wk-prod">%s</div>' % pl)
        body.append('  </div>')
        page = HEAD.format(title=escape(title), desc=escape(desc), url=url, ld=ld) + '\n'.join(body) + FOOT
        d = os.path.join(outdir, t['slug'])
        os.makedirs(d, exist_ok=True)
        write(os.path.join(d, 'index.html'), page)

    # ---------- 인덱스 ----------
    url = '/wiki/'
    title = '배터리 사전 — 공정·재료·전기화학·장비 용어 %d개 | 실험셋업연구소' % len(terms)
    desc = '소성·하소·공침부터 기준전극·과전압·패러데이 효율, sccm·C-rate까지 — 에너지·배터리 실험에서 만나는 용어를 위키 형식으로 설명합니다. 검색하거나 분야별로 찾아보세요.'
    ld = ('<script type="application/ld+json">'
          + json.dumps({
              "@context": "https://schema.org",
              "@type": "DefinedTermSet",
              "name": "실험셋업연구소 배터리 사전",
              "description": desc,
              "url": "https://rndsetup.com/wiki/",
              "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t['term'], "url": "https://rndsetup.com/wiki/%s/" % t['slug']} for t in terms]
            }, ensure_ascii=False)
          + '</script>\n')
    body = ['  <div class="wk-wrap" style="max-width:1000px">']
    body.append('    <div class="wk-crumb"><a href="/">홈</a> › 배터리 사전</div>')
    body.append('    <h1>배터리 사전</h1>')
    body.append('    <p style="max-width:720px">에너지·배터리 실험에서 만나는 용어 %d개를 위키 형식으로 설명합니다. 정의 → 개요 → 실무 포인트 → 같이 보기 순서로, 논문을 읽다 막히는 말을 빠르게 해소하는 것이 목적입니다.</p>' % len(terms))
    body.append('    <input type="search" id="wkq" placeholder="용어 검색 — 예: 하소, 과전압, sccm" style="width:100%;max-width:440px;border:2px solid #3B3695;border-radius:10px;padding:11px 16px;font-size:14px;margin:6px 0 8px" aria-label="용어 검색">')
    for c in cats:
        group = [t for t in terms if t['cat'] == c]
        if not group:
            continue
        body.append('    <h2>%s</h2>' % c)
        body.append('    <div class="wk-see" style="gap:10px">')
        for t in sorted(group, key=lambda x: x['term']):
            body.append('      <a class="wk-item" data-t="%s %s" href="/wiki/%s/">%s</a>'
                        % (escape(t['term'].lower()), escape(t['en'].lower()), t['slug'], escape(t['term'])))
        body.append('    </div>')
    body.append('  </div>')
    js = ('<script>(function(){var q=document.getElementById("wkq");if(!q)return;'
          'q.addEventListener("input",function(){var v=q.value.trim().toLowerCase();'
          'document.querySelectorAll(".wk-item").forEach(function(a){'
          'a.style.display=(!v||a.getAttribute("data-t").indexOf(v)>-1||a.textContent.toLowerCase().indexOf(v)>-1)?"":"none";});});})();</script>')
    page = HEAD.format(title=escape(title), desc=escape(desc), url=url, ld=ld) + '\n'.join(body) + js + FOOT
    write(os.path.join(outdir, 'index.html'), page)
    print('  배터리 사전: 항목 %d개 + 인덱스 정적 생성 (/wiki/)' % len(terms))


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
    SKIP_DIRS = {'_build', '_to_delete', '.git', 'admin', 'api', 'functions',
                 'node_modules', 'img', 'assets', 'out', '.wrangler'}
    # 검색 동의어 — 한 그룹의 말이 페이지에 하나라도 있으면 나머지 말을 색인에 덧붙인다.
    # 사이트 표기가 'in-situ'인데 사람은 '인시츄'로 찾는 문제를 한 곳에서 해결한다.
    SEARCH_SYN = [
        ['인시츄', '인시추', '인시투', 'in-situ', 'in situ', 'insitu', '오퍼란도', 'operando', '실시간 관찰'],
        ['덴드라이트', 'dendrite', '수지상', '수지상정'],
        ['전기화학', 'electrochemical', 'echem'],
        ['기준전극', 'reference electrode', '레퍼런스 전극'],
        ['상대전극', 'counter electrode', '카운터 전극'],
        ['작업전극', 'working electrode', '워킹 전극'],
        ['회전전극', 'rde', 'rrde', '회전원판전극', '회전링원판전극'],
        ['유리탄소', 'gc', 'glassy carbon', '글라시카본', '글래시카본'],
        ['전해셀', '전해조', '전기화학 셀', 'electrochemical cell'],
        ['코인셀', 'coin cell', '2032', '2032형'],
        ['수전해', '물분해', 'water splitting', 'electrolysis', '전기분해'],
        ['이차전지', '배터리', 'battery', '리튬이온', 'li-ion'],
        ['전고체', 'solid-state', 'solid state', '고체전해질'],
        ['퍼니스', '전기로', '튜브퍼니스', '관상로', 'furnace'],
        ['질량유량계', 'mfc', 'mass flow controller', '유량제어기'],
        ['연동펌프', '페리스탈틱', 'peristaltic', '정량펌프'],
        ['사파이어', 'sapphire'],
        ['석영', '쿼츠', 'quartz', 'fused silica', '용융석영'],
        ['라만', 'raman'],
        ['현미경', 'microscope', '광학관찰'],
    ]

    def syn_expand(text):
        low = text.lower()
        extra = []
        for grp in SEARCH_SYN:
            if any(g.lower() in low for g in grp):
                extra += [g for g in grp if g.lower() not in low]
        return (' ' + ' '.join(dict.fromkeys(extra))) if extra else ''

    redirected = _redirect_sources()
    entries = []
    for dirpath, filenames in html_tree():
        if set(dirpath.split(os.sep)) & SKIP_DIRS:
            continue
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
            if 'noindex' in t[:2000] or 'http-equiv="refresh"' in t[:2000]:
                continue  # noindex·리다이렉트 스텁은 검색 인덱스 제외
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
            elif url.startswith('/wiki'):
                cat = '배터리 사전'
            elif url.startswith('/magazine'):
                cat = '매거진'
            elif url.startswith('/setups') or url.startswith('/furnace/setups') or url.startswith('/pump/setups'):
                cat = '셋업 사례'
            elif url.startswith('/pump/atoz'):
                cat = '펌프 문제해결'
            elif url.startswith('/guides'):
                cat = '선택 가이드'
            elif url.startswith('/manuals') or url.startswith('/temp-controller'):
                cat = '메뉴얼'
            elif url.startswith('/application'):
                cat = '실험 가이드'
            elif url.startswith('/pumps') or url.startswith('/pump'):
                cat = '펌프'
            else:
                cat = '페이지'
            k = ' '.join(x for x in (h1, desc, kw) if x)[:400]
            k += syn_expand(title + ' ' + k)   # 동의어는 400자 컷 뒤에 붙인다
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
        ('materials/',               '0.9', 'weekly'),   # 소재 허브
        ('info/',                    '0.9', 'weekly'),   # 제품 정보 허브
        ('wiki/',                    '0.9', 'weekly'),   # 배터리 사전 인덱스
        ('magazine/deposition/',     '0.8', 'monthly'),  # 증착 허브
        ('magazine/heat-treatment/', '0.8', 'monthly'),  # 열처리 허브
        ('magazine/oxidation/',      '0.8', 'monthly'),  # 산화·확산 허브
        ('guides/',       '0.8', 'monthly'),  # 선택 가이드 허브
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
        ('brands/alicat/mc-series/','0.8', 'monthly'),
        ('brands/alicat/mfc-guide/','0.7', 'monthly'),
        ('brands/alicat/manual/','0.7', 'monthly'),
        ('brands/sh-scientific/guide/','0.9', 'monthly'),  # 삼흥 허브 = 제품 선택 가이드(견적 funnel)
        ('brands/sh-scientific/manual/','0.7', 'monthly'),  # 삼흥 메뉴얼
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
    _idir = os.path.join(ROOT_DIR, 'info')
    if os.path.isdir(_idir):
        for slug in sorted(os.listdir(_idir)):
            idx = os.path.join(_idir, slug, 'index.html')
            if os.path.isfile(idx):
                rel = 'info/%s/' % slug
                if rel not in _known and ('/' + rel) not in _red_srcs:
                    _auto.append((rel, '0.7', 'monthly'))
    _wdir = os.path.join(ROOT_DIR, 'wiki')
    if os.path.isdir(_wdir):
        for slug in sorted(os.listdir(_wdir)):
            idx = os.path.join(_wdir, slug, 'index.html')
            if os.path.isfile(idx):
                rel = 'wiki/%s/' % slug
                if rel not in _known and ('/' + rel) not in _red_srcs:
                    _auto.append((rel, '0.7', 'monthly'))
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
    build_product_pages()  # 제품 상세페이지 (products/<brand>.json SSOT · 손 HTML 금지)
    build_wiki()  # 배터리 사전 (wiki.json SSOT)
    inject_static_nav()
    inject_head_schema()
    normalize_html_urls()
    build_new_research()  # 홈 최신연구 레일 — posts.json 자동 렌더
    build_prices()        # 가격 SSOT — SQL 최저가를 index.html·site.js 마커에 주입
    stamp_assets()        # 자산 URL ?v=해시 — 배포 후 옛 JS/CSS 캐시가 남는 것을 막는다
    build_search_index()  # 사이트 검색 인덱스(/search-index.json) — 전 페이지 자동 스캔 (301 소스 제외)
    lint_fail = lint_detail_pages()   # 상세페이지 디자인 표준 검사 (신규 위반이면 빌드 중단)

    if lint_fail:
        print('\n' + '=' * 60)
        print('  빌드 중단 — 파일을 쓰지 않았습니다 (신규 표준 위반 %d건)' % lint_fail)
        print('=' * 60)
        sys.exit(1)

    saved = flush_writes()

    print('\n' + '=' * 60)
    print(f'  파일 쓰기: {saved}개 (안 바뀐 파일은 건드리지 않음)')
    print(f'  완료: {len(written)}개 페이지 + sitemap.xml')
    print('=' * 60)


if __name__ == '__main__':
    main()
# pumps pillar wired: peristaltic/syringe/metering/gear + hub (2026-07)
