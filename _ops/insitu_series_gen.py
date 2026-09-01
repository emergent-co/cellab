# 인시츄 시리즈 002·004·005편 생성 (003 파일을 골격으로) + 003 라인업 링크화
import os, re, json

BASE = 'magazine/insitu-li-dendrite-observation/index.html'
base = open(BASE, encoding='utf-8').read()

def seg(h, a, b):
    i = h.find(a); assert i >= 0, a[:50]
    j = h.find(b, i); assert j > i, b[:50]
    return h[i:j]

# 공통 블록 추출
SCOPE = seg(base, '<h3 style="font-size:16px;color:#2A2570;margin:18px 0 4px">공통 광학계', '<figure style="margin:18px 0 6px">')  # h3+p+figure+spec+... 까지 확인 필요
# SCOPE는 h3~카메라 스펙 div 종료까지: 다시 정확히
a = base.find('<h3 style="font-size:16px;color:#2A2570;margin:18px 0 4px">공통 광학계')
b = base.find('</div>', base.find('U820', a)) + 6
SCOPE = base[a:b]
DLBOX = seg(base, '<div class="msc-dl">', '</div>\n\n    <h2') + '</div>'
BUY = seg(base, '<div style="background:#F4F8FC;border:1px solid #D8E4F2;border-radius:10px;padding:12px 16px;margin:6px 0 14px', '</div>') + '</div>'
POPUP = seg(base, '<div class="msc-ov" id="msc-ov"', '<script src="/assets/site.js"')
LBX = seg(base, '<div class="lbx" id="lbx"', '</script>') + '</script>'
STYLE = seg(base, '<style>', '</style>') + '</style>'
HEADLD_ORG = ''  # build가 주입

ROWS = {
 '003': ('<b>CIS-OM-003</b><br>표준형', 'PEEK · 고순도 Ti 가동 전극(재질 커스텀)', '석영창 Φ24 mm · 두께 0.05 mm · 최소 작동거리 1 mm', '상온 · 가압 모듈 옵션 최대 6 MPa', '시료 10×10 mm · 0.6~2 mm · 액체·전고체 겸용', '/magazine/insitu-li-dendrite-observation/'),
 '002': ('<b>CIS-OM-002</b><br>비커형', '석영 비커 5 mL · PTFE 셸(O링 밀봉) · 순티타늄 전극', '비커 측벽 개방 광학 경로 · 전극 간격 3 mm', '상온', '아연 대칭 전지 등 수계 입문', '/magazine/insitu-cell-002/'),
 '004': ('<b>CIS-OM-004</b><br>고저온형', 'PEEK · 기본 유리질 탄소(GC) 전극', '석영창 Φ24 mm · 최소 작동거리 1 mm', '<b>−30~150℃</b> · ±1℃ 프로그램 — 냉각·가열 플랫폼 분리(교체식)', '시료 10×10 mm · 0.6~2 mm · 본체 두께 33 mm · 가압 모듈 옵션', '/magazine/insitu-cell-004/'),
 '005': ('<b>CIS-OM-005</b><br>극저온형', 'PEEK + 구리 · 냉각·가열 유닛 분리', '석영창 Φ10 mm · 초점거리 &lt;2 mm', '<b>−100~100℃</b> · 대기압~약한 양압', '본체 약 60×70×50 mm · 액체·폴리머 리튬전지, 전극+분리막 &lt;10×10 mm', '/magazine/insitu-cell-005/'),
}
def lineup(cur):
    out = ['<h2 style="margin-top:26px">시리즈 라인업</h2>\n    <table class="msc-tbl">\n      <thead><tr><th>모델</th><th>몸체 · 전극</th><th>관찰창 · 광학</th><th>온도 · 압력</th><th>시료 · 용도</th></tr></thead>\n      <tbody>']
    for k in ['003', '002', '004', '005']:
        n, b_, o, t, s, u = ROWS[k]
        if k == cur:
            out.append(f'        <tr class="hot"><td>{n} <span style="font-size:11px;font-weight:800;color:#0F69AF">← 이 페이지</span></td><td>{b_}</td><td>{o}</td><td>{t}</td><td>{s}</td></tr>')
        else:
            n2 = n.replace('<b>', f'<b><a href="{u}" style="color:#0F69AF">').replace('</b>', '</a></b>', 1)
            out.append(f'        <tr><td>{n2}</td><td>{b_}</td><td>{o}</td><td>{t}</td><td>{s}</td></tr>')
    out.append('      </tbody>\n    </table>')
    return '\n'.join(out)

MODELS = {
'002': dict(
 slug='insitu-cell-002', name='석영 비커형 인시츄 셀', model='CIS-OM-002',
 desc='석영 비커형 인시츄 셀 CIS-OM-002 — 석영 비커 5 mL에 순티타늄 전극을 3 mm 간격으로 고정한 입문형. 아연 대칭 전지 등 수계 전지의 덴드라이트·계면 변화를 광학현미경으로 실시간 관찰합니다. PTFE 셸·O링 밀봉.',
 ans_ko='<b>CIS-OM-002는 석영 비커에 순티타늄 전극을 3 mm 간격으로 고정한 비커형 인시츄 셀입니다.</b><br>아연 대칭 전지 등 수계 전지의 덴드라이트·계면 변화를 광학현미경으로 관찰합니다.',
 ans_en='CIS-OM-002 is a quartz-beaker in-situ cell with pure-titanium electrodes fixed at 3 mm spacing — for real-time optical observation of aqueous batteries such as symmetric zinc cells.',
 intro='<b>현미경용 인시츄 셀 시리즈(CIS-OM)</b>의 입문형입니다. 석영 비커의 투명한 측벽이 그대로 광학 경로가 되어 별도 관찰창 없이 전극을 옆에서 봅니다. 충방전 중 배터리 셀 안에서 일어나는 <b>계면의 변화(덴드라이트 등)</b>를 시각적으로 실시간 관찰하기 위해 만들어졌습니다.',
 spec=[('Model','CIS-OM-002'),('Material','Quartz (cell body) · approx. <b>5 mL</b>'),('Electrode','Pure titanium · spacing <b>3 mm</b> (fixed)'),('Shell','PTFE, sealed with O-rings'),('Optical path','Transparent quartz side wall (no separate window)'),('Application','Symmetric zinc battery and other aqueous cells')],
 feats=[('① 석영 비커 광학 경로','비커 측벽이 그대로 창이라 <b>창 정렬·밀착 작업이 없습니다</b>. 세척 후 반복 사용합니다.'),
        ('② 고정 3 mm 전극 간격','전극 간격이 셀에 고정되어 있어 <b>실험 간 재현성</b>이 확보됩니다.'),
        ('③ PTFE 셸 · O링 밀봉','전해액 증발을 막고 장시간 관찰을 지원합니다.'),
        ('④ 수계 입문용','아연 대칭 전지 등 수계 전해질은 글러브박스 없이 시작할 수 있어 <b>시리즈에서 가장 간단한 구성</b>입니다. 리튬(유기 전해액)은 밀봉·주액 구조를 갖춘 <a href="/magazine/insitu-li-dendrite-observation/" style="color:#0F69AF;font-weight:700">표준형 003</a>이 맞습니다.')],
 exp='아연 덴드라이트 성장·용해 관찰, 수계 전해질 첨가제 비교, 대칭셀 정전류 사이클과 전압-영상 동기 — 옆에서 보는 전극 단면 형상 변화가 그대로 기록됩니다.',
 equip=[["CIS-OM-002 관찰 셀","석영 비커 5 mL · Ti 전극 3 mm 간격"],["덴드라이트 관찰 전용 현미경","대물 5~100× 5종 · 인시츄 배터리 클램프 스테이지 · U820 카메라"],["포텐시오스탯·사이클러","정전류 도금·박리, 전압 로그 기록"],["전해액·시료 준비","수계 전해질 · 아연 포일 등"]],
 faq=[('CIS-OM-002로 리튬 전지도 관찰할 수 있나요?','수계 전지용 개방-비커 구조라 유기 전해액·리튬메탈에는 권장하지 않습니다. 리튬 관찰은 밀봉·별도 주액 피팅을 갖춘 표준형 CIS-OM-003을 쓰는 것이 맞습니다.'),
      ('전극 간격을 바꿀 수 있나요?','전극 간격은 3 mm로 셀에 고정되어 있습니다. 간격이 다른 구성이 필요하면 견적 문의 시 조건을 남겨 주세요.'),
      ('어떤 현미경이 필요한가요?','비커 측벽을 옆에서 보는 구조라 일반 반사광 현미경·스테레오 현미경으로 관찰할 수 있습니다. 시리즈 공통의 덴드라이트 관찰 전용 현미경(대물 5~100×, U820 카메라)을 함께 안내합니다.')],
 tags='#아연전지 #수계전지 #덴드라이트 #인시츄셀 #비커셀',
 summary_field='#아연전지 #수계전지 #덴드라이트 #인시츄셀',
 post_sum='석영 비커 5 mL·순티타늄 전극 3 mm 간격의 입문형 인시츄 셀. 비커 측벽이 그대로 광학 경로가 되어 아연 대칭 전지 등 수계 전지의 덴드라이트·계면 변화를 글러브박스 없이 관찰한다. PTFE 셸·O링 밀봉.'),
'004': dict(
 slug='insitu-cell-004', name='고저온 인시츄 셀', model='CIS-OM-004',
 desc='고저온 인시츄 셀 CIS-OM-004 — −30~150℃를 ±1℃ 프로그램 제어하며 전지 계면을 광학현미경으로 관찰. PEEK 몸체·석영창 Φ24 mm·가스 퍼지·온라인 주액, 냉각·가열 플랫폼 분리 교체식. 가압 전고체 모듈(최대 6 MPa) 옵션.',
 ans_ko='<b>CIS-OM-004는 −30~150℃를 프로그램 제어하며 전지 계면을 관찰하는 고저온 인시츄 셀입니다.</b><br>온도별 덴드라이트·계면 거동을 ±1℃ 정밀도로 한 셀에서 측정합니다.',
 ans_en='CIS-OM-004 is a high/low-temperature in-situ cell for observing battery interfaces from −30 to 150 ℃ with ±1 ℃ programmable control.',
 intro='<b>현미경용 인시츄 셀 시리즈(CIS-OM)</b>의 온도 제어형입니다. 표준형 003의 관찰 골격(석영창·주액 피팅·가스 퍼지)에 <b>−30~150℃ 프로그램 온도 제어</b>를 더해, 저온 충전 덴드라이트부터 고온 계면 열화까지 온도 축에서 관찰합니다.',
 spec=[('Model','CIS-OM-004 High and Low Temperature Microscopic Observation Cell'),('Body · Electrode','PEEK body · standard <b>glassy carbon (GC)</b> electrode'),('Window','Quartz Φ24 mm · min working distance 1 mm'),('Liquid · Gas','Gas purge + online liquid addition'),('Temperature','<b>−30 to 150 ℃</b> · ±1 ℃ programmable'),('Platform','Independent cooling / heating platforms (swapped in use; sealing unaffected)'),('Sample','10×10 mm rectangle · thickness 0.6–2 mm · body thickness 33 mm'),('Option','Pressurized solid-state module, max 6 MPa (60 kg) · higher customizable')],
 feats=[('① −30~150℃ · ±1℃ 프로그램','저온 도금(저온 충전 덴드라이트)부터 고온 가속 열화까지 <b>온도 스케줄을 걸어 두고 관찰</b>합니다.'),
        ('② 냉각·가열 플랫폼 분리','저온용·고온용 플랫폼이 분리된 교체식입니다. 교체는 <b>관찰 셀의 밀봉과 무관</b>해 시료를 유지한 채 온도 영역을 바꿉니다.'),
        ('③ 표준형과 같은 관찰 골격','석영창 Φ24 mm·최소 작동거리 1 mm·별도 주액 피팅·가스 퍼지 — <a href="/magazine/insitu-li-dendrite-observation/" style="color:#0F69AF;font-weight:700">003편</a>의 기포 제거·현미경 호환 방법이 그대로 적용됩니다.'),
        ('④ 가압 전고체 모듈 옵션','최대 6 MPa(60 kg) 정압 모듈로 온도×압력 조건의 전고체 관찰도 가능합니다.')],
 exp='저온 충전 시 리튬 도금 형상, 온도별 전해액·첨가제 성능 비교, 고온 계면 열화 진행, 온도 스케줄과 전압-영상 동기 기록.',
 equip=[["CIS-OM-004 관찰 셀","−30~150℃ ±1℃ · 석영창 Φ24 mm"],["냉각·가열 플랫폼","온도 영역별 분리 교체식"],["가압 전고체 모듈(옵션)","정압 최대 6 MPa(60 kg)"],["덴드라이트 관찰 전용 현미경","대물 5~100× 5종 · U820 카메라"],["글러브박스","Ar 분위기 조립·이송"],["포텐시오스탯·사이클러","정전류 도금·박리, 전압 로그 기록"],["튜브·밸브·주사기","주액·퍼지·기포 제거"]],
 faq=[('관찰 중에 온도를 바꿀 수 있나요?','네. −30~150℃ 범위에서 ±1℃ 정밀도의 프로그램 제어가 되므로 온도 스케줄을 걸어 두고 관찰합니다. 냉각·가열 플랫폼은 분리된 교체식이며, 교체가 관찰 셀의 밀봉에는 영향을 주지 않습니다.'),
      ('표준형 003과 무엇이 다른가요?','관찰 골격(석영창 Φ24 mm·주액 피팅·가스 퍼지·시료 10×10 mm)은 같고, 온도 제어(−30~150℃)와 기본 전극(유리질 탄소)이 다릅니다. 상온 관찰만 필요하면 003, 온도 축 실험이 필요하면 004입니다.'),
      ('전고체도 관찰할 수 있나요?','가압 전고체 모듈(최대 6 MPa, 60 kg)을 옵션으로 걸면 온도×압력 조건에서 전고체 계면(보이드·들뜸)을 관찰할 수 있습니다.')],
 tags='#고저온 #저온충전 #덴드라이트 #인시츄셀 #온도제어',
 summary_field='#리튬메탈 #저온충전 #덴드라이트 #인시츄셀',
 post_sum='−30~150℃를 ±1℃ 프로그램 제어하며 전지 계면을 관찰하는 온도 제어형 인시츄 셀. 냉각·가열 플랫폼 분리 교체식(밀봉 무관), 표준형과 같은 석영창·주액 피팅 골격, 가압 전고체 모듈(최대 6 MPa) 옵션.'),
'005': dict(
 slug='insitu-cell-005', name='극저온 인시츄 셀', model='CIS-OM-005',
 desc='극저온 인시츄 셀 CIS-OM-005 — 설계온도 −100~100℃, PEEK+구리 몸체, 석영창 Φ10 mm, 초점거리 <2 mm. 통전 상태에서 극저온 전극 표면 형상을 광학현미경으로 in-situ 관찰. 액체·폴리머 리튬전지 대응.',
 ans_ko='<b>CIS-OM-005는 −100~100℃ 극저온 영역까지 내려가는 인시츄 관찰 셀입니다.</b><br>PEEK+구리 몸체와 Φ10 mm 석영창으로 통전 상태의 전극 표면 형상을 관찰합니다.',
 ans_en='CIS-OM-005 is a cryogenic in-situ cell (−100 to 100 ℃) with a PEEK + copper body and a Φ10 mm quartz window for observing electrode surface morphology while powered.',
 intro='<b>현미경용 인시츄 셀 시리즈(CIS-OM)</b>의 극저온형입니다. 열전도가 좋은 <b>구리를 몸체에 결합</b>해 −100℃까지 내려가며, 통전 상태 그대로 전극 표면 형상 변화를 관찰합니다.',
 spec=[('Model','CIS-OM-005'),('Design temperature','<b>−100 to 100 ℃</b> (cooling / heating are separate units)'),('Design pressure','Atmospheric · slightly positive pressure'),('Body','PEEK + copper'),('Dimensions','approx. 60 × 70 × 50 mm'),('Sample','Liquid or polymer lithium batteries · electrodes + separator &lt; 10×10 mm'),('Focal length','&lt; 2 mm'),('Window','Quartz · Φ10 mm')],
 feats=[('① −100℃ 극저온','구리 몸체의 열전도로 극저온 영역까지 안정적으로 도달합니다. 냉각·가열 유닛은 분리형입니다.'),
        ('② 통전 상태 관찰','전원을 건 상태에서 −100~100℃ 전 구간의 <b>표면 형상(morphology)</b> 변화를 기록합니다.'),
        ('③ 근접 광학','초점거리 &lt;2 mm·창 Φ10 mm — 고배율 대물로 표면을 가까이서 봅니다.'),
        ('④ 대기압~약한 양압 설계','저온에서의 결로·수분 유입을 양압으로 억제하는 설계입니다.')],
 exp='극저온 전해액 스크리닝, 저온 리튬 도금 형상 관찰, 온도 하강 중 표면 형상 변화의 연속 기록, 통전 상태의 전압-영상 동기.',
 equip=[["CIS-OM-005 관찰 셀","−100~100℃ · PEEK+구리 · 창 Φ10 mm"],["냉각·가열 유닛","분리형 온도 유닛"],["덴드라이트 관찰 전용 현미경","대물 5~100× 5종 · U820 카메라"],["글러브박스","Ar 분위기 조립·이송"],["포텐시오스탯·사이클러","정전류 도금·박리, 전압 로그 기록"],["주사기·액세서리","전해액 주입·기포 제거"]],
 faq=[('몸체에 구리를 쓰는 이유가 있나요?','열전도입니다. 극저온 유닛의 냉량을 시료까지 빠르고 균일하게 전달하기 위해 PEEK 절연 몸체에 구리를 결합했습니다.'),
      ('어떤 시료를 넣을 수 있나요?','액체 전해질 또는 폴리머 리튬전지 시료이며, 전극+분리막 기준 10×10 mm 미만입니다.'),
      ('표준형 003·고저온 004와 어떻게 고르나요?','상온 관찰은 003, −30~150℃ 프로그램 제어는 004, −100℃ 극저온 표면 관찰은 005입니다. 창 지름(Φ10 mm)과 초점거리(<2 mm)가 다르므로 보유 현미경 대물과 함께 검토하세요.')],
 tags='#극저온 #저온전해액 #덴드라이트 #인시츄셀',
 summary_field='#리튬메탈 #극저온 #덴드라이트 #인시츄셀',
 post_sum='설계온도 −100~100℃의 극저온형 인시츄 셀. PEEK+구리 몸체, 석영창 Φ10 mm·초점거리 <2 mm로 통전 상태의 전극 표면 형상을 관찰한다. 액체·폴리머 리튬전지 대응, 대기압~약한 양압 설계.'),
}

PAGE = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} {model} — In-situ Microscopic Observation System 시리즈 | 실험셋업연구소</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://rndsetup.com/magazine/{slug}/">
<meta property="og:type" content="article">
<meta property="og:title" content="{name} {model} — In-situ Microscopic Observation System 시리즈">
<meta property="og:description" content="{desc_short}">
<meta property="og:url" content="https://rndsetup.com/magazine/{slug}/">
<meta property="og:image" content="https://rndsetup.com/img/magazine/insitu-{num}-hero.jpg">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"TechArticle",
"headline":"{name} {model} — In-situ Microscopic Observation System 시리즈",
"datePublished":"2026-09-01",
"inLanguage":"ko",
"image":"https://rndsetup.com/img/magazine/insitu-{num}-hero.jpg",
"about":{{"@type":"Thing","name":"{name} {model} 인시츄 관찰 셋업","url":"https://rndsetup.com/magazine/{slug}/"}},
"author":{{"@type":"Person","@id":"https://rndsetup.com/#yhlee","name":"이영현","url":"https://rndsetup.com/about/#author","affiliation":{{"@type":"Organization","name":"실험셋업연구소"}}}},
"publisher":{{"@type":"Organization","name":"실험셋업연구소","url":"https://rndsetup.com/"}},
"mainEntityOfPage":{{"@type":"WebPage","@id":"https://rndsetup.com/magazine/{slug}/"}}}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
</script>
<link rel="stylesheet" href="/assets/site.css">
{style}
</head>
<body>
<div id="pumplab-header"></div>

<article class="sd-wrap">
  <div class="sd-crumb"><a href="/">홈</a> › <a href="/magazine/">매거진</a> › 인시츄 셀 · 시리즈</div>
  <h1>In-situ Microscopic Observation System 시리즈<br>— {name} ({model})</h1>
  <div class="sd-meta">현미경용 인시츄 셀 시리즈 · {model} 편</div>
  <div class="sd-byline" style="font-size:13px;color:#8a8f98;margin:4px 0 2px;text-align:center">실험셋업연구소 매거진 · 글 <a href="/about/#author" style="color:inherit;text-decoration:underline;text-underline-offset:2px">이영현</a> · <time datetime="2026-09-01">2026년 9월 1일</time> 발행</div>

  <div class="sd-summary">
    <h3>셋업 요약</h3>
    <div class="row"><span class="k">제품</span><span><b>{model}</b> — {name}</span></div>
    <div class="row"><span class="k">구성</span><span>관찰 셀 + 덴드라이트 관찰 전용 현미경 + 포텐시오스탯 (전압-영상 동기)</span></div>
    <div class="row"><span class="k">분야</span><span>{summary_field}</span></div>
  </div>

  <div class="sd-answer">
    {ans_ko}
    <div style="font-size:13px;color:#5a6570;margin-top:8px;line-height:1.6"><i>{ans_en}</i></div>
  </div>

  <div class="sd-body">
    <h2>{model} — {name}</h2>
    <p>{intro}</p>
    <figure style="margin:14px 0 6px">
      <img src="/img/magazine/insitu-{num}-hero.jpg" alt="{model} {name} 제품 사진" loading="lazy" style="display:block;width:100%;max-width:420px;margin:0 auto;border:1px solid var(--line);border-radius:12px;background:#fff">
    </figure>
    {dlbox}

    <h2 style="margin-top:26px">Specification</h2>
    <div style="background:#fff;border:1px solid #D8E4F2;border-radius:12px;padding:16px 18px;margin:4px 0 14px">
      <div style="display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:6px;margin-bottom:10px">
        <b style="font-size:16px;color:#2A2570">{model}</b>
        <button type="button" onclick="document.getElementById('msc-open').click()" style="background:#3B3695;color:#fff;border:none;border-radius:7px;font-size:12.5px;font-weight:700;padding:6px 13px;cursor:pointer">견적문의</button>
      </div>
      <div class="bx-spec">
{spec_rows}
      </div>
    </div>

    <h2 style="margin-top:26px">Features</h2>
{feat_rows}

    <h2 style="margin-top:26px">가능한 실험</h2>
    <p>{exp}</p>
    {scope}

    {lineup}
    {buy}
  </div>

  <h2 style="font-family:var(--serif);font-size:19px;margin:26px 0 4px;color:#3B3695">이 셋업에 필요한 장비</h2>
  <p class="msc-note">아래 사양에서 필요한 항목을 골라 바로 견적 문의할 수 있습니다.</p>
  <div class="msc-spec" id="msc-spec"></div>
  <button class="msc-cta" id="msc-open">필요한 장비 선택해 문의하기</button>

  <div class="sd-sources">
    <h4>출처·안내</h4>
    제품 사진·사양·카탈로그: Hefei In-situ Technology Co., Ltd. 공식 자료 (사용 허가).<br>
    ※ 본 페이지는 제조사 공식 자료와 실험셋업연구소의 셋업 경험을 정리한 것입니다. CIS-OM 시리즈 관찰 셀은 실험셋업연구소가 소싱·공급하고 구매·수리·국내 A/S는 실험 장비 수리 전문 업체 이머전트(Emergent co)가 맡습니다.
  </div>

  <div class="sd-tags">{tag_spans}</div>

  <div class="sd-related">
    <h3>관련 콘텐츠</h3>
    <div class="sd-rel-grid">
      <a class="sd-rc" href="/magazine/insitu-li-dendrite-observation/"><div class="cat">인시츄 셀 · 시리즈</div><div class="t">표준형 CIS-OM-003 편</div><div class="d">셀 구조·격벽·기포 제거·전고체 겸용 — 시리즈 기준편.</div></a>
      <a class="sd-rc" href="/brands/hefei/om003-microscope-cell/"><div class="cat">제품 상세</div><div class="t">CIS-OM-003 제품 페이지</div><div class="d">사양·정가·구성 옵션.</div></a>
      <a class="sd-rc" href="/brands/gaossunion/special-cell-dendrite/"><div class="cat">전기화학 · 셀</div><div class="t">C031-5 덴드라이트 관찰 셀</div><div class="d">코인셀 모사 — 사파이어 창 구성.</div></a>
    </div>
  </div>
</article>

<div id="pumplab-footer"></div>

{popup}
<script src="/assets/site.js" defer></script>
<script>
(function(){{
  var specs={equip_js};
  var spec=document.getElementById('msc-spec'),checks=document.getElementById('msc-checks');
  spec.innerHTML=specs.map(function(s,i){{return '<div class="msc-sr"><span class="msc-sn">'+(i+1)+'</span><b>'+s[0]+'</b><span class="d">'+s[1]+'</span></div>';}}).join('');
  checks.innerHTML=specs.map(function(s){{return '<label><input type="checkbox" class="msc-cb" data-name="'+s[0]+'" checked><span class="n">'+s[0]+'</span><span class="d">'+s[1]+'</span></label>';}}).join('');
  var ov=document.getElementById('msc-ov');
  var step1=document.getElementById('msc-step1'),step2=document.getElementById('msc-step2'),ok=document.getElementById('msc-ok'),sub=document.getElementById('msc-sub');
  var cbs=function(){{return Array.prototype.slice.call(document.querySelectorAll('.msc-cb'));}};
  var cnt=document.getElementById('msc-count');
  function rf(){{cnt.textContent='('+cbs().filter(function(c){{return c.checked;}}).length+')';}}
  rf();checks.addEventListener('change',rf);
  function show1(){{step1.style.display='';step2.style.display='none';ok.style.display='none';sub.textContent='1/2 · 필요한 사양을 선택하세요';}}
  function open(){{ov.classList.add('on');show1();}}
  function close(){{ov.classList.remove('on');}}
  document.getElementById('msc-open').onclick=open;
  document.getElementById('msc-close').onclick=close;
  document.getElementById('msc-cancel').onclick=close;
  ov.addEventListener('click',function(e){{if(e.target===ov)close();}});
  document.getElementById('msc-next').onclick=function(){{
    var sel=cbs().filter(function(c){{return c.checked;}}).map(function(c){{return c.getAttribute('data-name');}});
    if(sel.length===0){{alert('사양을 하나 이상 선택하세요.');return;}}
    var note=document.getElementById('msc-note').value.trim();
    document.getElementById('msc-h-eq').value=sel.join(', ');
    document.getElementById('msc-h-note').value=note;
    document.getElementById('msc-pick').innerHTML='<b>선택 장비 '+sel.length+'개</b> — '+sel.join(', ')+(note?'<br>메모: '+note.replace(/</g,'&lt;'):'');
    step1.style.display='none';step2.style.display='';ok.style.display='none';sub.textContent='2/2 · 연락처를 입력하세요';
  }};
  document.getElementById('msc-back').onclick=show1;
  step2.addEventListener('submit',function(e){{
    e.preventDefault();
    var btn=document.getElementById('msc-send');btn.disabled=true;btn.textContent='전송 중…';
    fetch('https://formspree.io/f/mnjkzppj',{{method:'POST',body:new FormData(step2),headers:{{'Accept':'application/json'}}}})
      .then(function(r){{
        if(r.ok){{
          var eq=document.getElementById('msc-h-eq').value;
          document.getElementById('msc-oklist').innerHTML='<div style="font-weight:700;margin-bottom:4px">문의한 장비</div><div>'+eq+'</div>';
          step2.style.display='none';ok.style.display='block';sub.textContent='전송 완료';step2.reset();
        }}else{{alert('전송에 실패했습니다. 잠시 후 다시 시도하거나 070-8983-2600으로 연락 주세요.');}}
      }})
      .catch(function(){{alert('전송에 실패했습니다. 네트워크를 확인하고 다시 시도해 주세요.');}})
      .finally(function(){{btn.disabled=false;btn.textContent='문의 전송';}});
  }});
}})();
</script>
{lbx}
</body>
</html>
'''

for num, m in MODELS.items():
    faq_ld = ',\n'.join('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}' % (q, a) for q, a in m['faq'])
    spec_rows = '\n'.join(f'        <span>{k}</span><span>{v}</span>' for k, v in m['spec'])
    feat_rows = '\n'.join(f'    <h3 style="font-size:16px;color:#2A2570;margin:16px 0 4px">{t}</h3>\n    <p>{b}</p>' for t, b in m['feats'])
    tag_spans = ''.join(f'<span>{t}</span>' for t in m['tags'].split())
    popup = POPUP.replace('[매거진] 장비 문의 — in-situ 리튬 덴드라이트 관찰 셋업', f'[매거진] 장비 문의 — {m["model"]} {m["name"]}')
    popup = popup.replace('매거진 · in-situ 리튬 덴드라이트 관찰 (/magazine/insitu-li-dendrite-observation/)', f'매거진 · {m["model"]} {m["name"]} (/magazine/{m["slug"]}/)')
    html = PAGE.format(num=num, slug=m['slug'], name=m['name'], model=m['model'], desc=m['desc'],
                       desc_short=m['desc'][:110], ans_ko=m['ans_ko'], ans_en=m['ans_en'], intro=m['intro'],
                       spec_rows=spec_rows, feat_rows=feat_rows, exp=m['exp'], scope=SCOPE,
                       lineup=lineup(num), buy=BUY, dlbox=DLBOX, popup=popup, lbx=LBX, style=STYLE,
                       equip_js=json.dumps(m['equip'], ensure_ascii=False), faq_ld=faq_ld,
                       tag_spans=tag_spans, summary_field=m['summary_field'])
    d = f'magazine/{m["slug"]}'
    os.makedirs(d, exist_ok=True)
    fo = open(d + '/index.html', 'w', encoding='utf-8'); fo.write(html); fo.flush(); os.fsync(fo.fileno()); fo.close()
    assert html.rstrip().endswith('</html>')
    print('생성:', m['slug'])

# 003 라인업 표 → 링크 버전으로 교체
h = base
a = h.find('<h2 style="margin-top:26px">시리즈 라인업</h2>')
b = h.find('</table>', a) + 8
assert a > 0
h = h[:a] + lineup('003') + h[b:]
fo = open(BASE, 'w', encoding='utf-8'); fo.write(h); fo.flush(); os.fsync(fo.fileno()); fo.close()
print('003 라인업 링크화')

# posts.json 등록
d = json.load(open('_build/posts.json', encoding='utf-8'))
for num, m in MODELS.items():
    if not any(x.get('slug') == m['slug'] for x in d['posts']):
        d['posts'].insert(0, {"type": "magazine", "slug": m['slug'],
            "title": f"{m['name']} {m['model']} — In-situ Microscopic Observation System 시리즈",
            "summary": m['post_sum'], "date": "2026-09-01",
            "tags": ["인시츄 셀", "덴드라이트", m['model']],
            "url": f"/magazine/{m['slug']}/",
            "model_focus": f"{m['model']} 인시츄 관찰 셀", "application": "인시츄 셀 · 시리즈",
            "image": f"/img/magazine/insitu-{num}-hero.jpg"})
json.dump(d, open('_build/posts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('posts.json:', len(d['posts']), '건')
