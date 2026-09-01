# -*- coding: utf-8 -*-
# 그린 헤더/푸터 site-wide + 홈 리파인. site.js / site.css / index.html 패치.
import io
import os
R=os.path.dirname(os.path.abspath(__file__)).rstrip('/')+'/'

# ============ 1) site.js ============
js = io.open(R+'assets/site.js', encoding='utf-8').read()

# 1a) NAV 4개로 교체
a = js.index('  var NAV = [')
b = js.index('  ];', a) + len('  ];')
NEW_NAV = """  var NAV = [
    { href:'/materials/', label:'Products', icon:'guide' },
    { href:'/product/', label:'Equipments', icon:'devices' },
    { href:'/magazine/', label:'Setup Blog', icon:'feed' },
    { href:'/about/', label:'Company', icon:'contact' }
  ];"""
js = js[:a] + NEW_NAV + js[b:]

# 1b) 뉴스레터 섹션 제거 (FOOTER 시작의 <section 2A2570 ...> ~ <footer 직전)
a = js.index('var FOOTER =')
fp = js.index("'<footer class=\"chrome-footer\">'", a)
js = js[:a] + "var FOOTER =\n    " + js[fp:]

# 1c) 푸터 링크 정리 (trust/repair/FAQ 제거, 메뉴얼 추가)
js = js.replace(
 '<a href="/product/?q=리드플루이드">제품·모델</a><a href="/about/">회사소개</a><a href="/trust/">정품·인증</a><a href="/repair/">A/S·수리</a>',
 '<a href="/product/">제품·모델</a><a href="/manuals/">메뉴얼</a><a href="/about/">회사소개</a>')
js = js.replace(
 '<a href="/contact/">일반 문의</a><a href="/contact/#quote">견적 문의</a><a href="/contact/">자주 묻는 질문(FAQ)</a>',
 '<a href="/contact/">일반 문의</a><a href="/contact/#quote">견적 문의</a>')
io.open(R+'assets/site.js','w',encoding='utf-8').write(js)
print('site.js patched; NAV·newsletter·footer OK')

# ============ 2) site.css: 그린 오버라이드 append ============
css = io.open(R+'assets/site.css', encoding='utf-8').read()
GREEN = """
/* ===== 그린 크롬 오버라이드 (랜딩 통일) ===== */
:root{ --green:#39b54a; }
.ch-brand{ color:#141821 !important; }
.ch-brand::before{ content:""; display:inline-block; width:16px; height:16px; margin-right:7px; vertical-align:-2px;
  background:#39b54a; -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 15c5-1 8.5-9 17-11-2.2 8.5-9.5 12.5-17 11z'/%3E%3C/svg%3E") center/contain no-repeat;
  mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 15c5-1 8.5-9 17-11-2.2 8.5-9.5 12.5-17 11z'/%3E%3C/svg%3E") center/contain no-repeat; }
.tn-link{ color:#3c4652 !important; }
.tn-link:hover, .tn-link.active{ color:#2f9d3f !important; }
.tn-link.active::after, .ch-nav .tn-item .tn-link.active::after{ background:#39b54a !important; }
.tn-dd a:hover, .tn-dd a.active{ color:#2f9d3f !important; }
.s-item.active, .s-sub a.active{ color:#2f9d3f !important; }
.ch-msearch button{ background:#39b54a !important; }
.ch-msearch input:focus{ border-color:#39b54a !important; }
.ch-ic:hover{ color:#2f9d3f !important; }
.ch-cnt{ background:#39b54a !important; }
/* 푸터 그린/다크 */
.chrome-footer{ background:#12161d !important; color:#8b96a5 !important; }
.chrome-footer .cf-col h4{ color:#cdd4dd !important; }
.chrome-footer .cf-col a, .chrome-footer .cf-col span{ color:#8b96a5 !important; }
.chrome-footer .cf-col a:hover{ color:#8fe6a3 !important; }
.chrome-footer .cf-co, .chrome-footer .cf-cp{ color:#6a7482 !important; border-color:#232a34 !important; }
.chrome-footer .cf-co strong{ color:#e7ecf2 !important; }
"""
if '그린 크롬 오버라이드' not in css:
    css = css + '\n' + GREEN
io.open(R+'assets/site.css','w',encoding='utf-8').write(css)
print('site.css green override appended')

# ============ 3) index.html: 홈 공유헤더 복귀 + 리파인 ============
h = io.open(R+'index.html', encoding='utf-8').read()
assert '<div class="lb-hd">' in h, '홈에 인라인 그린헤더 없음(이미 복귀?)'

# 3a) 인라인 그린 헤더 → 공유 헤더 div
a = h.index('<div class="lb-hd">'); b = h.index('<main class="home-main">')
h = h[:a] + '<div id="pumplab-header"></div>\n\n' + h[b:]

# 3b) CSS+섹션 교체 (LB_CSS ~ 이용후기 직전) — 헤더/푸터 CSS 제거, 히어로 중앙, 슬라이더 이미지+자동재생
IC = { 'box':'<svg viewBox="0 0 24 24"><path d="M3 7l9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7"/></svg>',
 'clock':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 'doc':'<svg viewBox="0 0 24 24"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 16h6"/></svg>',
 'tools':'<svg viewBox="0 0 24 24"><path d="M14.5 6.5a3.5 3.5 0 0 1-4.6 4.6L5 16l3 3 4.9-4.9a3.5 3.5 0 0 0 4.6-4.6l-2.1 2.1-2-2z"/></svg>',
 'anode':'<svg viewBox="0 0 24 24"><rect x="4" y="7" width="14" height="10" rx="2"/><path d="M18 10h2v4h-2"/><path d="M8 12h4"/></svg>',
 'cathode':'<svg viewBox="0 0 24 24"><rect x="4" y="7" width="14" height="10" rx="2"/><path d="M18 10h2v4h-2"/><path d="M8 12h4M10 10v4"/></svg>',
 'binder':'<svg viewBox="0 0 24 24"><path d="M12 3c3 4 5 6.5 5 9a5 5 0 0 1-10 0c0-2.5 2-5 5-9z"/></svg>',
 'cond':'<svg viewBox="0 0 24 24"><circle cx="7" cy="9" r="1.6"/><circle cx="14" cy="7" r="1.6"/><circle cx="17" cy="13" r="1.6"/><circle cx="10" cy="15" r="1.6"/><circle cx="6" cy="16" r="1.4"/></svg>',
 'sep':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.4"/><path d="M12 5v3M12 16v3"/></svg>',
 'foil':'<svg viewBox="0 0 24 24"><path d="M4 9c3-2 5 2 8 0s5-2 8 0M4 14c3-2 5 2 8 0s5-2 8 0"/></svg>',
 'sheet':'<svg viewBox="0 0 24 24"><rect x="5" y="6" width="12" height="12" rx="1"/><path d="M8 4h12v12"/></svg>',
 'cell':'<svg viewBox="0 0 24 24"><path d="M9 3h6M10 3v5l-4 9a2 2 0 0 0 1.8 3h8.4a2 2 0 0 0 1.8-3l-4-9V3"/><path d="M7.5 15h9"/></svg>',
 'electrode':'<svg viewBox="0 0 24 24"><path d="M12 3v10"/><rect x="9.5" y="13" width="5" height="7" rx="1.2"/><path d="M9 6h6M9 9h6"/></svg>',
 'flow':'<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M2 12h4M18 12h4M12 2v4M12 18v4"/></svg>',
 'lab':'<svg viewBox="0 0 24 24"><rect x="8" y="3" width="8" height="18" rx="4"/><path d="M8 9h8"/></svg>',
 'tube':'<svg viewBox="0 0 24 24"><rect x="2" y="9.5" width="20" height="5" rx="2.5"/><rect x="8" y="6" width="8" height="12" rx="1.5"/></svg>',
 'muffle':'<svg viewBox="0 0 24 24"><rect x="4" y="6" width="16" height="12" rx="1.5"/><path d="M4 9.5h16M9 12h6"/></svg>',
 'rotary':'<svg viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="9" ry="5"/><path d="M6 8.5L4 6M18 8.5l2-2.5"/></svg>',
 'pump':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="7" r="1.3"/><circle cx="16.3" cy="14.5" r="1.3"/><circle cx="7.7" cy="14.5" r="1.3"/></svg>',
 'syringe':'<svg viewBox="0 0 24 24"><path d="M13 4l7 7M17.5 6.5l-10 10-3.5 1 1-3.5 10-10z"/></svg>',
 'gauge':'<svg viewBox="0 0 24 24"><path d="M4 16a8 8 0 0 1 16 0"/><path d="M12 16l4-3"/><circle cx="12" cy="16" r="1"/></svg>'}
CHIP='<span class="lb-bb"><i></i>rndsetup</span>'; MAT='/materials/'
CATS=[('ANODE','CNB-1-A01','anode',MAT),('CATHODE','CNB-1-C11','cathode',MAT),('BINDER','CNB-6-B01','binder',MAT),('CONDUCTIVE ADDITIVE','CNB-1-CA02','cond',MAT),
 ('SEPARATORS','Celgard® H1612','sep',MAT),('FOIL AND FOAM','Titanium (Ti)','foil',MAT),('ELECTRODE SHEET','Cu / Al','sheet',MAT),('TOOLS','Part B','tools',MAT),
 ('ELECTROCHEMICAL CELLS','C002-1 Jacketed','cell','/brands/gaossunion/battery-cell-b002/'),('ELECTRODES','Electrode Clamp','electrode','/brands/gaossunion/simple-electrode-holder/'),
 ('IN-SITU AND FLOW CELLS','Flow Cell E6','flow','/brands/gaossunion/gas-diffusion-cell-standard/'),('LAB CONSUMABLES','CNB-13-PB02','lab',MAT)]
EQ=[('튜브퍼니스','Tube Furnace','tube','/product/?q=%ED%8A%9C%EB%B8%8C%ED%8D%BC%EB%8B%88%EC%8A%A4'),('머플로·전기로','Muffle Furnace','muffle','/product/?q=%EB%A8%B8%ED%94%8C%EB%A1%9C'),
 ('회전 튜브로','Rotary Kiln','rotary','/brands/sh-scientific/rotary-tube-furnace-pro/'),('진공·건조','Vacuum · Drying','vacuum' if False else 'box','/product/?q=%EC%A7%84%EA%B3%B5'),
 ('정량·연동펌프','Peristaltic Pump','pump','/product/?q=%EC%97%B0%EB%8F%99%ED%8E%8C%ED%94%84'),('시린지·기어펌프','Syringe · Gear','syringe','/product/?q=%EA%B8%B0%EC%96%B4%ED%8E%8C%ED%94%84'),
 ('질량유량계 MFC','Mass Flow','gauge','/product/?q=MFC'),('온도 컨트롤러','Temp Controller','box','/temp-controller-guide/')]
POSTS=[('논문 셋업 · Energy Technology','초후막 양극, 믹싱만 바꿔 1C 용량 1.67배 — 슬러리 믹싱·전극 코팅 셋업','2026-08-23 · 플래니터리 믹서 · 정량 급액 펌프','/magazine/electrode-slurry-mixing-thick-cathode/','/img/product/sh/tube-1500.jpg'),
 ('논문 셋업 · Nature Communications','소듐 양극재 상순도 합성 — 소성 동적 분위기 제어(DCA) 셋업','2025 · 튜브퍼니스 · MFC 동적 분위기','/magazine/sodium-cathode-atmosphere-dca/','/img/magazine/dca-setup-diagram-3d.jpg'),
 ('논문 셋업 · PNAS','레독스흐름전지 전해액 순환 셋업 — 유로 설계 + 연동펌프','2024 · 유로 설계 · 연동펌프 140 mL/min','/magazine/aorfb-flowfield-electrolyte-pump/','/img/magazine/aorfb-setup-3d.jpg'),
 ('논문 셋업 · Chem. Eng. Technol.','배터리 양극재 전구체 공침 셋업 — CSTR + 연동펌프','2023 · CSTR · 연동펌프 3채널','/magazine/nickel-hydroxide-coprecipitation-cstr/','/img/magazine/nickel-cstr-setup-3d.jpg'),
 ('논문 셋업 · Nature Communications','실리콘 음극 아세틸렌 CVD 탄소 코팅 셋업 — 튜브퍼니스+MFC','2018 · 튜브퍼니스 · MFC 가스 유량 제어','/magazine/si-anode-cvd-carbon-coating/','/img/magazine/si-cvd-setup-3d.jpg'),
 ('논문 셋업 · Batteries & Supercaps','전극 진공 후건조·잔류 수분 관리 셋업 — 압력 사이클과 노점','2021 · 진공 건조 · 압력 사이클','/magazine/electrode-vacuum-post-drying-moisture/','/img/product/sh/vacuum-muffle-1500.jpg'),
 ('논문 셋업 · Scientific Reports','구리 열산화 CuO 나노와이어 성장 셋업 — 공기 450℃','2019 · 머플로 · 공기 분위기 450℃','/magazine/cuo-nanowire-thermal-oxidation/','/img/magazine/cuo-oxidation-setup-3d.jpg'),
 ('인시츄 셀 · NEW','극저온 인시츄 셀 CIS-OM-005 — In-situ 관찰 시스템','2026-09-01 · CIS-OM-005 인시츄 관찰 셀','/magazine/insitu-cell-005/','/img/magazine/insitu-005-hero.jpg')]
VALS=[('box','소량 단위 공급','연구실에서 쓰는 만큼만 — 소량 단위로 공급.'),('clock','빠른 납기','재고 다수 즉시 출고, 커스텀도 최단 납기로.'),
 ('doc','스펙 시트 제공','조성·물성·안전정보 문서와 함께 재현성 있게.'),('tools','국내 기술지원·A/S','실험셋업연구소가 셋업·문의·A/S를 직접 대응.')]
def cat_cards(items): return ''.join('<a class="lb-cat" href="%s"><div class="lb-tile">%s%s</div><div class="lb-bd"><div class="lb-t">%s</div><span class="lb-code">%s</span></div></a>'%(href,IC[ic],CHIP,n,c) for n,c,ic,href in items)
def sb_cards(): return ''.join('<a class="lb-sbcard" href="%s"><div class="lb-sbtop" style="background-image:url(\'%s\')"><span class="lb-tag">%s</span></div><div class="lb-cb"><div class="lb-ct">%s</div><div class="lb-cm">%s</div></div></a>'%(href,img,tag,ti,me) for tag,ti,me,href,img in POSTS)
def val_cards(): return ''.join('<div class="lb-val"><div class="lb-c">%s</div><div class="lb-vt">%s</div><div class="lb-vd">%s</div></div>'%(IC[i],t,d) for i,t,d in VALS)

LB_CSS='''<style>
/* ===== B안 랜딩 본문 (lb-, 헤더/푸터는 공유 크롬 사용) ===== */
.lb-hero{width:100vw;margin-left:calc(50% - 50vw);background:radial-gradient(120% 90% at 50% 0%,#233042 0%,#171b23 48%,#0f1319 100%);color:#eef2f7;position:relative;overflow:hidden}
.lb-hero::after{content:"";position:absolute;left:50%;top:-160px;transform:translateX(-50%);width:620px;height:520px;background:radial-gradient(circle,rgba(57,181,74,.22),transparent 62%);pointer-events:none}
.lb-hin{max-width:1180px;margin:0 auto;padding:66px 24px 74px;position:relative;z-index:1;text-align:center}
.lb-hin .in2{max-width:760px;margin:0 auto}
.lb-ey{font-size:12px;font-weight:800;letter-spacing:.22em;color:#8fe6a3}
.lb-hero h1{font-size:44px;font-weight:800;line-height:1.14;letter-spacing:-1px;margin-top:16px;color:#fff}
.lb-hero h1 em{font-style:normal;color:#39b54a}
.lb-sub{font-size:16px;color:#aeb8c6;line-height:1.7;margin:18px auto 0;max-width:620px}
.lb-cta{display:flex;gap:12px;margin-top:28px;justify-content:center;flex-wrap:wrap}
.lb-btn{display:inline-block;background:#39b54a;color:#fff;font-weight:700;font-size:14px;padding:10px 20px;border-radius:24px;text-decoration:none}
.lb-btn:hover{background:#2f9d3f}.lb-btn.o{background:transparent;color:#fff;border:1.5px solid rgba(255,255,255,.55)}.lb-btn.o:hover{border-color:#39b54a;color:#8fe6a3}
.lb-stats{display:flex;gap:34px;margin-top:40px;justify-content:center;flex-wrap:wrap}
.lb-stats .n{font-size:25px;font-weight:800;color:#fff}.lb-stats .l{font-size:12px;color:#8b96a5;margin-top:3px}
.lb-sec{max-width:1180px;margin:0 auto;padding:56px 24px}
.lb-soft{width:100vw;margin-left:calc(50% - 50vw);background:#f5f7fa}.lb-soft .lb-inr{max-width:1180px;margin:0 auto;padding:56px 24px}
.lb-sh{text-align:center;margin-bottom:28px}.lb-sh .k{font-size:11.5px;font-weight:800;letter-spacing:.22em;color:#2f9d3f}
.lb-sh h2{font-size:28px;font-weight:800;letter-spacing:-.5px;margin-top:7px;color:#141821}.lb-sh p{font-size:14px;color:#5c6674;margin-top:9px}
.lb-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.lb-cat{position:relative;border-radius:15px;overflow:hidden;background:#fff;border:1px solid #e6e9ee;text-decoration:none;color:inherit;transition:transform .16s,box-shadow .16s;display:block}
.lb-cat:hover{transform:translateY(-4px);box-shadow:0 18px 38px rgba(20,30,50,.16)}
.lb-tile{height:124px;background:radial-gradient(120% 120% at 50% 0%,#39404d,#20242c);display:flex;align-items:center;justify-content:center;position:relative}
.lb-tile svg{width:46px;height:46px;stroke:#8fe6a3;fill:none;stroke-width:1.5;opacity:.95}
.lb-bb{position:absolute;top:11px;right:13px;font-size:9.5px;font-weight:700;color:#d5dbe4;display:flex;align-items:center;gap:4px;opacity:.82}.lb-bb i{width:9px;height:9px;background:#39b54a;border-radius:2px;transform:skewX(-12deg);display:inline-block}
.lb-bd{padding:13px 15px 15px}.lb-t{font-size:15px;font-weight:800;color:#141821}
.lb-code{display:inline-block;margin-top:8px;font-size:11px;color:#5b6572;background:#f4f6f8;border:1px solid #e6e9ee;border-radius:7px;padding:3px 9px;font-weight:600}
.lb-vals{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.lb-val{text-align:center;padding:8px 10px}
.lb-c{width:56px;height:56px;border-radius:16px;background:#eafaee;display:flex;align-items:center;justify-content:center;margin:0 auto 14px}.lb-c svg{width:27px;height:27px;stroke:#2f9d3f;fill:none;stroke-width:1.7}
.lb-vt{font-size:16px;font-weight:800;color:#141821}.lb-vd{font-size:13px;color:#5c6674;line-height:1.6;margin-top:7px}
.lb-ctaband{width:100vw;margin-left:calc(50% - 50vw);background:linear-gradient(100deg,#16351f,#123a1e 40%,#0f2a18);color:#eaf5ec}
.lb-cin{max-width:1180px;margin:0 auto;padding:46px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}
.lb-cin h3{font-size:24px;font-weight:800;color:#fff}.lb-cin p{font-size:14px;color:#a9c6b1;margin-top:8px}.lb-cin .r{margin-left:auto;display:flex;gap:12px}
.lb-sbwrap{position:relative}.lb-sbview{overflow:hidden}.lb-sbtrack{display:flex;gap:18px;transition:transform .42s cubic-bezier(.22,.61,.36,1)}
.lb-sbcard{flex:0 0 calc((100% - 54px)/4);border:1px solid #e6e9ee;border-radius:14px;overflow:hidden;background:#fff;text-decoration:none;color:inherit;transition:transform .16s,box-shadow .16s}
.lb-sbcard:hover{transform:translateY(-4px);box-shadow:0 16px 34px rgba(20,30,50,.14)}
.lb-sbtop{height:140px;background:#20242c center/contain no-repeat;position:relative;display:flex;align-items:flex-end;padding:10px}
.lb-tag{font-size:10px;font-weight:800;color:#8fe6a3;background:rgba(15,19,25,.72);border:1px solid rgba(57,181,74,.4);border-radius:20px;padding:3px 10px}
.lb-cb{padding:14px 15px 16px}.lb-ct{font-size:14px;font-weight:800;line-height:1.42;min-height:3.0em;color:#141821}.lb-cm{font-size:11.5px;color:#5c6674;margin-top:10px;line-height:1.5}
.lb-sbnav{position:absolute;top:38%;width:40px;height:40px;border-radius:50%;background:#fff;border:1px solid #e6e9ee;box-shadow:0 6px 16px rgba(20,30,50,.14);display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:3}
.lb-sbnav svg{width:18px;height:18px;stroke:#3c4652;fill:none;stroke-width:2.2}.lb-sbnav.prev{left:-18px}.lb-sbnav.next{right:-18px}
.lb-sbdots{display:flex;justify-content:center;gap:8px;margin-top:22px}.lb-sbdots i{width:8px;height:8px;border-radius:50%;background:#cbd2db;cursor:pointer;transition:width .2s,background .2s}.lb-sbdots i.on{background:#39b54a;width:22px;border-radius:5px}
@media(max-width:960px){.lb-grid{grid-template-columns:repeat(3,1fr)}.lb-vals{grid-template-columns:repeat(2,1fr)}.lb-hero h1{font-size:32px}.lb-sbcard{flex:0 0 calc((100% - 18px)/2)}.lb-sbnav{display:none}}
@media(max-width:600px){.lb-grid{grid-template-columns:repeat(2,1fr)}}
</style>'''
SECTIONS = LB_CSS + (
 '<div class="lb-hero"><div class="lb-hin"><div class="in2">'
 '<div class="lb-ey">BATTERY R&amp;D · MATERIALS · EQUIPMENT</div>'
 '<h1>배터리 연구에 필요한 모든 것,<br><em>한 곳에서</em>.</h1>'
 '<div class="lb-sub">양극·음극재부터 전극·셀·실험 소모품, 그리고 튜브퍼니스·펌프·MFC 같은 실험 장비까지 — 소량 단위로, 스펙 시트와 함께 바로 공급합니다.</div>'
 '<div class="lb-cta"><a class="lb-btn" href="#lb-products">카테고리 보기</a><a class="lb-btn o" href="/contact/">견적 요청</a></div>'
 '<div class="lb-stats"><div><div class="n">12</div><div class="l">소재 카테고리</div></div><div><div class="n">1,700+</div><div class="l">SKU 정품 공급</div></div>'
 '<div><div class="n">소량</div><div class="l">단위 공급</div></div><div><div class="n">국내</div><div class="l">기술지원·A/S</div></div></div></div></div></div>'
 '<section class="lb-sec" id="lb-products"><div class="lb-sh"><div class="k">PRODUCTS · 소재</div><h2>배터리 소재 카테고리</h2><p>필요한 소재를 카테고리로 바로 찾으세요.</p></div><div class="lb-grid">'+cat_cards(CATS)+'</div></section>'
 '<div class="lb-soft"><div class="lb-inr"><div class="lb-sh"><div class="k">EQUIPMENTS · 실험 장비</div><h2>실험 장비 라인업</h2><p>튜브퍼니스·전기로·펌프·질량유량계 등 실험셋업연구소 정품 장비.</p></div><div class="lb-grid">'+cat_cards(EQ)+'</div></div></div>'
 '<section class="lb-sec" id="setupblog"><div class="lb-sh"><div class="k">SETUP BLOG · 셋업 사례</div><h2>최신 셋업 사례</h2><p>논문과 현장이 실제로 쓴 에너지·소재 공정 셋업을 공정 → 조건 → 장비 순으로.</p></div>'
 '<div class="lb-sbwrap"><div class="lb-sbnav prev" id="lbPrev"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></div><div class="lb-sbnav next" id="lbNext"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></div>'
 '<div class="lb-sbview"><div class="lb-sbtrack" id="lbTrack">'+sb_cards()+'</div></div><div class="lb-sbdots" id="lbDots"></div></div></section>'
 '<div class="lb-soft"><div class="lb-inr"><div class="lb-sh"><div class="k">WHY 실험셋업연구소</div><h2>연구실이 멈추지 않게</h2></div><div class="lb-vals">'+val_cards()+'</div></div></div>'
 '<div class="lb-ctaband"><div class="lb-cin"><div><h3>찾는 소재·장비가 목록에 없나요?</h3><p>수급 가능 여부와 납기를 확인해 드립니다. 커스텀 사양·통합 셋업도 직접 설계·공급합니다.</p></div><div class="r"><a class="lb-btn" href="/contact/">견적 요청 →</a><a class="lb-btn o" href="/contact/">문의하기</a></div></div></div>'
 '<script>(function(){var t=document.getElementById("lbTrack"),d=document.getElementById("lbDots"),p=document.getElementById("lbPrev"),n=document.getElementById("lbNext");'
 'if(!t)return;var per=4,pages=Math.ceil(t.children.length/per),pg=0,timer=null;'
 'for(var i=0;i<pages;i++){var s=document.createElement("i");s.dataset.i=i;d.appendChild(s);}'
 'function r(){var v=t.parentElement;t.style.transform="translateX("+(-pg*(v.clientWidth+18))+"px)";for(var i=0;i<d.children.length;i++)d.children[i].className=(i===pg?"on":"");}'
 'function go(k){pg=(k+pages)%pages;r();}p.onclick=function(){go(pg-1);reset();};n.onclick=function(){go(pg+1);reset();};'
 'd.onclick=function(e){var i=e.target.dataset.i;if(i!=null){go(+i);reset();}};'
 'function start(){timer=setInterval(function(){go(pg+1);},2000);}function stop(){if(timer){clearInterval(timer);timer=null;}}function reset(){stop();start();}'
 'var w=t.closest(".lb-sbwrap");w.addEventListener("mouseenter",stop);w.addEventListener("mouseleave",start);window.addEventListener("resize",r);r();start();})();</script>'
)
a = h.index('<style>\n/* ===== B안 랜딩'); b = h.index('<section class="bb-sec">\n    <div class="brand-head">')
h = h[:a] + SECTIONS + '\n\n    ' + h[b:]

for must in ['</html>','id="pumplab-header"','id="pumplab-footer"','회전 튜브로 PRO','rv-band','lb-hero','text-align:center','setInterval','lb-sbtop']:
    assert must in h, 'MISSING '+must
assert '<div class="lb-hd">' not in h
io.open(R+'index.html','w',encoding='utf-8').write(h)
print('index.html patched OK bytes=',len(h))
