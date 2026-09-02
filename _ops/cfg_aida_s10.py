# -*- coding: utf-8 -*-
"""AIDA 10 — 전극 홀더 · 시료 지지대 (카탈로그 p2, p13)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C, cfg_aida_floor as F

_RAW = ([
 ('J110','전극 홀더 (PTFE) · Φ6 × 80 mm',97),
 ('J120','전극 홀더 (STS304) · Φ6 × 80 mm',29),
 ('J210','시료 지지대 · 작용면적 1 cm² · 전극봉 길이 10 cm',194),
])
ROWS = C.rows(_RAW)
ROWS = F.floor('electrode-holder', ROWS)   # 가오스 동일 제품 −5,000원 하한
for _l in F.report('electrode-holder', C.rows(_RAW)): print(_l)

B.build(dict(
 landed=True, brand='aida', slug='electrode-holder', cat='전극 부속',
 h1='전극 홀더 · 시료 지지대', sub='Electrode Holder (PTFE / SS304) · Sample Support J210',
 title='아이다 전극 홀더·시료 지지대 — J110 PTFE · J120 STS304 · J210 시료 지지대 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 전극 홀더 J110(PTFE)·J120(STS304) Φ6 × 80 mm와 시료 지지대 J210(작용면적 1 cm², 전극봉 10 cm). 판·박막 시료를 셀에 물려 작업전극으로 쓰는 부속입니다. %s원부터.'%C.lo(ROWS),
 ldname='전극 홀더 · 시료 지지대 (Electrode Holder · Sample Support)',
 answer='봉입되지 않은 판·박막 시료를 집어 작업전극으로 쓰게 해 주는 부속입니다. 시료 자체가 연구 대상일 때 씁니다.',
 summary='<b>전극 홀더 PTFE · STS304 Φ6 × 80 mm · 시료 지지대 1 cm²</b> 3종 · %s원부터'%C.lo(ROWS),
 quote='아이다 전극 홀더·시료 지지대',
 feat=[
  '<b>봉입하지 않은 시료를 그대로 씁니다</b> — 직접 만든 박막·도금판·소재 쿠폰을 작업전극으로 물립니다',
  '<b>J110 (PTFE)</b>는 절연체라 홀더 자체가 전류를 흘리지 않습니다. 부식성 용액에도 무던합니다',
  '<b>J120 (STS304)</b>은 값이 싸지만 금속이라 <b>용액에 닿는 부분이 함께 반응</b>합니다 — 액면 위로 올려 쓰십시오',
  '<b>J210 시료 지지대</b>는 작용면적이 <b>1 cm²</b>로 고정입니다 — 전류밀도 계산이 간단해집니다',
  'J210은 시료 <b>두께 5 mm 미만 · 외경 Φ15 mm 미만</b>, 셀 <b>용량 150 mL 이상</b>이어야 들어갑니다',
 ],
 spec=[
  ('J110 전극 홀더','<b>PTFE</b> · Φ6 × 80 mm — 절연·내약품'),
  ('J120 전극 홀더','<b>STS304</b> · Φ6 × 80 mm — 저가·도전성'),
  ('J210 시료 지지대','작용면적 <b>1 cm²</b> · 전극봉 길이 <b>10 cm</b>'),
  ('J210 시료 조건','두께 <b>5 mm 미만</b> · 외경 <b>Φ15 mm 미만</b>'),
  ('J210 셀 조건','용량 <b>150 mL 이상</b>'),
  ('표 외 규격','<b>주문 제작</b>'),
 ],
 price=ROWS, note=C.note(ROWS),
 warn='<b>J210은 시료·셀 치수 제한이 있습니다.</b> 시료는 두께 5 mm 미만·외경 Φ15 mm 미만, 셀은 용량 150 mL 이상이어야 합니다. 쓰시는 셀과 시료 치수를 먼저 확인해 주십시오.',
 cross='전극 계열: <a href="/brands/aida/gc-disc-working-electrode/">유리탄소 디스크 작업전극</a> · <a href="/brands/aida/pt-disc-working-electrode/">백금·금·은 디스크 작업전극</a> · <a href="/brands/aida/reference-electrode/">기준전극</a>',
 faq=[
  ('J110과 J120 중 뭘 써야 하나요?','대부분 J110(PTFE)이 안전합니다. J120은 금속이라 용액에 닿으면 함께 반응하므로, 접점이 액면 위로 올라오는 구조에서만 쓰십시오.'),
  ('J210의 1 cm²는 정확한가요?','설계 면적입니다. 정밀한 전류밀도가 필요하면 실제 젖은 면적을 확인해 보정하십시오.'),
  ('내 시료가 Φ20 mm인데 쓸 수 있나요?','J210은 Φ15 mm 미만까지입니다. 더 크면 잘라 쓰시거나 주문 제작을 문의해 주십시오.'),
  ('홀더에 물린 시료 뒷면도 용액에 닿나요?','구조상 앞면만 노출되도록 물립니다. 다만 밀봉이 완전하지 않으면 새어 들어갈 수 있으니 체결 상태를 확인하십시오.'),
 ]))
print('AIDA 10 — 전극 홀더·시료 지지대 %d종'%len(ROWS))
