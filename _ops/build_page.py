#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""가오스유니온 시리즈 페이지 → 모델별 단독 페이지 생성 (product-upload 스킬 구조)

build_mb.py 를 시리즈 무관하게 일반화한 것. 원본 페이지 슬러그와 SQL 접두어만 바꾸면
어느 계열에도 쓸 수 있다.

  import build_page as B
  B.init('quartz-cell', 'GU-QZCELL', '부식 시험·석영 전기화학 셀')
  B.build(cfg)
"""
import io, os, re, json, sys

BASE = os.path.expanduser('~/mnt/rndsetup_homepage/brands/gaossunion')
SQL  = os.path.expanduser('~/mnt/rndsetup_homepage/rndsetup_products.sql')
SRC = None
SRC_SLUG = None
SRC_H1 = None
ROWS = {}

def fld(l):
    m = re.search(r"VALUES \((.*)\);\s*$", l)
    if not m: return None
    s = m.group(1); out=[];cur='';q=False;i=0
    while i < len(s):
        c = s[i]
        if q:
            if c == "'":
                if i+1 < len(s) and s[i+1] == "'": cur+="'";i+=2;continue
                q=False;i+=1;continue
            cur+=c;i+=1
        else:
            if c=="'": q=True;i+=1
            elif c==',': out.append(cur);cur='';i+=1
            else: cur+=c;i+=1
    out.append(cur); return out


def init(src_slug, sql_prefix, src_h1):
    """원본 페이지를 읽고 SQL 에서 모델별 가격행을 뽑는다."""
    global SRC, SRC_SLUG, SRC_H1, ROWS
    SRC_SLUG, SRC_H1 = src_slug, src_h1
    SRC = io.open(os.path.join(BASE, src_slug, 'index.html'), encoding='utf-8').read()
    ROWS = {}
    for l in io.open(SQL, encoding='utf-8').read().split('\n'):
        f = fld(l)
        if f and f[0].startswith(sql_prefix):
            ROWS.setdefault(f[7], []).append((f[9], f[15]))
    return ROWS


def price_table(models, headers=('용량 · 구성', '형식', '정가(VAT 별도)')):
    """모델명 병기 가격표. opt_value 를 '용량 · 형식' 으로 분해."""
    out = ['<div class="pkg-tblwrap"><table class="pkg-tbl pkg-opt"><thead><tr>'
           + ''.join('<th>%s</th>' % h for h in headers) + '</tr></thead><tbody>']
    for mo in models:
        for ov, pr in ROWS.get(mo, []):
            if ' · ' in ov:
                cap, form = ov.split(' · ', 1)
            else:
                cap, form = ov, '—'
            cap_c = re.sub(r'(\d)\s*mL', r'\1mL', cap)
            val = ('<b>%s원</b>' % format(int(pr), ',')) if pr.isdigit() and int(pr) > 0 else '<b>문의</b>'
            out.append('<tr><td><b>%s</b>-%s</td><td>%s</td><td style="text-align:center">%s</td></tr>'
                       % (mo, cap_c, form, val))
    out.append('</tbody></table></div>')
    return '\n'.join(out)

def opt_table(rows):
    out = ['<h3 class="pkg-h" style="font-size:16px;margin-top:22px">옵션 · 별매</h3>',
           '<div class="pkg-tblwrap"><table class="pkg-tbl pkg-opt"><thead><tr>'
           '<th>품목</th><th>적용</th><th>정가(VAT 별도)</th></tr></thead><tbody>']
    for name, app, pr in rows:
        out.append('<tr><td>%s</td><td>%s</td><td style="text-align:center"><b>%s원</b></td></tr>'
                   % (name, app, format(pr, ',')))
    out.append('</tbody></table></div>')
    return '\n'.join(out)

# ---------- 공통 CSS ----------
CSS = ('<style>'
 '.mdl-hd{display:flex;gap:28px;align-items:flex-start;flex-wrap:wrap;margin-top:30px}'
 '.mdl-hd .mdl-tx{flex:1 1 320px;min-width:280px}'
 '.mdl-hd .mdl-im{flex:0 0 400px;display:flex;flex-direction:column;gap:12px}'
 '.mdl-hd figure{margin:0;width:400px;max-width:100%}'
 '.mdl-hd img{width:400px;max-width:100%;height:300px;object-fit:contain;background:#fff;border:1px solid #e5e7eb;border-radius:6px}'
 '.mdl-hd figcaption{font-size:12px;color:#6b7280;margin-top:3px;line-height:1.4;text-align:center}'
 '.mdl-en{font-size:13px;color:#6b7280;font-weight:400;display:block;margin-top:3px}'
 '.spec-ol{margin:6px 0 14px;padding-left:0;list-style:none;font-size:13.5px;line-height:1.75;color:#374151}'
 '.spec-ol li{margin:3px 0;padding-left:26px;position:relative}'
 '.spec-ol li .sn{position:absolute;left:0;top:2px;display:inline-flex;width:19px;height:19px;'
 'align-items:center;justify-content:center;border-radius:50%;color:#fff;font-size:11px;font-weight:700}'
 '.sn.b{background:#1E3A5F}.sn.d{background:#0D6E6E}.sn.o{background:#646469}.sn.x{background:#B22222}'
 '.spec-ul{margin:2px 0 6px;padding-left:0;list-style:none;font-size:13.5px;line-height:1.7;color:#374151}'
 '.spec-ul li{margin:3px 0;padding-left:16px;position:relative}'
 '.spec-ul li:before{content:"·";position:absolute;left:4px;font-weight:900;color:#9ca3af}'
 '.spec-ul li.warn{color:#7c2d12}.spec-ul li.warn:before{content:"!";color:#B45309}'
 '.bdg{font-size:11px;font-weight:700;border-radius:4px;padding:1px 6px;margin-left:6px;white-space:nowrap}'
 '.bdg.in{background:#dcfce7;color:#166534}.bdg.dl{background:#ccfbf1;color:#0f766e}'
 '.bdg.op{background:#f1f5f9;color:#334155}.bdg.ex{background:#fee2e2;color:#991b1b}'
 '.part-h{font-size:13px;font-weight:800;color:#1c1917;margin:12px 0 4px}'
 '.spec-src{font-size:12px;color:#6b7280;margin:8px 0 6px}'
 '.buy-box{border:1px solid #C2410C;border-left-width:4px;border-radius:6px 12px 12px 6px;'
 'background:#FFF7ED;padding:12px 16px;margin:10px 0 12px;font-size:13.5px;line-height:1.8;color:#3a3330}'
 '.buy-box .bt{display:block;font-weight:800;color:#9A3412;font-size:13px;margin-bottom:3px}'
 '.buy-box b{color:#1c1917}'
 '.mdl-im.slide{position:relative}.mdl-im.slide figure{display:none}.mdl-im.slide figure.on{display:block}'
 '.mdl-dots{display:flex;gap:6px;justify-content:center;margin-top:2px}'
 '.mdl-dots button{width:9px;height:9px;border-radius:50%;border:none;background:#d1d5db;padding:0;cursor:pointer}'
 '.mdl-dots button.on{background:#1E3A5F}'
 '.mdl-nav{position:absolute;top:150px;transform:translateY(-50%);width:34px;height:34px;border-radius:50%;'
 'border:1px solid #d6d3d1;background:rgba(255,255,255,.92);color:#44403c;font-size:17px;line-height:1;'
 'cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 4px rgba(0,0,0,.12);z-index:2}'
 '.mdl-nav:hover{background:#1E3A5F;color:#fff;border-color:#1E3A5F}'
 '.mdl-nav.prev{left:8px}.mdl-nav.next{right:8px}'
 '.dt-thumbs button{display:flex;flex-direction:column;align-items:center}'
 '.dt-thumbs .thlb{display:block;font-size:11px;line-height:1.35;color:#57534e;margin-top:4px;text-align:center}'
 '.dt-thumbs .thlb b{display:block;color:#1c1917;font-size:11.5px}'
 '</style>')

SLIDE_JS = ('<script>(function(){document.querySelectorAll(".mdl-hd .mdl-im").forEach(function(box){'
 'var figs=[].slice.call(box.querySelectorAll("figure"));if(figs.length<2)return;'
 'box.classList.add("slide");'
 'var dots=document.createElement("div");dots.className="mdl-dots";'
 'figs.forEach(function(f,i){var b=document.createElement("button");b.type="button";'
 'b.setAttribute("aria-label","사진 "+(i+1)+"번 보기");'
 'b.addEventListener("click",function(){show(i,true)});dots.appendChild(b)});'
 'box.appendChild(dots);'
 'var pv=document.createElement("button");pv.type="button";pv.className="mdl-nav prev";'
 'pv.innerHTML="&#10094;";pv.setAttribute("aria-label","이전 사진");'
 'var nx=document.createElement("button");nx.type="button";nx.className="mdl-nav next";'
 'nx.innerHTML="&#10095;";nx.setAttribute("aria-label","다음 사진");'
 'box.appendChild(pv);box.appendChild(nx);'
 'pv.addEventListener("click",function(){show((cur-1+figs.length)%figs.length,true)});'
 'nx.addEventListener("click",function(){show((cur+1)%figs.length,true)});'
 'var cur=0,timer;'
 'function show(i,manual){figs[cur].classList.remove("on");dots.children[cur].classList.remove("on");'
 'cur=i;figs[cur].classList.add("on");dots.children[cur].classList.add("on");'
 'if(manual){clearInterval(timer);timer=setInterval(next,4000)}}'
 'function next(){show((cur+1)%figs.length)}'
 'figs[0].classList.add("on");dots.children[0].classList.add("on");'
 'timer=setInterval(next,4000);'
 'box.addEventListener("mouseenter",function(){clearInterval(timer)});'
 'box.addEventListener("mouseleave",function(){timer=setInterval(next,4000)});'
 '})})();</script>')

IN='<span class="bdg in">본체 구성</span>'
DL='<span class="bdg dl">이중층형만</span>'
OPT='<span class="bdg op">주문 시 옵션</span>'
EX='<span class="bdg ex">미포함 · 별매</span>'
def OP(t): return '<span class="bdg op">%s</span>' % t

def parts(items):
    return ('<p class="part-h">사진 속 부위</p><ul class="spec-ol">'
            + ''.join('<li><span class="sn %s">%d</span>%s%s</li>' % (k, i, t, b)
                      for i, (t, k, b) in enumerate(items, 1)) + '</ul>')

def feats(items):
    return ('<p class="part-h">특징·사용 안내</p><ul class="spec-ul">'
            + ''.join('<li%s>%s</li>' % (' class="warn"' if w else '', t) for t, w in items) + '</ul>')

def figs(imgs):
    return ''.join('<figure><img src="/img/gaossunion/%s" alt="%s" loading="lazy" '
                   'onerror="this.parentElement.style.display=\'none\'">'
                   '<figcaption><b>%d</b>%s</figcaption></figure>' % (fn, cap, i, cap)
                   for i, (fn, cap) in enumerate(imgs, 1))

def model_block(mid, ko, en, src, buy, plist, flist, imgs):
    return ('<div class="mdl-hd" id="%s"><div class="mdl-tx">'
            '<h3 class="pkg-h" style="font-size:17px;margin:0 0 2px">%s<span class="mdl-en">%s</span></h3>'
            '<div class="buy-box"><span class="bt">%s</span>%s</div>'
            '<p class="spec-src">%s</p>%s%s</div>'
            '<div class="mdl-im">%s</div></div>\n'
            % (mid, ko, en, buy[0], buy[1], src, parts(plist), feats(flist), figs(imgs)))

def faq_html(title, items):
    h = '<section class="faq-sec"><div class="wrap"><hr class="pkg-hr"><h2 class="faq-h">%s</h2>\n' % title
    for tag, q, a in items:
        h += ('<div class="faq-item"><p class="faq-q"><span class="faq-tag">%s</span>%s</p>'
              '<p class="faq-a">%s</p></div>' % (tag, q, a))
    h += '</div></section>\n'
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": a}} for _, q, a in items]}
    return h + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'

def cross(label, links):
    """같은 계열 다른 모델 페이지로 가는 줄. links = [(slug, 표시명)]"""
    return ('<p class="pkg-note" style="margin:6px 0 14px">%s: ' % label
            + ' · '.join('<a href="/brands/gaossunion/%s/">%s</a>' % (sl, nm) for sl, nm in links)
            + '</p>')



def build(cfg):
    s = SRC
    # 1) head: CSS 주입
    s = s.replace('</head>', CSS + '</head>', 1)
    # 2) 히어로: 대표 이미지 + 썸네일 교체
    a = s.find('<div class="dt-thumbs">'); b = s.find('</div>', a)
    thumbs = ''.join(
        '<button type="button" data-src="/img/gaossunion/%s" onclick="agSwap(this)">'
        '<img src="/img/gaossunion/%s" alt="%s" loading="lazy" '
        'onerror="this.parentElement.style.display=\'none\'">'
        '<span class="thlb"><b>%s</b>%s</span></button>' % (fn, fn, lb2, lb1, lb2)
        for fn, lb1, lb2 in cfg['thumbs'])
    s = s[:a] + '<div class="dt-thumbs">' + thumbs + s[b:]
    s = re.sub(r'(<div class="dt-img"><img src=")/img/gaossunion/[^"]+(")',
               r'\g<1>/img/gaossunion/%s\g<2>' % cfg['thumbs'][0][0], s, count=1)
    # 3) 메타·제목
    s = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % cfg['title'], s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', '\\g<1>' + cfg['desc'], s, count=1)
    s = re.sub(r'(og:title" content=")[^"]*', '\\g<1>' + cfg['h1'] + ' — 가오스유니온 정품', s, count=1)
    s = re.sub(r'(og:description" content=")[^"]*', '\\g<1>' + cfg['desc'][:150], s, count=1)
    s = s.replace('/brands/gaossunion/%s/' % SRC_SLUG, '/brands/gaossunion/%s/' % cfg['slug'])
    s = re.sub(r'(<h1 class="dt-name">)[^<]*', '\\g<1>' + cfg['h1'], s, count=1)
    s = re.sub(r'(<p class="dt-sum">)[^<]*', '\\g<1>' + cfg['sum'], s, count=1)
    if SRC_H1: s = s.replace(SRC_H1, cfg['h1'])
    # 4) 특징 ul 제거
    m = re.search(r'<h2 class="pkg-h">특징</h2>\s*<ul class="pkg-feat"[\s\S]*?</ul>', s)
    if m: s = s[:m.start()] + s[m.end():]
    # 5) 본문 교체: '모델 · 구성 · 정가' 헤딩 ~ 견적문의 버튼 직전
    # 헤딩 문구는 계열마다 다르다('모델 · 구성 · 정가' / '모델 · 규격 · 정가' …).
    # 문구를 통째로 찾으면 -1 이 나오고 s[:-1] 로 </html> 가 잘려나간다. 실제로 그렇게 터졌다.
    i = s.find('<h2 class="pkg-h">모델')
    assert i > 0, cfg['slug'] + ': 모델 헤딩 없음'
    j = s.find('<p style="margin-top:16px"><button type="button" class="qbtn"', i)
    assert j > i, cfg['slug'] + ': 견적문의 버튼 없음'
    body = ('<h2 class="pkg-h">사양 요약</h2>' + cfg['spec_table']
            + cfg.get('cross', '')
            + '<h2 class="pkg-h">모델 · 용량 · 정가 (%d종)</h2>' % cfg['nrows']
            + ''.join(cfg['blocks'])
            + cfg['price_html'] + cfg.get('opt_html', '')
            + cfg['note'])
    s = s[:i] + body + s[j:]
    # 6) 상세이미지 섹션 제거
    a = s.find('<section class="pkg"><div class="wrap"><h2 class="pkg-h">상세 이미지 (제조사 자료)</h2>')
    if a < 0:
        a = s.find('<h2 class="pkg-h">상세 이미지 (제조사 자료)</h2>')
        if a > 0: a = s.rfind('<section', 0, a)
    if a > 0:
        b = s.find('</section>', a) + len('</section>')
        s = s[:a] + ('<p class="pkg-note" style="max-width:1100px;margin:0 auto 8px;padding:0 20px">'
                     '사진은 가오스유니온 2026 전해셀 카탈로그 원본입니다.</p>') + s[b:]
    # 7) FAQ 교체 — 기존 FAQPage JSON-LD 를 모두 먼저 제거한 뒤 새 FAQ 삽입
    #    (먼저 삽입하면 새 JSON-LD 가 첫 매치가 되어 새것이 지워진다 — 실제로 그렇게 터졌다)
    while True:
        m = re.search(r'<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"FAQPage"[\s\S]*?</script>\s*', s)
        if not m: break
        s = s[:m.start()] + s[m.end():]
    a = s.find('<section class="faq-sec">')
    b = s.find('</section>', a) + len('</section>')
    assert a > 0, cfg['slug'] + ': faq-sec 없음'
    s = s[:a] + cfg['faq'] + s[b:]
    # 8) Product JSON-LD 재계산 — 전역 정규식은 FAQ 질문까지 잡아먹는다. 블록을 파싱해서 고친다.
    trs = [l for l in s.split('\n') if l.lstrip().startswith('<tr>')]
    pr = [int(x.replace(',', '')) for l in trs for x in re.findall(r'<b>([\d,]+)\uc6d0</b>', l)]
    inq = sum(l.count('<b>\ubb38\uc758</b>') for l in trs)
    hit = None
    for mm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            d = json.loads(mm.group(1))
        except Exception:
            continue
        if isinstance(d, dict) and d.get('@type') == 'Product':
            hit = (mm, d); break
    assert hit, cfg['slug'] + ': Product JSON-LD \uc5c6\uc74c'
    mm, d = hit
    d['name'] = cfg['ldname']
    d['model'] = list(cfg['models'])
    d['url'] = 'https://rndsetup.com/brands/gaossunion/%s/' % cfg['slug']
    d['image'] = 'https://rndsetup.com/img/gaossunion/%s' % cfg['thumbs'][0][0]
    d['category'] = '\uc804\uae30\ud654\ud559 \u00b7 ' + cfg['h1']
    if pr:
        o = d.get('offers') or {}
        o.update({'@type': 'AggregateOffer', 'priceCurrency': 'KRW',
                  'lowPrice': min(pr), 'highPrice': max(pr), 'offerCount': len(pr) + inq})
        d['offers'] = o
    else:
        # \uac00\uaca9\ubb38\uc758 \uc804\uc6a9 \ud398\uc774\uc9c0 \u2014 \uc774\uc804 \uac00\uaca9\uc744 \ub0a8\uae30\uba74 \uac70\uc9d3\ub9d0\uc774 \ub41c\ub2e4
        d.pop('offers', None)
    s = s[:mm.start()] + '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>' + s[mm.end():]

    # 9) 슬라이드 JS
    k = s.rfind('</body>')
    s = s[:k] + SLIDE_JS + s[k:]
    assert s.rstrip().endswith('</html>'), cfg['slug']
    for mm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(mm.group(1))
    d = os.path.join(BASE, cfg['slug'])
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(s)
    return len(pr), len(s)
