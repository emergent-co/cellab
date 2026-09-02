# -*- coding: utf-8 -*-
"""AIDA 셀 1 — C002 일반 유리 전해셀 (카탈로그 p15)"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B, cfg_aida_common as C, cfg_aida_floor as F

_RAW=[('C002-30','10 ~ 30 mL',15), ('C002-50','50 mL',19), ('C002-100','100 mL',23),
      ('C002-150','150 mL',27), ('C002-250','200 ~ 250 mL',31), ('C002-300','300 mL',47),
      ('C002-500','500 mL',58)]
ROWS=C.rows(_RAW); ROWS=F.floor('glass-cell-c002',ROWS)
for _l in F.report('glass-cell-c002', C.rows(_RAW)): print(_l)

B.build(dict(
 landed=True, brand='aida', slug='glass-cell-c002', cat='전해셀',
 h1='C002 일반 유리 전해셀', sub='Regular Electrolytic Cell C002 · 10 ~ 500 mL',
 title='아이다 C002 일반 유리 전해셀 — 10~500 mL 7종 정가 | 실험셋업연구소',
 desc='아이다(TianJin AIDA) C002 일반 유리 전해셀 7종 — 10~30·50·100·150·200~250·300·500 mL. 3전극 측정의 기본 셀로, 뚜껑 구멍은 쓰시는 전극 직경에 맞춰 출하 전에 가공합니다. %s원부터.'%C.lo(ROWS),
 ldname='C002 일반 유리 전해셀 (Regular Electrolytic Cell)',
 answer='3전극 측정에 쓰는 가장 기본적인 유리 전해셀입니다. 작업·기준·상대전극을 뚜껑 구멍에 꽂아 씁니다.',
 summary='<b>10 ~ 500 mL 7종</b> · 붕규산 유리 · 전극 구멍 주문 가공 · %s원부터'%C.lo(ROWS),
 quote='아이다 C002 일반 유리 전해셀',
 feat=['<b>뚜껑 구멍은 출하 전에 뚫습니다</b> — 주문 시 쓰실 전극의 바깥지름을 알려 주십시오',
       '<b>용량은 실사용량보다 넉넉히</b> 잡으십시오. 전극이 잠기고 교반 여유가 있어야 합니다',
       '<b>항온이 필요하면</b> <a href="/brands/aida/jacket-cell-c003/">C003 재킷형</a>, <b>밀폐가 필요하면</b> <a href="/brands/aida/sealed-cell-c001/">C001</a>을 보십시오',
       '가장 흔한 선택은 <b>100 mL</b>입니다 — 전극 3개를 넣고도 여유가 있습니다',
       '<b>전극은 포함되지 않습니다</b> — 작업·기준·상대전극은 별도 주문입니다'],
 spec=[('셀 본체','<b>붕규산 유리</b>'),('용량','<b>10 ~ 30 · 50 · 100 · 150 · 200~250 · 300 · 500 mL</b>'),
       ('밀폐','비밀폐(개방형)'),('전극 구멍','<b>주문 시 전극 직경에 맞춰 가공</b>'),
       ('구성','<b>셀 본체 + 뚜껑</b> — 전극 미포함'),('항온','불가 — <a href="/brands/aida/jacket-cell-c003/">C003</a> 참조')],
 price=ROWS, note=C.note(ROWS),
 warn='<b>전극은 별매입니다.</b> 사진에 보이는 전극은 배치를 보여 주기 위한 것으로 셀 구성에 들어가지 않습니다. 뚜껑 구멍은 주문하신 전극 직경 기준으로 가공되므로, <b>전극을 먼저 정하고 셀을 주문</b>하시는 편이 안전합니다.',
 cross='전해셀 계열: <a href="/brands/aida/sealed-cell-c001/">C001 밀폐형</a> · <a href="/brands/aida/jacket-cell-c003/">C003 항온 재킷</a> · <a href="/brands/aida/five-port-cell-c010/">C010 5구</a> · <a href="/brands/aida/h-cell-ch2001/">CH2001 H형</a>',
 faq=[('용량은 어떻게 고르나요?','전극이 충분히 잠기고 교반 공간이 남을 정도면 됩니다. 소량 시료라면 30~50 mL, 일반 측정은 100 mL가 무난합니다.'),
      ('전극 구멍을 나중에 늘릴 수 있나요?','유리는 재가공이 어렵습니다. 주문 전에 쓰실 전극의 바깥지름을 확정해 주십시오.'),
      ('전극도 같이 오나요?','오지 않습니다. 작업·기준·상대전극은 각각 별도 주문입니다.'),
      ('온도를 걸 수 있나요?','C002는 개방형이라 항온 재킷이 없습니다. 온도 제어가 필요하면 C003 재킷형을 보십시오.')]))
print('AIDA 셀 1 — C002 %d종'%len(ROWS))
