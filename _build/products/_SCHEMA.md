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
