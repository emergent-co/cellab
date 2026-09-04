# Alicat 원문 수집 방법

## egress

`www.alicat.com` · `documents.alicat.com` 모두 **클라우드·로컬 셸에서 CONNECT 403** (프록시 차단).
curl/requests 불가. **Chrome 탭 same-origin fetch() 로만 수집한다.**

## 절차

1. `navigate` 로 `https://www.alicat.com/` 진입
2. `fetch('/page-sitemap.xml')` — 제품·산업 페이지 196개 (다국어 `/de/` `/fr/` 등은 제외할 것)
   - `document-sitemap.xml` 48개 · `support-sitemap.xml` 362개 · `post-sitemap.xml` · `reps-sitemap.xml`
   - **제품 전용 sitemap 은 없다.** page-sitemap 에서 `/products/` 로 거른다.
3. 마스터 모델 목록: `/products/gas-flow/mass-flow-controller/laminar-dp-mass-flow-controllers/`
   여기 하나에 MC 계열 스톡 파트넘버가 전부 있다. 저압은 `.../low-pressure-drop-mass-flow-controllers/`
4. 데이터시트 PDF: `https://documents.alicat.com/specifications/DOC-SPECS-<시리즈>.pdf` (59종)

## 함정

- **모델 번호가 줄바꿈 없이 붙어서 나온다** — `MC-0.5SCCMMC-1SCCMMC-2SCCM...`
  파싱 전에 `.replace(/(SCCM|SLPM|PSIA|PSIG|PSID|TORRA)(?=[A-Z])/g,'$1 ')` 로 끊을 것.
  안 끊으면 `SCCMMC` 같은 가짜 시리즈 코드가 생긴다.
- **PDF 는 `documents.alicat.com` 별 오리진** — www 탭에서 fetch 하면 CORS 로 전부 실패한다.
  탭을 `https://documents.alicat.com/robots.txt` 로 옮긴 뒤 same-origin fetch 할 것.
- PDF 본문은 압축돼 있어 latin1 raw 로는 텍스트가 안 나온다. REV 번호는 대부분 못 읽고
  발행연월(`YYYY-MM`)만 잡힌다. 정확한 REV 대조는 PDF 뷰어나 pdf.js 가 필요하다.
- `get_page_text` 는 엉뚱한 `<article>`(추천글)을 잡는다. `document.body.innerText` 를 쓸 것.
- `javascript_tool` 반환값은 약 1,000자에서 잘린다. window 변수에 쌓고 slice 로 나눠 받는다.
- 71개 페이지 순회 fetch 에 약 80초 걸린다. `Runtime.evaluate` 는 45초에 타임아웃하므로
  백그라운드 async 로 던져놓고 카운터(`window.__done`)만 폴링할 것.
- 정규식 `\b(M|P|L)[A-Z]{1,5}\b` 는 PSI·PDF·PLC·MFC·LCD 같은 약어를 그대로 잡는다.
  모델 코드 판정에 그대로 쓰면 안 되고, 반드시 `-<숫자><단위>` 가 붙은 실제 파트넘버로 확인할 것.
