# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
P=[]
s="syringe-pump-microfluidics"
P.append({
"slug":"syringe-pump-microfluidics","name":"미세유체 시린지 펌프 SY-03B","name_en":"Runze Fluid SY-03B Microfluidic Syringe Pump",
"sub":"정격 스트로크 60 mm(6000 / 48000 스텝) · 시린지 25 µL~25 mL · M01~M10 분배 밸브 · 0.7 MPa",
"category":"시린지 펌프 · 밸브 일체형 모듈",
"title":"Runze Fluid 미세유체 시린지 펌프 SY-03B — 25 µL~25 mL 프로그래머블 정량 모듈 | 실험셋업연구소",
"desc":"Runze Fluid SY-03B 미세유체 시린지 펌프 — 정격 스트로크 60 mm(표준 6000 · 마이크로스텝 48000), 0.1~600 rpm, 시린지 25 µL~25 mL, M01~M10 분배 밸브, 습부 붕규산 유리·PTFE·사파이어·PCTFE, 0.7 MPa, RS232/RS485. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 미세유체 시린지 펌프 SY-03B",
"answer":"SY-03B는 정격 스트로크 60 mm에 분배 밸브를 얹은 프로그래머블 시린지 펌프로, 25 µL부터 25 mL까지 시린지를 바꿔 끼우며 미세유체·자동 전처리 라인에서 정량 흡입과 분주를 수행합니다.",
"features":[
 "정격 스트로크 <b>60 mm</b> — 표준 6000 스텝, <b>마이크로스텝 모드 48000 스텝</b>, 분해능 0.01 mm/스텝",
 "회전수 <b>0.1 ~ 600 rpm</b>, 선속도 0.01 ~ 60 mm/s, 정격 스트로크 주행 1 s ~ 6000 s",
 "시린지 <b>25 · 50 · 100 · 250 · 500 µL · 1 · 2.5 · 5 · 10 · 25 mL</b> — Runze 계열에서 가장 넓은 용량 폭입니다",
 "분배 밸브 <b>M01 ~ M10</b> — Y · T · 분배 · 라디오 · 바이패스와 다포트 분배 유로를 고릅니다",
 "습부는 <b>붕규산 유리 · PTFE · 사파이어 · PCTFE</b>, 최대 압력 <b>0.7 MPa</b>",
 "펌웨어에서 <b>가감속 · 백래시 보정 · 절대/상대 위치 · 주행 중 속도 변경 · 비휘발성 메모리</b> 를 프로그래밍합니다",
 "<b>RS232 / RS485</b> 로 최대 15대 개별 주소 제어, 치수 65 × 145.5 × 253.3 mm · 2.2 kg"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PTFE · 사파이어 · PCTFE"],
 ["정확도 (Accuracy)","≤1% @100% 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.5% @100% 스트로크"],
 ["정격 스트로크 (Rated stroke)","60 mm · 6000 스텝 (마이크로스텝 48000 스텝)"],
 ["회전수 범위 (RPM range)","0.1 ~ 600 rpm"],
 ["선속도 (Linear speed)","0.01 ~ 60 mm/s (매질 물)"],
 ["주행 시간 (Running time)","1 s ~ 6000 s (정격 스트로크)"],
 ["분해능 (Resolution)","0.01 mm / 스텝"],
 ["시린지 (Syringe)","25 · 50 · 100 · 250 · 500 µL · 1 · 2.5 · 5 · 10 · 25 mL (ILS)"],
 ["밸브 모델 (Valve model)","M01 ~ M10"],
 ["최대 압력 (Max pressure)","0.7 MPa"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 6 mm / 1 mm"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)","RS232 / RS485 9600 · 38400 bps"],
 ["통신 주소 (Address)","개별 주소 최대 15개"],
 ["전원 (Power supply)","DC24V / 3A · 최대 35 W"],
 ["치수 L×W×H (Dimension)","65 × 145.5 × 253.3 mm"],
 ["순중량 (Net weight)","2.2 kg"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 미만 · 비결로"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/syringe-pump-sy03b-in-dk-series/">시린지 펌프 SY-03B DK</a> · <a href="/brands/runze/8-channel-micro-syringe-pump-module/">8채널 마이크로 시린지 펌프 SY-03B T-DK</a> · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="https://www.runzefluid.com/uploads/file/sy-03b-syringe-pump.pdf" rel="nofollow">SY-03B 카탈로그 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=CzMfAISYRlw" rel="nofollow">SY-03B 제조사 소개 영상</a>'),
"keywords":KW+[["#미세유체","/product/"],["#시린지펌프","/product/"],["#자동전처리","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-SY03B-60-M□□-□</b> 형태입니다. <b>60</b> 은 정격 스트로크 60 mm, <b>M□□</b> 는 분배 밸브 모델, 마지막 자리는 제어 스텝 수(6000 스텝, ASCII 코드)입니다.</p>"+figs([(D(s,0),"모델 번호 구성 — Model No. · Rated stroke 60 mm · Valve model · Control steps")])},
 {"h":"분배 밸브 유로 구성 (Valve options)","html":"<p>C 포트가 시린지에 연결되는 공통 포트입니다.</p><ul>"
  "<li><b>M01</b> — Y 유로 (C-1 / 1-2 / C-2 연동)</li>"
  "<li><b>M02</b> — T 유로 (C-1-2 / C-1 / 1-2 / C-2 연동)</li>"
  "<li><b>M03</b> — 분배 유로 (C-1 / C-2 / C-3 연동)</li>"
  "<li><b>M04</b> — 라디오 유로 (C-1 / 1-2 / 2-3 / C-3 연동)</li>"
  "<li><b>M05</b> — 바이패스 유로 (C-1 / 2-3 연동, C-3 / 1-2 연동)</li>"
  "<li><b>M06 ~ M10</b> — 다포트 분배 유로. 공통 포트가 6 · 8 · 10 · 12 · 15 포트 중 하나에 선택 연결되며, 모델별 포트 수는 제조사 밸브 옵션 도면 표기를 따릅니다</li></ul>"
  +figs([(D(s,1),"밸브 모델별 유로 논리 M01~M10")])},
 {"h":"적용 시린지 규격 (K60 syringe)","html":"<p>정격 스트로크 60 mm 규격의 K60 기밀 시린지를 씁니다. 50 µL 부터 50 mL 까지 <b>RZ-K60-□-W-1-U</b> 코드로 지정합니다.</p>"+figs([(D(s,2),"K60 시린지 용량별 치수 도면 — RZ-K60-50ML ~ RZ-K60-50ul")])},
 {"h":"외형 치수 (Dimension, unit: mm)","html":"<p>상부 6-M4, 하부 4-M3 마운팅 홀이 있습니다.</p>"+figs([(D(s,3),"SY-03B 외형 치수와 상·하부 마운팅 홀 배치")])},
 {"h":"용도 (Applications)","html":"<p>마이크로리터~밀리리터 구간을 프로그램으로 다루는 장비에 씁니다.</p><ul><li>미세유체(Microfluidics) 플랫폼</li><li>자동 피펫팅 · 희석 · 분주</li><li>실험실 자동 전처리 · 분석기기 시약 공급</li></ul>"}],
"faq":[
 {"tag":"용량","q":"SY-03B는 시린지를 어디까지 물릴 수 있나요?","a":"25 µL부터 25 mL까지 열 가지입니다. Runze 시린지 펌프 중에서 용량 폭이 가장 넓습니다."},
 {"tag":"정밀도","q":"마이크로스텝 모드는 몇 스텝인가요?","a":"정격 스트로크 60 mm를 표준 6000 스텝, 마이크로스텝 모드에서 48000 스텝으로 나눕니다. 스텝당 이동은 0.01 mm입니다."},
 {"tag":"밸브","q":"밸브는 몇 포트까지 되나요?","a":"M06부터 M10까지가 다포트 분배 유로이고 6·8·10·12·15 포트 구성이 있습니다. 모델별 포트 수는 제조사 밸브 옵션 도면 표기를 따릅니다."},
 {"tag":"압력","q":"압력 정격은 얼마인가요?","a":"최대 0.7 MPa입니다."},
 {"tag":"제어","q":"몇 대까지 같이 제어하나요?","a":"RS232/RS485로 개별 주소를 최대 15개까지 할당합니다. 통신 속도는 9600 bps와 38400 bps입니다."},
 {"tag":"소모품","q":"시린지 규격은 어떻게 지정하나요?","a":"정격 스트로크 60 mm용 K60 기밀 시린지를 쓰며 RZ-K60-용량-W-1-U 코드로 지정합니다."},
 {"tag":"설치","q":"크기와 무게는?","a":"65 × 145.5 × 253.3 mm, 2.2 kg입니다. 상부 6-M4, 하부 4-M3 마운팅 홀이 있습니다."}],
"ld":{"name":"Runze Fluid 미세유체 시린지 펌프 SY-03B","sku":"SY-03B","category":"시린지 펌프 · 밸브 일체형 모듈",
 "description":"정격 스트로크 60 mm(6000/48000 스텝) 프로그래머블 시린지 펌프. 시린지 25 µL~25 mL, M01~M10 분배 밸브, 습부 붕규산 유리·PTFE·사파이어·PCTFE, 0.7 MPa, RS232/RS485.",
 "models":["SY-03B"],"count":10},
"source":SRCU("syringe-pump-microfluidics")})
add(P)
