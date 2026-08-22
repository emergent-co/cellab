---
name: rndsetup-product-page
description: 실험셋업연구소(rndsetup.com) 저장소 C:\dev\rndsetup_homepage 에 브랜드 제품 상세페이지를 표준 틀 그대로 만들어 배선한다. 사용자가 "제품 올려줘", "상세페이지 만들어줘", "신규 브랜드 등록", "이 제품 사이트에 등록", "제품 페이지 추가", "브랜드 허브 만들어줘", "카탈로그에 넣어줘" 라고 하거나 제조사 자료(URL·PDF·엑셀·이미지)와 정가를 주면서 사이트 등록을 요청하면 반드시 이 스킬을 사용하라. 페이지 생성 → SQL 등록 → 허브 카드 → 빌드 → GEO 검증까지 한 번에 수행한다.
---

# 실험셋업연구소 제품 상세페이지 생성

## 0. 대원칙 (어기면 사이트가 깨진다)

1. **새 디자인 금지.** 기존 표준 틀을 **복제·치환**한다. 레이아웃·클래스명·색을 새로 만들지 않는다.
2. **여러 HTML 일괄 치환(`re.sub`/`sed`) 금지.** 파일 하나씩 편집한다. (과거 후반부 잘림 사고 다수 — `CRITICAL_RULES.md`)
3. **GEO가 0순위.** 크롤러가 **raw HTML만으로** 본문·링크·스키마를 읽을 수 있어야 한다. JS로만 렌더 금지.
4. **갱신 1곳 원칙.** 가격·사이트맵·CNAV·검색인덱스는 전부 자동이다. 손으로 고치지 말 것.
5. 작업 전 `CLAUDE.md` → `CRITICAL_RULES.md` → `OPERATIONS.md`를 읽는다. PRO급 장비는 `PRO_상세페이지_구성안.md`를 **반드시** 따른다.

## 1. 시작 전 — 동기화

```powershell
.\go.ps1          # 잠금정리 · 빌드 · HTML 무결성 검증 · fetch · 안전 pull
```

origin/main이 기준이다. 동기화 없이 편집하면 다른 PC 작업과 갈라진다.

> **빌드가 느린 환경(Cowork 원격 등)에서는** 저장소를 로컬 디스크로 복사해 작업하면 빌드가 수십 배 빨라진다:
> `rsync -a --exclude='.git/' --exclude='img/' <repo>/ /tmp/wrk/ && ln -s <repo>/img /tmp/wrk/img`
> → `/tmp/wrk`에서 편집·빌드 → `rsync -rlt --exclude='.git/' --exclude='img' /tmp/wrk/ <repo>/`

## 2. 입력 확인 (없으면 사용자에게 묻는다)

| 항목 | 필수 | 비고 |
|---|---|---|
| 브랜드명 / 브랜드 슬러그 | ✅ | 예약: `gaossunion`(가오스유니온·화학), `neware`(뉴웨어·충방전기), 전기화학은 브랜드 확정 전까지 `electrochem` |
| 제품명 · 모델명(들) | ✅ | 모델이 여러 개면 사양표에 행으로 |
| 카테고리 | ✅ | 브랜드 허브의 `data-cat` 값과 일치시킬 것 |
| **정가**(공급가 아님) | ✅ | SQL `retail_price`에 넣는 값. 화면 표기가는 빌드가 자동으로 3% 할인 적용 |
| 사양(스펙 표에 들어갈 항목) | ✅ | 전원·용량·온도·유량 등 |
| 제품 이미지 | ✅ | **제조사 정식 자산 또는 사용자 제공분만.** 타사(오실라 등) 사진 무단 사용 금지 |
| 소모품·옵션·리드타임 | ⭕ | 있으면 표로 |

**모르는 값을 지어내지 말 것.** 특히 납기·인증·성능 수치는 자료에 있는 것만 쓴다. 없으면 그 행을 빼거나 "문의 시 안내"로 둔다.

## 3. 경로 결정

```
brands/<brand-slug>/<product-slug>/index.html     ← 상세페이지
brands/<brand-slug>/index.html                    ← 브랜드 허브 (신규 브랜드일 때만 생성)
```

- 슬러그는 소문자+하이픈. 모델명이 아니라 **제품 종류**로 짓는다 (`fume-hood-mup`, `rotary-tube-furnace`).
- 이미 있는 슬러그면 덮어쓰지 말고 사용자에게 확인한다.

## 4. 상세페이지 생성 — 표준 틀 복제

**표준 틀(보강 완료판):** `brands/sh-scientific/fume-hood-mup/index.html`
**PRO급 장비:** `PRO_상세페이지_구성안.md`의 구성을 따르고 기준 페이지는 `brands/sh-scientific/rotary-tube-furnace-pro/index.html`.

```bash
mkdir -p brands/<brand>/<slug>
cp brands/sh-scientific/fume-hood-mup/index.html brands/<brand>/<slug>/index.html
```

그다음 **그 파일 하나만** 열어 아래 순서대로 치환한다. 섹션 순서는 고정이다:

`<head>` → `#pumplab-header` → `detail-top`(사진·정답블록·견적버튼) → `pkg`(특징 → 사양표 → 소모품표) → `pkg`(상세 이미지) → `ctbar-sec`(연락 바) → `faq-sec`(FAQ) → JSON-LD 3종 → `#pumplab-footer` → `site.js`

치환 항목의 전체 목록·주의사항은 **`references/page-template.md`** 를 읽어라.

### 절대 빠지면 안 되는 GEO 요소 (하나라도 없으면 미완성)

- [ ] `<title>` — `제품명 (영문) 모델 — 사양·정가 | 실험셋업연구소`
- [ ] `<meta name="description">` — **따옴표 이중 금지**(과거 112페이지 메타 붕괴 사고). 큰따옴표 속에 큰따옴표를 넣지 말 것
- [ ] `<link rel="canonical">` — `https://rndsetup.com/brands/<brand>/<slug>/` (끝 슬래시 포함)
- [ ] OG 5종 + Twitter Card
- [ ] `<h1 class="dt-name">` **1개만**
- [ ] **정답블록 `<p class="dt-ans">`** — H1 바로 아래, 질문에 답하는 **80~100자**
- [ ] 사양표 `<table class="pkg-tbl">`
- [ ] 정가 표기 `<p class="pkg-note">본체 정가 <b>N,NNN,NNN원</b> (VAT 별도)</p>`
- [ ] 견적 버튼 `<button type="button" class="qbtn" data-quote="제품명 · 모델">견적문의</button>` (최소 1개)
- [ ] `<img>` 전부 `alt` 보유
- [ ] **JSON-LD 3종**: `Product` + `FAQPage` + `BreadcrumbList` — 화면 FAQ와 FAQPage가 **1:1 일치**
- [ ] `<div id="pumplab-footer"></div>` (내용 비움 — 빌드가 CNAV 주입)
- [ ] `<!--HEADLD_START-->…<!--HEADLD_END-->` 는 그대로 두거나 통째로 지운다(빌드가 재주입). **손으로 고치지 말 것**
- [ ] 파일이 `</html>`로 끝난다

### 가격 규칙 (중요)

- 상세페이지 `pkg-note`의 "정가 N원"과 JSON-LD `offers`의 `price`/`lowPrice`는 **정가 그대로** 둔다.
- 홈·레일에 뜨는 시작가는 `build_prices()`가 SQL 최저 정가에 **3% 할인**(`DISCOUNT_RATE=0.97`, 만원 미만 버림)을 적용해 자동 주입한다. 손대지 말 것.

## 5. SQL 등록 — `rndsetup_products.sql`

기존 행 형식을 그대로 따라 `INSERT INTO products (...) VALUES (...)` 를 파일 끝에 추가한다.
열 순서·인용부호 규칙은 **`references/sql-row.md`** 참조.

- `retail_price` = **정가**, `supply_price` = 공급가(모르면 정가와 동일하게 두지 말고 사용자에게 확인)
- `daebun`/`sobun`(대분류/소분류)은 기존 값 어휘를 재사용한다. 새 어휘를 만들면 가격 매칭이 깨질 수 있다.
- 모델이 여러 개면 **모델당 1행**.

## 6. 브랜드 허브에 카드 추가

`brands/<brand>/index.html` 안 카드 목록에 `<article class="dscard">` 한 장을 추가한다(기존 카드 복제·치환).
`data-cat`·`data-text`(소문자 검색 키워드)를 채워야 허브 필터·검색에 잡힌다.

**신규 브랜드**라면 허브부터 만든다:
1. `brands/sh-scientific/index.html` 또는 `brands/alicat/index.html`을 틀로 복제
2. `brands/index.html`의 브랜드 카드 + `ItemList` JSON-LD에 브랜드 1건 추가
3. `_build/build.py`의 `CRAWLER_LINKS`에 브랜드 허브 1줄 추가 → 빌드하면 전 페이지 CNAV에 자동 반영
4. `llms.txt`에 **허브만** 등재 (개별 상세페이지는 등재 금지 — IA 일관성)

## 7. 빌드 + 검증

```bash
python _build/build.py
```

빌드가 자동으로 해주는 것 — **직접 손대지 말 것**:
`sitemap.xml`(브랜드 상세는 자동 등재) · `search-index.json` · CNAV · `feed.xml` · 가격 주입 · head JSON-LD.

이어서 검증 스크립트를 돌린다:

```bash
python scripts/verify_product_page.py brands/<brand>/<slug>/index.html
# (저장소에도 같은 스크립트가 있다: python _ops/skills/rndsetup-product-page/scripts/verify_product_page.py ...)
```

전 사이트 무결성도 확인한다:

```bash
# 모든 HTML이 </html>로 끝나는지
for f in $(find . -path ./.git -prune -o -path ./_build -prune -o -name '*.html' -print); do
  tail -c 30 "$f" | tr -d '[:space:]' | grep -q '</html>$' || echo "JEOLLIM: $f"
done
node --check assets/site.js
```

**하나라도 실패하면 커밋 중단**하고 정상 커밋에서 복원한다(`git show <해시>:<경로> > <경로>`).

## 8. 마감

- `git status`로 **이미지 파일까지** 스테이징됐는지 확인한다(누락 잦음).
- 배포는 사용자가 실행한다: `.\go.ps1 "제품 등록: <브랜드> <제품명>"`
- 에이전트는 push하지 않는다.

## 9. 체크리스트 (완료 보고 전 전부 확인)

- [ ] `brands/<brand>/<slug>/index.html` 생성, 표준 틀 준수
- [ ] 정답블록 80~100자 · 사양표 · 정가 · 견적 버튼
- [ ] canonical · description(따옴표 이중 없음) · OG/Twitter
- [ ] Product · FAQPage · BreadcrumbList JSON-LD 파싱 성공, FAQ 1:1 일치
- [ ] `rndsetup_products.sql` INSERT 추가(모델당 1행, 정가 기준)
- [ ] 브랜드 허브 카드 추가 (+ 신규 브랜드면 허브·brands/index.html·CRAWLER_LINKS·llms.txt)
- [ ] `python _build/build.py` 통과 → sitemap·검색인덱스·CNAV 자동 반영 확인
- [ ] `verify_product_page.py` 전 항목 통과
- [ ] 전 HTML `</html>` 종료, `node --check assets/site.js` 통과
- [ ] 죽은 링크·리다이렉트 체인 0
- [ ] 사용자에게 `.\go.ps1 "커밋 메시지"` 안내
