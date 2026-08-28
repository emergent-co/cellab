# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B

# ── 3. 염화은 기준전극 (단염교)
AG=[('R1038','유리관 Φ3.8 mm · 표준',70000),('R1060-Standard','유리관 Φ6.0 mm · 표준',70000),
    ('R1060-Extended','유리관 Φ6.0 mm · 연장형',70000),('R1038K','유리관 Φ3.8 mm · 갈색 내광형',70000),
    ('R1060K','유리관 Φ6.0 mm · 다갈색 내광형',70000),('PK-1020','PEEK관 Φ2.0 mm',333000),
    ('PK-1038','PEEK관 Φ3.8 mm',333000),('이중접점형','이중 접점',228000)]
B.build(dict(slug='agcl-reference-electrode', cat='기준전극',
 h1='염화은 기준전극 (단염교)', sub='Ag/AgCl · 중성 전해액',
 title='가오스유니온 염화은 기준전극 Ag/AgCl 단염교 — 유리 Φ3.8/6.0 · PCTFE · PEEK Φ2.0 | 실험셋업연구소',
 desc='가오스유니온 염화은(Ag/AgCl) 기준전극 단염교형 — 중성 전해액 전기화학 측정용. 1038형 유리관 Φ3.8 mm, 1060형 유리관 Φ6.0 mm, 2060형 PCTFE관 Φ6.0 mm, 1020형 PEEK관 Φ2.0 mm. 내광형·PEEK 로드 사양 선택. 정가 70,000원부터.',
 ldname='염화은 기준전극 단염교 (Ag/AgCl Reference Electrode, Single Salt Bridge)',
 answer='염화은 기준전극은 <b>중성 전해액</b>에서 쓰는 표준 기준전극입니다. 관 재질과 지름으로 사양이 갈립니다.',
 summary='<b>중성 전해액</b>용 · 1038형 유리 <b>Φ3.8</b> / 1060형 유리 <b>Φ6.0</b> / 2060형 <b>PCTFE Φ6.0</b> / 1020형 <b>PEEK Φ2.0</b> · 70,000원부터',
 quote='가오스유니온 염화은 기준전극 (단염교)',
 imgs=['agcl-reference-electrode-1.jpg','agcl-reference-electrode-2.jpg','agcl-reference-electrode-3.jpg','agcl-reference-electrode-4.jpg'], models=[m for m,_,_ in AG],
 feat=['<b>중성 전해액</b>이 기본 적용 범위입니다. 산성은 <a href="/brands/gaossunion/hg2so4-reference-electrode/">황산제일수은</a>, 알칼리는 <a href="/brands/gaossunion/hgo-reference-electrode/">산화수은</a>을 쓰십시오',
       '<b>세경 Φ2.0 mm(PEEK)</b>까지 있어 좁은 셀이나 마이크로 셀에도 넣을 수 있습니다',
       '<b>내광형(K)</b>은 갈색 유리라 광전기화학처럼 조사광이 있는 셋업에서 광분해를 막습니다',
       '염화물 이온이 실험을 방해하면 <a href="/brands/gaossunion/agcl-reference-double/">이중염교형(R8060)</a>을 쓰십시오'],
 spec=[('적용 용액','<b>중성</b> 전해액'),
       ('1038형','유리관 <b>Φ3.8 mm</b>'),('1060형','유리관 <b>Φ6.0 mm</b>'),
       ('2060형','<b>PCTFE(삼불화)관</b> Φ6.0 mm'),('1020형','<b>PEEK관</b> Φ2.0 mm'),
       ('내광 사양','R1038K 갈색 · R1060K 다갈색'),('충전액','포화 염화칼륨')],
 price=B.rows_by(sobun='기준전극', name_has='염화은'),
 cross='기준전극 계열: <a href="/brands/gaossunion/agcl-reference-double/">이중염교</a> · <a href="/brands/gaossunion/sce-reference-electrode/">포화칼로멜</a> · <a href="/brands/gaossunion/hgo-reference-electrode/">산화수은</a> · <a href="/brands/gaossunion/hg2so4-reference-electrode/">황산제일수은</a> · <a href="/brands/gaossunion/ag-agion-reference-electrode/">은-은이온</a>',
 faq=[('산성이나 알칼리 용액에도 쓸 수 있나요?','원칙적으로는 중성용입니다. 산성·알칼리에서 쓰려면 염다리로 분리해 충전액과 시료액이 직접 섞이지 않게 하십시오. 아예 조건에 맞는 전극(산성 황산제일수은, 알칼리 산화수은)을 쓰는 편이 전위가 안정됩니다.'),
      ('PEEK관(PK-1020·PK-1038)은 왜 비싼가요?','유리 대신 PEEK로 만들면 깨질 위험이 없고 불소 함유 용액에서도 견딥니다. 좁은 셀에 넣을 수 있는 Φ2.0 mm 세경도 PEEK 사양입니다.'),
      ('내광형은 어떤 경우에 필요한가요?','광전기화학이나 광촉매 실험처럼 셀에 빛을 쬐는 셋업입니다. 투명 유리관이면 내부 충전액과 은/염화은 계면이 광분해돼 전위가 흐를 수 있습니다.'),
      ]))

# ── 4. 백금선 상대전극
PW=[('PT0537','Φ0.5 × 37 mm 노출',175000),('PT1037','Φ1.0 × 37 mm 노출',665000)]
B.build(dict(slug='pt-wire-counter-electrode', cat='상대전극',
 h1='백금선 상대전극', sub='Φ0.5 · Φ1.0 × 37 mm · 순도 99.99%',
 title='가오스유니온 백금선 상대전극 — Φ0.5/1.0 × 37 mm · 순도 99.99% | 실험셋업연구소',
 desc='가오스유니온 백금선 상대전극(Platinum Wire Electrode) — 규격 Φ0.5 mm × 37 mm, Φ1.0 mm × 37 mm. 순도 99.99%, 외피 PTFE. 정가 175,000원부터.',
 ldname='백금선 상대전극 (Platinum Wire Counter Electrode)',
 answer='백금선은 좁은 셀이나 소량 전해액에서 쓰는 가장 단순한 상대전극입니다.',
 summary='<b>Φ0.5 × 37 mm</b> / <b>Φ1.0 × 37 mm</b> · 순도 <b>99.99%</b> · 외피 PTFE · 175,000원부터',
 quote='가오스유니온 백금선 상대전극',
 imgs=['pt-wire-counter-electrode-1.jpg'], models=[m for m,_,_ in PW],
 feat=['<b>좁은 셀·소량 전해액</b>에 넣기 쉬운 형상입니다',
       '표면적이 작아 <b>큰 전류에는 불리</b>합니다 — 그때는 <a href="/brands/gaossunion/pt-mesh-counter-electrode/">백금망</a>이나 <a href="/brands/gaossunion/pt-plate-counter-electrode/">백금판</a>',
       '길이 <b>230 mm 나선형</b>이 필요하면 <a href="/brands/gaossunion/pt-wire-spiral-counter-electrode/">나선 백금선</a>',
       '상대전극 생성물이 작업전극에 닿으면 안 되는 실험은 <a href="/brands/gaossunion/pt-wire-with-salt-bridge/">염다리형</a>'],
 spec=[('재질 · 순도','백금 <b>99.99%</b>'),('규격','<b>Φ0.5 × 37 mm</b> · <b>Φ1.0 × 37 mm</b>'),
       ('외피','<b>PTFE</b>'),('용도','상대전극(대향전극)')],
 price=[r for r in B.rows_by(sobun='상대전극', name_has='백금선 전극') if r[0] in ('PT0537','PT1037')],
 cross='상대전극 계열: <a href="/brands/gaossunion/pt-plate-counter-electrode/">백금판</a> · <a href="/brands/gaossunion/pt-mesh-counter-electrode/">백금망</a> · <a href="/brands/gaossunion/graphite-rod-counter-electrode/">흑연봉</a>',
 faq=[('Φ0.5와 Φ1.0 중 무엇을 고르나요?','흘릴 전류로 정하십시오. 표면적이 두 배 차이 나므로 전류 밀도가 높은 실험이면 Φ1.0이 안전합니다. 다만 가격 차이가 큽니다.'),
      ('나선형과 무엇이 다른가요?','나선형은 백금선 길이가 230 mm로 훨씬 길어 표면적이 큽니다. 회전전극 장비와 함께 쓰도록 PEEK 봉에 달려 나옵니다. 이 페이지의 직선형은 37 mm입니다.'),
      ('표에 없는 규격도 되나요?','제작 가능한 범위가 있습니다. 필요 규격을 알려주시면 안내드립니다.')]))

# ── 5. RDE 외나사
RDE=[('GC 유리탄소 Φ5mm','디스크 Φ5.0 mm · 전극 외경 15 mm',1050000),
     ('PT 백금 Φ5mm','디스크 Φ5.0 mm · 전극 외경 15 mm',1645000),
     ('AU 금 Φ5mm','디스크 Φ5.0 mm · 전극 외경 15 mm',2800000)]
B.build(dict(slug='rde-external-thread', cat='회전전극',
 h1='회전원판전극 RDE (외나사)', sub='디스크 Φ5.0 mm · 전극 외경 15 mm',
 title='가오스유니온 회전원판전극 RDE 외나사형 — GC·Pt·Au Φ5 mm | 실험셋업연구소',
 desc='가오스유니온 회전원판전극(RDE) 외나사형 — 디스크 재질 유리탄소(GC)·금(AU)·백금(PT), 봉 재질 PTFE·PEEK, 디스크 직경 5.0 mm, 전극 외경 15 mm, 사용 온도 10~25℃. PTFE 봉지로 내식성이 좋아 농산 계에서도 작동. 정가 1,050,000원부터.',
 ldname='회전원판전극 RDE 외나사형 (Rotating Disk Electrode, External Thread)',
 answer='회전원판전극은 전극을 일정 속도로 돌려 물질 전달을 계산 가능한 상태로 만드는 장치입니다. ORR·HER 촉매 활성 평가의 표준입니다.',
 summary='디스크 <b>GC · Pt · Au Φ5.0 mm</b> · 전극 외경 <b>15 mm</b> · 봉 PTFE·PEEK · 사용 온도 10~25℃ · 1,050,000원부터',
 quote='가오스유니온 회전원판전극 RDE (외나사)',
 imgs=['rde-external-thread-1.jpg','rde-external-thread-2.jpg','rde-external-thread-3.jpg'], models=[m for m,_,_ in RDE],
 feat=['<b>외나사 설계</b>라 접촉이 좋고 신호 전달이 안정적입니다',
       '<b>PTFE 봉지</b>로 내화학성이 좋아 <b>농산(濃酸) 계</b>에서도 작동합니다',
       '재료 밀도가 균일해 <b>전극마다 특성이 같습니다</b> — 반복 실험의 재현성',
       '내나사형은 전극 외경이 <b>12 mm</b>입니다 — <a href="/brands/gaossunion/rde-internal-thread/">내나사형</a>과 장비 규격을 확인하십시오'],
 spec=[('디스크 재질','<b>GC(유리탄소) · AU(금) · PT(백금)</b> 등'),
       ('봉 재질','<b>PTFE · PEEK</b>'),('디스크 직경','<b>Φ5.0 mm</b>'),
       ('전극 외경','<b>15 mm</b>'),('사용 온도','<b>10 ~ 25 ℃</b>'),
       ('나사 방식','<b>외나사</b>')],
 price=RDE,
 warn='<b>장비 호환 확인 필요</b> — 외나사/내나사는 회전전극 구동부 규격에 맞아야 합니다. 보유 장비 제조사와 모델을 알려주시면 맞는 쪽을 안내드립니다.',
 cross='회전전극 계열: <a href="/brands/gaossunion/rde-internal-thread/">RDE 내나사</a> · <a href="/brands/gaossunion/rrde/">RRDE</a> · <a href="/brands/gaossunion/rde-high-temp/">내고온 RDE</a>',
 faq=[('외나사와 내나사 중 무엇을 골라야 하나요?','회전전극 구동부(로테이터)의 축 규격에 맞춰야 합니다. 외나사는 전극 외경 15 mm, 내나사는 12 mm입니다. 보유 장비 모델을 알려주시면 확인해 드립니다.'),
      ('디스크 재질은 어떻게 고르나요?','ORR 촉매 평가는 유리탄소가 기본입니다. 촉매 잉크를 얹어 쓰기 때문입니다. 금·백금은 그 자체의 전극 반응을 볼 때 씁니다.'),
      ('회전 속도는 어디까지 되나요?','전극이 아니라 로테이터(구동부) 사양에 달렸습니다. 이 페이지는 전극만 판매합니다. 구동부는 <a href="/brands/gaossunion/rde-rotator/">회전전극 장치</a>를 보십시오.'),
      ('표에 없는 규격도 되나요?','제작 가능한 범위가 있습니다. 필요 규격을 알려주시면 안내드립니다.')]))
print('3장 생성')
