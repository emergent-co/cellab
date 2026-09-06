# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
VALVE_UL=("<ul><li><b>M01</b> — Y 유로 (C-1 / 1-2 / C-2 연동)</li>"
 "<li><b>M02</b> — T 유로 (C-1-2 / C-1 / 1-2 / C-2 연동)</li>"
 "<li><b>M03</b> — 분배 유로 (C-1 / C-2 / C-3 연동)</li>"
 "<li><b>M04</b> — 라디오 유로 (C-1 / 1-2 / 2-3 / C-3 연동)</li>"
 "<li><b>M05</b> — 바이패스 유로 (C-1 / 2-3 연동, C-3 / 1-2 연동)</li>"
 "<li><b>M06 · M10 · M12</b> — 분배 유로 (C 가 1~6 / 1~9 / 1~12 포트에 선택 연결)</li></ul>")
ILS="25 · 50 · 125 · 250 · 500 µL · 1.25 · 2.5 · 5 mL (ILS 시린지)"
P=[]

# ---------------- SY-01C ----------------
s="high-precision-syringe-pump"
P.append({
"slug":"high-precision-syringe-pump","name":"고정밀 시린지 펌프 SY-01C","name_en":"Runze Fluid Smart SY-01C High Precision Syringe Pump",
"sub":"정격 스트로크 30 mm(3000 스텝) · M01~M12 분배 밸브 · 최대 450 rpm · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 밸브 일체형 모듈",
"title":"Runze Fluid 고정밀 시린지 펌프 SY-01C — 30mm 스트로크 밸브 일체형 모듈 | 실험셋업연구소",
"desc":"Runze Fluid Smart SY-01C 고정밀 시린지 펌프 — 정격 스트로크 30 mm(3000 스텝), 분해능 0.0025 mm, 최대 450 rpm, 시린지 25 µL~5 mL, M01~M12 분배 밸브, 습부 붕규산 유리·PTFE·사파이어·PCTFE. RS485/CAN 최대 15대 개별 주소. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 고정밀 시린지 펌프 SY-01C",
"answer":"Smart SY-01C는 정격 스트로크 30 mm에 분배 밸브를 얹은 마이크로 시린지 펌프로, 마이크로리터에서 밀리리터까지 정량 이송하며 RS485·CAN으로 최대 15대까지 개별 주소를 붙여 함께 제어합니다.",
"features":[
 "정격 스트로크 <b>30 mm · 3000 스텝(표준 모드)</b>, 스텝당 분해능 <b>0.0025 mm</b>",
 "최대 <b>450 rpm</b>, 선속도 0.0333 ~ 15 mm/s, 정격 스트로크 주행 2 s ~ 900 s (매질 물)",
 "정확도 <b>≤1%</b>, 반복 정밀도 <b>0.3~0.5%</b> (정격 스트로크 100% 기준)",
 "시린지 <b>"+ILS+"</b> 중에서 고릅니다",
 "분배 밸브 <b>M01 · M02 · M03 · M04 · M05 · M06 · M10 · M12</b> 조합",
 "습부는 <b>붕규산 유리 · PTFE · 사파이어 · PCTFE</b> 로 금속이 없습니다",
 "<b>RS485 / CAN 으로 최대 15대</b> 를 개별 주소로 제어하며 무보수 스텝모터 구동입니다",
 "치수 <b>142.7 × 127 × 45 mm</b>, 순중량 1.5 kg — 상·하부 M3 마운팅 홀로 세로·가로 설치 모두 됩니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · 사파이어 · PCTFE"],
 ["정확도 (Accuracy)","≤1% @100% 정격 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.5% @100% 정격 스트로크"],
 ["정격 스트로크 (Rated stroke)","30 mm · 3000 스텝 (표준 모드)"],
 ["최대 속도 (Max speed)","450 rpm"],
 ["선속도 (Linear speed)","0.0333 ~ 15 mm/s (매질 물)"],
 ["주행 시간 (Running time)","2 s ~ 900 s (정격 스트로크)"],
 ["분해능 (Resolution)","0.0025 mm / 스텝"],
 ["시린지 (Syringe)",ILS],
 ["밸브 모델 (Valve model)","M01 · M02 · M03 · M04 · M05 · M06 · M10 · M12"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 2 mm"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)","RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"],
 ["통신 주소 (Address)","개별 주소 최대 15개"],
 ["전원 (Power supply)","DC24V / 3A"],
 ["치수 L×W×H (Dimension)","142.7 × 127 × 45 mm"],
 ["순중량 (Net weight)","1.5 kg"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/multi-channel-syringe-pump/">멀티채널 시린지 펌프 SY-01B</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#고정밀분주","/product/"],["#SY01C","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-SY01C-30-M□□</b> 형태입니다. <b>30</b> 은 정격 스트로크 30 mm, <b>M□□</b> 는 조합할 분배 밸브 모델입니다.</p>"+figs([(D(s,0),"모델 번호 구성 — Model No. · Rated stroke 30 mm · Valve model")])},
 {"h":"분배 밸브 유로 구성 (Valve options)","html":"<p>C 포트가 시린지에 연결되는 공통 포트입니다.</p>"+VALVE_UL+figs([(D(s,1),"밸브 모델별 유로 논리 M01~M12와 시린지 구성")])},
 {"h":"외형 치수 · 마운팅 (Dimension, unit: mm)","html":"<p>상부 2-M3, 하부 M3, 측면 4-M3 마운팅 홀이 있습니다.</p>"+figs([(D(s,2),"외형 치수와 마운팅 홀 배치 도면")])},
 {"h":"포트 정의 · 배선 (Port definition & wiring)","html":figs([(D(s,3),"포트 정의와 단독 시린지 펌프 배선 — 통신 · 전원 · 종단 저항 · 로터리 스위치"),(D(s,4),"SY-01C 외형 (제조사 자료)")])},
 {"h":"용도 (Applications)","html":"<p>미량 정량이 필요한 분석·진단 장비에 넣어 씁니다.</p><ul><li>자동 피펫팅 · 희석 · 분주</li><li>체외진단(IVD) 분석기</li><li>환경 모니터링 시스템</li><li>실험실 자동화 장비</li></ul>"}],
"faq":[
 {"tag":"사양","q":"SY-01C의 정격 스트로크와 분해능은?","a":"정격 스트로크 30 mm에 표준 3000 스텝이고 스텝당 0.0025 mm입니다."},
 {"tag":"속도","q":"최대 속도는 얼마인가요?","a":"450 rpm이며 선속도로는 0.0333~15 mm/s입니다. 정격 스트로크 한 번에 2초에서 900초까지 걸리도록 설정합니다."},
 {"tag":"시린지","q":"어떤 시린지를 쓰나요?","a":"ILS 시린지 25 µL, 50 µL, 125 µL, 250 µL, 500 µL, 1.25 mL, 2.5 mL, 5 mL 중에서 고릅니다."},
 {"tag":"밸브","q":"밸브는 어떤 것을 붙일 수 있나요?","a":"M01부터 M12까지 여덟 가지 분배 밸브를 붙일 수 있습니다. 유로 논리가 Y·T·분배·라디오·바이패스로 나뉩니다."},
 {"tag":"제어","q":"몇 대까지 같이 제어하나요?","a":"RS485 또는 CAN으로 최대 15대까지 개별 주소를 할당해 제어합니다."},
 {"tag":"설치","q":"크기와 설치 방법은?","a":"142.7 × 127 × 45 mm, 1.5 kg입니다. 상부 2-M3, 하부 M3, 측면 4-M3 마운팅 홀이 있어 세워서도 눕혀서도 고정할 수 있습니다."},
 {"tag":"압력","q":"최대 압력 정격은?","a":"제조사 사양표에 이 항목이 비어 있습니다. 압력 조건이 중요한 용도라면 SY-01B(0.7 MPa)나 SY-06B(0.7 MPa)로 검토하는 편이 안전합니다."}],
"ld":{"name":"Runze Fluid 고정밀 시린지 펌프 SY-01C","sku":"SY-01C","category":"시린지 펌프 · 밸브 일체형 모듈",
 "description":"정격 스트로크 30 mm(3000 스텝) 밸브 일체형 마이크로 시린지 펌프. 분해능 0.0025 mm, 최대 450 rpm, 시린지 25 µL~5 mL, M01~M12 밸브, RS232/RS485/CAN 최대 15대.",
 "models":["SY-01C"],"count":8},
"source":SRCU("high-precision-syringe-pump")})

# ---------------- SY-01B ----------------
s="multi-channel-syringe-pump"
P.append({
"slug":"multi-channel-syringe-pump","name":"멀티채널 시린지 펌프 SY-01B","name_en":"Runze Fluid Smart SY-01B Multi-Channel Syringe Pump",
"sub":"정격 스트로크 30 mm(12000 / 96000 스텝) · M01~M12 분배 밸브 · 0.7 MPa · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 밸브 일체형 모듈",
"title":"Runze Fluid 멀티채널 시린지 펌프 SY-01B — 마이크로스텝 96000 정밀 분주 모듈 | 실험셋업연구소",
"desc":"Runze Fluid Smart SY-01B 멀티채널 시린지 펌프 — 정격 스트로크 30 mm(표준 12000 스텝 · 마이크로스텝 96000 스텝), 최대 450 rpm, 최대 압력 0.7 MPa, 시린지 25 µL~5 mL, M01~M12 분배 밸브, 습부 붕규산 유리·PTFE·사파이어·PCTFE. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 멀티채널 시린지 펌프 SY-01B",
"answer":"Smart SY-01B는 정격 스트로크 30 mm를 마이크로스텝에서 96000 스텝까지 쪼개는 밸브 일체형 시린지 펌프로, 좁은 공간에 여러 대를 나란히 넣어 다채널 정량 분주 라인을 만드는 데 씁니다.",
"features":[
 "정격 스트로크 <b>30 mm</b> — 표준 12000 스텝, <b>마이크로스텝 모드 96000 스텝</b>",
 "최대 <b>450 rpm</b>, 선속도 0.0067 ~ 15 mm/s, 정격 스트로크 주행 2 s ~ 4500 s (매질 물)",
 "정확도 <b>≤1%</b>, 반복 정밀도 <b>0.3~0.5%</b>, 스텝당 분해능 0.0025 mm",
 "최대 압력 정격 <b>0.7 MPa</b>, 습부는 붕규산 유리 · PTFE · 사파이어 · PCTFE 입니다",
 "시린지 <b>"+ILS+"</b>, 분배 밸브 <b>M01~M12</b> 조합",
 "펌웨어에서 <b>가감속 곡선 · 백래시 보정 · 절대/상대 위치 · 주행 중 속도 변경 · 비휘발성 메모리</b> 를 프로그래밍합니다",
 "치수 <b>45 × 143.3 × 127 mm</b>, 1.5 kg — 설치 면적이 작아 여러 대를 나란히 배치하기 좋습니다",
 "제조사는 SY-01B·SY-03B 계열을 <b>30 mm 스트로크 업계 표준 규격</b> 의 기능 대체 모듈로 안내합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · 사파이어 · PCTFE"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.5% @100% 스트로크"],
 ["정격 스트로크 (Rated stroke)","30 mm · 12000 스텝 (마이크로스텝 96000 스텝)"],
 ["최대 속도 (Max speed)","450 rpm"],
 ["선속도 (Linear speed)","0.0067 ~ 15 mm/s (매질 물)"],
 ["주행 시간 (Running time)","2 s ~ 4500 s (정격 스트로크)"],
 ["분해능 (Resolution)","0.0025 mm / 스텝"],
 ["시린지 (Syringe)",ILS],
 ["밸브 모델 (Valve model)","M01 · M02 · M03 · M04 · M05 · M06 · M10 · M12"],
 ["최대 압력 (Max pressure)","0.7 MPa"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 1 mm / 2 mm"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)","RS232 / RS485 9600 · 38400 bps"],
 ["통신 주소 (Address)","개별 주소 최대 15개"],
 ["전원 (Power supply)","DC24V / 3A · 최대 25 W"],
 ["치수 L×W×H (Dimension)","45 × 143.3 × 127 mm"],
 ["순중량 (Net weight)","1.5 kg"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/high-precision-syringe-pump/">고정밀 시린지 펌프 SY-01C</a> · <a href="/brands/runze/syringe-pump-sy03b-in-dk-series/">시린지 펌프 SY-03B DK</a> · <a href="https://www.runzefluid.com/uploads/file/mart-sy-01b-syringe-pump.pdf" rel="nofollow">SY-01B 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/sy-01b-ascii-code-instruction-manuall-v1-1.pdf" rel="nofollow">SY-01B ASCII 통신 매뉴얼 V1.1 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=-G57RfCf2ws" rel="nofollow">SY-01B 제조사 소개 영상</a>'),
"keywords":KW+[["#멀티채널시린지펌프","/product/"],["#IVD분석기","/product/"],["#마이크로스텝","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-SY01B-30-M□□-□</b> 형태입니다. <b>30</b> 은 정격 스트로크 30 mm, <b>M□□</b> 는 분배 밸브 모델, 마지막 자리는 시린지 구성입니다.</p>"+figs([(D(s,0),"모델 번호 구성 — Model No. · Rated stroke 30 mm · Valve model · Syringe")])},
 {"h":"분배 밸브 유로 구성 (Valve options)","html":"<p>C 포트가 시린지에 연결되는 공통 포트입니다.</p>"+VALVE_UL+figs([(D(s,i),"밸브 모델별 유로 논리 (제조사 자료)") for i in range(2,len(META[s]["det"]))])},
 {"h":"펌웨어 기능 (Firmware)","html":"<ul><li>가감속 프로그래밍</li><li>동작 종료 명령</li><li>피스톤 속도 프로그래밍</li><li>에러 진단 조회</li><li>백래시 보정 프로그래밍</li><li>절대 위치 · 상대 위치 지정</li><li>주행 중 속도 변경</li><li>비휘발성 메모리 프로그래밍</li></ul>"},
 {"h":"용도 (Applications)","html":"<p>설치 공간이 좁은 자동 분석 장비에 여러 대를 넣어 다채널로 씁니다.</p><ul><li>체외진단(IVD) 분석기</li><li>환경 모니터링 시스템</li><li>유전자 시퀀서 (Genetic sequencers)</li><li>실험실 자동화 · 시약 정량 공급</li></ul>"}],
"faq":[
 {"tag":"차이","q":"SY-01B와 SY-01C는 뭐가 다른가요?","a":"둘 다 정격 스트로크 30 mm이지만 SY-01B가 표준 12000 스텝·마이크로스텝 96000 스텝으로 더 잘게 쪼개고 최대 압력 0.7 MPa가 명시돼 있습니다. SY-01C는 표준 3000 스텝이고 통신 속도 선택폭이 넓습니다."},
 {"tag":"정밀도","q":"마이크로스텝 모드는 무엇인가요?","a":"정격 스트로크 30 mm를 96000 스텝으로 나눠 구동하는 모드입니다. 표준 모드는 12000 스텝입니다."},
 {"tag":"압력","q":"압력 정격은 얼마인가요?","a":"최대 0.7 MPa입니다."},
 {"tag":"시린지","q":"시린지 용량은 어떻게 고르나요?","a":"ILS 시린지 25 µL부터 5 mL까지 여덟 가지 중에서 고릅니다. 필요한 최소 토출량과 1회 분주량을 함께 보고 정합니다."},
 {"tag":"제어","q":"통신 속도는 어떻게 되나요?","a":"RS232/RS485에서 9600 bps와 38400 bps입니다. 개별 주소는 최대 15개까지 할당합니다."},
 {"tag":"기능","q":"백래시 보정이 되나요?","a":"됩니다. 가감속 곡선, 절대/상대 위치, 주행 중 속도 변경, 비휘발성 메모리도 함께 프로그래밍할 수 있습니다."},
 {"tag":"설치","q":"여러 대를 나란히 넣을 수 있나요?","a":"치수가 45 × 143.3 × 127 mm로 폭이 좁아 여러 대를 붙여 배치하기 좋습니다. 무게는 1.5 kg입니다."}],
"ld":{"name":"Runze Fluid 멀티채널 시린지 펌프 SY-01B","sku":"SY-01B","category":"시린지 펌프 · 밸브 일체형 모듈",
 "description":"정격 스트로크 30 mm(12000/96000 스텝) 밸브 일체형 시린지 펌프. 최대 450 rpm, 0.7 MPa, 시린지 25 µL~5 mL, M01~M12 밸브, RS232/RS485/CAN.",
 "models":["SY-01B"],"count":8},
"source":SRCU("multi-channel-syringe-pump")})

add(P)
