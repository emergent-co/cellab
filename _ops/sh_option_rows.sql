-- _ops/sh_option_rows.sql
-- 삼흥 가스플로 패키지 옵션 6종을 products 테이블에 추가한다.
-- 카탈로그 페이지의 data-d1="<model>" 마커가 이 행들의 retail_price 를 읽어 간다.
--
-- 실행:
--   wrangler d1 execute rndsetup-products --remote --file=_ops/sh_option_rows.sql
--
-- 주의
--   · retail_price 는 silhumsil.com 표기가(VAT 별도) 기준 · 2026-07-28 수집
--   · supply_price 는 미상이라 NULL. admin 에서 채우면 된다.
--   · model 값을 바꾸면 HTML 의 data-d1 도 같이 바꿔야 한다.
--   · SH-SC-5080 / SH-QGD-50 은 삼흥 공식 품번이 확인되지 않아 임시로 부여한 코드다.
--     공식 품번을 확인하면 이 행의 model 과 HTML 의 data-d1 을 함께 교체할 것.

INSERT INTO products
 (sku, group_no, brand, maker, origin, daebun, sobun, model, opt_name, opt_value,
  name, features, unit, supply_price, retail_price, image_url, product_url,
  lead_time, attr1_n, attr1_v, status)
VALUES
 ('SH-MFC-MC', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-MFC-MC', '등급', 'MC (기본)',
  'SH Scientific 가스질량유량계 MFC (Multi gas selectable)',
  '가스 종류별 질량 기준 정밀 유량 투입 | 등급: MC 기본 / MCV +900,000 / MCS +1,300,000 / MCSS +2,140,000',
  'ea', NULL, 3240000, NULL, NULL, '14~21일', '적용', '가스플로 패키지 공통', '등록가능'),

 ('SH-BPR', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-BPR', '등급', 'BPR (기본)',
  'SH Scientific 압력컨트롤러 BPR (Back Pressure Regulator)',
  '튜브 내부 양압 유지(무산소 분위기)·튜브 파손 방지 | 등급: BPR 기본 / BPRS +1,710,000 / BPRSS +2,410,000',
  'ea', NULL, 2630000, NULL, NULL, '14~21일', '적용', '가스플로 패키지 공통', '등록가능'),

 ('SH-HD-MUP', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-HD-MUP', '품목', '이동식 암후드',
  'SH Scientific 이동식 암후드 Mobile Lab Hood SH-HD-MUP',
  '반응가스·분진 국소 배기',
  'ea', NULL, 1160000, NULL, NULL, '14~21일', '적용', '가스플로 패키지 공통', '등록가능'),

 ('SH-SC-5080', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-SC-5080', '품목', '안전 덮개 1SET(좌/우 2개)',
  'SH Scientific 안전 덮개 Safety Cover (튜브로 양끝단 50~80Ø)',
  '반응가스 응축 방지·화상 방지·튜브 파손 방지 | 좌/우 2개 1SET',
  'set', NULL, 900000, NULL, NULL, '14~21일', '적용', '튜브경 50~80Ø', '등록가능'),

 ('SH-QWC-2', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-QWC-2', '규격', '2인치 웨이퍼용',
  'SH Scientific 석영 웨이퍼 캐리어 Quartz wafer carrier 2인치',
  '웨이퍼 시료 거치 | 규격: 2˝ 기본 / 4˝ +170,000 / 6˝ +310,000 / 8˝ +380,000',
  'ea', NULL, 670000, NULL, NULL, '14~21일', '적용', '웨이퍼 2~8인치', '등록가능'),

 ('SH-QGD-50', 900, 'SH Scientific', 'SH Scientific(삼흥에너지)', '대한민국',
  '전기로 옵션', '가스플로 패키지 옵션', 'SH-QGD-50', '규격', '50Φ 튜브용',
  'SH Scientific 석영 디퓨저 Quartz Gas Diffuser 50Φ',
  '가스 확산 균일화 | 튜브경별 규격 상이(50Φ 기준가)',
  'ea', NULL, 300000, NULL, NULL, '14~21일', '적용', '튜브경 50Φ', '등록가능');

-- 확인용
-- SELECT model, name, retail_price, status FROM products WHERE sobun = '가스플로 패키지 옵션';
