# -*- coding: utf-8 -*-
"""기존 리드플루이드 상세페이지 62종에 중국 본사 원문 이미지를 보강한다.
- 썸네일(dt-thumbs)에 제품컷 추가
- FAQ 앞에 '제조사 자료'(det-imgs) 섹션 추가 — 한글 캡션
구조는 건드리지 않고 두 곳에만 삽입한다. 앵커가 없으면 그 파일은 건너뛴다(리포트에 남김).
멱등: 이미 삽입된 파일(마커 존재)은 건너뛴다.
"""
import os, json, re, html, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PLAN = os.path.join(ROOT, '_ops/leadfluid_cn/phase2_plan.json')
MARK = '<!--cn-boost-->'

def thumb_html(slug, files):
    out = []
    for f in files:
        out.append('<button type="button" data-src="/img/leadfluid/%s" onclick="lfSwap(this)">'
                   '<img src="/img/leadfluid/%s" alt="%s 제품 사진" loading="lazy" '
                   'onerror="this.parentElement.style.display=\'none\'"></button>' % (f, f, html.escape(slug.upper())))
    return MARK + ''.join(out)

def figs_html(items):
    out = ['%s<h2 class="pkg-h">제조사 자료</h2><div class="det-imgs">' % MARK]
    for f, cap in items:
        out.append('<figure><img src="/img/leadfluid/%s" alt="%s" loading="lazy">'
                   '<figcaption>%s</figcaption></figure>' % (f, html.escape(cap), html.escape(cap)))
    out.append('<p class="pkg-note">제조사 원문 도판입니다. 캡션은 실험셋업연구소가 한글로 옮긴 것이며, '
               '도판 안의 수치·표기는 제조사 원문 그대로입니다.</p></div>')
    return ''.join(out)

def apply_one(slug, thumbs, figs, dry):
    p = os.path.join(ROOT, 'brands/leadfluid', slug, 'index.html')
    if not os.path.exists(p):
        return 'NOFILE', 0, 0
    h = open(p, encoding='utf-8').read()
    if MARK in h:
        return 'SKIP(이미 반영)', 0, 0
    nt = nf = 0
    # 1) 썸네일
    if thumbs:
        m = re.search(r'<div class="dt-thumbs">', h)
        if not m:
            return 'NO_THUMB_ANCHOR', 0, 0
        j = h.find('</div>', h.rfind('</button>', m.end(), m.end() + 20000))
        if j < 0:
            return 'NO_THUMB_CLOSE', 0, 0
        h = h[:j] + thumb_html(slug, thumbs) + h[j:]
        nt = len(thumbs)
    # 2) 제조사 자료 섹션 — FAQ h2 앞
    if figs:
        m = re.search(r'<h2 class="pkg-h">\s*자주 묻는 질문', h)
        if not m:
            m = re.search(r'<h2[^>]*>\s*자주 묻는 질문', h)
        if not m:
            return 'NO_FAQ_ANCHOR', nt, 0
        h = h[:m.start()] + figs_html(figs) + h[m.start():]
        nf = len(figs)
    if not h.rstrip().endswith('</html>'):
        return 'BROKEN_TAIL', 0, 0
    if not dry:
        open(p, 'w', encoding='utf-8').write(h)
    return 'OK', nt, nf

def main():
    dry = '--apply' not in sys.argv
    plan = json.load(open(PLAN, encoding='utf-8'))
    tot = {'OK': 0}
    lines = []
    for slug, v in sorted(plan.items()):
        if slug.startswith('_'):
            continue
        st, nt, nf = apply_one(slug, v.get('thumbs', []), v.get('figs', []), dry)
        tot[st] = tot.get(st, 0) + 1
        lines.append('  %-12s %-18s 썸네일+%d · 도판+%d' % (slug, st, nt, nf))
    print(('[미리보기] ' if dry else '[적용] ') + '결과:', tot)
    print('\n'.join(lines))
    if dry:
        print('\n실제 반영: python3 _ops/leadfluid_cn/phase2_apply.py --apply')

main()
