# -*- coding: utf-8 -*-
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _pcommon import *
P=[]
APPS=("<ul><li>의료 진단 장비 (Medical diagnostics)</li><li>환경 계측기 · 스마트 수질 모니터링</li>"
 "<li>분석기기 (Analytical instruments) · 생화학 분석</li><li>암모니아성 질소 온라인 측정기 · COD 소화 장치</li>"
 "<li>단백질 면역블롯 장비</li><li>잉크 분사 · 세정 장비</li><li>식품·음료 · 실험 연구 · 산업기계 · 스마트 가전</li></ul>")

# ---- BJ-RZ-01 ----
s="small-peristaltic-pump-bj-rz-01"
P.append({
"slug":"small-peristaltic-pump-bj-rz-01","name":"소형 연동펌프 BJ-RZ-01","name_en":"Runze Fluid BJ-RZ-01 Small Peristaltic Pump",
"sub":"RZ-01 헤드 · PPS 롤러 · PC 투명 하우징 · 수입 42 스텝모터 · 토출압 0.2 MPa · 최대 152 mL/min",
"category":"연동펌프 · 스텝모터 일체형",
"title":"Runze Fluid 소형 연동펌프 BJ-RZ-01 — PC 투명 하우징 42 스텝모터 | 실험셋업연구소",
"desc":"Runze Fluid BJ-RZ-01 소형 연동펌프 — RZ-01 헤드(PPS 롤러 · PC 투명 하우징), 수입 42 스텝모터, 토출압 0.2 MPa, 양정 약 20 m, 튜브 두께 0.8 / 1.6 mm, 최대 152 mL/min. OEM 대응. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 소형 연동펌프 BJ-RZ-01",
"answer":"BJ-RZ-01은 PC 투명 하우징의 RZ-01 헤드에 수입 42 스텝모터를 직결한 소형 연동펌프로, 튜브 상태를 눈으로 보면서 0.2 MPa 토출압으로 최대 152 mL/min을 이송합니다.",
"features":[
 "롤러 <b>PPS</b> — 구조 성능이 좋고 내마모성이 있습니다",
 "하우징 <b>PC 투명</b> — 펌프 동작과 튜브 상태를 눈으로 확인합니다. 하우징에 회전 방지 잠금 구조가 있어 장시간 안정적으로 돕니다",
 "<b>수입 42 스텝모터</b> — 저소음 · 고안정 · 긴 수명 · 정밀도 확보",
 "토출압 <b>0.2 MPa</b>, 양정 약 <b>20 m</b>(피에조메트릭 헤드 기준)",
 "튜브 두께 <b>0.8 mm</b> 계열 최대 96 mL/min, <b>1.6 mm</b> 계열 최대 152 mL/min",
 "흡입 범위는 대기압(표준 10.33 m)에서 펌프 캐비테이션 여유 · 튜브 입구 손실 · 안전 여유(0.5) · 매질 캐비테이션 압력을 뺀 값입니다",
 "<b>OEM 대응</b> — 넓은 튜브 규격에 맞춰 헤드를 구성합니다"],
"specs":[
 ["유량 범위 (Flow rate)","최대 96 mL/min (WT 0.8 mm) · 최대 152 mL/min (WT 1.6 mm)"],
 ["모델 (Model No.)","BJ-RZ-01 (RZ-01 헤드)"],
 ["롤러 (Pump roller)","PPS 4롤러"],
 ["하우징 재질 (Housing)","PC (투명)"],
 ["모터 (Motor type)","수입 42 스텝모터"],
 ["토출압 (Outlet pressure)","0.2 MPa"],
 ["양정 (Head)","약 20 m"],
 ["튜브 규격 (Tubing size)","ID 0.64-3.0 mm · WT 0.8 mm · ID 1.6-3.2 mm · WT 1.6 mm"]],
"variants":{"heading":"튜브 규격별 최대 유량 (mL/min · RZ-01)","head":["튜브 두께","내경 (mm)","최대 유량"],
 "rows":[["0.8 mm","0.64 / 0.76 / 0.89 / 1.02 / 1.14 / 1.30 / 1.42","12 / 13 / 16 / 22 / 28 / 34 / 42"],
  ["0.8 mm","1.52 / 1.65 / 1.85 / 2.06 / 2.29 / 2.54 / 2.79","44 / 47 / 60 / 65 / 88 / 90 / 96"],
  ["1.6 mm","1.6 / 2.4 / 3.2","48 / 94 / 152"]],
 "note":"상온 20℃·무가압에서 순수를 이송해 잰 참고값입니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/small-peristaltic-pump-bj-rz-02/">소형 연동펌프 BJ-RZ-02</a> · <a href="/brands/runze/mini-peristaltic-pump/">미니 연동펌프 BJ-RZ1030</a> · <a href="/brands/runze/lm40b-micro-peristaltic-pump/">지능형 충전 연동펌프 LM40B</a>'),
"keywords":PKW+[["#소형연동펌프","/product/"],["#투명하우징","/product/"],["#OEM","/product/"]],
"sections":[
 {"h":"모델명 규칙 (Naming rules)","html":"<p>모델 번호는 <b>고무 튜브 두께</b> 와 <b>롤러 수(4롤러)</b> 를 붙여 표기합니다.</p>"+figs([(D(s,0),"BJ-RZ-01 모델명 구성 규칙")])},
 {"h":"구조 · 튜브 장착 (Structure & installation)","html":"<p>PPS 롤러, 관찰용 PC 하우징, 회전 방지 잠금 구조입니다. 튜브 장착은 7단계로 진행하며 호스에 윤활을 하면 수명이 길어집니다.</p>"
  +figs([(D(s,4),"넓은 규격 대응 구조와 튜브 장착 7단계 — PPS 롤러 · PC 하우징 · 회전 방지 잠금")])},
 {"h":"적용 튜브 · 참고 유량","html":figs([(D(s,5),"RZ-01 적용 호스와 참고 유량표")])},
 {"h":"용도 (Applications)","html":APPS+figs([(D(s,8),"산업별 적용 분야")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"BJ-RZ-01 (제조사 자료)") for i in [1,2,3,6,7,9]])}],
"faq":[
 {"tag":"유량","q":"BJ-RZ-01은 유량이 얼마나 나오나요?","a":"두께 0.8 mm 튜브에서 최대 96 mL/min, 두께 1.6 mm 튜브(내경 3.2 mm)에서 최대 152 mL/min입니다."},
 {"tag":"하우징","q":"하우징이 투명한 이유는?","a":"PC 투명 하우징이라 펌프가 도는 상태와 튜브 상태를 눈으로 바로 확인할 수 있습니다. 회전 방지 잠금 구조도 함께 들어가 있습니다."},
 {"tag":"압력","q":"토출압과 양정은 어떻게 되나요?","a":"토출압 0.2 MPa이고 양정은 약 20 m입니다."},
 {"tag":"흡입","q":"흡입 높이는 어떻게 계산하나요?","a":"대기압(표준 10.33 m)에서 펌프 캐비테이션 여유, 튜브 입구 손실, 안전 여유 0.5, 매질의 캐비테이션 압력을 뺀 값입니다."},
 {"tag":"수명","q":"튜브 수명을 늘리는 방법이 있나요?","a":"호스에 윤활유를 바르면 수명이 길어집니다. 회전수를 낮추고 액성이 순할수록 오래 갑니다."},
 {"tag":"차이","q":"BJ-RZ-01과 BJ-RZ-02는 뭐가 다른가요?","a":"RZ-01은 PC 투명 하우징에 4롤러 고정, RZ-02는 PPS+합성섬유 하우징에 3롤러(대유량)와 6롤러(저맥동)를 고르고 스프링 클립으로 튜브를 갈아 끼웁니다."}],
"ld":{"name":"Runze Fluid 소형 연동펌프 BJ-RZ-01","sku":"BJ-RZ-01","category":"연동펌프 · 스텝모터 일체형",
 "description":"PC 투명 하우징 RZ-01 헤드 소형 연동펌프. PPS 4롤러, 수입 42 스텝모터, 토출압 0.2 MPa, 양정 약 20 m, 최대 152 mL/min.",
 "models":["BJ-RZ-01"],"count":1},
"source":SRCU("small-peristaltic-pump-bj-rz-01")})

# ---- BJ-RZ-02 ----
s="small-peristaltic-pump-bj-rz-02"
P.append({
"slug":"small-peristaltic-pump-bj-rz-02","name":"소형 연동펌프 BJ-RZ-02","name_en":"Runze Fluid BJ-RZ-02 Small Peristaltic Pump",
"sub":"RZ-02 헤드 · PPS 롤러 3 / 6 · 스프링 클립 튜브 장착 · 수입 42 스텝모터 · 최대 236 mL/min",
"category":"연동펌프 · 스텝모터 일체형",
"title":"Runze Fluid 소형 연동펌프 BJ-RZ-02 — 스프링 클립 3·6롤러 42 스텝모터 | 실험셋업연구소",
"desc":"Runze Fluid BJ-RZ-02 소형 연동펌프 — RZ-02 헤드, PPS 롤러 3롤러(대유량)/6롤러(저맥동), PPS+합성섬유 하우징, 스프링 클립으로 튜브 장착, 수입 42 스텝모터, 최대 236 mL/min. OEM 대응. 가격 문의.",
"images":gal(s),"image_alt":"Runze Fluid 소형 연동펌프 BJ-RZ-02",
"answer":"BJ-RZ-02는 스프링 클립으로 튜브를 눌러 고정하는 RZ-02 헤드에 수입 42 스텝모터를 붙인 소형 연동펌프로, 3롤러는 대유량, 6롤러는 저맥동으로 나뉩니다.",
"features":[
 "롤러 <b>PPS</b> — <b>6롤러는 저맥동 안정 토출</b>, <b>3롤러는 대유량</b>",
 "하우징 <b>PPS + 합성섬유</b> — 내열·내식성이 좋습니다",
 "<b>스프링 클립</b> 마운팅 — 튜브를 빠르게 넣고 뺍니다 (두께 0.8 / 1.6 mm · 외경 6.4 mm 이하)",
 "<b>수입 42 스텝모터</b> — 저소음 · 고안정 · 긴 수명 · 정밀도 확보",
 "유량 두께 0.8 mm 계열 최대 <b>161 mL/min</b>, 두께 1.6 mm 계열 최대 <b>236 mL/min</b>",
 "L자 브래킷(측면 패널 관통 설치)과 Z자 브래킷(수직 패널 관통 설치) 두 가지 마운팅",
 "의료 기기와 소유량 액체 이송 분석 장비를 주 대상으로 하며 <b>OEM 대응</b> 합니다"],
"specs":[
 ["유량 범위 (Flow rate)","최대 161 mL/min (WT 0.8 mm) · 최대 236 mL/min (WT 1.6 mm)"],
 ["모델 (Model No.)","BJ-RZ-02 (RZ-02 헤드)"],
 ["롤러 (Pump roller)","PPS 3롤러 (대유량) / 6롤러 (저맥동)"],
 ["하우징 재질 (Housing)","PPS + 합성섬유"],
 ["모터 (Motor type)","수입 42 스텝모터"],
 ["튜브 장착 (Tube mounting)","스프링 클립 (WT 0.8 / 1.6 mm · OD ≤6.4 mm)"],
 ["마운팅 (Mounting)","L자 브래킷 (측면 패널 관통) · Z자 브래킷 (수직 패널 관통) · 2-M3 홀"]],
"variants":{"heading":"튜브 규격별 유량 (mL/min · RZ-02)","head":["튜브 두께","3롤러 유량","6롤러 유량"],
 "rows":[["0.8 mm","0 ~ 161","0 ~ 114.33"],["1.6 mm","0.08 ~ 236.33","0.073 ~ 183"]],
 "note":"두께 0.8 mm 계열은 내경 0.64 mm 에서 16 mL/min 부터 내경 2.79 mm 에서 161 mL/min 까지, 두께 1.6 mm 계열은 23 · 79.67 · 157 · 236.33 mL/min 구간으로 표기됩니다. 상온 20℃·무가압 순수 기준 참고값입니다."},
"buybox":[],
"related":PREL(' · <a href="/brands/runze/small-peristaltic-pump-bj-rz-01/">소형 연동펌프 BJ-RZ-01</a> · <a href="/brands/runze/lm40b-micro-peristaltic-pump/">지능형 충전 연동펌프 LM40B</a> · <a href="https://www.youtube.com/watch?v=UgMxYNjY7v4" rel="nofollow">BJ-RZ-02 제조사 소개 영상</a>'),
"keywords":PKW+[["#소형연동펌프","/product/"],["#저맥동","/product/"],["#의료기기용","/product/"]],
"sections":[
 {"h":"모델명 규칙 (Naming rules)","html":figs([(D(s,0),"BJ-RZ-02 모델명 구성 규칙")])},
 {"h":"튜브 장착 (Tube installation)","html":"<p>스프링 클립으로 다섯 단계에 끝냅니다. 상부 압착 블록을 안쪽으로 누르고, 스프링 락을 열고, 상부 압착 블록을 젖힌 뒤 호스를 넣고, 다시 상부 압착 블록을 눌러 스프링 락을 닫습니다. 호스에 그리스를 바르면 수명이 길어집니다.</p>"
  +figs([(D(s,5),"스프링 클립 튜브 장착 5단계 — 두께 0.8 / 1.6 mm · 외경 6.4 mm 이하")])},
 {"h":"외형 치수 · 설치 (Dimension & mounting)","html":"<p>L자 브래킷은 측면 패널 관통 설치, Z자 브래킷은 수직 패널 관통 설치용입니다. 2-M3 마운팅 홀을 씁니다.</p>"
  +figs([(D(s,7),"RZ-02 외형 치수와 L자 · Z자 브래킷 설치 방식")])},
 {"h":"적용 튜브 · 참고 유량","html":figs([(D(s,9),"RZ-02 적용 튜브 규격과 3·6롤러 유량표")])},
 {"h":"용도 (Applications)","html":APPS+figs([(D(s,8),"산업별 적용 분야")])},
 {"h":"제품 사진 (Product)","html":figs([(D(s,i),"BJ-RZ-02 (제조사 자료)") for i in [1,2,3,4,6]])}],
"faq":[
 {"tag":"롤러","q":"3롤러와 6롤러 중 어느 쪽을 골라야 하나요?","a":"유량이 필요하면 3롤러, 맥동을 줄이고 토출을 고르게 하려면 6롤러입니다. 두께 1.6 mm 튜브에서 3롤러는 최대 236 mL/min, 6롤러는 183 mL/min입니다."},
 {"tag":"튜브","q":"튜브 교체가 쉬운가요?","a":"스프링 클립 구조라 상부 압착 블록을 누르고 젖혀 호스를 넣는 다섯 단계면 됩니다. 두께 0.8 / 1.6 mm, 외경 6.4 mm 이하 호스를 씁니다."},
 {"tag":"재질","q":"하우징 재질은 무엇인가요?","a":"PPS에 합성섬유를 넣은 재질입니다. 내열성과 내식성이 좋습니다. 롤러도 PPS입니다."},
 {"tag":"설치","q":"패널에 매립할 수 있나요?","a":"L자 브래킷으로 측면 패널 관통, Z자 브래킷으로 수직 패널 관통 설치가 가능합니다. 2-M3 마운팅 홀을 씁니다."},
 {"tag":"용도","q":"주로 어디에 쓰나요?","a":"의료 기기와 소유량 액체 이송 분석 장비입니다. 환경 계측, 수질 모니터링, 식품·음료, 산업기계에도 씁니다."},
 {"tag":"OEM","q":"OEM 대응이 되나요?","a":"됩니다. 헤드 구성과 마운팅을 장비에 맞춰 조정합니다."}],
"ld":{"name":"Runze Fluid 소형 연동펌프 BJ-RZ-02","sku":"BJ-RZ-02","category":"연동펌프 · 스텝모터 일체형",
 "description":"RZ-02 헤드 소형 연동펌프. PPS 3·6롤러, PPS+합성섬유 하우징, 스프링 클립 튜브 장착, 수입 42 스텝모터, 최대 236 mL/min, L자·Z자 브래킷.",
 "models":["BJ-RZ-02"],"count":2},
"source":SRCU("small-peristaltic-pump-bj-rz-02")})
add(P)
