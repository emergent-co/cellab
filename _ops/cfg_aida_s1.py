# -*- coding: utf-8 -*-
"""AIDA 샘플 1 — 유리탄소(GC) 디스크 작업전극 (카탈로그 p1)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C

ROWS = C.rows([
 ('GC120','Φ2 mm',97), ('GC130','Φ3 mm',93), ('GC140','Φ4 mm',108),
 ('GC150','Φ5 mm',108), ('GC160','Φ6 mm',135), ('GC370','Φ7 mm',194),
 ('GC380','Φ8 mm',290), ('GC390','Φ9 mm',425), ('GC310','Φ10 mm',580),
 ('GC315','Φ15 mm',1160), ('GC321','Φ20 mm',1935),
])

B.build(dict(
 brand='aida', slug='gc-disc-working-electrode', cat='작업전극',
 h1='유리탄소(GC) 디스크 작업전극', sub='Glassy Carbon Disk Working Electrode · GC120 ~ GC321',
 title='아이다 유리탄소(GC) 디스크 작업전극 — Φ2~20 mm 11종 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 유리탄소(GC) 디스크 작업전극 11종 — Φ2·3·4·5·6·7·8·9·10·15·20 mm. CV·LSV·RDE의 기본 작업전극으로, 넓은 전위창과 낮은 배경전류가 특징입니다. 135,000원부터.',
 ldname='유리탄소 디스크 작업전극 (Glassy Carbon Disk Working Electrode)',
 answer='유리탄소를 원판으로 봉입한 표준 작업전극입니다. 전위창이 넓고 배경전류가 낮아 CV·LSV의 기준 전극면으로 가장 널리 씁니다.',
 summary='<b>Φ2 ~ 20 mm 11종</b> · 유리탄소 원판 · PTFE 외피 · 135,000원부터',
 quote='아이다 유리탄소(GC) 디스크 작업전극',
 imgs=[],
 feat=[
  '<b>Φ2 ~ 20 mm 11종</b>으로 나뉩니다 — 소면적은 정량 분석, 대면적(Φ10 이상)은 전해 합성·박막 평가에 씁니다',
  '유리탄소는 <b>전위창이 넓고 배경전류가 낮아</b> 미량 산화·환원 피크를 읽기 좋습니다',
  '표면을 <b>알루미나로 재연마</b>하면 매번 새 전극면이 나옵니다 — 0.3 µm → 0.05 µm 순으로 내려가십시오',
  '<b>Φ3 · Φ5 mm</b>가 논문에서 가장 흔한 규격입니다. 문헌 조건을 그대로 따라갈 때 먼저 보십시오',
  '회전전극으로 쓰시려면 <a href="/brands/aida/rde-rrde/">회전원판전극(RDE·RRDE)</a>이 따로 있습니다',
 ],
 spec=[
  ('디스크 재질','<b>유리탄소 (Glassy Carbon)</b>'),
  ('디스크 직경','<b>Φ2 · 3 · 4 · 5 · 6 · 7 · 8 · 9 · 10 · 15 · 20 mm</b>'),
  ('외피','PTFE'),
  ('용도','CV · LSV · 크로노암페로메트리 · 전해 합성'),
  ('연마','알루미나 0.3 µm → 0.05 µm 순'),
  ('표 외 규격','<b>주문 제작</b>'),
 ],
 price=ROWS,
 cross='작업전극 계열: <a href="/brands/aida/pt-disc-working-electrode/">백금 디스크</a> · <a href="/brands/aida/pt-sheet-counter-electrode/">백금판 상대전극</a> · <a href="/brands/aida/reference-electrode/">기준전극</a>',
 faq=[
  ('Φ3과 Φ5 중 뭘 골라야 하나요?','문헌을 따라가시면 그 논문이 쓴 직경을 그대로 쓰십시오. 정하기 어려우면 Φ3이 무난합니다. 면적이 작을수록 iR 강하와 용량성 전류가 줄어 피크가 깨끗합니다.'),
  ('연마는 얼마나 자주 하나요?','측정 전마다 하는 것이 기본입니다. 배경 CV를 떠서 이전과 모양이 달라졌으면 반드시 다시 연마하십시오.'),
  ('Φ15·Φ20 같은 큰 것은 어디에 쓰나요?','전해 합성이나 박막 증착처럼 전류를 많이 흘려야 할 때 씁니다. 분석용으로는 용량성 전류가 커서 불리합니다.'),
  ('표에 없는 직경도 되나요?','주문 제작됩니다. 필요한 직경과 외피 재질을 알려주십시오.'),
 ]))
print('AIDA 샘플 1 — GC 디스크 작업전극 %d종'%len(ROWS))
