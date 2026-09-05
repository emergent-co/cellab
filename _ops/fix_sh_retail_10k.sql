-- 사이트 표시가와 견적서 단가를 한 값으로 맞춘다. (2026-09-05)
--
-- 사이트(_ops/add_buyrail.py 의 disc(), _build/build.py 도 동일):
--     판매가 = int(정가 * 0.97) // 10000 * 10000      ← 3% 할인 + 만원 미만 버림
-- D1 products.retail_price 에는 «만원 버림»이 빠진 채 3% 만 적용된 값이 들어 있었다.
--     예) SH-dVP10  정가 370,000 → 사이트 350,000 / D1 358,900
-- 견적 발행 화면은 D1 값을 그대로 쓰므로, 고객이 본 가격보다 비싼 견적이 나갔다.
--
-- 의도적으로 더 깎아둔 행(대형 퍼니스 등 약 15% 할인, 122건)은 건드리지 않는다.
-- «정확히 3% 만 적용된» 행만 골라 만원 버림을 다시 먹인다. (대상 292건)
UPDATE products
   SET retail_price = CAST(list_price * 0.97 AS INTEGER) / 10000 * 10000
 WHERE brand = 'SH Scientific'
   AND list_price  > 0
   AND retail_price > 0
   AND retail_price =  CAST(list_price * 0.97 AS INTEGER)
   AND retail_price <> CAST(list_price * 0.97 AS INTEGER) / 10000 * 10000;
