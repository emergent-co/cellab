# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_web as B

# 1. 표준 유리탄소(GC) 작업전극
B.build(dict(slug='gc-disc-working-electrode', cat='작업전극',
 h1='표준 유리탄소(GC) 작업전극', sub='Φ1~10 mm · 미국·일본산 유리탄소',
 title='가오스유니온 표준 유리탄소(GC) 작업전극 — Φ1~10 mm · 외피 PTFE/PEEK/PCTFE | 실험셋업연구소',
 desc='가오스유니온 표준 유리탄소(GC) 작업전극 — 유리탄소 직경 Φ1·2·3·4·5·6·7·8·10 mm(길이 5~10 mm), 미국·일본산 유리탄소. 외피 PTFE·PEEK·PCTFE, 외피 직경 3~17 mm, 전극 총장 75 mm(연장 가능), 꼬리 금도금 도선주.',
 ldname='표준 유리탄소 작업전극 (Standard Glassy Carbon Working Electrode)',
 answer='유리탄소는 가장 널리 쓰이는 작업전극 재료입니다. 넓은 전위창과 낮은 배경전류를 가지며, 연마해 반복 사용합니다.',
 summary='유리탄소 <b>Φ1~10 mm</b> · 외피 <b>PTFE·PEEK·PCTFE</b> Φ3~17 mm · 전극 총장 75 mm(연장 가능) · 꼬리 <b>금도금 도선주</b>',
 quote='가오스유니온 표준 유리탄소(GC) 작업전극',
 imgs=['gc-disc-working-electrode-1.jpg','gc-disc-working-electrode-2.jpg'],
 models=['Φ1mm','Φ2mm','Φ3mm','Φ4mm','Φ5mm','Φ6mm','Φ7mm','Φ8mm','Φ10mm'],
 feat=['<b>유리탄소(glassy carbon)</b>는 전위창이 넓고 배경전류가 낮아 순환전압전류법의 기본 작업전극입니다',
       '연마해 표면을 되살려 <b>반복 사용</b>합니다 — <a href="/brands/gaossunion/electrode-polishing/">전극 연마용품</a>',
       '외피를 <b>PCTFE·PEEK</b>로 고르면 유기 용매나 불소 함유 용액에서 팽윤·침투를 줄일 수 있습니다',
       '전극 꼬리가 <b>금도금 도선주</b>라 접촉 저항이 늘지 않습니다'],
 spec=[('유리탄소 직경','<b>Φ1 · 2 · 3 · 4 · 5 · 6 · 7 · 8 · 10 mm</b> — 길이 5~10 mm'),
       ('유리탄소 원산지','<b>미국 · 일본</b>'),
       ('외피 재질','<b>PTFE · PEEK · PCTFE</b>'),
       ('외피 직경','3 mm ~ 17 mm'),
       ('전극 총장','<b>75 mm</b> (연장 가능)'),
       ('외피 길이','60 mm'),
       ('전극 꼬리','<b>금도금 도선주</b>')],
 price=None,
 cross='작업전극 계열: <a href="/brands/gaossunion/pt-disc-working-electrode/">백금 디스크</a> · <a href="/brands/gaossunion/au-disc-working-electrode/">금 디스크</a>',
 faq=[('유리탄소 전극은 왜 연마하나요?','표면이 오염되거나 산화되면 전류 응답이 흐려집니다. 알루미나 슬러리로 거울면까지 연마하면 초기 상태에 가깝게 돌아옵니다. 측정 전마다 연마하는 것이 표준 절차입니다.'),
      ('외피 재질은 어떻게 고르나요?','일반 수용액이면 PTFE로 충분합니다. 유기 용매나 불소 함유 용액, 고온 조건이면 PEEK 또는 PCTFE를 권합니다. 외피와 유리탄소 사이로 용액이 스며들면 측정값이 흔들립니다.'),
      ('원하는 직경이 목록에 없는데요?','Φ1~10 mm 외 규격과 외피 조합도 제작됩니다. 필요 규격을 알려주시면 안내드립니다.')]))

# 2. 백금판 상대전극 — SQL 34행 전량
B.build(dict(slug='pt-plate-counter-electrode', cat='상대전극',
 h1='백금판 상대전극', sub='순도 99.99% · 5×2 ~ 30×30 mm',
 title='가오스유니온 백금판 상대전극 — 순도 99.99% · 두께 0.1~0.5 mm 34종 | 실험셋업연구소',
 desc='가오스유니온 백금판 상대전극(Platinum electrodes) — 순도 99.99%, 두께 0.1·0.2·0.3·0.5 mm, 백금판 규격 5×2 / 5×5 / 5×10 / 10×10 / 10×15 / 10×20 / 10×30 / 15×15 / 20×20 / 30×30 mm 34종. 외피 PTFE. 88,000원부터.',
 ldname='백금판 상대전극 (Platinum Plate Counter Electrode)',
 answer='상대전극은 작업전극에 흐르는 전류를 받아 주는 짝입니다. 백금판은 면적이 넓어 전류 밀도를 낮게 유지하며, 가장 널리 쓰입니다.',
 summary='순도 <b>99.99%</b> · 두께 <b>0.1 · 0.2 · 0.3 · 0.5 mm</b> · 규격 <b>5×2 ~ 30×30 mm</b> 34종 · 외피 PTFE · 88,000원부터',
 quote='가오스유니온 백금판 상대전극',
 imgs=['pt-plate-counter-electrode-1.jpg'],
 models=[m for m,_,_ in B.rows_by(sobun='상대전극', name_has='백금판')],
 feat=['<b>작업전극보다 충분히 넓은 면적</b>을 잡아야 상대전극 쪽이 반응 속도를 제한하지 않습니다',
       '백금 순도 <b>99.99%</b>. 표에 없는 치수도 <b>주문 제작</b>됩니다',
       '장시간 산화 조건에서는 백금이 미량 녹아 작업전극에 재석출될 수 있습니다 — <a href="/brands/gaossunion/graphite-rod-counter-electrode/">흑연봉</a>이나 <a href="/brands/gaossunion/pt-wire-with-salt-bridge/">염다리형</a>을 쓰십시오',
       '두께가 두꺼울수록 기계적으로 튼튼하고 반복 사용에 유리합니다'],
 spec=[('재질 · 순도','백금 <b>99.99%</b>'),('두께','<b>0.1 · 0.2 · 0.3 · 0.5 mm</b>'),
       ('백금판 규격','5×2 · 5×5 · 5×10 · 10×10 · 10×15 · 10×20 · 10×30 · 15×15 · 20×20 · 30×30 mm'),
       ('외피','<b>PTFE</b>'),('용도','상대전극(대향전극)')],
 price=B.rows_by(sobun='상대전극', name_has='백금판'),
 cross='상대전극 계열: <a href="/brands/gaossunion/pt-mesh-counter-electrode/">백금망</a> · <a href="/brands/gaossunion/pt-wire-counter-electrode/">백금선</a> · <a href="/brands/gaossunion/graphite-rod-counter-electrode/">흑연봉</a>',
 faq=[('상대전극 면적은 얼마나 커야 하나요?','작업전극 면적의 최소 몇 배 이상을 권합니다. 상대전극이 좁으면 그쪽 반응이 전체 전류를 제한해 작업전극의 거동을 제대로 못 봅니다.'),
      ('백금판과 백금망 중 무엇이 좋나요?','같은 겉넓이라면 망이 실효 면적이 훨씬 큽니다. 큰 전류를 흘리는 실험이면 망, 일반적인 CV·LSV면 판으로 충분합니다.'),
      ('두께는 어떻게 고르나요?','전기화학적으로는 차이가 없습니다. 두꺼울수록 휘지 않고 오래 쓰지만 가격이 올라갑니다. 반복 탈착이 잦으면 0.2 mm 이상을 권합니다.'),
      ('백금이 작업전극을 오염시킨다는데요?','장시간 산화 전위에서 백금이 미량 용출돼 작업전극 표면에 재석출될 수 있습니다. 특히 수소 발생 반응 연구에서 문제가 됩니다. 흑연봉 상대전극을 쓰거나 염다리로 분리하십시오.')]))
print('2장')
