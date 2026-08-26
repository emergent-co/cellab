# -*- coding: utf-8 -*-
# build.py에 build_wiki() 추가 + main 호출 + sitemap 자동 등재
import io, os, re
here=os.path.dirname(os.path.abspath(__file__))
bp=os.path.join(here,'..','_build','build.py')
b=io.open(bp,encoding='utf-8').read()
assert 'def build_wiki' not in b

FUNC = '''

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
        '<!DOCTYPE html>\\n<html lang="ko">\\n<head>\\n<meta charset="UTF-8">\\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\\n'
        '<title>{title}</title>\\n<meta name="description" content="{desc}">\\n'
        '<link rel="canonical" href="https://rndsetup.com{url}">\\n'
        '<meta property="og:type" content="article">\\n'
        '<meta property="og:title" content="{title}">\\n'
        '<meta property="og:description" content="{desc}">\\n'
        '<meta property="og:url" content="https://rndsetup.com{url}">\\n'
        '{ld}'
        '<link rel="stylesheet" href="/assets/site.css">\\n'
        '<style>\\n'
        '.wk-wrap{{max-width:860px;margin:0 auto;padding:26px 18px 70px}}\\n'
        '.wk-crumb{{font-size:12.5px;color:#9aa3ad;margin-bottom:14px}}\\n'
        '.wk-crumb a{{color:#9aa3ad;text-decoration:none}}\\n'
        '.wk-wrap h1{{font-family:"Noto Serif KR",Georgia,serif;font-size:clamp(23px,3vw,32px);font-weight:800;color:#1A1A1A;letter-spacing:-.02em;line-height:1.35}}\\n'
        '.wk-en{{font-size:13px;color:#9aa3ad;font-weight:700;margin-top:4px}}\\n'
        '.wk-cat{{display:inline-block;font-size:11.5px;font-weight:800;color:#1E3A5F;background:#EDF2F8;border-radius:999px;padding:4px 12px;margin-top:10px}}\\n'
        '.wk-def{{margin:16px 0 26px;padding:14px 18px;background:#EDF2F8;border-left:4px solid #1E3A5F;border-radius:0 10px 10px 0;font-size:14.5px;line-height:1.75;color:#26313c}}\\n'
        '.wk-wrap h2{{font-size:18px;font-weight:800;color:#1A1A1A;margin:30px 0 10px;padding-bottom:7px;border-bottom:2px solid #1E3A5F}}\\n'
        '.wk-wrap p{{font-size:14.5px;color:#3a4550;line-height:1.85;margin:10px 0}}\\n'
        '.wk-see{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}\\n'
        '.wk-see a{{font-size:13px;font-weight:700;color:#1E3A5F;background:#fff;border:1px solid #d9e2ec;border-radius:999px;padding:6px 14px;text-decoration:none}}\\n'
        '.wk-see a:hover{{background:#EDF2F8}}\\n'
        '.wk-prod{{margin-top:8px}}\\n'
        '.wk-prod a{{display:inline-block;font-size:13px;font-weight:800;color:#fff;background:#1E3A5F;border-radius:9px;padding:9px 16px;text-decoration:none;margin:4px 8px 0 0}}\\n'
        '</style>\\n</head>\\n<body>\\n<div id="pumplab-header"></div>\\n<main>\\n'
    )
    FOOT = '\\n</main>\\n<div id="pumplab-footer"></div>\\n<script src="/assets/site.js" defer></script>\\n</body>\\n</html>\\n'

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
              + '</script>\\n')
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
        page = HEAD.format(title=escape(title), desc=escape(desc), url=url, ld=ld) + '\\n'.join(body) + FOOT
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
          + '</script>\\n')
    body = ['  <div class="wk-wrap" style="max-width:1000px">']
    body.append('    <div class="wk-crumb"><a href="/">홈</a> › 배터리 사전</div>')
    body.append('    <h1>배터리 사전</h1>')
    body.append('    <p style="max-width:720px">에너지·배터리 실험에서 만나는 용어 %d개를 위키 형식으로 설명합니다. 정의 → 개요 → 실무 포인트 → 같이 보기 순서로, 논문을 읽다 막히는 말을 빠르게 해소하는 것이 목적입니다.</p>' % len(terms))
    body.append('    <input type="search" id="wkq" placeholder="용어 검색 — 예: 하소, 과전압, sccm" style="width:100%;max-width:440px;border:2px solid #1E3A5F;border-radius:10px;padding:11px 16px;font-size:14px;margin:6px 0 8px" aria-label="용어 검색">')
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
    page = HEAD.format(title=escape(title), desc=escape(desc), url=url, ld=ld) + '\\n'.join(body) + js + FOOT
    write(os.path.join(outdir, 'index.html'), page)
    print('  배터리 사전: 항목 %d개 + 인덱스 정적 생성 (/wiki/)' % len(terms))
'''

anchor = 'def build_new_research():'
assert anchor in b
b = b.replace(anchor, FUNC.lstrip('\n') + '\n\n' + anchor, 1)

# main() 호출 추가 — build_all_products() 호출 뒤
call_anchor = '    build_all_products()'
i = b.find(call_anchor)
assert i > 0
j = b.find('\n', i)
b = b[:j] + '\n    build_wiki()  # 배터리 사전 (wiki.json SSOT)' + b[j:]

# sitemap 자동 등재 — 브랜드 스캔과 같은 방식으로 wiki/<slug>/ 추가
sm_anchor = "    _bdir = os.path.join(ROOT_DIR, 'brands')"
assert sm_anchor in b
wiki_scan = '''    _wdir = os.path.join(ROOT_DIR, 'wiki')
    if os.path.isdir(_wdir):
        for slug in sorted(os.listdir(_wdir)):
            idx = os.path.join(_wdir, slug, 'index.html')
            if os.path.isfile(idx):
                rel = 'wiki/%s/' % slug
                if rel not in _known and ('/' + rel) not in _red_srcs:
                    _auto.append((rel, '0.7', 'monthly'))
'''
b = b.replace(sm_anchor, wiki_scan + sm_anchor, 1)

io.open(bp, 'w', encoding='utf-8').write(b)
print('build.py patched')
