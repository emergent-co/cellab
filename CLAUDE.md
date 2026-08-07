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

## 4. 구조 요약 (2026-07 기준)
- **브랜드 2축**: 리드플루이드 `/leadfluid/{guide,manuals,blog}` + 삼흥에너지 `/sh-scientific/{guide,catalog,manual,blog}`.
  개별 모델 페이지는 없음 → 전부 `/leadfluid/guide/` **선택 위저드**로 통합(옛 모델 URL은 301).
- **공유 크롬(SSOT)**: `assets/site.js`(상단바·사이드바 `NAV`·푸터), `assets/site.css`. 색=네이비 `#1E3A5F`, 폰트=Pretendard.
- **데이터/빌드**: `_build/*.json`(catalog·settings·posts·products·parts·categories) → `_build/build.py`가 `sitemap.xml` 생성(직접 수정 금지).
- **백엔드**: `functions/`(Cloudflare Functions — `/admin`·`/api`), `rndsetup_products.sql`(D1), `catalog/leadfluid_catalog.py`.
- **배포**: Cloudflare Pages, `main` push 시 자동.
- 기능 페이지: `about/ trust/ contact/ faq/ repair/ requests/ alicat/ setups/ application/ pump/atoz/`.
