# Hench 파이프라인 (2026-09 중문 기준 재구성)

사양의 1차 출처는 **제조사 중문 사이트**다. 영문판은 구 리비전이고 산술적으로 성립하지 않는 값이 다수라
어긋날 때는 중문을 따른다.

## 실행 순서

```
python cn_parse.py    # hench_cn_raw.json  -> hench_cn.json   (라벨 어휘 기반 파싱)
python merge.py       # 영문 119종 x 중문 164종 매칭 -> hench_master.json
python cn_spec.py     # 중문 사양을 영문 키 + 한국어 값으로 -> hench_products.csv (+ 신규 49행)
python gen_models.py  # YP 6종 + HMY 11밴드 (17장)
python gen_rest.py    # 나머지 151장 + 허브
python verify_cn.py   # 압력 x 실린더 면적 = 하중 검산
python ..\..\_build\build.py
```

`hench_products_en.csv` 가 영문 원본이다. `cn_spec.py` 는 매 실행마다 여기서 다시 시작하므로
`hench_products.csv` 를 손으로 고치지 말 것.

## 파일

| 파일 | 역할 |
|---|---|
| `hench_cn_raw.json` | 중문 상세 원문(브라우저 same-origin fetch 수집) |
| `cn_parse.py` | 콜론 없는 중문 사양표를 라벨 어휘로 끊는다 |
| `cn_ko.py` | 중문 라벨/값 -> 한국어. 사전에 없어 한자가 남으면 **싣지 않는다** |
| `merge.py` | 슬러그/모델/다이 밴드 대응표로 영문 행 <-> 중문 레코드 연결 |
| `cn_spec.py` | 중문 우선 병합 + 제조사 오기 교정표(CORR) + 신규 49행 |
| `newmap.py` | 중문 전용 신규 49종의 계열/슬러그/한국어명 확정표 |
| `verify_cn.py` | T = MPa x pi d^2/4 / 9806.65 검산 |

## 확인된 제조사 오기 (영문판)

- 40T 수동기: 모델명 `YP-30`, 압력 `0-30T` -> 실제 **YP-40 / 0-40T(0-30MPa)**, 실린더 Φ130
- `YP-15B`: `0-35MPa` -> **0-30MPa** (Φ80 x 35MPa = 17.9T 로 15T 기기에서 불가능)
- `YP-12`: `0-15T` -> **0-12T(0-30MPa)**
- 다이 재질/경도: `ASSAB+17 / Cr12MoV, HRC68~70` -> **9Cr18 / HRC58** (HMY-G 만 3Cr13)
- 작업대 직경·외형 높이·중량이 전 기종에서 중문이 크다 = 영문판이 구 리비전

## 중문판 자체 오기 (CORR 로 교정)

- `YP-60FS` 압력범위 `0-35=4Mpa` -> `0-34MPa` (동일 60T 기종 YP-60F, 자체 환산 1MPa=1.76T)
- `YP-30J/S` 압력범위 `0-30T/3.15Mpa` -> `0-30T/31.5MPa` (자체 환산 1MPa=0.95T)

## 미해결

- `YP-30J/S`: 표기 30T vs 피스톤 Φ100 x 31.5MPa = 25.2T (16% 차). 피스톤 지름 또는 톤수 확인 필요.
- `YP-20J/S`(20T 수동 등정압), `HDP-20J`(20T 전동 등정압), `HMC`(눈금 원통 다이): 중문판에 없다. 영문 값 유지 — 단종 여부 확인 필요.
- 가격: 전 품목 견적. 제조사 견적 또는 국내 비교 표본이 필요하다.
