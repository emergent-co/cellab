# 인시츄 003편 v2: 제품 우선 구성(소개→구조→스펙→특징→조립→가능한 실험→시리즈)
import os, re

p = 'magazine/insitu-li-dendrite-observation/index.html'
h = open(p, encoding='utf-8').read()

def bal(start_pat, tag='div'):
    """start_pat 위치부터 태그 균형으로 블록 추출"""
    a = h.find(start_pat)
    assert a >= 0, start_pat[:60]
    d, i = 0, a
    op, cl = '<' + tag, '</' + tag + '>'
    while i < len(h):
        no = h.find(op, i); nc = h.find(cl, i)
        if nc < 0: raise AssertionError('unbalanced')
        if 0 <= no < nc:
            d += 1; i = no + len(op)
        else:
            d -= 1; i = nc + len(cl)
            if d == 0: return h[a:i]
    raise AssertionError('eof')

CARD  = bal('<div style="background:#fff;border:1px solid #D8E4F2;border-radius:12px;padding:16px 18px;margin:4px 0 14px">')
STACK = bal('<div style="background:#F4F8FC;border:1px solid #D8E4F2;border-radius:12px;padding:14px 16px;margin:0 0 14px">')
SYR   = re.search(r'<figure style="margin:14px 0 4px">.*?insitu-bubble-syringe.*?</figure>', h, re.S).group(0)
VID   = re.search(r'<div class="msc-vid">.*?</div>\s*<p class="msc-note">[^<]*bilibili[^<]*</p>', h, re.S).group(0)
SCOPEF= re.search(r'<figure style="margin:12px 0 10px">\s*<img src="/img/magazine/hefei-dendrite-scope\.jpg".*?</figure>', h, re.S).group(0)
SCOPES= bal('<div class="bx-spec" style="max-width:560px;margin:6px 0 4px">')
RES   = re.findall(r'<figure[^>]*>\s*<img src="/img/magazine/hefei-(?:depth-fusion|timelapse)\.jpg".*?</figure>', h, re.S)
LIN_A = h.find('<details class="msc-acc">'); LIN_B = h.find('</details>', LIN_A) + 10
LINEUP = h[LIN_A:LIN_B]
DL    = bal('<div class="msc-dl">')
BUY   = bal('<div style="background:#F4F8FC;border:1px solid #D8E4F2;border-radius:10px;padding:12px 16px;margin:6px 0 14px')
assert len(RES) == 2

# 카드 제목행: 링크는 제품소개로 이동하므로 '주요 스펙'으로
CARD = CARD.replace('<b style="font-size:16px;color:#2A2570">표준형 CIS-OM-003</b>',
                    '<b style="font-size:16px;color:#2A2570">주요 스펙</b>')

ANSWER = '''<div class="sd-answer">
    <b>CIS-OM-003은 광학현미경 아래에서 전지 계면을 실시간 관찰하는 밀봉 인시츄 셀입니다.</b> 석영창 0.05 mm · 별도 주액 피팅 · 정압 가압 모듈(최대 6 MPa)로, 액체 전해질의 덴드라이트부터 전고체의 보이드·들뜸까지 <b>한 셀에서</b> 관찰합니다. 풀셀·하프셀 모두 구성 가능합니다.
  </div>'''

BODY = f'''{ANSWER}

  <div class="sd-body">
    <h2>CIS-OM-003 — 현미경 위에서 전지 내부를 보는 셀</h2>
    <p><b>현미경용 인시츄 셀 시리즈(In-situ Microscopic Observation System)</b>의 표준형입니다. 코인셀이 전압·효율 숫자만 남길 때, 이 셀은 도금·박리가 진행되는 <b>계면 그 자체</b>를 전압 곡선과 같은 시간축에서 보여줍니다. 실험셋업연구소가 Hefei In-situ Technology에서 소싱하며, 국내 견적·A/S를 지원합니다. <a href="/brands/hefei/om003-microscope-cell/" style="font-weight:800;color:#0F69AF">제품 상세·가격 보기 →</a></p>
    <figure style="margin:14px 0 6px">
      <img src="/img/magazine/insitu-003-hero.jpg" alt="CIS-OM-003 현미경용 인시츄 관찰 셀 — PEEK 몸체, 석영 관찰창, 양측 티타늄 가동 전극, 하단 주액·퍼지 피팅" loading="lazy" style="display:block;width:100%;max-width:520px;margin:0 auto;border:1px solid var(--line);border-radius:12px;background:#fff">
    </figure>
    {DL}

    <h2 style="margin-top:26px">기본 구조</h2>
    {STACK}

    <h2 style="margin-top:26px">스펙 — 이 창이면 보유 현미경으로 됩니다</h2>
    {CARD}
    <p>호환 확인은 세 수치면 끝납니다 — <b>창 두께 0.05 mm(Φ24) · 창-샘플 거리 0.6 mm · 본체 60×70×30 mm</b>. 일반 금속현미경 대물의 작동거리와 스테이지 공간에 이 수치를 대조하면 되고, 단초점 대물이면 창-샘플 거리를 더 얇게 커스텀합니다.</p>

    <h2 style="margin-top:26px">특징 넷 — 이 셀이 해결하는 것</h2>
    <h3 style="font-size:16px;color:#2A2570;margin:16px 0 4px">① PEEK 격벽 — 덴드라이트가 자랄 공간</h3>
    <p>적층 가운데의 <b>격벽(세퍼레이터 자리)</b>은 소모품 분리막이 아니라 <span class="hl">반영구 PEEK 부품</span>입니다. 역할은 절연이 아니라 두 전극 사이에 <b>덴드라이트가 자랄 공간을 확보</b>하는 것 — 시판 분리막을 끼우면 틈이 사라져 관찰 자체가 어려워집니다. 관찰 간격이 다르게 필요하면 <b>격벽 두께를 커스텀 제작</b>합니다.</p>
    <h3 style="font-size:16px;color:#2A2570;margin:16px 0 4px">② 별도 주액 피팅 — 기포 없는 시야</h3>
    <p>창 아래 기포는 시야를 가리고 <b>국부 전류밀도를 왜곡</b>합니다. 이 셀은 <span class="hl">전해액 주입 피팅이 별도로</span> 있어, 글러브박스 건조 조립·밀봉 → 포트 주액 → <span class="hl">주사기 음압으로 잔류 기포 제거</span> 순서가 그대로 됩니다. 가스 퍼지 포트로 분위기 유지도 됩니다.</p>
    {SYR}
    <h3 style="font-size:16px;color:#2A2570;margin:16px 0 4px">③ 한 셀로 전고체까지</h3>
    <p>정압 가압 모듈(<b>최대 6 MPa</b>, 고압 오더메이드)을 걸면 전고체 관찰 셀이 됩니다. 체결 압력은 <b>토크 렌치 값으로 판단</b>하고, 격벽 없이 적층해 계면의 <span class="hl">보이드·들뜸(박리)</span>을 봅니다. 사각 시료 성형이 문제라면 <b>필렛 다이 제공·원형 시료 가이드 제작</b>으로 지원합니다.</p>
    <h3 style="font-size:16px;color:#2A2570;margin:16px 0 4px">④ 풀셀·하프셀 모두</h3>
    <p>양쪽에 리튬을 두면 대칭(하프)셀, 한쪽을 양극 등 <b>다른 전극으로 바꾸면 풀셀</b> 구성 — 가동식 Ti 전극이 시료 두께에 맞춰 조여지므로 전기 접촉만 잡히면 됩니다. 전극 재질 커스텀도 가능합니다.</p>

    <h2 style="margin-top:26px">조립 영상 — 10분이면 끝납니다</h2>
    {VID}

    <h2 style="margin-top:26px">가능한 실험 — 무엇이 보이나</h2>
    <p>정전류 사이클을 걸며 <b>촬영 프레임과 전압 로그를 타임스탬프로 묶으면</b>, 전압 곡선의 변곡이 어떤 계면 사건인지 1:1로 확인됩니다 — 액체 전해질에서는 <span class="hl">덴드라이트 성장 ↔ 피트 전환</span>, 전해액·첨가제·전류밀도별 형상 비교, 전고체(가압)에서는 <span class="hl">보이드·들뜸</span> 진행. 아연계 등 수계 전지도 같은 방식입니다.</p>
    <h3 style="font-size:16px;color:#2A2570;margin:18px 0 4px">공통 광학계 — 덴드라이트 관찰 전용 현미경</h3>
    <p>시리즈 전 모델이 함께 쓰는 전용 광학계입니다. <b>덴드라이트 관찰 전용 대물 5종(5~100×)</b>과 <b>인시츄 배터리 클램프가 달린 2층 스테이지</b>가 일반 금속현미경과의 차이입니다.</p>
    {SCOPEF}
    {SCOPES}
    {RES[0]}
    {RES[1]}

    <h2 style="margin-top:26px">시리즈 라인업 — 002 · 004 · 005</h2>
    <p>같은 관찰 방식에 시료·온도 조건만 다릅니다. 각 모델은 별도 편으로 연재합니다.</p>
    {LINEUP}
    {BUY}
  </div>

'''

a = h.find('<div class="sd-answer">')
b = h.find('  <h2 style="font-family:var(--serif)')
assert 0 < a < b
h = h[:a] + BODY + h[b:]

assert h.count('</html>') == 1 and h.rstrip().endswith('</html>')
for k, c in [('sd-answer', 1), ('msc-dl"', None), ('insitu-003-hero', 1), ('id="msc-ov"', 1),
             ('msc-vid', None), ('dendrite-scope', 1), ('depth-fusion', 1), ('bilibili', None)]:
    if c is not None:
        assert h.count(k) == c, (k, h.count(k))
fo = open(p, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('v2 저장')
for m in re.findall(r'<h[23][^>]*>([^<]{1,46})', h):
    if 'msc' not in m: print(' -', m)
