# -*- coding: utf-8 -*-
# 상세페이지 오렌지 액센트 → 퍼플 통일 (가격·경고 박스는 오렌지 유지), dt-sum 왼쪽 색 바 제거
import glob, io, re

PROTECT = [
    re.compile(r'\.warn[a-z\- ]*\{[^}]*\}'),          # 경고 박스 계열
    re.compile(r'\.pfrom\{[^}]*\}'),                  # 정가 강조
    re.compile(r'\.ds-price[^{]*\{[^}]*\}'),          # 카드 가격
    re.compile(r'<b style="color:#(?:C2410C|E8632C)">정가[^<]*</b>'),  # 인라인 정가 강조
]

def convert(p):
    s = io.open(p, encoding='utf-8').read()
    o = s
    # 1) dt-sum 왼쪽 색 바 제거
    s = s.replace('border-left:3px solid #C2410C;border-radius:4px 12px 12px 4px', 'border-radius:12px')
    s = s.replace('border-left:3px solid #E8632C;border-radius:4px 12px 12px 4px', 'border-radius:12px')
    s = s.replace('border-left:3px solid #2A2570;border-radius:4px 12px 12px 4px', 'border-radius:12px')
    s = s.replace('border-left:3px solid #3B3695;border-radius:4px 12px 12px 4px', 'border-radius:12px')
    # 2) 보호 구간 치환
    saved = []
    def stash(m):
        saved.append(m.group(0))
        return '\x00PROT%d\x00' % (len(saved) - 1)
    for rx in PROTECT:
        s = rx.sub(stash, s)
    # 3) 오렌지 액센트 → 퍼플
    s = s.replace('#C2410C', '#2A2570').replace('#c2410c', '#2a2570')
    s = s.replace('#E8632C', '#3B3695').replace('#e8632c', '#3b3695')
    # 잔여 틸/연녹 배경(재생성 페이지)
    s = s.replace('#eef4f1', '#eaf4fb').replace('#EEF4F1', '#EAF4FB')
    # 4) 복원
    for i, seg in enumerate(saved):
        s = s.replace('\x00PROT%d\x00' % i, seg)
    if s != o:
        assert s.rstrip().endswith('</html>'), p
        io.open(p, 'w', encoding='utf-8').write(s)
        return 1
    return 0

n = 0
for p in glob.glob('brands/*/*/index.html') + glob.glob('brands/*/*/*/index.html'):
    n += convert(p)
print('converted:', n)
# 검증: 남은 비보호 오렌지 (warn·price 밖)
import collections
left = 0
for p in glob.glob('brands/*/*/index.html'):
    s = io.open(p, encoding='utf-8').read()
    t = s
    for rx in PROTECT:
        t = rx.sub('', t)
    left += t.count('#C2410C') + t.count('#E8632C')
print('unprotected orange left:', left)
