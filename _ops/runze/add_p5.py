# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]
YZFLOW={"heading":"튜브 규격별 유량 (mL/min · 5-400 rpm)","head":["튜브","YZ1515X 3롤러","YZ1515X 6롤러","SN15 3롤러","SN15 6롤러"],
 "rows":[["14# (1.6×1.6)","1.1 - 116.5","0.8 - 92.1","1.1 - 87.4","0.8 - 59.5"],
  ["16# (3.2×1.6)","4.0 - 421.3","3.0 - 334.8","4.3 - 358.3","3.2 - 220.8"],
  ["25# (4.8×1.6)","9.1 - 920.2","−","10.1 - 735.1","−"],
  ["17# (6.4×1.6)","15.6 - 1394.2","−","13.2 - 1171.3","−"],
  ["18# (8.0×1.6)","20.1 - 1627.2","−","−","−"]],
 "note":"상온 상압에서 순수를 이송해 잰 값이며 매질과 사용 환경에 따라 실제 유량은 달라집니다."}

# ---- BJ30 industrial ----
s="industrial-peristaltic-pump"
P.append({
"slug":"industrial-peristaltic-pump","name":"산업용 연동펌프 BJ30","name_en":"Runze Fluid BJ30 Industrial Peristaltic Pump",
"sub":"57 스텝모터(NEMA 23) · 0-400 rpm · 0-1700 mL/min · YZ1515X / YZ2515X / SN15 / SN25 헤드 · 3 bar",
"category":"연동펌프 · 스텝모터 일체형",
"title":"Runze Fluid 산업용 연동펌프 BJ30 — 최대 1700 mL/min NEMA 23 일체형 | 실험셋업연구소",
"desc":"Runze Fluid BJ30 산업용 연동펌프 — 57 스텝모터(NEMA 23), 0-400 rpm, 유량 0-1700 mL/min, 헤드 YZ1515X / YZ2515X / SN15 / SN25, 스테인리스 3·6롤러, 튜브 ID 1.6-8.0 mm, 최대 3 bar(0.3 MPa). 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 산업용 연동펌프 BJ30",
"answer":"BJ30은 57 스텝모터(NEMA 23)에 YZ 또는 SN 계열 펌프헤드를 직결한 산업용 연동펌프로, 튜브 굵기에 따라 0~1700 mL/min 구간을 다루며 액체가 튜브 안에만 닿아 교차오염이 없습니다.",
"features":[
 "모터 <b>57 스텝모터 (= NEMA 23)</b>, 회전수 0 ~ 400 rpm, 최대 18 W",
 "유량 <b>0 ~ 1700 mL/min</b> — 14# 부터 18# 까지 튜브로 조절합니다",
 "펌프헤드 <b>YZ1515X · YZ2515X (ABS · 흰색/검정)</b> 또는 <b>SN15 · SN25 (PC · 투명)</b> 선택",
 "롤러 <b>스테인리스 3롤러 / 6롤러</b> — 6롤러는 맥동이 작고 3롤러는 유량이 큽니다",
 "<b>퀵 튜브 장착(Fast tubing)</b> 지원, 튜브 ID 1.6-8.0 mm · 두께 1.6-2.5 mm · 외경 11.4 mm 이하",
 "압력 정격 <b>최대 3 bar (0.3 MPa)</b>, 흡입 양정 5 m · 토출 양정 8 m, 소음 65 dB",
 "치수 175.2 × 122.1 × 106 mm, 1525 g(3롤러) / 1585 g(6롤러)"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 1700 mL/min"],
 ["모델 (Model No.)","BJ30-YZ1515X / YZ2515X / SN15 / SN25"],
 ["롤러 (Pump roller)","스테인리스 3롤러 / 6롤러"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱 (YZ) · PC 엔지니어링 플라스틱 (SN)"],
 ["헤드 색상 (Pump color)","흰색 / 검정 (YZ) · 투명 (SN)"],
 ["퀵 튜브 (Fast tubing)","지원"],
 ["모터 (Motor type)","57 스텝모터 (= NEMA 23)"],
 ["회전수 (Motor speed)","0 ~ 400 rpm"],
 ["최대 출력 (Max power)","18 W"],
 ["튜브 규격 (Tubing size)","ID 1.6-8.0 mm · WT 1.6-2.5 mm · OD ≤11.4 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 3 bar (0.3 MPa)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","175.2 × 122.1 × 106 mm"],
 ["순중량 (Net weight)","1525 g (3롤러) · 1585 g (6롤러)"]],
"variants":YZFLOW,"buybox":[],
"related":PREL(' · <a href="/brands/runze/peristaltic-dosing-pump/">YZ1515X · YZ2515X 펌프헤드</a> · <a href="/brands/runze/mini-peristaltic-pump/">미니 연동펌프 BJ-RZ1030</a> · <a href="https://www.runzefluid.com/uploads/file/bj30-series-peristaltic-pump.pdf" rel="nofollow">BJ30 시리즈 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/yz1515x-yz2515x.pdf" rel="nofollow">YZ1515X · YZ2515X 헤드 자료 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=CYH5xKnUeE0" rel="nofollow">BJ30 제조사 소개 영상</a>'),
"keywords":PKW+[["#산업용연동펌프","/product/"],["#NEMA23","/product/"],["#교차오염방지","/product/"]],
"sections":[
 {"h":"펌프헤드 선택 (Pump head)","html":"<ul>"
  "<li><b>YZ1515X · YZ2515X</b> — ABS 엔지니어링 플라스틱, 흰색 또는 검정. 3롤러·6롤러 선택.</li>"
  "<li><b>SN15 · SN25</b> — PC 엔지니어링 플라스틱, 투명. 튜브 상태를 눈으로 확인할 수 있습니다. 같은 튜브에서 YZ 대비 유량이 조금 낮습니다.</li></ul>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":"<p>소형 모터와 대형 모터 구성으로 전장이 달라집니다. BJ30-SN15/SN25 는 152.7 mm / 173.7 mm, BJ30-YZ1515X/YZ2515X 는 154.2 mm / 175.2 mm 입니다.</p>"
  +figs([(D(s,3),"BJ30-SN15/SN25 및 BJ30-YZ1515X/YZ2515X 외형 치수 — 소형·대형 모터 구성")])},
 {"h":"적용 튜브 (Peristaltic tubing)","html":"<ul>"
  "<li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
  "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
  "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"
  "<p>수명은 상온 20℃·무가압에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 회전수가 낮고 액성이 순할수록 길어집니다.</p>"},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"BJ30 (제조사 자료)") for i in [0,1,2,4]])}],
"faq":[
 {"tag":"유량","q":"BJ30은 유량이 얼마나 나오나요?","a":"0~1700 mL/min입니다. 18# 튜브(8.0×1.6 mm)에 YZ1515X 3롤러 조합이 1627.2 mL/min으로 가장 큽니다."},
 {"tag":"헤드","q":"YZ 헤드와 SN 헤드는 뭐가 다른가요?","a":"YZ는 ABS 하우징이고 SN은 PC 투명 하우징이라 튜브 상태를 눈으로 볼 수 있습니다. 같은 튜브에서 SN 쪽 유량이 조금 낮습니다."},
 {"tag":"롤러","q":"3롤러와 6롤러 중 어느 쪽을 골라야 하나요?","a":"유량이 필요하면 3롤러, 맥동을 줄여야 하면 6롤러입니다. 6롤러는 같은 튜브에서 유량이 20~25% 정도 낮고 25#·17#·18# 굵은 튜브는 3롤러 전용입니다."},
 {"tag":"모터","q":"모터는 무엇인가요?","a":"57 스텝모터로 NEMA 23 규격과 같습니다. 0~400 rpm이고 최대 18 W입니다."},
 {"tag":"압력","q":"압력 정격은 얼마인가요?","a":"최대 3 bar(0.3 MPa)입니다. 흡입 양정 5 m, 토출 양정 8 m입니다."},
 {"tag":"오염","q":"펌프 내부가 오염되지 않나요?","a":"액체가 튜브 안쪽에만 닿기 때문에 펌프와 액체 사이에 교차오염이 없습니다."}],
"ld":{"name":"Runze Fluid 산업용 연동펌프 BJ30","sku":"BJ30","category":"연동펌프 · 스텝모터 일체형",
 "description":"57 스텝모터(NEMA 23) 산업용 연동펌프. 0-400 rpm, 0-1700 mL/min, YZ1515X/YZ2515X/SN15/SN25 헤드, 스테인리스 3·6롤러, 튜브 ID 1.6-8.0 mm, 최대 3 bar.",
 "models":["BJ30-YZ1515X","BJ30-YZ2515X","BJ30-SN15","BJ30-SN25"],"count":4},
"source":SRCU("industrial-peristaltic-pump")})

# ---- YZ1515X / YZ2515X head ----
s="peristaltic-dosing-pump"
P.append({
"slug":"peristaltic-dosing-pump","name":"정량 연동펌프 헤드 YZ1515X · YZ2515X","name_en":"Runze Fluid YZ1515X / YZ2515X Peristaltic Dosing Pump Head",
"sub":"플립탑 퀵 튜브 · 스테인리스 3 / 6롤러 · 0-400 rpm · 0-1700 mL/min · 3 bar · 373 g",
"category":"연동펌프 · 펌프헤드",
"title":"Runze Fluid 정량 연동펌프 헤드 YZ1515X · YZ2515X — 플립탑 스테인리스 롤러 | 실험셋업연구소",
"desc":"Runze Fluid YZ1515X / YZ2515X 정량 연동펌프 헤드 — 플립탑 구조로 튜브 교체가 빠르고 스테인리스 3·6롤러 선택, 0-400 rpm, 0-1700 mL/min, 튜브 ID 1.6-8.0 mm, 최대 3 bar(0.3 MPa), 373 g. 스텝·DC·AC 모터 호환. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 정량 연동펌프 헤드 YZ1515X",
"answer":"YZ1515X / YZ2515X는 뚜껑을 젖혀 튜브를 갈아 끼우는 플립탑 정량 연동펌프 헤드로, 스테인리스 3롤러 또는 6롤러를 골라 스텝·DC·AC 어느 모터에나 물려 씁니다.",
"features":[
 "<b>플립탑(Flip-top) 구조</b> — 뚜껑을 젖혀 튜브를 빠르게 갈아 끼웁니다",
 "<b>스테인리스 3롤러 / 6롤러</b> 선택 — 여러 튜브 규격에 자동으로 맞춰집니다",
 "모델 <b>YZ1515X-3B / 3H / 6B / 6H</b>, <b>YZ2515X-3B / 3H / 6B / 6H</b>",
 "<b>스텝모터 · DC모터 · AC모터</b> 어느 쪽에도 물릴 수 있고 회전수 0-400 rpm 입니다",
 "유량 <b>0 ~ 1700 mL/min</b>, 튜브 ID 1.6-8.0 mm · 두께 1.6-2.5 mm · 외경 11.4 mm 이하",
 "압력 정격 <b>최대 3 bar (0.3 MPa)</b>, 흡입 양정 5 m · 토출 양정 8 m",
 "치수 122.1 × 106 × 73.5 mm, 373 g(3롤러) / 433 g(6롤러) — 헤드만으로도 가볍습니다"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 1700 mL/min"],
 ["모델 (Model No.)","YZ1515X-3B / 3H / 6B / 6H · YZ2515X-3B / 3H / 6B / 6H"],
 ["롤러 (Pump roller)","스테인리스 3롤러 / 6롤러"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱"],
 ["헤드 색상 (Pump color)","흰색 / 검정"],
 ["퀵 튜브 (Fast tubing)","지원 (플립탑)"],
 ["호환 모터 (Motor)","스텝모터 · DC모터 · AC모터"],
 ["회전수 (Motor speed)","0 ~ 400 rpm"],
 ["튜브 규격 (Tubing size)","ID 1.6-8.0 mm · WT 1.6-2.5 mm · OD ≤11.4 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 3 bar (0.3 MPa)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","122.1 × 106 × 73.5 mm"],
 ["순중량 (Net weight)","373 g (3롤러) · 433 g (6롤러)"]],
"variants":YZFLOW,"buybox":[],
"related":PREL(' · <a href="/brands/runze/industrial-peristaltic-pump/">산업용 연동펌프 BJ30</a> · <a href="/brands/runze/peristaltic-hose-pump/">호스펌프 헤드 SN15 · SN25</a> · <a href="https://www.runzefluid.com/uploads/file/yz1515x-yz2515x-peristaltic-pump-head.pdf" rel="nofollow">YZ1515X · YZ2515X 헤드 자료 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=cDjRFqiTo6A" rel="nofollow">YZ 헤드 제조사 소개 영상</a>'),
"keywords":PKW+[["#펌프헤드","/product/"],["#플립탑","/product/"],["#정량투입","/product/"]],
"sections":[
 {"h":"모델 코드 (Model code)","html":"<p><b>YZ1515X</b> 와 <b>YZ2515X</b> 뒤에 붙는 <b>3 / 6</b> 은 롤러 수, <b>B / H</b> 는 헤드 구성 구분입니다. 예를 들어 YZ1515X-6H 는 6롤러 구성입니다.</p>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,i),"YZ1515X · YZ2515X 외형 치수 (제조사 자료)") for i in range(2,len(META[s]["det"]))])},
 {"h":"적용 튜브 (Peristaltic tubing)","html":"<ul>"
  "<li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
  "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
  "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"YZ 정량 펌프헤드 (제조사 자료)") for i in range(2)])}],
"faq":[
 {"tag":"구조","q":"플립탑 구조가 뭔가요?","a":"헤드 뚜껑을 위로 젖혀 여는 구조입니다. 공구 없이 튜브를 빠르게 갈아 끼울 수 있습니다."},
 {"tag":"모터","q":"모터가 포함되나요?","a":"펌프헤드 단품입니다. 스텝모터·DC모터·AC모터 어느 쪽에나 물릴 수 있고, 모터가 붙은 완제품이 필요하면 BJ30 구성을 봅니다."},
 {"tag":"롤러","q":"3롤러와 6롤러 차이는?","a":"3롤러가 유량이 크고 6롤러가 맥동이 작습니다. 25#·17#·18# 굵은 튜브는 3롤러 구성만 지원합니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"0~1700 mL/min입니다. 18# 튜브(8.0×1.6 mm) 3롤러에서 20.1~1627.2 mL/min이 나옵니다."},
 {"tag":"튜브","q":"어떤 튜브를 쓰나요?","a":"내경 1.6~8.0 mm, 두께 1.6~2.5 mm, 외경 11.4 mm 이하입니다. 14#·16#·25#·17#·18# 규격을 씁니다."},
 {"tag":"압력","q":"압력은 얼마까지 되나요?","a":"최대 3 bar(0.3 MPa)입니다."},
 {"tag":"중량","q":"헤드 무게는?","a":"3롤러 373 g, 6롤러 433 g입니다. 치수는 122.1 × 106 × 73.5 mm입니다."}],
"ld":{"name":"Runze Fluid 정량 연동펌프 헤드 YZ1515X · YZ2515X","sku":"YZ1515X","category":"연동펌프 · 펌프헤드",
 "description":"플립탑 정량 연동펌프 헤드. 스테인리스 3·6롤러, 0-400 rpm, 0-1700 mL/min, 튜브 ID 1.6-8.0 mm, 최대 3 bar, 373 g, 스텝·DC·AC 모터 호환.",
 "models":["YZ1515X-3B","YZ1515X-3H","YZ1515X-6B","YZ1515X-6H","YZ2515X-3B","YZ2515X-3H","YZ2515X-6B","YZ2515X-6H"],"count":8},
"source":SRCU("peristaltic-dosing-pump")})
add(P)
