# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import gal,figs,add,KW,SRCU,REL,META
D=lambda s,i:META[s]["det"][i]
BAUD="RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"
P=[]

# ---------------- SY-08 ----------------
s="Syringe Pump-sy-08"; g=gal(s)
P.append({
"slug":"syringe-pump-sy-08","name":"시린지 펌프 SY-08","name_en":"Runze Fluid Syringe Pump SY-08",
"sub":"5 / 12.5 / 25 mL · 정격 스트로크 30 mm(12000 스텝) · 42×42 mm 슬림 바디 · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
"title":"Runze Fluid 시린지 펌프 SY-08 — 5·12.5·25 mL 산업용 정밀 시린지 펌프 | 실험셋업연구소",
"desc":"Runze Fluid 시린지 펌프 SY-08 — 5 / 12.5 / 25 mL, 정격 스트로크 30 mm(12000 스텝), 분해능 0.416~2.083 µL, 습부 붕규산 유리·PCTFE·PTFE, 정압 0-0.8 MPa, RS232/RS485/CAN. 가격 문의.",
"images":g,"image_alt":"Runze Fluid 시린지 펌프 SY-08",
"answer":"시린지 펌프 SY-08은 42×42 mm 단면의 슬림 바디에 5·12.5·25 mL 시린지를 물리는 산업용 정밀 시린지 펌프로, 정격 스트로크 30 mm를 12000 스텝으로 나눠 마이크로리터 단위 액체를 이송합니다.",
"features":[
 "용량 <b>5 mL · 12.5 mL · 25 mL</b> 세 가지 — 정격 스트로크는 모두 30 mm(12000 스텝)입니다",
 "유량 정확도 <b>≤1%</b>, 반복 정밀도 <b>0.3~0.7%</b> (정격 스트로크 100% 기준)",
 "수명 <b>무누출 300만 회</b> — 정격 스트로크 1회를 1회로 세고 매질은 순수입니다",
 "습부는 <b>붕규산 유리 실린더 · PCTFE 밸브헤드 · PTFE 피스톤</b> 으로 강산·강염기(98% 황산 등) 이송이 가능합니다",
 "최대 피스톤 구동력 <b>≥100 N</b>, 구동부는 사다리꼴 나사(리드 1 mm)입니다",
 "단면 <b>42×42 mm</b> 로 좁은 장비 안에도 세워 넣기 좋습니다 — 순중량 0.56~0.66 kg",
 "<b>RS232 / RS485 / CAN</b> 제어, 주소·파라미터를 통신으로 설정합니다"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PCTFE 밸브헤드 · PTFE 피스톤"],
 ["유량 정확도 (Accuracy)","≤1% @100% 정격 스트로크"],
 ["반복 정밀도 (Repeatability)","0.3 ~ 0.7% @100% 정격 스트로크"],
 ["수명 (Service life)","무누출 300만 회 (매질 물)"],
 ["정격 스트로크 (Rated stroke)","30 mm · 12000 스텝"],
 ["최대 피스톤 힘 (Piston drive)","≥100 N"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 1 mm"],
 ["최대 압력 (Max pressure)","정압 0-0.8 MPa · 부압 0-0.06 MPa (유지 시간은 시험 기준)"],
 ["채널 (Channel)","단일 채널 (Single channel)"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["통신 속도 (Baud rate)",BAUD],
 ["주소 설정 (Address setting)","통신으로 설정 (Via communication)"],
 ["전원 (Power supply)","DC24V / 3A · 최대 15 W"],
 ["동작 온도 (Operating temp)","5℃ ~ 55℃"],
 ["동작 습도 (Operating humidity)","상대습도 80% 이하 · 비결로"]],
"variants":{"heading":"용량별 규격 (Volume)","head":["항목","5 mL","12.5 mL","25 mL"],
 "rows":[["최대 회전수 (Max speed)","600 rpm","600 rpm","500 rpm"],
  ["선속도 (Linear speed)","0.017-10 mm/s","0.017-10 mm/s","0.017-8.33 mm/s"],
  ["주행 시간 (Running time)","3-1800 s","3-1800 s","3.6-1800 s"],
  ["분해능 (Resolution)","0.0025 mm / 0.416 µL","0.0025 mm / 1.042 µL","0.0025 mm / 2.083 µL"],
  ["시린지 내경 (Syringe ID)","14.55 mm","23.03 mm","32.57 mm"],
  ["치수 L×W×H (Dimension)","42×42×192.8 mm","42×42×201.8 mm","42×42×201.8 mm"],
  ["순중량 (Net weight)","0.56 kg","0.62 kg","0.66 kg"]],
 "note":"제조사 신형 브로슈어는 25 mL 최대 회전수를 450 rpm, 순중량을 0.53 / 0.58 / 0.63 kg, 정격 전원을 DC24V/1.5A 로 표기하고 배압을 1.32 / 0.51 / 0.28 MPa 로 추가 명시합니다. 습부에는 PVDF 나사 포트와 FFKM 실링을 포함합니다."},
"buybox":[],
"related":REL(' · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="https://www.runzefluid.com/uploads/file/sy-08.pdf" rel="nofollow">SY-08 카탈로그 (제조사 PDF)</a> · <a href="https://www.runzefluid.com/uploads/file/sy-08-syringe-pump-ascii-v1-6.pdf" rel="nofollow">SY-08 ASCII 통신 매뉴얼 V1.6 (제조사 PDF)</a> · <a href="https://www.youtube.com/watch?v=mYFD3WrbIGM" rel="nofollow">SY-08 제조사 소개 영상</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#정밀분주","/product/"],["#산업용시린지펌프","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB08-LS-0.9-1-□-1-Q</b> 형태입니다. <b>0.9</b> 는 스텝 각도, 그 다음 <b>1</b> 은 나사 리드 1 mm, <b>□</b> 는 용량(5 · 12.5 · 25), 마지막 <b>1</b> 은 단일 채널, <b>Q</b> 는 드라이버 포함을 뜻합니다.</p>"+figs([(D(s,0),"모델 번호 구성 — Model No. · 스텝 각도 · 나사 리드 · 용량 · 채널 · 드라이버")])},
 {"h":"제조사 기술 사양표 (Technical parameters)","html":figs([(D(s,1),"SY-08 정밀 마이크로 시린지 펌프 — 컴팩트 · 내산내알칼리"),(D(s,2),"제조사 기술 파라미터 표 (용량별 배압 · 속도 · 분해능 포함)")])},
 {"h":"수명 · 내식성 (Service life & chemical resistance)","html":figs([(D(s,3),"무누출 300만 회 — 상온 상압 순수 이송 자체 시험 결과"),(D(s,4),"한 손에 들어오는 크기와 무게"),(D(s,5),"98% 황산 등 강산·강염기 이송 · PVDF 나사 포트")])},
 {"h":"밸브 옵션 · 외형 치수 (Valve options & dimensions)","html":figs([(D(s,i),"밸브 옵션 · 외형 치수 도면 (제조사 자료)") for i in range(6,len(META[s]["det"]))])},
 {"h":"용도 (Applications)","html":"<p>미량 액체를 정밀하게 옮겨야 하는 분석·검사 장비에 씁니다.</p><ul><li>환경 분석 기기 (Environmental analysis instruments)</li><li>의료 분석 장비 (Medical analysis instruments)</li><li>고정밀 비표준 샘플링 설비</li></ul>"}],
"faq":[
 {"tag":"용량","q":"SY-08은 어떤 용량이 있나요?","a":"5 mL, 12.5 mL, 25 mL 세 가지입니다. 정격 스트로크는 모두 30 mm(12000 스텝)이고 시린지 내경만 14.55 / 23.03 / 32.57 mm로 달라집니다."},
 {"tag":"정밀도","q":"한 스텝에 얼마나 나오나요?","a":"5 mL은 0.416 µL, 12.5 mL은 1.042 µL, 25 mL은 2.083 µL입니다. 스텝당 이동 거리는 모두 0.0025 mm입니다."},
 {"tag":"재질","q":"강산도 이송할 수 있나요?","a":"습부가 붕규산 유리 실린더, PCTFE 밸브헤드, PTFE 피스톤이라 98% 황산 같은 강산·강염기도 이송할 수 있습니다. 불산과 이 재질들과 반응하는 액체는 피해야 합니다."},
 {"tag":"압력","q":"압력 정격은 어떻게 되나요?","a":"정압 0-0.8 MPa, 부압 0-0.06 MPa입니다. 유지 시간은 시험 조건에 따라 달라집니다."},
 {"tag":"수명","q":"수명은 얼마나 되나요?","a":"제조사 자체 시험에서 상온 상압 순수 기준 무누출 300만 회입니다. 정격 스트로크 1회를 1회로 셉니다."},
 {"tag":"설치","q":"장비에 넣기에 크기가 어떤가요?","a":"단면이 42×42 mm이고 높이는 192.8~201.8 mm, 무게는 0.56~0.66 kg입니다."},
 {"tag":"제어","q":"어떤 통신을 지원하나요?","a":"RS232, RS485, CAN을 지원합니다. RS232/RS485는 9600~115200 bps, CAN은 100 Kbps~1 Mbps입니다."}],
"ld":{"name":"Runze Fluid 시린지 펌프 SY-08","sku":"SY-08","category":"시린지 펌프 · 산업용 정밀 시린지 펌프",
 "description":"5/12.5/25 mL 산업용 정밀 시린지 펌프. 정격 스트로크 30 mm(12000 스텝), 분해능 0.416~2.083 µL, 습부 붕규산 유리·PCTFE·PTFE, 정압 0-0.8 MPa, RS232/RS485/CAN.",
 "models":["SY-08-5ML","SY-08-12.5ML","SY-08-25ML"],"count":3},
"source":SRCU("Syringe%20Pump-sy-08")})

add(P)
