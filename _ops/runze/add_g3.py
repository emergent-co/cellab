# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
P=[]
s="syringe-pump-sy03b-in-dk-series"
P.append({
"slug":"syringe-pump-sy03b-in-dk-series","name":"시린지 펌프 SY-03B DK 시리즈","name_en":"Runze Fluid Syringe Pump SY-03B DK Series",
"sub":"시린지 25 µL~5 mL · 솔레노이드 밸브 · 0.1~900 rpm · 마이크로스텝 48000 스텝 · RS232 / RS485",
"category":"시린지 펌프 · 다채널 모듈",
"title":"Runze Fluid 시린지 펌프 SY-03B DK 시리즈 — 병렬 마이크로 시린지 펌프 | 실험셋업연구소",
"desc":"Runze Fluid 시린지 펌프 SY-03B DK — 시린지 여러 개를 병렬 구동하는 마이크로 시린지 펌프. 25 µL~5 mL, 정격 스트로크 60 mm(6000/48000 스텝), 0.1~900 rpm, 습부 붕규산 유리·PTFE·FKM·PEEK(PPS), 0.2 MPa, RS232/RS485. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 시린지 펌프 SY-03B DK 시리즈",
"answer":"SY-03B DK 시리즈는 시린지 여러 개를 고정밀 병렬 구동하는 마이크로 시린지 펌프로, 스텝모터가 시린지와 밸브를 함께 움직여 정량 흡입·분주하며 시린지는 교체할 수 있습니다.",
"features":[
 "시린지 <b>25 µL ~ 5 mL</b> (25 · 50 · 100 · 250 · 500 µL · 1 · 1.25 · 2.5 · 5 mL) — 교체형입니다",
 "플런저 속도 <b>0.1 ~ 900 rpm</b>, 선속도 0.01 ~ 100 mm/s, 정격 스트로크 주행 1.8 s ~ 6000 s",
 "정격 스트로크 <b>60 mm</b> — 표준 6000 스텝, 마이크로스텝 모드 48000 스텝, 분해능 0.01 mm/스텝",
 "<b>가감속 곡선 · 백래시 보정 · 탈조 검출</b> 을 프로그래밍할 수 있고 오프라인 자동 운전과 에러 진단을 지원합니다",
 "습부는 <b>붕규산 유리 · PTFE · FKM · PEEK(PPS)</b>, 최대 압력 0.2 MPa",
 "구동부는 <b>사다리꼴 나사(리드 6 mm)</b>, 밸브는 솔레노이드 밸브입니다",
 "<b>RS232 / RS485</b> — 최대 15개 주소를 개별 할당해 여러 대를 병렬 제어합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · FKM · PEEK (PPS)"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.5% @100% 스트로크"],
 ["정격 스트로크 (Rated stroke)","60 mm · 6000 스텝 (마이크로스텝 48000 스텝)"],
 ["회전수 범위 (RPM range)","0.1 ~ 900 rpm"],
 ["선속도 (Linear speed)","0.01 ~ 100 mm/s (매질 물)"],
 ["주행 시간 (Running time)","1.8 s ~ 6000 s (정격 스트로크)"],
 ["분해능 (Resolution)","0.01 mm / 스텝"],
 ["밸브 형식 (Valve type)","솔레노이드 밸브 (Solenoid valve)"],
 ["시린지 (Syringe)","25 · 50 · 100 · 250 · 500 µL · 1 · 1.25 · 2.5 · 5 mL"],
 ["최대 압력 (Max pressure)","0.2 MPa"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 6 mm"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)","RS232 / RS485 9600 · 38400 bps"],
 ["통신 주소 (Address)","개별 주소 최대 15개"],
 ["전원 (Power supply)","DC24V / 3A · 최대 18 W"],
 ["치수 L×W×H (Dimension)","65 × 150 × 261.3 mm"],
 ["순중량 (Net weight)","2.2 kg"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/8-channel-micro-syringe-pump-module/">8채널 마이크로 시린지 펌프 SY-03B T-DK</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="https://www.runzefluid.com/uploads/file/sy-03b-syringe-pump.pdf" rel="nofollow">SY-03B 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/sy-03b-ascii-code-instruction-manuall.pdf" rel="nofollow">SY-03B ASCII 통신 매뉴얼 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=SirjQFUbf0I" rel="nofollow">SY-03B 제조사 소개 영상</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#병렬분주","/product/"],["#프로그래머블펌프","/product/"]],
"sections":[
 {"h":"펌웨어 기능 (Firmware)","html":"<ul><li>가감속 프로그래밍 (Programmable acceleration / deceleration)</li><li>동작 종료 명령 (Termination of movement)</li><li>플런저 속도 프로그래밍</li><li>에러 진단 조회 (Diagnostic query error)</li><li>백래시 보정 프로그래밍 (Clearance compensation)</li><li>절대 위치 · 상대 위치 지정</li><li>주행 중 속도 변경 (Change speed on the fly)</li><li>비휘발성 메모리 프로그래밍</li></ul>"},
 {"h":"배선 구성 (Wiring diagram)","html":"<p>여러 대를 병렬 제어할 때는 <b>RS485</b> 로 데이지체인하고 각 펌프에 DC24V를 공급합니다. 한 대만 쓸 때는 <b>RS232 또는 RS485</b> 를 씁니다.</p>"
  +figs([(D(s,0),"병렬 제어 배선과 단독 제어 배선 — RS485 다중 연결 / RS232·RS485 단독 연결")])},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,1),"SY-03B DK 외형 치수 도면")])},
 {"h":"용도 (Applications)","html":"<p>마이크로리터~밀리리터 구간의 자동 피펫팅·희석·분주에 씁니다.</p><ul><li>실험실 자동 전처리 장비</li><li>체외진단·의료 분석 장비</li><li>분석기기 시약 정량 공급</li></ul>"}],
"faq":[
 {"tag":"차이","q":"SY-03B DK와 SY-03B T-DK는 뭐가 다른가요?","a":"T-DK가 8채널로 고정된 완성 모듈이고, DK 시리즈는 시린지를 병렬로 묶는 기본 라인입니다. DK 쪽은 시린지 25 µL부터 쓸 수 있고 최대 압력이 0.2 MPa로 조금 더 높습니다."},
 {"tag":"속도","q":"플런저 속도 범위는 어떻게 되나요?","a":"0.1 rpm에서 900 rpm까지이고 선속도로는 0.01~100 mm/s입니다. 정격 스트로크 한 번 주행에 1.8초에서 6000초까지 설정됩니다."},
 {"tag":"제어","q":"몇 대까지 한 버스에 물릴 수 있나요?","a":"개별 주소를 최대 15개까지 할당할 수 있습니다. RS485로 데이지체인해 병렬 제어합니다."},
 {"tag":"기능","q":"백래시 보정이 되나요?","a":"백래시 보정을 프로그래밍할 수 있고 탈조 검출, 가감속 곡선, 주행 중 속도 변경, 에러 진단도 지원합니다."},
 {"tag":"소모품","q":"시린지는 교체할 수 있나요?","a":"교체할 수 있습니다. 25 µL부터 5 mL까지 아홉 가지 용량 중에서 고릅니다."}],
"ld":{"name":"Runze Fluid 시린지 펌프 SY-03B DK 시리즈","sku":"SY-03B-DK","category":"시린지 펌프 · 다채널 모듈",
 "description":"시린지 병렬 구동 마이크로 시린지 펌프. 25 µL~5 mL 교체형, 정격 스트로크 60 mm(6000/48000 스텝), 0.1~900 rpm, 습부 붕규산 유리·PTFE·FKM·PEEK, 0.2 MPa, RS232/RS485.",
 "models":["SY-03B-DK"],"count":1},
"source":SRCU("syringe-pump-sy03b-in-dk-series")})
add(P)
