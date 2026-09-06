# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]

# ---- RZ35 head ----
s="rz35-industrial-high-flow-pump-head"
P.append({
"slug":"rz35-industrial-high-flow-pump-head","name":"산업용 대유량 펌프헤드 RZ35","name_en":"Runze Fluid RZ35-3H-U Industrial High Flow Pump Head",
"sub":"PSU 하우징 · 304 스테인리스 3롤러 · 100-900 rpm · 73# / 82# 튜브 · 0.2 MPa · 1.74 kg",
"category":"연동펌프 · 펌프헤드",
"title":"Runze Fluid 산업용 대유량 펌프헤드 RZ35 — 73#·82# 튜브 스테인리스 3롤러 | 실험셋업연구소",
"desc":"Runze Fluid RZ35-3H-U 산업용 대유량 펌프헤드 — PSU 하우징, 304 스테인리스 3롤러, 100~900 rpm, 73# / 82# 고무·실리콘 튜브, 튜브 수압 0.2 MPa, 1.74 kg. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 산업용 대유량 펌프헤드 RZ35",
"answer":"RZ35-3H-U는 PSU 하우징에 304 스테인리스 롤러 3개를 넣은 산업용 대유량 펌프헤드로, 73#·82# 굵은 튜브를 물려 100~900 rpm 구간에서 대유량을 뽑습니다.",
"features":[
 "하우징 <b>PSU</b>, 롤러 <b>304 스테인리스 3롤러</b> — 산업 현장 조건을 견딥니다",
 "회전수 <b>100 ~ 900 rpm</b>",
 "적용 튜브 <b>73# · 82#</b> 고무 튜브 또는 실리콘 튜브",
 "튜브 수압 <b>0.2 MPa</b>",
 "중량 <b>1.74 kg</b> — LM80C 등 대유량 구동부에 물려 씁니다"],
"specs":[
 ["유량 범위 (Flow rate)","73# / 82# 튜브 · 100-900 rpm 구간 (구동부 구성에 따름)"],
 ["모델 (Model No.)","RZ35-3H-U"],
 ["하우징 재질 (Housing)","PSU"],
 ["롤러 재질 (Roller)","304 스테인리스 (304 SST)"],
 ["롤러 수 (Rollers)","3롤러"],
 ["회전수 (Speed)","100 ~ 900 rpm"],
 ["적용 튜브 (Pump tube)","73# · 82# 고무 튜브 / 실리콘 튜브"],
 ["튜브 수압 (Water pressure)","0.2 MPa"],
 ["중량 (Weight)","1.74 kg"]],
"variants":{"heading":"적용 연동펌프 튜브 (Peristaltic tubing)","head":["재질 (Material)","특성 (Features)","수명 (Service life)"],
 "rows":[["실리콘 (Silicone)","식품 등급 · 유연성 높음 · 사용 온도 −4℃ ~ +180℃ · 비부식성 액체용","≥200 h"],
  ["PharMed BPT","Saint-Gobain · FDA 규격 · 사용 온도 −51℃ ~ +132℃ · 약산·약염기 대응","≥1000 h"]],
 "note":"튜브 수명은 상온 20℃·무가압 조건에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 매질·회전수·사용 환경에 따라 달라지며 회전수가 낮고 액성이 순할수록 길어집니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/lm80c-intelligent-large-flow-peristaltic-pump/">LM80C 대유량 연동펌프</a> · <a href="/brands/runze/ts600-industrial-high-flow-peristaltic-pump/">TS600 산업용 대유량 연동펌프</a>'),
"keywords":PKW+[["#대유량펌프헤드","/product/"],["#산업용펌프헤드","/product/"]],
"sections":[
 {"h":"외형 치수 · 장착 순서 (Dimension & installation)","html":figs([(D(s,3),"RZ35 외형 치수 도면"),(D(s,4),"펌프헤드 장착 순서")])},
 {"h":"참고 유량 (Flow rate)","html":figs([(D(s,2),"73# · 82# 튜브 참고 유량표")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"RZ35 펌프헤드 (제조사 자료)") for i in range(2)])}],
"faq":[
 {"tag":"튜브","q":"RZ35는 어떤 튜브를 쓰나요?","a":"73#과 82# 고무 튜브 또는 실리콘 튜브입니다. 굵은 튜브를 쓰는 대유량 헤드입니다."},
 {"tag":"재질","q":"롤러 재질이 스테인리스인 이유는?","a":"304 스테인리스라 굵은 튜브를 누르는 하중과 산업 현장의 사용 조건을 견디기 위해서입니다. 하우징은 PSU입니다."},
 {"tag":"속도","q":"회전수 범위는 어떻게 되나요?","a":"100~900 rpm입니다."},
 {"tag":"압력","q":"압력은 얼마까지 되나요?","a":"튜브 수압 기준 0.2 MPa입니다."},
 {"tag":"구성","q":"모터가 포함되나요?","a":"펌프헤드 단품입니다. LM80C 같은 대유량 구동부에 물려 씁니다."}],
"ld":{"name":"Runze Fluid 산업용 대유량 펌프헤드 RZ35","sku":"RZ35-3H-U","category":"연동펌프 · 펌프헤드",
 "description":"PSU 하우징 · 304 스테인리스 3롤러 산업용 대유량 펌프헤드. 100~900 rpm, 73#/82# 튜브, 튜브 수압 0.2 MPa, 1.74 kg.",
 "models":["RZ35-3H-U"],"count":1},
"source":SRCU("rz35-industrial-high-flow-pump-head")})

# ---- TS600 ----
s="ts600-industrial-high-flow-peristaltic-pump"
P.append({
"slug":"ts600-industrial-high-flow-peristaltic-pump","name":"산업용 대유량 연동펌프 TS600","name_en":"Runze Fluid TS600 Industrial High Flow Peristaltic Pump",
"sub":"최대 14.28 L/min · 73# / 82# 튜브 · PSU 하우징·스테인리스 로터 · 86 스텝모터 · ≤900 rpm",
"category":"연동펌프 · 산업용 대유량",
"title":"Runze Fluid 산업용 대유량 연동펌프 TS600 — 최대 14.28 L/min 일체형 | 실험셋업연구소",
"desc":"Runze Fluid TS600 산업용 대유량 연동펌프 — 최대 유량 14.28 L/min, 73# / 82# 튜브, PSU 하우징·스테인리스 3롤러, 86 스텝모터(홀딩 토크 8.5 N·m), 회전수 900 rpm 이하, 튜브 출구압 0.2 MPa, 8.75 kg. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 산업용 대유량 연동펌프 TS600",
"answer":"TS600은 73#·82# 굵은 튜브로 최대 14.28 L/min을 내는 일체형 산업용 연동펌프로, 86 스텝모터와 전용 컨트롤러로 속도·이송량·지연·반복 횟수를 설정해 화학 원료와 식품 원료 이송에 씁니다.",
"features":[
 "최대 유량 <b>14.28 L/min</b> (매질 청수 기준) — 73# · 82# 튜브 적용",
 "펌프헤드 <b>PSU 하우징 + 스테인리스 로터 3개</b>",
 "구동 <b>86 스텝모터</b> — 스텝 각도 1.8°, 홀딩 토크 8.5 N·m, 절연 100 MΩ MIN(500 VDC), 사용 온도 −20℃ ~ +50℃",
 "회전수 <b>900 rpm 이하</b>, 구동 토크 1.61 N·m, 튜브 출구압 0.2 MPa",
 "<b>산업용 모터 컨트롤러</b> — 속도 · 이송 거리 · 지연 · 반복 횟수를 엔코더 노브로 설정하고 정·역 표시등으로 상태를 봅니다",
 "저소음 · 고안정 · 긴 수명을 겨냥한 정밀 가공 일체형 구조, 중량 8.75 kg"],
"specs":[
 ["유량 범위 (Flow rate)","최대 14.28 L/min (매질 청수)"],
 ["모델 (Product name)","TS600"],
 ["적용 튜브 (Tube)","73# · 82#"],
 ["롤러 (Roller)","스테인리스 3롤러"],
 ["펌프헤드 (Pump head)","PSU 하우징 · 스테인리스 로터"],
 ["회전수 (Speed range)","≤900 rpm"],
 ["구동 토크 (Driver torque)","1.61 N·m"],
 ["튜브 출구압 (Outlet pressure)","0.2 MPa"],
 ["모터 (Motor)","86 스텝모터 · 스텝 각도 1.8° · 홀딩 토크 8.5 N·m"],
 ["절연 (Insulation)","100 MΩ MIN · 500 VDC"],
 ["사용 온도 (Ambient temp)","−20℃ ~ +50℃"],
 ["중량 (Weight)","8.75 kg"]],
"buybox":[],
"related":PREL(' · <a href="/brands/runze/lm80c-intelligent-large-flow-peristaltic-pump/">LM80C 대유량 연동펌프</a> · <a href="/brands/runze/rz35-industrial-high-flow-pump-head/">RZ35 대유량 펌프헤드</a> · <a href="https://www.youtube.com/watch?v=aCdpuqbwrs8" rel="nofollow">TS600 제조사 소개 영상</a>'),
"keywords":PKW+[["#대유량연동펌프","/product/"],["#산업용연동펌프","/product/"],["#원료이송","/product/"]],
"sections":[
 {"h":"모터 · 컨트롤러 (Motor & controller)","html":"<p>구동은 <b>86 스텝모터</b> 입니다. 스텝 각도 1.8°, 홀딩 토크 8.5 N·m, 절연 100 MΩ MIN(500 VDC), 사용 온도 −20℃ ~ +50℃ 입니다.</p>"
  "<p>산업용 모터 컨트롤러로 <b>속도 · 이송 거리 · 지연 시간 · 반복 횟수</b> 를 설정합니다. 정회전·역회전 표시등과 엔코더 설정 노브가 있습니다.</p>"
  +figs([(D(s,3),"86 스텝모터 사양과 모터 인터페이스 배선 정의"),(D(s,4),"산업용 모터 컨트롤러 — 속도·거리·지연·반복 횟수 설정")])},
 {"h":"성능 · 구조 (Performance & structure)","html":figs([(D(s,1),"최대 유량 14.28 L/min · 73#·82# 튜브 적용 · 대표 적용 분야"),(D(s,2),"정밀 가공 일체형 구조 — PSU 하우징 · 스테인리스 로터")])},
 {"h":"용도 (Applications)","html":"<ul><li>화학 원료 이송 (Chemical raw material transportation)</li><li>반응기 투입 (Reactor feeding)</li><li>식품 원료 이송 (Food raw material transportation)</li></ul>"},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"TS600 (제조사 자료)") for i in [0,5,6,7,8]])}],
"faq":[
 {"tag":"유량","q":"TS600은 유량이 얼마나 나오나요?","a":"최대 14.28 L/min입니다. 청수를 매질로 잰 값이고 73#·82# 튜브를 씁니다."},
 {"tag":"튜브","q":"어떤 튜브를 쓰나요?","a":"73#과 82# 굵은 튜브입니다. RZ35 헤드와 같은 계열의 튜브 규격입니다."},
 {"tag":"모터","q":"모터 사양은 어떻게 되나요?","a":"86 스텝모터로 스텝 각도 1.8°, 홀딩 토크 8.5 N·m입니다. 구동 토크는 1.61 N·m이고 회전수는 900 rpm 이하입니다."},
 {"tag":"제어","q":"어떤 항목을 설정할 수 있나요?","a":"속도, 이송 거리, 지연 시간, 반복 횟수를 컨트롤러 엔코더로 설정합니다. 정·역 회전은 표시등으로 확인합니다."},
 {"tag":"압력","q":"압력은 얼마까지 되나요?","a":"튜브 출구압 기준 0.2 MPa입니다."},
 {"tag":"차이","q":"LM80C와 TS600 중 어느 쪽을 골라야 하나요?","a":"LM80C는 연속·정량·예약·교정 4모드와 RS232/RS485 통신이 들어간 지능형 제어형이고, TS600은 컨트롤러로 속도·거리·지연·반복을 설정하는 이송 중심 구성입니다. 통신 연동이 필요하면 LM80C, 단순 대유량 이송이면 TS600입니다."}],
"ld":{"name":"Runze Fluid 산업용 대유량 연동펌프 TS600","sku":"TS600","category":"연동펌프 · 산업용 대유량",
 "description":"최대 14.28 L/min 산업용 대유량 연동펌프. 73#/82# 튜브, PSU 하우징·스테인리스 3롤러, 86 스텝모터(홀딩 토크 8.5 N·m), ≤900 rpm, 튜브 출구압 0.2 MPa, 8.75 kg.",
 "models":["TS600"],"count":1},
"source":SRCU("ts600-industrial-high-flow-peristaltic-pump")})
add(P)
