# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]

# ---- RZ1030-4 pump head ----
s="miniature-peristaltic-pump"
P.append({
"slug":"miniature-peristaltic-pump","name":"미니어처 연동펌프 헤드 RZ1030-4","name_en":"Runze Fluid RZ1030-4 Miniature Peristaltic Pump Head",
"sub":"POM 4롤러 · ABS 헤드 · 0-500 rpm · 0-170 mL/min · 퀵 튜브 장착 · 58 g",
"category":"연동펌프 · 펌프헤드",
"title":"Runze Fluid 미니어처 연동펌프 헤드 RZ1030-4 — 0-170 mL/min 소형 펌프헤드 | 실험셋업연구소",
"desc":"Runze Fluid RZ1030-4 미니어처 연동펌프 헤드 — POM 4롤러, ABS 엔지니어링 플라스틱 헤드, 0-500 rpm, 유량 0-170 mL/min, 튜브 ID 0.64-3.0 mm, 2 bar, 57×65×23 mm · 58 g. 스텝모터·DC모터 호환. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 미니어처 연동펌프 헤드 RZ1030-4",
"answer":"RZ1030-4는 POM 4롤러에 ABS 헤드를 쓴 58 g짜리 미니어처 연동펌프 헤드로, 스텝모터나 DC모터에 직접 물려 0-170 mL/min 구간을 다루는 장비 내장용 헤드입니다.",
"features":[
 "롤러 <b>POM 4롤러</b>, 헤드 <b>ABS 엔지니어링 플라스틱</b> — 검정색",
 "<b>퀵 튜브 장착(Fast tubing)</b> — 공구 없이 튜브를 갈아 끼웁니다",
 "<b>스텝모터 · DC모터</b> 어느 쪽에도 물릴 수 있고 회전수 0-500 rpm 입니다",
 "유량 <b>0 ~ 170 mL/min</b>, 튜브 ID 0.64-3.0 mm · 두께 0.8-1.0 mm · 외경 5 mm 이하",
 "압력 정격 <b>최대 2 bar(30 psi)</b>, 흡입 양정 5 m · 토출 양정 8 m",
 "치수 <b>57 × 65 × 23 mm</b>, 58 g — 4-M3 마운팅 홀",
 "습부는 튜브 내면뿐이라 <b>강산·강염기·유기용매·입자 포함 액체</b> 도 튜브만 맞으면 이송합니다"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 170 mL/min"],
 ["모델 (Model No.)","RZ1030-4"],
 ["롤러 (Pump roller)","POM 4롤러"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱"],
 ["퀵 튜브 (Fast tubing)","지원"],
 ["호환 모터 (Motor)","스텝모터 · DC모터"],
 ["회전수 (Motor speed)","0 ~ 500 rpm"],
 ["튜브 규격 (Tubing size)","ID 0.64-3.0 mm · WT 0.8-1.0 mm · OD ≤5 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 2 bar (30 psi)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","57 × 65 × 23 mm"],
 ["순중량 (Net weight)","58 g"]],
"variants":TUBE,"buybox":[],
"related":PREL(' · <a href="/brands/runze/mini-peristaltic-pump/">미니 연동펌프 BJ-RZ1030</a> · <a href="/brands/runze/12v-peristaltic-pump/">12V 연동펌프 ZL12-RZ1030</a> · <a href="https://www.youtube.com/watch?v=WSRScBa2Oy4" rel="nofollow">RZ1030-4 제조사 소개 영상</a>'),
"keywords":PKW+[["#펌프헤드","/product/"],["#소형연동펌프","/product/"]],
"sections":[
 {"h":"연동펌프의 작동 원리","html":"<p>미니 연동펌프는 저압 펌프로 일반 사용 압력이 0.7 MPa를 넘지 않습니다(대형 호스펌프는 1 MPa 이상). 롤러가 탄성 튜브를 번갈아 누르고 놓으면 튜브 안에 음압이 생기면서 액체가 밀려 나갑니다. 손가락 두 개로 호스를 집어 훑는 것과 같은 동작입니다. 입자가 든 액체는 물론 강산·강염기·강한 유기용매도 튜브 재질만 맞으면 이송할 수 있습니다.</p>"},
 {"h":"연동펌프의 장점","html":"<ol><li><b>무오염</b> — 액체가 튜브 내면에만 닿고 펌프 본체에는 닿지 않습니다</li>"
  "<li><b>정밀도</b> — 반복 정밀도와 안정도가 높습니다</li>"
  "<li><b>낮은 전단력</b> — 전단에 민감한 액체와 부식성 액체 이송에 적합합니다</li>"
  "<li><b>기밀성</b> — 자흡력이 좋고 공회전이 가능하며 역류를 막습니다</li>"
  "<li><b>간단한 유지보수</b> — 밸브와 실링이 없습니다</li>"
  "<li><b>낮은 가격</b> — 헤드 디스크를 플라스틱으로 만들어 원가를 낮췄습니다</li></ol>"},
 {"h":"유지보수 · 주의 사항","html":"<p>연동펌프는 드라이버 · 펌프헤드 · 튜브 세 부분으로 나뉩니다. 이 중 <b>튜브가 소모품</b> 이라 주기적으로 갈아야 하고, 드라이버와 펌프헤드는 무보수 부품이라 건조하게 유지하고 청소만 하면 됩니다.</p>"
  "<p>펌프헤드가 상하는 경우는 대체로 세 가지입니다. 첫째 설계 회전수를 넘겨 돌린 경우, 둘째 높은 곳에서 떨어뜨려 헤드가 변형·파손된 경우, 셋째 튜브가 새서 액체가 롤러와 주축 베어링으로 들어가 베어링을 망가뜨린 경우입니다.</p>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,3),"RZ1030-4 외형 치수와 4-M3 마운팅 홀")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"RZ1030-4 펌프헤드 (제조사 자료)") for i in range(3)])}],
"faq":[
 {"tag":"유량","q":"RZ1030-4는 유량이 얼마나 나오나요?","a":"0~170 mL/min입니다. 튜브 내경과 회전수에 따라 달라지며 최대 회전수는 500 rpm입니다."},
 {"tag":"모터","q":"모터는 따로 준비해야 하나요?","a":"펌프헤드 단품이라 모터는 따로 물립니다. 스텝모터와 DC모터 모두 호환됩니다. 완제품이 필요하면 BJ-RZ1030(스텝모터)이나 ZL12-RZ1030(DC모터) 구성을 봅니다."},
 {"tag":"튜브","q":"어떤 튜브를 쓰나요?","a":"내경 0.64~3.0 mm, 두께 0.8~1.0 mm, 외경 5 mm 이하입니다. 실리콘·PharMed BPT·Viton 중에서 액성에 맞춰 고릅니다."},
 {"tag":"수명","q":"튜브는 얼마나 쓰나요?","a":"실리콘 200시간 이상, PharMed BPT와 Viton은 1000시간 이상입니다. 상온 무가압 순수 기준이라 실제 조건에서는 달라집니다."},
 {"tag":"압력","q":"압력은 얼마까지 견디나요?","a":"최대 2 bar(30 psi)입니다. 흡입 양정 5 m, 토출 양정 8 m입니다."},
 {"tag":"설치","q":"크기와 고정 방법은?","a":"57 × 65 × 23 mm에 58 g이고 4-M3 마운팅 홀로 고정합니다."},
 {"tag":"오염","q":"액체가 펌프 안쪽에 닿나요?","a":"닿지 않습니다. 액체는 튜브 내면에만 접촉하므로 시료 오염이 없고 밸브·실링도 없습니다."}],
"ld":{"name":"Runze Fluid 미니어처 연동펌프 헤드 RZ1030-4","sku":"RZ1030-4","category":"연동펌프 · 펌프헤드",
 "description":"POM 4롤러 미니어처 연동펌프 헤드. 0-500 rpm, 0-170 mL/min, 튜브 ID 0.64-3.0 mm, 최대 2 bar, 57×65×23 mm, 58 g, 스텝모터·DC모터 호환.",
 "models":["RZ1030-4"],"count":1},
"source":SRCU("miniature-peristaltic-pump")})

# ---- 12V peristaltic pump ----
s="12v-peristaltic-pump"
P.append({
"slug":"12v-peristaltic-pump","name":"12V 연동펌프 ZL12-RZ1030-4","name_en":"Runze Fluid ZL12/ZL24-RZ1030-4-300R 12V Peristaltic Pump",
"sub":"12V / 24V DC 모터 일체형 · 300 rpm · 0-120 mL/min · POM 4롤러 · 255 g",
"category":"연동펌프 · DC모터 일체형",
"title":"Runze Fluid 12V 연동펌프 ZL12-RZ1030-4 — DC모터 일체형 소형 연동펌프 | 실험셋업연구소",
"desc":"Runze Fluid 12V 연동펌프 ZL12/ZL24-RZ1030-4-300R — 12V/24V DC 모터 일체형, 300 rpm, 유량 0-120 mL/min, POM 4롤러, 튜브 ID 0.64-3.0 mm, 최대 2 bar, 90×57×65 mm · 255 g. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 12V 연동펌프 ZL12-RZ1030-4",
"answer":"ZL12/ZL24-RZ1030-4-300R은 RZ1030-4 헤드에 12V 또는 24V DC 모터를 붙인 일체형 소형 연동펌프로, 전원만 넣으면 바로 도는 저가·저맥동 정량 이송용입니다.",
"features":[
 "<b>12V / 24V DC 모터</b> 일체형 — 전원을 넣으면 바로 돕니다",
 "회전수 <b>300 rpm</b> 고정, 유량 <b>0 ~ 120 mL/min</b>",
 "정격 전류 0.15 A, 정격 출력 <b>1.8 W(12V) / 3.6 W(24V)</b>, 최대 15 W",
 "롤러 <b>POM 4롤러</b>, 헤드 ABS 엔지니어링 플라스틱",
 "튜브 ID 0.64-3.0 mm · 두께 0.8-1.0 mm · 외경 5 mm 이하, 압력 정격 최대 2 bar(30 psi)",
 "흡입 양정 5 m · 토출 양정 8 m, 소음 65 dB",
 "치수 <b>90 × 57 × 65 mm</b>, 255 g — 4-Ø4.1 마운팅 홀"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 120 mL/min"],
 ["모델 (Model No.)","ZL12-RZ1030-4-300R · ZL24-RZ1030-4-300R"],
 ["롤러 (Pump roller)","POM 4롤러"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱"],
 ["모터 (Motor type)","12V / 24V DC 모터"],
 ["회전수 (Motor speed)","300 rpm"],
 ["정격 전류 (Rated current)","0.15 A"],
 ["정격 출력 (Rated power)","1.8 W (12V) · 3.6 W (24V) · 최대 15 W"],
 ["튜브 규격 (Tubing size)","ID 0.64-3.0 mm · WT 0.8-1.0 mm · OD ≤5 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 2 bar (30 psi)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","90 × 57 × 65 mm"],
 ["순중량 (Net weight)","255 g"]],
"variants":{"heading":"튜브 규격별 최대 유량 (mL/min · 300 rpm)","head":["튜브","ID×WT (mm)","ZL12-RZ1030-4-300R","ZL24-RZ1030-4-300R"],
 "rows":[["고무 튜브","0.64 × 0.8","6","10"],["고무 튜브","0.76 × 0.8","9","13"],["고무 튜브","0.89 × 0.8","10","16"],
  ["고무 튜브","1.02 × 0.8","13","22"],["고무 튜브","1.14 × 0.8","14","24"],["고무 튜브","1.30 × 0.8","22","32"],
  ["고무 튜브","1.42 × 0.8","28","36"],["고무 튜브","1.52 × 0.8","31","41"],["고무 튜브","1.65 × 0.8","37","46"],
  ["고무 튜브","1.85 × 0.8","46","54"],["고무 튜브","2.06 × 0.8","55","67"],["고무 튜브","2.29 × 0.8","58","96"],
  ["고무 튜브","2.54 × 0.8","95","112"],["고무 튜브","2.79 × 0.8","105","125"],
  ["실리콘 튜브","1 × 1","15","23"],["실리콘 튜브","2 × 1","47","86"],["실리콘 튜브","3 × 1","122","140"]],
 "note":"상온 상압에서 순수를 이송해 잰 값입니다. 매질과 사용 환경에 따라 실제 유량은 달라집니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/miniature-peristaltic-pump/">미니어처 연동펌프 헤드 RZ1030-4</a> · <a href="/brands/runze/mini-peristaltic-pump/">미니 연동펌프 BJ-RZ1030</a> · <a href="https://www.youtube.com/watch?v=_2QP7HLIT60" rel="nofollow">12V 연동펌프 제조사 소개 영상</a>'),
"keywords":PKW+[["#12V연동펌프","/product/"],["#DC모터펌프","/product/"]],
"sections":[
 {"h":"적용 튜브 (Peristaltic tubing)","html":"<p>실리콘 · PharMed BPT · Viton 세 가지를 액성에 맞춰 고릅니다.</p><ul>"
  "<li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
  "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
  "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,3),"ZL12/ZL24-RZ1030-4 외형 치수와 4-Ø4.1 마운팅 홀")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"12V 연동펌프 (제조사 자료)") for i in range(3)])}],
"faq":[
 {"tag":"전압","q":"12V와 24V 중 어느 쪽을 골라야 하나요?","a":"같은 튜브에서 24V 모델이 유량이 더 많이 나옵니다. 예를 들어 실리콘 3×1 튜브에서 12V는 122 mL/min, 24V는 140 mL/min입니다. 장비 전원에 맞춰 고르면 됩니다."},
 {"tag":"유량","q":"유량은 어떻게 조절하나요?","a":"이 모델은 300 rpm 고정이라 튜브 규격으로 유량을 정합니다. 속도 조절이 필요하면 스텝모터 구성인 BJ-RZ1030이나 컨트롤러가 붙은 LM 시리즈를 봅니다."},
 {"tag":"튜브","q":"어떤 튜브를 쓸 수 있나요?","a":"내경 0.64~3.0 mm, 두께 0.8~1.0 mm, 외경 5 mm 이하입니다."},
 {"tag":"압력","q":"압력은 얼마까지 되나요?","a":"최대 2 bar(30 psi)이고 흡입 양정 5 m, 토출 양정 8 m입니다."},
 {"tag":"소비전력","q":"소비전력은 얼마인가요?","a":"정격 1.8 W(12V) 또는 3.6 W(24V), 정격 전류 0.15 A입니다. 최대 15 W입니다."},
 {"tag":"설치","q":"크기와 고정 방법은?","a":"90 × 57 × 65 mm, 255 g이고 4-Ø4.1 마운팅 홀로 고정합니다."}],
"ld":{"name":"Runze Fluid 12V 연동펌프 ZL12-RZ1030-4","sku":"ZL12-RZ1030-4-300R","category":"연동펌프 · DC모터 일체형",
 "description":"12V/24V DC 모터 일체형 소형 연동펌프. 300 rpm, 0-120 mL/min, POM 4롤러, 튜브 ID 0.64-3.0 mm, 최대 2 bar, 90×57×65 mm, 255 g.",
 "models":["ZL12-RZ1030-4-300R","ZL24-RZ1030-4-300R"],"count":2},
"source":SRCU("12v-peristaltic-pump")})
add(P)
