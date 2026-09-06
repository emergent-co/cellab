# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]
TUBE3=("<ul><li><b>실리콘</b> — 식품 등급 · −4℃ ~ +180℃ · 비부식성 액체 · 수명 200시간 이상</li>"
 "<li><b>PharMed BPT</b> — Saint-Gobain · FDA 규격 · −51℃ ~ +132℃ · 약산·약염기 · 1000시간 이상</li>"
 "<li><b>Viton</b> — MasterFlex · FDA 규격 · −20℃ ~ +260℃ · 강산·강염기 · 1000시간 이상</li></ul>"
 "<p>수명은 상온 20℃·무가압에서 순수를 연속 이송해 균열이 생길 때까지를 잰 값입니다. 회전수가 낮고 액성이 순할수록 길어집니다.</p>")

# ---- SR400 ----
s="peristaltic-pump-price"
P.append({
"slug":"sr400-peristaltic-pump","name":"탁상형 연동펌프 SR400","name_en":"Runze Fluid SR400 Peristaltic Pump",
"sub":"AC110-240V 탁상형 · 스텝모터 0-400 rpm · 0-1700 mL/min · 풋 페달 · YZ / SN 헤드 선택",
"category":"연동펌프 · 탁상형",
"title":"Runze Fluid 탁상형 연동펌프 SR400 — 풋 페달 지원 대유량 실험실 펌프 | 실험셋업연구소",
"desc":"Runze Fluid SR400 탁상형 연동펌프 — AC110-240V, 스텝모터 0-400 rpm, 유량 0-1700 mL/min, 헤드 YZ1515X / YZ2515X / SN15 / SN25, 스테인리스 3·6롤러, 풋 페달 지원, 301×151.5×233 mm · 5.5 kg. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 탁상형 연동펌프 SR400",
"answer":"SR400은 AC 전원을 그대로 꽂아 쓰는 탁상형 연동펌프로, 앞면 속도 노브와 풋 페달로 조작하며 YZ·SN 헤드를 골라 최대 1700 mL/min 까지 이송합니다.",
"features":[
 "<b>AC110-240V</b> 탁상형 — 별도 전원 장치 없이 바로 씁니다",
 "펌프헤드 <b>YZ1515X · YZ2515X (ABS · 흰색/검정)</b> 또는 <b>SN15 · SN25 (PC · 투명)</b> 선택, 스테인리스 3·6롤러",
 "스텝모터 <b>0 ~ 400 rpm</b>, 유량 <b>0 ~ 1700 mL/min</b>",
 "<b>풋 페달</b> 로 시동·정지 — 손이 자유로워 반복 충전 작업에 편합니다",
 "튜브 ID 1.6-8.0 mm · 두께 1.6-2.5 mm · 외경 11.4 mm 이하, <b>퀵 튜브 장착</b> 지원",
 "압력 정격 최대 2 bar(30 psi), 흡입 양정 5 m · 토출 양정 8 m, 소음 65 dB",
 "치수 301 × 151.5 × 233 mm, 5508 g(3롤러) / 5608 g(6롤러)"],
"specs":[
 ["유량 범위 (Flow rate)","0 ~ 1700 mL/min"],
 ["모델 (Model No.)","SR400-YZ1515X / YZ2515X / SN15 / SN25"],
 ["롤러 (Pump roller)","스테인리스 3롤러 / 6롤러"],
 ["헤드 재질 (Pump head)","ABS 엔지니어링 플라스틱 (YZ) · PC 엔지니어링 플라스틱 (SN)"],
 ["헤드 색상 (Pump color)","흰색 / 검정 (YZ) · 투명 (SN)"],
 ["퀵 튜브 (Fast tubing)","지원"],
 ["모터 (Motor type)","스텝모터"],
 ["회전수 (Motor speed)","0 ~ 400 rpm"],
 ["전원 (Power supply)","AC110-240V"],
 ["튜브 규격 (Tubing size)","ID 1.6-8.0 mm · WT 1.6-2.5 mm · OD ≤11.4 mm"],
 ["튜브 수명 (Tubing life)","실리콘 ≥200 h · BPT 고무 ≥1000 h"],
 ["압력 정격 (Pressure)","최대 2 bar (30 psi)"],
 ["사용 환경 (Environment)","0-40℃ · 상대습도 80% 미만 · 비결로"],
 ["소음 (Max noise)","65 dB"],
 ["흡입 · 양정 (Suction · Head)","흡입 5 m · 양정 8 m"],
 ["치수 L×W×H (Dimension)","301 × 151.5 × 233 mm"],
 ["순중량 (Net weight)","5508 g (3롤러) · 5608 g (6롤러)"]],
"variants":{"heading":"튜브 규격별 유량 (mL/min · 0-400 rpm · YZ1515X)","head":["튜브","ID×WT (mm)","3롤러","6롤러"],
 "rows":[["고무 튜브","1.6 × 1.6","0 - 113","0 - 88"],["고무 튜브","3.2 × 1.6","0 - 462","0 - 347"],
  ["고무 튜브","4.8 × 1.6","0 - 966","0 - 612"],["고무 튜브","6.4 × 1.6","0 - 1447","0 - 804"],
  ["고무 튜브","8.0 × 1.6","0 - 1887","0 - 1332"],
  ["실리콘 튜브","1.6 × 1.6","0 - 117","0 - 92"],["실리콘 튜브","3.2 × 1.6","0 - 491","0 - 375"],
  ["실리콘 튜브","4.8 × 1.6","0 - 1020","0 - 652"],["실리콘 튜브","6.4 × 1.6","0 - 1494","0 - 848"],
  ["실리콘 튜브","8.0 × 1.6","0 - 1700","0 - 1400"]],
 "note":"상온 상압에서 순수를 이송해 잰 값입니다. 매질과 사용 환경에 따라 실제 유량은 달라집니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/peristaltic-dosing-pump/">YZ1515X · YZ2515X 펌프헤드</a> · <a href="/brands/runze/peristaltic-metering-pump/">지능형 정량 연동펌프 LM60A · LM60B</a> · <a href="https://www.runzefluid.com/uploads/file/sr400-peristaltic-pump.pdf" rel="nofollow">SR400 카탈로그 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=lXUtMebT3Js" rel="nofollow">SR400 제조사 소개 영상</a>'),
"keywords":PKW+[["#탁상형연동펌프","/product/"],["#풋페달","/product/"],["#실험실펌프","/product/"]],
"sections":[
 {"h":"풋 페달 사용 순서 (Foot pedal)","html":"<ol>"
  "<li>전원 플러그를 AC110-240V 에 꽂습니다</li>"
  "<li>풋 페달을 펌프 뒷면 인터페이스에 연결합니다</li>"
  "<li>펌프 뒷면 메인 전원 스위치를 켭니다</li>"
  "<li>펌프 앞면 빨간 ON/OFF 버튼을 눌러 시동합니다 — 축이 도는지 확인합니다</li>"
  "<li>앞면 SPEED 노브를 천천히 돌려 속도를 맞춥니다</li></ol>"
  "<p>주의할 점이 넷 있습니다. 시동은 낮은 속도에서 걸어야 하므로 SPEED 노브를 중간 이하(반시계 방향)에 두고 시작합니다. 풋 페달은 앞면 빨간 버튼이 ON 일 때만 동작합니다. 풋 페달을 연결하지 않으면 펌프 앞면 버튼도 기능을 잃습니다. SPEED 조절은 펌프가 도는 중에만 됩니다.</p>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":figs([(D(s,3),"SR400 외형 치수 도면")])},
 {"h":"적용 튜브 (Peristaltic tubing)","html":TUBE3},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"SR400 (제조사 자료)") for i in range(3)])}],
"faq":[
 {"tag":"전원","q":"별도 전원 장치가 필요한가요?","a":"필요 없습니다. AC110-240V를 그대로 꽂아 씁니다."},
 {"tag":"조작","q":"풋 페달은 어떻게 쓰나요?","a":"펌프 뒷면 인터페이스에 연결하고 앞면 빨간 ON/OFF 버튼을 ON으로 둔 상태에서 밟습니다. 빨간 버튼이 OFF면 풋 페달이 동작하지 않습니다."},
 {"tag":"주의","q":"속도 노브를 쓸 때 주의할 점이 있나요?","a":"시동은 낮은 속도에서 걸어야 하므로 노브를 중간 이하에 두고 시작합니다. 속도 조절은 펌프가 도는 중에만 됩니다."},
 {"tag":"유량","q":"유량은 얼마까지 나오나요?","a":"0~1700 mL/min입니다. 실리콘 8.0×1.6 mm 튜브에 3롤러 조합에서 최대입니다."},
 {"tag":"헤드","q":"헤드는 무엇을 고를 수 있나요?","a":"YZ1515X·YZ2515X(ABS)와 SN15·SN25(PC 투명)입니다. 롤러는 3롤러와 6롤러 중에서 고릅니다."},
 {"tag":"차이","q":"LM60A와 SR400 중 어느 쪽인가요?","a":"정량·예약 모드로 반복 분주를 자동화하려면 LM60A, 손과 발로 조작하며 이송량을 눈으로 보고 맞추는 실험실 작업이면 SR400이 편합니다."}],
"ld":{"name":"Runze Fluid 탁상형 연동펌프 SR400","sku":"SR400","category":"연동펌프 · 탁상형",
 "description":"AC110-240V 탁상형 연동펌프. 스텝모터 0-400 rpm, 0-1700 mL/min, YZ1515X/YZ2515X/SN15/SN25 헤드, 스테인리스 3·6롤러, 풋 페달 지원, 5.5 kg.",
 "models":["SR400-YZ1515X","SR400-YZ2515X","SR400-SN15","SR400-SN25"],"count":4},
"source":SRCU("peristaltic-pump-price")})
add(P)
