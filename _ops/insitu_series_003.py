# 인시츄 글: 논문 요소 제거 + '현미경용 인시츄 셀 시리즈' 003편으로 재구성
import os, re

p = 'blog/insitu-li-dendrite-observation/index.html'
h = open(p, encoding='utf-8').read()

# ── 1) head: 타이틀·메타에서 논문 제거 ──
h = h.replace('리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — in-situ 광학 관찰 셀 (ACS Cent. Sci. 2016 · Sci. Adv. 2022) | 실험셋업연구소',
              '리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003 | 실험셋업연구소')
h = re.sub(r'<meta name="description" content="[^"]*">',
 '<meta name="description" content="리튬메탈 덴드라이트 관찰용 현미경용 인시츄 셀 CIS-OM-003 셋업 가이드. 셀 구조·조립, 격벽(PEEK)의 역할, 별도 주액 피팅과 주사기 음압 기포 제거, 창 스펙(석영 0.05mm)·현미경 호환, 전고체 가압(최대 6 MPa) 겸용까지 — 액체·전고체 한 셀로 관찰하는 방법을 정리했습니다.">', h, count=1)
h = h.replace('<meta property="og:title" content="리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — in-situ 광학 관찰 셀">',
              '<meta property="og:title" content="리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003">')
# TechArticle: headline·citation 제거
h = h.replace('"headline":"리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — in-situ 광학 관찰 셀",',
              '"headline":"리튬메탈 덴드라이트, 눈으로 확인하는 셋업 — 현미경용 인시츄 셀 CIS-OM-003",')
h = re.sub(r'"citation":\[.*?\],\n', '', h, flags=re.S, count=1)

# ── 2) FAQ LD: 논문 언급 제거 ──
h = re.sub(r'석영 관찰창이 있는 밀봉형 in-situ 전기화학 셀을 광학현미경 아래 두고, 정전류 사이클의 전압 곡선과 영상을 타임스탬프로 동기화해 기록합니다\. Wood 등[^"]*보였습니다\.',
 '석영 관찰창이 있는 밀봉형 인시츄 전기화학 셀을 광학현미경 아래 두고, 정전류 사이클의 전압 곡선과 영상을 타임스탬프로 동기화해 기록합니다. 글러브박스에서 조립한 셀을 스테이지에 거치하고, 전압 곡선의 변곡(덴드라이트 성장↔피트 전환 등)을 영상과 1:1로 대응시키는 방식입니다.', h, count=1)
h = h.replace('정압 가압(논문 5 MPa, 시판 모듈 최대 6 MPa)', '정압 가압(5 MPa급, 모듈 최대 6 MPa)')

# ── 3) 상단: sd-meta·byline·요약 ──
h = h.replace('<h1>리튬메탈 덴드라이트, 눈으로 확인하는 셋업<br>— in-situ 광학 관찰 셀</h1>',
              '<h1>리튬메탈 덴드라이트, 눈으로 확인하는 셋업<br>— 현미경용 인시츄 셀 CIS-OM-003</h1>')
h = h.replace('<div class="sd-meta">2016 · ACS Central Science (NREL·Michigan) &nbsp;+&nbsp; 2022 · Science Advances</div>',
              '<div class="sd-meta">현미경용 인시츄 셀 시리즈 · CIS-OM-003 편 — 002 · 004 · 005 편 연재 예정</div>')
summary_new = '''<div class="sd-summary">
    <h3>셋업 요약</h3>
    <div class="row"><span class="k">시리즈</span><span>현미경용 인시츄 셀 (In-situ Microscopic Observation System)</span></div>
    <div class="row"><span class="k">이 편</span><span><b>CIS-OM-003</b> — 액체·전고체 겸용 표준형</span></div>
    <div class="row"><span class="k">핵심 장비</span><span><b>CIS-OM-003 관찰 셀 + 덴드라이트 관찰 전용 현미경 + 정전류 사이클러</b></span></div>
    <div class="row"><span class="k">제어</span><span>정전류 도금·박리 · 전압-영상 타임스탬프 동기 · (전고체) 정압 가압</span></div>
    <div class="row"><span class="k">분야</span><span>#리튬메탈 #덴드라이트 #인시츄셀 #전고체</span></div>
  </div>'''
a = h.find('<div class="sd-summary">'); b = h.find('</div>', h.find('DOI', a)) + 6
assert a > 0 and 'DOI' in h[a:b]
h = h[:a] + summary_new + h[b:]

# ── 4) 조건표 ①·② 섹션 통째 제거 ──
a = h.find('<h2>셋업 조건 ① — 액체 전해질 (논문 수치 기준)</h2>')
b = h.find('<h2 style="margin-top:26px">창 스펙과 현미경 환경</h2>')
assert 0 < a < b
h = h[:a] + h[b:]
a = h.find('<h2>셋업 조건 ② — 전고체 (논문 수치 기준)</h2>')
b = h.find('<h2 style="margin-top:26px">변형 모델 사양</h2>')
assert 0 < a < b
h = h[:a] + h[b:]

# ── 5) 본문 논문 흔적 제거·문구 정리 ──
h = re.sub(r'\s*<span style="font-size:12\.5px;color:#8a8f98">\(셋업 출처:[^<]*</span>', '', h)
h = h.replace('<p>보통은 이렇게 셋팅합니다. 글러브박스(H₂O·O₂ &lt; 1 ppm)에서 O링 밀봉으로 조립한 Li–Li 가시화 셀을 반사광 현미경(5× 대물, WD 31 mm) 아래 두고, 정전류(5 mA/cm²급)로 사이클을 돌리며 <b>반주기당 수십 프레임</b>을 촬영해 전압 로그와 타임스탬프로 묶습니다. </p>',
              '<p>순서는 단순합니다. 글러브박스에서 건조 조립 → 현미경 스테이지 거치 → 정전류 사이클을 걸며 <b>촬영 프레임과 전압 로그를 타임스탬프로 묶기</b>. 전압 곡선의 변곡이 어떤 계면 사건인지 영상으로 확인하는 것이 목적입니다.</p>')
h = h.replace('아래 두 논문이 이 방법론의 기준점입니다. 하나는 액체 전해질에서, 하나는 전고체에서.', '')

# ── 6) 시리즈 소개 문단 (구조 섹션 인트로 뒤) ──
h = h.replace('<p>이 실험에 쓰는 관찰 셀입니다 — <b>기밀 · 별도 주액 피팅 · 얇은 관찰창 · 정압 가압</b>을 갖춘 표준형. 실험셋업연구소가 Hefei In-situ Technology에서 소싱합니다.</p>',
 '''<p><b>현미경용 인시츄 셀 시리즈(CIS-OM)</b>는 광학현미경 아래에서 전지 계면을 실시간 관찰하는 밀봉 셀 라인업입니다. 이 편은 그 표준형 — <b>기밀 · 별도 주액 피팅 · 얇은 관찰창 · 정압 가압</b>을 갖춘 <b>CIS-OM-003</b>입니다. 실험셋업연구소가 Hefei In-situ Technology에서 소싱합니다.</p>''')
h = h.replace('<span>몸체 · 전극</span><span>PEEK 몸체 · 고순도 티타늄 <b>가동 전극</b>(악어클립 체결)</span>',
              '<span>몸체 · 전극</span><span>PEEK 몸체 · 고순도 티타늄 <b>가동 전극</b>(다른 재질 커스텀 가능)</span>')

# ── 7) 창 스펙·현미경 섹션 재작성 (기존 OPR-DM01 블록 → 공통 광학계) ──
a = h.find('<h2 style="margin-top:26px">창 스펙과 현미경 환경</h2>')
b = h.find('<h2>전고체까지 같은 셀로')
assert 0 < a < b
# 결과 이미지 2장은 보존
seg = h[a:b]
figs = re.findall(r'<figure[^>]*>\s*<img src="/img/blog/hefei-(?:depth-fusion|timelapse)\.jpg".*?</figure>', seg, flags=re.S)
scope = '''<h2 style="margin-top:26px">창 스펙과 현미경 호환</h2>
    <p>보유 현미경과의 호환은 위 카드의 세 수치 — <b>창 두께 0.05 mm(Φ24) · 창-샘플 거리 0.6 mm · 본체 60×70×30 mm</b> — 를 대물 작동거리·스테이지 공간과 대조하면 됩니다.</p>

    <h2 style="margin-top:26px">공통 광학계 — 덴드라이트 관찰 전용 현미경</h2>
    <p>시리즈 전 모델이 함께 쓰는 전용 광학계입니다. <b>덴드라이트 관찰 전용 대물 5종(5~100×)</b>과 <b>인시츄 배터리 클램프가 달린 2층 스테이지</b>가 일반 금속현미경과의 차이입니다.</p>
    <figure style="margin:12px 0 10px">
      <img src="/img/blog/hefei-dendrite-scope.jpg" alt="덴드라이트 관찰 전용 현미경 — 삼안 경통, 5공 터렛(5~100배 덴드라이트 관찰 대물), 인시츄 배터리 클램프 스테이지, U820 카메라" loading="lazy" style="display:block;width:100%;max-width:360px;margin:0 auto;border:1px solid var(--line);border-radius:12px;background:#fff">
    </figure>
    <div class="bx-spec" style="max-width:560px;margin:6px 0 4px">
      <span>대물렌즈</span><span><b>5 / 10 / 20 / 50 / 100×</b> 덴드라이트 관찰 전용 · 수동 5공 터렛</span>
      <span>접안 · 경통</span><span>10× 초광시야(시야수 25 mm) · 삼안 20° 틸트 · 분할 100:0 / 50:50</span>
      <span>조명</span><span>반사·투과 <b>6.6 W 풀스펙트럼 LED</b> · 편광판 내장 · NA 1.25 집광기</span>
      <span>초점</span><span>동축 조동·미동 · 미동 <b>1 µm</b> · 조동 잠금장치</span>
      <span>스테이지</span><span>2층 기계식 — 브래킷 + 유리판 + <b>인시츄 배터리 클램프</b></span>
      <span>카메라</span><span><b>U820</b> · SONY CMOS 5472×3648(약 20 Mpx) · 15 fps · Type-C</span>
    </div>
''' + '\n    '.join(figs) + '\n\n    '
h = h[:a] + scope + h[b:]

# ── 8) 변형 아코디언 → 시리즈 라인업(신규 스펙 반영) ──
a = h.find('<h2 style="margin-top:26px">변형 모델 사양</h2>')
b = h.find('</details>', a) + 10
assert a > 0
lineup = '''<h2 style="margin-top:26px">시리즈 라인업 — 어떤 모델을 고르나</h2>
    <p>같은 관찰 방식에 시료·온도 조건만 다릅니다. 각 모델은 별도 편으로 연재합니다.</p>
    <details class="msc-acc">
      <summary>시리즈 사양 비교 펼치기 — 002 비커형 · 004 고저온 · 005 극저온</summary>
      <table class="msc-tbl">
        <thead><tr><th>모델</th><th>몸체 · 전극</th><th>관찰창 · 광학</th><th>온도 · 압력</th><th>시료 · 용도</th></tr></thead>
        <tbody>
          <tr><td><b>CIS-OM-002</b><br>비커형</td><td>석영 비커 5 mL · PTFE 셸(O링 밀봉) · 순티타늄 전극</td><td>비커 측벽 개방 광학 경로 · 전극 간격 3 mm</td><td>상온</td><td>아연 대칭 전지 등 수계 입문</td></tr>
          <tr><td><b>CIS-OM-004</b><br>고저온형</td><td>PEEK · 기본 유리질 탄소(GC) 전극</td><td>석영창 Φ24 mm · 최소 작동거리 1 mm</td><td><b>−30~150℃</b> · ±1℃ 프로그램 — 냉각·가열 플랫폼 분리(교체식, 실링 무관)</td><td>시료 10×10 mm · 0.6~2 mm · 본체 두께 33 mm · 가압 모듈 옵션</td></tr>
          <tr><td><b>CIS-OM-005</b><br>극저온형</td><td>PEEK + 구리 · 냉각·가열 유닛 분리</td><td>석영창 Φ10 mm · 초점거리 &lt;2 mm</td><td><b>−100~100℃</b> · 대기압~약한 양압</td><td>본체 약 60×70×50 mm · 액체·폴리머 리튬전지, 전극+분리막 &lt;10×10 mm</td></tr>
        </tbody>
      </table>
    </details>'''
h = h[:a] + lineup + h[b:]

# ── 9) 출처: 논문 2줄 제거, 자료 기반 문구로 ──
a = h.find('<div class="sd-sources">')
b = h.find('</div>', a) + 6
assert a > 0
src_new = '''<div class="sd-sources">
    <h4>출처·안내</h4>
    제품 사진·사양·카탈로그·영상: Hefei In-situ Technology Co., Ltd. 공식 자료 (사용 허가).<br>
    ※ 본 페이지는 제조사 공식 자료와 실험셋업연구소의 셋업 경험을 정리한 것입니다. CIS-OM 시리즈 관찰 셀은 실험셋업연구소가 소싱·공급하고 구매·수리·국내 A/S는 실험 장비 수리 전문 업체 이머전트(Emergent co)가 맡습니다.
  </div>'''
h = h[:a] + src_new + h[b:]

# ── 10) 사양 리스트(팝업): OPR-DM01·논문 문구 갱신 ──
h = h.replace('"가압 전고체 모듈(003 옵션)","정압 최대 6 MPa(60 kg), 상향 커스텀 — Sci. Adv. 5 MPa 재현"',
              '"가압 전고체 모듈(003 옵션)","정압 최대 6 MPa(60 kg), 상향 커스텀"')
h = h.replace('"OPR-DM01 전용 광학계","줌 0.7~4.5×(WD 82~179mm) + 10/20/40/50× 대물, 16 Mpx"',
              '"덴드라이트 관찰 전용 현미경","대물 5~100× 5종 · 인시츄 배터리 클램프 스테이지 · U820 20Mpx"')

assert h.count('</html>') == 1 and h.rstrip().endswith('</html>')
for k in ['ACS Cent', 'Sci. Adv', 'Wood', 'Science Advances', '논문']:
    if k in h:
        # 남은 위치 보고 (팝업 문의 placeholder 등 확인용)
        i = h.find(k)
        print('잔존:', k, '→', h[max(0,i-50):i+60].replace('\n', ' ')[:110])
fo = open(p, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('저장 완료')
for m in re.findall(r'<h[23][^>]*>([^<]{1,44})', h):
    if 'msc' not in m: print(' -', m)
