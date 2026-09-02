# `_build/products/<brand>.json` — 제품 상세페이지 SSOT 스키마

`build_product_pages()`(`_build/build.py`)가 이 JSON만 읽어
`brands/<brand>/<slug>/index.html` 을 통째로 생성한다.

- **신규 상세페이지 = 이 JSON에 `products` 1건 추가 + 빌드.** 손 HTML 작성 금지.
- **디자인 수정 = `assets/detail.css` 또는 `_pp_render()` 템플릿 1곳.** 페이지에 `<style>` 복사 금지.
- head의 Organization/WebSite JSON-LD와 푸터 크롤러 nav는 빌드가 자동 주입한다(적지 말 것).
- 레이아웃 순서는 템플릿이 강제한다:
  크럼 → h1 → 영문명 → 보조문구(`sub`) → 대표사진 → 정답블록 → **특징 → 사양 → 규격 비교표**
  → 추가 섹션 → 관련링크 → 견적 CTA → 문의바 → FAQ.
- **소비자가는 본문 표에 적지 않는다.** 가격 노출 지점은 오른쪽 주문정보(`buybox`) 한 곳뿐이다.

## 최상위

```jsonc
{
  "brand": { ... },        // 브랜드 공통 (파일당 1개)
  "products": [ { ... } ]  // 제품 N건
}
```

## `brand`

| 키 | 필수 | 설명 |
|---|---|---|
| `slug` | ✔ | URL·이미지 폴더에 쓰는 브랜드 슬러그 (`dodochem`) |
| `name_ko` | ✔ | 화면에 쓰는 브랜드명 (`DodoChem`, `가오스유니온`) |
| `name_en` |  | 영문 브랜드명. `name_ko`와 같으면 한 번만 표기 |
| `hub` |  | 브랜드 허브 경로. 기본 `/brands/<slug>/` |
| `hub_label` |  | "← ○○ 전체" 되돌아가기 링크 문구 |
| `img_dir` |  | 이미지 폴더. 기본 `/img/<slug>/` |

## `products[]`

### 신원 · 메타

| 키 | 필수 | 설명 |
|---|---|---|
| `slug` | ✔ | `brands/<brand>/<slug>/` |
| `name` | ✔ | h1 제품명(브랜드명 제외) |
| `name_en` |  | h1 아래 영문명 |
| `sub` |  | h1·영문명 **아래 한 줄**로 들어가는 보조 문구(배합·규격 요약) |
| `category` |  | 크럼 마지막 마디. 기본값 = `name` |
| `title` `desc` |  | `<title>`·meta description. 없으면 자동 조립 |
| `og_title` `og_desc` |  | OG/트위터 문구 |
| `images` |  | 파일명 배열. 첫 장이 대표사진, 2장 이상이면 썸네일 스와퍼 |
| `image_alt` |  | 대표사진 alt |

### 본문

| 키 | 설명 |
|---|---|
| `answer` | **정답블록**(`.dt-ans`) — 80~100자 한 문장. GEO 0순위 |
| `summary` | 요약 박스(`.dt-sum`) |
| `variants` | `{heading, head:[열이름], rows:[[셀,…]], note}` — **규격 비교표**. 값이 모든 행에서 같은 열은 자동으로 접혀 "모든 규격 공통" 줄이 되고, 구분되는 열이 하나만 남으면 라벨/값 2열 표 하나로 합쳐진다(동일 내용 표 쪼개짐 방지). 가격 열은 넣지 않는다 |
| `specs_note` | 사양표 아래 주석 한 줄 |
| `buybox` | **오른쪽 주문정보**(필수). `[{"m":모델,"s":규격,"p":제품가+배송료,"x":제품가}]` — `p−x`가 주문당 1회 배송료. 규격표가 있는데 이게 없으면 린터가 warn |
| `features` | 특징 불릿 배열 |
| `specs` | 사양표. `[[라벨, 값], …]` 2열 |
| `sections` | 추가 섹션 배열. `{h, head?, rows?, html?, note?}` (논문 인용·구성품 등) |
| `related` | 관련 링크 한 줄(HTML) |
| `keywords` | `[[표시문구, 링크], …]` 해시 키워드 |
| `faq` | `[{tag, q, a}]` — FAQPage JSON-LD로도 자동 생성 |

### JSON-LD

`ld` = `{name, sku, category, description, models:[], low, high, count}`.
`low`가 있으면 AggregateOffer가 붙는다. Breadcrumb는 템플릿이 자동 생성.

## 마크업 규칙

- `answer` · `summary` · `features` · `specs` 값 · `price.rows` · `sections` · `related` · `faq.a`
  → **HTML 그대로 통과**한다(`<b>` `<a>` `<i>` 사용 가능). 작성자 책임.
- `title` · `desc` · `name` · 크럼 · JSON-LD → **자동 이스케이프**. 태그를 넣지 말 것.
- 색은 절대 인라인으로 쓰지 말 것. 링크·강조는 detail.css가 `--merck-link`(#0F69AF)로 칠한다.

---

# 제조사 원문 수집 가이드 (모든 브랜드 공통)

제품 상세페이지는 **제조사 제품 페이지의 본문을 빠짐없이 옮겨 담는 것**이 기본이다.
아래 9개 항목은 빌드가 매번 검사해서 빠진 것을 `[warn] <brand>/<slug> — 원문 미수집: …` 으로 찍는다.

| # | JSON 키 | 제조사 페이지에서 가져올 것 | 최소 기준 |
|---|---|---|---|
| 1 | `answer` | 제품이 무엇인지 한 문장 | 80~100자, GEO 0순위 |
| 2 | `images` | 제품 사진 | 1장 이상 |
| 3 | `features` | 셀링포인트·특징 | 2개 이상 |
| 4 | `specs` | **물성·기본정보** — 외관·순도·수분·인화점·밀도·유통기한·보관조건 | 3행 이상 |
| 5 | `variants` | 규격·모델·포장 비교 | 필수 |
| 6 | `buybox` | 규격별 가격(주문정보) | 필수 |
| 7 | `faq` | 자주 묻는 질문 | 2개 이상 |
| 8 | `source` | 제조사 원문 URL | 필수 |
| 9 | `safety` | **안전정보(GHS)** — 그림문자·H·P·저장·폐기 | 화학품이면 필수 |

화학품 판정: `category` 또는 `name` 에 전해액·용액·시약·재료·소재·촉매·분말·슬러리·바인더·용매·염 중 하나가 들어가면 안전정보를 요구한다 (`PP_CHEM_HINTS`).

**옮길 때 원칙**

- 제조사가 표로 준 것은 표로 옮긴다(문장으로 풀어쓰지 않는다).
- 수치·코드(H/P 문구, 인화점, ppm)는 **원문 그대로**. 반올림·의역 금지.
- 제조사가 안 준 값을 추정해 채우지 않는다. 없으면 그 행을 뺀다.
- 논문은 **최대 3편**. 없으면 섹션을 아예 내지 않는다(억지로 채우지 않는다).

## `papers` 스키마 — 관련 논문 (최대 3편)

우선순위: ① 제품 코드가 논문 Methods에 나온 것 → ② 없거나 모자라면 **같은 배합·같은 사양**의 대표 논문(피인용 많은 원전).
어느 쪽이든 **`grade` 배지로 근거 등급을 반드시 표기**한다. 제품과 무관한 논문(브랜드 시약만 산 논문 등)은 넣지 않는다.

```jsonc
"papers": {
  "heading": "관련 논문",
  "items": [{
    "title":   "논문 제목",
    "journal": "<i>Research</i> <b>2020</b>, 5714349",
    "authors": "Ji, J. et al.",
    "grade":   "LS-009 지정",        // 제품 지정 | 같은 배합 | 같은 사양
    "evidence":"논문 원문 인용 또는 무엇이 같은지 한 줄",
    "doi":     "10.34133/2020/5714349"
  }],
  "note": "※ 등급 뜻풀이 + 보증·제휴 아님 고지"
}
```

논문 찾는 법: Europe PMC 전문검색 API(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=…&format=json`)가 본문까지 색인하므로 제품 코드·브랜드명을 큰따옴표로 묶어 검색한다. Google Scholar·RSC/ACS SI PDF는 봇 차단이라 못 읽는다.

## `safety` 스키마

```jsonc
"safety": {
  "warn": {"h": "고인화성 · 부식성 · 생식독성 물질", "p": "인화점 −2 ℃ …"},   // 경고 박스(선택)
  "pictograms": ["GHS02 인화성", "GHS05 부식성", "GHS06 급성독성"],
  "h_codes": [["H225", "고인화성 액체 및 증기"], ["H314", "피부에 심한 화상 …"]],
  "p_codes": ["P210", "P233", "P280"],
  "storage_codes": ["P403+P233"],
  "disposal_codes": ["P501"],
  "extra": [["추가 라벨", "값"]],                                        // 선택
  "note": "※ 제조사 표기 기준입니다. 실제 취급 전 MSDS를 확인하십시오."
}
```

## `source` 스키마

```jsonc
"source": {"url": "https://www.dodochem.com/…", "label": "DodoChem 제품 페이지"}
```

본문 맨 아래 "자료 출처 — …" 한 줄로 렌더링된다.
