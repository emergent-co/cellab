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
- **NAV 4개**(2026-08 축소): 셋업 사례(`/magazine/`) · 에너지 랩 A to Z(`/magazine/battery/`) · 제품소개(`/product/` 통합 카탈로그, sub: 제품소개·메뉴얼 `/manuals/`) — NAV 1번째 · 문의하기(`/contact/`, sub: 문의하기·회사소개 `/about/`). 상단 가로 메뉴바(스크롤 시 반투명 고정) + 모바일 드로어. 규칙: **하위 메뉴가 있는 상위 메뉴는 noclick**, 첫 하위탭 href = 대표 href.
- **문의·FAQ = `/contact/` 원페이지**(2026-08 통합): 정답블록 → 검색 필터 → 카테고리 탭(구매·견적/수리·A/S/제어·소프트웨어/배송·기타) → FAQ 아코디언 26문 → 문의 폼(`#form`, Formspree `mnjkzppj`). **FAQPage JSON-LD 26문 전량 정적 렌더**(JS는 표시 토글만). `/faq/`는 301 + 파일 삭제.
- **콘텐츠 허브 = `/magazine/` "셋업 사례"** — 논문 셋업·가이드·용어사전·트러블슈팅·도입 사례를 3열 카드로 통합. `/setups/` 인덱스는 301→`/magazine/` (세부 사례 글 URL은 유지). 공정 허브: battery(커리큘럼)·deposition·heat-treatment·oxidation.
- **제품**: 삼흥 상세 `/brands/sh-scientific/<slug>/` 150+, 리드플루이드 모델 페이지 78개 잔존(+`guide` 위저드) — **모델 페이지 정리 여부는 보류 중(유입 있음)**.
- **가오스유니온(Gaoss Union) 전기화학** `/brands/gaossunion/` (2026-08 신규): 허브 + 계열 9장(기준전극·RHE·상대전극·작업전극·RDE/RRDE·전극클램프·연마용품·전기화학재료·CO₂RR촉매) · **322 SKU**.
  가격 = 2026 카탈로그 EUR × **1,620원**(SQL 상단 주석에 기준 명시) · **3% 상시 할인 대상 아님**(홈 시작가 키에 넣지 않으면 자동 미적용) · 국제 운송비 별도.
  원본 SQL 조각 = `_ops/gaossunion_products.sql`(병합 완료본, 재병합 금지). 이미지 = `img/gaossunion/<slug>-<n>.jpg`(제조사 카탈로그 추출, 사용 허가 받음).
  홈 전기화학 코너 10칸 중 **전극 4칸은 상세페이지 링크**로 전환됨. 셀 6칸(전기화학·광전기화학·분광전기화학·GDE유동·MEA전해조·PSE반응기)은 **자료 미확보로 견적 팝업 유지**.
- **공유 크롬(SSOT)**: `assets/site.js`(NAV·헤더·푸터·글 페이지 좌측 목차/우측 관련제품 레일·부품주문 팝업·검색), `assets/site.css`. 색=네이비 `#1E3A5F`.
- **데이터/빌드 (SSOT·자동 주입)** — `_build/build.py`가 처리. **아래 항목은 절대 손으로 고치지 말 것**:
  - `sitemap.xml`, `feed.xml`, `search-index.json`(전 페이지 자동 인덱스, 301 소스 제외)
  - 홈 '셋업 사례' 카드 ← `_build/paper_cases.json`
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

## 5. 운영 원칙 (스프롤 방지)
- **갱신 1곳 원칙**: 새 기능·섹션은 "이게 바뀔 때 수정 지점이 1곳인가?"를 통과해야 추가한다. 통과 못 하면 build.py 자동화부터.
- **신규 약속 동결**: 배터리 커리큘럼 4~8단계를 채우기 전까지 새 "준비 중" 섹션·코너를 만들지 않는다. (현재 부채: 커리큘럼 5단계, 재료·시약, 전기화학 입고)
- **페이지 삭제 = 파일 삭제 + `_redirects` 1홉 301** 한 세트. 파일만 남기고 링크만 끊는 좀비 금지 — 검색 인덱스는 _redirects를 자동 반영한다.
- 보류 중 결정: 리드플루이드 모델 78페이지 유지/통합 (상세페이지 직접 유입 있어 검토 중).

## 가오스유니온 카탈로그 원본 PDF

원본(8~35 MB)을 저장소 루트에 커밋하면 **Cloudflare Pages 배포가 막힌다.** 압축본만 쓸 것 — `_ops/gaossunion_pricelist_2026_battery.pdf` · `_electrolytic_cell.pdf` · `_flow_insitu_mea.pdf`. 경로·압축 방법·가격 판독 주의는 `_ops/가오스유니온_카탈로그_원본_경로.md` 참조.
