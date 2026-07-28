/* ============================================================
   실험셋업연구소 공유 헤더·푸터 (site.js) — 전 페이지 동일 구조 주입(SSOT)
   각 페이지의 <div id="pumplab-header"></div> / <div id="pumplab-footer"></div>
   자리에 아래 마크업을 넣는다. 헤더·푸터는 여기서만 고치면 전 페이지 반영.
   ============================================================ */
(function () {
  var path = location.pathname;

  var SEARCH_INDEX = [
    { t:'홈', u:'/', k:'소프트웨어 제어 펌프 시스템 관류', c:'페이지' },
    { t:'리드플루이드(LeadFluid) — 정품·국내 A/S·제어', u:'/leadfluid/guide/', k:'리드플루이드 leadfluid 정품 국내 as 수리 3년보증 연동 시린지 기어 정량펌프 baoding ingersoll rand 나비엠알오 제어 소프트웨어', c:'리드플루이드' },
    { t:'Masterflex·Watson-Marlow 연동펌프 국내 대안', u:'/compare/imported-peristaltic-alternative/', k:'마스터플렉스 masterflex 왓슨말로우 watson-marlow 이즈마텍 ismatec 대안 비교 갈아타기 수입 연동펌프 국내 as 제어', c:'비교' },
    { t:'ALICAT 질량유량계(MFC) 브랜드', u:'/alicat/', k:'alicat 알리캣 질량유량계 mfc mass flow controller 다기체 응답속도 rs485 modbus 소프트웨어 호환 장비', c:'호환 장비' },
    { t:'삼흥에너지(SH-Scientific) 전기로·튜브퍼니스 — 제품 선택·견적', u:'/sh-scientific/guide/', k:'삼흥에너지 sh scientific 튜브퍼니스 관상로 전기로 머플로 열처리 온도 스케줄 가스 연동 공식 대리점 지역 as 제품 선택 가이드 견적문의 구성 종류 온도 분위기 컨트롤러 옵션 시료 공정', c:'호환 장비' },
    { t:'삼흥에너지 전기로·튜브퍼니스 메뉴얼', u:'/sh-scientific/manual/', k:'삼흥에너지 전기로 튜브퍼니스 메뉴얼 사용법 승온 프로그램 온도컨트롤러 sp590 안전 주의사항 설치 열처리 sh scientific', c:'호환 장비' },
    { t:'삼흥에너지 전기로·튜브퍼니스 설치·A/S 블로그', u:'/sh-scientific/blog/', k:'삼흥에너지 전기로 튜브퍼니스 설치 as 점검 사례 블로그 설치 체크리스트 열처리 sh scientific', c:'호환 장비' },
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
    { t:'펌프 셋업 사례 — 실제 도입·제어·유량 보정', u:'/leadfluid/blog/', k:'펌프 셋업 사례 도입 제어 유량 보정 도금 다펌프 튜브퍼니스 mfc 스토리', c:'펌프 셋업 사례' },
    { t:'리드플루이드 국내 A/S·정품·3년보증', u:'/leadfluid/guide/', k:'리드플루이드 leadfluid 국내 as 수리 정품 보증 신뢰 진단 품질', c:'호환 장비' },
    { t:'연동펌프 유량 캘리브레이션 방법', u:'/pump/atoz/flow-calibration/', k:'유량 캘리브레이션 보정 calibration 연동펌프 설정값 실제유량 드리프트 저울 메스실린더 보정계수 재현성', c:'펌프를 고를 때' },
    { t:'연동펌프 튜브 규격·펌프헤드 가이드', u:'/pump/atoz/tube-size-guide/', k:'튜브 규격 번호 내경 mm 13 14 16 25 17 18 펌프헤드 YT25 YZ35 튜브 재질 실리콘 tygon pharmed viton 연동펌프', c:'펌프를 고를 때' },
    { t:'자주 묻는 질문 FAQ', u:'/faq/', k:'질문 faq 정량펌프 연동펌프 튜브 채널 제어 수리 소프트웨어', c:'FAQ' },
    { t:'기술자료 허브 — 사용법·문제해결·제어 자동화', u:'/', k:'기술자료 사용법 가이드 문제해결 캘리브레이션 자동화 허브', c:'페이지' },
    { t:'온도컨트롤러(SP590·NOVA500E) 사용법 가이드', u:'/temp-controller-guide/', k:'온도컨트롤러 sp590 sp570 nova500e 삼원테크 사용법 전기로 온도 설정 승온 유지 하강 반복 hold 무한반복 rs485 가상 시뮬레이터 삼흥에너지', c:'호환 장비' },
    { t:'문의하기', u:'/contact/', k:'상담 수리 개발 견적 실험 문의', c:'문의하기' }
  ];
  fetch('/_build/posts.json').then(function (r) { return r.json(); }).then(function (d) {
    (d.posts || []).forEach(function (p) {
      SEARCH_INDEX.push({ t: p.title, u: p.url,
        k: (p.tags || []).join(' ') + ' ' + (p.journal || '') + ' ' + (p.model_focus || '') + ' ' + (p.application || ''),
        c: (p.type === 'setup' ? '도입·논문 사례' : '블로그') });
    });
  }).catch(function () {});

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
  var NAV = [
    { href:'/sh-scientific/guide/', label:'삼흥에너지(sh-scientific)', icon:'devices', sub:[
        ['/sh-scientific/guide/',   '퍼니스 선택 가이드'],
        ['/sh-scientific/catalog/', '카탈로그'],
        ['/sh-scientific/manual/',  '메뉴얼'],
        ['/sh-scientific/blog/',    '블로그']
      ] },
    { href:'/leadfluid/guide/', label:'리드플루이드(LeadFluid)', icon:'wrench', sub:[
        ['/leadfluid/guide/',  '펌프 선택 가이드'],
        ['/leadfluid/manuals/', '메뉴얼'],
        ['/leadfluid/blog/',    '블로그']
      ] },
    { href:'/alicat/', label:'Alicat MFC', icon:'gas' },
    { href:'/about/', label:'회사소개', icon:'shield' },
    { href:'/contact/', label:'문의하기', icon:'contact' },
    { href:'/faq/', label:'FAQ', icon:'faq' }
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

  var HEADER =
    '<header class="ch-top">' +
      '<button class="ch-burger" type="button" aria-label="메뉴" aria-expanded="false"><span></span><span></span><span></span></button>' +
      '<a class="ch-brand" href="/">실험셋업연구소</a>' +
      '<form class="ch-search" id="chSearch" role="search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg><input type="search" placeholder="검색" aria-label="사이트 검색" autocomplete="off"><div class="ch-results" id="chResults"></div></form>' +
      '<a class="ch-cta" href="/contact/">문의하기</a>' +
    '</header>' +
    '<aside class="ch-side" id="chSide"><nav>' + navHTML + '</nav>' +
      '<div class="ch-side-foot">실험 장비 시스템 통합·제어 · 국내 직접 A/S<br>리드플루이드·삼흥 공식 대리점 · 나비엠알오 등록 공급사</div>' +
      '<a id="adminNav" href="/admin" style="display:block;margin:12px 14px 8px;font-size:11px;color:#9aa3ad;text-decoration:none;border-top:1px solid #e6eaf0;padding-top:9px">\u2699 관리자</a>' +
      '<a id="adminOut" href="#" style="display:none;margin:0 14px 10px;font-size:10.5px;color:#b3b9c2;text-decoration:none">로그아웃</a>' +
    '</aside>' +
    '<div class="ch-scrim" id="chScrim"></div>';

  var FOOTER =
    '<section class="cta-band"><div class="cta-band-in">' +
      '<div class="cta-band-t">실험 장비 시스템 통합·제어 · 온도·진공·유량 통합 제어 · 국내 직접 A/S</div>' +
      '<div class="cta-band-btns">' +
        '<a href="https://www.navimro.com/s/?x=0&y=0&q=leadfluid&disp=0&keyword=" target="_blank" rel="noopener" data-ga="band_navimro">구매 (나비엠알오) →</a>' +
        '<a href="/repair/" data-ga="band_repair">A/S·수리 접수 →</a>' +
        '<a class="cta-band-main" href="/contact/#quote" data-ga="band_quote">견적·문의 →</a>' +
      '</div></div></section>' +
    '<footer class="chrome-footer">' +
      '<div class="cf-inner">' +
        '<div class="cf-cols">' +
          '<div class="cf-col"><h4>바로가기</h4>' +
            '<a href="/leadfluid/">제품·모델</a><a href="/about/">회사소개</a><a href="/trust/">정품·인증</a><a href="/repair/">A/S·수리</a><a href="/faq/">FAQ</a></div>' +
          '<div class="cf-col"><h4>문의</h4>' +
            '<a href="/contact/">일반 문의</a><a href="/contact/#quote">견적 문의</a>' +
            '<a href="https://www.navimro.com/s/?x=0&y=0&q=leadfluid&disp=0&keyword=" target="_blank" rel="noopener" data-ga="navimro_footer">견적·구매 (나비엠알오)</a></div>' +
          '<div class="cf-col"><h4>고객센터</h4>' +
            '<a href="mailto:info@rndsetup.com">info@rndsetup.com</a>' +
            '<a href="tel:+827089832600">070-8983-2600</a>' +
            '<span>실험 장비 시스템 통합·제어 · 온도·진공·유량 통합 제어</span><span>리드플루이드·삼흥 공식 대리점 · 국내 직접 A/S · 3년 무상보증</span></div>' +
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
      // 자동 인사말 말풍선 — 방문 후 잠시 뒤 노출, 클릭 시 채널톡 상담창 열림
      window.addEventListener('load', function () {
        try { if (sessionStorage.getItem('ccGreetX')) return; } catch (e) {}
        var b = document.createElement('div');
        b.className = 'cc-greet-pop';
        b.innerHTML = '<button class="cc-greet-x" type="button" aria-label="닫기">×</button>' +
          '<div class="cc-greet-tx">안녕하세요, <b>실험셋업연구소</b>입니다 👋<br>정량펌프·질량유량계(MFC)·진공·자동화 셋업과 제어, 수리까지 무엇이든 편하게 물어보세요.</div>';
        function hide() { b.classList.remove('show'); try { sessionStorage.setItem('ccGreetX', '1'); } catch (e) {} setTimeout(function () { if (b.parentNode) b.parentNode.removeChild(b); }, 300); }
        b.querySelector('.cc-greet-x').addEventListener('click', function (ev) { ev.stopPropagation(); hide(); });
        b.addEventListener('click', function () { if (window.ChannelIO) window.ChannelIO('showMessenger'); hide(); });
        document.body.appendChild(b);
        setTimeout(function () { b.classList.add('show'); }, 2500);
      });
    }
    // 리드플루이드 펌프 보기 — /pump/ 하위 전 페이지 하단 고정 배너(스크롤 따라 진해짐)
    if (window.self === window.top && path.indexOf('/pump/') === 0 && !document.querySelector('.lf-sticky')) {
      var lf = document.createElement('a');
      lf.className = 'lf-sticky';
      lf.href = '/leadfluid/guide/';
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
    var sf = document.getElementById('chSearch');
    var rbox = document.getElementById('chResults');
    if (sf && rbox) {
      var inp = sf.querySelector('input');
      function esc(s){ return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
      function doSearch() {
        var q = (inp.value || '').trim().toLowerCase();
        if (!q) { rbox.classList.remove('open'); rbox.innerHTML = ''; return; }
        var hits = SEARCH_INDEX.filter(function (it) {
          return (it.t + ' ' + (it.k || '') + ' ' + (it.c || '')).toLowerCase().indexOf(q) > -1;
        }).slice(0, 8);
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
    if (!document.querySelector('.navimro-fab')) {
      document.body.insertAdjacentHTML('beforeend',
        '<a class="navimro-fab" href="https://www.navimro.com/s/?x=0&y=0&q=leadfluid&disp=0&keyword=" target="_blank" rel="noopener" data-ga="navimro_fab" aria-label="나비엠알오에서 LeadFluid 제품 보기">' +
          '<span class="nm-brand">NAVI<b>MRO</b></span>' +
          '<span class="nm-t">LeadFluid<br>제품 바로가기</span>' +
        '</a>');
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
