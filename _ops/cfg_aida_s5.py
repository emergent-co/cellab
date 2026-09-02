# -*- coding: utf-8 -*-
"""AIDA 샘플 5 — 회전원판전극 RDE · 회전링원판전극 RRDE (카탈로그 p9~12)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C

ROWS = C.rows([
 ('E3-PTFE','RDE E3 시리즈 · GC 디스크 Φ3·4·5 mm · PTFE 외피',348),
 ('E3-PEEK','RDE E3 시리즈 · GC 디스크 Φ3·4·5 mm · PEEK 외피',368),
 ('E5-PTFE','RDE E5 시리즈 · GC 디스크 Φ3·4·5 mm · PTFE 외피',445),
 ('E5-PEEK','RDE E5 시리즈 · GC 디스크 Φ3·4·5 mm · PEEK 외피',465),
 ('RRDE GC-Pt','RRDE · GC 디스크 + 백금 링 · Φ5.61 mm · PTFE',1645),
 ('RRDE Pt-Pt','RRDE · 백금 디스크 + 백금 링 · Φ5.61 mm · PTFE',3600),
 ('Change-Disk RRDE','디스크 교체형 RRDE · GC 디스크 Φ5 mm · PTFE',800),
])

B.build(dict(
 brand='aida', slug='rde-rrde', cat='회전전극',
 h1='회전원판전극(RDE) · 회전링원판전극(RRDE)',
 sub='Rotating Disk / Ring-Disk Electrode · PINE 호환 · E3 · E5 · RRDE',
 title='아이다 회전원판전극 RDE · 회전링원판전극 RRDE — PINE 호환 7종 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) 회전원판전극(RDE)·회전링원판전극(RRDE) 7종 — PINE 호환 E3·E5 시리즈(GC 디스크 Φ3·4·5 mm, PTFE/PEEK 외피), RRDE GC-Pt·Pt-Pt(Φ5.61 mm, 수집효율 37%), 디스크 교체형 RRDE. ORR 4전자 선택성 평가의 표준 도구입니다. '+C.lo(ROWS)+'원부터.',
 ldname='회전원판전극 · 회전링원판전극 (Rotating Disk / Ring-Disk Electrode)',
 answer='전극을 돌려 확산층 두께를 회전수로 고정하는 전극입니다. ORR 촉매의 전자수와 과산화수소 생성률을 정량하는 표준 도구입니다.',
 summary='<b>PINE 호환 · E3 · E5 · RRDE GC-Pt · Pt-Pt · 디스크 교체형</b> 7종 · %s원부터'%C.lo(ROWS),
 quote='아이다 회전원판전극(RDE)·회전링원판전극(RRDE)',
 feat=[
  '<b>PINE 회전기에 맞는 규격</b>입니다 — 쓰시는 회전기 모델을 알려주시면 체결부를 확인해 드립니다',
  '<b>RDE</b>는 Koutecký–Levich 해석으로 전자수(n)를 구합니다 — 회전수를 바꿔가며 잰 전류를 ω<sup>-1/2</sup>로 그립니다',
  '<b>RRDE</b>는 링에서 과산화수소를 바로 잡아내 <b>4전자 선택성</b>을 한 번에 봅니다. 수집효율 <b>37%</b>',
  '<b>PEEK 외피</b>는 PTFE보다 단단해 촉매 잉크를 반복 도포·세척할 때 형상이 덜 상합니다',
  '<b>디스크 교체형 RRDE</b>는 디스크만 갈아 끼웁니다 — 여러 촉매를 비교할 때 값이 훨씬 덜 듭니다',
  'Pt-Pt RRDE는 백금 디스크라 <b>백금 기준선</b>을 그대로 얻습니다. 값이 비싼 만큼 용도가 분명할 때 고르십시오',
 ],
 spec=[
  ('호환','<b>PINE</b> 회전기 규격'),
  ('RDE E3 / E5','디스크 <b>유리탄소 Φ3 · 4 · 5 mm</b> · 외피 PTFE 또는 PEEK'),
  ('RRDE 디스크경','<b>Φ5.61 mm</b> (면적 0.2475 cm²)'),
  ('RRDE 링','내경 6.25 mm · 외경 7.92 mm (면적 0.1866 cm²)'),
  ('링–디스크 간격','<b>318 µm</b>'),
  ('수집효율','<b>37%</b>'),
  ('외피 외경','15.0 mm'),
  ('디스크 교체형','유리탄소 <b>Φ5 mm</b> · PTFE 외피'),
 ],
 price=ROWS,
 warn='회전기 체결부는 제조사마다 다릅니다. <b>쓰시는 회전기 모델명을 먼저 알려주십시오.</b> 나사 규격이 맞지 않으면 장착이 안 됩니다.',
 cross='전극 계열: <a href="/brands/aida/gc-disc-working-electrode/">유리탄소(GC) 디스크 작업전극</a> · <a href="/brands/aida/pt-disc-working-electrode/">백금·금·은 디스크 작업전극</a> · <a href="/brands/aida/reference-electrode/">기준전극</a>',
 faq=[
  ('RDE와 RRDE 중 뭐가 필요한가요?','전자수만 구하시면 RDE로 충분합니다. 과산화수소가 얼마나 나오는지 직접 재야 하면 RRDE가 필요합니다. ORR 촉매 논문은 대개 둘 다 싣습니다.'),
  ('수집효율 37%는 무슨 뜻인가요?','디스크에서 나온 생성물 중 링이 잡아내는 비율입니다. 과산화수소 수율을 계산할 때 이 값으로 나눠 보정합니다. 실측으로 다시 확인해 쓰시는 것이 정확합니다.'),
  ('PTFE와 PEEK 중 어느 외피가 낫나요?','PEEK가 단단해 반복 사용에 유리하고 디스크와의 틈이 덜 벌어집니다. PTFE는 화학적으로 더 무던하고 값이 쌉니다.'),
  ('디스크 교체형은 성능이 떨어지나요?','디스크와 링 사이 밀봉이 일체형만큼 완벽하지는 않아 수집효율이 조금 달라질 수 있습니다. 여러 촉매를 비교하는 용도라면 비용 이점이 큽니다.'),
  ('회전기도 같이 구할 수 있나요?','문의 주십시오. 쓰시는 셀·전극 구성에 맞춰 안내드립니다.'),
 ]))
print('AIDA 샘플 5 — RDE·RRDE %d종'%len(ROWS))
