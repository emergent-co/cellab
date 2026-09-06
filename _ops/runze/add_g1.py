# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from helper23 import tbl,gal,figs,dets,add,KW,SRCU,REL,META

P=[]

# ---------------- SY-06B ----------------
P.append({
"slug":"syringe-pump-sy-06b","name":"시린지 펌프 SY-06B","name_en":"Runze Fluid Syringe Pump SY-06B",
"sub":"60 mm 스트로크 · M01~M12 분배 밸브 선택 · 밸브 전환 ≤280 ms · RS232 / RS485 / CAN",
"category":"시린지 펌프 · 밸브 일체형 모듈",
"title":"Runze Fluid 시린지 펌프 SY-06B — 60mm 스트로크 밸브 일체형 정량 펌프 | 실험셋업연구소",
"desc":"Runze Fluid 시린지 펌프 SY-06B — 정격 스트로크 60 mm(6000 스텝), 선속도 0.005~30 mm/s, M01~M12 분배 밸브 선택, 습부 붕규산 유리·PCTFE·사파이어·PTFE, 최대 0.7 MPa. RS232/RS485/CAN. 가격 문의.",
"images":gal("syringe-pump-sy-06b"),
"image_alt":"Runze Fluid 시린지 펌프 SY-06B",
"answer":"시린지 펌프 SY-06B는 정격 스트로크 60 mm에 분배 밸브를 얹은 밸브 일체형 시린지 펌프 모듈로, 마이크로리터에서 밀리리터까지 자동 피펫팅·희석·분주를 상위 컴퓨터 제어로 수행합니다.",
"features":[
 "정격 스트로크 <b>60 mm · 6000 스텝(표준 모드)</b> — 스텝당 분해능 0.01 mm입니다",
 "선속도 <b>0.005 ~ 30 mm/s</b>, 정격 스트로크 주행 시간 <b>2 s ~ 12000 s</b>(매질 물)로 극저맥동 정량이 가능합니다",
 "분배 밸브를 <b>M01 · M02 · M03 · M04 · M05 · M06 · M10 · M12</b> 중에서 골라 조합합니다 — 인접 포트 간 전환 시간 ≤280 ms",
 "습부는 <b>붕규산 유리 · PCTFE · 사파이어 · PTFE</b> 로 금속이 없습니다 — 최대 압력 0.7 MPa",
 "구동부는 <b>사다리꼴 나사(리드 2 mm)</b> 이며 <b>TTL 3채널</b> 입력을 받습니다",
 "<b>RS232 / RS485 / CAN</b> 제어 — 주소와 파라미터를 통신으로 설정하고 여러 대를 직렬로 연결해 쓸 수 있습니다",
 "제조사는 SY-06B를 <b>60 mm 스트로크 · 마이크로 스테핑 구동</b> 사양의 CX 계열 대체 모델로 안내합니다 (최대 25 mL 정량)"],
"specs":[
 ["습부 재질 (Wetted material)","붕규산 유리 · PCTFE · 사파이어 · PTFE (Borosilicate glass, PCTFE, Sapphire, PTFE)"],
 ["정격 스트로크 (Rated stroke)","60 mm · 6000 스텝 (표준 모드)"],
 ["분해능 (Resolution)","0.01 mm / 스텝"],
 ["선속도 (Linear speed)","0.005 ~ 30 mm/s"],
 ["주행 시간 (Running time)","2 s ~ 12000 s (정격 스트로크 · 매질 물)"],
 ["밸브 모델 (Valve model)","M01 · M02 · M03 · M04 · M05 · M06 · M10 · M12"],
 ["밸브 전환 시간 (Valve switching)","≤280 ms (인접 포트 간)"],
 ["구동부 (Actuator)","사다리꼴 나사 · 리드 2 mm (Trapezoidal screw)"],
 ["입력 신호 (Input signal)","TTL 3채널 (3 channels TTL)"],
 ["연결부 (Connection)","1/4-28 UNF"],
 ["최대 압력 (Max pressure)","0.7 MPa"],
 ["통신 (Communication)","RS232 / RS485 / CAN"],
 ["통신 속도 (Baud rate)","RS232/RS485 9600 · 19200 · 38400 · 57600 · 115200 bps<br>CAN 100K · 200K · 500K · 1M bps"],
 ["주소 설정 (Address setting)","통신으로 설정 (Via communication)"]],
"buybox":[],
"related":REL(' · <a href="/brands/runze/gastight-syringe/">기밀 시린지</a> · <a href="/brands/runze/selector-valve-sv-07/">셀렉터 밸브 SV-07</a>'),
"keywords":KW+[["#시린지펌프","/product/"],["#정량펌프","/product/"],["#밸브일체형","/product/"]],
"sections":[
 {"h":"모델 번호 체계 (Model number)","html":"<p>주문 코드는 <b>ZSB-SY06B-60-M□□</b> 형태로, <b>60</b> 은 정격 스트로크 60 mm, <b>M□□</b> 는 조합할 분배 밸브 모델(M01~M12)을 뜻합니다.</p>"+figs([(META["syringe-pump-sy-06b"]["det"][0],"모델 번호 구성 — Model No. · Rated stroke 60 mm · Valve model")])},
 {"h":"분배 밸브 유로 구성 (Valve options)","html":"<p>C 포트가 시린지에 연결되는 공통 포트입니다. 밸브 모델에 따라 유로 논리가 달라집니다.</p><ul>"
  "<li><b>M01</b> — Y 유로 (C-1 / 1-2 / C-2 연동)</li>"
  "<li><b>M02</b> — T 유로 (C-1-2 / C-1 / 1-2 / C-2 연동)</li>"
  "<li><b>M03</b> — 분배 유로 (C-1 / C-2 / C-3 연동)</li>"
  "<li><b>M04</b> — 라디오 유로 (C-1 / 1-2 / 2-3 / C-3 연동)</li>"
  "<li><b>M05</b> — 바이패스 유로 (C-1 / 2-3 연동, C-3 / 1-2 연동)</li>"
  "<li><b>M06 · M10 · M12</b> — 분배 유로 (C 가 1~6 / 1~9 / 1~12 포트에 선택 연결)</li></ul>"
  +figs([(META["syringe-pump-sy-06b"]["det"][3],"밸브 모델별 유로 논리 M01~M05"),
         (META["syringe-pump-sy-06b"]["det"][4],"밸브 모델별 유로 논리 M06 · M10 · M12"),
         (META["syringe-pump-sy-06b"]["det"][5],"적용 가능한 기밀 시린지 규격 — 정격 스트로크 60 mm 기준")])},
 {"h":"제품 사진 (Product)","html":figs([(META["syringe-pump-sy-06b"]["det"][1],"SY-06B 외형 (제조사 자료)"),
         (META["syringe-pump-sy-06b"]["det"][2],"SY-06B 외형 (제조사 자료)")])},
 {"h":"용도 (Applications)","html":"<p>마이크로리터~밀리리터 구간의 정밀 액체 이송에 씁니다.</p><ul><li>자동 피펫팅 · 희석 · 분주 (Automatic pipetting, dilution, dispensing)</li><li>의료 분석 장비 (Medical analysis equipment)</li><li>실험실 자동화 · 전처리 장비</li><li>온라인 수질 분석기</li></ul>"}],
"faq":[
 {"tag":"사양","q":"SY-06B의 정격 스트로크와 분해능은 어떻게 되나요?","a":"정격 스트로크 60 mm에 표준 모드 6000 스텝이며, 스텝당 분해능은 0.01 mm입니다."},
 {"tag":"속도","q":"주입 속도는 어디까지 조절되나요?","a":"선속도 0.005~30 mm/s이고, 정격 스트로크를 주행하는 데 2초에서 12000초까지 걸리도록 설정할 수 있습니다(매질 물 기준)."},
 {"tag":"밸브","q":"밸브 모델 M01~M12는 무엇이 다른가요?","a":"유로 논리가 다릅니다. M01은 Y 유로, M02는 T 유로, M03·M04·M05는 3포트 분배·라디오·바이패스 유로이고, M06·M10·M12는 공통 포트가 각각 6·9·12 포트에 선택 연결되는 분배 유로입니다."},
 {"tag":"재질","q":"습부 재질은 무엇인가요?","a":"붕규산 유리, PCTFE, 사파이어, PTFE입니다. 최대 압력 정격은 0.7 MPa입니다."},
 {"tag":"제어","q":"어떤 통신으로 제어하나요?","a":"RS232 · RS485 · CAN을 지원합니다. RS232/RS485는 9600~115200 bps, CAN은 100 Kbps~1 Mbps이며 TTL 3채널 입력도 받습니다."},
 {"tag":"확장","q":"여러 대를 같이 쓸 수 있나요?","a":"직렬로 연결해 여러 대를 함께 제어할 수 있습니다. 주소와 파라미터는 통신으로 설정합니다."},
 {"tag":"소모품","q":"시린지는 어떤 규격을 쓰나요?","a":"정격 스트로크 60 mm 규격의 기밀 시린지를 씁니다. 25 µL부터 250 µL 이상까지 용량별로 선택합니다."}],
"ld":{"name":"Runze Fluid 시린지 펌프 SY-06B","sku":"SY-06B","category":"시린지 펌프 · 밸브 일체형 모듈",
 "description":"정격 스트로크 60 mm(6000 스텝) 밸브 일체형 시린지 펌프. 선속도 0.005~30 mm/s, M01~M12 분배 밸브, 습부 붕규산 유리·PCTFE·사파이어·PTFE, 0.7 MPa, RS232/RS485/CAN.",
 "models":["SY-06B"],"count":8},
"source":SRCU("syringe-pump-sy-06b")})

add(P)
