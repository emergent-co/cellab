-- 삼흥 온도등급이 모델명을 공유하던 15행 분리 + 정가 부가세 보정 (2026-09-06)
--
-- 배경 : SH-FU-4MS/11MS/22MS · 2MSU/4MSU/6MSU 는 1700/1800/1900℃ 등급이 같은 model 값을
--        써서 _middleware.js 가 «같은 model 이 2행 이상이면 주입 안 함» 으로 막고 있었고,
--        견적 자동완성에서도 온도를 구분할 수 없었다.
-- 표기 : 공식 가격표(실험실닷컴)가 쓰는 «모델명+온도» 를 따른다. MS 계열은 공식표 그대로,
--        엘레베이터(MSU)는 공식표가 1700만 싣고 온도를 안 붙이지만 규칙을 하나로 두려고
--        1700/1800 양쪽에 붙였다.
-- 가격 : 15행 중 11행이 list_price 에 부가세가 붙어 있었다(÷1.1 이 공식표와 정확히 일치).
--        id 41(22MS 1900)은 28,700,000 이 이미 공식 정가이고 %11≠0 이라 손대지 않는다.
--        id 45/46/47(MSU 1700)은 list_price 가 비어 있어 공식표 값을 채운다.
--        retail_price 는 건드리지 않는다 — 이미 보정 후 정가 대비 3% 안팎이고,
--        일부러 더 깎아 둔 행이 섞여 있다.
-- 가드 : 보정 후 판매가 ≤ 정가 11/11, 판매가 > 매입가 15/15 확인함.

-- ── 1) 정가에서 부가세 걷어내기 (11행) ─────────────────────────────
UPDATE products SET list_price = 12000000 WHERE id = 33 AND list_price = 13200000;
UPDATE products SET list_price = 14900000 WHERE id = 34 AND list_price = 16390000;
UPDATE products SET list_price = 21700000 WHERE id = 35 AND list_price = 23870000;
UPDATE products SET list_price = 14270000 WHERE id = 36 AND list_price = 15697000;
UPDATE products SET list_price = 18350000 WHERE id = 37 AND list_price = 20185000;
UPDATE products SET list_price = 24530000 WHERE id = 38 AND list_price = 26983000;
UPDATE products SET list_price = 15600000 WHERE id = 39 AND list_price = 17160000;
UPDATE products SET list_price = 19800000 WHERE id = 40 AND list_price = 21780000;
UPDATE products SET list_price = 16260000 WHERE id = 48 AND list_price = 17886000;
UPDATE products SET list_price = 18230000 WHERE id = 49 AND list_price = 20053000;
UPDATE products SET list_price = 20080000 WHERE id = 50 AND list_price = 22088000;

-- ── 2) 비어 있던 정가 채우기 (공식표 1700℃ Elevator) ────────────────
UPDATE products SET list_price = 15000000 WHERE id = 45 AND list_price IS NULL;
UPDATE products SET list_price = 16550000 WHERE id = 46 AND list_price IS NULL;
UPDATE products SET list_price = 18400000 WHERE id = 47 AND list_price IS NULL;

-- ── 3) 잘못 박힌 분류·이름 (MSU 1700 3행) ──────────────────────────
--     sobun 이 «Ciller for 2400/3000 전기로» 로 들어가 있었다. 엘레베이터로다.
UPDATE products SET sobun = '1700℃ 전기로, Elevator Type',
       features = '1.특징 1700℃ 엘레베이터로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1700℃ 전기로, Elevator Type, automatic door up/down | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id IN (45, 46, 47);

-- ── 4) 모델명·SKU·이름에 온도 붙이기 (15행) ─────────────────────────
UPDATE products SET model='SH-FU-4MS1700',  sku='SH-FU-4MS1700',  opt_value='SH-FU-4MS1700 (4.5L)',  name='SH Scientific 전기로 1700℃ 4.5L SH-FU-4MS1700'  WHERE id=33;
UPDATE products SET model='SH-FU-11MS1700', sku='SH-FU-11MS1700', opt_value='SH-FU-11MS1700 (11L)', name='SH Scientific 전기로 1700℃ 11L SH-FU-11MS1700'  WHERE id=34;
UPDATE products SET model='SH-FU-22MS1700', sku='SH-FU-22MS1700', opt_value='SH-FU-22MS1700 (22L)', name='SH Scientific 전기로 1700℃ 22L SH-FU-22MS1700'  WHERE id=35;
UPDATE products SET model='SH-FU-4MS1800',  sku='SH-FU-4MS1800',  opt_value='SH-FU-4MS1800 (4.5L)',  name='SH Scientific 전기로 1800℃ 4.5L SH-FU-4MS1800'  WHERE id=36;
UPDATE products SET model='SH-FU-11MS1800', sku='SH-FU-11MS1800', opt_value='SH-FU-11MS1800 (11L)', name='SH Scientific 전기로 1800℃ 11L SH-FU-11MS1800'  WHERE id=37;
UPDATE products SET model='SH-FU-22MS1800', sku='SH-FU-22MS1800', opt_value='SH-FU-22MS1800 (22L)', name='SH Scientific 전기로 1800℃ 22L SH-FU-22MS1800'  WHERE id=38;
UPDATE products SET model='SH-FU-4MS1900',  sku='SH-FU-4MS1900',  opt_value='SH-FU-4MS1900 (4.5L)',  name='SH Scientific 전기로 1900℃ 4.5L SH-FU-4MS1900'  WHERE id=39;
UPDATE products SET model='SH-FU-11MS1900', sku='SH-FU-11MS1900', opt_value='SH-FU-11MS1900 (11L)', name='SH Scientific 전기로 1900℃ 11L SH-FU-11MS1900'  WHERE id=40;
UPDATE products SET model='SH-FU-22MS1900', sku='SH-FU-22MS1900', opt_value='SH-FU-22MS1900 (22L)', name='SH Scientific 전기로 1900℃ 22L SH-FU-22MS1900'  WHERE id=41;
UPDATE products SET model='SH-FU-2MSU1700', sku='SH-FU-2MSU1700', opt_value='SH-FU-2MSU1700 (2.2L)', name='SH Scientific 엘레베이터로 1700℃ 2.2L SH-FU-2MSU1700' WHERE id=45;
UPDATE products SET model='SH-FU-4MSU1700', sku='SH-FU-4MSU1700', opt_value='SH-FU-4MSU1700 (3.8L)', name='SH Scientific 엘레베이터로 1700℃ 3.8L SH-FU-4MSU1700' WHERE id=46;
UPDATE products SET model='SH-FU-6MSU1700', sku='SH-FU-6MSU1700', opt_value='SH-FU-6MSU1700 (6.2L)', name='SH Scientific 엘레베이터로 1700℃ 6.2L SH-FU-6MSU1700' WHERE id=47;
UPDATE products SET model='SH-FU-2MSU1800', sku='SH-FU-2MSU1800', opt_value='SH-FU-2MSU1800 (2.2L)', name='SH Scientific 엘레베이터로 1800℃ 2.2L SH-FU-2MSU1800' WHERE id=48;
UPDATE products SET model='SH-FU-4MSU1800', sku='SH-FU-4MSU1800', opt_value='SH-FU-4MSU1800 (3.8L)', name='SH Scientific 엘레베이터로 1800℃ 3.8L SH-FU-4MSU1800' WHERE id=49;
UPDATE products SET model='SH-FU-6MSU1800', sku='SH-FU-6MSU1800', opt_value='SH-FU-6MSU1800 (6.2L)', name='SH Scientific 엘레베이터로 1800℃ 6.2L SH-FU-6MSU1800' WHERE id=50;
