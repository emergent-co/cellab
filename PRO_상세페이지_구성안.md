# PRO 버전 제품 상세페이지 — 표준 구성안 (확정)

> 기준 페이지: `sh-scientific/catalog/rotary-tube-furnace-pro/index.html`
> **다음부터 모든 PRO 버전 상세페이지는 이 구성을 반드시 따른다.** (섹션 순서·컴포넌트·GEO 요소 고정)
> 데이터(사양·문구·옵션)는 제품마다 바뀌지만 **틀(폼)은 동일**해야 한다.

---

## 0. 파일·경로
- 위치: `sh-scientific/catalog/<slug>-pro/index.html` (일반형은 별도 `<slug>` 페이지, PRO는 별도 페이지)
- 대표 이미지: `/img/product/sh/<slug>-pro.jpg` (제품+PC 화면 합성, 대표사진에 `PRO` 배지)
- 배포: 이미지·JS/CSS 변경분까지 `git add` 확인 후 push (누락 잦음)

## 1. `<head>` (필수 요소)
- `<title>` : `제품명 (영문 부제) 모델 — 사양·구성 | 실험셋업연구소`
- `<meta name="description">` (150~170자), `<link rel="canonical">`
- **OG 5종** (type=product, title, description, url, image) + **Twitter Card 4종** (summary_large_image)
- `<!--HEADLD_START-->` Organization 그래프(#org) — 빌드 주입, 임의수정 금지
- 페이지 인라인 `<style>` **먼저**, 그 다음 `<link href="/assets/site.css">`
  - 캐시 무관 보장이 필요한 규칙(호버 팝업·영상·연락처바)은 **인라인에 `.pkg`/`.dt-left` 등 고우선순위 셀렉터로** 중복 정의

## 2. `<body>` 섹션 순서 (고정)
1. `#pumplab-header` **+ 숨은 `<span data-quote-init data-quote="제품명…" hidden>`**
   - ⚠ **필수**: 이 요소가 없으면 견적 모달이 초기화되지 않아 `.qbtn` 스타일·견적창이 깨진다.
2. `<section class="detail-top">` → `.dt-grid` (좌 44% / 우 1fr, `align-items:start`)
   - **좌 `.dt-left`** : `.dt-img`(대표사진 + `.pro-badge`) → 그 아래 **연락처·QR 바 `.ctbar`** (세로 열이라 1행 유지되게 축소)
   - **우 `.dt-info`** : `.dt-brand` → `<h1 class="dt-name">`(제품명 + `.pro-mark` PRO) → **정답블록 `.dt-ans` (80~100자, GEO 0순위)** → 요약 `.dt-sum` → **견적문의 버튼 `.qbtn.qsel-open`**(텍스트 "견적문의"만) → `#키워드 .dt-kw`
3. `<section class="prosec">` — **BASIC vs PRO**
   - 비교표 `.vs-box` : 데스크톱 3열 `[기본 1fr | 라벨 var(--ax) | PRO 1fr]`, `grid-auto-flow:row dense` (라벨이 같은 줄 세로중앙)
   - **행별 축 라벨**(중앙열): 예) 안전 / 효율 / 확장성 / 기록 — 각 행 1항목, 좌=기본(회색)·우=PRO(주황 `#C2410C`)
   - 문구는 **줄바꿈 최소화**(간결하게), 서브노트는 `.vs-sub`
   - 표 아래 `.vsq` : 대표 Q&A 1개(예: Alicat MFC 가스 스케줄) — 필요시 인라인 SVG 차트
4. `<section class="pkg">`
   - `.bc-grid` **기본구성** : 좌 `.bc-fig`(번호 이미지 + `.mkzone` 영역 호버 → `.mkpop` 화면중앙 상세팝업) / 우 `.bc-ol` 리스트 + `.bc-note`
   - `.bc-video` **유튜브 임베드**(중앙, ~560px) + **`.bc-video-cap` "실제 설치·운용 영상입니다…"** (AI 인용용 1차경험 신호)
   - `<h2 class="pkg-h">모델별 사양</h2>` + `.pkg-tbl` (동일 스펙은 colspan 병합, Max Temp 셀 안에 **실사용 경고 `.tw-note`** 중앙정렬)
5. 하단 **연락처·QR 바 `.ctbar`** (본문 웜톤 배경 `#FAF8F5`, 테두리 `#E7E3DE`)
6. `<section class="faq-sec">` **이 제품 FAQ**
   - 각 항목 `.faq-item` = `.faq-q`(앞에 **키워드 태그 `.faq-tag`**: 기본원리/온도/진공/가스제어/소재이송 등) + `.faq-a`
   - **옵션 중 GEO 유리 내용은 FAQ로 편입**하고 JSON-LD FAQPage에도 동일 반영
7. **견적 팝업 모달 `#qselBack`** + 인라인 `<script>`
   - 순서: **모델(간단스펙) → 버전(기본/PRO) → 옵션(체크박스)** → 견적문의
   - 제출 시 `제품 / 버전 / 모델 / 옵션` 문자열로 임시 `[data-quote]` 버튼 클릭 → 공용 견적폼 오픈
   - 모델 미선택 시 안내. 본문에는 옵션 선택 UI를 노출하지 않음(카탈로그로 재사용 가능하게)

## 3. 구조화 데이터 (JSON-LD) — 필수
- **Product** (brand, model[], additionalProperty[], offers, image)
- **FAQPage** (화면 FAQ와 1:1 일치)
- **BreadcrumbList** (홈 › 삼흥에너지 › 제품 카탈로그 › 제품명)
- Organization 그래프(#org)는 HEADLD로 포함
- CNAV(크롤러 내비) 주석블록 유지

## 4. GEO 체크리스트 (0순위 — 반드시 통과)
- [ ] raw HTML만으로 본문·링크·스키마가 읽힌다 (JS 렌더 금지)
- [ ] **정답블록(80~100자)** H1 바로 아래
- [ ] Product·FAQPage·BreadcrumbList JSON-LD 유효(JSON 파싱 OK)
- [ ] 모든 `<img>` alt 존재, 단일 H1, H2/H3 계층
- [ ] title·description·canonical·OG·Twitter 완비
- [ ] 유튜브 캡션 등 **1차 경험(설치·운용) 신호** 포함
- [ ] sitemap 포함 / `llms.txt`는 허브만 등재(개별 상세 추가 금지 — IA 일관성)
- [ ] 모든 `.html`이 `</html>`로 종료

## 5. 스타일 규칙
- 색: 네이비 `#1E3A5F`(브랜드) · 주황 `#C2410C`/`#9A3412`(PRO·강조) · 본문 웜톤 `#FAF8F5`
- 폰트: Pretendard(본문) / Noto Serif KR(제목 `--serif`)
- 연락처 바·팝업 등 재사용 컴포넌트는 site.css에 두되, 이 페이지에서 캐시 이슈가 있으면 인라인 고우선순위로 덮는다
- **여러 HTML 일괄 치환(re.sub/sed) 금지** — 파일 하나씩 편집 (CRITICAL_RULES 준수)

---
_최종 확정: 2026-07-31 · 기준 = 회전 튜브로 PRO 페이지_
