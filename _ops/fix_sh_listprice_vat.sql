-- 삼흥 전기로 계열 정가에서 부가세를 걷어낸다 (2026-09-05)
--
-- 증상: 사이트·견적서에 «정가 44,880,000원 VAT 별도 · 15.3% 할인» 으로 찍혔다.
--       삼흥 공식 판매가는 40,800,000원(VAT 별도)이고 우리 판매가 38,000,000 은 6.9% 할인이다.
--       즉 판매가는 멀쩡한데 정가(list_price)에 ×1.1 이 들어가 할인율이 부풀어 보였다.
--
-- 근거: 프로젝트 문서 claude/sh_실험실닷컴_재스크랩_데이터.md (실험실닷컴 표시가 = 공식 정가)
--       와 대조해 «현재 정가 ÷ 1.1 = 공식 정가» 가 48건 전부 정확히 일치했다.
--
-- 판별: ① 3% 정상행이 아니고  ② 정가가 11로 나눠떨어지고(×1.1 흔적)
--       ③ 보정값이 천원 단위이고  ④ 보정 후에도 판매가 ≤ 정가
--       ⑤ 온도등급이 모델명을 공유해 가격이 여러 개인 6종은 제외(대조 불가)
-- 대상 99건. 보정 후 할인율 0~9.7%, 마진 10% 미만 0건.
--
-- 적용 전 확인:
--   SELECT model, list_price, list_price/11*10 AS 보정, retail_price FROM products
--    WHERE brand='SH Scientific' AND list_price>0 AND retail_price>0
--      AND retail_price <> CAST(list_price*0.97 AS INTEGER)
--      AND list_price % 11 = 0 AND (list_price/11*10) % 1000 = 0
--      AND retail_price <= list_price/11*10
--      AND model NOT IN ('SH-FU-4MS','SH-FU-11MS','SH-FU-22MS','SH-FU-2MSU','SH-FU-4MSU','SH-FU-6MSU');
UPDATE products
   SET list_price = list_price / 11 * 10
 WHERE brand = 'SH Scientific'
   AND list_price > 0 AND retail_price > 0
   AND retail_price <> CAST(list_price * 0.97 AS INTEGER)
   AND list_price % 11 = 0
   AND (list_price / 11 * 10) % 1000 = 0
   AND retail_price <= list_price / 11 * 10
   AND model NOT IN ('SH-FU-4MS','SH-FU-11MS','SH-FU-22MS','SH-FU-2MSU','SH-FU-4MSU','SH-FU-6MSU');
