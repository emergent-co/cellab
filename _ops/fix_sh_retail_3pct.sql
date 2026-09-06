-- 삼흥 판매가를 «정가 × 0.97» 하나로 통일한다 (2026-09-06)
--
-- 배경: 436행 중 335행만 3% 규칙을 따르고 있었고, 나머지 124행은 0%·4~5%·6~7%·8~10% 로
--       제각각이었다. 사이트 문구는 «정가 대비 3% 이상 상시 할인» 인데 실제로 0% 로 받는
--       품목(CVD Gas Flow Package 14종)까지 있었고, 견적을 뽑을 때마다 어느 값이 맞는지
--       계산기를 두드려 확인해야 했다.
--
-- 영향: 124행 — 94행은 가격이 오르고(로터리킬른·튜브전기로 등), 30행은 내린다(CVD 패키지 등).
--       원가 이하로 내려가는 행은 0건. 그래도 아래 마지막 조건으로 한 번 더 막는다.
--
-- 확인 쿼리:
--   SELECT COUNT(*) FROM products WHERE brand='SH Scientific'
--     AND list_price>0 AND retail_price>0 AND retail_price <> CAST(list_price*0.97 AS INTEGER);
UPDATE products
   SET retail_price = CAST(list_price * 0.97 AS INTEGER)
 WHERE brand = 'SH Scientific'
   AND list_price > 0
   AND retail_price > 0
   AND retail_price <> CAST(list_price * 0.97 AS INTEGER)
   -- 안전장치: 어떤 경우에도 매입가 이하로는 내리지 않는다
   AND (supply_price IS NULL OR supply_price <= 0
        OR CAST(list_price * 0.97 AS INTEGER) > supply_price);
