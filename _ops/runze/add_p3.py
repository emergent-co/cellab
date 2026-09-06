# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]

# ---- LM40B ----
s="lm40b-micro-peristaltic-pump"
P.append({
"slug":"lm40b-micro-peristaltic-pump","name":"지능형 충전 연동펌프 LM40B","name_en":"Runze Fluid LM40B Intelligent Filling Peristaltic Pump",
"sub":"0.1-400 rpm · ±0.1 rpm · 0.03-152 mL/min · 헤드 4종 선택 · 풋스위치 · RS485 · 전류/전압 제어",
"category":"연동펌프 · 컨트롤러 일체형",
"title":"Runze Fluid 지능형 충전 연동펌프 LM40B — 헤드 4종 선택 정량 충전 펌프 | 실험셋업연구소",
"desc":"Runze Fluid LM40B 지능형 충전 연동펌프 — 0.1~400 rpm, 속도 정밀도 ±0.1 rpm, 유량 0.03~152 mL/min, 펌프헤드 RZ1030-4 / RZ1030B / RZ-01 / RZ-02 선택, 키패드·풋스위치·RS485·전류/전압 제어, DC24V, IP31. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 지능형 충전 연동펌프 LM40B",
"answer":"LM40B는 병 충전과 반복 분주를 겨냥한 지능형 연동펌프로, 펌프헤드를 네 가지 중에서 고르고 키패드·풋스위치·RS485·전류/전압 네 가지 방식으로 운전하며 속도를 ±0.1 rpm 으로 맞춥니다.",
"features":[
 "펌프헤드 <b>RZ1030-4 · RZ1030B · RZ-01 · RZ-02</b> 네 가지 중에서 고릅니다",
 "속도 <b>0.1 ~ 400 rpm</b>, 속도 정밀도 <b>±0.1 rpm</b> — 모터 세분화가 자동으로 맞춰집니다",
 "유량 <b>0.03 ~ 152 mL/min</b> (헤드와 튜브에 따라)",
 "<b>병 충전과 무한 반복(무한 루프)</b> 을 통신 제어 모드에서 지원합니다",
 "키패드 패널과 <b>로터리 엔코더</b> 로 속도를 조절하고, 독립 LED로 정·역 회전 · 풋스위치 상태 · 모터 구동 · 외부 제어 유효 여부를 표시합니다",
 "외부 제어 — <b>풋스위치 · RS485 · 전류/전압 제어</b>. 한 버튼으로 최고속(Fast speed) 전환",
 "하우징이 산화되지 않는 재질이고 중문·영문 표시를 지원합니다 — DC24V ±10% · 최대 20 W · IP31 · 0.9 kg(헤드 제외)"],
"specs":[
 ["유량 범위 (Flow rate)","0.03 ~ 152 mL/min"],
 ["모델 (Product name)","LM40B 시리즈 지능형 연동펌프"],
 ["적용 펌프헤드 (Pump head)","RZ1030-4 · RZ1030B · RZ-01 · RZ-02"],
 ["모터 (Motor type)","일본 수입 스텝모터"],
 ["속도 범위 (Speed range)","0.1 ~ 400 rpm"],
 ["속도 정밀도 (Speed accuracy)","±0.1 rpm"],
 ["롤러 재질 (Roller material)","POM / PPS"],
 ["표시 언어 (Language)","중문 / 영문"],
 ["외부 제어 (External control)","풋스위치 · RS485 · 전류/전압 제어"],
 ["풋스위치 입력 (Foot pedal)","시동·정지 (키패드 제어 모드 전용)"],
 ["속도 신호 입력 (Speed signal)","다중 스위칭 제어 입력 (외부 제어 모드 전용)"],
 ["방향 신호 입력 (Steering)","방향 전환 입력 (외부 제어 · 풋스위치 모드 전용)"],
 ["기동 신호 입력 (Start signal)","기동·정지 스위치 입력 (외부 제어 모드 전용)"],
 ["최고속 (Fast speed)","한 버튼 전환"],
 ["전원 (Power supply)","DC24V ±10% · 최대 20 W"],
 ["사용 환경 (Environment)","0 ~ 40℃ · 상대습도 80% 미만"],
 ["보호 등급 (Protection)","IP31"],
 ["치수 L×W×H (Dimension)","180.1 × 107.4 × 101.5 mm"],
 ["순중량 (Net weight)","0.9 kg (펌프헤드 제외)"]],
"variants":{"heading":"펌프헤드·튜브별 최대 유량 (mL/min)","head":["펌프헤드 · 롤러","튜브 두께","튜브 내경 (mm)","최대 유량"],
 "rows":[["RZ1030 / RZ1030B · 4롤러","0.8 mm","0.64 / 1.02 / 1.42 / 1.85 / 2.29 / 2.79","12 / 25 / 47 / 70 / 94 / 128"],
  ["RZ-01 · 4롤러","0.8 mm","0.64 / 1.02 / 1.42 / 1.85 / 2.29 / 2.79","12 / 22 / 42 / 60 / 88 / 96"],
  ["RZ-01 · 4롤러","1.6 mm","1.6 / 2.4 / 3.2","48 / 94 / 152"],
  ["RZ-02 · 3 / 6롤러","0.8 mm","−","0.054 ~ 142.564"],
  ["RZ-02 · 3 / 6롤러","1.6 mm","−","0.029 ~ 135.878"]],
 "note":"RZ1030 / RZ1030B 4롤러 0.8 mm 두께 전체 계열은 내경 0.64 · 0.76 · 0.89 · 1.02 · 1.14 · 1.30 · 1.42 · 1.52 · 1.65 · 1.85 · 2.06 · 2.29 · 2.54 · 2.79 mm 에서 각각 12 · 15 · 18 · 25 · 32 · 38 · 47 · 50 · 56 · 70 · 87 · 94 · 113 · 128 mL/min, RZ-01 은 12 · 13 · 16 · 22 · 28 · 34 · 42 · 44 · 47 · 60 · 65 · 88 · 90 · 96 mL/min 입니다. 상온 무가압 순수 기준 참고값입니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/micro-peristaltic-pump/">마이크로 연동펌프 LM40A</a> · <a href="/brands/runze/lm80c-intelligent-large-flow-peristaltic-pump/">LM80C 대유량 연동펌프</a> · <a href="/brands/runze/db15-rs485-communication-cable/">DB15-RS485 통신 케이블</a> · <a href="https://www.runzefluid.com/uploads/file/lm40b-intelligent-filling-peristaltic-pump-instruction-manual.pdf" rel="nofollow">LM40B 매뉴얼 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=PCOKnWJnyKw" rel="nofollow">LM40B 제조사 소개 영상</a>'),
"keywords":PKW+[["#충전펌프","/product/"],["#정량분주","/product/"],["#RS485제어","/product/"]],
"sections":[
 {"h":"펌프헤드 4종 비교 (Pump head)","html":"<ul>"
  "<li><b>LM40B-RZ1030</b> — 하우징/롤러 ABS / POM. 구조 성능이 좋고 ABS 라 내식성이 있으며 튜브 교체가 쉽습니다.</li>"
  "<li><b>LM40B-RZ1030B</b> — 하우징/롤러 PPS / PPS. PPS 라 내식·내마모가 더 좋고 튜브 교체가 쉽습니다.</li>"
  "<li><b>LM40B-RZ-01</b> — 하우징/롤러 PC / PPS. 가격 대비 성능이 좋고 크기가 작습니다. 투명 하우징이라 튜브 상태를 눈으로 확인할 수 있고, 슬롯 설계로 바브-암나사 어댑터를 붙이기 쉽습니다.</li>"
  "<li><b>LM40B-RZ-02</b> — 하우징/롤러 PPS / PPS. 가격 경쟁력이 있고 스프링 클램프 구조라 튜브 장착이 더 쉽습니다.</li></ul>"
  +figs([(D(s,1),"펌프헤드 4종 — LM40B-RZ1030 / RZ1030B / RZ-01 / RZ-02 재질과 특징")])},
 {"h":"제어 방식 · 부속 (Control mode & accessories)","html":"<ol>"
  "<li><b>패널 제어</b> — 펌프 단독</li>"
  "<li><b>통신 제어</b> — 펌프 + DB15-RS485 통신 케이블 + USB 시리얼 변환기</li>"
  "<li><b>풋스위치 제어</b> — 펌프 + 풋 페달</li>"
  "<li><b>전류/전압 제어</b> — 펌프 + 전압/전류 제어 입력</li></ol>"
  +figs([(D(s,5),"제어 방식 네 가지와 필요한 부속 구성")])},
 {"h":"적용 튜브 · 참고 유량 (Tubing & flow rate)","html":figs([(D(s,4),"펌프헤드별 적용 튜브 규격과 참고 유량표")])},
 {"h":"외형 치수 · 제품 사진","html":figs([(D(s,i),"LM40B 외형 · 치수 (제조사 자료)") for i in [2,3,0,6]])}],
"faq":[
 {"tag":"헤드","q":"펌프헤드는 어떤 기준으로 고르나요?","a":"내식성이 중요하면 PPS 하우징인 RZ1030B나 RZ-02, 튜브 상태를 눈으로 봐야 하면 투명 하우징인 RZ-01, 큰 유량이 필요하면 1.6 mm 두께 튜브를 쓰는 RZ-01(최대 152 mL/min)을 고릅니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"헤드와 튜브에 따라 0.03~152 mL/min입니다. RZ-01에 두께 1.6 mm·내경 3.2 mm 튜브를 쓸 때가 152 mL/min으로 가장 큽니다."},
 {"tag":"제어","q":"제어 방식은 몇 가지인가요?","a":"패널(키패드) 제어, RS485 통신 제어, 풋스위치 제어, 전류/전압 제어 네 가지입니다. 통신 제어에는 DB15-RS485 케이블과 USB 시리얼 변환기가 필요합니다."},
 {"tag":"충전","q":"병 충전 반복이 되나요?","a":"통신 제어 모드에서 병 충전과 무한 반복 루프를 지원합니다."},
 {"tag":"정밀도","q":"속도 정밀도는 얼마인가요?","a":"±0.1 rpm입니다. 모터 세분화가 자동으로 맞춰집니다."},
 {"tag":"표시","q":"운전 상태를 어떻게 확인하나요?","a":"독립 LED로 정·역 회전, 풋스위치 상태, 모터 구동 여부, 외부 제어 인터페이스 유효 여부를 표시합니다."},
 {"tag":"차이","q":"LM40A와 LM40B는 뭐가 다른가요?","a":"LM40B가 펌프헤드 선택폭이 넓고(4종) 전류/전압 제어와 최고속 원터치 버튼, 로터리 엔코더 조작이 추가됐습니다. 유량 상한도 117 mL/min에서 152 mL/min로 늘었습니다."}],
"ld":{"name":"Runze Fluid 지능형 충전 연동펌프 LM40B","sku":"LM40B","category":"연동펌프 · 컨트롤러 일체형",
 "description":"지능형 충전 연동펌프. 0.1~400 rpm, ±0.1 rpm, 0.03~152 mL/min, 펌프헤드 RZ1030-4/RZ1030B/RZ-01/RZ-02 선택, 키패드·풋스위치·RS485·전류전압 제어, DC24V, IP31.",
 "models":["LM40B-RZ1030","LM40B-RZ1030B","LM40B-RZ-01","LM40B-RZ-02"],"count":4},
"source":SRCU("lm40b-micro-peristaltic-pump")})

# ---- LM80C ----
s="lm80c-intelligent-large-flow-peristaltic-pump"
P.append({
"slug":"lm80c-intelligent-large-flow-peristaltic-pump","name":"산업용 대유량 연동펌프 LM80C","name_en":"Runze Fluid LM80C Intelligent Large Flow Peristaltic Pump",
"sub":"LM80C-RZ35-3H-U · 1-500 rpm · 스테인리스 바디·로터 · 연속/정량/예약/교정 4모드 · DC48V 144 W",
"category":"연동펌프 · 산업용 대유량",
"title":"Runze Fluid 산업용 대유량 연동펌프 LM80C — 4모드 정량 제어 일체형 | 실험셋업연구소",
"desc":"Runze Fluid LM80C 산업용 대유량 연동펌프 — LM80C-RZ35-3H-U, 1~500 rpm, 스테인리스 바디·로터, 연속·정량·예약·교정 4모드, RS232/RS485, DC48V ±10% · 144 W, 417.6×195.1×298.64 mm · 13 kg, IP3. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 산업용 대유량 연동펌프 LM80C",
"answer":"LM80C는 스테인리스 바디에 지능형 제어 패널을 붙인 일체형 산업용 대유량 연동펌프로, 연속·정량·예약·교정 네 가지 모드로 화학 원료와 식품 원료 이송, 반응기 투입 같은 작업을 처리합니다.",
"features":[
 "<b>연속 · 정량 · 예약 · 교정</b> 네 가지 운전 모드 — 패널 메뉴에서 고릅니다",
 "속도 <b>1 ~ 500 rpm</b>(펌프헤드와 튜브에 따라 최고 속도가 조금 달라집니다), 속도 정밀도 1 rpm",
 "<b>스테인리스 바디와 스테인리스 로터</b> — 산업 현장용 일체형 구조입니다",
 "<b>RS232 / RS485</b> 통신 제어",
 "전원 <b>DC48V ±10% · 144 W</b>, 치수 417.6 × 195.1 × 298.64 mm · 13 kg",
 "동작 환경 0 ~ 40℃ · 상대습도 80% 미만, 보호 등급 IP3",
 "화학 원료 이송 · 반응기 투입 · 식품 원료 이송 같은 산업 정량 이송에 씁니다"],
"specs":[
 ["유량 범위 (Flow rate)","펌프헤드·튜브 구성에 따름 (RZ35 대유량 헤드)"],
 ["모델 (Model No.)","LM80C-RZ35-3H-U"],
 ["속도 범위 (Speed range)","1 ~ 500 rpm"],
 ["속도 정밀도 (Speed accuracy)","1 rpm"],
 ["운전 모드 (Working mode)","연속 · 정량 · 예약 · 교정 (Continuous · Rationing · Booking · Calibration)"],
 ["통신 (Communication)","RS232 / RS485"],
 ["전원 (Power supply)","DC48V ±10%"],
 ["소비전력 (Power)","144 W"],
 ["동작 온도 (Operating temp)","0 ~ 40℃"],
 ["동작 습도 (Operating humidity)","80% 미만"],
 ["보호 등급 (Protection)","IP3"],
 ["치수 L×W×H (Dimension)","417.6 × 195.1 × 298.64 mm"],
 ["순중량 (Net weight)","13 kg"]],
"variants":{"heading":"운전 모드 (Working mode)","head":["모드","동작"],
 "rows":[["연속 (Continuous)","특별한 조건 없이 액체를 계속 이송합니다. 모터를 연속 운전하며 속도와 유량을 실시간으로 감시합니다."],
  ["정량 (Rationing)","지정한 부피만큼 한 번에 분주합니다. 시간·속도·액량을 정해 운전합니다."],
  ["예약 (Booking)","지정한 속도에서 지정 부피를 N회 반복 분주합니다."],
  ["교정 (Calibration)","다른 모드를 시작하기 전이나 펌프·튜브를 교체한 뒤 분주량과 유량의 정확도를 맞춥니다."]]},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/rz35-industrial-high-flow-pump-head/">RZ35 대유량 펌프헤드</a> · <a href="/brands/runze/ts600-industrial-high-flow-peristaltic-pump/">TS600 산업용 대유량 연동펌프</a> · <a href="https://www.youtube.com/watch?v=P_EA4ZvcpE8" rel="nofollow">LM80C 제조사 소개 영상</a>'),
"keywords":PKW+[["#대유량연동펌프","/product/"],["#산업용연동펌프","/product/"],["#정량충전","/product/"]],
"sections":[
 {"h":"4가지 운전 모드 (Four modes)","html":"<p>패널 메뉴에서 <b>Calibrate · Inquiry · Settings · Rationing · Booking · Flow</b> 항목을 다룹니다.</p>"
  +figs([(D(s,4),"4가지 운전 모드 — 연속 · 정량 · 예약 · 교정")])},
 {"h":"성능 파라미터 (Performance)","html":figs([(D(s,6),"제조사 성능 파라미터 — 모델·속도·모드·통신·전원·치수·중량·보호등급")])},
 {"h":"구조 (Structure)","html":"<p>스테인리스 바디와 스테인리스 로터에 지능형 제어 패널을 얹은 일체형 구조입니다.</p>"
  +figs([(D(s,3),"스테인리스 바디 · 스테인리스 로터 · 지능형 제어 패널 구성")])},
 {"h":"용도 (Applications)","html":"<ul><li>화학 원료 이송 (Chemical raw material transportation)</li><li>반응기 투입 (Reactor feeding)</li><li>식품 원료 이송 (Food raw material transportation)</li></ul>"
  +figs([(D(s,2),"대표 적용 — 화학 원료 이송 · 반응기 투입 · 식품 원료 이송")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"LM80C (제조사 자료)") for i in [0,1,5,7,8,9,10]])}],
"faq":[
 {"tag":"모드","q":"정량 모드와 예약 모드는 뭐가 다른가요?","a":"정량 모드는 지정한 부피를 한 번 분주하고, 예약 모드는 같은 부피를 정해진 횟수(N회)만큼 반복 분주합니다."},
 {"tag":"교정","q":"교정 모드는 언제 쓰나요?","a":"다른 모드를 시작하기 전이나 펌프·튜브를 교체한 뒤에 씁니다. 분주량과 유량의 정확도를 맞추는 절차입니다."},
 {"tag":"속도","q":"속도 범위는 어떻게 되나요?","a":"1~500 rpm입니다. 최고 속도는 펌프헤드와 튜브 조합에 따라 조금 달라집니다."},
 {"tag":"전원","q":"전원은 무엇인가요?","a":"DC48V ±10%이고 소비전력은 144 W입니다."},
 {"tag":"재질","q":"본체 재질은 무엇인가요?","a":"바디와 로터가 스테인리스입니다. 산업 현장에서 쓸 수 있게 만든 일체형 구조입니다."},
 {"tag":"통신","q":"상위 시스템과 연동되나요?","a":"RS232와 RS485를 지원합니다."},
 {"tag":"설치","q":"크기와 무게는?","a":"417.6 × 195.1 × 298.64 mm에 13 kg입니다. 보호 등급은 IP3입니다."}],
"ld":{"name":"Runze Fluid 산업용 대유량 연동펌프 LM80C","sku":"LM80C-RZ35-3H-U","category":"연동펌프 · 산업용 대유량",
 "description":"스테인리스 바디 산업용 대유량 연동펌프. 1~500 rpm, 연속·정량·예약·교정 4모드, RS232/RS485, DC48V 144 W, 13 kg, IP3.",
 "models":["LM80C-RZ35-3H-U"],"count":1},
"source":SRCU("lm80c-intelligent-large-flow-peristaltic-pump")})
add(P)
