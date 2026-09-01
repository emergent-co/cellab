# 003편 v3: 사용자 검수 반영 16건
import os, re
p = 'magazine/insitu-li-dendrite-observation/index.html'
h = open(p, encoding='utf-8').read()
R = []
def rep(a, b, must=True):
    global h
    n = h.count(a)
    if must: assert n >= 1, a[:70]
    h = h.replace(a, b); R.append((n, a[:44]))

# 1) 타이틀·h1·메타
rep('리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003 | 실험셋업연구소',
    '측면 관찰용 인시츄 셀 CIS-OM-003 — In-situ Microscopic Observation System 시리즈 | 실험셋업연구소')
rep('<meta property="og:title" content="리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003">',
    '<meta property="og:title" content="측면 관찰용 인시츄 셀 CIS-OM-003 — In-situ Microscopic Observation System 시리즈">')
rep('"headline":"리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003",',
    '"headline":"측면 관찰용 인시츄 셀 CIS-OM-003 — In-situ Microscopic Observation System 시리즈",')
rep('<h1>리튬메탈 덴드라이트, 눈으로 확인하는 셋업<br>— 현미경용 인시츄 셀 CIS-OM-003</h1>',
    '<h1>In-situ Microscopic Observation System 시리즈<br>— 측면 관찰용 인시츄 셀 (표준형 CIS-OM-003)</h1>')
# 2) 연재 예정 삭제 + 바이라인 중앙정렬
rep('<div class="sd-meta">현미경용 인시츄 셀 시리즈 · CIS-OM-003 편 — 002 · 004 · 005 편 연재 예정</div>',
    '<div class="sd-meta">현미경용 인시츄 셀 시리즈 · CIS-OM-003 편</div>')
rep('<div class="sd-byline" style="font-size:13px;color:#8a8f98;margin:4px 0 2px">',
    '<div class="sd-byline" style="font-size:13px;color:#8a8f98;margin:4px 0 2px;text-align:center">')
# 3) 정답블록 두 줄
a = h.find('<div class="sd-answer">'); b = h.find('</div>', a) + 6
h = h[:a] + '''<div class="sd-answer">
    <b>CIS-OM-003은 광학현미경 아래에서 전지 계면을 실시간 관찰하는 밀봉 인시츄 셀입니다.</b><br>액체 전해질의 덴드라이트부터 전고체의 보이드·들뜸까지 한 셀로 측정이 가능합니다.
  </div>''' + h[b:]
# 4) 제품 소개 문단
rep('코인셀이 전압·효율 숫자만 남길 때, 이 셀은 도금·박리가 진행되는 <b>계면 그 자체</b>를 전압 곡선과 같은 시간축에서 보여줍니다.',
    '충방전 중 배터리 셀 안에서 일어나는 <b>계면의 변화(덴드라이트 등)</b>를 시각적으로 실시간 관찰하기 위해 만들어졌습니다.')
rep(' 실험셋업연구소가 Hefei In-situ Technology에서 소싱하며, 국내 견적·A/S를 지원합니다. <a href="/brands/hefei/om003-microscope-cell/" style="font-weight:800;color:#0F69AF">제품 상세·가격 보기 →</a>', '')
# 5) 기본구조: 확대 합성 이미지로 교체(적층 카드 내 이미지)
rep('src="/img/magazine/insitu-cell-stack.jpg" alt="CIS-OM-003 셀 내부 적층 분해도',
    'src="/img/magazine/insitu-003-structure.jpg" alt="CIS-OM-003 관찰창 부위를 원형으로 표시하고 확대한 내부 적층 분해도')
rep('style="display:block;width:100%;max-width:560px;margin:0 auto;border:1px solid #C9D6E6;border-radius:10px;background:#fff">',
    'style="display:block;width:100%;max-width:680px;margin:0 auto;border:1px solid #C9D6E6;border-radius:10px;background:#fff">')
# 6) Specification (h2·라벨·값 영어)
rep('<h2 style="margin-top:26px">스펙 — 이 창이면 보유 현미경으로 됩니다</h2>', '<h2 style="margin-top:26px">Specification</h2>')
rep('<b style="font-size:16px;color:#2A2570">주요 스펙</b>', '<b style="font-size:16px;color:#2A2570">CIS-OM-003</b>')
rep('<span>몸체 · 전극</span><span>PEEK 몸체 · 고순도 티타늄 <b>가동 전극</b>(다른 재질 커스텀 가능)</span>',
    '<span>Body · Electrode</span><span>PEEK body · high-purity titanium <b>movable electrodes</b> (other materials customizable)</span>')
rep('<span>관찰창</span><span>석영 Φ24 mm · 두께 <b>0.05 mm</b></span>',
    '<span>Window</span><span>Quartz Φ24 mm · thickness <b>0.05 mm</b></span>')
rep('<span>시료-창 상면</span><span><b>약 0.6 mm</b> — 더 얇게 커스텀 가능</span>',
    '<span>Sample-to-window</span><span>approx. <b>0.6 mm</b> (thinner customizable)</span>')
rep('<span>주액 · 퍼지</span><span><b>별도 주액 피팅</b> + 가스 퍼지 → 주사기 기포 제거 대응</span>',
    '<span>Liquid · Gas</span><span><b>Separate liquid-addition fitting</b> + gas purge port</span>')
rep('<span>전고체 옵션</span><span>정압 가압 모듈 <b>최대 6 MPa</b>(60 kg) · 상향 커스텀</span>',
    '<span>Solid-state option</span><span>Pressurized module, max <b>6 MPa</b> (60 kg) · higher customizable</span>')
rep('<span>시료</span><span>최대 10×10 mm · 두께 0.6~2 mm</span>',
    '<span>Sample</span><span>10×10 mm rectangle · thickness 0.6–2 mm</span>')
rep('<span>본체 크기</span><span>약 <b>60 × 70 × 30 mm</b> — 현미경 스테이지 호환 확인용</span>',
    '<span>Dimensions</span><span>approx. <b>60 × 70 × 30 mm</b></span>')
# 7) 호환 문단 삭제
h = re.sub(r'\s*<p>호환 확인은 세 수치면 끝납니다[^<]*(<b>[^<]*</b>[^<]*)*</p>', '', h)
# 8) Features
rep('<h2 style="margin-top:26px">특징 넷 — 이 셀이 해결하는 것</h2>', '<h2 style="margin-top:26px">Features</h2>')
rep('역할은 절연이 아니라 두 전극 사이에', '절연의 의미도 있지만, 두 전극 사이에')
rep(' — 시판 분리막을 끼우면 틈이 사라져 관찰 자체가 어려워집니다', '')
rep('순서가 그대로 됩니다. 가스 퍼지 포트로 분위기 유지도 됩니다.',
    '순서로 계면의 일정한 전류밀도를 구현해, 실험의 정확성과 재현성을 보장합니다.')
rep('봅니다. 사각 시료 성형이 문제라면 <b>필렛 다이 제공·원형 시료 가이드 제작</b>으로 지원합니다.',
    '봅니다(사각형 펠렛 다이 필요).')
# 9) 광학계 문장
rep('<b>인시츄 배터리 클램프가 달린 2층 스테이지</b>가 일반 금속현미경과의 차이입니다.',
    '<b>인시츄 배터리 클램프가 달린 2층 스테이지</b>를 보여드리니 실험에 참고하세요(구매 문의).')
# 10) 시리즈 라인업: 제목·intro 삭제·표 상시 노출·003 행 추가(하이라이트)
rep('<h2 style="margin-top:26px">시리즈 라인업 — 002 · 004 · 005</h2>', '<h2 style="margin-top:26px">시리즈 라인업</h2>')
rep('<p>같은 관찰 방식에 시료·온도 조건만 다릅니다. 각 모델은 별도 편으로 연재합니다.</p>', '')
a = h.find('<details class="msc-acc">'); b = h.find('</details>', a) + 10
assert a > 0
tbl_a = h.find('<table class="msc-tbl">', a); tbl_b = h.find('</table>', tbl_a) + 8
tbl = h[tbl_a:tbl_b]
tbl = tbl.replace('<tbody>', '''<tbody>
          <tr class="hot"><td><b>CIS-OM-003</b><br>표준형 <span style="font-size:11px;font-weight:800;color:#0F69AF">← 이 페이지</span></td><td>PEEK · 고순도 Ti 가동 전극(재질 커스텀)</td><td>석영창 Φ24 mm · 두께 0.05 mm · 최소 작동거리 1 mm</td><td>상온 · 가압 모듈 옵션 최대 6 MPa</td><td>시료 10×10 mm · 0.6~2 mm · 액체·전고체 겸용</td></tr>''')
h = h[:a] + tbl + h[b:]
# 11) 팝업 장비 리스트 교체
a = h.find('var specs=['); b = h.find('];', a) + 2
assert a > 0
h = h[:a] + '''var specs=[
    ["CIS-OM-003 관찰 셀","측면 관찰 표준형 — 석영창 0.05mm·별도 주액 피팅"],
    ["가압 전고체 모듈(옵션)","정압 최대 6 MPa(60 kg) · 상향 커스텀"],
    ["덴드라이트 관찰 전용 현미경","대물 5~100× 5종 · 인시츄 배터리 클램프 스테이지 · U820 카메라"],
    ["글러브박스","Ar 분위기 조립·이송"],
    ["포텐시오스탯·사이클러","정전류 도금·박리, 전압 로그 기록"],
    ["튜브·피팅","주액·가스 퍼지 라인"],
    ["밸브","주액 라인 개폐"],
    ["주사기","전해액 주입·음압 기포 제거"]
  ];''' + h[b:]

assert h.count('</html>') == 1 and h.rstrip().endswith('</html>')
fo = open(p, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('v3 저장 —', len(R), '건 치환')
