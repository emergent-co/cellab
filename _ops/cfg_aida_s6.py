# -*- coding: utf-8 -*-
"""AIDA 6 — 백금선·백금봉·나선 백금선 상대전극 (카탈로그 p5)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C, cfg_aida_floor as F

_RAW = ([
 ('Pt005','백금선 Φ0.5 × 37 mm',74),
 ('Pt017','백금선 Φ1 × 37 mm',216),
 ('Pt015','백금봉 Φ1 × 5 mm',73),
 ('Pt010','백금봉 Φ1 × 10 mm',100),
 ('Pt505','나선 백금선 Φ0.5 × 150 mm',180),
])
ROWS = C.rows(_RAW)
ROWS = F.floor('pt-wire-counter-electrode', ROWS)   # 가오스 동일 제품 −5,000원 하한
for _l in F.report('pt-wire-counter-electrode', C.rows(_RAW)): print(_l)

B.build(dict(
 landed=True, brand='aida', slug='pt-wire-counter-electrode', cat='상대전극',
 h1='백금선 · 백금봉 상대전극', sub='Platinum Wire / Column Counter Electrode · Pt005 · Pt010 · Pt015 · Pt017 · Pt505',
 title='아이다 백금선·백금봉 상대전극 — Pt005·Pt010·Pt015·Pt017·나선 Pt505 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 백금선·백금봉 상대전극 5종 — Pt005(Φ0.5×37), Pt017(Φ1×37), Pt015(Φ1×5), Pt010(Φ1×10), 나선형 Pt505(Φ0.5×150). 좁은 셀이나 소용량 셀에서 백금판 대신 씁니다. %s원부터.'%C.lo(ROWS),
 ldname='백금선·백금봉 상대전극 (Platinum Wire / Column Counter Electrode)',
 answer='선이나 짧은 봉 형태의 백금 상대전극입니다. 셀 입구가 좁거나 용액이 적어 백금판을 넣기 어려울 때 씁니다.',
 summary='<b>백금선 · 백금봉 · 나선형</b> 5종 · Φ0.5 ~ 1 mm · %s원부터'%C.lo(ROWS),
 quote='아이다 백금선·백금봉 상대전극',
 feat=[
  '<b>좁은 셀·소용량 셀</b>에서 백금판 대신 씁니다 — 표준 조인트 구멍으로 그대로 들어갑니다',
  '<b>나선형 Pt505</b>는 같은 길이에서 표면적을 크게 벌어 놓은 형태입니다. 선형보다 전류를 여유 있게 받습니다',
  '<b>Pt015 · Pt010</b>은 노출 길이가 5 · 10 mm로 짧아, 용액 깊이가 얕은 셀에 맞습니다',
  '표면적이 백금판보다 작으므로 <b>작업전극이 크면 백금판·백금망</b>을 보십시오',
  '백금은 <b>묽은 황산에서 전위 순환</b>으로 세척합니다 — 표면 상태가 배경전류를 좌우합니다',
 ],
 spec=[
  ('재질','<b>백금 (Pt)</b>'),
  ('백금선','Pt005 Φ0.5 × 37 mm · Pt017 Φ1 × 37 mm'),
  ('백금봉','Pt015 Φ1 × 5 mm · Pt010 Φ1 × 10 mm'),
  ('나선형','Pt505 Φ0.5 × 150 mm'),
  ('용도','좁은 셀 · 소용량 셀의 상대전극'),
  ('표 외 규격','<b>주문 제작</b>'),
 ],
 price=ROWS, note=C.note(ROWS),
 cross='상대전극 계열: <a href="/brands/aida/pt-sheet-counter-electrode/">백금판</a> · <a href="/brands/aida/pt-mesh-counter-electrode/">백금망</a> · <a href="/brands/aida/graphite-rod-counter-electrode/">흑연봉</a>',
 faq=[
  ('백금선으로 충분한가요, 백금판을 써야 하나요?','작업전극이 Φ3 mm 정도의 디스크이고 전류가 크지 않다면 백금선으로 됩니다. 전류가 크거나 장시간 흘리면 상대전극 쪽에서 제한이 걸리니 백금판·백금망으로 올리십시오.'),
  ('나선형은 뭐가 다른가요?','같은 길이에 감아 놓아 표면적이 큽니다. 셀 벽을 따라 배치하면 작업전극 주위 전류 분포도 고르게 됩니다.'),
  ('Pt005와 Pt017의 차이는?','굵기입니다. Φ0.5와 Φ1 mm. 굵은 쪽이 표면적이 크고 잘 휘지 않습니다.'),
  ('백금선이 검게 변했습니다.','유기물 오염이거나 산화막입니다. 묽은 황산에서 전위를 순환시켜 벗겨 내십시오.'),
 ]))
print('AIDA 6 — 백금선·백금봉 %d종'%len(ROWS))
