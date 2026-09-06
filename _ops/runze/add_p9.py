# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]
APPS=("<ul><li>스마트 수질 모니터링 장비 · 암모니아성 질소 온라인 측정기</li><li>COD 소화 장치 · 단백질 면역블롯 장비</li>"
 "<li>의료 진단 · 생화학 분석 · 분석기기</li><li>식품·음료 · 세차 설비 · 잉크 분사 · 세정</li>"
 "<li>실험 연구 · 산업기계 · 스마트 가전</li></ul>")

# ---- BJ-RZ01B ----
s="bj-rz01b-42-stepper-peristaltic-pump"
P.append({
"slug":"bj-rz01b-42-stepper-peristaltic-pump","name":"소형 연동펌프 BJ-RZ01B","name_en":"Runze Fluid BJ-RZ01B 42 Stepper Peristaltic Pump",
"sub":"POM 4롤러 중간 맥동 · PC 하우징 · 방수·방진 · 데드스페이스 없음 · 42 스텝모터 · CE / RoHS",
"category":"연동펌프 · 스텝모터 일체형",
"title":"Runze Fluid 소형 연동펌프 BJ-RZ01B — 42 스텝모터 방수·방진 헤드 | 실험셋업연구소",
"desc":"Runze Fluid BJ-RZ01B 42 스텝모터 연동펌프 — POM 4롤러(중간 맥동), PC 하우징으로 상태 확인, 방수·방진·청소 용이·데드스페이스 없음, 방진 커버, 42 스텝모터 수명 10만 시간, CE / RoHS 인증, OEM 대응. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 소형 연동펌프 BJ-RZ01B",
"answer":"BJ-RZ01B는 POM 4롤러 헤드에 42 스텝모터를 붙인 소형 연동펌프로, PC 하우징과 방진 커버로 이물질을 막아 튜브와 펌프 수명을 늘린 CE·RoHS 인증 모델입니다.",
"features":[
 "롤러 <b>POM</b> — 내피로·저마찰이라 안정적이고, 4롤러 구성으로 맥동이 중간 수준입니다",
 "하우징 <b>PC</b> — 펌프 동작을 눈으로 확인합니다",
 "펌프헤드가 <b>방수·방진</b> 이고 <b>데드스페이스가 없어</b> 청소가 쉽습니다",
 "<b>방진 커버</b> 로 고형 이물질 유입을 막아 튜브 수명을 늘립니다",
 "<b>42 스텝모터</b> — 기대 수명 10만 시간, 녹슬지 않고 소음이 낮습니다",
 "<b>CE · RoHS</b> 인증, <b>OEM 대응</b>"],
"specs":[
 ["유량 범위 (Flow rate)","RZ01B 헤드 구성 기준 (튜브 규격에 따름)"],
 ["모델 (Model No.)","BJ-RZ01B"],
 ["롤러 (Pump roller)","POM 4롤러 (중간 맥동)"],
 ["하우징 재질 (Housing)","PC"],
 ["모터 (Motor type)","42 스텝모터 · 기대 수명 10만 시간"],
 ["보호 구조 (Protection)","방수 · 방진 · 방진 커버 · 데드스페이스 없음"],
 ["인증 (Certification)","CE · RoHS"],
 ["커스터마이즈 (Customization)","OEM 대응"]],
"buybox":[],
"related":PREL(' · <a href="/brands/runze/zl-ws-ys-rz01b-dc-motor-peristaltic-pump/">DC모터 연동펌프 ZL(WS/YS)-RZ01B</a> · <a href="/brands/runze/small-peristaltic-pump-bj-rz-01/">소형 연동펌프 BJ-RZ-01</a> · <a href="https://www.youtube.com/watch?v=y_Yu_27x00I" rel="nofollow">BJ-RZ01B 제조사 소개 영상</a>'),
"keywords":PKW+[["#소형연동펌프","/product/"],["#방진커버","/product/"],["#CE인증","/product/"]],
"sections":[
 {"h":"구조 비교 (Why POM rotor)","html":"<p>제조사는 일반 플라스틱 로터가 버(burr) 때문에 안정성과 내구성이 떨어지는 것과 비교해, <b>POM 로터</b> 가 내피로·저마찰로 안정적이라고 설명합니다. 일반 모터가 녹슬고 소음이 크며 수명이 짧은 것과 달리 <b>42 스텝모터</b> 는 기대 수명 10만 시간에 저소음입니다. 방진 커버가 없으면 고형 이물질이 들어와 펌프 수명을 깎지만, 이 모델은 동작부에 <b>먼지·오염 보호</b> 가 들어갑니다.</p>"
  +figs([(D(s,3),"POM 로터 · 42 스텝모터 · 방진 커버 구조 비교")])},
 {"h":"용도 (Applications)","html":APPS+figs([(D(s,4),"적용 분야 — 스마트 수질 모니터링 · 암모니아성 질소 온라인 측정 · COD 소화 · 단백질 면역블롯"),(D(s,5),"적용 분야 — 식품 기계 · 세차 설비")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"BJ-RZ01B (제조사 자료)") for i in [0,1,2]+list(range(6,len(META[s]["det"])))])}],
"faq":[
 {"tag":"맥동","q":"BJ-RZ01B의 맥동은 어느 정도인가요?","a":"POM 4롤러 구성이라 중간 수준입니다. 더 낮춰야 하면 6롤러 헤드를 쓰는 BJ-RZ-02나 8롤러 구성인 BJ-RZ1030B를 봅니다."},
 {"tag":"보호","q":"먼지가 많은 곳에서도 쓸 수 있나요?","a":"펌프헤드가 방수·방진이고 동작부에 방진 커버가 있어 고형 이물질 유입을 막습니다. 데드스페이스가 없어 청소도 쉽습니다."},
 {"tag":"모터","q":"모터 수명은 얼마인가요?","a":"제조사 표기 기준 42 스텝모터의 기대 수명은 10만 시간입니다."},
 {"tag":"인증","q":"인증은 무엇을 받았나요?","a":"CE와 RoHS입니다."},
 {"tag":"차이","q":"BJ-RZ01B와 ZL-RZ01B는 뭐가 다른가요?","a":"헤드는 같은 RZ01B 계열이고 모터가 다릅니다. BJ는 42 스텝모터, ZL은 24V DC 모터(브러시/브러시리스 선택)입니다."}],
"ld":{"name":"Runze Fluid 소형 연동펌프 BJ-RZ01B","sku":"BJ-RZ01B","category":"연동펌프 · 스텝모터 일체형",
 "description":"POM 4롤러 · PC 하우징 소형 연동펌프. 42 스텝모터(수명 10만 시간), 방수·방진·방진 커버, 데드스페이스 없음, CE·RoHS 인증, OEM 대응.",
 "models":["BJ-RZ01B"],"count":1},
"source":SRCU("bj-rz01b-42-stepper-peristaltic-pump")})

# ---- ZL(WS/YS)-RZ01B ----
s="zl-ws-ys-rz01b-dc-motor-peristaltic-pump"
P.append({
"slug":"zl-ws-ys-rz01b-dc-motor-peristaltic-pump","name":"DC모터 연동펌프 ZL(WS/YS)-RZ01B","name_en":"Runze Fluid ZL(WS/YS)-RZ01B DC Motor Peristaltic Pump",
"sub":"RZ01B 헤드 · PPS 롤러 4개 · 24V DC 브러시 / 브러시리스 선택 · ≤420 rpm · 최대 152 mL/min",
"category":"연동펌프 · DC모터 일체형",
"title":"Runze Fluid DC모터 연동펌프 ZL(WS/YS)-RZ01B — 브러시·브러시리스 선택 | 실험셋업연구소",
"desc":"Runze Fluid ZL(WS/YS)-RZ01B DC모터 연동펌프 — RZ01B 헤드(PPS 롤러 4개 · PPS 하우징 · PC 투명 커버), 24V DC 브러시(YS) 또는 브러시리스(WS) 선택, 420 rpm 이하, 토출압 0.2 MPa, 최대 152 mL/min, 0.66 kg. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid DC모터 연동펌프 ZL(WS/YS)-RZ01B",
"answer":"ZL(WS/YS)-RZ01B는 RZ01B 헤드에 24V DC 모터를 붙인 소형 연동펌프로, 저가·단순 구조가 필요하면 브러시(YS), 긴 수명과 낮은 유지비가 필요하면 브러시리스(WS)를 고릅니다.",
"features":[
 "롤러 <b>PPS 4개</b> — 맥동이 중간 수준이고 구조 성능이 좋습니다",
 "하우징 <b>PPS</b> + <b>PC 투명 펌프헤드 커버</b> — 동작을 눈으로 확인하고, 회전 방지 잠금으로 장시간 안정 운전합니다",
 "펌프헤드가 <b>방수·방진</b> 이고 데드스페이스가 없어 청소가 쉽습니다",
 "<b>24V DC 모터</b> — 작고 소비전력이 낮고 저렴합니다. <b>브러시리스(WS)</b> 는 더 안정적이고, <b>브러시(YS)</b> 는 가격이 유리합니다",
 "회전수 <b>≤420 rpm</b>, 토출압 <b>0.2 MPa</b>, 유량 <b>최대 152 mL/min</b>",
 "브러시리스는 <b>PWM 외부 제어</b> 배선을 지원합니다 — 청색 PWM · 녹색 비상정지 · 백색 정·역 · 적색 모터+ · 흑색 모터−",
 "중량 0.66 kg, 사용 환경 0-40℃ · 상대습도 98% 미만"],
"specs":[
 ["유량 범위 (Flow rate)","최대 152 mL/min"],
 ["모델 (Product name)","ZL-RZ01B · ZL(YS)-RZ01B (브러시) · ZL(WS)-RZ01B (브러시리스)"],
 ["적용 펌프헤드 (Pump head)","RZ01B"],
 ["롤러 (Pump roller)","PPS 4롤러"],
 ["하우징 재질 (Housing)","PPS · PC 투명 커버"],
 ["모터 (Motor type)","24V DC 모터 (브러시 / 브러시리스 선택)"],
 ["회전수 (Speed range)","≤420 rpm"],
 ["토출압 (Discharge pressure)","0.2 MPa"],
 ["정격 전압 (Rated voltage)","24V"],
 ["전류 (Current)","브러시 0.8 A 무부하 / 3 A 정격 · 브러시리스 0.6 A 무부하 / 2.3 A 정격"],
 ["출력 토크 (Torque)","브러시 9.0 kgf·cm · 브러시리스 9.5 kgf·cm"],
 ["회전 방향 (Steering)","CW / CCW"],
 ["사용 환경 (Environment)","0 ~ 40℃ · 상대습도 98% 미만"],
 ["중량 (Weight)","0.66 kg"]],
"variants":{"heading":"모터 사양 비교 (Motor)","head":["항목","ZL(YS)-RZ01B 브러시","ZL(WS)-RZ01B 브러시리스"],
 "rows":[["회전수 범위","≤420 rpm","≤420 rpm"],["정격 전압","24V","24V"],
  ["전류 (무부하 / 정격)","0.8 A / 3 A","0.6 A / 2.3 A"],
  ["토출압","0.2 MPa","0.2 MPa"],["출력 · 회전 방향","CCW / CW","CCW / CW"],
  ["토크","9.0 kgf·cm","9.5 kgf·cm"],
  ["배선","모터 꼬리의 금속편 2개 (+ · −). + 를 전원 +, − 를 전원 − 에 연결하면 정회전(시계 방향), 반대로 연결하면 역회전","모터 꼬리의 전선 4개. 적색을 전원 +, 흑색·백색·청색을 전원 − 에 연결하면 정회전, 적색을 전원 −, 흑색·청색을 전원 − 에 연결하면 역회전"],
  ["외부 PWM 제어","−","청색 PWM · 녹색 비상정지 · 백색 정·역 · 적색 모터+ · 흑색 모터−"]],
 "note":"제조사 자체 시험실 데이터이며 개체 차이가 있을 수 있습니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/bj-rz01b-42-stepper-peristaltic-pump/">소형 연동펌프 BJ-RZ01B</a> · <a href="/brands/runze/zlys-fg-16-peristaltic-pump/">DC모터 연동펌프 ZL(YS)-FG-16</a>'),
"keywords":PKW+[["#DC모터펌프","/product/"],["#브러시리스","/product/"],["#PWM제어","/product/"]],
"sections":[
 {"h":"브러시 · 브러시리스 선택","html":"<p><b>브러시 DC 모터</b> 는 구조가 단순하고 가격이 낮아, 성능 요구가 크지 않은 곳에 맞습니다. <b>브러시리스 DC 모터</b> 는 오래 안정적으로 돌고 유지보수 비용이 낮습니다.</p>"
  +figs([(D(s,4),"브러시 · 브러시리스 DC 모터 선택 기준"),(D(s,5),"ZL(YS) · ZL(WS) 모터 사양과 배선 방법 비교")])},
 {"h":"참고 유량 (Flow rate)","html":figs([(D(s,2),"펌프헤드·로터 수별 참고 유량표와 두께 1.6 mm 튜브 유량 곡선")])},
 {"h":"제품 파라미터 (Parameters)","html":figs([(D(s,3),"ZL-RZ01B 제품 파라미터")])},
 {"h":"구조 (Structure)","html":"<p>방진 커버 설계로 먼지와 이물질을 막아 튜브 수명을 늘립니다.</p>"+figs([(D(s,9),"방진 커버 구조")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"ZL(WS/YS)-RZ01B (제조사 자료)") for i in [0,1,6,7,8]+list(range(10,len(META[s]["det"])))])}],
"faq":[
 {"tag":"선택","q":"브러시와 브러시리스 중 어느 쪽을 골라야 하나요?","a":"단순하고 저렴한 구성이면 브러시(YS), 오래 안정적으로 돌리고 유지보수를 줄이려면 브러시리스(WS)입니다. 브러시리스가 전류가 적고 토크는 조금 더 높습니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"최대 152 mL/min입니다. 회전수는 420 rpm 이하이고 토출압은 0.2 MPa입니다."},
 {"tag":"배선","q":"회전 방향은 어떻게 바꾸나요?","a":"브러시 모델은 전원 극성을 바꿔 끼우면 됩니다. 브러시리스 모델은 적색·흑색·백색·청색 네 선의 연결 조합으로 정·역을 정하고, PWM 제어가 필요하면 청색을 PWM, 녹색을 비상정지, 백색을 정·역에 씁니다."},
 {"tag":"보호","q":"먼지가 들어가지 않나요?","a":"방진 커버 설계로 먼지와 이물질을 막습니다. 펌프헤드는 방수·방진이고 데드스페이스가 없어 청소가 쉽습니다."},
 {"tag":"재질","q":"습부와 하우징 재질은?","a":"액체는 튜브 안쪽에만 닿습니다. 하우징은 PPS, 펌프헤드 커버는 PC 투명, 롤러는 PPS입니다."},
 {"tag":"중량","q":"무게는 얼마인가요?","a":"0.66 kg입니다. 사용 환경은 0~40℃, 상대습도 98% 미만입니다."}],
"ld":{"name":"Runze Fluid DC모터 연동펌프 ZL(WS/YS)-RZ01B","sku":"ZL-RZ01B","category":"연동펌프 · DC모터 일체형",
 "description":"RZ01B 헤드 DC모터 연동펌프. PPS 4롤러, 24V DC 브러시/브러시리스 선택, ≤420 rpm, 토출압 0.2 MPa, 최대 152 mL/min, PWM 외부 제어, 0.66 kg.",
 "models":["ZL(YS)-RZ01B","ZL(WS)-RZ01B"],"count":2},
"source":SRCU("zl-ws-ys-rz01b-dc-motor-peristaltic-pump")})

# ---- ZL(YS)-FG-16 ----
s="zlys-fg-16-peristaltic-pump"
P.append({
"slug":"zlys-fg-16-peristaltic-pump","name":"DC모터 대유량 연동펌프 ZL(YS)-FG-16","name_en":"Runze Fluid ZL(YS)-FG-16 DC Motor Peristaltic Pump",
"sub":"FG-16 헤드 · PPS 하우징 · 304 스테인리스 3 / 6롤러 · 24V DC 브러시 / 브러시리스 · 최대 1539 mL/min",
"category":"연동펌프 · DC모터 일체형",
"title":"Runze Fluid DC모터 대유량 연동펌프 ZL(YS)-FG-16 — 최대 1539 mL/min | 실험셋업연구소",
"desc":"Runze Fluid ZL(YS)-FG-16 DC모터 연동펌프 — 표준 FG-16 헤드, PPS 하우징에 304 스테인리스 3·6롤러, 플립 커버로 튜브 교체, 24V DC 브러시(1510 mL/min) 또는 브러시리스(1539 mL/min), 421 rpm 이하. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid DC모터 대유량 연동펌프 ZL(YS)-FG-16",
"answer":"ZL(YS)-FG-16은 표준 FG-16 헤드에 24V DC 모터를 붙인 대유량 연동펌프로, 304 스테인리스 롤러로 고온을 견디고 플립 커버로 튜브를 빠르게 갈면서 최대 1539 mL/min을 이송합니다.",
"features":[
 "표준 <b>FG-16 펌프헤드</b> — PPS 하우징에 <b>304 스테인리스 3롤러 / 6롤러</b>, 고온을 견딥니다",
 "<b>플립 커버(Flip cover)</b> 설계 — 튜브 교체가 빠릅니다",
 "<b>24V DC 브러시 / 브러시리스</b> 선택 — 작고 소비전력이 낮고 저렴합니다",
 "최대 유량 <b>1510 mL/min(브러시) · 1539 mL/min(브러시리스)</b>",
 "회전수 <b>≤421 rpm</b>, 전류 브러시 0.35 A 무부하 / 1.8 A 정격, 브러시리스 0.6 A 무부하 / 2.3 A 정격",
 "조작이 간단하고 소음이 낮습니다",
 "스테인리스 로터는 내피로·저마찰이라 플라스틱 로터보다 안정적이라고 제조사가 안내합니다"],
"specs":[
 ["유량 범위 (Flow rate)","최대 1510 mL/min (브러시) · 1539 mL/min (브러시리스)"],
 ["모델 (Model No.)","ZL(YS)-FG-16 (브러시) · ZL-FG-16 (브러시리스)"],
 ["적용 펌프헤드 (Pump head)","FG-16 (표준)"],
 ["롤러 (Pump roller)","304 스테인리스 3롤러 / 6롤러"],
 ["하우징 재질 (Housing)","PPS"],
 ["모터 (Motor type)","24V DC 모터 (브러시 / 브러시리스 선택)"],
 ["회전수 (Speed range)","≤421 rpm"],
 ["정격 전압 (Rated voltage)","24V"],
 ["전류 (Current)","브러시 0.35 A 무부하 / 1.8 A 정격 · 브러시리스 0.6 A 무부하 / 2.3 A 정격"],
 ["튜브 교체 (Tube change)","플립 커버 (Flip cover)"]],
"variants":{"heading":"모터 사양 비교 (Motor)","head":["항목","ZL(YS)-FG-16 브러시","ZL-FG-16 브러시리스"],
 "rows":[["회전수 범위","≤421 rpm","≤421 rpm"],["정격 전압","24V","24V"],
  ["전류 (무부하 / 정격)","0.35 A / 1.8 A","0.6 A / 2.3 A"],
  ["유량 범위","1510 mL/min","1539 mL/min"],
  ["로터 수","3롤러 / 6롤러","3롤러 / 6롤러"]],
 "note":"제조사 자체 시험실 데이터이며 개체 차이가 있을 수 있습니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/zl-ws-ys-rz01b-dc-motor-peristaltic-pump/">DC모터 연동펌프 ZL(WS/YS)-RZ01B</a> · <a href="/brands/runze/industrial-peristaltic-pump/">산업용 연동펌프 BJ30</a> · <a href="/brands/runze/sr400-peristaltic-pump/">탁상형 연동펌프 SR400</a>'),
"keywords":PKW+[["#대유량연동펌프","/product/"],["#DC모터펌프","/product/"],["#스테인리스로터","/product/"]],
"sections":[
 {"h":"구조 비교 (Stainless rotor)","html":"<p>제조사는 <b>스테인리스 로터</b> 가 내피로·저마찰로 안정적인 데 비해 플라스틱 로터는 쉽게 변형된다고 설명합니다. 또한 고품질 모터는 수명이 길고 안정적이며 소음이 낮은 반면 일반 모터는 녹슬고 소음이 크며 수명이 짧다고 안내합니다.</p>"
  +figs([(D(s,3),"스테인리스 로터 · 고품질 모터 구조 비교")])},
 {"h":"모터 사양 (Motor specification)","html":figs([(D(s,8),"ZL(YS)-FG-16 브러시 · ZL-FG-16 브러시리스 모터 사양 비교")])},
 {"h":"용도 (Applications)","html":APPS+figs([(D(s,5),"적용 분야 — 스마트 수질 모니터링 · 암모니아성 질소 온라인 측정 · COD 소화 · 단백질 면역블롯"),(D(s,6),"적용 분야 — 식품·음료 · 의료 진단 · 분석기기 · 잉크 · 세정 · 환경 · 산업기계")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"ZL(YS)-FG-16 (제조사 자료)") for i in [0,1,2,4,7]+list(range(9,len(META[s]["det"])))])}],
"faq":[
 {"tag":"유량","q":"ZL(YS)-FG-16은 유량이 얼마나 나오나요?","a":"브러시 모델 최대 1510 mL/min, 브러시리스 모델 최대 1539 mL/min입니다. 회전수는 421 rpm 이하입니다."},
 {"tag":"롤러","q":"3롤러와 6롤러 차이는?","a":"3롤러가 유량이 크고 6롤러가 맥동이 작습니다. 둘 다 304 스테인리스입니다."},
 {"tag":"튜브","q":"튜브 교체가 쉬운가요?","a":"플립 커버 설계라 커버를 젖혀 바로 갈아 끼웁니다."},
 {"tag":"재질","q":"고온에도 쓸 수 있나요?","a":"PPS 하우징에 304 스테인리스 롤러라 고온을 견딥니다. 실제 온도 한계는 쓰는 튜브 재질이 결정합니다."},
 {"tag":"모터","q":"브러시와 브러시리스는 뭐가 다른가요?","a":"브러시는 전류가 낮고(0.35 A 무부하 / 1.8 A 정격) 가격이 유리하며, 브러시리스는 유량이 조금 더 나오고 수명과 안정성이 좋습니다."},
 {"tag":"비교","q":"BJ30이나 SR400과 비교하면 어떤가요?","a":"BJ30과 SR400은 스텝모터라 속도를 정밀하게 맞추고 유량 재현성이 좋습니다. ZL(YS)-FG-16은 DC 모터라 구조가 단순하고 저렴해 대유량 이송 자체가 목적일 때 유리합니다."}],
"ld":{"name":"Runze Fluid DC모터 대유량 연동펌프 ZL(YS)-FG-16","sku":"ZL(YS)-FG-16","category":"연동펌프 · DC모터 일체형",
 "description":"FG-16 표준 헤드 대유량 DC모터 연동펌프. PPS 하우징, 304 스테인리스 3·6롤러, 플립 커버, 24V DC 브러시/브러시리스, ≤421 rpm, 최대 1539 mL/min.",
 "models":["ZL(YS)-FG-16","ZL-FG-16"],"count":2},
"source":SRCU("zlys-fg-16-peristaltic-pump")})
add(P)
