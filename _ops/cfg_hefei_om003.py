# -*- coding: utf-8 -*-
# 허페이 인시츄(Hefei In-situ Technology) CIS-OM-003 광학관찰 셀 — 1장
# 출처: chinain-situ.com/en/raman_view_500.html + CISOM003_Technical_Proposal_EN.pdf + 제조사 회신
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B

# bilibili 외부 임베드 — bvid만으로는 재생되지 않는다. aid·cid까지 넣어야 한다.
# (2026-09-01 브라우저에서 실제 재생 확인: 03:37 재생됨)
VIDEO = (
 '<h2 class="pkg-h">설치 영상</h2>\n'
 '<div class="det-imgs"><figure>'
 '<div style="position:relative;width:100%;max-width:760px;margin:0 auto;aspect-ratio:16/9;'
 'border:1px solid #ECECEC;border-radius:10px;overflow:hidden;background:#000">'
 '<iframe src="https://player.bilibili.com/player.html?isOutside=true'
 '&amp;aid=112908298095343&amp;bvid=BV1vnYFeNESP&amp;cid=500001639003496'
 '&amp;p=1&amp;autoplay=0&amp;danmaku=0&amp;high_quality=1" '
 'style="position:absolute;inset:0;width:100%;height:100%;border:0" '
 'scrolling="no" frameborder="no" framespacing="0" allowfullscreen="true" '
 'allow="autoplay; fullscreen; encrypted-media" '
 'title="합비원위과기 원위현미관찰지003 설치"></iframe></div>'
 '<figcaption>제조사 설치 영상 3분 37초 — 부품 확인부터 셀 조립까지 (Hefei In-situ Technology Co., Ltd.). '
 '왼쪽 아래 재생 버튼을 누르면 이 자리에서 바로 재생됩니다.</figcaption>'
 '</figure></div>\n')

FIGS = (
 '<h2 class="pkg-h">구조</h2>\n'
 '<div class="det-imgs">'
 '<figure><p class="det-h">셀 상부 — 나사 구멍 · 셀 커버 · 실링 가스켓 · 석영창</p>'
 '<img src="/img/hefei/hefei-om003-fig1.jpg" alt="CIS-OM-003 셀 커버 분해 구조 — 석영창과 실링 가스켓" loading="lazy">'
 '<figcaption>커버를 열면 실링 가스켓과 초박형 석영창이 차례로 나옵니다. 창 두께는 0.05 mm입니다.</figcaption></figure>'
 '<figure><p class="det-h">셀 본체 — 전극 · O링 · 전극 실링 슬리브</p>'
 '<img src="/img/hefei/hefei-om003-fig2.jpg" alt="CIS-OM-003 셀 본체 구조 — 티타늄 전극과 O링, 전극 실링 슬리브" loading="lazy">'
 '<figcaption>가동식 티타늄 전극 한 쌍이 실링 슬리브를 통해 셀 본체에 들어갑니다. 양극·음극을 나눠 관찰합니다.</figcaption></figure>'
 '</div>\n')

SPEC004 = (
 '<h2 class="pkg-h">형제 모델 — CIS-OM-004 (온도 제어형)</h2>\n'
 '<p class="pkg-note" style="margin:0 0 12px">003과 같은 관찰 구조에 '
 '<b>−30 ~ +150 °C 온도 스테이지</b>를 얹은 모델입니다. 저온 리튬 도금·고온 열화처럼 '
 '온도를 변수로 두는 실험에 씁니다. 전극이 <b>유리탄소(GC)</b>로 바뀌고 셀이 두꺼워집니다.</p>\n'
 + B.spec_tbl([
   ('셀 본체 재질','<b>PEEK</b>'),
   ('전극','<b>표준 유리탄소(GC) 전극</b> · 주문 시 변경'),
   ('관찰창','용융 석영 (fused silica) · <b>Ø24 mm</b>'),
   ('최소 작동거리','<b>1 mm 이상</b>'),
   ('시료 챔버','10 × 10 mm · 두께 <b>0.6 ~ 2 mm</b>'),
   ('셀 전체 두께','<b>35 mm 이하</b>'),
   ('온도 범위','<b>−30 °C ~ +150 °C</b>'),
   ('온도 정확도','<b>±1 °C</b>'),
   ('온도 제어','<b>프로그래머블 PID 컨트롤러</b>'),
   ('열 설계','<b>모듈형 냉각·가열 스테이지</b> — 셀 밀봉을 풀지 않고 교체 / 저온용·고온용 베이스 플레이트 별도'),
   ('대응 계','<b>모든 이차전지 계</b>'),
   ('공통 기능','덴드라이트 성장 관찰 · 불활성 가스 퍼지 · 인시츄 전해액 주입 · 헬륨 리크 시험 밀봉'),
   ('옵션','고체전해질 가압 모듈 — <b>최대 60 kgf (약 6 MPa)</b>, 그 이상 주문 제작'),
   ('가격','<b>문의</b>'),
 ])
)


def _rows(pairs):
    return B.spec_tbl([('<span style="font-weight:600;color:#3a3330">%s</span>' % en, ko)
                       for en, ko in pairs])

_S003 = [
 ('Material: PEEK',
  '셀 본체 재질 — PEEK'),
 ('Electrodes: High-purity titanium (custom materials optional)',
  '전극 — 고순도 티타늄. 주문 시 다른 재질로 제작'),
 ('Window Material: Fused silica',
  '창 재질 — 용융 석영'),
 ('Dendrite growth observation capability',
  '덴드라이트 성장 관찰'),
 ('Gas-purge function &amp; in-situ liquid injection',
  '가스 퍼지 기능 · 인시츄 액체(전해액) 주입'),
 ('Sample Chamber: 10 × 10 mm rectangular area',
  '시료 챔버 — 10 × 10 mm 사각 영역'),
 ('Thickness Range: 0.6–2 mm',
  '시료 두께 범위 — 0.6 ~ 2 mm'),
 ('Applications: All rechargeable battery systems',
  '적용 — 모든 이차전지 계'),
 ('Helium-leak tested sealing',
  '헬륨 리크 시험으로 밀봉 확인'),
 ('Optical Window: Ø24 mm',
  '광학창 — Ø24 mm'),
 ('Minimum Working Distance: 1 mm',
  '최소 작동거리 — 1 mm'),
 ('Horizontal / side-mountable orientation (minimizes bubble formation)',
  '수평 · 측면 거치 — 기포 발생 영향을 줄입니다'),
 ('Compatible with Li-air battery testing',
  '리튬-공기 전지 시험 가능'),
 ('Optional Solid-State Module (CIS-0M-003): Pressurization up to 60 kg (6 MPa)',
  '고체전해질 모듈(옵션) — 최대 60 kg(약 6 MPa) 가압'),
 ('Higher pressure customization available',
  '더 높은 압력은 주문 제작'),
]

_S004 = [
 ('Material: PEEK',
  '셀 본체 재질 — PEEK'),
 ('Electrodes: Standard glassy carbon (GC) electrode (customizable)',
  '전극 — 표준 유리탄소(GC) 전극. 주문 시 변경'),
 ('Window Material: Fused silica (quartz)',
  '창 재질 — 용융 석영'),
 ('Dendrite growth observation capability',
  '덴드라이트 성장 관찰'),
 ('Inert gas purging &amp; in-situ electrolyte injection',
  '불활성 가스 퍼지 · 인시츄 전해액 주입'),
 ('Helium-leak tested sealing',
  '헬륨 리크 시험으로 밀봉 확인'),
 ('Optical Window: Ø24 mm',
  '광학창 — Ø24 mm'),
 ('Working Distance: ≥ 1 mm',
  '작동거리 — 1 mm 이상'),
 ('Sample Chamber: 10 × 10 mm rectangular area',
  '시료 챔버 — 10 × 10 mm 사각 영역'),
 ('Thickness Range: 0.6–2 mm',
  '시료 두께 범위 — 0.6 ~ 2 mm'),
 ('Overall Thickness: ≤ 35 mm',
  '셀 전체 두께 — 35 mm 이하'),
 ('Range: −30 °C to +150 °C',
  '온도 범위 — −30 °C ~ +150 °C'),
 ('Accuracy: ±1 °C',
  '온도 정확도 — ±1 °C'),
 ('Compatibility: All rechargeable battery systems',
  '적용 — 모든 이차전지 계'),
 ('Control System: Programmable PID controller',
  '제어 — 프로그래머블 PID 컨트롤러'),
 ('Modular cooling / heating stages (swappable without breaking cell seal)',
  '모듈형 냉각 · 가열 스테이지 — 셀 밀봉을 풀지 않고 교체'),
 ('Independent base plates for subzero / HT operation',
  '영하용 · 고온용 베이스 플레이트 별도'),
 ('Optional Solid-State Accessory — Pressurization Module: Max. pressure 60 kgf (6 MPa)',
  '고체전해질 부속(옵션) 가압 모듈 — 최대 60 kgf(약 6 MPa)'),
 ('Higher pressures customizable',
  '더 높은 압력은 주문 제작'),
]

SHEET = (
 '<h2 class="pkg-h">제조사 사양 시트 (원문)</h2>\n'
 '<p class="pkg-note" style="margin:0 0 14px">제조사가 게시한 영문 사양을 그대로 옮기고 우리말을 붙였습니다. '
 '<b>In situ microscopic observation cell series — Product parameter</b></p>\n'
 '<h3 class="det-h" style="text-align:left;font-size:15px;margin:18px 0 8px">CIS-0M-003 · CIS-0M-003-1</h3>\n'
 + _rows(_S003)
 + '<h3 class="det-h" style="text-align:left;font-size:15px;margin:22px 0 8px">CIS-0M-004 (온도 제어형)</h3>\n'
 + _rows(_S004)
 + '<div class="det-imgs" style="margin-top:20px"><figure>'
   '<img src="/img/hefei/hefei-spec-sheet.jpg" '
   'alt="허페이 인시츄 관찰 셀 제조사 사양 시트 — CIS-0M-003 · CIS-0M-003-1 · CIS-0M-004" loading="lazy">'
   '<figcaption>제조사 사양 시트 원본 — 위 CIS-0M-003 · CIS-0M-003-1, 아래 CIS-0M-004</figcaption>'
   '</figure></div>\n')

B.build(dict(
 brand='hefei', slug='om003-microscope-cell', cat='인시츄 관찰 셀',
 landed=True,          # price가 이미 판매가(해외배송비 별도)
 h1='인시츄 리튬 덴드라이트 광학관찰 셀 CIS-OM-003',
 sub='In-situ Lithium Dendrite Observation Cell · Microscope Visual Battery Test Cell',
 title='허페이 인시츄 CIS-OM-003 리튬 덴드라이트 광학관찰 셀 — 석영창 0.05 mm · 현미경 인시츄 | 실험셋업연구소',
 desc='허페이 인시츄(Hefei In-situ) CIS-OM-003 인시츄 리튬 덴드라이트 광학관찰 셀 — PEEK 본체, 고순도 티타늄 전극 한 쌍, 용융 석영창 두께 0.05 mm, 광학창 Ø24 mm, 시료 10×10 mm, 시료~창 거리 0.6 mm, 최소 작동거리 1 mm, 헬륨 리크 밀봉. 충·방전 중 덴드라이트 성장·용해를 현미경으로 실시간 관찰합니다.',
 ldname='In-situ Lithium Dendrite Observation Cell CIS-OM-003 (인시츄 리튬 덴드라이트 광학관찰 셀)',
 answer='광학현미경 아래에 그대로 올려 두고 충·방전을 걸어, 리튬·나트륨·아연 금속 음극에서 덴드라이트가 자라고 녹는 과정을 실시간으로 보는 밀폐 셀입니다.',
 summary='<b>PEEK 본체 · 용융 석영창 0.05 mm · 시료 10 × 10 mm · 시료~창 0.6 mm · 최소 작동거리 1 mm · 헬륨 리크 밀봉</b> · 5,000,000원 (VAT 별도)',
 quote='허페이 인시츄 CIS-OM-003 광학관찰 셀',
 imgs=['hefei-cis-om-003.jpg','hefei-cis-om-003-1.jpg','hefei-cis-om-004.jpg'],
 models=['CIS-OM-003','CIS-OM-003-1'],
 feat=[
  '<b>창이 0.05 mm</b>입니다 — 시료 표면에서 창 바깥면까지 약 <b>0.6 mm</b>라 고배율 대물렌즈의 작동거리(WD 1 mm) 안에 들어옵니다. 더 얇게도 주문 제작됩니다',
  '<b>가동식 티타늄 전극 한 쌍</b>이라 양극·음극을 나눠 볼 수 있습니다. 전극 재질은 주문 시 변경 가능합니다',
  '<b>수평·측면 어느 쪽으로도 거치</b>됩니다 — 측면으로 세우면 발생 기포가 관찰면을 가리는 일이 줄어듭니다',
  '<b>가스 퍼지와 인시츄 전해액 주입</b>이 설계에 들어가 있어 리튬-공기계도 다룹니다',
  '<b>헬륨 리크 시험</b>으로 밀봉을 확인해 출하합니다',
  '고체전해질 모듈(옵션)을 붙이면 <b>최대 60 kg(약 6 MPa)</b>까지 가압합니다. 더 높은 압력은 주문 제작입니다',
  '온도를 걸어야 하면 <b>CIS-OM-004</b>(−30 ~ +150 °C, ±1 °C PID)가 따로 있습니다 — 문의 주십시오',
 ],
 spec=[
  ('셀 본체 재질','<b>PEEK</b>'),
  ('전극','<b>고순도 티타늄</b> 한 쌍 (가동식) · 주문 시 재질 변경'),
  ('관찰창','<b>용융 석영 (fused silica)</b>'),
  ('창 두께','<b>0.05 mm</b> · 더 얇게 주문 제작 가능'),
  ('광학창 직경','<b>Ø24 mm</b>'),
  ('시료 챔버','<b>10 × 10 mm</b> (정사각 ≤ 10 × 10 mm)'),
  ('시료 두께','<b>0.6 ~ 2 mm</b>'),
  ('시료 ~ 창 상면','<b>약 0.6 mm</b>'),
  ('최소 작동거리','<b>1 mm</b>'),
  ('셀 외형','<b>약 60 × 70 × 30 mm</b>'),
  ('설계 온도 · 압력','상온 · 대기압'),
  ('밀봉','<b>헬륨 리크 시험</b> 통과'),
  ('거치','수평 · 측면 모두 가능'),
  ('부가 기능','<b>가스 퍼지</b> · 인시츄 전해액 주입'),
  ('대응 계','리튬 · 나트륨 · 아연 등 금속 음극 · <b>리튬-공기</b> 가능'),
  ('옵션','고체전해질 모듈 — <b>최대 60 kg (약 6 MPa)</b> 가압, 그 이상 주문 제작'),
  ('모델','CIS-OM-003 · CIS-OM-003-1'),
 ],
 price=[('CIS-OM-003','석영창 Ø24 mm · 시료 10 × 10 mm · 창 0.05 mm',5000000)],
 extra=FIGS+VIDEO+SPEC004+SHEET,
 warn='<b>창이 0.05 mm입니다.</b> 조립·세척 때 핀셋이나 손톱이 닿으면 바로 깨집니다. 커버를 조일 때는 대각선 순서로 조금씩, 가스켓이 고르게 눌리는 정도까지만 조이십시오.',
 cross='허페이 인시츄는 라만·XRD 등 다른 인시츄 셀도 만듭니다. 필요한 분석 장비와 시료 조건을 알려주시면 맞는 셀을 안내드립니다.',
 faq=[
  ('제 현미경 대물렌즈로 초점이 잡힐까요?','창 바깥면에서 시료까지가 약 0.6 mm입니다. 작동거리 1 mm 이상인 대물렌즈면 들어갑니다. 100배급 고배율은 작동거리가 0.3 mm 안팎인 경우가 많으니, 쓰시는 렌즈의 WD를 먼저 확인해 주십시오. 더 얇은 창으로 주문 제작도 됩니다.'),
  ('리튬 말고 나트륨·아연도 되나요?','됩니다. 금속 음극의 덴드라이트 성장·용해 관찰이 목적이라 리튬·나트륨·아연 모두 같은 방식으로 씁니다.'),
  ('글로브박스 안에서 조립해서 밖으로 꺼내도 되나요?','그 용도로 만든 셀입니다. 헬륨 리크 시험으로 밀봉을 확인해 출하합니다. 다만 창이 얇으므로 이송 중 충격을 주지 마십시오.'),
  ('고체전해질도 볼 수 있나요?','옵션 모듈을 붙이면 최대 60 kg(약 6 MPa)까지 가압한 상태로 관찰합니다. 그보다 높은 압력이 필요하면 주문 제작합니다.'),
  ('납기는 얼마나 걸리나요?','주문 확정 후 안내드립니다. 해외 발주 제품이라 재고 상황에 따라 달라집니다.'),
 ]))
print('허페이 CIS-OM-003 1장 생성')
