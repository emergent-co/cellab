// functions/admin/_shell.js — 관리자 페이지 공용 셸
//   /member/ 와 같은 헤더 + 왼쪽 메뉴를 씌운다.
//   관리자 메뉴를 눌렀다고 왼쪽 메뉴가 사라지면 길을 잃는다.
//   (파일명이 _ 로 시작하므로 라우팅되지 않는다)

export const SHELL_CSS = `
:root{
  --navy:#3B3695;--navy-dk:#2A2570;--ink:#1A1A1A;--mut:#6B6B6B;--mut-2:#9A9A9A;
  --line:#EAEAEA;--bg:#F2F4F6;--soft-blue:#EAF4FB;--teal:#1a6e56;--warn:#C2410C;
  --side:240px;--head:60px;
}
html,body{font-family:'Pretendard Variable',Pretendard,-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
  color:var(--ink);background:var(--bg)}
.ashell{min-height:100vh}
.ahead{position:fixed;left:0;right:0;top:0;height:var(--head);background:#fff;
  border-bottom:1px solid var(--line);display:flex;align-items:center;gap:16px;padding:0 22px;z-index:35}
.ahead .hbrand{font-size:21px;font-weight:700;letter-spacing:-.01em;color:var(--ink);
  text-decoration:none;flex:0 0 auto;line-height:1}
.ahead .hbrand:hover{color:var(--navy)}
.ahead .hbrand em{font-style:normal;font-size:12.5px;font-weight:600;color:var(--mut);margin-left:7px}
.ahead h1{font-size:14px;font-weight:700;color:var(--mut);padding-left:16px;
  border-left:1px solid var(--line);line-height:1.2;flex:0 0 auto;margin:0}
.ahead .who{margin-left:auto;font-size:13.5px;color:var(--mut);white-space:nowrap}
.ahead .who a{color:var(--mut);text-decoration:none}
.ahead .who a:hover{color:var(--ink);text-decoration:underline}
.ahead .burger{display:none;background:0;border:0;font-size:22px;line-height:1;cursor:pointer;
  width:38px;height:38px;flex:0 0 auto;padding:0}
.aside{position:fixed;left:0;top:var(--head);bottom:0;width:var(--side);background:#fff;
  border-right:1px solid var(--line);z-index:30;display:flex;flex-direction:column;overflow-y:auto}
.aside nav{padding:14px 0}
.aside nav a{display:block;padding:16px 22px;font-size:15px;font-weight:700;color:var(--mut);
  border-left:4px solid transparent;text-decoration:none}
.aside nav a:hover{background:#FAFAFB}
.aside nav.adm{padding:0 0 12px;border-top:1px solid var(--line);margin-top:4px}
.aside nav.adm .admh{font-size:11px;font-weight:800;color:var(--mut-2);letter-spacing:.04em;padding:14px 22px 6px}
.aside nav.adm a{padding:11px 22px;font-size:13.5px;font-weight:600}
.aside nav.adm a:hover{background:var(--soft-blue);color:var(--navy)}
.aside nav a.on{color:var(--ink);font-weight:800;border-left-color:var(--navy);background:var(--soft-blue)}
.ascrim{display:none;position:fixed;inset:0;background:rgba(26,26,26,.4);z-index:25}
.ascrim.on{display:block}
.main{margin-left:var(--side);padding-top:var(--head)}
/* 페이지 본문은 가운데 정렬 폭으로 — 넓은 화면에서 좌우로 늘어지지 않게 */
.main>.chips,.main>.srch,.main>.tabs,.main>.wrap{max-width:980px;margin-left:auto;margin-right:auto}
/* 페이지 안의 sticky 막대는 셸 헤더 아래에 붙는다 */
.main>.chips{top:var(--head);border-radius:0}
.main>.srch{position:sticky;top:calc(var(--head) + 44px);z-index:14}
.main>.wrap{padding-top:14px}
/* 탭은 내용만큼만 */
.main>.tabs button{flex:0 0 auto;padding:10px 20px}
@media(max-width:900px){
  :root{--side:0px}
  .aside{transform:translateX(-260px);width:260px;transition:transform .22s}
  .aside.on{transform:none}
  .ahead .burger{display:flex;align-items:center;justify-content:center}
  .ahead .hbrand{font-size:17px}
  .ahead .hbrand em{display:none}
  .ahead h1{display:none}
  .main{margin-left:0}
  .main>.tabs button{flex:1}
  .main>.srch{top:calc(var(--head) + 44px)}
}
`;

/** active: 'orders' | 'settle' | 'members' | 'products' */
export function shellTop(title, active) {
  const on = (k) => (k === active ? ' class="on"' : '');
  return `<div class="ashell">
<header class="ahead">
  <button class="burger" id="aBurger" aria-label="메뉴">☰</button>
  <a class="hbrand" href="/">실험셋업연구소<em>관리자</em></a>
  <h1>${title}</h1>
  <div class="who"><a href="/member/">← 내 화면으로</a></div>
</header>
<aside class="aside" id="aSide">
  <nav>
    <a href="/member/#home">홈</a>
    <a href="/member/#new">주문하기</a>
    <a href="/member/#orders">주문 현황</a>
    <a href="/member/#settle">정산하기</a>
    <a href="/member/#me">회원정보</a>
  </nav>
  <nav class="adm">
    <div class="admh">관리자</div>
    <a href="/admin/orders/"${on('orders')}>주문 관리</a>
    <a href="/admin/settlement/"${on('settle')}>정산 관리</a>
    <a href="/admin/customers/"${on('members')}>멤버십 · 문의</a>
  </nav>
</aside>
<div class="ascrim" id="aScrim"></div>
<main class="main">`;
}

export const SHELL_END = `</main></div>
<script>
(function(){
  var s=document.getElementById('aSide'), c=document.getElementById('aScrim'), b=document.getElementById('aBurger');
  if(b) b.onclick=function(){ s.classList.toggle('on'); c.classList.toggle('on'); };
  if(c) c.onclick=function(){ s.classList.remove('on'); c.classList.remove('on'); };
})();
</script>`;
