# -*- coding: utf-8 -*-
"""상세페이지 색 → assets/site.css 머크 토큰 1곳으로 전역 통일 (2026-09).

무엇을 하나
  1) 페이지 인라인 <style>·style="" 안의 구색(테라코타 #C2410C / 오렌지 #E8632C /
     경고 #FFF7ED+#FED7AA)을 CLAUDE.md 확정 머크값으로 교정하고,
  2) 확정 머크값까지 전부 var(--merck-*) 토큰 참조로 바꾼다.
  → 이후 팔레트 변경은 assets/site.css :root 8줄만 고치면 전 상세페이지에 반영된다.
  3) CLAUDE.md '좌측 포인트 바 금지' 위반인 .buy-box 의 border-left-width:4px 제거.

JSON-LD·SVG·본문 텍스트는 건드리지 않는다(<style> 블록과 style="" 속성만 대상).
멱등(idempotent) — 여러 번 돌려도 결과가 같다.
"""
import io, os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ── 1단계: 구색 → 확정 머크 hex
LEGACY = [
    # .buy-box : 좌측 포인트 바 제거 + 연배경/테두리 머크화
    ('border:1px solid #2A2570;border-left-width:4px;', 'border:1px solid #D8E4F2;'),
    ('border:1px solid #C2410C;border-left-width:4px;', 'border:1px solid #D8E4F2;'),
    ('.buy-box{border:1px solid #D8E4F2;border-radius:12px;background:#FFF7ED',
     '.buy-box{border:1px solid #D8E4F2;border-radius:12px;background:#EAF4FB'),
    ('.buy-box{border:1px solid #D8E4F2;border-radius:6px 12px 12px 6px;background:#FFF7ED',
     '.buy-box{border:1px solid #D8E4F2;border-radius:12px;background:#EAF4FB'),
    # 경고 박스 → 머크 옐로 계열
    ('#FFF7ED', '#FDF6E9'), ('#fff7ed', '#FDF6E9'),
    ('#FED7AA', '#F3E0BC'), ('#fed7aa', '#F3E0BC'),
    # 테라코타·오렌지 퇴출
    ('color:#C2410C', 'color:#0F69AF'), ('color:#c2410c', 'color:#0F69AF'),
    ('#C2410C', '#3B3695'), ('#c2410c', '#3B3695'),
    ('color:#E8632C', 'color:#0F69AF'), ('color:#e8632c', 'color:#0F69AF'),
    ('#E8632C', '#3B3695'), ('#e8632c', '#3B3695'),
    ('#9A3412', '#2A2570'), ('#1E3A5F', '#3B3695'), ('#0D6E6E', '#3B3695'),
    ('#1a6e56', '#3B3695'), ('#1A6E56', '#3B3695'),
    ('rgba(194,65,12,.92)', 'rgba(59,54,149,.92)'),
    ('#eef4f1', '#EAF4FB'), ('#EEF4F1', '#EAF4FB'),
]

# ── 2단계: 확정 hex → site.css 토큰
TOKEN = [
    ('#3B3695', 'var(--merck)'), ('#3b3695', 'var(--merck)'),
    ('#2A2570', 'var(--merck-d)'), ('#2a2570', 'var(--merck-d)'),
    ('#0F69AF', 'var(--merck-link)'), ('#0f69af', 'var(--merck-link)'),
    ('#EAF4FB', 'var(--merck-soft)'), ('#eaf4fb', 'var(--merck-soft)'),
    ('#D8E4F2', 'var(--merck-line)'), ('#d8e4f2', 'var(--merck-line)'),
    ('#FDF6E9', 'var(--warn-bg)'), ('#F3E0BC', 'var(--warn-line)'),
    ('#EF9F27', 'var(--merck-yellow)'),
    ('#B22222', 'var(--danger)'),
]

def conv(css):
    for a, b in LEGACY:
        css = css.replace(a, b)
    for a, b in TOKEN:
        css = css.replace(a, b)
    return css

RX_STYLE = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S)
RX_ATTR  = re.compile(r'style="([^"]*)"')

def patch_html(p):
    s = o = io.open(p, encoding='utf-8').read()
    s = RX_STYLE.sub(lambda m: m.group(1) + conv(m.group(2)) + m.group(3), s)
    s = RX_ATTR.sub(lambda m: 'style="' + conv(m.group(1)) + '"', s)
    if s == o:
        return 0
    assert s.rstrip().endswith('</html>'), p
    io.open(p, 'w', encoding='utf-8').write(s)
    return 1

def patch_py(p):
    """생성기(.py) — 문자열 리터럴 안의 CSS도 같은 토큰을 쓰게 한다."""
    s = o = io.open(p, encoding='utf-8').read()
    s = conv(s)
    if s == o:
        return 0
    io.open(p, 'w', encoding='utf-8').write(s)
    return 1

if __name__ == '__main__':
    pages = sorted(set(glob.glob('brands/*/*/index.html') + glob.glob('brands/*/*/*/index.html')))
    n = sum(patch_html(p) for p in pages)
    print('상세페이지 %d장 중 %d장 갱신' % (len(pages), n))

    tpl = patch_html('_ops/tpl/product.html')
    print('_ops/tpl/product.html:', '갱신' if tpl else '변화없음')

    for g in ('_ops/build_page.py', '_ops/build_web.py', '_ops/hench/gen_hench.py'):
        if os.path.exists(g):
            print(' ', g, ':', '갱신' if patch_py(g) else '변화없음')

    # 검증 — 상세페이지에 금지색이 남아 있으면 실패
    BAN = ('#C2410C', '#c2410c', '#E8632C', '#e8632c', '#1E3A5F',
           '#0D6E6E', '#1a6e56', '#FFF7ED', '#fff7ed', '#FED7AA', '#fed7aa')
    left = []
    for p in pages:
        s = io.open(p, encoding='utf-8').read()
        css = ''.join(m.group(2) for m in RX_STYLE.finditer(s)) + ''.join(RX_ATTR.findall(s))
        for b in BAN:
            if b in css:
                left.append((p, b))
    print('잔여 금지색:', len(left), left[:5])
    sys.exit(1 if left else 0)
