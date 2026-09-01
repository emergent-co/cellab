/* ============================================================
   실험셋업연구소 공유 헤더·푸터 (site.js) — 전 페이지 동일 구조 주입(SSOT)
   각 페이지의 <div id="pumplab-header"></div> / <div id="pumplab-footer"></div>
   자리에 아래 마크업을 넣는다. 헤더·푸터는 여기서만 고치면 전 페이지 반영.
   ============================================================ */
(function () {
  var path = location.pathname;

  var SEARCH_INDEX = [
    { t:'홈 — 셋업으로 읽는 에너지·소재', u:'/', k:'에너지 소재 공정 셋업 매거진 논문 셋업 공정 조건 필요 장비 소성 증착 가스 분위기 유량 배터리 열처리 유체 펌프 분석', c:'페이지' },
    { t:'리드플루이드(LeadFluid) 펌프 — 전체 제품', u:'/brands/leadfluid/', k:'리드플루이드 leadfluid 정품 국내 as 수리 3년보증 연동 시린지 기어 정량펌프 baoding ingersoll rand 나비엠알오 제어 소프트웨어', c:'리드플루이드' },
    { t:'Masterflex·Watson-Marlow 연동펌프 국내 대안', u:'/compare/imported-peristaltic-alternative/', k:'마스터플렉스 masterflex 왓슨말로우 watson-marlow 이즈마텍 ismatec 대안 비교 갈아타기 수입 연동펌프 국내 as 제어', c:'비교' },
    { t:'ALICAT 질량유량계(MFC) 브랜드', u:'/brands/alicat/', k:'alicat 알리캣 질량유량계 mfc mass flow controller 다기체 응답속도 rs485 modbus 소프트웨어 호환 장비', c:'호환 장비' },
    { t:'삼흥에너지(SH-Scientific) 전기로·튜브퍼니스 — 제품 선택·견적', u:'/brands/sh-scientific/guide/', k:'삼흥에너지 sh scientific 튜브퍼니스 관상로 전기로 머플로 열처리 온도 스케줄 가스 연동 설치 지역 as 취급 제품 선택 가이드 견적문의 구성 종류 온도 분위기 컨트롤러 옵션 시료 공정', c:'호환 장비' },
    { t:'삼흥에너지 전기로·튜브퍼니스 메뉴얼', u:'/brands/sh-scientific/manual/', k:'삼흥에너지 전기로 튜브퍼니스 메뉴얼 사용법 승온 프로그램 온도컨트롤러 sp590 안전 주의사항 설치 열처리 sh scientific', c:'호환 장비' },
    { t:'삼흥에너지 전기로·튜브퍼니스 설치·A/S 블로그', u:'/brands/sh-scientific/blog/', k:'삼흥에너지 전기로 튜브퍼니스 설치 as 점검 사례 블로그 설치 체크리스트 열처리 sh scientific', c:'호환 장비' },
    { t:'소프트웨어 제어 펌프 시스템', u:'/requests/', k:'자동화 무인 관류 채널 독립 유량 기록 재현 modbus rs485 python 스케줄 레시피 로그 다펌프 동기', c:'실험을 자동화할 때' },
    { t:'프로그래밍 제어 (Modbus·RS-485·Python)', u:'/requests/#control', k:'modbus rs485 python 시리얼 제어 자동화 스크립트 레지스터', c:'실험을 자동화할 때' },
    { t:'유량 스케줄·ramp·레시피', u:'/requests/#schedule', k:'스케줄 ramp 램프 레시피 시퀀스 프로파일 반복 저장', c:'실험을 자동화할 때' },
    { t:'다펌프 동기·무인 연속 운전', u:'/requests/#sync', k:'다펌프 동기 무인 장시간 연속 운전 대조군 채널 독립', c:'실험을 자동화할 때' },
    { t:'운전 로그 기록·재현', u:'/requests/#record', k:'로그 기록 csv 재현 프로파일 재현성', c:'실험을 자동화할 때' },
    { t:'펌프 고르는 방법', u:'/application/pump-selection.html', k:'펌프 선택 종류 연동 시린지 기어 정량 유량 정밀도 미량 추천 위저드', c:'펌프를 고를 때' },
    { t:'튜브 선택 가이드', u:'/application/tube-selection.html', k:'튜브 재질 실리콘 tygon pharmed viton 화학 적합성 교체', c:'펌프를 고를 때' },
    { t:'관류배양 자동 배지교환 (세포배양 관류)', u:'/application/cell-culture-perfusion.html', k:'관류 perfusion 배지 교환 연동 페리스탈틱 무오염 세포배양', c:'실험 가이드' },
    { t:'연속배양(chemostat) 유량제어', u:'/application/chemostat-continuous-culture.html', k:'연속배양 chemostat 희석률 정상상태 배지 공급 배출 연동펌프', c:'실험 가이드' },
    { t:'광배양·미세조류 정량공급', u:'/application/photobioreactor-microalgae.html', k:'광배양 미세조류 광생물반응기 photobioreactor co2 영양 정량 공급', c:'실험 가이드' },
    { t:'flow chemistry 연속흐름 반응', u:'/application/flow-chemistry.html', k:'flow chemistry 연속흐름 반응 시린지 유량비 체류시간 마그네틱 유기용매', c:'실험 가이드' },
    { t:'장기칩·오가노이드 관류', u:'/application/organ-on-chip-perfusion.html', k:'장기칩 organ on chip 오가노이드 관류 미세유체 저유량 전단응력', c:'실험 가이드' },
    { t:'실험 가이드 허브', u:'/application/', k:'응용별 셋업 가이드 펌프 튜브', c:'실험 가이드' },
    { t:'펌프 셋업 사례 — 실제 도입·제어·유량 보정', u:'/brands/leadfluid/blog/', k:'펌프 셋업 사례 도입 제어 유량 보정 도금 다펌프 튜브퍼니스 mfc 스토리', c:'펌프 셋업 사례' },
    { t:'리드플루이드 국내 A/S·정품·3년보증', u:'/trust/', k:'리드플루이드 leadfluid 국내 as 수리 정품 보증 신뢰 진단 품질', c:'호환 장비' },
    { t:'연동펌프 유량 캘리브레이션 방법', u:'/pump/atoz/flow-calibration/', k:'유량 캘리브레이션 보정 calibration 연동펌프 설정값 실제유량 드리프트 저울 메스실린더 보정계수 재현성', c:'펌프를 고를 때' },
    { t:'연동펌프 튜브 규격·펌프헤드 가이드', u:'/pump/atoz/tube-size-guide/', k:'튜브 규격 번호 내경 mm 13 14 16 25 17 18 펌프헤드 YT25 YZ35 튜브 재질 실리콘 tygon pharmed viton 연동펌프', c:'펌프를 고를 때' },
    { t:'셋업 사례 — 논문 셋업·가이드·도입 사례', u:'/magazine/', k:'셋업 사례 매거진 논문 셋업 분석 열처리 증착 퍼니스 유체 펌프 공정 조건 장비 magazine setups', c:'셋업 사례' },
    { t:'온도컨트롤러(SP590·NOVA500E) 사용법 가이드', u:'/temp-controller-guide/', k:'온도컨트롤러 sp590 sp570 nova500e 삼원테크 사용법 전기로 온도 설정 승온 유지 하강 반복 hold 무한반복 rs485 가상 시뮬레이터 삼흥에너지', c:'호환 장비' },
    { t:'문의하기 · 자주 묻는 질문(FAQ)', u:'/contact/', k:'문의 상담 수리 개발 견적 실험 질문 faq 가격 할인 납기 배송 설치 보증 정량펌프 연동펌프 튜브 채널 제어 소프트웨어', c:'문의하기' }
  ];
  // 헤더 검색창 제거(2026-08)로 인덱스 페치는 검색 UI가 있는 페이지에서만 수행
  function loadSearchIndex() {
    fetch('/_build/posts.json').then(function (r) { return r.json(); }).then(function (d) {
      (d.posts || []).forEach(function (p) {
        SEARCH_INDEX.push({ t: p.title, u: p.url,
          k: (p.tags || []).join(' ') + ' ' + (p.journal || '') + ' ' + (p.model_focus || '') + ' ' + (p.application || ''),
          c: (p.type === 'setup' ? '사례 아카이브' : '블로그') });
      });
    }).catch(function () {});
    // 전 페이지 자동 인덱스(빌드 생성) 병합 — 제품 상세·허브·메뉴얼 등 전부 검색 가능
    fetch('/search-index.json').then(function (r) { return r.json(); }).then(function (d) {
      var seen = {};
      SEARCH_INDEX.forEach(function (it) { seen[(it.u || '').replace(/\/$/, '')] = 1; });
      (d.items || []).forEach(function (it) {
        var key = (it.u || '').replace(/\/$/, '');
        if (!seen[key]) { seen[key] = 1; SEARCH_INDEX.push(it); }
      });
    }).catch(function () {});
  }

  var ICONS = {
    home:'<svg viewBox="0 0 24 24"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>',
    sw:'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
    guide:'<svg viewBox="0 0 24 24"><path d="M9 3h6M10 3v6l-5.2 8.6A2 2 0 0 0 6.5 21h11a2 2 0 0 0 1.7-3.4L14 9V3"/></svg>',
    feed:'<svg viewBox="0 0 24 24"><circle cx="6" cy="18" r="1.6"/><path d="M4 11a9 9 0 0 1 9 9M4 5a15 15 0 0 1 15 15"/></svg>',
    faq:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3 2.4c-.8.3-1 .8-1 1.6M12 17h.01"/></svg>',
    contact:'<svg viewBox="0 0 24 24"><path d="M4 5h16v12H8l-4 3z"/></svg>',
    star:'<svg viewBox="0 0 24 24"><path d="M12 3l2.6 5.9 6.4.6-4.8 4.3 1.4 6.3L12 17.8 6.4 20.4l1.4-6.3L3 9.8l6.4-.6z"/></svg>',
    pick:'<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h7"/></svg>',
    shield:'<svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M9.5 12l1.8 1.8L15 10"/></svg>',
    gas:'<svg viewBox="0 0 24 24"><path d="M4 9c2-2.2 4 2.2 6 0s4-2.2 6 0 4 2.2 4 2.2M4 15c2-2.2 4 2.2 6 0s4-2.2 6 0 4 2.2 4 2.2"/></svg>',
    vacuum:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 12l4-3"/><path d="M12 5v2"/></svg>',
    devices:'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M7 8h3M7 12h2"/></svg>',
    find:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    wrench:'<svg viewBox="0 0 24 24"><path d="M14.5 6.5a3.5 3.5 0 0 1-4.6 4.6L5 16l3 3 4.9-4.9a3.5 3.5 0 0 0 4.6-4.6l-2.1 2.1-2-2 2.1-2.1z"/></svg>'
  };
  // 규칙: 하위 메뉴가 있는 상위 메뉴는 클릭 불가(noclick) — 이동은 하위 메뉴로만.
  var NAV = [
    { href:'/product/', label:'툴·실험장비', icon:'devices', noclick:true, sub:[
        ['/product/', '통합 카탈로그'],
        ['/manuals/', '메뉴얼']
      ] },
    { href:'/materials/', label:'소재', icon:'guide' },
    { href:'/magazine/', label:'셋업 사례', icon:'feed' },
    { href:'/info/', label:'유용한 정보', icon:'pick', noclick:true, sub:[
        ['/info/', '제품 정보'],
        ['/wiki/', '배터리 사전']
      ] },
    { href:'/contact/', label:'문의하기', icon:'contact', noclick:true, sub:[
        ['#chat',     '문의하기'],
        ['/contact/', 'FAQ'],
        ['/about/',   '회사소개']
      ] }
  ];
  function matches(href){ if(href.indexOf('#') > -1) return false; return href === '/' ? path === '/' : path === href; }
  function subOnPage(href){ var i = href.indexOf('#'); if(i === -1) return false; return path === (href.slice(0, i) || '/'); }
  var navHTML = NAV.map(function (n) {
    // 부모 페이지(예: /pumps/)에 있으면 부모를 활성화하고, 하위 페이지에 있으면 해당 하위탭을 활성화한다.
    var cur = matches(n.href);
    var row = n.noclick
      ? '<div class="s-item s-noclick">' + (ICONS[n.icon] || '') + '<span>' + n.label + '</span></div>'
      : '<a class="s-item' + (cur ? ' active' : '') + '" href="' + n.href + '"' +
        (cur ? ' aria-current="page"' : '') + '>' + (ICONS[n.icon] || '') +
        '<span>' + n.label + '</span></a>';
    if (n.sub) {
      // 현재 페이지와 일치하는 하위탭을 찾는다: 경로형 우선, 해시형은 해시 일치, 해시 없으면 첫 하위탭 기본 활성.
      var activeIdx = -1;
      n.sub.forEach(function (s, i) {
        var href = s[0], hi = href.indexOf('#');
        if (hi === -1) { if (matches(href)) activeIdx = i; }
        else if (subOnPage(href) && location.hash === href.slice(hi)) { activeIdx = i; }
      });
      if (activeIdx === -1 && !location.hash) {
        n.sub.forEach(function (s, i) { if (activeIdx === -1 && subOnPage(s[0])) activeIdx = i; });
      }
      row += '<div class="s-sub">' + n.sub.map(function (s, i) {
        var sc = (i === activeIdx);
        return '<a class="' + (sc ? 'active' : '') + '" href="' + s[0] + '"' +
               (sc ? ' aria-current="page"' : '') + '>' + s[1] + '</a>';
      }).join('') + '</div>';
    }
    return row;
  }).join('');

  // 상단 가로 메뉴바 (데스크톱) — 사이드바와 같은 NAV 데이터, 서브는 호버 드롭다운
  var topNavHTML = NAV.map(function (n) {
    var cur = matches(n.href);
    var html = '<div class="tn-item">' +
      '<a class="tn-link' + (cur ? ' active' : '') + '" href="' + n.href + '"' +
      (cur ? ' aria-current="page"' : '') + '>' + n.label + '</a>';
    if (n.sub) {
      html += '<div class="tn-dd">' + n.sub.map(function (s) {
        var sc = matches(s[0]);
        return '<a class="' + (sc ? 'active' : '') + '" href="' + s[0] + '">' + s[1] + '</a>';
      }).join('') + '</div>';
    }
    return html + '</div>';
  }).join('');

  var HEADER =
    '<header class="ch-top">' +
      '<button class="ch-burger" type="button" aria-label="메뉴" aria-expanded="false"><span></span><span></span><span></span></button>' +
      '<a class="ch-brand" href="/">실험셋업연구소</a>' +
      '<form class="ch-msearch" action="/product/" method="get" role="search">' +
        '<input type="search" name="q" placeholder="제품명·모델명 검색 — 예: 튜브퍼니스, BT101S, MFC" aria-label="제품 검색" autocomplete="off">' +
        '<button type="submit"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg><span>검색</span></button>' +
      '</form>' +
      '<a class="ch-ic srch" href="/product/" aria-label="제품 검색" title="제품 검색"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg></a><a class="ch-ic ch-cart" href="/cart/" aria-label="장바구니" title="장바구니"><svg viewBox="0 0 24 24"><circle cx="9" cy="20" r="1.6"/><circle cx="17" cy="20" r="1.6"/><path d="M3 4h2l2.6 12h10.8L21 8H6"/></svg><i class="ch-cnt" hidden>0</i></a>' +
      '<a class="ch-ic" href="/login/" aria-label="로그인" title="로그인"><svg viewBox="0 0 24 24"><circle cx="12" cy="8.5" r="3.6"/><path d="M4.5 20c1.6-3.4 4.3-5 7.5-5s5.9 1.6 7.5 5"/></svg></a>' +
    '</header>' +
    '<nav class="ch-nav" aria-label="주 메뉴">' + topNavHTML + '</nav>' +
    '<aside class="ch-side" id="chSide"><nav>' + navHTML + '</nav>' +
      '<div class="ch-side-foot">에너지·배터리·수전해 실험장비 원스톱 스토어<br>논문 셋업으로 검증된 장비 구성 · 셋업 매거진 운영</div>' +
      '<a id="adminNav" href="/admin" style="display:block;margin:12px 14px 8px;font-size:11px;color:#9aa3ad;text-decoration:none;border-top:1px solid #e6eaf0;padding-top:9px">\u2699 관리자</a>' +
      '<a id="adminOut" href="#" style="display:none;margin:0 14px 10px;font-size:10.5px;color:#b3b9c2;text-decoration:none">로그아웃</a>' +
    '</aside>' +
    '<div class="ch-scrim" id="chScrim"></div>';

  var FOOTER =
    '<section style="background:#2A2570;padding:26px 20px;text-align:center">' +
      '<div style="max-width:560px;margin:0 auto">' +
        '<div style="color:#fff;font-weight:800;font-size:16px;line-height:1.4;margin-bottom:4px">새 논문 셋업이 올라오면 이메일로 알려드립니다</div>' +
        '<div style="color:#C9D4E2;font-size:13px;margin-bottom:14px">실험 셋업 매거진 구독 · 새 글 알림만, 스팸 없음</div>' +
        '<form action="https://formspree.io/f/mnjkzppj" method="POST" style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap" data-ga="subscribe">' +
          '<input type="hidden" name="_subject" value="[매거진 구독] 새 구독 신청">' +
          '<input type="hidden" name="구분" value="실험 셋업 매거진 구독">' +
          '<input type="hidden" name="_next" value="https://rndsetup.com/?subscribed=1">' +
          '<input type="email" name="email" required placeholder="이메일 주소" style="flex:1;min-width:220px;max-width:320px;height:44px;border:none;border-radius:9px;padding:0 14px;font-size:14px;font-family:inherit">' +
          '<button type="submit" style="height:44px;padding:0 24px;border:none;border-radius:9px;background:#EF9F27;color:#1a1a1a;font-weight:800;font-size:14px;cursor:pointer;font-family:inherit">구독</button>' +
        '</form>' +
        '<div style="color:#8fa3ba;font-size:12px;margin-top:10px">RSS로도 구독 가능 · <a href="/feed.xml" style="color:#C9D4E2;text-decoration:underline">feed.xml</a></div>' +
      '</div>' +
    '</section>' +
    '<footer class="chrome-footer">' +
      '<div class="cf-inner">' +
        '<div class="cf-cols">' +
          '<div class="cf-col"><h4>바로가기</h4>' +
            '<a href="/product/?q=리드플루이드">제품·모델</a><a href="/about/">회사소개</a><a href="/trust/">정품·인증</a><a href="/repair/">A/S·수리</a></div>' +
          '<div class="cf-col"><h4>문의</h4>' +
            '<a href="/contact/">일반 문의</a><a href="/contact/#quote">견적 문의</a><a href="/contact/">자주 묻는 질문(FAQ)</a></div>' +
          '<div class="cf-col"><h4>고객센터</h4>' +
            '<a href="mailto:info@rndsetup.com">info@rndsetup.com</a>' +
            '<a href="tel:+827089832600">070-8983-2600</a>' +
            '<span>에너지·배터리·수전해 실험장비 원스톱 스토어 · 셋업 매거진</span></div>' +
        '</div>' +
        '<div class="cf-co"><strong>실험셋업연구소</strong> (이머전트) · 이영현 · 070-8983-2600 · 사업자등록 328-03-02926<br>' +
          '부산광역시 · 서비스·도매/소매업 · 정밀·과학기기 도매, 화학제품 도매, 전기·전자·정밀기기 수리</div>' +
        '<div class="cf-cp">© 2026 실험셋업연구소. All Rights Reserved.</div>' +
      '</div></footer>';

  var CTA_FAB =
    '<div class="cta-chat" id="ctaChat">' +
      '<div class="cc-panel" role="dialog" aria-label="문의 패널">' +
        '<div class="cc-head">' +
          '<div class="cc-brand">실험셋업연구소</div>' +
          '<button class="cc-x" type="button" aria-label="닫기" onclick="ccToggle(false)">×</button>' +
        '</div>' +
        '<div class="cc-body">' +
          '<div class="cc-greet"><b>무엇을 도와드릴까요?</b><br>정량펌프·질량유량계(MFC)·진공·자동화 셋업과 제어, 수리까지 편하게 문의하세요.</div>' +
          '<a class="cc-cta" href="/contact/" data-ga="fab_contact">문의하기 →</a>' +
          '<div class="cc-note">보통 몇 분 내 답변드려요</div>' +
          '<div class="cc-alt">다른 방법으로 문의</div>' +
          '<div class="cc-chans">' +
            '<a href="http://pf.kakao.com/_GCsjX" target="_blank" rel="noopener" data-ga="fab_kakao">카카오톡</a>' +
            '<a href="tel:+827089832600" data-ga="fab_tel">전화</a>' +
            '<a href="mailto:info@rndsetup.com" data-ga="fab_email">이메일</a>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<button class="cc-launch" type="button" aria-label="문의하기" onclick="ccToggle()">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4z"/></svg><span>문의</span>' +
      '</button>' +
    '</div>';

  var REPAIR_MODAL =
    '<div class="rp-modal" id="repairModal">' +
      '<div class="rp-box">' +
        '<button class="rp-close" type="button" aria-label="닫기">×</button>' +
        '<h3>무료 수리진단 신청</h3>' +
        '<p class="rp-sub">모델명·증상·연락처만 적으면 끝. 보내실 주소를 안내드립니다.</p>' +
        '<form id="repairPopForm">' +
          '<input type="hidden" name="_subject" value="[무상 진단 신청] 펌프 수리">' +
          '<label>펌프 모델명 <span class="req">*</span>' +
            '<input type="text" name="모델명" required placeholder="예: BT100S"></label>' +
          '<label>제조사 <span class="req">*</span>' +
            '<input type="text" name="제조사" required placeholder="예: LeadFluid / Masterflex / 기타"></label>' +
          '<label>증상 <span class="req">*</span>' +
            '<textarea name="증상" required placeholder="예: 유량이 안 나옴 / 소음 / 안 켜짐 / 누액"></textarea></label>' +
          '<label>연락처(이메일 또는 전화) <span class="req">*</span>' +
            '<input type="text" name="연락처" required placeholder="you@lab.ac.kr 또는 010-0000-0000"></label>' +
          '<label>회사·연구실명 <span class="req">*</span>' +
            '<input type="text" name="소속" required placeholder="OO대학교 OO연구실"></label>' +
          '<button class="rp-send" type="submit">무료 수리진단 신청 보내기</button>' +
        '</form>' +
        '<div class="rp-done" id="repairPopDone"><div class="ok">✓</div><h3>신청이 접수되었습니다</h3><p>보내실 주소를 안내드리겠습니다.</p></div>' +
      '</div>' +
    '</div>';

  function initRepairModal() {
    if (document.getElementById('repairModal')) return;
    document.body.insertAdjacentHTML('beforeend', REPAIR_MODAL);
    var rm = document.getElementById('repairModal');
    window.openRepairForm = function () { rm.classList.add('open'); document.body.style.overflow = 'hidden'; };
    window.closeRepairForm = function () { rm.classList.remove('open'); document.body.style.overflow = ''; };
    rm.addEventListener('click', function (e) { if (e.target === rm) closeRepairForm(); });
    rm.querySelector('.rp-close').addEventListener('click', closeRepairForm);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeRepairForm(); });
    document.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target.closest('.js-repair') : null;
      if (t) { e.preventDefault(); openRepairForm(); }
    });
    var rf = document.getElementById('repairPopForm');
    rf.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target, btn = f.querySelector('.rp-send');
      btn.disabled = true; btn.textContent = '보내는 중…';
      fetch('https://formspree.io/f/mnjkzppj', { method: 'POST', body: new FormData(f), headers: { 'Accept': 'application/json' } })
        .then(function (r) {
          btn.disabled = false; btn.textContent = '무료 수리진단 신청 보내기';
          if (r.ok) {
            if (typeof gtag === 'function') gtag('event', 'generate_lead', { lead_type: 'repair_diagnosis', page_path: location.pathname });
            f.style.display = 'none'; document.getElementById('repairPopDone').style.display = 'block';
          } else { alert('전송에 실패했습니다. 이메일로 보내주세요: info@rndsetup.com'); }
        })
        .catch(function () { btn.disabled = false; btn.textContent = '무료 수리진단 신청 보내기'; alert('전송에 실패했습니다. 이메일로 보내주세요: info@rndsetup.com'); });
    });
  }

  function inject() {
    // 임베드 모드(?embed=1): iframe 등으로 삽입 시 사이트 헤더·푸터를 넣지 않는다.
    if (/[?&]embed=1/.test(location.search)) {
      var eh = document.getElementById('pumplab-header'); if (eh) eh.remove();
      var ef = document.getElementById('pumplab-footer'); if (ef) ef.remove();
      document.documentElement.classList.add('embed');
      return;
    }
    var h = document.getElementById('pumplab-header');
    if (h) h.outerHTML = HEADER;
    try { if (localStorage.getItem('rnd_admin') === '1') {
      var _ao = document.getElementById('adminOut');
      if (_ao) { _ao.style.display = 'block'; _ao.addEventListener('click', function (ev) { ev.preventDefault(); try { localStorage.removeItem('rnd_admin'); } catch (x) {} _ao.style.display = 'none'; }); }
    } } catch (e) {}
    var f = document.getElementById('pumplab-footer');
    if (f) f.outerHTML = FOOTER;
    // 채널톡(Channel Talk) 실시간 상담 위젯 — 우측 하단 (커스텀 CTA_FAB는 중복 방지 위해 미주입)
    if (window.self === window.top && !window.__channelIOBooted) {
      window.__channelIOBooted = true;
      (function(){var w=window;if(w.ChannelIO){return;}var ch=function(){ch.c(arguments);};ch.q=[];ch.c=function(a){ch.q.push(a);};w.ChannelIO=ch;function l(){if(w.ChannelIOInitialized){return;}w.ChannelIOInitialized=true;var s=document.createElement("script");s.type="text/javascript";s.async=true;s.src="https://cdn.channel.io/plugin/ch-plugin-web.js";var x=document.getElementsByTagName("script")[0];if(x.parentNode){x.parentNode.insertBefore(s,x);}}if(document.readyState==="complete"){l();}else{w.addEventListener("DOMContentLoaded",l);w.addEventListener("load",l);}})();
      window.ChannelIO('boot', { pluginKey: '9ef4232c-59bb-4911-a4c7-363c6b5bc513' });
    }
    // 리드플루이드 펌프 보기 — /pump/ 하위 전 페이지 하단 고정 배너(스크롤 따라 진해짐)
    if (window.self === window.top && path.indexOf('/pump/') === 0 && !document.querySelector('.lf-sticky')) {
      var lf = document.createElement('a');
      lf.className = 'lf-sticky';
      lf.href = '/magazine/pump-selection-wizard/';
      lf.innerHTML = '<span class="lf-name">리드플루이드(LeadFluid)</span><span class="lf-go">펌프 보기 →</span>';
      document.body.appendChild(lf);
      document.body.classList.add('has-lfsticky');
      var lfScroll = function () {
        var y = window.scrollY || document.documentElement.scrollTop || 0;
        var a = (0.5 + Math.min(y / 240, 1) * 0.5).toFixed(2);
        lf.style.background = 'rgba(15,42,71,' + a + ')';
      };
      window.addEventListener('scroll', lfScroll, { passive: true });
      lfScroll();
    }
    // 매거진 글 페이지: 우측 '관련 제품' 레일 주입 (article.sd-wrap 페이지 공통)
    var art = document.querySelector('article.sd-wrap');
    if (art && !document.querySelector('.art-rail')) {
      var HEAT_PRODS = [
        { u:'/brands/sh-scientific/muffle-1050/', i:'/img/product/sh/muffle-1050.jpg', n:'ECO 머플로 1050℃', d:'열처리·회화·소성 입문 표준. 프로그램 PID 제어.', d2:'승온 프로그램 · 균일 온도분포 · 국산 정품', p:/*P:muffle1050*/'106만 원~' },
        { u:'/brands/sh-scientific/gas-flow-package/', i:'/img/product/sh/gas-flow-package.jpg', n:'튜브로 가스플로 패키지', d:'석영튜브+가스라인 통합 — CVD·분위기 소성용.', d2:'1200℃ · 불활성/환원 가스 치환 구성', p:/*P:cvdpkg*/'499만 원~' },
        { u:'/brands/sh-scientific/tube-1500/', i:'/img/product/sh/tube-1500.jpg', n:'튜브전기로 1500℃', d:'고온 소성·소결. 균일 항온대 보증.', d2:'세라믹·양극재 고온 공정 · 3존 옵션', p:/*P:tube1500*/'756만 원~' },
        { u:'/brands/sh-scientific/muffle-1500/', i:'/img/product/sh/muffle-1500.jpg', n:'전기로 1500℃', d:'고온 박스로 — 소결·치밀화 공정용.', d2:'4.5~36L 용량 선택 · 프로그램 제어', p:/*P:muffle1500*/'571만 원~' },
        { u:'/brands/sh-scientific/vacuum-muffle-1200/', i:'/img/product/sh/vacuum-muffle-1200.jpg', n:'진공 머플로 1200℃', d:'진공·분위기 겸용 — 산화 민감 소재 열처리.', d2:'감압 열처리 · 진공펌프 연결 구성(별도)', p:/*P:vacmuffle1200*/'934만 원~' },
        { u:'/brands/sh-scientific/rotary-tube-furnace/', i:'/img/product/sh/rotary-tube-furnace.jpg', n:'회전 튜브로 300mm', d:'분말을 굴리며 균일 소성 — 배치 편차 해결.', d2:'배치식 · 가스 분위기 겸용 · 파일럿 전 단계', p:/*P:rotary*/'1,285만 원~' }
      ];
      var FLUID_PRODS = [
        { u:'/magazine/pump-selection-wizard/', i:'/img/leadfluid/official/bt101s-1.jpg', n:'BT101S 연동펌프', d:'정량 공급·공침 표준. RS-485 제어.', d2:'유량 캘리브레이션 · 다양한 펌프헤드 호환', p:/*P:bt101s*/'94만 원~' },
        { u:'/magazine/pump-selection-wizard/', i:'/img/leadfluid/official/bt300s-1.jpg', n:'BT300S 연동펌프', d:'중유량 이송·분주 — 랩 범용.', d2:'분배·타이머 운전 · 정량 분주 모드', p:/*P:bt300s*/'166만 원~' },
        { u:'/magazine/pump-selection-wizard/', i:'/img/leadfluid/official/bt600s-1.jpg', n:'BT600S 연동펌프', d:'대유량 순환·이송. 다채널 헤드 확장.', d2:'반응기 순환·스케일업 · 멀티채널 구성', p:/*P:bt600s*/'212만 원~' },
        { u:'/magazine/pump-selection-wizard/', i:'/img/leadfluid/official/ct3001f-1.jpg', n:'CT3001F 기어펌프', d:'무맥동 연속 이송 — PEEK 내화학 헤드.', d2:'전해액·유기용매 순환 · 논문 검증 모델', p:/*P:ct3001*/'224만 원~' },
        { u:'/magazine/pump-selection-wizard/', i:'/img/leadfluid/official/tyd01-01-1.jpg', n:'TYD01 시린지펌프', d:'미량 정밀 주입·전해액 정량.', d2:'저맥동 정밀 주입 · 시린지 규격 대응', p:/*P:tyd01*/'232만 원~' },
        { u:'/brands/alicat/', i:'/img/product/%EC%95%8C%EB%A6%AC%EC%BA%A3%20%EC%A0%9C%ED%92%88.jpg', n:'Alicat 질량유량계(MFC)', d:'가스 유량 sccm 정밀 제어·기록.', d2:'다기체 대응 · Modbus·RS-485 로그', p:'견적 문의' }
      ];
      var ECHEM_PRODS = [
        { u:'/brands/hefei/om003-microscope-cell/', i:'/img/hefei/hefei-cis-om-003.jpg', n:'CIS-OM-003 인시츄 관찰 셀', d:'석영창 0.05 mm — 리튬 덴드라이트 광학 관찰 표준.', d2:'별도 주액 피팅 · 가압 전고체 모듈 옵션', p:'500만 원~' },
        { u:'/brands/gaossunion/special-cell-dendrite/', i:'/img/gaossunion/spcell-1.jpg', n:'C031-5 덴드라이트 관찰 셀', d:'코인셀 모사 — 사파이어 창 2종 구성.', d2:'가오스유니온 · 인시츄 광학 관찰', p:'253만 원~' },
        { u:'/brands/gaossunion/agcl-reference-electrode/', i:'/img/gaossunion/agcl-reference-electrode-1.jpg', n:'Ag/AgCl 기준전극', d:'염화은 단염교 — 전기화학 측정 기본.', d2:'유리 Φ3.8/6.0 · PCTFE · PEEK', p:'10만 원~' }
      ];
      var crumb = art.querySelector('.sd-crumb');
      var ct = crumb ? (crumb.textContent || '') : '';
      var isEchem = /인시츄|전기화학|덴드라이트|전극/.test(ct);
      var isFluid = /유체|펌프/.test(ct);
      var prods = isEchem ? ECHEM_PRODS : (isFluid ? FLUID_PRODS : HEAT_PRODS);
      var layout = document.createElement('div');
      layout.className = 'art-layout';
      art.parentNode.insertBefore(layout, art);
      layout.appendChild(art);
      var rail = document.createElement('aside');
      rail.className = 'art-rail';
      rail.setAttribute('aria-label', '관련 제품');
      rail.innerHTML = '<div class="ar-h">이 셋업에 쓰는 장비</div>' +
        prods.slice(0, 3).map(function (p) {
          return '<a class="ar-card" href="' + p.u + '">' +
            '<span class="ai" style="background-image:url(\'' + p.i + '\')"></span>' +
            '<span class="ab"><span class="an">' + p.n + '</span>' +
            '<span class="ad" style="display:block">' + p.d + '</span>' +
            '<span class="ad2" style="display:block">' + (p.d2 || '') + '</span>' +
            '<span class="ap">' + p.p + '<span class="ag">사양 보기 →</span></span></span></a>';
        }).join('') +
        '<button type="button" class="ar-order" id="arOrderBtn">' +
          '<span class="ao-ic">🛒</span>' +
          '<span class="ao-bd"><span class="ao-t">셋업 구성에 필요한 부품 주문하기</span>' +
          '<span class="ao-d">필요한 장비를 골라 견적 문의 — 매거진 독자 할인가</span></span>' +
          '<span class="ao-go">＋</span>' +
        '</button>';
      layout.appendChild(rail);

      // 부품 주문 팝업 — 장비 체크리스트 + 연락처 → Formspree
      var ORDER_EP = 'https://formspree.io/f/mnjkzppj';
      var om = document.createElement('div');
      om.className = 'ao-back';
      om.innerHTML = '<div class="ao-modal">' +
        '<button type="button" class="ao-x" aria-label="닫기">&times;</button>' +
        '<form id="aoForm">' +
        '<h3>셋업 구성 부품·장비 주문 문의</h3>' +
        '<p class="ao-sub">필요한 장비를 선택하고 연락처를 남기면, 구성·견적(독자 할인가)으로 회신드립니다.</p>' +
        '<div class="ao-list">' +
        prods.map(function (p) {
          return '<label class="ao-item"><input type="checkbox" name="장비" value="' + p.n + ' (' + p.p + ')">' +
            '<span class="ao-nm">' + p.n + '</span><span class="ao-pp">' + p.p + '</span></label>';
        }).join('') +
        '</div>' +
        '<label class="ao-lb">기타 필요한 부품·구성 (선택)</label>' +
        '<textarea name="기타요청" placeholder="예: 석영튜브 여분, 튜브 피팅, MFC 2채널, 진공펌프 포함 여부 등"></textarea>' +
        '<div class="ao-g2">' +
        '<div><label class="ao-lb">이름 <b>*</b></label><input type="text" name="이름" required placeholder="홍길동"></div>' +
        '<div><label class="ao-lb">소속 <b>*</b></label><input type="text" name="소속" required placeholder="OO대학교 OO연구실"></div>' +
        '</div>' +
        '<label class="ao-lb">이메일 <b>*</b></label>' +
        '<input type="email" name="이메일" required placeholder="you@lab.ac.kr">' +
        '<input type="hidden" name="_subject" value="[셋업 부품 주문] 장비 선택 문의">' +
        '<input type="hidden" name="문의유형" value="셋업 부품·장비 주문">' +
        '<input type="hidden" name="출처페이지" value="' + location.pathname + '">' +
        '<button type="submit" class="ao-send">선택한 장비로 문의 보내기 →</button>' +
        '<p class="ao-err" id="aoErr"></p>' +
        '</form>' +
        '<div class="ao-done" id="aoDone"><h3>문의가 접수되었습니다</h3><p>선택하신 장비 구성을 검토해 견적으로 회신드립니다.<br>급하시면 <b>info@rndsetup.com</b> · <b>070-8983-2600</b></p></div>' +
        '</div>';
      document.body.appendChild(om);
      function aoOpen() { om.classList.add('on'); document.body.style.overflow = 'hidden'; }
      function aoClose() { om.classList.remove('on'); document.body.style.overflow = ''; }
      document.getElementById('arOrderBtn').addEventListener('click', aoOpen);
      om.querySelector('.ao-x').addEventListener('click', aoClose);
      om.addEventListener('click', function (e) { if (e.target === om) aoClose(); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && om.classList.contains('on')) aoClose(); });
      var aoForm = om.querySelector('#aoForm');
      aoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var err = om.querySelector('#aoErr');
        var checked = aoForm.querySelectorAll('input[name="장비"]:checked');
        var extra = (aoForm.querySelector('[name="기타요청"]').value || '').trim();
        if (!checked.length && !extra) {
          err.textContent = '장비를 하나 이상 선택하거나, 기타 요청을 적어주세요.';
          err.classList.add('on');
          return;
        }
        err.classList.remove('on');
        var btn = aoForm.querySelector('.ao-send'), txt = btn.textContent;
        btn.disabled = true; btn.textContent = '보내는 중…';
        fetch(ORDER_EP, { method: 'POST', body: new FormData(aoForm), headers: { Accept: 'application/json' } })
          .then(function (r) {
            if (!r.ok) throw new Error('bad');
            if (typeof window.gtag === 'function') {
              gtag('event', 'generate_lead', { lead_type: 'setup_parts_order', page_path: location.pathname });
            }
            aoForm.style.display = 'none';
            om.querySelector('#aoDone').style.display = 'block';
          })
          .catch(function () {
            btn.disabled = false; btn.textContent = txt;
            err.textContent = '전송에 실패했습니다. info@rndsetup.com 으로 보내주세요.';
            err.classList.add('on');
          });
      });

      // 좌측 목차 가이드 — 본문 h2를 수집해 스크롤 스파이 목차 생성
      var heads = Array.prototype.slice.call(art.querySelectorAll('h2'));
      if (heads.length >= 2) {
        var toc = document.createElement('nav');
        toc.className = 'art-toc';
        toc.setAttribute('aria-label', '목차');
        var links = heads.map(function (h, i) {
          if (!h.id) h.id = 'sec-' + (i + 1);
          h.style.scrollMarginTop = '120px';
          return '<a href="#' + h.id + '">' + (h.textContent || '').trim() + '</a>';
        }).join('');
        toc.innerHTML = '<div class="at-h">이 글의 목차</div>' + links;
        layout.insertBefore(toc, art);
        var tocLinks = toc.querySelectorAll('a');
        var spyTick = false;
        function spy() {
          if (spyTick) return; spyTick = true;
          requestAnimationFrame(function () {
            var mid = 140, cur = 0;
            heads.forEach(function (h, i) {
              if (h.getBoundingClientRect().top <= mid) cur = i;
            });
            tocLinks.forEach(function (a, i) { a.classList.toggle('on', i === cur); });
            spyTick = false;
          });
        }
        window.addEventListener('scroll', spy, { passive: true });
        spy();
      }
    }

    // 스크롤다운 시 상단바 접기 — 메뉴바만 반투명하게 남김 (데스크톱, CSS가 처리)
    var hdrTick = false;
    function hdrOnScroll() {
      if (hdrTick) return; hdrTick = true;
      requestAnimationFrame(function () {
        var y = window.scrollY || document.documentElement.scrollTop || 0;
        document.body.classList.toggle('hdr-collapsed', y > 90);
        hdrTick = false;
      });
    }
    window.addEventListener('scroll', hdrOnScroll, { passive: true });
    hdrOnScroll();

    var burger = document.querySelector('.ch-burger');
    var side = document.getElementById('chSide');
    var scrim = document.getElementById('chScrim');
    if (burger && side) {
      function closeSide() { side.classList.remove('open'); if (scrim) scrim.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
      burger.addEventListener('click', function () {
        var open = side.classList.toggle('open');
        if (scrim) scrim.classList.toggle('open', open);
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      if (scrim) scrim.addEventListener('click', closeSide);
      side.addEventListener('click', function (e) { if (e.target.closest('a')) closeSide(); });
    }
    // 검색창 자동완성 — 연관검색어(매칭 카드 수) 실시간 제안 (헤더·홈 히어로 공용)
    function attachSuggest(mf) {
      if (!mf) return;
      var minp = mf.querySelector('input[name="q"]');
      if (!minp) return;
      var box = document.createElement('div');
      box.className = 'ch-sug';
      mf.appendChild(box);
      var TERMS = null, loading = false;
      function load(cb) {
        if (TERMS) { cb(); return; }
        if (loading) return;
        loading = true;
        fetch('/assets/search-terms.json').then(function (r) { return r.json(); })
          .then(function (d) { TERMS = d; cb(); }).catch(function () { loading = false; });
      }
      function hide() { box.classList.remove('on'); box.innerHTML = ''; }
      function show() {
        var v = (minp.value || '').trim().toLowerCase();
        if (!v) { hide(); return; }
        load(function () {
          var starts = [], has = [];
          for (var i = 0; i < TERMS.length; i++) {
            var tl = TERMS[i][0].toLowerCase();
            if (tl === v) continue;
            if (tl.indexOf(v) === 0) { starts.push(TERMS[i]); continue; }
            if (tl.indexOf(v) > -1) { has.push(TERMS[i]); continue; }
            var al = TERMS[i][2] || [], hit = false, first = false;
            for (var a = 0; a < al.length; a++) {
              var av = al[a].toLowerCase();
              if (av.indexOf(v) === 0) { first = true; break; }
              if (av.indexOf(v) > -1) hit = true;
            }
            if (first) starts.push(TERMS[i]);
            else if (hit) has.push(TERMS[i]);
          }
          var list = starts.concat(has).slice(0, 8);
          if (!list.length) { hide(); return; }
          box.innerHTML = '';
          list.forEach(function (t) {
            var b = document.createElement('button');
            b.type = 'button';
            var s1 = document.createElement('span'); s1.textContent = t[0];
            var s2 = document.createElement('span'); s2.className = 'n'; s2.textContent = t[1] + '개';
            b.appendChild(s1); b.appendChild(s2);
            b.addEventListener('mousedown', function (e) {
              e.preventDefault();
              location.href = '/product/?q=' + encodeURIComponent(t[0]);
            });
            box.appendChild(b);
          });
          box.classList.add('on');
        });
      }
      if (window.innerWidth <= 640 && mf.classList.contains('ch-msearch')) { minp.placeholder = '제품명·모델명 검색'; }
      minp.addEventListener('input', show);
      minp.addEventListener('focus', show);
      minp.addEventListener('blur', function () { setTimeout(hide, 150); });
      minp.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
    }
    attachSuggest(document.querySelector('.ch-msearch'));
    attachSuggest(document.querySelector('.hero-search'));

    // 로그인 계정 메뉴 — 로그인 시 사람 아이콘이 계정 드롭다운으로 전환
    (function () {
      var ic = document.querySelector('.ch-top .ch-ic[href="/login/"]');
      if (!ic || !window.fetch) return;
      fetch('/api/auth/me', { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (d) {
        if (!d || !d.login) return;
        var cu = d.customer || {};
        var name = (cu.name || '고객') + ' 님';
        var email = cu.email || cu.work_email || '';
        var initial = (cu.name || 'C').charAt(0);
        var p = document.createElement('div');
        p.className = 'ch-acct';
        p.innerHTML =
          '<div class="ah"><div class="av"></div><div><div class="an"></div><div class="ae"></div></div></div>' +
          '<ul>' +
          '<li><a href="/member/#orders"><span class="i">&#128203;</span>주문내역</a></li>' +
          '<li><a href="/member/#new"><span class="i">&#128722;</span>주문하기</a></li>' +
          '<li><a href="/member/#settle"><span class="i">&#128179;</span>정산 내역</a></li>' +
          '<li class="sep"></li>' +
          '<li><a href="/member/#me"><span class="i">&#9881;&#65039;</span>프로필 설정</a></li>' +
          '<li><a href="#logout" class="out"><span class="i">&#10162;</span>로그아웃</a></li>' +
          '</ul>';
        p.querySelector('.av').textContent = initial;
        p.querySelector('.an').textContent = name;
        p.querySelector('.ae').textContent = email;
        document.body.appendChild(p);
        ic.setAttribute('href', '#account');
        ic.setAttribute('title', name);
        ic.addEventListener('click', function (e) {
          e.preventDefault();
          p.classList.toggle('on');
          ic.classList.toggle('acct-on', p.classList.contains('on'));
        });
        document.addEventListener('click', function (e) {
          if (e.target.closest('.ch-acct') || e.target.closest('.ch-ic[href="#account"]')) return;
          p.classList.remove('on'); ic.classList.remove('acct-on');
        });
        p.querySelector('a.out').addEventListener('click', function (e) {
          e.preventDefault();
          fetch('/api/auth/me', { method: 'DELETE', credentials: 'same-origin' })
            .then(function () { location.href = '/'; })
            .catch(function () { location.href = '/'; });
        });
      }).catch(function () {});
    })();

    // 문의하기 = 대화창 열기 (채널톡 → 자체 패널 → /contact/ 폴백)
    window.chatOpen = function () {
      try { if (window.ChannelIO) { window.ChannelIO('showMessenger'); return false; } } catch (e) {}
      var c = document.getElementById('ctaChat');
      if (c) { c.classList.add('open'); return false; }
      location.href = '/contact/';
      return false;
    };
    // 헤더 장바구니 배지 — 주문 페이지와 같은 rs_cart 를 읽는다
    window.cartCount = function () {
      try { return (JSON.parse(localStorage.getItem('rs_cart') || '[]') || []).length; } catch (e) { return 0; }
    };
    window.paintCart = function () {
      var n = window.cartCount();
      document.querySelectorAll('.ch-cart .ch-cnt').forEach(function (el) {
        el.textContent = n > 99 ? '99+' : String(n);
        el.hidden = !n;
      });
    };
    window.paintCart();
    window.addEventListener('storage', function (e) { if (e.key === 'rs_cart') window.paintCart(); });

    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href="#chat"], a[href$="#chat"]');
      if (a) { e.preventDefault(); window.chatOpen(); }
    });

    var sf = document.getElementById('chSearch');
    var rbox = document.getElementById('chResults');
    if (sf && rbox) {
      loadSearchIndex();
      var inp = sf.querySelector('input');
      function esc(s){ return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
      function doSearch() {
        var q = (inp.value || '').trim().toLowerCase();
        if (!q) { rbox.classList.remove('open'); rbox.innerHTML = ''; return; }
        var terms = q.split(/\s+/).filter(Boolean);
        var hits = SEARCH_INDEX.filter(function (it) {
          var hay = (it.t + ' ' + (it.k || '') + ' ' + (it.c || '')).toLowerCase();
          return terms.every(function (tm) { return hay.indexOf(tm) > -1; });
        });
        // 제목 일치 우선 정렬
        hits.sort(function (a, b) {
          var at = terms.every(function (tm) { return a.t.toLowerCase().indexOf(tm) > -1; }) ? 0 : 1;
          var bt = terms.every(function (tm) { return b.t.toLowerCase().indexOf(tm) > -1; }) ? 0 : 1;
          return at - bt;
        });
        hits = hits.slice(0, 10);
        if (!hits.length) {
          rbox.innerHTML = '<div class="rempty">"' + esc(inp.value.trim()) + '" 검색 결과가 없습니다.</div>';
        } else {
          rbox.innerHTML = hits.map(function (it) {
            return '<a href="' + it.u + '"><div class="rc">' + esc(it.c || '') + '</div><div class="rt">' + esc(it.t) + '</div></a>';
          }).join('');
        }
        rbox.classList.add('open');
      }
      inp.addEventListener('input', doSearch);
      inp.addEventListener('focus', function () { if (inp.value.trim()) doSearch(); });
      sf.addEventListener('submit', function (e) {
        e.preventDefault();
        var first = rbox.querySelector('a');
        if (first) location.href = first.getAttribute('href');
      });
      document.addEventListener('click', function (e) { if (!sf.contains(e.target)) rbox.classList.remove('open'); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();

/* 구조화 데이터(Organization/WebSite/BreadcrumbList)는 build.py inject_head_schema()가
   각 페이지 <head>에 정적 주입한다(크롤러 가시화). JS 주입은 GEO상 크롤러 미가시라 제거함. */

/* ============================================================
   GA4 + 클릭 추적 — 전 페이지 공통 (무엇을 눌렀는지 측정)
   ============================================================ */
(function () {
  var GA_ID = 'G-QPK55EPDVM';

  // 이미 gtag가 있는 페이지(recommend·inquiry·블로그 등)는 중복 로드 방지
  if (typeof window.gtag !== 'function') {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', GA_ID);
  }

  // 버튼·링크 클릭을 'click' 이벤트로 전송 (link_text = 누른 텍스트)
  document.addEventListener('click', function (e) {
    var el = (e.target && e.target.closest) ? e.target.closest('a, button, [data-ga]') : null;
    if (!el || typeof window.gtag !== 'function') return;
    var label = (el.getAttribute('data-ga') || el.textContent || el.getAttribute('aria-label') || '')
      .replace(/\s+/g, ' ').trim().slice(0, 90);
    if (!label) return;
    gtag('event', 'click', {
      link_text: label,
      link_url: el.getAttribute('href') || '',
      page_path: location.pathname
    });
  }, true);

  // 전환(주요 이벤트) — 프로그램 다운로드
  document.addEventListener('click', function (e) {
    var a = (e.target && e.target.closest) ? e.target.closest('a') : null;
    if (!a || typeof window.gtag !== 'function') return;
    var href = a.getAttribute('href') || '';
    if (a.hasAttribute('download') || /\.(exe|zip|msi)(\?|#|$)/i.test(href)) {
      gtag('event', 'file_download', {
        file_name: (href.split('/').pop() || (a.textContent || '').trim()).slice(0, 60),
        link_url: href,
        page_path: location.pathname
      });
    }
  }, true);

  // 전환(주요 이벤트) — 문의·개발요청 폼 제출
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.tagName !== 'FORM' || typeof window.gtag !== 'function') return;
    var act = f.getAttribute('action') || '';
    if (/formspree\.io/i.test(act) || /\/(inquiry|requests)\//.test(location.pathname)) {
      gtag('event', 'generate_lead', {
        form_action: act,
        page_path: location.pathname
      });
    }
  }, true);

  // 전환 후보 — 나비엠알오(구매 채널) 클릭
  document.addEventListener('click', function (e) {
    var a = (e.target && e.target.closest) ? e.target.closest('a') : null;
    if (!a || typeof window.gtag !== 'function') return;
    if (/navimro\.com/i.test(a.getAttribute('href') || '')) {
      gtag('event', 'navimro_click', {
        link_text: (a.getAttribute('data-ga') || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60),
        page_path: location.pathname
      });
    }
  }, true);
})();

/* =========================================================================
   견적 문의 모달 (Quote Modal)
   -------------------------------------------------------------------------
   쓰는 법 — 페이지에 버튼만 하나 두면 된다.
     <button type="button" class="qbtn" data-quote="1200℃ 튜브 전기로 Gas Flow Package · 300mm">
       견적 문의
     </button>
   data-quote 값이 메일의 "문의제품" 필드로 그대로 들어간다.
   버튼이 없는 페이지에서는 아무것도 실행되지 않는다.
   전송은 기존 삼흥 견적폼과 같은 Formspree 엔드포인트를 쓴다.
   ========================================================================= */
(function () {
  var ENDPOINT = 'https://formspree.io/f/mnjkzppj';
  if (!document.querySelector('[data-quote]')) return;

  var CSS = ''
    + '.qbtn{display:inline-block;font-family:inherit;font-size:14px;font-weight:800;color:#fff;'
    + 'background:#3B3695;border:0;padding:12px 22px;border-radius:10px;cursor:pointer;line-height:1.2}'
    + '.qbtn:hover{background:#2A2570}'
    + '.qm-back{position:fixed;inset:0;background:rgba(20,18,16,.55);display:none;align-items:center;'
    + 'justify-content:center;z-index:9000;padding:20px}'
    + '.qm-back.on{display:flex}'
    + '.qm{background:#fff;border-radius:16px;max-width:520px;width:100%;max-height:88vh;overflow:auto;'
    + 'padding:26px 26px 24px;position:relative;box-shadow:0 20px 60px rgba(0,0,0,.28)}'
    + '.qm h2{font-family:var(--serif,Georgia);font-size:20px;font-weight:700;margin:0 0 6px;color:#1A1A1A}'
    + '.qm .qm-sub{font-size:13.5px;color:#6B6B6B;line-height:1.65;margin:0 0 16px}'
    + '.qm .qm-for{font-size:12.5px;font-weight:700;color:#0F69AF;background:#EAF4FB;border-radius:8px;'
    + 'padding:8px 12px;margin:0 0 16px;line-height:1.5}'
    + '.qm label{display:block;font-size:12.5px;font-weight:700;color:#3a3a3a;margin:12px 0 5px}'
    + '.qm label .req{color:#0F69AF}'
    + '.qm input,.qm textarea{width:100%;border:1px solid #E0DCD7;border-radius:9px;padding:10px 12px;'
    + 'font-size:14px;font-family:inherit;line-height:1.55;background:#fff;color:#1A1A1A}'
    + '.qm textarea{min-height:74px;resize:vertical}'
    + '.qm input:focus,.qm textarea:focus{outline:0;border-color:#3B3695}'
    + '.qm .qm-body select{width:100%;font-family:inherit;font-size:14px;padding:11px 12px;border:1px solid #E7E3DE;border-radius:9px;background:#fff;margin-bottom:4px}.qm-fx{font-size:11.5px;color:#9C958D;margin-top:4px;line-height:1.5}'
    + '.qm .qm-g2{display:grid;grid-template-columns:1fr 1fr;gap:10px}'
    + '.qm .qm-send{width:100%;margin-top:18px;font-size:15px;font-weight:800;color:#fff;background:#3B3695;'
    + 'border:0;padding:13px;border-radius:10px;cursor:pointer;font-family:inherit}'
    + '.qm .qm-send:hover{background:#2A2570}'
    + '.qm .qm-send:disabled{opacity:.55;cursor:default}'
    + '.qm .qm-x{position:absolute;right:14px;top:12px;border:0;background:transparent;font-size:24px;'
    + 'line-height:1;color:#9C958D;cursor:pointer;padding:4px 8px;font-family:inherit}'
    + '.qm .qm-x:hover{color:#1A1A1A}'
    + '.qm .qm-err{display:none;font-size:13px;color:#B4453A;margin-top:10px;line-height:1.6}'
    + '.qm .qm-err.on{display:block}'
    + '.qm .qm-priv{font-size:11.5px;color:#9C958D;margin-top:12px;line-height:1.6}'
    + '.qm-done{display:none;text-align:center;padding:14px 0 6px}'
    + '.qm-done.on{display:block}'
    + '.qm-done h2{margin-bottom:8px}'
    + '.qm-done p{font-size:14px;color:#6B6B6B;line-height:1.7}'
    + '@media(max-width:520px){.qm .qm-g2{grid-template-columns:1fr}}';

  var st = document.createElement('style');
  st.textContent = CSS;
  document.head.appendChild(st);

  var back = document.createElement('div');
  back.className = 'qm-back';
  back.setAttribute('role', 'dialog');
  back.setAttribute('aria-modal', 'true');
  back.setAttribute('aria-label', '견적 문의');
  back.innerHTML = ''
    + '<div class="qm">'
    +   '<button type="button" class="qm-x" aria-label="닫기">&times;</button>'
    +   '<form id="qmForm" novalidate>'
    +     '<h2 id="qmTitle">견적 문의</h2>'
    +     '<p class="qm-sub" id="qmSub">구성에 따라 사양·금액이 달라집니다. <b>다루는 시료와 공정</b>만 남겨주시면, 맞는 구성과 견적으로 회신드립니다.</p>'
    +     '<p class="qm-for" id="qmFor"></p>'
    +     '<div id="qmFurn">'+ '<label>샘플 시료 <span class="req">*</span></label>'+ '<textarea name="샘플시료" placeholder="재질 · 형태 · 양 (예: 알루미나 분말 50g / 실리콘 웨이퍼 2인치 5장)"></textarea>'+ '<div class="qm-fx">무엇을 넣고 처리하는지 — 재질, 형태(분말·벌크·박막), 대략의 양</div>'+ '<label>사용 공정 <span class="req">*</span></label>'+ '<textarea name="사용공정" placeholder="목표 온도 · 분위기 · 승온/유지 조건 (예: Ar 분위기 900℃까지 5℃/min 승온 후 2시간 유지)"></textarea>'+ '<div class="qm-fx">목표 온도 · 분위기(대기/불활성/진공) · 승온·유지 조건 · 처리 목적</div>'+ '</div>'+ '<div id="qmPump" style="display:none">'+ '<label><span id="qmHeadLabel">구성 (펌프헤드) </span><span class="req">*</span></label>'+ '<select name="구성헤드" id="qmHead"><option value="">선택해 주세요</option></select>'+ '<div class="qm-fx" id="qmHeadFx">헤드에 따라 유량 범위·채널 수·가격이 달라집니다. 모르시면 <b>추천 요청</b>을 선택하세요.</div>'+ '<label>목표 유량 <span class="req">*</span></label>'+ '<input type="text" name="목표유량" placeholder="예: 50 mL/min 연속 / 200 μL 정량 분주">'+ '<div class="qm-fx">필요한 유량과 운전 방식(연속 이송 · 정량 분주 · 순환)</div>'+ '<label>현재 사용 중인 펌프 <span style="font-weight:600;color:#9C958D">(있으면)</span></label>'+ '<input type="text" name="기존펌프" placeholder="예: Masterflex L/S 07528-10 / 리드플루이드 BT100S">'+ '<div class="qm-fx">교체·증설이면 기존 모델명을 알려주시면 호환 구성으로 잡아드립니다.</div>'+ '<label>요청사항</label>'+ '<textarea name="요청사항" placeholder="유체 종류(점도·부식성) · 채널 수 · 통신 연동 · 납기 등 알려주실 내용"></textarea>'+ '</div>'
    + '<div id="qmProdBox" style="display:none">'+ '<label>모델 · 옵션</label>'+ '<input type="text" name="모델옵션" id="qmModel" readonly>'+ '<label>수량</label>'+ '<input type="number" name="수량" id="qmQty" min="1" value="1">'+ '<label>문의 내용 <span class="req">*</span></label>'+ '<textarea name="문의내용" id="qmMsg" placeholder="규격·수량·납기 등 궁금하신 점을 적어주세요"></textarea>'+ '</div>'
    +     '<div class="qm-g2">'
    +       '<div><label>이름 <span class="req">*</span></label>'
    +         '<input type="text" name="이름" required placeholder="홍길동"></div>'
    +       '<div><label>소속 <span class="req">*</span></label>'
    +         '<input type="text" name="소속" required placeholder="OO대학교 OO연구실"></div>'
    +     '</div>'
    +     '<label>이메일 <span class="req">*</span></label>'
    +     '<input type="email" name="이메일" required placeholder="you@lab.ac.kr">'
    +     '<input type="hidden" name="문의유형" id="qmType" value="삼흥 열처리 견적(카탈로그)">'
    +     '<input type="hidden" name="문의제품" id="qmProd" value="">'
    +     '<input type="hidden" name="출처페이지" id="qmPath" value="">'
    +     '<button type="submit" class="qm-send" id="qmSend">견적 요청 보내기 →</button>'
    +     '<p class="qm-err" id="qmErr"></p>'
    +     ''
    +   '</form>'
    +   '<div class="qm-done" id="qmDone">'
    +     '<h2>문의가 접수되었습니다</h2>'
    +     '<p id="qmDoneMsg">보내주신 조건을 검토해 회신드립니다.</p>'
    +   '</div>'
    + '</div>';
  document.body.appendChild(back);

  var form = back.querySelector('#qmForm');
  var done = back.querySelector('#qmDone');
  var errEl = back.querySelector('#qmErr');
  var lastFocus = null;

  function open(product, opts) {
    lastFocus = document.activeElement;
    opts = opts || {};
    back.querySelector('#qmProd').value = product || '';

    /* ── 제품문의 모드 (전기화학 등 개별 제품 페이지) ── */
    var isProd = !!opts.productMode;
    back.querySelector('#qmProdBox').style.display = isProd ? '' : 'none';
    back.querySelector('#qmTitle').textContent = isProd ? '제품문의' : '견적 문의';
    back.querySelector('#qmSend').textContent  = isProd ? '문의 보내기 →' : '견적 요청 보내기 →';
    back.querySelector('#qmSub').innerHTML = isProd
      ? '모델·수량과 궁금하신 점을 남겨주시면 확인해 회신드립니다.'
      : '구성에 따라 사양·금액이 달라집니다. <b>다루는 시료와 공정</b>만 남겨주시면, 맞는 구성과 견적으로 회신드립니다.';
    back.querySelector('#qmDoneMsg').textContent = isProd
      ? '문의 내용을 확인해 회신드립니다.'
      : '보내주신 조건을 검토해 회신드립니다.';
    if (isProd) {
      back.querySelector('#qmFurn').style.display = 'none';
      back.querySelector('#qmPump').style.display = 'none';
      back.querySelector('#qmModel').value = opts.model || '';
      back.querySelector('#qmQty').value   = opts.qty || 1;
      back.querySelector('#qmType').value  = '제품문의';
      var forEl = back.querySelector('#qmFor');
      if (forEl) forEl.textContent = product || '';
      back.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      var f0 = back.querySelector('#qmMsg'); if (f0) setTimeout(function(){ f0.focus(); }, 30);
      return;
    }

    var isPump = /leadfluid|리드플루이드|BT\d|WT\d|WG\d|MF\d|MS\d|BQ\d|JP\d|TYD|TFD|TSD|TGD|CT300|EF\d|FG\d|FP\d|AF9|G3030|G6060|MC10|MM10|\ud38c\ud504\ud5e4\ub4dc/i.test((product||'') + ' ' + location.pathname);
    back.querySelector('#qmFurn').style.display = isPump ? 'none' : '';
    back.querySelector('#qmPump').style.display = isPump ? '' : 'none';
    back.querySelector('#qmType').value = isPump ? '리드플루이드 펌프 견적' : '삼흥 열처리 견적(카탈로그)';
    if (isPump) {
      var isSyr = /TYD|TFD|TSD|TGD|G3030|G6060|시린지/i.test((product || '') + ' ' + location.pathname);
      var sel = back.querySelector('#qmHead');
      var lab = back.querySelector('#qmHeadLabel');
      var fx  = back.querySelector('#qmHeadFx');
      var heads = [];
      document.querySelectorAll('.price-tbl tbody tr').forEach(function (tr) {
        var td = tr.querySelector('th[scope="row"], td');
        var t2 = td ? (td.textContent || '').replace(/\s+/g, ' ').trim() : '';
        if (t2 && t2 !== '—' && !/^\d+$/.test(t2) && heads.indexOf(t2) < 0 && heads.length < 40) heads.push(t2);
      });
      if (isSyr) {
        if (lab) lab.textContent = '시린지 규격 ';
        if (fx) fx.innerHTML = '사용할 시린지 용량을 알려주세요. 모르시면 <b>추천 요청</b>을 선택하세요.';
        heads = ['10 μL','50 μL','100 μL','500 μL','1 mL','5 mL','10 mL','20 mL','50 mL','60 mL','140 mL'];
      } else {
        if (lab) lab.textContent = '구성 (펌프헤드) ';
        if (fx) fx.innerHTML = '헤드에 따라 유량 범위·채널 수·가격이 달라집니다. 모르시면 <b>추천 요청</b>을 선택하세요.';
      }
      sel.innerHTML = '<option value="">선택해 주세요</option>' +
        heads.map(function (x) { return '<option>' + x + '</option>'; }).join('') +
        '<option value="추천 요청">잘 모르겠음 — 추천 요청</option>';
    }
    back.querySelector('#qmPath').value = location.pathname;
    var forEl = back.querySelector('#qmFor');
    if (product) { forEl.textContent = '문의 제품 · ' + product; forEl.style.display = ''; }
    else { forEl.style.display = 'none'; }
    form.style.display = '';
    done.classList.remove('on');
    errEl.classList.remove('on');
    back.classList.add('on');
    document.body.style.overflow = 'hidden';
    var t = form.querySelector('textarea');
    if (t) setTimeout(function () { t.focus(); }, 30);
    if (typeof window.gtag === 'function') {
      gtag('event', 'quote_modal_open', { product: product || '', page_path: location.pathname });
    }
  }

  function close() {
    back.classList.remove('on');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    var pb = (e.target && e.target.closest) ? e.target.closest('[data-inquiry]') : null;
    if (pb) {
      e.preventDefault();
      var box = document.getElementById('buybox');
      var mSel = document.getElementById('pdModel');
      var qEl  = document.getElementById('pdQty');
      open(pb.getAttribute('data-inquiry'), {
        productMode: true,
        model: mSel ? (mSel.options[mSel.selectedIndex] || {}).text || '' : '',
        qty:   qEl ? (qEl.value || 1) : 1
      });
      return;
    }
    var b = (e.target && e.target.closest) ? e.target.closest('[data-quote]') : null;
    if (b) { e.preventDefault(); open(b.getAttribute('data-quote')); }
  });
  back.querySelector('.qm-x').addEventListener('click', close);
  back.addEventListener('click', function (e) { if (e.target === back) close(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && back.classList.contains('on')) close();
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    errEl.classList.remove('on');
    var missing = [];
    (back.querySelector('#qmPump').style.display !== 'none' ? ['구성헤드','목표유량','이름','소속','이메일'] : ['샘플시료','사용공정','이름','소속','이메일']).forEach(function (n) {
      var f = form.querySelector('[name="' + n + '"]');
      if (f && !f.value.trim()) missing.push(n);
    });
    var mail = form.querySelector('[name="이메일"]');
    if (!missing.length && mail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail.value.trim())) {
      missing.push('이메일 형식');
    }
    if (missing.length) {
      errEl.textContent = '다음 항목을 확인해 주세요 — ' + missing.join(' · ');
      errEl.classList.add('on');
      return;
    }
    var btn = form.querySelector('.qm-send'), txt = btn.textContent;
    btn.disabled = true; btn.textContent = '보내는 중…';
    fetch(ENDPOINT, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error('bad');
        if (typeof window.gtag === 'function') {
          gtag('event', 'generate_lead', {
            lead_type: 'sh_catalog_quote',
            product: form.querySelector('#qmProd').value,
            page_path: location.pathname
          });
        }
        form.style.display = 'none';
        done.classList.add('on');
      })
      .catch(function () {
        btn.disabled = false; btn.textContent = txt;
        errEl.textContent = '전송에 실패했습니다. info@rndsetup.com 로 보내주시면 바로 회신드리겠습니다.';
        errEl.classList.add('on');
      });
  });
})();


/* 구성 선택 → 견적문의 (.cfgq) — 모델 필수, 옵션 선택, 미선택 시 안내 */
(function () {
  function init() {
    var boxes = document.querySelectorAll('.cfgq');
    if (!boxes.length) return;
    Array.prototype.forEach.call(boxes, function (box) {
      var btn = box.querySelector('.cfgq-btn');
      var msg = box.querySelector('.cfgq-msg');
      if (!btn) return;
      btn.addEventListener('click', function () {
        var radios = box.querySelectorAll('input[type="radio"]');
        var m = box.querySelector('input[type="radio"]:checked');
        var opts = Array.prototype.map.call(
          box.querySelectorAll('input[type="checkbox"]:checked'),
          function (c) { return c.value; });
        if (radios.length && !m) {
          if (msg) { msg.textContent = '구성을 체크하세요 — 먼저 모델을 선택해 주세요.'; msg.classList.add('on'); }
          var g = box.querySelector('.cfgq-grp');
          if (g && g.scrollIntoView) g.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }
        if (msg) { msg.textContent = ''; msg.classList.remove('on'); }
        var product = box.getAttribute('data-product') || '';
        var cfg = product + (m ? ' / 선택 모델: ' + m.value : '') + (opts.length ? ' / 옵션: ' + opts.join(', ') : ' / 옵션: 없음');
        var tmp = document.createElement('button');
        tmp.setAttribute('data-quote', cfg);
        tmp.style.display = 'none';
        document.body.appendChild(tmp);
        tmp.click();
        document.body.removeChild(tmp);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

/* ===========================================================
   제품 상세 — 모델 드롭다운 + 구매 박스 (buybox)
   페이지가 <div id="buybox" data-name="..." data-models='[...]'> 를 두면 동작.
   models: [{m:모델, s:규격, p:정가(0=문의)}]
   =========================================================== */
(function () {
  var box = document.getElementById('buybox');
  if (!box) return;

  var NAME = box.dataset.name || document.title;
  var MODELS = [];
  try { MODELS = JSON.parse(box.dataset.models || '[]'); } catch (e) { MODELS = []; }

  var css = document.createElement('style');
  css.textContent =
    '.pd-pick{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:18px 0 0}'
  + '.pd-pick select{flex:1;min-width:190px;max-width:340px;padding:10px 11px;border:1px solid #D9D4CE;'
  +   'border-radius:9px;font-family:inherit;font-size:12.5px;background:#fff;color:#17202A;'
  +   'text-overflow:ellipsis;padding-right:26px}'
  + '.bb{border:1px solid #D8E4F2;border-radius:14px;padding:16px 16px 14px;background:#fff;'
  +   'font-size:13.5px;line-height:1.6}'
  + '.bb-price{font-family:var(--serif,Georgia,serif);font-size:26px;font-weight:800;color:#17202A;letter-spacing:-.01em}'
  + '.bb-price small{font-size:13px;font-weight:700;color:#7a6f68;margin-left:5px}'
  + '.bb-extra{margin:6px 0 0;font-size:12.5px;color:#7a6f68;line-height:1.65}'
  + '.bb-extra b{color:#0F69AF}'
  + '.bb-row{display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-top:1px solid #F1EDE9}'
  + '.bb-row .k{color:#7a6f68;flex:0 0 auto}'
  + '.bb-was{color:#9A9A9A;font-weight:500;margin-right:5px}'
  + '.bb-row .v{text-align:right;font-weight:700;color:#17202A}'
  + '.bb-qty{display:flex;align-items:center;gap:8px;margin:12px 0 10px}'
  + '.bb-qty label{color:#7a6f68;font-size:12.5px}'
  + '.bb-qty input{width:74px;padding:8px 9px;border:1px solid #D9D4CE;border-radius:8px;'
  +   'font-family:inherit;font-size:13.5px;text-align:center}'
  + '.bb-btn{display:block;width:100%;padding:11px 12px;border-radius:10px;font-family:inherit;'
  +   'font-size:14px;font-weight:800;cursor:pointer;border:1px solid transparent;margin-top:8px}'
  + '.bb-cart{background:#EAF4FB;color:#17202A;border-color:#C9DCEF}'
  + '.bb-cart:hover{background:#EFEAE4}'
  + '.bb-buy{background:#3B3695;color:#fff}.bb-buy:hover{background:#2A2570}'
  + '.bb-note{margin:10px 0 0;font-size:12px;color:#9C958D;line-height:1.6}'
  + '.bb-toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:#17202A;color:#fff;'
  +   'padding:11px 18px;border-radius:10px;font-size:13.5px;font-weight:700;opacity:0;pointer-events:none;'
  +   'transition:opacity .25s;z-index:9999}'
  + '.bb-toast.on{opacity:1}';
  document.head.appendChild(css);

  function won(n) { return n ? n.toLocaleString('ko-KR') + '원' : '문의'; }
  /* 모델명과 규격이 같으면 한 번만 쓴다 (예: '표준 · 표준' 방지) */
  function lbl(o) { return (o.m || '') + (o.s && o.s !== o.m ? ' · ' + o.s : ''); }

  /* ── 상단 드롭다운 + 제품문의 버튼 ── */
  var qbtn = document.querySelector('.dt-info .qbtn');
  if (qbtn && MODELS.length) {
    var pick = document.createElement('div');
    pick.className = 'pd-pick';
    var sel = document.createElement('select');
    sel.id = 'pdModel';
    sel.setAttribute('aria-label', '모델 · 옵션 선택');
    MODELS.forEach(function (o, i) {
      var op = document.createElement('option');
      op.value = i;
      op.textContent = lbl(o) + ' — ' + won(unitOf(o));   // 드롭다운은 제품가격 기준 (배송 제외)
      sel.appendChild(op);
    });
    pick.appendChild(sel);
    qbtn.parentNode.insertBefore(pick, qbtn);
    pick.appendChild(qbtn);
  }
  if (qbtn) {
    qbtn.textContent = '제품문의';
    qbtn.setAttribute('data-inquiry', qbtn.getAttribute('data-quote') || NAME);
    qbtn.removeAttribute('data-quote');
  }

  /* ── 우측 구매 박스 ── */
  function cur() {
    var sel = document.getElementById('pdModel');
    var i = sel ? +sel.value : 0;
    return MODELS[i] || { m: '', s: '', p: 0, x: 0 };
  }
  var QTY_ASK = 10;      // 이 수량부터는 배송료를 따로 안내
  /* 합계 = 제품가격 x 수량 + 해외배송료
     제품가격(개당) = o.x , 배송료 = o.p - o.x  (주문당 1회, 수량에 비례하지 않음)
     행 구성은 수량과 무관하게 항상 동일 — 클릭해도 높이가 변하지 않는다 */
  function unitOf(o) { return (o.x != null ? o.x : o.p) || 0; }
  function shipOf(o) { return o.p ? Math.max(0, o.p - unitOf(o)) : 0; }
  function sum(o, q) { return o.p ? unitOf(o) * q + shipOf(o) : 0; }
  /* o.d = 정가(할인 전). 국내 브랜드는 정가 대비 3% 상시 할인가를 제품가격으로 쓰고
     정가는 취소선으로 함께 보여준다. 해외 발주(가오스·허페이)는 o.d 가 없다. */
  function hasDisc(o) { return o.d && o.d > unitOf(o); }
  function unitHtml(o) {
    if (!o.p) return '문의';
    return hasDisc(o)
      ? '<s class="bb-was">' + won(o.d) + '</s> ' + won(unitOf(o))
      : won(unitOf(o));
  }
  function render() {
    var o = cur();
    var q = Math.max(1, +(document.getElementById('pdQty') || {}).value || 1);
    var many = q >= QTY_ASK;
    var head = !o.p ? '문의'
             : many ? '문의<small>10개 이상</small>'
                    : won(sum(o, q)) + '<small>합계 · VAT 별도</small>';
    box.innerHTML =
      '<div class="bb-price">' + head + '</div>'
    + (o.p ? '' : '<p class="bb-extra">규격을 알려주시면 금액을 안내드립니다.</p>')
    + '<div class="bb-row"><span class="k">선택</span><span class="v">' + (lbl(o) || '—') + '</span></div>'
    + '<div class="bb-row"><span class="k">제품가격 (1개)</span><span class="v">' + unitHtml(o) + '</span></div>'
    + '<div class="bb-row"><span class="k">배송</span><span class="v">'
    +   (!o.p ? '문의'
             : shipOf(o) ? (many ? '해외배송 확인 필요' : '해외배송 ' + won(shipOf(o)))
                         : '국내배송 · 주문 시 안내')
    +   '</span></div>'
    + '<div class="bb-row"><span class="k">예상 배송일</span><span class="v">주문 확정 후 안내</span></div>'
    + '<div class="bb-qty"><label for="pdQty">수량</label>'
    +   '<input type="number" id="pdQty" min="1" value="' + q + '"></div>'
    + '<button type="button" class="bb-btn bb-cart" id="bbCart">장바구니 담기</button>'
    + '<button type="button" class="bb-btn bb-buy" id="bbBuy">' + (many ? '수량 문의하기' : '구매하기') + '</button>'
    + '<p class="bb-note">' + (hasDisc(o) ? '정가 대비 3% 상시 할인가입니다. ' : '')
    +   (shipOf(o) ? '배송료는 주문당 1회입니다. ' : '')
    +   '담으신 품목은 장바구니에서 확인하실 수 있습니다.</p>';
  }
  function toast(m) {
    var t = document.querySelector('.bb-toast');
    if (!t) { t = document.createElement('div'); t.className = 'bb-toast'; document.body.appendChild(t); }
    t.textContent = m; t.classList.add('on');
    setTimeout(function () { t.classList.remove('on'); }, 1900);
  }
  function addCart() {
    var o = cur();
    var q = Math.max(1, +(document.getElementById('pdQty') || {}).value || 1);
    var cart = [];
    try { cart = JSON.parse(localStorage.getItem('rs_cart') || '[]') || []; } catch (e) { cart = []; }
    cart.push({ name: NAME + (o.m ? ' ' + o.m : ''), spec: o.s || '',
                link: location.origin + location.pathname, qty: q,
                unit: o.p || 0, extra: (o.x != null ? o.x : o.p) || 0, total: sum(o, q),
                note: q >= QTY_ASK ? '10개 이상 — 배송료 별도 안내' : '' });
    try { localStorage.setItem('rs_cart', JSON.stringify(cart)); } catch (e) {}
    return cart.length;
  }

  /* ── 우측 여백 레일 : 본문 폭은 건드리지 않고 바깥 여백만 사용 ──
     여백이 부족한 화면(<1560px)에서는 제품 정보 아래로 내려보낸다 */
  function railFit() {
    var rail = document.querySelector('.buyrail');
    if (!rail) return;
    var wide = window.matchMedia('(min-width:1560px)').matches;
    var host = wide ? rail : document.querySelector('.dt-info');
    if (host && box.parentNode !== host) host.appendChild(box);
    if (!wide) { rail.style.top = ''; rail.style.height = ''; return; }
    var start = document.querySelector('.detail-top');
    var end   = document.querySelector('#pumplab-footer') || document.querySelector('.ctbar-sec');
    if (!start || !end) return;
    var top = start.offsetTop;
    rail.style.top = top + 'px';
    rail.style.height = Math.max(320, end.offsetTop - top) + 'px';
  }
  railFit();
  window.addEventListener('load', railFit);
  var rzT;
  window.addEventListener('resize', function () {
    clearTimeout(rzT); rzT = setTimeout(railFit, 150);
  });

  render();
  document.addEventListener('change', function (e) {
    if (e.target && (e.target.id === 'pdModel' || e.target.id === 'pdQty')) {
      var keep = e.target.id === 'pdQty' ? e.target.value : null;
      render();
      if (keep) document.getElementById('pdQty').value = keep;
    }
  });
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (t.closest('#bbCart')) { addCart(); if (window.paintCart) window.paintCart(); toast('장바구니에 담았습니다'); }
    if (t.closest('#bbBuy'))  { addCart(); if (window.paintCart) window.paintCart(); location.href = '/cart/'; }
  });
})();
