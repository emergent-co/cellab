# 크롬 확장 ↔ 주문 페이지 연동 규약

주문 페이지: `https://rndsetup.com/order/` (해시 `#new` = 주문하기 화면)

## 보내는 형식

확장이 긁어온 품목을 아래 형태로 넘기면, 주문 페이지가 미리보기 표를 띄우고
사용자가 확인한 뒤 장바구니에 담는다. (자동으로 담지 않는다 — 잘못 긁힌 줄을 거르기 위해)

```js
{
  type: 'rndsetup:items',
  site: '대한과학',                       // 어디서 가져왔는지 (표시용, 선택)
  items: [
    { name: 'Potassium hydroxide',       // 제품명   (필수)
      option: '500g, 시약급',             // 옵션     (선택)
      qty: 2,                            // 수량     (없으면 1)
      url: 'https://.../product/12345' } // 상품 URL (선택)
  ]
}
```

키 이름은 아래 중 아무거나 받는다: `name|title|product`, `option|options|spec`,
`qty|quantity`, `url|link|href`. 이름이 빈 항목은 버린다.

## 전달 경로 — 둘 중 편한 쪽

### A. content script에서 postMessage (가장 간단, manifest 추가 설정 없음)

`https://rndsetup.com/order/*` 에 주입된 content script에서:

```js
window.postMessage({ type:'rndsetup:items', site:'대한과학', items: rows }, location.origin);
```

주문 페이지가 항상 이 메시지를 듣고 있다. 사용자가 '여러 건 한 번에'를 누르지
않아도 받는다.

### B. 페이지가 확장을 호출 (버튼을 누르면 확장이 동작하는 방식)

`manifest.json` 에:

```json
"externally_connectable": { "matches": ["https://rndsetup.com/*"] }
```

`background`(service worker)에서:

```js
chrome.runtime.onMessageExternal.addListener(function (msg, sender, sendResponse) {
  if (msg.type !== 'rndsetup:pull') return;
  // 즉시 줄 수 있으면:
  sendResponse({ items: rows, site: '대한과학' });
  // 창을 띄워 사용자가 담게 하는 방식이면 응답 없이 두고,
  // 나중에 A(postMessage)로 보내면 된다. 페이지는 대기 화면을 띄우고 기다린다.
  return true;
});
```

그리고 주문 페이지 `order/index.html` 상단의

```js
var EXT_ID = '';   // ← 여기에 확장 ID(32자) 를 넣는다
```

## 동작 순서

1. 사용자가 `여러 건 한 번에` 클릭
2. `EXT_ID`가 있으면 확장에 `rndsetup:pull` 전송
   - 바로 응답 → 미리보기 표
   - 응답 없음 → "가져오는 중" 대기 화면 (A로 오는 것을 기다림)
   - 확장 미설치/오류 → 붙여넣기 폼으로 자동 전환
3. `EXT_ID`가 비어 있으면 곧바로 붙여넣기 폼

## 주문 페이지가 저장하는 값

| 확장이 준 값 | 저장되는 곳 |
|---|---|
| name | `order_items.name` (품명) |
| option | `order_items.spec` (규격·옵션) |
| qty | `order_items.qty` |
| url | `order_items.link` (관리자 화면·주문 상세에서 링크로 열림) |
