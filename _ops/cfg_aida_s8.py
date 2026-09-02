# -*- coding: utf-8 -*-
"""AIDA 8 — 흑연봉 상대전극 (카탈로그 p6)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C, cfg_aida_floor as F

_RAW = ([
 ('C303','흑연봉 Φ3 mm',29), ('C304','흑연봉 Φ4 mm',29),
 ('C305','흑연봉 Φ5 mm',29), ('C306','흑연봉 Φ6 mm',29),
])
ROWS = C.rows(_RAW)
ROWS = F.floor('graphite-rod-counter-electrode', ROWS)   # 가오스 동일 제품 −5,000원 하한
for _l in F.report('graphite-rod-counter-electrode', C.rows(_RAW)): print(_l)

B.build(dict(
 landed=True, brand='aida', slug='graphite-rod-counter-electrode', cat='상대전극',
 h1='흑연봉 상대전극', sub='Graphite Rod Counter Electrode · C303 ~ C306 · Φ3 ~ 6 mm',
 title='아이다 흑연봉 상대전극 — Φ3·4·5·6 mm 4종 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 흑연봉 상대전극 4종 — C303~C306, Φ3·4·5·6 mm. PTFE 외피에 흑연을 봉입한 형태로 Φ3 기준 흑연부와 PTFE부가 각 50 mm, 전장 120 mm입니다. 백금 상대전극의 저렴한 대안입니다. %s원부터.'%C.lo(ROWS),
 ldname='흑연봉 상대전극 (Graphite Rod Counter Electrode)',
 answer='백금 대신 쓰는 값싼 상대전극입니다. 백금이 녹아 작업전극을 오염시키는 것을 피하고 싶을 때도 씁니다.',
 summary='<b>Φ3 · 4 · 5 · 6 mm</b> 4종 · PTFE 외피 · 전장 120 mm · %s원부터'%C.lo(ROWS),
 quote='아이다 흑연봉 상대전극',
 feat=[
  '<b>백금보다 훨씬 쌉니다</b> — 일반적인 CV·LSV 측정에는 성능 차이가 거의 없습니다',
  '<b>백금 용출 걱정이 없습니다</b> — 장시간 산화 조건에서 백금이 녹아 작업전극에 재석출되는 문제를 피할 수 있습니다',
  'Φ3 mm 기준 <b>흑연부 50 mm · PTFE부 50 mm · 전장 120 mm</b>입니다',
  '흑연은 <b>강한 산화 조건에서 서서히 깎입니다</b> — 탄소 입자가 떨어져 나오면 정밀 측정에 방해가 됩니다',
  '탄소 오염이 문제가 되는 계에서는 <a href="/brands/aida/pt-sheet-counter-electrode/">백금판</a>·<a href="/brands/aida/pt-mesh-counter-electrode/">백금망</a>을 쓰십시오',
 ],
 spec=[
  ('재질','<b>흑연 (Graphite)</b> · 외피 PTFE'),
  ('직경','<b>Φ3 · 4 · 5 · 6 mm</b>'),
  ('길이 (Φ3 기준)','흑연부 <b>50 mm</b> · PTFE부 <b>50 mm</b> · 전장 <b>120 mm</b>'),
  ('장점','저가 · 백금 용출 없음'),
  ('한계','강한 산화 조건에서 소모 · 탄소 입자 이탈'),
  ('표 외 규격','<b>주문 제작</b>'),
 ],
 price=ROWS, note=C.note(ROWS),
 warn='흑연은 <b>소모품에 가깝습니다.</b> 강한 산화 전위를 오래 걸면 표면이 깎이고 탄소 입자가 용액으로 떨어집니다. 촉매 활성을 정밀하게 재는 실험이라면 백금 상대전극을 쓰시고, 흑연은 일상적인 측정용으로 두십시오.',
 cross='상대전극 계열: <a href="/brands/aida/pt-sheet-counter-electrode/">백금판</a> · <a href="/brands/aida/pt-mesh-counter-electrode/">백금망</a> · <a href="/brands/aida/pt-wire-counter-electrode/">백금선·백금봉</a>',
 faq=[
  ('흑연봉으로 백금을 대체해도 되나요?','일반적인 CV·LSV·크로노암페로메트리에서는 됩니다. 다만 장시간 산화 전해나 정밀 촉매 평가에는 백금이 낫습니다.'),
  ('얼마나 자주 갈아야 하나요?','쓰는 조건에 따라 다릅니다. 표면이 눈에 띄게 패이거나 용액에 검은 입자가 보이면 교체하십시오.'),
  ('직경은 어떻게 고르나요?','작업전극 대비 면적을 넉넉히 잡으면 됩니다. 대부분 Φ5~6 mm면 충분합니다.'),
  ('세척은 어떻게 하나요?','증류수로 헹구고 말리는 정도면 됩니다. 표면이 오염됐으면 고운 사포로 살짝 갈아 새 면을 내십시오.'),
 ]))
print('AIDA 8 — 흑연봉 %d종'%len(ROWS))
