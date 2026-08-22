# 1단계 작업지시서 — 그릇 정리 + 지렛대 제작

> 이 문서는 새 Cowork 세션에 주는 작업 지시서다. 시작 전 반드시 `CLAUDE.md` → `CRITICAL_RULES.md` → `OPERATIONS.md`를 읽을 것.
> 작업 시작: `.\go.ps1` (동기화) / 작업 종료: 사용자에게 `.\go.ps1 "커밋 메시지"` 실행 요청 (에이전트는 push 불가).
> 대원칙: **갱신 1곳 원칙** — 무엇이든 바뀔 때 수정 지점이 1곳이어야 한다. 아니면 build.py 자동화부터 만든다.

## 배경 (5단계 로드맵 중 1단계)

사이트는 "에너지·배터리·수전해 실험의 자료·장비·소모품·시약 원스톱"으로 가는 중.
1단계는 **반복 작업의 비용을 낮추는 기반 공사** 4건이다. 이게 끝나야 2단계(전기화학·가오스유니온·뉴웨어 제품 등록)가 싸진다.

작업 순서: ① 3% 할인가 → ② 문의+FAQ 통합 → ③ 메뉴 축소 → ④ 제품 등록 스킬 제작

---

## ① 3% 할인가 게시 (반나절)

**목표**: 사이트에 노출되는 모든 가격을 "정가 대비 3% 할인 판매가"로 표기.

**기존 메커니즘 (이미 구축됨 — 재발명 금지)**:
- `_build/build.py`의 `build_prices()` 함수가 `rndsetup_products.sql`(정가 899행)에서 카테고리·모델별 **최저 정가**를 계산해 자동 주입한다:
  - `index.html`의 `<span data-price="키">…</span>` (4곳: muffle1050, cvdpkg, pumplab, rotary)
  - `assets/site.js`의 `/*P:키*/'…'` 마커 (11곳: 글 우측 관련제품 레일)
- **가격 개정 = SQL만 수정**이 유지돼야 한다.

**할 일**:
1. `build_prices()`의 `fmt()` 직전에 할인 적용: `sale = int(v * 0.97)`, 표기값은 sale 기준. 절사 규칙: **만원 미만 버림** (예: 정가 1,100,000 → 1,067,000 → "106만 원").
2. 홈의 가격 단서 문구(`※ 표기 가격은 정가 기준 시작가…`)를 "표기 가격은 **정가 대비 3% 상시 할인 적용가**(부가세·옵션·설치 별도)…"로 수정. 이 문구는 index.html에 1곳.
3. 상세페이지(예: `brands/sh-scientific/fume-hood-mup/index.html`)의 `pkg-note` "정가 X원"은 이번엔 손대지 않는다(수동 산재 — ④스킬과 2단계에서 SQL 주입으로 흡수 예정). 단, JSON-LD Product offers의 price는 **정가 유지**(할인가는 화면 표기만).
4. 검증: `python _build/build.py` 후 index.html 스팬·site.js 마커 값이 3% 할인 반영됐는지, `node --check assets/site.js` 통과.

## ② 문의 + FAQ 통합 원페이지 (1일)

**목표**: `/contact/` 하나로 통합. 고객이 **질문하기 전에 FAQ에서 답을 먼저 찾도록** 유도하는 구조.

**현재**: `contact/index.html`(문의폼, Formspree `mnjkzppj`) + `faq/index.html`(FAQ, FAQPage JSON-LD 보유) 분리.

**할 일**:
1. `/contact/` 재구성 (위→아래 순서):
   - 상단: "궁금한 점을 검색해 보세요" — FAQ 내 실시간 필터 검색창 (입력하면 아래 아코디언이 필터링)
   - 중단: FAQ 아코디언 (기존 faq의 Q&A 전부 이관, 카테고리 탭: 구매·견적 / 수리·A/S / 제어·소프트웨어 / 배송·기타)
   - 하단: "원하는 답이 없다면" → 기존 문의폼 (앵커 `#form`)
2. **FAQPage JSON-LD를 통합 페이지로 이관** (GEO 핵심 — Q&A 전부 스키마에 포함, raw HTML에 정적 렌더. JS 아코디언은 표시 토글만).
3. `/faq/` → `_redirects`에 `/faq/  /contact/  301` 추가 + `faq/index.html` 파일 삭제 (삭제 = 파일 삭제 + 1홉 301 세트. 삭제 권한 필요 시 allow_cowork_file_delete 사용).
4. 전 사이트의 `/faq/` 내부 링크를 `/contact/`로 교체: `assets/site.js`(NAV·푸터), `_build/build.py`(CRAWLER_LINKS), `llms.txt`, 각 페이지 FAQ 링크. **build.py CRAWLER_LINKS 수정 후 재빌드하면 CNAV는 전 페이지 자동 반영.**
5. 검증: 리다이렉트 체인 없음, 죽은 링크 없음, 전 HTML `</html>` 종료, FAQPage 스키마가 /contact/ raw HTML에 존재.

## ③ 메뉴 축소 (반나절)

**목표**: NAV 6개 → 4~5개. **작업 전 사용자에게 최종안 확인받을 것.**

**현재 NAV** (`assets/site.js`의 `NAV` 배열): 셋업 사례 / 에너지 랩 A to Z / 제품소개 / 메뉴얼 / 회사소개 / 문의하기(sub:FAQ)

**제안안** (사용자 확인용):
- 셋업 사례 / 에너지 랩 A to Z / 제품소개(sub: 메뉴얼) / 회사소개 / 문의하기 — 5개, FAQ sub는 ②에서 통합돼 제거
- 더 줄이려면: 회사소개를 문의하기 sub로 → 4개

**주의**: NAV는 site.js 한 곳(SSOT)이며 상단 가로 메뉴바·모바일 드로어에 동시 반영된다. `llms.txt`·`CLAUDE.md §4`의 NAV 서술도 함께 갱신할 것.

## ④ 제품 등록 스킬 제작 (1~2일, 최대 지렛대)

**목표**: "브랜드·모델 자료를 주면 상세페이지가 자동으로 나오는" Cowork 스킬 `rndsetup-product-page` 제작. 2단계(전기화학·가오스유니온 시약·뉴웨어 충방전기 등록)의 도구다.

**스킬 입력** (사용자가 제공): 브랜드명 / 제품 자료(제조사 URL·PDF·엑셀·이미지) / 정가(또는 공급가) / 카테고리

**스킬이 수행할 일** (기존 틀 활용이 핵심 — 새 디자인 금지):
1. **템플릿**: `brands/sh-scientific/fume-hood-mup/index.html`을 표준 틀로 복제·치환 (이 페이지가 보강 완료판: 특징 리스트 → 사양표 → 소모품표 → 상세 이미지 → 연락 바 → FAQ 6문 → Product·FAQPage·Breadcrumb JSON-LD 순). PRO급 장비는 `PRO_상세페이지_구성안.md` 준수.
2. **경로 규칙**: `brands/<brand-slug>/<product-slug>/index.html`. 신규 브랜드면 `brands/<brand-slug>/index.html` 허브도 생성(기존 브랜드 허브 틀 참조).
3. **데이터 등록**: `rndsetup_products.sql`에 INSERT 행 추가 (sku, daebun, sobun, model, name, features, supply_price, retail_price, image_url 등 — 기존 행 형식 준수). 가격 표기는 ①의 3% 할인 로직이 자동 처리.
4. **필수 GEO 요소** (하나라도 빠지면 미완성): 정답블록(dt-ans), 사양표, 정가·판매가, canonical, description(따옴표 이중 금지 — 과거 112페이지 사고 있었음), Product+FAQPage+Breadcrumb JSON-LD, 견적 버튼 `data-quote="…"`.
5. **마감**: `python _build/build.py` 실행 → 사이트맵·검색 인덱스·CNAV 자동 배선 확인 → 전 HTML `</html>` 검증.
6. **스킬 작성 시**: 위 절차를 SKILL.md로 정리해 save_skill로 저장. 트리거 문구: "제품 올려줘", "상세페이지 만들어줘", "신규 브랜드 등록" 등.

**주의사항**:
- 이미지: 제조사 정식 자산 또는 사용자 제공분만. 타사(오실라 등) 사진 무단 사용 금지.
- 브랜드 슬러그 예약: `gaossunion`(가오스유니온·화학), `neware`(뉴웨어·충방전기), 전기화학은 브랜드 확정 전까지 `electrochem`.

---

## 완료 기준 체크리스트

- [ ] 사이트 노출 가격 전부 3% 할인가, 빌드 재실행만으로 갱신됨
- [ ] /contact/ = 검색→FAQ→폼 원페이지, FAQPage 스키마 보존, /faq/ 301+파일 삭제, 내부 링크 0 잔존
- [ ] NAV 4~5개 (사용자 승인안), llms.txt·CLAUDE.md 일치
- [ ] `rndsetup-product-page` 스킬 저장 완료, 테스트로 더미 1페이지 생성→검증→삭제까지 확인
- [ ] 최종: 빌드 통과, 전 HTML `</html>`, 리다이렉트 체인 0, 죽은 링크 0
- [ ] CLAUDE.md §4·§5 변경사항 반영 후 사용자에게 배포 명령 안내
