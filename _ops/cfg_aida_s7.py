# -*- coding: utf-8 -*-
"""AIDA 7 — 백금망 상대전극 (카탈로그 p6~7)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C

ROWS = C.rows([
 ('Pt305','5 × 10 mm',116),  ('Pt310','10 × 10 mm',138), ('Pt315','10 × 15 mm',160),
 ('Pt312','10 × 20 mm',183), ('Pt350','15 × 15 mm',189), ('Pt320','20 × 20 mm',250),
 ('Pt330','30 × 30 mm',410), ('Pt321','Φ20 mm (원형)',213), ('Pt313','10 × 30 mm',226),
])

B.build(dict(
 landed=True, brand='aida', slug='pt-mesh-counter-electrode', cat='상대전극',
 h1='백금망 상대전극', sub='Platinum Mesh Counter Electrode · 5×10 ~ 30×30 mm · Φ20 mm',
 title='아이다 백금망 상대전극 — 5×10 ~ 30×30 mm, Φ20 mm 9종 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 백금망 상대전극 9종 — Pt305(5×10)부터 Pt330(30×30)까지와 원형 Pt321(Φ20). 같은 외형에서 백금판보다 실표면적이 크고 용액이 통과해 기포가 잘 빠집니다. %s원부터.'%C.lo(ROWS),
 ldname='백금망 상대전극 (Platinum Mesh Counter Electrode)',
 answer='백금을 그물로 짠 상대전극입니다. 같은 크기의 판보다 실표면적이 크고, 용액이 그물을 통과해 기포가 갇히지 않습니다.',
 summary='<b>5×10 ~ 30×30 mm · 원형 Φ20 mm</b> 9종 · %s원부터'%C.lo(ROWS),
 quote='아이다 백금망 상대전극',
 feat=[
  '<b>같은 외형에서 판보다 실표면적이 큽니다</b> — 전류를 더 여유 있게 받습니다',
  '<b>용액이 그물을 통과</b>하므로 수소·산소 기포가 표면에 갇히지 않습니다. 장시간 전해에 유리합니다',
  '<b>원형 Pt321(Φ20)</b>은 원통형 셀에서 작업전극을 둘러싸도록 말아 쓰기 좋습니다 — 전류 분포가 고르게 됩니다',
  '그물 구조라 <b>세척 시 잔여물이 남기 쉽습니다</b> — 초음파 세척 후 묽은 산으로 마무리하십시오',
  '판이 필요하면 <a href="/brands/aida/pt-sheet-counter-electrode/">백금판</a>, 값을 아끼려면 <a href="/brands/aida/graphite-rod-counter-electrode/">흑연봉</a>이 있습니다',
 ],
 spec=[
  ('재질','<b>백금 (Pt)</b> 메시'),
  ('사각형','5×10 · 10×10 · 10×15 · 10×20 · 15×15 · 20×20 · 10×30 · 30×30 mm'),
  ('원형','<b>Φ20 mm</b> (Pt321)'),
  ('장점','실표면적 확대 · 기포 배출'),
  ('세척','초음파 세척 후 묽은 산'),
  ('표 외 규격','<b>주문 제작</b>'),
 ],
 price=ROWS, note=C.note(ROWS),
 cross='상대전극 계열: <a href="/brands/aida/pt-sheet-counter-electrode/">백금판</a> · <a href="/brands/aida/pt-wire-counter-electrode/">백금선·백금봉</a> · <a href="/brands/aida/graphite-rod-counter-electrode/">흑연봉</a>',
 faq=[
  ('망과 판 중 뭐가 낫나요?','기체가 발생하는 반응이면 망이 낫습니다. 기포가 빠져나가 유효 면적이 유지됩니다. 단순한 CV 측정이면 판으로 충분하고 세척이 쉽습니다.'),
  ('원형 Pt321은 어떻게 쓰나요?','원통형 셀에서 벽을 따라 둥글게 두고 작업전극을 가운데 놓습니다. 전류가 사방에서 고르게 흘러 전위 분포가 안정됩니다.'),
  ('망 사이에 낀 침전물은 어떻게 빼나요?','초음파 세척조에 증류수로 돌린 뒤 묽은 질산이나 황산으로 마무리하십시오. 눌러서 긁으면 그물이 상합니다.'),
  ('면적은 표기 치수 그대로인가요?','표기는 외형 치수입니다. 그물이라 실표면적은 그보다 큽니다. 정량 비교가 필요하면 전기화학적 활성면적을 직접 재십시오.'),
 ]))
print('AIDA 7 — 백금망 %d종'%len(ROWS))
