# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
P=[]
s="precision-dispense-piston-pump"
P.append({
"slug":"precision-dispense-piston-pump","name":"정밀 분주 피스톤 펌프 RP-01","name_en":"Runze Fluid RP-01 Precision Dispense Piston Pump",
"sub":"6 mL · 단공 / 이중공 밸브헤드 · 엔코더 · 드라이버 · 솔레노이드 밸브 조합 9종 · 세라믹 습부",
"category":"시린지 펌프 · 마이크로 플런저 펌프",
"title":"Runze Fluid 정밀 분주 피스톤 펌프 RP-01 — 6 mL 세라믹 밸브헤드 정량 펌프 | 실험셋업연구소",
"desc":"Runze Fluid RP-01 정밀 분주 피스톤 펌프 — 6 mL, 분해능 0.005 mm / 1.5707 µL, 최대 500 rpm, 압력 0.075-0.2 MPa, 습부 PC·세라믹·PTFE, 단공/이중공 밸브헤드와 엔코더·드라이버·솔레노이드 밸브 조합 9종. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 정밀 분주 피스톤 펌프 RP-01",
"answer":"RP-01은 6 mL 정량을 1.5707 µL 단위로 밀어내는 피스톤 펌프로, 단공·이중공 밸브헤드에 엔코더·드라이버·솔레노이드 밸브를 붙이고 빼는 조합 9종으로 장비 사양에 맞춰 고릅니다.",
"features":[
 "용량 <b>6 mL</b>, 분해능 <b>0.005 mm / 1.5707 µL</b>, 반복 정밀도 0.3~0.7%(스트로크 100%)",
 "최대 <b>500 rpm</b>, 정격 스트로크 주행 2.292 s ~ 1146 s",
 "밸브헤드 <b>단공(single hole) · 이중공(double hole)</b> 선택",
 "습부는 <b>PC · 세라믹 · PTFE</b>, 연결부는 1/4-28 UNF 암나사입니다",
 "압력 <b>0.075 ~ 0.2 MPa</b> — 저압 정량 분주 구간입니다",
 "<b>엔코더 · 드라이버 · 솔레노이드 밸브</b> 를 넣고 빼는 조합으로 총 9개 모델이 있습니다",
 "35 스텝모터(1.8°, 홀딩 토크 350 mN·m) 구동, DC24V / 1.5A · 15 W · 보증 1년(제조사 표기)"],
"specs":[
 ["습부 재질 (Wetted material)","PC · 세라믹 · PTFE"],
 ["용량 (Volume)","6 mL"],
 ["분해능 (Resolution)","0.005 mm / 1.5707 µL"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% (스트로크 100%)"],
 ["최대 속도 (Max speed)","500 rpm"],
 ["주행 시간 (Running time)","2.292 s ~ 1146 s (정격 스트로크)"],
 ["압력 (Pressure)","0.075 ~ 0.2 MPa"],
 ["밸브헤드 (Valve head)","단공 · 이중공 (밸브 포함)"],
 ["연결부 (Connection)","1/4-28 UNF 암나사"],
 ["모터 (Motor)","35 스텝모터 · 스텝 각도 1.8°"],
 ["전원 (Power supply)","DC24V / 1.5A · 15 W"],
 ["동작 온도 (Operating temp)","5 ~ 55℃"],
 ["보증 (Warranty)","1년 (제조사 표기)"],
 ["커스터마이즈 (Customization)","OEM 대응"]],
"variants":{"heading":"모델 구성 9종 (Model)","head":["모델","밸브헤드","용량","드라이버","엔코더","솔레노이드 밸브"],
 "rows":[["ZSB-RP01-LS-1.8-1-6-2","이중공","6 mL","−","−","−"],
  ["ZSB-RP01-LS-1.8-1-6-F-2","이중공","6 mL","−","−","○"],
  ["ZSB-RP01-LS-1.8-1-6-M-2","이중공","6 mL","−","○","−"],
  ["ZSB-RP01-LS-1.8-1-6-M-F-2","이중공","6 mL","−","○","○"],
  ["ZSB-RP01-LS-1.8-1-6-M-Q-2","이중공","6 mL","○","○","−"],
  ["ZSB-RP01-LS-1.8-1-6-M-Q-F-2","이중공","6 mL","○","○","○"],
  ["ZSB-RP01-LS-1.8-1-6-1","단공","6 mL","−","−","−"],
  ["ZSB-RP01-LS-1.8-1-6-M-1","단공","6 mL","−","○","−"],
  ["ZSB-RP01-LS-1.8-1-6-M-Q-1","단공","6 mL","○","○","−"]],
 "note":"코드 끝자리 1 은 단공 밸브, 2 는 이중공 밸브를 뜻합니다. M 은 엔코더, Q 는 드라이버, F 는 솔레노이드 밸브 포함을 뜻하며 단공 구성에는 솔레노이드 밸브가 들어가지 않습니다."},
"buybox":[],
"related":REL(' · <a href="/brands/runze/stepper-motor-syringe-pump/">스텝모터 플런저 펌프 RPM-01</a> · <a href="/brands/runze/rp42-industrial-micro-syringe-pump/">산업용 마이크로 플런저 펌프 RP42</a> · <a href="https://www.runzefluid.com/uploads/file/rp-01-piston-pump.pdf" rel="nofollow">RP-01 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/rp-01-piston-pump-v1-1.pdf" rel="nofollow">RP-01 매뉴얼 V1.1 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=_eMEbl_F3Kc" rel="nofollow">RP-01 제조사 소개 영상</a>'),
"keywords":KW+[["#피스톤펌프","/product/"],["#정밀분주","/product/"],["#의료분석장비","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-RP01-LS-1.8-1-6-□-□</b> 형태입니다. <b>1.8</b> 은 스텝 각도, <b>1</b> 은 리드 1 mm, <b>6</b> 은 6 mL 용량, 그 다음이 옵션(M 엔코더 · Q 드라이버 · F 솔레노이드 밸브), 마지막이 채널(1 단공 · 2 이중공)입니다.</p>"+figs([(D(s,0),"모델 번호 구성 — 스텝 각도 · 리드 · 용량 · 엔코더/드라이버/솔레노이드 밸브 · 채널")])},
 {"h":"드라이버 포트 핀 배열 (Driver port)","html":"<p>H · L 이 CANH · CANL, A · B 가 RS485A · RS485B, GND · RXD · TXD 가 RS232, − · + 가 DC24V 입니다. 반대편은 A+/A− · B+/B− 모터 상 배선, IO1(NC), IO2 · IO3 엔코더 A/B상, IO4 포토커플러, +5V, PE, GND 입니다.</p>"+figs([(D(s,1),"드라이버 포트 배치 — RS232 · 전원 · 표시등")])},
 {"h":"전기 사양 (Electrical parameters)","html":"<p><b>35 스텝모터</b> — 최대 출력 10.8 W, 스텝 각도 1.8°, 정격 전압 3.6 V, 정격 전류 1.5 A, 홀딩 토크 350 mN·m, 저항 2.4 Ω ±0.24 Ω, 인덕턴스 3.6 mH, 구동 토크 12 mN·m, 회전 관성 43 g·cm², 절연 100 Ω MIN, 최고 온도 80℃, 절연 등급 B. 출력 전류는 모터 정격 전류를 넘기지 않아야 합니다.</p>"
  "<p><b>솔레노이드 밸브</b> — 동작 전압 24V ±10%, 기동 전류 154 mA, 정상 전류 42 mA, 기동 소비전력 3.7 W, 정상 소비전력 1 W 미만, 허용 누설 전류 4 mA, 절연 저항 100 MΩ MIN, 적색 LED 표시등, 서지 흡수 다이오드 내장.</p>"},
 {"h":"외형 치수 (Dimension, unit: mm)","html":"<p>단채널·L형 이중채널·솔레노이드 이중공 구성별로 치수가 다르며 마운팅 홀은 2-3.5 입니다.</p>"
  +figs([(D(s,i),"구성별 외형 치수 도면 (제조사 자료)") for i in range(2,len(META[s]["det"]))])},
 {"h":"용도 (Applications)","html":"<ul><li>미생물 검출 (Micro biology detection)</li><li>의료 분석 시스템 (Medical analysis)</li><li>마이크로리터~밀리리터 정량 분주</li></ul>"}],
"faq":[
 {"tag":"모델","q":"RP-01은 모델이 왜 아홉 개인가요?","a":"밸브헤드가 단공·이중공 두 가지이고, 여기에 엔코더(M)·드라이버(Q)·솔레노이드 밸브(F)를 넣고 빼는 조합이 붙기 때문입니다. 단공 구성에는 솔레노이드 밸브가 들어가지 않습니다."},
 {"tag":"정밀도","q":"1 스텝에 얼마나 나오나요?","a":"0.005 mm 이동에 1.5707 µL입니다. 반복 정밀도는 스트로크 100% 기준 0.3~0.7%입니다."},
 {"tag":"압력","q":"압력 정격은 얼마인가요?","a":"0.075~0.2 MPa입니다. 저압 정량 분주용이라 고압 라인에는 맞지 않습니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"PC, 세라믹, PTFE입니다. 연결부는 1/4-28 UNF 암나사입니다."},
 {"tag":"모터","q":"모터 사양은 어떻게 되나요?","a":"35 스텝모터로 스텝 각도 1.8°, 정격 3.6 V / 1.5 A, 홀딩 토크 350 mN·m, 구동 토크 12 mN·m입니다."},
 {"tag":"엔코더","q":"엔코더는 꼭 필요한가요?","a":"위치 되먹임이 필요 없는 단순 반복 분주라면 없는 구성으로도 됩니다. 탈조 감시나 위치 확인이 필요하면 M이 붙은 구성을 고릅니다."},
 {"tag":"보증","q":"보증 기간은 얼마인가요?","a":"제조사 표기 기준 1년입니다."}],
"ld":{"name":"Runze Fluid 정밀 분주 피스톤 펌프 RP-01","sku":"RP-01","category":"시린지 펌프 · 마이크로 플런저 펌프",
 "description":"6 mL 정밀 분주 피스톤 펌프. 분해능 0.005 mm/1.5707 µL, 최대 500 rpm, 0.075-0.2 MPa, 습부 PC·세라믹·PTFE, 단공/이중공 밸브헤드에 엔코더·드라이버·솔레노이드 밸브 조합 9종.",
 "models":["RP-01"],"count":9},
"source":SRCU("precision-dispense-piston-pump")})
add(P)
