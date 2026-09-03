# CLAUDE.md — AI 에이전트 작업 지침 (진입점)

> 어느 컴퓨터에서든 세션을 열면 **이 파일을 먼저** 읽는다. 상세는 아래 문서로.

## 0. 먼저 읽을 문서
- `CRITICAL_RULES.md` — 사이트 손상 방지 절대 규칙
- `OPERATIONS.md` — 운영·빌드·배포·GEO 지침 (0순위=GEO)
- `PRO_상세페이지_구성안.md` — **PRO 버전 제품 상세페이지 표준 폼(양식). PRO 상세 작업 시 반드시 준수** (기준=회전 튜브로 PRO)

## 1. 기준선 — origin/main이 무조건 기준
- 작업자는 **2대의 컴퓨터를 오가며** 작업한다. 로컬이 오래됐을 수 있으니 **진실의 출처는 git(origin/main)**.
- 편집 전 최신인지 확인하고, 시작할 때 반드시 동기화한다(아래 §2).

## 2. 작업 루틴 (한 줄 명령)
- **시작:** `.\go.ps1`  /  **배포:** `.\go.ps1 "커밋 메시지"`
  → 잠금정리 · 빌드 · HTML 무결성 검증 · fetch · 안전 pull(배포 모드는 `pull --rebase` 후 push)까지 한 번에.
  배포 모드는 **원격 최신 위로 자동 재정렬**하므로, 다른 컴퓨터가 먼저 올렸어도 갈라지지 않는다. 충돌 시 자동 중단.
- **수정은 모아서 한 번에 배포한다.** 수정 1건마다 커밋하면 왕복이 길어진다.
- (구버전) `.\sync.ps1`
  → .git 잠금정리 · `git fetch` · 안전 pull(FF) · `build.py` · 모든 HTML `</html>` 검증 · 현재 커밋 리포트.
  (커밋 안 된 로컬 변경/갈라짐이면 자동으로 안 지우고 알려줌. 새 구조 무조건 기준이면 `git reset --hard origin/main`.)
- **종료/배포:** 변경 → `python _build\build.py` → `.\sync.ps1`로 검증 → `git add -A` → `git commit` → `git push` (또는 `deploy.ps1`).
- **git이 유일한 동기화 수단** — OneDrive/Drive 동기화 금지.

## 3. 절대 규칙 요약 (상세=CRITICAL_RULES.md)
- **GEO가 0순위.** 모든 변경은 "AI 크롤러가 raw HTML만으로 링크·본문·스키마를 읽는가"를 먼저 통과. JS로만 렌더 금지, 정답블록(80~100자)·JSON-LD·정적 내부링크 필수, 리다이렉트 체인(2홉+)·죽은 링크 금지, `llms.txt`=실제 IA 일치.
- **여러 HTML 일괄 치환(re.sub/sed) 금지** — 잘림 사고. 파일 하나씩 편집.
- 작업 후 **모든 .html이 `</html>`로 끝나는지 검증**(sync.ps1이 수행).
- 운영 데이터(사양·라벨·옵션·매칭 어휘·경계값)를 HTML/JS에 박지 말 것 → **`_build/*.json`(SSOT)** 에.
- `.gitattributes` 삭제·임의수정 금지.

## 4. 구조 요약 (2026-08 기준)
- **NAV 5개**(2026-08): 툴·실험장비(`/product/`, sub: 통합 카탈로그·메뉴얼) · 소재(`/materials/`) · 셋업 사례(`/magazine/`) · 유용한 정보(sub: 제품 정보 `/info/`·배터리 사전 `/wiki/`) · 문의하기(`/contact/`, sub: 문의하기(챗)·FAQ·회사소개). 홈 밴드 CTA(재료·소모품→/materials/, 툴·장비→/product/)와 연결. 상단 가로 메뉴바(스크롤 시 반투명 고정) + 모바일 드로어. 규칙: **하위 메뉴가 있는 상위 메뉴는 noclick**, 첫 하위탭 href = 대표 href.
- **문의·FAQ = `/contact/` 원페이지**(2026-08 통합): 정답블록 → 검색 필터 → 카테고리 탭(구매·견적/수리·A/S/제어·소프트웨어/배송·기타) → FAQ 아코디언 26문 → 문의 폼(`#form`, Formspree `mnjkzppj`). **FAQPage JSON-LD 26문 전량 정적 렌더**(JS는 표시 토글만). `/faq/`는 301 + 파일 삭제.
- **유용한 정보(2026-08 신설)**: NAV '에너지 랩 A to Z' 폐지 → '유용한 정보'(noclick, sub: 제품 정보 `/info/` · 배터리 사전 `/wiki/`). `/magazine/battery/` 커리큘럼은 삭제+301→`/wiki/`.
  - `/info/` = **브랜드별 장비 비교 전용**(카드 검색창 포함). 비교 글=단품 모델·유형 비교(`compare-peristaltic|muffle|furnace|mfc|echem-cell/`+기존 `/compare/`), 각 글 하단에 **선택 위저드**(글의 비교 기준을 질문으로 변환→모델 직링크). 부품소개·FAQ 블록 없음, 단순 브랜드 소개 없음. NAV 제품소개 sub에서 '선택 가이드' 제거됨(위저드로 대체).
  - `/wiki/` = 배터리 사전(위키형). **SSOT=`_build/wiki.json`** — 항목 추가는 JSON 1건, `build_wiki()`가 항목 페이지·인덱스·DefinedTerm JSON-LD·sitemap·검색 인덱스 전부 자동 생성. 원본 생성 스크립트 `_ops/make_wiki.py`.
- **콘텐츠 허브 = `/magazine/` "셋업 사례"** — 논문 셋업·가이드·용어사전·트러블슈팅·도입 사례를 3열 카드로 통합. `/setups/` 인덱스는 301→`/magazine/` (세부 사례 글 URL은 유지). 공정 허브: battery(커리큘럼)·deposition·heat-treatment·oxidation.
- **제품**: 삼흥 상세 `/brands/sh-scientific/<slug>/` 150+, 리드플루이드 모델 페이지 78개 잔존(+`guide` 위저드) — **모델 페이지 정리 여부는 보류 중(유입 있음)**.
- **가오스유니온(Gaoss Union) 전기화학** `/brands/gaossunion/` (2026-08 신규): 허브 + 계열 9장(기준전극·RHE·상대전극·작업전극·RDE/RRDE·전극클램프·연마용품·전기화학재료·CO₂RR촉매) · **322 SKU**.
  가격 = 2026 카탈로그 EUR × **1,620원**(SQL 상단 주석에 기준 명시) · **3% 상시 할인 대상 아님**(홈 시작가 키에 넣지 않으면 자동 미적용) · 국제 운송비 별도.
  원본 SQL 조각 = `_ops/gaossunion_products.sql`(병합 완료본, 재병합 금지). 이미지 = `img/gaossunion/<slug>-<n>.jpg`(제조사 카탈로그 추출, 사용 허가 받음).
  홈 전기화학 코너 10칸 중 **전극 4칸은 상세페이지 링크**로 전환됨. 셀 6칸(전기화학·광전기화학·분광전기화학·GDE유동·MEA전해조·PSE반응기)은 **자료 미확보로 견적 팝업 유지**.
- **공유 크롬(SSOT)**: `assets/site.js`(NAV·헤더·푸터·글 페이지 좌측 목차/우측 관련제품 레일·부품주문 팝업·검색), `assets/site.css`. 색=네이비 `#1E3A5F`.
- **데이터/빌드 (SSOT·자동 주입)** — `_build/build.py`가 처리. **아래 항목은 절대 손으로 고치지 말 것**:
  - `sitemap.xml`, `feed.xml`, `search-index.json`(전 페이지 자동 인덱스, 301 소스 제외)
  - ~~홈 '셋업 사례' 카드~~ (2026-08 홈에서 섹션 삭제 — 마커 없어 주입 생략 warn은 정상. 콘텐츠 노출은 홈 '최신연구' 레일=posts.json 최신 6편으로 일원화)
  - 홈 '최신연구' 레일 ← `_build/posts.json` 최신 6편 (`<!--NEWRESEARCH-->` 마커)
  - **전 제품 통합 카탈로그** ← `brands/<brand>/index.html`의 `<article class="dscard">` 를 `build_all_products()` 가 수집해 `product/index.html` 의 `<!--ALLPROD_START-->` (구 /brands/ 는 301→/product/, 브랜드 하위 경로는 유지) 마커에 주입(현재 241장). 브랜드 허브에 카드를 추가하면 **빌드만으로 자동 반영**. 통합 카테고리 매핑은 `ALLPROD_CATMAP`, 매핑 실패 시 `ALLPROD_BRANDS` 의 브랜드 기본값.
  - **sitemap 브랜드 페이지 자동 등재** ← `brands/<brand>/index.html`·`brands/<brand>/<slug>/index.html` 스캔(리다이렉트 스텁·noindex·301 소스 제외). 새 브랜드·제품 페이지는 빌드만으로 sitemap에 들어간다.
  - **가격** ← `rndsetup_products.sql` 최저 정가 → `index.html`의 `data-price="key"` 스팬 + `site.js`의 `/*P:key*/'...'` 마커. **가격 개정 = SQL만 수정.**
    사이트 노출 가격은 `build_prices()`의 `DISCOUNT_RATE=0.97`(정가 대비 **3% 상시 할인**, 만원 미만 버림)이 적용된 판매가. 할인율 변경 = 이 상수 1곳. 상세페이지 `pkg-note`의 '정가 X원'과 JSON-LD `offers.price`는 **정가 유지**.
  - 크롤러 nav(CNAV) ← `CRAWLER_LINKS` — 반드시 `#pumplab-footer` div **안**의 마커에 주입돼야 함(밖에 있으면 방문자에게 노출됨).
- **새 글 발행 절차(고정)**: 글 페이지 작성 → `posts.json` 1건 추가 (+홈 노출 원하면 `paper_cases.json`) → 빌드. 그 외 배선은 전부 자동.
- **신제품 등록 절차(고정, 2026-08)**: 브랜드 허브(`brands/<brand>/index.html`)에 `dscard` 1장 추가 → 빌드. **허브 페이지는 사용자 비노출**(meta refresh→/product/, noindex) — 카드 수집용 내부 원천으로만 유지하며, 삭제·리다이렉트 스텁화 금지(카탈로그가 빈다). 개별 상세페이지는 카탈로그 카드의 목적지이므로 유지. 그러면 **카탈로그 표준 카드(스펙 3행·#키워드 7)·검색 텍스트(연관검색어+동의어 확장)·가격(상세→SQL 모델코드 자동 매칭)·자동완성 카드 수·카드 총수·sitemap·검색 인덱스**가 전부 자동 반영된다. 수동 작업은 딱 3가지 경우뿐:
  1. **새 제품군 신설 시** (기존에 없던 장비 유형): `_build/build.py`의 4개 사전에 그 군을 등록 — `KW_BY_SUBCAT`(연관검색어 10개+, 군 전체에 참인 일반어만·세부 유형어 금지), `SPEC_SCHEMA`(표준 스펙 라벨 3슬롯), 필요시 `SYN_GROUPS`(동의어 그룹 — 카드 원본 텍스트가 방아쇠), `CANON_TERMS`(자동완성 대표 키워드 — 동의어 말고 제품군 구분어만).
  2. **모델코드 없는 시리즈 페이지**: SQL 자동 매칭 불가 → `SLUG_SQL`에 슬러그→SQL 매핑 1줄 추가.
  3. **SQL에 가격 없는 신제품**: `rndsetup_products.sql`에 행 추가(가격 SSOT). 잘못된 근사 매칭이 우려되면 `sql_price_for`의 deny 목록에 슬러그를 넣어 견적 유지.
  카탈로그 중복 카드는 `build_all_products` 초입의 **href 제외 목록**으로 숨긴다(페이지 삭제 아님). 검색 품질 검증은 빌드 후 "튜브퍼니스=해당 유형만, 퍼니스=전체"처럼 일반어/유형어가 분리되는지 확인.
- **백엔드**: `functions/`(Cloudflare Functions — `/admin`·`/api`), `rndsetup_products.sql`(D1), `catalog/leadfluid_catalog.py`.
- **배포**: Cloudflare Pages, `main` push 시 자동. 리다이렉트=`_redirects`(체인 금지, 1홉 직결).

## 4.5 제품 상세페이지 표준 (2026-08 고정)
- **모든 제품 상세페이지의 레이아웃 구성은 반드시 통일한다. 기준(최신) 템플릿 = 가오스유니온 상세페이지**(`brands/gaossunion/<slug>/index.html`): 크럼(홈›제품›계열) → h1+영문명 → 대표사진(부위 넘버링) → 정답블록 → 모델별 정가표 → 상세 설명 → 관련 링크/문의 CTA. 본문 폭 `.wrap{max-width:832px}`(모바일 768px).
- 신규 상세페이지 작성·기존 수정 시 이 구성을 따르고, 다른 세션/작업에서도 상세 레이아웃을 임의 변형하지 말 것. 삼흥·리드플루이드·Alicat 구형 레이아웃은 순차적으로 가오스 템플릿에 맞춰 통일한다(진행 중 부채).
- **좌측 포인트 바 금지**(2026-08-29 확정): `.dt-sum`·`.pkg-ans`·`.warn`·정답블록 등 어떤 박스에도 `border-left` 색 바(3~4px)를 쓰지 않는다. 배경+1px 테두리 박스로만 표현.
- 색상 팔레트(2026-08 머크풍): 프라이머리 퍼플 `#3B3695` / 진한 `#2A2570` / **링크·강조 블루 `#0F69AF`** / 연배경 `#EAF4FB` / 테두리 `#D8E4F2`. 옐로 포인트 `#EF9F27`은 경고 박스(`#FDF6E9`+`#F3E0BC`)에만. 구 네이비(#1E3A5F)·틸(#1a6e56)·테라코타(#C2410C) 금지.
- **색은 토큰 1곳에서만**(2026-09-02 확정): 팔레트 실값은 `assets/site.css` `:root` 의 `--merck / --merck-d / --merck-link / --merck-soft / --merck-line / --merck-yellow / --warn-bg / --warn-line / --danger` 9줄에만 둔다. 상세페이지 인라인 `<style>`·`style=""` 와 생성기(`_ops/build_web.py`·`build_page.py`·`tpl/product.html`)는 hex 대신 `var(--merck-*)` 만 쓴다. 색을 바꿀 일이 생기면 site.css 9줄만 고치면 전 상세페이지에 반영된다. 일괄 점검·재적용은 `python _ops\patch_merck_palette.py` (멱등, 잔여 금지색이 있으면 종료코드 1).
- **주황 글씨 금지**(2026-08-29 확정): 링크·강조 텍스트는 전부 `#0F69AF`. 오렌지 `#E8632C`는 상세페이지에서 퇴출했고 허브/통합 카탈로그 카드 가격에만 잔존(정리 대기).
- **좌측 포인트 바 금지**(2026-08-29 확정): `.dt-sum`·`.pkg-ans`·`.warn`·`.pkg-note`의 `border-left:3~4px` 색 바를 쓰지 않는다. 배경+1px 테두리 박스로 표현.

## 4.6 상세페이지 디자인 강제 (2026-09 신설 — 여기서만 바꾼다)

**디자인 SSOT 2층**

- **색 = `assets/site.css`의 `--merck-*` 토큰** (`--merck` `#3B3695` · `--merck-d` `#2A2570` · `--merck-link` `#0F69AF` · `--merck-soft` `#EAF4FB` · `--merck-line` `#D8E4F2` · `--warn-bg` `#FDF6E9` · `--warn-line` `#F3E0BC`). 색 바꾸기 = 이 토큰 8줄.
- **레이아웃·컴포넌트 = `assets/detail.css`** (기준 = 가오스유니온 상세). 상세페이지는 `<link rel="stylesheet" href="/assets/detail.css">` **1줄만** 쓴다. 본문 폭 `.wrap{max-width:920px}`.
- **페이지에 `<style>` 블록을 복사해 넣지 말 것.** 그게 지금까지 페이지마다 디자인이 갈린 원인이다(스냅샷 노화). 빌드 린터가 잔존 `<style>`을 warn으로 잡는다.

**본문 순서(2026-09-02 확정 — §4.5의 "정답블록 → 정가표" 순서를 이걸로 갱신)**

크럼 → h1 → 영문명 → 보조문구 → 대표사진 → 정답블록 → **특징 → 사양 → 규격 비교표** → 추가 섹션 → 관련링크 → 견적 CTA → 문의바 → FAQ.

- **소비자가는 본문 표에 적지 않는다.** 가격은 오른쪽 주문정보(`#buybox`) 한 곳에서만 노출한다.
- **오른쪽 열은 가격이 없는 제품에도 항상 낸다.** 가격이 하나도 없으면 site.js가 견적문의 창으로 렌더한다(견적문의 버튼 → 제품문의 모달, 모델·수량 전달). 견적 전용 제품은 JSON에 `"buybox": []` 로 명시한다. 레일 CSS(`.buyrail`)는 `assets/site.css` 에 있다 — 아직 detail.css로 이관 안 된 페이지에서도 떠야 하기 때문.
- **동일한 내용이면 표를 합친다.** 규격 비교표에서 모든 행 값이 같은 열은 자동으로 접히고, 구분되는 열이 하나만 남으면 라벨/값 2열 표 하나로 합쳐진다.
- 대표 논문은 **논문 제목 자체에 DOI 링크**를 건다.
- 구매박스 금액은 자릿수가 바뀌어도 줄바뀜·높이 변화가 없다(`detail.css`의 `.dt-buy .bb-price` 고정). 좁은 sticky 레일(250px)까지 검증.

**제조사 원문 수집 규칙 (전 브랜드 공통)**

상세페이지는 **제조사 제품 페이지 본문을 빠짐없이 옮겨 담는 것**이 기본이다. 빌드가 9개 항목을 매번 검사해 빠진 것을 `[warn] <brand>/<slug> — 원문 미수집: …` 으로 찍는다:
정답블록 · 대표사진 · 특징 · **사양(물성: 외관·순도·수분·인화점·유통기한·보관)** · 규격 비교표 · 주문정보 · FAQ · **제조사 원문 출처** · **안전정보(GHS: 그림문자·H·P·저장·폐기 — 화학품 필수)**.

- 제조사가 표로 준 것은 표로 옮긴다. 문장으로 풀어쓰지 않는다.
- **안전 정보(GHS)는 제조사 표를 라벨·값 그대로 싣는다.** 영문 라벨은 영문 그대로, H·P 코드는 번역하지 않고, 원문에 없는 경고문을 지어내 붙이지 않는다. 그림문자는 제조사 이미지를 `img/<brand>/<slug>-ghs.png` 로 저장해 그대로 쓴다.
- 수치·코드는 원문 그대로. 없는 값을 추정해 채우지 않는다.
- **페이지가 자기 자신을 설명하는 안내 문장 금지** — "~그대로 옮긴 것입니다", "~확인하실 수 있습니다", "아래 표와 같습니다" 류. 데이터는 표로만. 린터가 `LINT_BAD_PHRASES` 로 검출한다.
- 논문은 `papers` 필드에 **최대 3편**, 표는 **논문 / 저널 / 링크 3열 고정**.
  - **유명 저널 위주** — 빌드가 저널 등급(`PP_JOURNAL_T1`/`T2`)으로 정렬·필터한다. 등급 밖 저널은 제외하고 warn.
  - **근거(논문 Methods에 제품 코드·구매처 명시)가 있으면 그 논문만** 싣고, 하나도 없을 때에만 같은 배합·사양의 대표 논문으로 채운다.
  - 제품과 무관한 논문은 넣지 않는다. 없으면 섹션 생략.
- 체크리스트·스키마 전문 = `_build/products/_SCHEMA.md`

**브랜드 프로파일 = `_build/brands.json` (제품 올리기 전에 반드시 읽는다)**

브랜드마다 자료를 가져오는 사이트·구성·중요한 사양이 다르다. 그 차이를 문서가 아니라 데이터로 둔다.

- `pipeline` 이 브랜드 페이지를 뭐가 만드는지 · `page_unit` · `reference_page` 기준 통과본
- `source` 수집 방법 · `pitfalls` 사고 기록(전각 콜론 파서, 워터마크 컷, CDN 차단 등) · `pricing` 환율·할인 적용
- `families[].match` 슬러그 부분문자열 → `required_specs` 그 제품군이 반드시 갖춰야 할 사양 라벨.
  **기존 페이지 전원 공통 라벨에서 산출했다**(`_ops/seed_brand_families.py`) — 기준선 위반 0, 새 페이지가 빠뜨릴 때만 걸린다.
- `model_block_min`(기본 3) — 한 페이지에 모델을 이 수 이상 담으면 **모델별 사진·사양 블록**(`.mdl-hd` 또는 썸네일 모델명 라벨 `.thlb`)을 요구한다. 대표 모델 하나만 싣고 나머지를 드롭다운에만 두면 고객이 내용을 볼 수 없다.
- `brands/<브랜드>/` 가 있는데 여기 항목이 없으면 `NO_BRAND_PROFILE` 로 빌드가 선다.

**신규 상세페이지 = `_build/products/<brand>.json` 1건 추가 + 빌드. 손 HTML 작성 금지.**

- 스키마·필드 설명 = `_build/products/_SCHEMA.md`
- 생성기 = `_build/build.py`의 `build_product_pages()` / 템플릿 함수 `_pp_render()`
- **디자인 수정 지점은 딱 2곳**: `assets/detail.css` 또는 `_pp_render()`. 페이지 파일을 직접 고치지 않는다.
- 문의 CTA 바(전화·채널톡 QR)는 `_build/partial_ctbar.html` 1곳.

**빌드 린터 `lint_detail_pages()` — 신규 위반은 빌드를 세운다(커밋 불가).**
`_build/lint_allow.txt` 에 적힌 기존 부채만 경고로 넘어가고, 새로 생긴 위반이 있으면 `build.py` 가 **파일을 쓰지 않고 exit 1** → `go.ps1` 이 "빌드 실패"로 중단해 커밋·푸시가 막힌다. 위반 메시지에 유예 목록에 넣을 줄이 그대로 찍히니, 의도한 예외면 그 줄을 `lint_allow.txt` 에 추가한다.
검사 항목(코드): `STYLE_INLINE` `NO_DETAIL_CSS` `MISSING_BLOCK` `ORDER` `IMG_OUTSIDE` `BAD_COLOR` `BORDER_LEFT` `BAD_PHRASE` `NO_BUYBOX` `NO_SPEC_CTA` `HTML_END` `NO_BRAND_PROFILE` `REQ_SPEC` `NO_MODEL_BLOCK` —
필수 블록(크럼·h1·대표사진·정답블록) 존재와 순서, 가격표/견적 CTA 부재, 금지 색상(`#1E3A5F`·`#1a6e56`·`#C2410C`·`#E8632C`), `border-left` 3~4px 좌측 색 바, 인라인 `<style>` 잔존, `detail.css` 링크 누락, `</html>` 누락.
구형 브랜드(삼흥·리드플루이드·Alicat)는 순차 이관 부채라 검사 제외(`LINT_SKIP_BRANDS`).

**이관 현황(2026-09-02)**: detail.css 적용 = 가오스유니온·hefei·dodochem 125장. 이관 대기 = aida 5 · hench 2 · neware 2(린터가 매 빌드 warn), 그리고 구형 3개 브랜드.

## 5. 운영 원칙 (스프롤 방지)
- **갱신 1곳 원칙**: 새 기능·섹션은 "이게 바뀔 때 수정 지점이 1곳인가?"를 통과해야 추가한다. 통과 못 하면 build.py 자동화부터.
- **신규 약속 동결**: 배터리 커리큘럼 4~8단계를 채우기 전까지 새 "준비 중" 섹션·코너를 만들지 않는다. (현재 부채: 커리큘럼 5단계, 재료·시약, 전기화학 입고)
- **페이지 삭제 = 파일 삭제 + `_redirects` 1홉 301** 한 세트. 파일만 남기고 링크만 끊는 좀비 금지 — 검색 인덱스는 _redirects를 자동 반영한다.
- 보류 중 결정: 리드플루이드 모델 78페이지 유지/통합 (상세페이지 직접 유입 있어 검토 중).

## 가오스유니온 카탈로그 원본 PDF

원본(8~35 MB)을 저장소 루트에 커밋하면 **Cloudflare Pages 배포가 막힌다.** 압축본만 쓸 것 — `_ops/gaossunion_pricelist_2026_battery.pdf` · `_electrolytic_cell.pdf` · `_flow_insitu_mea.pdf`. 경로·압축 방법·가격 판독 주의는 `_ops/가오스유니온_카탈로그_원본_경로.md` 참조.
