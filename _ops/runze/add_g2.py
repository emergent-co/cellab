# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
P=[]

# ---------------- OEM Syringe Pump ----------------
s="oem-syringe-pump"
P.append({
"slug":"oem-syringe-pump","name":"OEM 시린지 펌프","name_en":"Runze Fluid OEM Syringe Pump",
"sub":"50 / 100 mL 대용량 · 볼스크류 구동 · 3포트 고압 밸브 조합 · RS232 / RS485 / CAN",
"category":"시린지 펌프 · OEM 대용량 모듈",
"title":"Runze Fluid OEM 시린지 펌프 — 50·100 mL 대용량 커스터마이즈 모듈 | 실험셋업연구소",
"desc":"Runze Fluid OEM 시린지 펌프 — 50 / 100 mL 대용량, 정확도 ≤1%, 볼스크류(리드 2 mm) 구동, 습부 붕규산 유리 실린더·PTFE 피스톤, 정압 0-1.0 MPa, RS232/RS485/CAN. 크기·재질·마운팅 커스터마이즈. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid OEM 시린지 펌프",
"answer":"OEM 시린지 펌프는 50·100 mL 대용량 시린지를 볼스크류로 구동하는 장비 내장형 모듈로, 용량·재질·마운팅 홀·부속 구성을 장비에 맞춰 주문 제작하는 라인입니다.",
"features":[
 "용량 <b>50 mL · 100 mL</b> 대용량 — 표준 시린지 펌프로 감당하기 어려운 구간을 커버합니다",
 "정확도 <b>≤1% @100% 스트로크</b>, 반복 정밀도 <b>0.3~0.7%</b>",
 "수명 <b>무누출 300만 회</b>(매질 물), 포토센서로 피스톤 원점을 검출합니다",
 "구동부는 <b>볼스크류(리드 2 mm)</b> — 회전 운동을 직선 운동으로 바꿔 정밀도와 역구동성을 함께 확보합니다",
 "습부는 <b>붕규산 유리 실린더 · PTFE 피스톤 · PTFE 출구</b> 이며 푸시로드는 304 스테인리스입니다",
 "<b>3포트 고압 밸브</b> 를 얹은 수평형, 50 mL 3연 병렬형 등 조합 구성이 가능합니다",
 "<b>커스터마이즈</b> — 시린지 용량(50/100 mL), 재질(SST · POM · PEEK), 마운팅 홀 위치를 도면대로 제작합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 실린더 · PTFE 피스톤 · PTFE 출구"],
 ["용량 (Volume)","50 mL · 100 mL"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% @100% 스트로크"],
 ["수명 (Service life)","무누출 300만 회 (매질 물)"],
 ["원점 검출 (Detection)","포토센서로 피스톤 원점 검출"],
 ["구동부 (Actuator)","볼스크류 · 리드 2 mm (Ball screw)"],
 ["압력 (Pressure)","0-1.0 MPa (공기) · 0-1.2 MPa (물)"],
 ["최대 압력 (Max pressure)","정압 0-1.0 MPa · 부압 0-0.05 MPa"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 (Communication)","RS232 / RS485 / CAN"],
 ["통신 속도 (Baud rate)","RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"],
 ["전원 (Power supply)","DC24V / 1.5A · 최대 15 W"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"],
 ["납기 (Delivery time)","약 20~25 영업일 (제조사 표기)"]],
"variants":{"heading":"드라이버 포트 핀 배열 (Driver port)","head":["포트","설명","포트","설명"],
 "rows":[["H","CANH","B+ / B−","B상 배선"],["L","CANL","A+ / A−","A상 배선"],
  ["A","RS485 A","O1","포토커플러 배선"],["B","RS485 B","O2","포토커플러 배선"],
  ["GND","GND","O3","포토커플러 배선"],["RX","RS232 RX","V1","포토커플러 전원"],
  ["TX","RS232 TX","V2","포토커플러 전원"],["−","DC24V","V3","포토커플러 전원"],["+","DC24V","GND","GND"]]},
"buybox":[],
"related":REL(' · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="/brands/runze/3-way-switching-valve/">3방 스위칭 밸브 MRV-01B</a> · <a href="/brands/runze/flangeless-fittings/">플랜지리스 피팅</a>'),
"keywords":KW+[["#OEM시린지펌프","/product/"],["#대용량시린지펌프","/product/"],["#장비내장모듈","/product/"]],
"sections":[
 {"h":"커스터마이즈 범위 (Customization)","html":"<ul>"
  "<li><b>크기</b> — 통상 50 mL 대용량 시린지, 50 mL / 100 mL 주문 제작. 고붕규산 유리 몸체, 304 스테인리스 푸시로드, PTFE 피스톤, 최대 압력 0.68 MPa, 표준 1/4-28 UNF 나사</li>"
  "<li><b>재질</b> — SST · POM · PEEK</li>"
  "<li><b>마운팅</b> — 고객 도면에 맞춘 마운팅 홀 가공, 패널 사전 타공, 커스텀 부품 지원</li></ul>"},
 {"h":"대표 구성 (Typical configurations)","html":"<ol>"
  "<li><b>100 mL 수평형 + 3포트 고압 밸브</b> — 내식·내열·무보수 구성. 스테인리스 부품을 배치 설계했고 대부분을 내식·내열 재질로 씁니다.</li>"
  "<li><b>100 mL 수평형 / 50 mL 3포트 수평형</b> — 3포트 고압 밸브 · 스텝모터 · 기밀 시린지 · 포토커플러 · 리니어 가이드 · 볼스크류 구성</li>"
  "<li><b>50 mL 3연 수평형</b> — 50 mL 기밀 시린지 3개를 나란히 병렬 구동. 패널 사전 타공과 커스텀 부품을 지원합니다.</li></ol>"
  +figs([(D(s,i),"OEM 시린지 펌프 구성 예 (제조사 자료)") for i in range(len(META[s]["det"]))])},
 {"h":"용도 (Applications)","html":"<p>대용량 정량이 필요한 장비에 넣어 씁니다.</p><ul><li>정용량 분주 시스템 (Constant specific volume dispensing)</li><li>프로그래머블 제어 시스템</li><li>의료·산업·실험실·환경 분석 장비</li></ul>"}],
"faq":[
 {"tag":"용량","q":"OEM 시린지 펌프는 몇 mL까지 나오나요?","a":"통상 50 mL와 100 mL입니다. 고붕규산 유리 몸체에 304 스테인리스 푸시로드, PTFE 피스톤 구성이며 최대 압력은 0.68 MPa입니다."},
 {"tag":"구동","q":"일반 시린지 펌프와 구동부가 다른가요?","a":"볼스크류(리드 2 mm)를 씁니다. 사다리꼴 나사보다 정밀도와 역구동 효율이 좋아 대용량 구동에 유리합니다."},
 {"tag":"커스터마이즈","q":"어디까지 맞춤 제작이 되나요?","a":"시린지 용량, 재질(SST·POM·PEEK), 마운팅 홀 위치와 패널 타공, 부속 부품 구성까지 도면대로 제작합니다."},
 {"tag":"압력","q":"압력 정격은 어떻게 되나요?","a":"공기 0-1.0 MPa, 물 0-1.2 MPa이고, 회로 기준 정압 0-1.0 MPa, 부압 0-0.05 MPa입니다."},
 {"tag":"납기","q":"납기는 얼마나 걸리나요?","a":"제조사 표기 기준 약 20~25 영업일입니다. 커스터마이즈 범위에 따라 달라지므로 사양 확정 후 다시 확인이 필요합니다."},
 {"tag":"제어","q":"어떤 통신을 지원하나요?","a":"RS232 · RS485 · CAN입니다. RS232/RS485는 9600~115200 bps, CAN은 100 Kbps~1 Mbps입니다."}],
"ld":{"name":"Runze Fluid OEM 시린지 펌프","sku":"OEM-SYRINGE-PUMP","category":"시린지 펌프 · OEM 대용량 모듈",
 "description":"50/100 mL 대용량 OEM 시린지 펌프 모듈. 볼스크류(리드 2 mm) 구동, 정확도 ≤1%, 습부 붕규산 유리·PTFE, 0-1.2 MPa(물), RS232/RS485/CAN, 크기·재질·마운팅 커스터마이즈.",
 "models":["OEM 50ML","OEM 100ML"],"count":2},
"source":SRCU("oem-syringe-pump")})

# ---------------- SY-03B T-DK 8ch ----------------
s="8-channel-micro-syringe-pump-module"
P.append({
"slug":"8-channel-micro-syringe-pump-module","name":"8채널 마이크로 시린지 펌프 SY-03B T-DK","name_en":"Runze Fluid SY-03B T-DK 8-Channel Micro Syringe Pump",
"sub":"8채널 독립 구동 · 채널별 3방 솔레노이드 밸브 · 정격 스트로크 60 mm · ASCII / Modbus",
"category":"시린지 펌프 · 다채널 모듈",
"title":"Runze Fluid 8채널 마이크로 시린지 펌프 SY-03B T-DK — 나노리터 병렬 분주 모듈 | 실험셋업연구소",
"desc":"Runze Fluid SY-03B T-DK 8채널 마이크로 시린지 펌프 — 채널마다 3방 솔레노이드 밸브 독립 제어, 시린지 50 µL~5 mL, 정격 스트로크 60 mm(6000/48000 스텝), 최대 900 rpm, 0.15 MPa, RS232/RS485/CAN · ASCII/Modbus. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 8채널 마이크로 시린지 펌프 SY-03B T-DK",
"answer":"SY-03B T-DK는 시린지 8개를 동기 병렬 리드스크류로 밀면서 채널마다 3방 솔레노이드 밸브를 따로 제어하는 8채널 마이크로 시린지 펌프 모듈로, IVD·시약 분주·실험실 자동화 라인에 통째로 넣어 씁니다.",
"features":[
 "<b>8채널 독립 유로</b> — 동기 병렬 리드스크류로 밀고, 채널마다 3방 솔레노이드 밸브가 유로를 따로 끊고 엽니다",
 "액량 정확도 <b>≤1%</b>, 반복 오차 <b>0.3~0.5%</b>, 제어 분해능 <b>0.01 mm / 스텝</b>",
 "정격 스트로크 <b>60 mm</b> — 표준 6000 스텝, 마이크로스텝 모드 48000 스텝",
 "최대 <b>900 rpm</b>, 선속도 <b>0.01 ~ 60 mm/s</b>, 정격 스트로크 주행 1 s ~ 6000 s",
 "시린지 <b>50 µL · 100 µL · 250 µL · 500 µL · 1 mL · 2.5 mL · 5 mL</b> 선택 (Runze TK60 시린지 호환)",
 "<b>ASCII / Modbus</b> 프로토콜을 RS232 · RS485 · CAN 위에서 지원하고, 주소는 DIP 스위치로 지정합니다",
 "구동부 · 시린지 · 밸브 모듈 · 제어 기판이 <b>한 덩어리로 통합</b> 되어 장비에 그대로 얹을 수 있습니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · FKM · PPS · PEEK"],
 ["채널 (Channels)","8채널 독립 제어"],
 ["시린지 용량 (Syringe)","50 · 100 · 250 · 500 µL · 1 · 2.5 · 5 mL (Runze TK60 호환)"],
 ["액량 정확도 (Accuracy)","≤1%"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.5%"],
 ["정격 스트로크 (Rated stroke)","60 mm · 6000 스텝 (마이크로스텝 48000 스텝)"],
 ["제어 분해능 (Resolution)","0.01 mm / 스텝"],
 ["최대 속도 (Max speed)","900 rpm"],
 ["선속도 (Linear speed)","0.01 ~ 60 mm/s"],
 ["주행 시간 (Running time)","1 s ~ 6000 s (정격 스트로크)"],
 ["밸브 형식 (Valve type)","3방 솔레노이드 밸브 (3-way solenoid)"],
 ["최대 압력 (Max pressure)","0.15 MPa"],
 ["구동부 (Actuator)","사다리꼴 리드스크류 · 리드 6 mm"],
 ["연결부 (Connection)","1/4-28 UNF 암나사"],
 ["통신 (Communication)","RS232 / RS485 / CAN · ASCII / Modbus"],
 ["통신 속도 (Baud rate)","RS232/RS485 9600 · 38400 bps<br>CAN 100K · 200K · 500K · 1M bps"],
 ["전원 (Power supply)","DC24V / 3A"],
 ["치수 W×H×D (Dimension)","187 × 254 × 117.5 mm · 마운팅 홀 4 × Ø4.5 mm"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/syringe-pump-sy03b-in-dk-series/">시린지 펌프 SY-03B DK 시리즈</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="/brands/runze/three-way-solenoid-valve/">3방 솔레노이드 밸브</a>'),
"keywords":KW+[["#다채널시린지펌프","/product/"],["#IVD분주","/product/"],["#실험실자동화","/product/"]],
"sections":[
 {"h":"구성 (Module layout)","html":"<ul>"
  "<li>전환 밸브 헤드 (Switching valve head)</li><li>샘플러 — 50 µL · 100 µL · 250 µL · 500 µL · 1 mL · 1.25 mL · 2.5 mL · 5 mL 선택</li>"
  "<li>상태 표시등 · 방열 홀 · 손조임 나사</li><li>3방 솔레노이드 밸브 8조</li>"
  "<li>스텝모터 · 주소 설정 DIP 스위치 · M3 접지 홀</li></ul>"
  +figs([(D(s,4),"구동부에서 밸브 헤드 유로까지 통합 설계 — 밸브 헤드 · 샘플러 · 표시등 · 솔레노이드 밸브 · DIP 주소"),
         (D(s,2),"동기 병렬 리드스크류 구동과 채널별 독립 솔레노이드 밸브 전환 모드"),
         (D(s,6),"제조사 기술 파라미터 표")])},
 {"h":"외형 치수 (Dimension, unit: mm)","html":"<p>전체 치수는 폭 187 mm × 높이 254 mm × 깊이 117.5 mm 이고, 마운팅 홀은 4 × Ø4.5 mm 입니다.</p>"
  +figs([(D(s,7),"외형 치수 도면 (제조사 자료)")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,0),"8채널 마이크로 시린지 펌프 — 8조 솔레노이드 밸브 모듈"),(D(s,1),"다채널 병렬 유체 제어 구성"),(D(s,3),"나노리터 안정 출력 · 반복 오차 0.3~0.5%"),(D(s,5),"상위 제어 장비와의 접속 — 다중 프로토콜 · 통신 인터페이스"),(D(s,8),"모듈 외형")])},
 {"h":"용도 (Applications)","html":"<ul><li>IVD 체외진단 시스템</li><li>시약 분주 시스템 (Reagent dispensing)</li><li>실험실 자동화 장비</li><li>미세유체 플랫폼 (Microfluidic platforms)</li><li>자동 샘플링 시스템</li><li>크로마토그래피 · 생화학 분석기</li></ul>"},
 {"h":"OEM 대응","html":"<p>제조사는 IVD·실험실 자동화·분석장비 제조사를 대상으로 채널 수, 스트로크 길이, 통신 프로토콜, 기구 통합 방식을 맞춘 OEM 모듈을 공급합니다.</p>"}],
"faq":[
 {"tag":"구조","q":"8채널이 각각 따로 움직이나요?","a":"밀어내는 리드스크류는 동기 병렬 구동이고, 유로는 채널마다 3방 솔레노이드 밸브가 따로 제어합니다. 그래서 흡입·토출·유로 전환을 채널별로 다르게 걸 수 있습니다."},
 {"tag":"시린지","q":"시린지는 어떤 용량을 쓸 수 있나요?","a":"50 µL, 100 µL, 250 µL, 500 µL, 1 mL, 2.5 mL, 5 mL입니다. Runze TK60 시린지와 호환됩니다."},
 {"tag":"정밀도","q":"분해능은 얼마인가요?","a":"스텝당 0.01 mm이고 정격 스트로크 60 mm를 표준 6000 스텝, 마이크로스텝 모드에서 48000 스텝으로 나눕니다."},
 {"tag":"압력","q":"압력 정격은 어떻게 되나요?","a":"최대 액회로 압력은 0.15 MPa입니다. 솔레노이드 밸브가 들어간 구성이라 고압용은 아닙니다."},
 {"tag":"제어","q":"프로토콜은 무엇을 지원하나요?","a":"ASCII와 Modbus를 지원하며 물리 계층은 RS232 · RS485 · CAN입니다. 주소는 본체 DIP 스위치로 지정합니다."},
 {"tag":"설치","q":"장비에 넣을 때 치수가 어떻게 되나요?","a":"폭 187 mm, 높이 254 mm, 깊이 117.5 mm이고 마운팅 홀은 4 × Ø4.5 mm입니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"붕규산 유리, PTFE, FKM, PPS, PEEK입니다."}],
"ld":{"name":"Runze Fluid 8채널 마이크로 시린지 펌프 SY-03B T-DK","sku":"SY-03B T-DK","category":"시린지 펌프 · 다채널 모듈",
 "description":"8채널 독립 솔레노이드 밸브 마이크로 시린지 펌프 모듈. 시린지 50 µL~5 mL, 정격 스트로크 60 mm(6000/48000 스텝), 최대 900 rpm, 0.15 MPa, RS232/RS485/CAN, ASCII/Modbus.",
 "models":["SY-03B T-DK"],"count":1},
"source":SRCU("8-channel-micro-syringe-pump-module")})

add(P)
