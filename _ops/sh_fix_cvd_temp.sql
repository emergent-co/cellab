-- 삼흥 CVD 6종 최고온도 오입력 정정 (2026-09-06)
--
-- 증상 : TH300(1500℃) 3종과 TS300/18(1800℃) 3종의 name·features·sobun·attr1_v 에
--        최고온도가 302 / 305 / 308℃ 로 들어가 있다. 실온 근처 CVD 장비는 없다 —
--        모델명 끝의 «-50TH302» 같은 값을 온도로 잘못 읽어 넣은 흔적이다.
--        sobun 에도 다른 모델명(SH-CVD-50TH302)이 들어가 있었다.
-- 근거 : 같은 계열의 정상행(id 109 SH-CVD-50TH300 = 1500℃, id 125 SH-CVD-50TS300/18 = 1800℃)
--        과 제조사 공식 가격표. TH = 1500℃(SiC), TS = 1700/1800℃(MoSi2) 계열이다.
-- 이력 : claude/rndsetup_제품시스템_핸드오프.md 에 «CVD 6종 302/305/308℃ 오입력» 으로
--        적혀 있던 건이다. 여태 안 고쳐져 있었다.
-- 가격 : 이 파일에서는 손대지 않는다. 별도 판단이 필요한 3행이 있다(아래 주석).

UPDATE products SET
  sobun    = '1500°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1500℃',
  name     = 'SH Scientific CVD로 1500℃ SH-CVD-80TH300',
  features = '1.특징 1500℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1500°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 110 AND model = 'SH-CVD-80TH300';

UPDATE products SET
  sobun    = '1500°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1500℃',
  name     = 'SH Scientific CVD로 1500℃ SH-CVD-100TH300',
  features = '1.특징 1500℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1500°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 111 AND model = 'SH-CVD-100TH300';

UPDATE products SET
  sobun    = '1500°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1500℃',
  name     = 'SH Scientific CVD로 1500℃ SH-CVD-120TH300',
  features = '1.특징 1500℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1500°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 112 AND model = 'SH-CVD-120TH300';

UPDATE products SET
  sobun    = '1800°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1800℃',
  name     = 'SH Scientific CVD로 1800℃ SH-CVD-80TS300/18',
  features = '1.특징 1800℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1800°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 126 AND model = 'SH-CVD-80TS300/18';

UPDATE products SET
  sobun    = '1800°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1800℃',
  name     = 'SH Scientific CVD로 1800℃ SH-CVD-100TS300/18',
  features = '1.특징 1800℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1800°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 127 AND model = 'SH-CVD-100TS300/18';

UPDATE products SET
  sobun    = '1800°C Gas Flow Package (CVD) , 300L 히팅존',
  attr1_v  = '1800℃',
  name     = 'SH Scientific CVD로 1800℃ SH-CVD-120TS300/18',
  features = '1.특징 1800℃ CVD로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 1800°C Gas Flow Package (CVD) , 300L 히팅존 | 3.용도 열처리·소성·회화·시료전처리'
 WHERE id = 128 AND model = 'SH-CVD-120TS300/18';

-- ── 손대지 않은 3행 — 사람이 정해야 한다 ─────────────────────────────
-- id 120 SH-CVD-120TS300/17 : 정가 35,233,000 (÷1.1 = 32,030,000 = 공식가) · 판매가 32,200,000
-- id 127 SH-CVD-100TS300/18 : 정가 33,858,000 (÷1.1 = 30,780,000 = 공식가) · 판매가 30,990,000
-- id 128 SH-CVD-120TS300/18 : 정가 37,686,000 (÷1.1 = 34,260,000 = 공식가) · 판매가 35,000,000
-- 셋 다 정가에 부가세가 붙어 있는데, 부가세를 걷어내면 «판매가 > 정가» 가 된다.
-- 즉 우리가 제조사 공식 정가보다 비싸게 팔고 있다. 어제 _ops/fix_sh_listprice_vat.sql 이
-- 이 3행을 건너뛴 이유도 그 가드였다. 정가를 내릴지 판매가를 내릴지는 마진을 보고 정할 것.
