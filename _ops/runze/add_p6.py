# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]
TUBE3=("<ul><li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
 "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
 "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"
 "<p>수명은 상온 20℃·무가압에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 회전수가 낮고 액성이 순할수록 길어지며, 정량 정밀도를 유지하려면 주기적으로 교체합니다.</p>")

# ---- SN15 / SN25 hose pump head ----
s="peristaltic-hose-pump"
P.append({
"slug":"peristaltic-hose-pump","name":"호스펌프 헤드 SN15 · SN25","name_en":"Runze Fluid SN15 / SN25 Peristaltic Hose Pump Head",
"sub":"투명 PC 하우징 · 스테인리스 3 / 6롤러 · 0-400 rpm · 0-1725 mL/min · 2단 구조 · 282 g",
"category":"연동펌프 · 펌프헤드",
"title":"Runze Fluid 호스펌프 헤드 SN15 · SN25 — 투명 하우징 스테인리스 롤러 | 실험셋업연구소",
"desc":"Runze Fluid SN15 / SN25 호스펌프 헤드 — 투명 PC 하우징으로 튜브 안 흐름을 눈으로 확인, 스테인리스 3·6롤러, 0-400 rpm, 0-1725 mL/min, 튜브 #14 #16 #25 #17 #15, 최대 2 bar, 77.1×72.5×76 mm · 282 g. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 호스펌프 헤드 SN15",
"answer":"SN15 / SN25는 투명 PC 하우징을 써서 튜브 안의 흐름을 눈으로 확인할 수 있는 호스펌프 헤드로, 2단 구조로 기밀을 잡고 스테인리스 3·6롤러를 골라 여러 모터에 물려 씁니다.",
"features":[
 "<b>투명 PC 하우징</b> — 튜브 안의 흐름 상태를 눈으로 바로 확인합니다",
 "<b>2단(Two-piece) 구조</b> — 기밀이 좋고 압축 간격이 고정되어 안정적입니다",
 "<b>스테인리스 3롤러 / 6롤러</b> — 3롤러는 대유량, 6롤러는 무맥동 고정밀",
 "표준 튜브 <b>#14 · #16 · #25 · #17 (SN15)</b>, <b>#15 (SN25)</b>",
 "<b>스텝모터 · DC모터 · AC모터</b> 호환, 회전수 0-400 rpm, 유량 0-1725 mL/min",
 "압력 정격 최대 2 bar(30 psi), 흡입 양정 5 m · 토출 양정 8 m, 소음 65 dB",
 "치수 <b>77.1 × 72.5 × 76 mm</b>, 282 g(3롤러) / 332 g(6롤러) — 4×4.5 마운팅 홀, 여러 대 직렬 사용 가능"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 1725 mL/min"],
 ["모델 (Model No.)","SN15-3/6- #14 #16 #25 #17 · SN25-3/6- #15"],
 ["롤러 (Pump roller)","스테인리스 3롤러 / 6롤러"],
 ["헤드 재질 (Pump head)","PC 하우징 (투명)"],
 ["퀵 튜브 (Fast tubing)","지원"],
 ["호환 모터 (Motor)","스텝모터 · DC모터 · AC모터"],
 ["회전수 (Motor speed)","0 ~ 400 rpm"],
 ["튜브 규격 (Tubing size)","ID 1.6-8.0 mm · WT 1.6-2.5 mm · OD ≤11.4 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 2 bar (30 psi)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","77.1 × 72.5 × 76 mm"],
 ["순중량 (Net weight)","282 g (3롤러) · 332 g (6롤러)"]],
"variants":{"heading":"튜브 규격별 유량 (mL/min · 5-400 rpm)","head":["튜브 (ID×WT mm)","3롤러","6롤러"],
 "rows":[["14# (1.6×1.6)","1.1 - 87.4","0.8 - 59.5"],["16# (3.2×1.6)","4.3 - 358.3","3.2 - 220.8"],
  ["25# (4.8×1.6)","10.1 - 735.1","−"],["17# (6.4×1.6)","13.2 - 1171.3","−"]],
 "note":"참고값이며 실제 유량은 매질·사용 조건·온습도·전압에 따라 달라집니다. 표의 값은 해당 회전수에서 가장 굵은 튜브로 낼 수 있는 최대 유량입니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/peristaltic-dosing-pump/">YZ1515X · YZ2515X 펌프헤드</a> · <a href="/brands/runze/industrial-peristaltic-pump/">산업용 연동펌프 BJ30</a> · <a href="https://www.youtube.com/watch?v=Z4PjQZFyn9Q" rel="nofollow">SN15 헤드 제조사 소개 영상</a>'),
"keywords":PKW+[["#호스펌프","/product/"],["#펌프헤드","/product/"],["#투명하우징","/product/"]],
"sections":[
 {"h":"구조 특징 (Details)","html":"<p>투명 하우징으로 튜브 상태를 확인하고, 압축 간격이 고정되어 있어 안정적입니다. 여러 대를 직렬로 이어 쓸 수 있습니다.</p>"
  +figs([(D(s,8),"투명 하우징 · 고정 압축 간격 · 직렬 사용 · SN15/SN25X 외형 치수"),(D(s,7),"헤드 세부 구조 (제조사 자료)")])},
 {"h":"적용 튜브 · 참고 유량 (Tubing & flow rate)","html":figs([(D(s,6),"고무 튜브 규격과 3·6롤러 참고 유량표")])+TUBE3},
 {"h":"장착 순서 (Installation steps)","html":figs([(D(s,i),"튜브 장착 순서 · 헤드 외형 (제조사 자료)") for i in [0,1,5]])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"SN15 · SN25 호스펌프 헤드 (제조사 자료)") for i in [2,3,4]])}],
"faq":[
 {"tag":"차이","q":"SN15와 YZ1515X는 뭐가 다른가요?","a":"SN 계열은 PC 투명 하우징이라 튜브 안 흐름을 눈으로 볼 수 있고 압력 정격이 2 bar입니다. YZ 계열은 ABS 하우징에 3 bar까지 견디고 같은 튜브에서 유량이 조금 더 나옵니다."},
 {"tag":"튜브","q":"어떤 튜브 번호를 쓰나요?","a":"SN15는 #14 · #16 · #25 · #17, SN25는 #15입니다. 내경 1.6~8.0 mm, 두께 1.6~2.5 mm 범위입니다."},
 {"tag":"롤러","q":"3롤러와 6롤러 중 어느 쪽인가요?","a":"대유량이 필요하면 3롤러, 맥동 없이 정밀하게 보내야 하면 6롤러입니다. 25#·17# 굵은 튜브는 3롤러만 지원합니다."},
 {"tag":"모터","q":"모터가 포함되나요?","a":"헤드 단품입니다. 스텝모터·DC모터·AC모터 어느 쪽에나 물릴 수 있습니다."},
 {"tag":"압력","q":"압력은 얼마까지 되나요?","a":"최대 2 bar(30 psi)입니다."},
 {"tag":"설치","q":"크기와 고정 방법은?","a":"77.1 × 72.5 × 76 mm, 282 g(3롤러) / 332 g(6롤러)이고 4×4.5 마운팅 홀로 고정합니다."}],
"ld":{"name":"Runze Fluid 호스펌프 헤드 SN15 · SN25","sku":"SN15","category":"연동펌프 · 펌프헤드",
 "description":"투명 PC 하우징 호스펌프 헤드. 스테인리스 3·6롤러, 0-400 rpm, 0-1725 mL/min, 튜브 #14/#16/#25/#17/#15, 최대 2 bar, 282 g, 스텝·DC·AC 모터 호환.",
 "models":["SN15-3","SN15-6","SN25-3","SN25-6"],"count":4},
"source":SRCU("peristaltic-hose-pump")})

# ---- LM60A / LM60B ----
s="peristaltic-metering-pump"
P.append({
"slug":"peristaltic-metering-pump","name":"지능형 정량 연동펌프 LM60A · LM60B","name_en":"Runze Fluid LM60A / LM60B Intelligent Peristaltic Pump",
"sub":"연속 / 정량 / 예약 / 교정 4모드 · 0.1-400 rpm 정·역 · LM60A 최대 1295 mL/min · LM60B 최대 236 mL/min",
"category":"연동펌프 · 컨트롤러 일체형",
"title":"Runze Fluid 지능형 정량 연동펌프 LM60A · LM60B — 4모드 프리셋 충전 펌프 | 실험셋업연구소",
"desc":"Runze Fluid LM60A / LM60B 지능형 정량 연동펌프 — 분주량·분주 시간·반복 횟수·대기 시간을 미리 넣어 반복 충전, 0.1~400 rpm 정·역, 속도 분해능 0.1 rpm, LM60A 0.027-1295 mL/min · LM60B 0-161 mL/min, 풋스위치·RS232·RS485, IP31. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 지능형 정량 연동펌프 LM60A",
"answer":"LM60A · LM60B는 분주량·분주 시간·반복 횟수·대기 시간을 미리 입력해 두면 그대로 반복 충전하는 지능형 연동펌프로, 연속·정량·예약·교정 네 가지 모드를 패널에서 고릅니다.",
"features":[
 "<b>연속 · 정량 · 예약 · 교정</b> 네 가지 운전 모드",
 "<b>분주량 · 분주 시간 · 반복 횟수 · 대기 시간(0-999999 s)</b> 을 미리 넣어 정기 충전 공정을 돌립니다",
 "속도 <b>0.1 ~ 400 rpm 정·역</b>, 속도 분해능 <b>0.1 rpm</b>",
 "<b>LM60A</b> — 헤드 YZ1515X / YZ2515X / SN15 / SN25, 유량 0.027 ~ 1295 mL/min, 최대 30 W, 3.5 kg(헤드 제외)",
 "<b>LM60B</b> — 헤드 RZ1030 / RZ1030B / RZ01 / RZ02, 유량 0 ~ 161 mL/min, 최대 20 W, 1.45 kg(헤드 제외)",
 "외부 제어 <b>풋스위치 · RS232 · RS485</b>, 한 버튼 최고속(충전·배출)",
 "중문·영문 표시, DC24V ±10%, 0-40℃ · 상대습도 80% 미만, 보호 등급 IP31"],
"specs":[
 ["유량 범위 (Flow rate)","LM60A 0.027 ~ 1295 mL/min · LM60B 0 ~ 161 mL/min"],
 ["모델 (Product name)","LM60A / LM60B 지능형 연동펌프"],
 ["적용 펌프헤드 (Pump head)","LM60A: YZ1515X · YZ2515X · SN15 · SN25<br>LM60B: RZ1030 · RZ1030B · RZ01 · RZ02"],
 ["롤러 (Pump roller)","YZ/SN 스테인리스 3·6롤러 · RZ1030 POM 4롤러 · RZ1030B POM 4/8롤러 · RZ01 PPS 4롤러 · RZ02 PPS 3/6롤러"],
 ["모터 (Motor type)","스텝모터"],
 ["속도 범위 (Speed range)","0.1 ~ 400 rpm · 정역 전환"],
 ["속도 분해능 (Speed resolution)","0.1 rpm"],
 ["운전 모드 (Working mode)","교정 · 연속 · 정량 · 예약"],
 ["외부 제어 (External control)","풋스위치 · RS232 · RS485"],
 ["대기 시간 (Latency time)","0 ~ 999999 s"],
 ["간격 시간 (Interval time)","0 ~ 999999 s · 사전 설정"],
 ["분주량 · 시간 (Dispensing)","사전 설정"],
 ["최고속 (Full speed)","한 버튼 전환 (충전 · 배출)"],
 ["표시 언어 (Language)","중문 / 영문"],
 ["전원 (Power supply)","DC24V ±10%"],
 ["최대 소비전력 (Max power)","LM60A 30 W · LM60B 20 W"],
 ["사용 환경 (Environment)","0 ~ 40℃ · 상대습도 80% 미만 · 비결로"],
 ["보호 등급 (Protection)","IP31"],
 ["순중량 (Net weight)","LM60A 3.5 kg · LM60B 1.45 kg (펌프헤드 제외)"]],
"variants":{"heading":"모델별 최대 유량 (Media: water)","head":["모델","헤드 재질 · 색상","롤러","적용 튜브","최대 유량"],
 "rows":[["LM60A-YZ1515X-3B / 3H","흰색 / 검정","3","#14 #16 #25 #17","1249 mL/min (400 rpm)"],
  ["LM60A-YZ1515X-6B / 6H","흰색 / 검정","6","#14 #16","244 mL/min (400 rpm)"],
  ["LM60A-YZ2515X-3B / 3H","흰색 / 검정","3","#15 #24","1295 mL/min (400 rpm)"],
  ["LM60A-SN15-3","투명","3","#14 #16 #25 #17","997 mL/min (300 rpm)"],
  ["LM60B-RZ1030 / RZ1030B","POM / PPS","4","ID 0.64-3.0 · WT 0.8-1.0 · OD ≤5.0 mm","128 mL/min (ID2.79×0.8) · 183 mL/min (ID3.0×1.0)"],
  ["LM60B-RZ1030B","PPS","8","ID 0.64-3.0 · WT 0.8-1.0 · OD ≤5.0 mm","81 mL/min (ID2.79×0.8) · 114 mL/min (ID3.0×1.0)"],
  ["LM60B-RZ01","PC","4","ID 0.64-3.0 · WT 0.8-1.0 · OD ≤6.4 mm","96 mL/min (ID2.79×0.8) · 152 mL/min (ID3.2×1.6)"],
  ["LM60B-RZ02","PPS","3","ID 0.64-3.0 · WT 0.8-1.0 · OD ≤6.4 mm","162 mL/min (ID2.79×0.8) · 236 mL/min (ID3.2×1.6)"],
  ["LM60B-RZ02","PPS","6","ID 0.64-3.0 · WT 0.8-1.0 · OD ≤6.4 mm","114 mL/min (ID2.79×0.8) · 183 mL/min (ID3.2×1.6)"]],
 "note":"매질 물 기준 최대 유량입니다. 실리콘 튜브 규격은 내경×두께(mm)로 표기했습니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/lm40b-micro-peristaltic-pump/">지능형 충전 연동펌프 LM40B</a> · <a href="/brands/runze/peristaltic-dosing-pump/">YZ1515X · YZ2515X 펌프헤드</a> · <a href="/brands/runze/peristaltic-hose-pump/">SN15 · SN25 호스펌프 헤드</a> · <a href="https://www.runzefluid.com/uploads/file/lm60a-intelligent-peristaltic-pump-instruction-manual.pdf" rel="nofollow">LM60A 매뉴얼 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/lm60b-intelligent-peristaltic-pump-instruction-manual.pdf" rel="nofollow">LM60B 매뉴얼 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=s9xC7UyDvfs" rel="nofollow">LM60 제조사 소개 영상</a>'),
"keywords":PKW+[["#정량충전","/product/"],["#반복분주","/product/"],["#지능형연동펌프","/product/"]],
"sections":[
 {"h":"4가지 운전 모드 (Working mode)","html":"<ul>"
  "<li><b>연속 (Continuous)</b> — 특별한 조건 없이 액체를 계속 이송합니다</li>"
  "<li><b>정량 (Rationing)</b> — 지정한 부피를 한 번에 분주합니다</li>"
  "<li><b>예약 (Booking)</b> — 지정한 부피를 N회 반복 분주합니다</li>"
  "<li><b>교정 (Calibration)</b> — 다른 모드를 시작하기 전에 정확도를 맞춥니다</li></ul>"},
 {"h":"제어 방식 · 외형 (Control mode & dimension)","html":figs([(D(s,i),"LM60A · LM60B 제어 방식과 외형 치수 (제조사 자료)") for i in range(12,len(META[s]["det"]))])},
 {"h":"적용 튜브 (Peristaltic tubing)","html":TUBE3},
 {"h":"제조사 자료 (Reference)","html":figs([(D(s,i),"LM60A · LM60B 제조사 자료") for i in range(0,12)])},
 {"h":"용도 (Applications)","html":"<ul><li>정기 충전 공정 (Regular filling)</li><li>시약·원료 반복 분주</li><li>실험실 자동 계량 이송</li></ul>"}],
"faq":[
 {"tag":"선택","q":"LM60A와 LM60B는 어떻게 고르나요?","a":"유량으로 갈립니다. LM60A는 YZ·SN 대유량 헤드로 최대 1295 mL/min, LM60B는 RZ 소형 헤드로 최대 236 mL/min입니다. 무게도 3.5 kg과 1.45 kg으로 차이가 큽니다."},
 {"tag":"모드","q":"예약 모드는 무엇인가요?","a":"지정한 속도에서 지정한 부피를 N회 반복 분주하는 모드입니다. 대기 시간과 간격 시간을 0~999999초 범위에서 미리 넣어 둡니다."},
 {"tag":"교정","q":"교정은 언제 하나요?","a":"다른 모드를 시작하기 전이나 펌프·튜브를 바꾼 뒤에 합니다. 분주량과 유량의 정확도를 맞추는 절차입니다."},
 {"tag":"제어","q":"외부 제어는 무엇을 지원하나요?","a":"풋스위치, RS232, RS485입니다."},
 {"tag":"속도","q":"역방향으로 돌릴 수 있나요?","a":"0.1~400 rpm 범위에서 정·역 모두 됩니다. 속도 분해능은 0.1 rpm입니다."},
 {"tag":"헤드","q":"펌프헤드는 따로 사야 하나요?","a":"본체 중량이 헤드 제외 기준으로 표기됩니다. LM60A는 YZ1515X·YZ2515X·SN15·SN25, LM60B는 RZ1030·RZ1030B·RZ01·RZ02 중에서 골라 조합합니다."},
 {"tag":"보호","q":"보호 등급은?","a":"IP31입니다. 사용 환경은 0~40℃, 상대습도 80% 미만입니다."}],
"ld":{"name":"Runze Fluid 지능형 정량 연동펌프 LM60A · LM60B","sku":"LM60A","category":"연동펌프 · 컨트롤러 일체형",
 "description":"지능형 정량 연동펌프. 연속·정량·예약·교정 4모드, 분주량·시간·횟수·대기 시간 프리셋, 0.1~400 rpm 정역, LM60A 0.027-1295 mL/min, LM60B 0-161 mL/min, 풋스위치·RS232·RS485, IP31.",
 "models":["LM60A-YZ1515X","LM60A-YZ2515X","LM60A-SN15","LM60B-RZ1030","LM60B-RZ1030B","LM60B-RZ01","LM60B-RZ02"],"count":9},
"source":SRCU("peristaltic-metering-pump")})
add(P)
