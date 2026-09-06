# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
BAUD="RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"
P=[]

# ---------------- SY-09 ----------------
s="peristaltic-pump-sy-09"; g=gal(s)
P.append({
"slug":"syringe-pump-sy-09","name":"시린지 펌프 SY-09","name_en":"Runze Fluid Syringe Pump SY-09",
"sub":"3 / 8 mL · 엔코더 내장 · 정격 스트로크 18 / 19.2 mm · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
"title":"Runze Fluid 시린지 펌프 SY-09 — 3·8 mL 엔코더 내장 수직형 시린지 펌프 | 실험셋업연구소",
"desc":"Runze Fluid 시린지 펌프 SY-09 — 3 / 8 mL, 정격 스트로크 18 mm(3600 스텝) · 19.2 mm(3840 스텝), 분해능 0.833 / 2.083 µL, 엔코더 내장 탈조 보정, 습부 붕규산 유리·PCTFE·PTFE, RS232/RS485/CAN. 가격 문의.",
"images":g,"image_alt":"Runze Fluid 시린지 펌프 SY-09",
"answer":"시린지 펌프 SY-09는 엔코더를 내장한 3·8 mL 수직형 정밀 시린지 펌프로, 상위 컴퓨터 명령을 사다리꼴 나사로 직선 운동으로 바꿔 피스톤을 움직이는 분석장비용 정량 펌프입니다.",
"features":[
 "용량 <b>3 mL · 8 mL</b> — 정격 스트로크 18 mm(3600 스텝) / 19.2 mm(3840 스텝)입니다",
 "<b>엔코더 내장</b> — 탈조를 자동 보정하고 모터 상태를 통신으로 조회할 수 있습니다",
 "유량 정확도 <b>≤1%</b>, 반복 정밀도 <b>0.3~0.7%</b>, 수명 <b>무누출 300만 회</b>(매질 물)",
 "분해능 <b>0.005 mm</b> — 3 mL은 0.833 µL, 8 mL은 2.083 µL 입니다",
 "습부는 <b>붕규산 유리 · PCTFE 밸브헤드 · PTFE 피스톤</b>, 하우징은 일체 사출 PPS 로 내식·방청입니다",
 "<b>Tecan 프로토콜과 커스텀 프로토콜</b> 을 함께 지원하며 RS232/RS485 로 여러 대를 캐스케이드할 수 있습니다",
 "세분화(마이크로스텝) <b>2~32 단계</b>, 회전 방향 CW/CCW, 강제 정지·리셋·펌웨어 버전 조회를 명령으로 지원합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PCTFE 밸브헤드 · PTFE 피스톤"],
 ["유량 정확도 (Accuracy)","≤1% @100% 정격 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% @100% 정격 스트로크"],
 ["수명 (Service life)","무누출 300만 회 (매질 물)"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 1 mm"],
 ["최대 압력 (Max pressure)","정압 0-0.8 MPa · 부압 0-0.06 MPa (유지 시간은 시험 기준)"],
 ["채널 (Channel)","단일 채널 (Single channel)"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)",BAUD],
 ["세분화 (Subdivision)","2 ~ 32 단계 설정"],
 ["주소 설정 (Address setting)","통신으로 설정 (Via communication)"],
 ["전원 (Power supply)","DC24V / 3A · 최대 15 W"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 이하 · 비결로"]],
"variants":{"heading":"용량별 규격 (Volume)","head":["항목","3 mL","8 mL"],
 "rows":[["정격 스트로크 (Rated stroke)","18 mm · 3600 스텝","19.2 mm · 3840 스텝"],
  ["최대 회전수 (Max speed)","600 rpm","300 rpm"],
  ["선속도 (Linear speed)","0.017-10 mm/s","0.017-5 mm/s"],
  ["주행 시간 (Running time)","1.8-1080 s","3.84-1129 s"],
  ["분해능 (Resolution)","0.005 mm / 0.833 µL","0.005 mm / 2.083 µL"],
  ["시린지 내경 (Syringe ID)","14.55 mm","23.03 mm"],
  ["치수 L×W×H (Dimension)","51×41.5×155.2 mm","51×41.5×157.2 mm"],
  ["순중량 (Net weight)","0.56 kg","0.62 kg"]],
 "note":"제조사 신형 브로슈어는 치수를 51×49.7×170.4 mm / 51×49.1×172 mm, 순중량을 0.45 / 0.49 kg 으로 표기하고 배압 1.5 MPa(3 mL) · 0.89 MPa(8 mL) 를 추가로 명시합니다. 습부에는 PVDF 나사 포트와 FFKM 실링을 포함합니다."},
"buybox":[],
"related":REL(' · <a href="/brands/runze/syringe-pump-sy-09s/">시린지 펌프 SY-09S</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="https://www.runzefluid.com/uploads/file/sy-09-syring-pump-v1-8-manual.pdf" rel="nofollow">SY-09 매뉴얼 V1.8 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/sy-09-syringe-pump.pdf" rel="nofollow">SY-09 카탈로그 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=ch9Kx0YK3rI" rel="nofollow">SY-09 제조사 소개 영상</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#엔코더내장","/product/"],["#정량주입","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-LS-18-1-3ML-M-Q</b> 형태입니다. <b>1.8</b> 은 스텝 각도, <b>1</b> 은 나사 리드 1 mm, 그 다음이 용량, <b>M</b> 은 코드디스크(엔코더) 포함, <b>Q</b> 는 드라이버 포함을 뜻합니다.</p>"+figs([(D(s,0),"모델 번호 구성 — Model No. · 스텝 각도 · 나사 리드 · 용량 · 엔코더 · 드라이버")])},
 {"h":"드라이버 포트 핀 배열 (Driver port)","html":"<p>+ · − 가 DC24V 전원, TX · RX · GND 가 RS232, H · L 이 CANH · CANL, A · B 가 RS485A · RS485B 입니다. 반대편은 A+/A− · B+/B− 모터 상 배선, IO1 포토커플러 신호, A · B 엔코더 상, NC(미사용), +5V, GND, PE 접지입니다.</p>"},
 {"h":"기능 · 명령 (Function)","html":"<ul>"
  "<li><b>주소 설정</b> — 시리얼 포트로 설정</li>"
  "<li><b>통신 속도 설정</b> — RS232 / RS485 / CAN 각각 설정</li>"
  "<li><b>CAN 목적지 주소</b> — 여러 대 병렬 제어 시 우선 주소 지정</li>"
  "<li><b>속도 설정</b> — 3 mL 1~600 rpm, 8 mL 1~300 rpm (기체·액체·모델에 따라 차이)</li>"
  "<li><b>세분화 설정</b> — 2~32 단계</li>"
  "<li><b>파라미터 · 버전 조회</b>, <b>공장 초기화</b>, <b>CW/CCW 방향</b>, <b>리셋(원점 복귀)</b>, <b>강제 정지</b>, <b>모터 상태 조회</b></li></ul>"},
 {"h":"제조사 기술 자료 (Technical data)","html":figs([(D(s,i),c) for i,c in [
   (1,"고정밀 수직형 미니 시린지 펌프 — 컴팩트 · 엔코더 내장 · 무누출 300만 회"),
   (2,"제조사 기술 파라미터 표 (배압 · 치수 · 중량 포함)"),
   (3,"무누출 300만 회 — 상온 상압 순수 이송 자체 시험 결과"),
   (4,"한 손에 들어오는 크기"),
   (5,"내산·내알칼리 구조와 습부 재질 구성"),
   (6,"수입 스텝모터 · 저마찰 베어링 구조"),
   (7,"이중 프로토콜(Tecan · 커스텀) 지원과 엔코더 탈조 보정"),
   (8,"분해능 0.005 mm · 최소 샘플링 0.833 / 2.083 µL"),
   (9,"RS232/RS485 배선과 전원 배선 — 다중 캐스케이드 지원")]])},
 {"h":"용도 (Applications)","html":"<p>미량 정량이 필요한 분석·검사 라인에 씁니다.</p><ul><li>의료 분석 장비 (Medical analysis equipment)</li><li>크로마토그래피 분석기 (Chromatographic analyzers)</li><li>식품·음료 검사 분석 시스템</li><li>수질 온라인 분석기 (Water quality on-line analyzer)</li><li>석유 검사 장비 · 바이오의약 추출 장치</li></ul>"}],
"faq":[
 {"tag":"용량","q":"SY-09은 어떤 용량이 있나요?","a":"3 mL과 8 mL입니다. 정격 스트로크는 각각 18 mm(3600 스텝), 19.2 mm(3840 스텝)입니다."},
 {"tag":"정밀도","q":"최소 토출량은 얼마인가요?","a":"스텝당 0.005 mm 이동이며 3 mL은 0.833 µL, 8 mL은 2.083 µL입니다."},
 {"tag":"엔코더","q":"엔코더가 내장되면 뭐가 좋나요?","a":"탈조가 생기면 자동으로 보정하고 모터 상태를 통신으로 조회할 수 있어, 무인 운전 중 위치 오차를 잡아냅니다."},
 {"tag":"제어","q":"어떤 프로토콜을 지원하나요?","a":"Tecan 프로토콜과 커스텀 프로토콜을 함께 지원합니다. 물리 계층은 RS232 · RS485 · CAN입니다."},
 {"tag":"속도","q":"속도는 어디까지 올릴 수 있나요?","a":"3 mL은 1~600 rpm, 8 mL은 1~300 rpm입니다. 기체와 액체, 모델에 따라 차이가 있습니다."},
 {"tag":"수명","q":"수명은 얼마나 되나요?","a":"제조사 자체 시험에서 상온 상압 순수 기준 무누출 300만 회입니다."},
 {"tag":"확장","q":"여러 대를 하나의 버스에 물릴 수 있나요?","a":"RS232/RS485 버스로 여러 대를 캐스케이드할 수 있고, CAN에서는 우선 주소를 지정해 병렬 제어합니다."}],
"ld":{"name":"Runze Fluid 시린지 펌프 SY-09","sku":"SY-09","category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
 "description":"3/8 mL 엔코더 내장 수직형 정밀 시린지 펌프. 정격 스트로크 18/19.2 mm, 분해능 0.833/2.083 µL, 습부 붕규산 유리·PCTFE·PTFE, RS232/RS485/CAN.",
 "models":["SY-09-3ML","SY-09-8ML"],"count":2},
"source":SRCU("peristaltic-pump-sy-09")})

# ---------------- SY-09S ----------------
s="syringe-pump-sy-09s"; g=gal(s)
P.append({
"slug":"syringe-pump-sy-09s","name":"시린지 펌프 SY-09S","name_en":"Runze Fluid Syringe Pump SY-09S",
"sub":"3 / 8 mL · 엔코더 + 솔레노이드 밸브 내장 · 듀얼 포트 PPS 펌프헤드 · RS232 / RS485",
"category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
"title":"Runze Fluid 시린지 펌프 SY-09S — 솔레노이드 밸브 내장 3·8 mL 시린지 펌프 | 실험셋업연구소",
"desc":"Runze Fluid 시린지 펌프 SY-09S — 3 / 8 mL, 엔코더와 솔레노이드 밸브 내장, 듀얼 포트 PPS 펌프헤드, 펌프헤드 데드볼륨 35 µL, 정격 스트로크 18 / 19.2 mm, RS232/RS485. 가격 문의.",
"images":g,"image_alt":"Runze Fluid 시린지 펌프 SY-09S",
"answer":"시린지 펌프 SY-09S는 SY-09에 솔레노이드 밸브까지 펌프헤드에 넣은 모델로, 별도 분배 밸브 없이 듀얼 포트 PPS 헤드 하나로 흡입·토출 유로를 전환하는 3·8 mL 정밀 시린지 펌프입니다.",
"features":[
 "<b>솔레노이드 밸브 내장</b> — 듀얼 포트 PPS 펌프헤드로 흡입·토출 유로를 하나의 헤드에서 전환합니다",
 "<b>엔코더 내장</b> — 탈조를 자동 보정하고 위치를 되먹임합니다",
 "용량 <b>3 mL · 8 mL</b>, 정격 스트로크 18 mm(3600 스텝) / 19.2 mm(3840 스텝)",
 "분해능 <b>0.005 mm</b> — 3 mL은 0.833 µL, 8 mL은 2.083 µL 입니다",
 "습부는 <b>붕규산 유리 · PTFE · PPS · PEEK / EPDM / FKM(솔레노이드 밸브)</b> 이며 하우징은 일체 사출 PPS 입니다",
 "펌프헤드 데드볼륨 <b>35 µL</b> — 캐리오버를 줄여야 하는 미량 분석에 유리합니다",
 "<b>Tecan 프로토콜과 커스텀 프로토콜</b> 을 함께 지원하고 RS232/RS485 버스로 여러 대를 캐스케이드합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · PPS · PEEK / EPDM / FKM (솔레노이드 밸브)"],
 ["유량 정확도 (Accuracy)","≤1% @100% 정격 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% @100% 정격 스트로크"],
 ["수명 (Service life)","무누출 300만 회"],
 ["펌프헤드 데드볼륨 (Dead volume)","35 µL"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 1 mm"],
 ["연결부 (Connection)","1/4-28 UNF 암나사"],
 ["통신 (Communication)","RS232 / RS485 버스"],
 ["통신 속도 (Baud rate)","9600 · 19200 · 38400 · 57600 · 115200 bps"],
 ["전원 (Power supply)","DC24V / 3A"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 이하 · 비결로"]],
"variants":{"heading":"용량별 규격 (Volume)","head":["항목","3 mL","8 mL"],
 "rows":[["정격 스트로크 (Rated stroke)","18 mm · 3600 스텝","19.2 mm · 3840 스텝"],
  ["최대 회전수 (Max speed)","600 rpm","300 rpm"],
  ["선속도 (Linear speed)","0.017-10 mm/s","0.017-5 mm/s"],
  ["주행 시간 (Running time)","1.8-1080 s","3.84-1152 s"],
  ["분해능 (Resolution)","0.005 mm / 0.833 µL","0.005 mm / 2.083 µL"],
  ["시린지 내경 (Syringe ID)","14.55 mm","23.03 mm"],
  ["순중량 (Net weight)","0.48 kg","0.50 kg"]],
 "note":"사양은 제조사 브로슈어 표기이며, 펌프헤드 데드볼륨은 유로 구성에 따라 35 µL 와 116.5 µL 두 값이 함께 표기됩니다."},
"buybox":[],
"related":REL(' · <a href="/brands/runze/syringe-pump-sy-09/">시린지 펌프 SY-09</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#솔레노이드밸브내장","/product/"],["#미량분주","/product/"]],
"sections":[
 {"h":"제조사 기술 자료 (Technical data)","html":figs([(D(s,i),c) for i,c in [
   (0,"고정밀 시린지 펌프 SY-09S — 컴팩트 · 엔코더/솔레노이드 밸브 내장 · 무누출 300만 회"),
   (1,"제조사 기술 파라미터 표 (용량 · 스트로크 · 분해능 · 데드볼륨)"),
   (2,"무누출 300만 회 — 상온 상압 순수 이송 자체 시험 결과"),
   (3,"한 손에 들어오는 크기"),
   (4,"듀얼 포트 PPS 펌프헤드와 습부 재질 구성"),
   (5,"수입 스텝모터 · 저마찰 베어링 구조"),
   (6,"엔코더 · 솔레노이드 밸브 내장 · 이중 프로토콜 지원"),
   (7,"분해능 0.005 mm · 최소 샘플링 0.833 / 2.083 µL"),
   (8,"RS232/RS485 버스 배선과 전원 배선 — 다중 캐스케이드")]])},
 {"h":"주의 사항 (Chemical compatibility)","html":"<p>습부는 붕규산 유리, PTFE, PPS 와 솔레노이드 밸브의 PEEK / EPDM / FKM 입니다. 대부분의 액체와 유기 용매를 견디지만 <b>불산(HF)</b> 과 위 재질에 반응하는 액체에는 쓸 수 없습니다.</p>"},
 {"h":"용도 (Applications)","html":"<p>밸브를 따로 달기 어려운 좁은 장비 안에서 흡입·토출을 함께 처리해야 할 때 씁니다.</p><ul><li>의료 분석 장비 · 체외진단 장비</li><li>수질 온라인 분석기</li><li>실험실 자동 전처리 장비</li></ul>"}],
"faq":[
 {"tag":"차이","q":"SY-09과 SY-09S는 뭐가 다른가요?","a":"SY-09S는 펌프헤드에 솔레노이드 밸브가 들어가 있습니다. 별도 분배 밸브 없이 듀얼 포트 PPS 헤드 하나로 흡입·토출 유로를 전환합니다."},
 {"tag":"데드볼륨","q":"펌프헤드 데드볼륨은 얼마인가요?","a":"제조사 표기 기준 35 µL입니다. 유로 구성에 따라 116.5 µL 값이 함께 표기되므로 실제 구성으로 확인이 필요합니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"붕규산 유리, PTFE, PPS이며 솔레노이드 밸브 쪽은 PEEK, EPDM, FKM입니다. 불산과 이 재질들에 반응하는 액체는 피해야 합니다."},
 {"tag":"제어","q":"통신은 무엇을 지원하나요?","a":"RS232와 RS485 버스입니다. 9600~115200 bps이며 여러 대를 데이지체인으로 물릴 수 있습니다."},
 {"tag":"정밀도","q":"최소 토출량은 얼마인가요?","a":"3 mL은 0.833 µL, 8 mL은 2.083 µL입니다."}],
"ld":{"name":"Runze Fluid 시린지 펌프 SY-09S","sku":"SY-09S","category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
 "description":"솔레노이드 밸브·엔코더 내장 3/8 mL 정밀 시린지 펌프. 듀얼 포트 PPS 펌프헤드, 데드볼륨 35 µL, 정격 스트로크 18/19.2 mm, RS232/RS485.",
 "models":["SY-09S-3ML","SY-09S-8ML"],"count":2},
"source":SRCU("syringe-pump-sy-09s")})

add(P)
