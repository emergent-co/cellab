# `rndsetup_products.sql` 행 형식

파일은 `-- product rows` 주석 뒤에 `INSERT INTO products (...) VALUES (...);` 가 **한 줄에 하나씩** 이어진다.
새 제품은 **파일 끝에 추가**한다. 기존 행은 건드리지 않는다.

## 열 순서 (30개, 고정)

```
sku, group_no, brand, maker, origin, daebun, sobun, model, opt_name, opt_value,
name, features, detail, unit, supply_price, retail_price, image_url, product_url,
lead_time, cert, stock, attr1_n, attr1_v, attr2_n, attr2_v, attr3_n, attr3_v,
attr4_n, attr4_v, status
```

## 실제 행 예시 (줄바꿈 없이 한 줄로 쓸 것)

```sql
INSERT INTO products (sku,group_no,brand,maker,origin,daebun,sobun,model,opt_name,opt_value,name,features,detail,unit,supply_price,retail_price,image_url,product_url,lead_time,cert,stock,attr1_n,attr1_v,attr2_n,attr2_v,attr3_n,attr3_v,attr4_n,attr4_v,status) VALUES ('SH-FU-3MGE',1,'SH Scientific','SH Scientific(삼흥에너지)','대한민국','전기로','ECO 1050℃ 전기로','SH-FU-3MGE','모델/용량','SH-FU-3MGE (3L)','SH Scientific 전기로 1050℃ 3L SH-FU-3MGE','1.특징 1050℃ 전기로, 프로그램/PID 제어, 균일 온도분포 | 2.형식 ECO 1050℃ 전기로 | 3.용도 열처리·소성','','ea',<공급가>,<정가>,'<이미지 URL>','<상세페이지 URL>','','','', '','','','','','','','','판매중');
```

## 값 규칙

| 열 | 규칙 |
|---|---|
| `sku` | 제조사 모델코드. 중복 금지. **가격 매칭 키**로 쓰이므로 임의 변형 금지 |
| `group_no` | 같은 시리즈끼리 같은 번호. 새 시리즈면 기존 최대값 + 1 |
| `brand` | 영문 브랜드명 (`SH Scientific`, `Leadfluid`, `Alicat`) |
| `maker` | `영문명(한글명)` |
| `daebun` / `sobun` | 대분류 / 소분류. **기존 어휘 재사용 필수** — 새 어휘를 만들면 `build_prices()`의 최저가 매칭에서 빠진다 |
| `model` | 모델명. 시리즈+옵션 조합이면 `본체+옵션코드` 형태 (예: `CT3001S+MG204XD0PT00000`) |
| `opt_name` / `opt_value` | 옵션 축 이름 / 값 (예: `모델/용량` / `SH-FU-3MGE (3L)`) |
| `name` | 검색용 전체 이름 (브랜드 + 종류 + 사양 + 모델) |
| `features` | `1.특징 … \| 2.형식 … \| 3.용도 …` 파이프 구분 |
| `unit` | 거의 항상 `'ea'` — **`build_prices()`가 `'ea',공급가,정가,` 패턴으로 가격을 읽으므로 바꾸지 말 것** |
| `supply_price` / `retail_price` | 정수, 원 단위, 따옴표 없음. `retail_price` = **정가** |
| `status` | `'판매중'` |

## 가격이 사이트에 반영되는 경로

```
rndsetup_products.sql (정가)
   └─ build_prices()  ── 카테고리/모델별 최저 정가 산출
        └─ DISCOUNT_RATE = 0.97 (3% 할인) + 만원 미만 버림
             ├─ index.html  <span data-price="키">
             └─ assets/site.js  /*P:키*/'...'
```

새 카테고리를 홈 시작가로 노출하고 싶으면 `build_prices()`의 `prices` 딕셔너리에 키를 1줄 추가하고,
`index.html`에 `<span data-price="새키">…</span>` 또는 `site.js`에 `/*P:새키*/'…'` 마커를 둔다.
**매칭은 `sku` 뿐 아니라 `model` 열도 본다** (`'CT3001' in r['sku'] or 'CT3001' in r['model']`).

## 검증

```bash
python - <<'PY'
import re, io
t = io.open('rndsetup_products.sql', encoding='utf-8').read()
rows = [l for l in t.splitlines() if l.startswith('INSERT INTO products')]
pat = re.compile(r"VALUES \('([^']*)',\d+,'[^']*','[^']*','[^']*','([^']*)','([^']*)','([^']*)'")
bad = [l[:120] for l in rows if not pat.search(l) or not re.search(r"'ea',(\d+),(\d+),", l)]
print('총 행:', len(rows), '/ 파싱 실패:', len(bad))
for b in bad[:5]: print('  ', b)
PY
```

파싱 실패 행은 **가격 주입에서 통째로 빠진다.** 0이어야 한다.
