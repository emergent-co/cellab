# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]

# ---- BJ-RZ1030 mini peristaltic pump (stepper) ----
s="mini-peristaltic-pump"
P.append({
"slug":"mini-peristaltic-pump","name":"미니 연동펌프 BJ-RZ1030","name_en":"Runze Fluid BJ-RZ1030-4 / BJ-RZ1030B Mini Peristaltic Pump",
"sub":"NMB 42 스텝모터 일체형 · 0-400 rpm · 9-183 mL/min · POM 4 / 8롤러 저맥동",
"category":"연동펌프 · 스텝모터 일체형",
"title":"Runze Fluid 미니 연동펌프 BJ-RZ1030-4 / BJ-RZ1030B — 42 스텝모터 저맥동 | 실험셋업연구소",
"desc":"Runze Fluid 미니 연동펌프 BJ-RZ1030-4 / BJ-RZ1030B — NMB 1.8° 42 스텝모터 일체형, 0-400 rpm, 유량 12.5-170 / 9-183 mL/min, POM 4 또는 8롤러 저맥동, ABS·PPS 헤드, 최대 2 bar. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 미니 연동펌프 BJ-RZ1030",
"answer":"BJ-RZ1030은 NMB 1.8° 42 스텝모터를 RZ1030 헤드에 직결한 미니 연동펌프로, 4롤러 저맥동 기본형(BJ-RZ1030-4)과 PPS 헤드에 4/8롤러를 고르는 상위형(BJ-RZ1030B) 두 가지가 있습니다.",
"features":[
 "<b>NMB 1.8° 42 스텝모터</b> 직결 — 24V DC, 정격 1.1 A, 최대 9.2 W",
 "회전수 <b>0 ~ 400 rpm</b> 무단 조절 — 스텝 구동이라 유량을 정밀하게 맞춥니다",
 "<b>BJ-RZ1030-4</b> — ABS 헤드 · POM 4롤러 저맥동 · 12.5 ~ 170 mL/min · 424 g",
 "<b>BJ-RZ1030B</b> — PPS 헤드 · POM 4 또는 8롤러 · 9 ~ 183 mL/min · 432 g (8롤러는 맥동이 더 작습니다)",
 "튜브 ID 0.64-3.0 mm · 두께 0.8-1.0 mm · 외경 5 mm 이하, 압력 정격 최대 2 bar(30 psi)",
 "튜브 수명 실리콘 ≥200 h, PharMed BPT · Viton ≥1000 h",
 "소음 70 dB, 흡입 양정 약 5 m, 사용 환경 0-40℃ · 상대습도 80% 이하"],
"specs":[
 ["유량 범위 (Flow rate)","12.5 ~ 170 mL/min (BJ-RZ1030-4) · 9 ~ 183 mL/min (BJ-RZ1030B)"],
 ["롤러 (Pump roller)","POM 4롤러 (저맥동) · BJ-RZ1030B 는 4 / 8롤러 선택"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱 (−4) · PPS (B)"],
 ["모터 (Motor type)","NMB 1.8° 42 스텝모터"],
 ["입력 전압 (Input voltage)","24V DC"],
 ["정격 전류 (Rated current)","1.1 A"],
 ["최대 출력 (Max power)","9.2 W"],
 ["회전수 (Motor speed)","0 ~ 400 rpm"],
 ["튜브 규격 (Tubing size)","ID 0.64-3.0 mm · WT 0.8-1.0 mm · OD ≤5 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h · Viton ≥1000 h"],
 ["압력 정격 (Pressure)","최대 2 bar (30 psi)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 이하 · 비결로"],
 ["소음 (Max noise)","70 dB"],
 ["흡입 (Suction)","약 5 m"],
 ["치수 L×W×H (Dimension)","57 × 57 × 63.5 mm (−4) · 57 × 57 × 72.4 mm (B)"],
 ["순중량 (Net weight)","424 g (−4) · 432 g (B)"]],
"variants":{"heading":"튜브 규격별 최대 유량 (mL/min)","head":["모델 · 롤러","0.64","1.02","1.42","1.85","2.29","2.79","실리콘 1×1","실리콘 2×1","실리콘 3×1"],
 "rows":[["BJ-RZ1030-4 (4롤러)","12.5","28.2","51.9","89","112.6","146.9","26.1","105","170"],
  ["BJ-RZ1030B (4롤러)","12","25","47","70","94","128","24","74","183"],
  ["BJ-RZ1030B (8롤러)","9","21","38","55","71","81","17","57","114"]],
 "note":"고무 튜브는 두께 0.8 mm 기준 내경(mm) 값이고, 실리콘 튜브는 내경×두께(mm) 값입니다. 상온 20℃·무가압에서 순수를 이송해 잰 참고값이며 매질·조건·압력·온습도에 따라 달라집니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/miniature-peristaltic-pump/">미니어처 연동펌프 헤드 RZ1030-4</a> · <a href="/brands/runze/12v-peristaltic-pump/">12V 연동펌프 ZL12-RZ1030</a> · <a href="https://www.runzefluid.com/uploads/file/bj-rz1030-4-peristaltic-pump.pdf" rel="nofollow">BJ-RZ1030-4 카탈로그 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=iCIzbFI_LM4" rel="nofollow">BJ-RZ1030 제조사 소개 영상</a>'),
"keywords":PKW+[["#스텝모터연동펌프","/product/"],["#저맥동","/product/"]],
"sections":[
 {"h":"모터 사양 · 배선 (Motor & wiring)","html":"<p><b>42 스텝모터</b> — 최대 출력 9.2 W, 스텝 각도 1.8°, 2상, 상전압 4.6 V, 상전류 1.1 A, 저항 3.8 Ω ±0.38 Ω, 인덕턴스 5.2 mH, 절연 100 MΩ MIN, 최고 온도 80℃, 절연 등급 B.</p>"
  "<p>모터 배선 색은 <b>A+ 주황 · A− 파랑 · B+ 빨강 · B− 노랑</b> 입니다.</p>"
  +figs([(D(s,6),"42 스텝모터 사양과 모터 배선 색 정의")])},
 {"h":"튜브 장착 (Tubing installation)","html":figs([(D(s,3),"튜브 장착 순서 (제조사 자료)")])},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,4),"BJ-RZ1030-4 외형 치수"),(D(s,5),"BJ-RZ1030B-4 / 8 외형 치수")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"BJ-RZ1030 (제조사 자료)") for i in range(3)])},
 {"h":"적용 튜브 (Peristaltic tubing)","html":"<ul>"
  "<li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
  "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
  "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"
  "<p>수명은 상온 20℃·무가압에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 회전수가 낮고 액성이 순할수록 길어지며, 정량 정밀도를 유지하려면 주기적으로 교체합니다.</p>"}],
"faq":[
 {"tag":"선택","q":"BJ-RZ1030-4와 BJ-RZ1030B는 뭐가 다른가요?","a":"헤드 재질과 롤러 수가 다릅니다. -4는 ABS 헤드에 4롤러 고정이고, B는 PPS 헤드에 4롤러와 8롤러를 고를 수 있습니다. B의 8롤러는 유량이 줄지만 맥동이 더 작습니다."},
 {"tag":"유량","q":"유량 범위는 어떻게 되나요?","a":"BJ-RZ1030-4는 12.5~170 mL/min, BJ-RZ1030B는 9~183 mL/min입니다. 튜브 규격과 회전수로 결정됩니다."},
 {"tag":"제어","q":"속도를 조절할 수 있나요?","a":"42 스텝모터 구동이라 0~400 rpm 사이에서 무단 조절됩니다. 별도 드라이버로 스텝 펄스를 넣어 제어합니다."},
 {"tag":"배선","q":"모터 배선 색 정의는?","a":"A+ 주황, A− 파랑, B+ 빨강, B− 노랑입니다. 2상 스텝모터이고 상전압 4.6 V, 상전류 1.1 A입니다."},
 {"tag":"맥동","q":"맥동을 줄이려면 어떻게 하나요?","a":"BJ-RZ1030B의 8롤러 구성을 고르면 맥동이 작아집니다. 다만 같은 튜브에서 유량은 4롤러 대비 30% 정도 줄어듭니다."},
 {"tag":"압력","q":"압력 정격은?","a":"최대 2 bar(30 psi)입니다."},
 {"tag":"소음","q":"소음은 어느 정도인가요?","a":"최대 70 dB입니다."}],
"ld":{"name":"Runze Fluid 미니 연동펌프 BJ-RZ1030","sku":"BJ-RZ1030","category":"연동펌프 · 스텝모터 일체형",
 "description":"NMB 42 스텝모터 일체형 미니 연동펌프. 0-400 rpm, 12.5-170 / 9-183 mL/min, POM 4·8롤러 저맥동, 최대 2 bar, 튜브 ID 0.64-3.0 mm.",
 "models":["BJ-RZ1030-4","BJ-RZ1030B"],"count":2},
"source":SRCU("mini-peristaltic-pump")})

# ---- LM40A ----
s="micro-peristaltic-pump"
P.append({
"slug":"micro-peristaltic-pump","name":"마이크로 연동펌프 LM40A","name_en":"Runze Fluid LM40A Micro Peristaltic Pump",
"sub":"박스형 컨트롤러 일체형 · 0.1-400 rpm · 속도 분해능 ±0.1 rpm · 풋스위치 · RS485 · IP31",
"category":"연동펌프 · 컨트롤러 일체형",
"title":"Runze Fluid 마이크로 연동펌프 LM40A — 박스형 속도 제어 연동펌프 | 실험셋업연구소",
"desc":"Runze Fluid LM40A 마이크로 연동펌프 — 박스형 컨트롤러 일체형, 0.1~400 rpm, 속도 분해능 ±0.1 rpm, 유량 0.03~117 mL/min(RZ1030 헤드), 풋스위치·외부 신호·RS485 제어, DC24V, IP31. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 마이크로 연동펌프 LM40A",
"answer":"LM40A는 컨트롤러를 케이스 안에 넣은 박스형 연동펌프로, 0.1 rpm 단위로 속도를 맞추고 키패드·풋스위치·외부 신호·RS485 네 가지 방식으로 운전하는 충전·분주용 소형 펌프입니다.",
"features":[
 "<b>박스형 일체형</b> — 컨트롤러와 펌프헤드가 한 케이스에 들어가 별도 드라이버가 필요 없습니다",
 "속도 <b>0.1 ~ 300 / 400 rpm</b>, 속도 분해능 <b>±0.1 rpm</b>",
 "유량 <b>0.03 ~ 117 mL/min</b> (RZ1030 헤드 · 두께 0.8 mm · 내경 2.54 mm 이하 기준)",
 "<b>풋스위치</b> 로 시동·정지 (키패드 제어 모드에서), 외부 제어 모드에서는 <b>속도 · 방향 · ON/OFF 신호</b> 를 받습니다",
 "<b>RS485</b> 통신 제어 모드 지원 — 상위 시스템에서 속도와 방향을 지정합니다",
 "정·역 전환 가능 — 액체 이송 방향을 CW/CCW 로 바꿉니다",
 "보호 등급 <b>IP31</b>, DC24V ±10% · 최대 18 W, 치수 173 × 105 × 96 mm · 1.45 kg"],
"specs":[
 ["유량 범위 (Flow rate)","0.03 ~ 117 mL/min (RZ1030 헤드)"],
 ["모델 (Model)","LM40A"],
 ["속도 (Speed)","0.1 rpm ~ 300 / 400 rpm"],
 ["속도 분해능 (Speed resolution)","±0.1 rpm"],
 ["적용 펌프헤드 (Pump head)","RZ1030 (두께 0.8 mm · 내경 ≤2.54 mm · 최대 400 rpm)"],
 ["풋스위치 입력 (Foot pedal)","시동·정지 제어 (키패드 제어 모드 전용)"],
 ["속도 신호 입력 (Speed signal)","다중 속도 신호 지원 (외부 제어 모드 전용)"],
 ["방향 신호 입력 (Direction)","다중 방향 신호 지원 (외부 제어 모드 전용)"],
 ["ON/OFF 신호 입력 (ON/OFF)","다중 ON/OFF 신호 지원 (외부 제어 모드 전용)"],
 ["통신 (Communication)","RS485 (통신 제어 모드 전용)"],
 ["전원 (Power supply)","DC24V ±10% · 최대 18 W"],
 ["사용 환경 (Environment)","0 ~ 40℃ · 상대습도 80% 미만 · 비결로"],
 ["보호 등급 (Protection)","IP31"],
 ["치수 L×W×H (Dimension)","173 × 105 × 96 mm"],
 ["순중량 (Net weight)","1.45 kg"]],
"variants":TUBE,"buybox":[],
"related":PREL(' · <a href="/brands/runze/lm80c-intelligent-large-flow-peristaltic-pump/">LM80C 대유량 연동펌프</a> · <a href="/brands/runze/miniature-peristaltic-pump/">미니어처 연동펌프 헤드 RZ1030-4</a> · <a href="https://www.runzefluid.com/uploads/file/lm40a-intelligent-filling-peristaltic-pump-instruction-manual.pdf" rel="nofollow">LM40A 매뉴얼 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=_mdR4t1rHXw" rel="nofollow">LM40A 제조사 소개 영상</a>'),
"keywords":PKW+[["#충전펌프","/product/"],["#속도제어","/product/"],["#풋스위치","/product/"]],
"sections":[
 {"h":"제조사 신형 자료 — YZ 펌프헤드 구성","html":"<p>제조사 신형 브로슈어는 LM40A 박스형 연동펌프에 <b>YZ1515S · YZ2515S</b> 펌프헤드(3롤러 / 6롤러 선택)를 얹은 구성을 함께 안내합니다. 이 구성에서는 속도 0.1 ~ 400 rpm, 유량 최대 1295 mL/min, RS232 / RS485 통신 제어, 스테인리스 로터, CE 인증, 풋스위치 지원으로 표기합니다. 위 사양표는 RZ1030 헤드 기준이므로 헤드 구성에 따라 유량 범위가 크게 달라집니다.</p>"
  +figs([(D(s,i),c) for i,c in [(3,"LM40A 박스형 연동펌프 제품 파라미터 — YZ1515S / YZ2515S 헤드 구성"),
    (1,"펌프헤드·로터 수별 최대 참고 유량표와 YZ1515S-3 로터 유량 곡선"),
    (2,"YZ1515S-6 · YZ2515S-3 · YZ2515S-6 로터 유량 곡선"),
    (0,"휴대형 박스 타입 · 57 스텝모터 · 스테인리스 로터 · 풋스위치 지원")]])},
 {"h":"제조사 자료 (Reference)","html":figs([(D(s,i),"LM40A 제조사 자료") for i in range(4,len(META[s]["det"]))])},
 {"h":"용도 (Applications)","html":"<ul><li>소량 충전 · 분주 (Filling · dispensing)</li><li>실험실 시약 정량 이송</li><li>온라인 분석기 시료 공급</li></ul>"}],
"faq":[
 {"tag":"제어","q":"LM40A는 어떻게 조작하나요?","a":"키패드 제어, 풋스위치 제어, 외부 신호 제어, RS485 통신 제어 네 가지 모드가 있습니다. 풋스위치는 키패드 모드에서만, 외부 속도·방향·ON/OFF 신호는 외부 제어 모드에서만 동작합니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"RZ1030 헤드 기준 0.03~117 mL/min입니다. 제조사 신형 자료의 YZ1515S·YZ2515S 헤드 구성에서는 최대 1295 mL/min까지 표기됩니다."},
 {"tag":"정밀도","q":"속도를 얼마나 세밀하게 맞출 수 있나요?","a":"±0.1 rpm 단위입니다. 0.1 rpm부터 400 rpm까지 설정합니다."},
 {"tag":"방향","q":"역방향으로 돌릴 수 있나요?","a":"CW와 CCW를 바꿀 수 있습니다. 외부 제어 모드에서는 방향 신호로도 전환합니다."},
 {"tag":"전원","q":"전원은 무엇인가요?","a":"DC24V ±10%이고 최대 소비전력은 18 W입니다."},
 {"tag":"보호","q":"방진·방수 등급은?","a":"IP31입니다. 물이 튀는 환경에는 별도 보호가 필요합니다."},
 {"tag":"헤드","q":"펌프헤드는 무엇을 쓰나요?","a":"기본 사양은 RZ1030 헤드이며 두께 0.8 mm, 내경 2.54 mm 이하 튜브를 400 rpm까지 씁니다. 대유량이 필요하면 YZ 계열 헤드 구성을 검토합니다."}],
"ld":{"name":"Runze Fluid 마이크로 연동펌프 LM40A","sku":"LM40A","category":"연동펌프 · 컨트롤러 일체형",
 "description":"박스형 컨트롤러 일체형 마이크로 연동펌프. 0.1~400 rpm, 속도 분해능 ±0.1 rpm, 0.03~117 mL/min(RZ1030 헤드), 풋스위치·외부 신호·RS485 제어, DC24V, IP31.",
 "models":["LM40A"],"count":1},
"source":SRCU("micro-peristaltic-pump")})
add(P)
