# -*- coding: utf-8 -*-
"""정리 끝난 썸네일(img/product/sh-cards-clean/<슬러그>.jpg)을 상세페이지에 반영.

바꾸는 곳 4군데 (파일 1개씩 열어서 편집 — 일괄 sed 금지 규칙 준수):
  1) .dt-img 대표사진 <img src>
  2) og:image
  3) twitter:image
  4) Product JSON-LD 의 image

사용법 (저장소 루트에서):
  python _ops/apply_sh_clean_thumbs.py               # 미리보기(변경 없음), 기본 5개
  python _ops/apply_sh_clean_thumbs.py --write       # 실제 반영, 5개
  python _ops/apply_sh_clean_thumbs.py --write --all # 전부 반영
  python _ops/apply_sh_clean_thumbs.py --write furnace-tube-1200  # 특정 슬러그만
"""
import io, os, re, sys

BASE = os.path.join('brands', 'sh-scientific')
CLEAN_DIR = os.path.join('img', 'product', 'sh-cards-clean')

argv = sys.argv[1:]
WRITE = '--write' in argv
ALL = '--all' in argv
LIMIT = 5
picks = []
i = 0
while i < len(argv):
    a = argv[i]
    if a in ('--write', '--all'):
        pass
    elif a == '--limit':
        i += 1; LIMIT = int(argv[i])
    elif a.startswith('--limit='):
        LIMIT = int(a.split('=', 1)[1])
    elif not a.startswith('--'):
        picks.append(a)
    i += 1
if picks:
    ALL = True


def targets():
    out = []
    for slug in sorted(os.listdir(BASE)):
        f = os.path.join(BASE, slug, 'index.html')
        if not os.path.isfile(f):
            continue
        if picks and slug not in picks:
            continue
        img = os.path.join(CLEAN_DIR, slug + '.jpg')
        if not os.path.exists(img):
            continue
        h = io.open(f, encoding='utf-8').read()
        m = re.search(r'<div class="dt-img">.*?<img[^>]*src="([^"]+)"', h, re.S)
        if not m:
            continue
        if m.group(1).startswith('/img/product/sh-cards-clean/'):
            continue          # 이미 반영됨
        out.append((slug, f, m.group(1)))
    return out


todo = targets()
if not todo:
    sys.exit('반영할 대상이 없습니다. (정리된 사진이 없거나 이미 전부 반영됨)')
batch = todo if ALL else todo[:LIMIT]
print('대상 %d개 → 이번 실행 %d개  [%s]\n' % (
    len(todo), len(batch), '실제 반영' if WRITE else '미리보기 (--write 를 붙이면 반영)'))

changed = 0
for slug, path, old in batch:
    new = '/img/product/sh-cards-clean/%s.jpg' % slug
    h = io.open(path, encoding='utf-8').read()
    before = h
    # 1) 대표사진
    def _hero(m):
        return m.group(0).replace(m.group(1), new)
    h = re.sub(r'(?s)(?<=<div class="dt-img">).*?<img[^>]*src="([^"]+)"',
               lambda m: m.group(0).replace('src="%s"' % m.group(1), 'src="%s"' % new),
               h, count=1)
    # 2) og:image / 3) twitter:image
    h = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com' + new + m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com' + new + m.group(2), h, count=1)
    # 4) Product JSON-LD image (문자열 형태만 — 배열이면 첫 항목)
    h = re.sub(r'("image"\s*:\s*")[^"]*(")',
               lambda m: m.group(1) + 'https://rndsetup.com' + new + m.group(2), h, count=1)

    if h == before:
        print('  [건너뜀] %-34s 치환할 자리를 못 찾음' % slug)
        continue
    if not h.rstrip().endswith('</html>'):
        print('  [중단] %-34s 결과가 </html> 로 끝나지 않음 — 저장하지 않음' % slug)
        continue
    print('  [%s] %-34s %s → %s' % ('반영' if WRITE else '예정', slug, old[:46], new))
    if WRITE:
        io.open(path, 'w', encoding='utf-8').write(h)
        # 저장 직후 재확인 (잘림 사고 방지)
        chk = io.open(path, encoding='utf-8').read()
        if not chk.rstrip().endswith('</html>'):
            sys.exit('!! %s 저장 후 파일이 잘렸습니다. git 에서 즉시 복원하세요.' % path)
    changed += 1

print('\n%s %d개   |   남은 대상 %d개' % ('반영 완료' if WRITE else '반영 예정', changed,
                                           len(todo) - (changed if WRITE else 0)))
if WRITE:
    print('다음: python _build/build.py  →  .\\go.ps1 "삼흥 대표사진 복구"')
