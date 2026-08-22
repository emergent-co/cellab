# 상세페이지 치환 가이드 — `brands/sh-scientific/fume-hood-mup/index.html` 기준

표준 틀을 복제한 뒤, 아래 항목을 **위에서 아래 순서로** 하나씩 치환한다.
파일 하나만 열어 편집한다. 여러 파일 일괄 치환 금지.

---

## A. `<head>`

| 위치 | 치환 내용 |
|---|---|
| `<title>` | `제품명 (영문 부제) 모델 — 사양·정가 \| 실험셋업연구소` |
| `<meta name="description">` | 130~170자. 모델·핵심 사양 2~3개·차별점·국내 A/S. **큰따옴표 안에 큰따옴표 금지** (홑따옴표도 되도록 피한다) |
| `<link rel="canonical">` | `https://rndsetup.com/brands/<brand>/<slug>/` — 끝 슬래시 필수 |
| `og:url` / `og:image` / `twitter:image` | 새 경로·새 대표 이미지로 |
| `<style>` 블록 | **건드리지 않는다** (틀 공용) |
| `<!--HEADLD_START-->…<!--HEADLD_END-->` | 그대로 두거나 통째로 삭제. 빌드가 Organization·Breadcrumb를 재주입한다 |

## B. `detail-top` — 첫 화면

```html
<div class="crumb"><a href="/">홈</a> › <a href="/brands/">실험장비 카탈로그</a> › <카테고리명></div>
```

- `.dt-img img` : 대표 사진 `src`·`alt`. `alt`는 "브랜드 제품명 제품 사진 (브랜드)" 형태
- `.dt-thumbs button[data-src]` : 추가 사진 수만큼. 사진이 1장이면 `.dt-thumbs` 블록째 삭제
- `.dt-brand` : `브랜드 한글명 · 영문명`
- `<h1 class="dt-name">` : 제품명 + `<span>` 안에 모델명. **h1은 페이지에 1개뿐**
- **`<p class="dt-ans">` 정답블록 — GEO 0순위.** 80~100자. "이 제품이 무엇이고 무엇을 해결하는가"에 한 문장으로 답한다. 핵심어 2개는 `<b>`
- `<p class="dt-sum">` : 핵심 사양 한 줄 요약(숫자 위주)
- `<button class="qbtn" data-quote="제품명 · 모델">견적문의</button>` — `data-quote` 값이 문의 메일의 "문의제품" 필드로 그대로 들어간다
- `.dt-kw` : 해시태그형 내부 링크 3개 내외 (`/brands/<brand>/?cat=<cat>` 등)

## C. `pkg` — 본문 (특징 → 사양 → 소모품)

1. `<a class="ds-back" href="/brands/">← 실험장비 통합 카탈로그</a>` — 신규 브랜드면 브랜드 허브로
2. `<h2 class="pkg-h">특징</h2>` + `<ul class="pkg-feat">` — 항목당 `<b>핵심어</b> — 설명` 형식, 6~10개
3. `<h2 class="pkg-h">사양</h2>` + `<table class="pkg-tbl">` — `<th scope="row">항목</th><td>값</td>`.
   모델이 여러 개면 `<thead>`에 모델을 열로 놓는 형태로 바꾼다
4. (있으면) `<h2 class="pkg-h">소모품</h2>` + `<table class="pkg-tbl pkg-opt">` — 품목/구성/정가(VAT 별도)
5. `<p class="pkg-note">본체 정가 <b>N,NNN,NNN원</b> (VAT 별도)</p>` — **정가 그대로**. 3% 할인은 홈 시작가에만 자동 적용된다
6. 두 번째 `qbtn` (선택)

## D. 상세 이미지 섹션

`<figure>` 반복. 각 `<figcaption>`에 **출처 표기**: "제조사(브랜드명) 제공 자료입니다."
제조사 정식 자산이 아니면 넣지 않는다.
모든 `<img>`에 `loading="lazy"`와 `onerror`로 깨진 이미지 숨김 처리를 유지한다.

## E. `ctbar-sec` — 연락처·QR 바

**통째로 그대로 복제**한다. 전화번호·채널톡 링크·QR SVG는 공용이다.

## F. `faq-sec` — 이 제품 FAQ

- `.faq-item` = `.faq-q`(앞에 `<span class="faq-tag">키워드</span>`) + `.faq-a`
- **4~6문**. 실제로 검색될 질문으로: 용도 / 성능·수치 / 소모품·유지보수 / 한계·주의 / 설치 조건
- 아래 FAQPage JSON-LD와 **문항·문구가 1:1 일치**해야 한다 (스크립트가 개수를 검사한다)

## G. JSON-LD 3종 (본문 끝, footer 앞)

1. **Product** — `name`, `brand`, `category`, `url`, `image`, `model[]`, `offers`
   - 단일가: `{"@type":"Offer","priceCurrency":"KRW","price":<정가>,"availability":"https://schema.org/InStock","seller":{"@id":"https://rndsetup.com/#org"}}`
   - 가격대: `AggregateOffer` + `lowPrice`/`highPrice`/`offerCount`
   - **price는 정가.** 할인가를 넣지 않는다
2. **BreadcrumbList** — 홈 › 실험장비 통합 카탈로그(`/brands/`) › 제품명 (마지막 항목은 `item` 없이 `name`만)
3. **FAQPage** — 화면 FAQ와 1:1

JSON 안에 `</` 가 들어가면 스크립트가 조기 종료된다. 답변 텍스트에 HTML 태그를 넣지 말 것.

## H. 꼬리

```html
<div id="pumplab-footer"></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
```

`#pumplab-footer`는 **비워 둔다**. 빌드(`inject_static_nav`)가 CNAV를 주입한다.
이미 `<!--CNAV_START-->…<!--CNAV_END-->`가 들어 있는 상태로 복제됐다면 그대로 둬도 된다(빌드가 갱신).

---

## 자주 나는 사고

| 증상 | 원인 | 대응 |
|---|---|---|
| 메타가 통째로 깨짐 | description 안에 큰따옴표 중첩 | 따옴표 제거 후 재빌드 |
| 페이지 후반부가 잘림 | 여러 파일 일괄 `sed`/`re.sub` | 정상 커밋에서 복원, 파일별 편집으로 전환 |
| 견적 버튼이 안 뜸 | `data-quote` 속성 누락 | `.qbtn` + `data-quote` 세트로 넣는다 |
| CNAV가 방문자에게 보임 | 마커가 `#pumplab-footer` div **밖**에 있음 | div 안으로 옮기고 재빌드 |
| 홈 시작가가 안 바뀜 | SQL의 `sobun`/`sku` 어휘가 기존과 달라 매칭 실패 | `build_prices()`의 매칭 조건 확인 후 어휘 정렬 |
