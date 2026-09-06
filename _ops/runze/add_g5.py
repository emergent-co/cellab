# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
BAUD="RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"
DRV={"heading":"드라이버 포트 핀 배열 (Driver port)","head":["포트","설명","포트","설명"],
 "rows":[["H","CANH","B+ / B−","B상 배선"],["L","CANL","A+ / A−","A상 배선"],
  ["A","RS485 A","O1","포토커플러 배선"],["B","RS485 B","O2","포토커플러 배선"],
  ["GND","GND","O3","포토커플러 배선"],["RX","RS232 RX","V1","포토커플러 전원"],
  ["TX","RS232 TX","V2","포토커플러 전원"],["−","DC24V","V3","포토커플러 전원"],["+","DC24V","GND","GND"]]}
P=[]

# ---------------- MiNi SY-04 ----------------
s="programmable-syringe-pump"
P.append({
"slug":"programmable-syringe-pump","name":"프로그래머블 시린지 펌프 MiNi SY-04","name_en":"Runze Fluid MiNi SY-04 Programmable Syringe Pump",
"sub":"5 / 10 / 20 mL · KSS 볼스크류 · 단채널 · 이중채널 · 42×42 mm · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
"title":"Runze Fluid 프로그래머블 시린지 펌프 MiNi SY-04 — 5·10·20 mL 볼스크류 정량 펌프 | 실험셋업연구소",
"desc":"Runze Fluid MiNi SY-04 프로그래머블 시린지 펌프 — 5 / 10 / 20 mL, KSS 볼스크류(리드 1 mm), 분해능 0.4154~2.0833 µL, 압력 0-1.2 MPa(물), 수명 무누출 300만 회, 습부 붕규산 유리·PTFE, RS232/RS485/CAN. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 프로그래머블 시린지 펌프 MiNi SY-04",
"answer":"MiNi SY-04는 42×42 mm 금속 하우징에 KSS 볼스크류를 넣은 5·10·20 mL 프로그래머블 시린지 펌프로, 단채널과 이중채널 구성 중에서 골라 소형 장비 안에 넣어 정량 이송에 씁니다.",
"features":[
 "용량 <b>5 mL · 10 mL · 20 mL</b> — 정격 스트로크 30 mm(12000 스텝) / 24.08 mm(9632 스텝) / 24 mm(9600 스텝)",
 "구동부가 <b>KSS 볼스크류(리드 1 mm)</b> — 소형기에서 정밀도와 수명을 함께 잡습니다",
 "정확도 <b>≤1%</b>, 반복 정밀도 <b>3‰ ~ 7‰</b> (정격 스트로크 100% 기준)",
 "압력 정격 <b>0-1.0 MPa(공기) · 0-1.2 MPa(물)</b>, 수명 무누출 <b>300만 회</b>",
 "<b>포토센서로 피스톤 원점</b> 을 검출합니다",
 "<b>단채널 · 이중채널</b> 구성과 드라이버 유무를 주문 코드로 선택합니다",
 "습부는 <b>붕규산 유리 · PTFE</b>, 하우징은 금속입니다 — 상한 리미트에 OMRON 포토커플러(NPN) 2개",
 "치수 <b>42×42×191 mm(드라이버 없음) / 42×42×206.2 mm(드라이버 포함)</b>, 0.72 kg"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","3‰ ~ 7‰ @100% 스트로크"],
 ["압력 정격 (Pressure rating)","0-1.0 MPa (공기) · 0-1.2 MPa (물)"],
 ["최대 압력 (Max pressure)","정압 0-1.0 MPa · 부압 0-0.05 MPa (시험 기준)"],
 ["수명 (Service life)","무누출 300만 회 (매질 물)"],
 ["원점 검출 (Detection)","포토센서로 피스톤 원점 검출"],
 ["선속도 (Linear speed)","0.017 ~ 5 mm/s"],
 ["구동부 (Actuator)","KSS 볼스크류 · 리드 1 mm"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["유로 채널 (Channel)","단채널 · 이중채널 선택"],
 ["통신 (Communication)","RS232 / RS485 / CAN"],
 ["통신 속도 (Baud rate)",BAUD],
 ["전원 (Power supply)","DC24V / 1.5A · 최대 15 W"],
 ["치수 L×W×H (Dimension)","42×42×191 mm (드라이버 없음) · 42×42×206.2 mm (드라이버 포함)"],
 ["순중량 (Net weight)","0.72 kg"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","80% 미만 · 비결로"]],
"variants":{"heading":"용량별 규격 (Volume)","head":["항목","5 mL","10 mL","20 mL"],
 "rows":[["정격 스트로크 (Rated stroke)","30 mm · 12000 스텝","24.08 mm · 9632 스텝","24 mm · 9600 스텝"],
  ["시린지 내경 (Syringe ID)","14.55 mm","23 mm","32 mm"],
  ["모터 속도 (Motor speed)","300 rpm","300 rpm","250 rpm"],
  ["주행 시간 (Running time)","6 s – 1765 s","4.8 s – 1416 s","5.76 s – 1412 s"],
  ["분해능 (Resolution)","0.0025 mm / 0.4154 µL","0.0025 mm / 1.0381 µL","0.0025 mm / 2.0833 µL"]]},
"buybox":[],
"related":REL(' · <a href="/brands/runze/syringe-pump-sy-08/">시린지 펌프 SY-08</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="https://www.runzefluid.com/uploads/file/mini-sy-04.pdf" rel="nofollow">MiNi SY-04 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/mini-sy-04-syringe-pump-v2-7.pdf" rel="nofollow">MiNi SY-04 매뉴얼 V2.7 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=A3LyYjxruqM" rel="nofollow">MiNi SY-04 제조사 소개 영상</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#볼스크류","/product/"],["#소형정량펌프","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-LS-0.9-1-□-□-□</b> 형태입니다. <b>0.9</b> 는 스텝 각도, <b>1</b> 은 나사 리드 1 mm, 그 다음이 용량(5 · 10 · 20 mL), 채널(1 단채널 · 2 이중채널), 마지막이 드라이버 유무(Q 포함 · 생략 미포함)입니다.</p>"+figs([(D(s,0),"모델 번호 구성 — 스텝 각도 · 리드 · 용량 · 채널 · 드라이버")])},
 {"h":"제품 구조 (Product structure)","html":"<p>금속 하우징에 붕규산 시린지를 물리고, 상한 리미트에 OMRON 포토커플러(NPN) 2개를 씁니다. 4×M3 마운팅 홀이 있으며, 마운팅 홀더는 RS232/RS485/CAN 드라이버가 달린 MiNi SY-04 구성에만 포함됩니다.</p>"+figs([(D(s,1),"단채널 · 이중채널 구조 — 금속 하우징 · 붕규산 시린지 · 상한 포토커플러 · 4×M3 마운팅 홀")])},
 {"h":"드라이버 포트 · 외형 치수 (Driver port & dimension)","html":figs([(D(s,2),"드라이버 포트 배치 — GND · RX · TX · − · + / V3 · V2 · V1 · O3 · O2 · O1"),(D(s,3),"용량별 외형 치수 도면 (5 / 10 / 20 mL)")])},
 {"h":"용도 (Applications)","html":"<p>리드스크류와 고정밀 붕규산 실린더 조합이라 소형 장비에 넣기 좋습니다.</p><ul><li>소형 분석 장비 정량 이송</li><li>시약 분주 · 희석</li><li>온라인 모니터링 설비</li></ul>"}],
"faq":[
 {"tag":"용량","q":"MiNi SY-04는 어떤 용량이 있나요?","a":"5 mL, 10 mL, 20 mL입니다. 정격 스트로크는 각각 30 mm, 24.08 mm, 24 mm이고 스텝 수는 12000 / 9632 / 9600입니다."},
 {"tag":"구동","q":"볼스크류를 쓰면 뭐가 다른가요?","a":"KSS 볼스크류(리드 1 mm)를 써서 사다리꼴 나사보다 마찰이 적고 역구동 효율이 좋습니다. 반복 정밀도는 3‰~7‰입니다."},
 {"tag":"채널","q":"이중채널은 무엇인가요?","a":"시린지 두 개를 한 몸체에 넣어 동시에 구동하는 구성입니다. 주문 코드의 채널 자리에서 1(단채널)과 2(이중채널)를 고릅니다."},
 {"tag":"압력","q":"압력 정격은 어떻게 되나요?","a":"공기 0-1.0 MPa, 물 0-1.2 MPa입니다. 회로 기준으로는 정압 0-1.0 MPa, 부압 0-0.05 MPa입니다."},
 {"tag":"설치","q":"드라이버 없이도 쓸 수 있나요?","a":"드라이버 없는 구성도 있습니다. 다만 마운팅 홀더는 RS232/RS485/CAN 드라이버가 달린 구성에만 들어갑니다. 치수도 191 mm와 206.2 mm로 달라집니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"붕규산 유리와 PTFE입니다."}],
"ld":{"name":"Runze Fluid 프로그래머블 시린지 펌프 MiNi SY-04","sku":"MiNi SY-04","category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
 "description":"5/10/20 mL 프로그래머블 시린지 펌프. KSS 볼스크류(리드 1 mm), 분해능 0.4154~2.0833 µL, 0-1.2 MPa(물), 습부 붕규산 유리·PTFE, 단채널·이중채널, RS232/RS485/CAN.",
 "models":["MiNi SY-04-5ML","MiNi SY-04-10ML","MiNi SY-04-20ML"],"count":3},
"source":SRCU("programmable-syringe-pump")})

# ---------------- RPM-01 ----------------
s="stepper-motor-syringe-pump"
P.append({
"slug":"stepper-motor-syringe-pump","name":"스텝모터 플런저 펌프 RPM-01","name_en":"Runze Fluid RPM-01 Stepper Motor Syringe Pump",
"sub":"1 / 2 / 3 mL 분주 · 편심 기어 구동 · 이중 유로 연속 토출 · 1-360 mL/min · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 마이크로 플런저 펌프",
"title":"Runze Fluid 스텝모터 플런저 펌프 RPM-01 — 연속 토출형 정량 펌프 | 실험셋업연구소",
"desc":"Runze Fluid RPM-01 스텝모터 플런저 펌프 — 1 / 2 / 3 mL 분주 분해능, 편심 기어 구동으로 맥동 없는 연속 토출, 유량 1-360 mL/min, 압력 0.3 MPa(물), 습부 붕규산 유리·PTFE, RS232/RS485/CAN. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 스텝모터 플런저 펌프 RPM-01",
"answer":"RPM-01은 편심 기어로 플런저를 왕복시키는 이중 유로 정량 펌프로, 연동펌프와 달리 흡입과 토출이 끊기지 않고 이어지는 연속 토출을 하면서 1회 1~3 mL 단위로 분주합니다.",
"features":[
 "<b>연속 토출</b> — 이중 유로 구조로 흡입과 토출이 번갈아 이어져 연동펌프처럼 끊기지 않습니다",
 "1회 분주 <b>1 mL · 2 mL · 3 mL</b> 시린지 용량 선택",
 "유량 <b>1 ~ 360 mL/min</b> (RPM-01-D), 정격 속도 1 ~ 120 rpm",
 "정확도 <b>≤1%</b>, 반복 정밀도 <b>0.3~0.7%</b>, 수명 무누출 <b>300만 회</b>(매질 물)",
 "구동부는 <b>편심 기어(Eccentric gear)</b> — 회전 운동을 플런저 왕복으로 바꿉니다",
 "습부는 <b>붕규산 유리 · PTFE</b> 로 시료를 오염시키지 않고 부식성 액체를 견딥니다",
 "<b>무보수 스텝모터</b> 구동에 RS232 / RS485 / CAN 제어(드라이버 포함 사양)"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE"],
 ["시린지 용량 (Syringe volume)","1 mL · 2 mL · 3 mL"],
 ["분주 분해능 (Dispensing)","1 mL · 2 mL · 3 mL"],
 ["정격 최대 속도 (Max speed)","120 rpm (RPM-01-D)"],
 ["정격 최소 속도 (Min speed)","1 rpm"],
 ["유량 (Flow rate)","1 ~ 360 mL/min (RPM-01-D)"],
 ["토출 특성 (Flow regularity)","연속 토출 (연동펌프 대체)"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% @100% 스트로크"],
 ["압력 정격 (Pressure rating)","0.3 MPa (매질 물)"],
 ["수명 (Service life)","무누출 300만 회 (매질 물)"],
 ["구동부 (Actuator)","편심 기어 (Eccentric gear)"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["유로 채널 (Channel)","이중 유로 (Double channel)"],
 ["통신 (Communication)","RS232 / RS485 / CAN (드라이버 포함 사양)"],
 ["통신 속도 (Baud rate)",BAUD],
 ["전원 (Power supply)","DC24V / 1.5A · 최대 15 W"],
 ["치수 L×W×H (Dimension)","98.3 × 42 × 116.4 mm (RPM-01-D)"],
 ["순중량 (Net weight)","0.8 kg (RPM-01-D)"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","80% 미만"]],
"variants":DRV,
"buybox":[],
"related":REL(' · <a href="/brands/runze/rp42-industrial-micro-syringe-pump/">산업용 마이크로 플런저 펌프 RP42</a> · <a href="https://www.runzefluid.com/uploads/file/rpm-01.pdf" rel="nofollow">RPM-01 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/rpm-01-users-manula-v2-5.pdf" rel="nofollow">RPM-01 매뉴얼 V2.5 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=u9K_wAPWLKI" rel="nofollow">RPM-01 제조사 소개 영상</a>'),
"keywords":KW+[["#플런저펌프","/product/"],["#연속토출","/product/"],["#정량펌프","/product/"]],
"sections":[
 {"h":"구조 · 배관 연결 (Structure & tubing)","html":"<p>이중 유로 구조로 한쪽이 흡입할 때 다른 쪽이 토출합니다. 배관은 1/4-28 UNF 로 연결합니다.</p>"
  +figs([(D(s,i),"RPM-01 구조와 배관 연결 · 외형 치수 (제조사 자료)") for i in range(len(META[s]["det"]))])},
 {"h":"연동펌프와의 차이","html":"<p>연동펌프는 롤러가 튜브를 눌러 밀기 때문에 튜브 수명과 맥동을 함께 관리해야 합니다. RPM-01은 붕규산 유리 실린더와 PTFE 플런저로 밀어내므로 튜브 마모가 없고 토출이 끊기지 않습니다. 대신 유량 상한이 360 mL/min 이고 압력 정격은 0.3 MPa 입니다.</p>"},
 {"h":"용도 (Applications)","html":"<ul><li>시약 연속 정량 공급</li><li>온라인 분석기 시료 이송</li><li>부식성 액체 정량 — 습부에 금속과 튜브가 없습니다</li></ul>"}],
"faq":[
 {"tag":"원리","q":"RPM-01은 시린지 펌프인가요 플런저 펌프인가요?","a":"편심 기어로 플런저를 왕복시키는 플런저(피스톤) 정량 펌프입니다. 제조사는 스텝모터 시린지 펌프 계열로 분류하지만 동작은 왕복 플런저 방식입니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"RPM-01-D 기준 1~360 mL/min입니다. 속도는 1~120 rpm입니다."},
 {"tag":"차이","q":"연동펌프 대신 쓸 수 있나요?","a":"제조사가 연동펌프 대체 용도로 안내합니다. 튜브 마모가 없고 토출이 끊기지 않는 대신 압력 정격이 0.3 MPa로 낮습니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"붕규산 유리와 PTFE입니다. 시료를 오염시키지 않습니다."},
 {"tag":"분주","q":"1회 분주량은 어떻게 되나요?","a":"시린지 용량에 따라 1 mL, 2 mL, 3 mL입니다."},
 {"tag":"제어","q":"통신 제어가 되나요?","a":"드라이버가 포함된 사양에서 RS232 · RS485 · CAN을 지원합니다. 주소와 파라미터는 시리얼 포트로 설정합니다."}],
"ld":{"name":"Runze Fluid 스텝모터 플런저 펌프 RPM-01","sku":"RPM-01","category":"시린지 펌프 · 마이크로 플런저 펌프",
 "description":"편심 기어 구동 이중 유로 정량 플런저 펌프. 1/2/3 mL 분주, 유량 1-360 mL/min, 0.3 MPa(물), 습부 붕규산 유리·PTFE, 연속 토출, RS232/RS485/CAN.",
 "models":["RPM-01","RPM-01-D"],"count":3},
"source":SRCU("stepper-motor-syringe-pump")})

add(P)
