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
| `buybox` | **오른쪽 주문정보**. `[{"m":모델,"s":규격,"p":제품가+배송료,"x":제품가}]` — `p−x`가 주문당 1회 배송료. **오른쪽 열은 가격이 없어도 항상 나온다** — 값이 비었거나 모든 `p`가 0이면 site.js가 **견적문의 창**으로 렌더한다(가격 문의 / 제품가격·배송 문의 / 견적문의 버튼 → 제품문의 모달). 가격을 아직 안 넣은 것과 구분하려면 견적 전용 제품은 `"buybox": []` 를 명시한다(빌드 감사 통과) |
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
- **페이지가 자기 자신을 설명하는 문장을 쓰지 않는다.** "제조사 표기 그대로 옮긴 것입니다", "오른쪽 주문정보에서 확인하실 수 있습니다", "아래 표와 같습니다" 류 금지. 데이터는 표로 보여주고 문장은 남기지 않는다. 빌드 린터가 `LINT_BAD_PHRASES` 로 잡는다.
- 논문은 **최대 3편**. 없으면 섹션을 아예 내지 않는다(억지로 채우지 않는다).

## `papers` 스키마 — 관련 논문 (최대 3편)

**표 구성은 논문 / 저널 / 링크 3열 고정.** 근거 열이나 등급 배지를 붙이지 않는다.

수록 기준:

1. **유명 저널 위주.** 빌드가 저널 등급으로 자동 정렬·필터한다 — **T1**(Nature/Science 계열·JACS·Angew·Adv. Mater.·EES·Joule·ACS Nano·Research 등) 우선, 다음 **T2**(J. Power Sources·Electrochim. Acta·J. Mater. Chem. A·JES·Sci. Rep.·Materials 등). **T1/T2 밖 저널은 제외**하고 빌드가 warn 으로 알린다(등급 안 논문이 하나도 없을 때만 예외 수록).
2. **근거가 있으면 근거 있는 것만 싣는다** — 논문 Methods에 제품 코드·브랜드 구매가 적힌 논문.
3. 근거 있는 논문이 **하나도 없을 때에만** 같은 배합·같은 사양의 대표 논문으로 채운다.
4. 제품과 무관한 논문(브랜드에서 시약만 산 논문 등)은 넣지 않는다.
5. 아무것도 없으면 섹션을 아예 내지 않는다.

저널명은 `journal` 값의 `<i>…</i>` 안에 적는다(등급 판정이 이 부분만 본다). 정식명·표준 약어 모두 인식하며, 목록에 없는 분야를 다루게 되면 `PP_JOURNAL_T1` / `PP_JOURNAL_T2` 에 저널명을 추가한다.

```jsonc
"papers": {
  "heading": "관련 논문",
  "items": [{
    "title":   "논문 제목",
    "journal": "<i>Research</i> <b>2020</b>, 5714349",
    "authors": "Ji, J. et al.",
    "doi":     "10.34133/2020/5714349"
  }],
  "note": "근거 한 줄 + 보증·제휴 아님 고지"
}
```

논문 찾는 법: Europe PMC 전문검색 API(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=…&format=json`)가 본문까지 색인하므로 제품 코드·브랜드명을 큰따옴표로 묶어 검색한다. Google Scholar·RSC/ACS SI PDF는 봇 차단이라 못 읽는다.

## `source` 스키마

```jsonc
"source": {"url": "https://www.dodochem.com/…", "label": "DodoChem 제품 페이지"}
```

본문 맨 아래 "자료 출처 — …" 한 줄로 렌더링된다.
