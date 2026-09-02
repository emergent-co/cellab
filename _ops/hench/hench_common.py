# -*- coding: utf-8 -*-
"""Hench 모델 단위 상세페이지 프레임워크.
지침 claude/제품올리기_지침.md §3-1(페이지 단위=모델) · §3-2(구성) 준수.
양식 CSS·문의블록은 기준 템플릿(가오스 glass-cell-c001)에서 런타임 추출 → 템플릿 바뀌면 재실행만."""
import os, re, json, io, math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# 신규 표준(2026-09): 인라인 <style> 금지. 공유 /assets/detail.css + /assets/site.css 만 링크한다.
# 기준 통과본 = brands/hefei/om003-microscope-cell/index.html
_STD = io.open(os.path.join(ROOT, 'brands', 'hefei', 'om003-microscope-cell', 'index.html'), encoding='utf-8').read()
HEADCSS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
           '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&display=swap" rel="stylesheet">\n'
           '<link rel="stylesheet" href="/assets/detail.css">\n'
           '<link rel="stylesheet" href="/assets/site.css">\n'
           '<!--HEADLD_START--><!--HEADLD_END-->')
CTBAR = re.search(r'<section class="ctbar-sec">.*?</section>', _STD, re.S).group(0)
EXTRA = ''   # 인라인 스타일 없음 — .hx-note / .xlink / .bdg2 는 detail.css 로 이관됨

FOOT = ('<div id="pumplab-footer"><!--CNAV_START--><!--CNAV_END--></div>\n'
        '<script src="/assets/site.js" defer></script>\n</body>\n</html>\n')

BRANDLINE = 'Hench · 天津恒创立达 (Tianjin Hengchuang Lida)'
TON = 0.056055  # 700 MPa 성형 시 필요 하중(T) = TON * d(mm)^2


def need_ton(d_mm, mpa=700.0):
    """지름 d(mm) 시료를 mpa로 성형할 때 필요한 하중(톤)."""
    return (mpa * math.pi * d_mm ** 2 / 4.0) / 9806.65


def max_dia(ton, mpa=700.0):
    """하중 ton(T)으로 mpa를 낼 수 있는 최대 시료 지름(mm)."""
    return math.sqrt(ton * 9806.65 * 4.0 / (mpa * math.pi))


def sample_mpa(ton, d_mm):
    """하중 ton(T)을 지름 d(mm) 시료에 걸었을 때 시료면 압력(MPa)."""
    return ton * 9806.65 / (math.pi * d_mm ** 2 / 4.0)


def _faq_html(items):
    return ''.join('<div class="faq-item"><p class="faq-q"><span class="faq-tag">%s</span>%s</p>'
                   '<p class="faq-a">%s</p></div>' % (t, q, a) for t, q, a in items)


def _faq_ld(items):
    plain = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()
    d = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
         {"@type": "Question", "name": plain(q),
          "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for _, q, a in items]}
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def render(p):
    """p = 모델 1개 dict. 필수 키는 gen_models.py 참조."""
    url = 'https://rndsetup.com/brands/hench/%s/' % p['slug']
    og = 'https://rndsetup.com' + p['img']
    head = ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n'
            '<link rel="canonical" href="%s">\n'
            '<meta property="og:type" content="product"><meta property="og:title" content="%s">'
            '<meta property="og:description" content="%s"><meta property="og:url" content="%s">'
            '<meta property="og:image" content="%s"><meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s">'
            '<meta name="twitter:image" content="%s">\n'
            % (p['title'], p['desc'], url, p['h1'], p['desc'], url, og, p['h1'], p['desc'], og)) \
           + HEADCSS + EXTRA + '</head>\n'

    thumbs = ''
    if p.get('thumbs'):
        thumbs = ('<div class="dt-thumbs">' + ''.join(
            '<button type="button" data-src="%s" onclick="agSwap(this)">'
            '<img src="%s" alt="%s %s" loading="lazy" onerror="this.parentElement.style.display=\'none\'">'
            '<span class="thlb"><b>%s</b>%s</span></button>' % (s, s, l, sub, l, sub)
            for s, l, sub in p['thumbs']) + '</div>'
            '<script>function agSwap(b){document.querySelector(".dt-img img").src=b.getAttribute("data-src");}</script>')

    buy = ('<div class="buyrail"><div id="buybox" class="bb dt-buy" data-name="%s" data-models=\'%s\'></div></div>\n'
           % (p['h1'], json.dumps(p['models'], ensure_ascii=False).replace("'", '&#39;')))
    body = ('<body>\n<div id="pumplab-header"></div>\n' + buy +
            '<section class="detail-top"><div class="wrap">'
            '<div class="crumb"><a href="/">홈</a> › <a href="/product/">제품</a> › %s</div>\n'
            '<div class="dt-grid">\n<div class="dt-col"><div class="dt-img">'
            '<img src="%s" alt="%s" loading="lazy" onerror="this.closest(\'.dt-img\').style.display=\'none\'">'
            '</div>%s</div>\n<div class="dt-info">\n'
            '<div class="dt-brand">%s</div>\n<h1 class="dt-name">%s</h1>\n'
            '<p class="dt-ans">%s</p>\n<p class="dt-sum">%s</p>\n'
            '<button type="button" class="qbtn" data-quote="%s">견적문의</button>\n'
            '<div class="dt-kw">%s</div>\n</div>\n</div></div></section>\n'
            % (p['crumb'], p['img'], p['h1'], thumbs, BRANDLINE, p['h1'], p['ans'], p['summ'],
               p['quote'], ''.join('<a href="%s">%s</a>' % (h, t) for h, t in p['kws'])))

    feats = ''.join('<li>%s</li>' % f for f in p['feats'])
    spec = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (k, v) for k, v in p['spec'])
    incl = ''
    if p.get('incl'):
        incl = ('<p class="part-h" style="font-size:13px;font-weight:800;margin:14px 0 4px">구매 구성</p>'
                '<ul class="spec-ul">' + ''.join(
                    '<li>%s<span class="bdg2 %s">%s</span></li>' % (t, c, lb) for t, c, lb in p['incl']) + '</ul>')
    figs = ''
    if p.get('figures'):
        figs = ('<div class="det-imgs" style="margin:22px 0 4px">' + ''.join(
            '<figure><img src="%s" alt="%s" loading="lazy" '
            'onerror="this.parentElement.style.display=\'none\'"><figcaption>%s</figcaption></figure>'
            % (s, c, c) for s, c in p['figures']) + '</div>')
    opt = p.get('opt_tbl', '')
    notes = ''.join('<p class="pkg-note" style="margin-top:14px">%s</p>' % n for n in p['notes'])
    xl = ''
    if p.get('xlinks'):
        xl = ('<p class="xlink"><b style="color:#6B6B6B;font-weight:700">같은 계열 →</b> '
              + ''.join('<a href="%s">%s</a>' % (h, t) for h, t in p['xlinks']) + '</p>')

    body += ('<section class="pkg"><div class="wrap">'
             '<a class="ds-back" href="/product/">← 실험장비 통합 카탈로그</a>\n'
             '<h2 class="pkg-h">특징</h2>\n<ul class="pkg-feat" style="margin-bottom:18px">%s</ul>\n%s\n'
             '<h2 class="pkg-h">사양 요약</h2><div class="pkg-tblwrap"><table class="pkg-tbl"><tbody>%s</tbody></table></div>\n'
             '%s\n%s\n<h2 class="pkg-h">가격</h2><p class="hx-note">%s</p>\n%s\n'
             '<div class="warn"><p class="warn-h">⚠ %s</p><p>%s</p></div>\n%s\n'
             '<p style="margin-top:14px"><button type="button" class="qbtn" data-quote="%s">견적문의</button></p>'
             '</div></section>\n'
             % (feats, incl, spec, opt, figs, p['price'], notes, p['warn_h'], p['warn_p'], xl, p['quote']))

    body += CTBAR + '\n'
    body += ('<script type="application/ld+json">'
             + json.dumps(p['ld'], ensure_ascii=False).replace('</', '<\\/') + '</script>\n')
    # 브랜드 상세(4단 경로)는 build.py의 _breadcrumb_ld 가 처리하지 않는다(2~3단만 지원).
    # → 페이지가 직접 BreadcrumbList 를 들고 있어야 한다 (가오스 기준본과 동일).
    _bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "홈", "item": "https://rndsetup.com/"},
        {"@type": "ListItem", "position": 2, "name": "제품", "item": "https://rndsetup.com/product/"},
        {"@type": "ListItem", "position": 3, "name": p['crumb'],
         "item": 'https://rndsetup.com/brands/hench/%s/' % p['slug']}]}
    body += ('<script type="application/ld+json">'
             + json.dumps(_bc, ensure_ascii=False).replace('</', '<\\/') + '</script>\n')
    body += ('<section class="faq-sec"><div class="wrap"><hr class="pkg-hr">'
             '<h2 class="faq-h">%s FAQ</h2>\n%s</div></section>\n' % (p['h1'], _faq_html(p['faqs'])))
    body += _faq_ld(p['faqs']) + '\n' + FOOT
    return head + body


def write(slug, html):
    d = os.path.join(ROOT, 'brands', 'hench', slug)
    if not os.path.isdir(d):
        os.makedirs(d)
    io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
    return len(html.encode('utf-8'))
