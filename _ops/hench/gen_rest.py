# -*- coding: utf-8 -*-
"""Hench 나머지 102종 생성 + 전체 허브(119장). 수치는 hench_products.csv 에서만 읽는다."""
import os, sys, re, json, io, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hench_common as H
import gen_models as G
import fam as F

MPA = 700.0
def U(v): return G.U(v)

# ── 스펙 라벨 한글화 ─────────────────────────────────────────────
KO = {
 'instrument model':'모델','model':'모델','product name':'제품명',
 'pressure range':'압력범위','pressure limit':'압력범위','maximum pressure':'최대 성형압',
 'accuracy range':'설정 분해능','pressure conversion':'압력 환산',
 'pressure gauge':'압력 표시','pressure gage':'압력 표시','pressure display':'압력 표시',
 'pressure stability':'압력 안정도','pressure mode':'가압 방식','pressure die':'가압 방식',
 'press process':'가압 방식','pressure holding time':'압력 유지','pressure holding':'압력 유지',
 'demoulding pressure':'탈형 압력','sealing pressure':'실링 압력','opening pressure':'분해 압력',
 'sealing die':'실링 다이','disconnecting die':'분해 다이',
 'cylinder diameter':'실린더 지름','piston diameter':'피스톤 지름',
 'cylinder stroke':'실린더 스트로크','piston stroke':'피스톤 스트로크',
 'travel ofpiston':'피스톤 스트로크','travel of piston':'피스톤 스트로크','max. piston stroke':'피스톤 스트로크',
 'table diameter':'압반 지름','working table diameter':'압반 지름',
 'number of columns':'컬럼 수','columns':'컬럼 수','column spacing':'컬럼 간격',
 'valid space':'유효공간','available space':'유효공간','effective space':'유효공간',
 'work space':'유효공간','working space':'유효공간',
 'chamber size':'챔버 크기','cavity material':'캐비티 재질','ambient temperature':'사용 환경온도',
 'heating range':'가열 범위','heating temperature':'가열 온도','heating plate type':'열판 구조',
 'heating core material':'발열체','heat insulation method':'단열','cooling method':'냉각',
 'temperature control accuracy':'온도 정밀도','dies heating temperature':'다이 가열온도',
 'temperature control by thermostat':'온도 제어',
 'pressure and temperature control accuracy':'압력·온도 정밀도',
 'intelligent temperature controller temperature range':'온도 컨트롤러 범위',
 'automatic control':'자동 제어','aftercompaction way':'가압 후 보정','after compaction way':'가압 후 보정',
 'screen display':'화면','display mode':'화면','display die':'화면','setting method':'설정 방식',
 'passive safety':'안전장치','safety configuration':'안전장치','safety protection':'안전장치',
 'power supply':'전원','device power supply':'전원','equipment power':'소비전력','voltage':'전원',
 'dimensions':'외형','size':'외형','machine size':'외형','host size':'본체 외형','controller size':'컨트롤러 외형',
 'weight':'무게','equipment weight':'무게','net weight':'무게',
 'overall structure':'구조','design structure':'구조','construction':'구조',
 'configuration description':'구성 안내','note':'비고','remark':'비고',
 'material':'재질','indenter hardness':'인덴터 경도','indenter material':'인덴터 재질',
 'sample size':'성형 규격','sample thickness':'시료 두께','cavity depth':'캐비티 깊이',
 'die size':'다이 크기','die material':'다이 재질','mold specifications':'몰드 규격',
 'mold material':'몰드 재질','mould material':'몰드 재질','shelf material':'프레임 재질',
 'insulating material':'절연재','punch material':'펀치 재질','base material':'베이스 재질',
 'punching pressure':'펀칭 하중','punch stroke':'펀치 스트로크','receiving box':'수집함',
 'slice size':'슬라이스 규격','suitable material':'적용 시료','standard tool head':'기본 툴헤드',
 'applicable model':'적용 모델','applicable mold':'적용 몰드','control mode':'제어 방식',
 'operation mode':'운전 방식','motor power':'모터 출력','precision':'정밀도','accuracy':'정밀도',
 'diameter':'지름','temperature':'온도','frequency':'주파수','surface treatment':'표면처리',
 'boundary dimension':'외형','device power':'소비전력','holding time':'압력 유지',
 'pressure process':'가압 단계','number of pressurized sections':'가압 구간 수',
 'active safety':'능동 안전','equipment safety':'안전장치','safety performance':'안전장치',
 'limit function':'리미트','limit protection':'리미트 보호','cylinder limit protection':'실린더 리미트 보호',
 'host protection':'본체 보호','equipment protection':'장비 보호','device display':'화면',
 'pressure relief die':'감압 방식','release die':'감압 방식','return mode':'복귀 방식',
 'pressure sensor':'압력 센서','pressure unit':'압력 단위','intelligent operation':'지능형 운전',
 'data management':'데이터 관리','operation record':'운전 기록',
 'supplementary pressure setting':'보압 설정','configuration instructions':'구성 안내',
}

# ── 영문 값 한글화 (긴 것부터) ───────────────────────────────
TR = [
 ('Japan High Speed Tool Steel','일본산 고속도 공구강'),
 ('Alloy tool steel','합금공구강'), ('Hard Alloy','초경합금'),
 ('3 chromium 13# die steel','3Cr13 다이스강'), ('die steel','다이스강'),
 ('Stainless steel','스테인리스'), ('anti-static ABS material','정전기 방지 ABS'),
 ('lithium positive or negative electrode sheet, diaphragm sheet','리튬 양극·음극 시트, 분리막'),
 ('forging process, integrated structure','단조 가공 일체형 구조'),
 ('forging process','단조 가공'), ('integrated structure','일체형 구조'),
 ('manual hydraulic system','수동 유압'), ('wear-resistant hydraulic oil','내마모 유압유'),
 ('equipped with','포함'),
 ('pressure tonnage (T), pressure Mpa double scale display','톤(T)·MPa 이중 눈금'),
 ('DDNT high precision digital sensor display','DDNT 고정밀 디지털 센서 표시'),
 ('tonnage display','톤(T) 표시'),
 ('electric PCB program buffer pressurization','전동 PCB 프로그램 완충 가압'),
 ('Electric PCB program buffer pressurization','전동 PCB 프로그램 완충 가압'),
 ('program automatic pressure','프로그램 자동 가압'),
 ('Real-time automatic pressure compensation','실시간 자동 압력 보정'),
 ('automatic pressure relief when the cylinder exceeds the limit','실린더 리미트 초과 시 자동 감압'),
 ('unlimited time (manual pressure relief)','시간 제한 없음 (수동 감압)'),
 ('unlimited time','시간 제한 없음'),
 ('Touch screen operation is convenient and fast','터치스크린 조작'),
 ('Touch directly modify the set value','터치로 설정값 직접 수정'),
 ('inch LCD touch screen/English interface can be switched','인치 LCD 터치스크린 (영문 인터페이스 전환)'),
 ('inch touch LCD screen/English interface can be switched','인치 LCD 터치스크린 (영문 인터페이스 전환)'),
 ('inch capacitive touch LCD screen','인치 정전식 LCD 터치스크린'),
 ('leakage protection','누전 차단'), ('emergency stop switch','비상정지 스위치'),
 ('plexiglass','아크릴 보호커버'), ('protective cover','보호커버'),
 ('four-column positioning insulation design','4컬럼 정렬 단열 설계'),
 ('upper and lower heating','상·하 가열'), ('Copper heating core','구리 발열체'),
 ('imported mica heat insulation board','마이카 단열판'), ('standard water cooler','표준 수냉 칠러'),
 ('The whole form structure, no pressure and no oil leakage','일체형 구조 · 무누유'),
 ('no pressure and no oil leakage','무누유'),
 ('can be customized to set the accuracy','정밀도 맞춤 설정 가능'),
 ('can be customized','맞춤 제작 가능'), ('customizable','맞춤 제작 가능'),
 ('can be selected within the pressure range','압력 범위 내에서 선택 가능'),
 ('and various types of round, square, shaped, battery molds','원형·사각·이형·버튼셀 몰드'),
 ('According to customer needs, the column can be increased','요청 시 컬럼 증설 가능'),
 ('side opening','측면 개방'), ('optional','옵션'), ('Customized','맞춤'),
 ('historical operation records','운전 이력 기록'), ('can store','저장 가능'),
 ('roots','본'), ('Max:','최대 '), ('Room temperature','상온'),
 ('Equipped with','포함'), ('quenched','담금질'), ('diameter','지름'), ('Die size','다이 크기'),
 ('room temperature','상온'), ('adjustable continuous','단 연속 조절'),
 ('mechanical failure error emergency stop function','기계 고장·비상정지 기능'),
 ('mechanical fault report emergency stop function','기계 고장 보고·비상정지 기능'),
 ('automatic precise pressure replenishment','자동 정밀 보압'),
]

def tr(v):
    for a, b in TR:
        if a in v: v = v.replace(a, b)
    v = v.replace('：', ' ')
    v = re.sub(r'\s{2,}', ' ', v).strip(' ,·')
    return v


def eng_words(v):
    return len(re.findall(r'[A-Za-z]{4,}', v))
# 표에서 뺄 항목(장황하거나 카드에 무의미)
DROP = {'구성 안내', '비고', '지능형 운전', '데이터 관리', '운전 기록', '장비 보호', '본체 보호'}
# 앞쪽에 오길 원하는 순서
ORDER = ['모델','압력범위','최대 성형압','설정 분해능','압력 환산','실린더 지름','피스톤 지름',
 '피스톤 스트로크','실린더 스트로크','압력 안정도','가압 방식','가압 후 보정','압력 유지','자동 제어',
 '성형 규격','재질','인덴터 경도','인덴터 재질','캐비티 깊이','시료 두께','다이 크기','몰드 규격',
 '가열 범위','온도 정밀도','압력·온도 정밀도','열판 구조','발열체','단열','냉각',
 '챔버 크기','캐비티 재질','실링 압력','분해 압력','실링 다이','분해 다이',
 '펀칭 하중','펀치 스트로크','슬라이스 규격','적용 시료','기본 툴헤드','수집함',
 '압반 지름','컬럼 수','컬럼 간격','유효공간','화면','설정 방식','안전장치',
 '전원','소비전력','사용 환경온도','구조','외형','본체 외형','컨트롤러 외형','무게']

def spec_rows(r, extra=()):
    sp = json.loads(r['spec'])
    out = {}
    for k, v in sp.items():
        ko = KO.get(k.strip().lower())
        if not ko or ko in DROP: continue
        v = tr(U(v))
        # 번역되지 않은 영문 서술은 사양표에 싣지 않는다(수치 자리이지 마케팅 문장 자리가 아니다)
        if eng_words(v) >= 4: continue
        if len(v) > 110: v = v[:107] + '…'
        out.setdefault(ko, v)
    rows = [(k, out[k]) for k in ORDER if k in out]
    rows += [(k, v) for k, v in out.items() if k not in ORDER]
    return rows + list(extra)

def g(r, *keys, **kw):
    sp = json.loads(r['spec'])
    for k in keys:
        for x in sp:
            if x.strip().lower() == k.lower():
                v = tr(U(re.sub(r'\s+', ' ', sp[x]).strip()))
                if v: return v
    return kw.get('d', '—')

def ton_of(r):
    m = re.match(r'(\d+(?:\.\d+)?)\s*T', r['name'])
    if m: return float(m.group(1))
    v = g(r, 'Pressure range', 'Pressure limit', 'Pressure')
    n = re.findall(r'(\d+(?:\.\d+)?)\s*T', v)
    return float(n[-1]) if n else 0.0

def dias(r):
    v = g(r, 'Sample size')
    n = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)', v)]
    return (min(n), max(n)) if n else (0.0, 0.0)

def notes_common(extra=()):
    return list(extra) + ['가격은 <b>구성별 견적(문의)</b>입니다. 제조사가 정가를 공개하지 않는 품목이라 '
                          '구성·수량을 확인한 뒤 안내드립니다. 부가세 별도, 해외 발주 제품으로 해외배송비가 주문당 1회 더해집니다.']


# ══════════════ 군별 설정 ══════════════
CFG = {
 'P1-manual': dict(kind='press', crumb='수동 유압 펠릿 프레스', sub='pellet',
   nm='수동 유압 펠릿 프레스',
   ans='레버로 유압을 올려 분말을 펠릿으로 성형하는 프레스입니다. 전원이 필요 없고 구조가 단순해 고장 요소가 적습니다.',
   why='레버 펌핑으로 유압을 만듭니다. 전원·배관이 없어 설치가 자유롭고, <b>일체형 단조 프레임</b>이라 반복 가압에서 압력 강하와 누유가 적습니다.'),
 'D1-cylindrical': dict(kind='die', crumb='원통형 펠릿 다이', sub='die',
   nm='원통형 펠릿 다이',
   ans='원판형 펠릿을 만드는 표준 성형 다이입니다. IR·XRD 시료 조제에 가장 널리 쓰이는 형상입니다.',
   why='캐비티·인덴터·베이스의 3피스 구조로, 눌러 성형한 뒤 인덴터로 밀어 탈형합니다. <b>지름 밴드별로 캐비티 깊이와 외경이 달라</b> 시료량에 맞춰 고릅니다.'),
 'P9-vacuum': dict(kind='press', crumb='진공 자동 열압기', sub='pellet',
   nm='진공 자동 열압기',
   ans='챔버를 진공으로 뽑은 상태에서 가열·가압하는 자동 열압기입니다. 대기 접촉이 문제되는 시료에 씁니다.',
   why='가열 가압을 <b>진공 챔버 안에서</b> 수행합니다. 대기 중 산화·수분 흡착이 문제되는 소재나 기공을 줄여야 하는 소결·접합 공정에 필요합니다.'),
 'P2-digital': dict(kind='press', crumb='디지털 수동 유압 펠릿 프레스', sub='pellet',
   nm='디지털 수동 유압 펠릿 프레스',
   ans='레버로 가압하되 압력을 디지털 게이지로 읽는 펠릿 프레스입니다. 지침식보다 판독 오차가 작아 성형압 재현이 쉽습니다.',
   why='수동 유압 구조는 같고 <b>압력 표시가 디지털</b>입니다. 눈금 사이를 읽어 어림하던 지침식과 달리 수치가 그대로 찍혀, 같은 성형압을 반복할 때 유리합니다.'),
 'P3-electric': dict(kind='press', crumb='전동 유압 펠릿 프레스', sub='pellet',
   nm='전동 유압 펠릿 프레스',
   ans='모터 유압으로 가압하는 펠릿 프레스입니다. 레버를 젓지 않아도 되고 설정 압력까지 자동으로 올라갑니다.',
   why='레버 펌핑이 없습니다. <b>PCB 프로그램 완충 가압</b>으로 설정값까지 올린 뒤, 가압 후 압력이 떨어지면 <b>실시간 자동 보정</b>합니다. 반복 작업량이 많을 때 손이 덜 갑니다.'),
 'P4-auto': dict(kind='press', crumb='자동 유압 펠릿 프레스', sub='pellet',
   nm='자동 유압 펠릿 프레스',
   ans='가압·유지·탈형을 프로그램으로 돌리는 자동 펠릿 프레스입니다. 터치 화면에서 압력과 유지 시간을 설정합니다.',
   why='가압 → 유지 → 감압을 <b>프로그램이 순서대로</b> 수행합니다. 작업자가 붙어 있지 않아도 되고, 같은 조건을 그대로 다시 불러 쓸 수 있습니다.'),
 'P5-isostatic': dict(kind='press', crumb='등온압축(Isostatic) 펠릿 프레스', sub='pellet',
   nm='등온압축 펠릿 프레스',
   ans='시료를 유체로 감싸 사방에서 균일하게 누르는 등온압축 프레스입니다. 밀도 편차가 작은 성형체를 만듭니다.',
   why='단축 프레스는 위아래로만 눌러 시료 안에 밀도 구배가 생깁니다. 등온압축은 <b>압력 매체가 시료를 전방향으로 균일하게</b> 눌러 밀도 편차를 줄입니다. 세라믹·고체전해질처럼 소결 후 변형이 문제되는 시료에 씁니다.'),
 'P6-hot': dict(kind='press', crumb='가열(Hot) 펠릿 프레스', sub='pellet',
   nm='가열 펠릿 프레스',
   ans='열판으로 다이를 데우면서 동시에 가압하는 프레스입니다. 상온에서 안 눌리는 고분자·복합재 시료에 씁니다.',
   why='열판이 다이를 데운 상태로 가압합니다. 상온 성형이 안 되는 <b>고분자 필름·복합재·박막</b>에서 온도와 압력을 함께 걸어야 할 때 필요합니다.'),
 'P7-fluoro': dict(kind='press', crumb='형광분석(XRF) 전용 자동 펠릿 프레스', sub='pellet',
   nm='형광분석 전용 자동 펠릿 프레스',
   ans='XRF 시료컵 규격에 맞춰 펠릿을 찍는 자동 프레스입니다. 압력·유지·탈형이 프로그램으로 돌아갑니다.',
   why='XRF는 시료 표면 상태가 결과를 좌우합니다. 이 계열은 <b>형광분석용 몰드 규격(40–32 mm 등)에 맞춰</b> 자동 가압·탈형까지 프로그램으로 처리해 표면 재현성을 확보합니다.'),
 'P8-cellseal': dict(kind='press', crumb='버튼셀 실링기', sub='pellet',
   nm='버튼셀 전지 실링기',
   ans='코인셀 케이스를 눌러 밀봉하는 전용 유압 실링기입니다. 분해용 다이로 되열 수도 있습니다.',
   why='코인셀 조립의 마지막 공정 전용기입니다. <b>실링 다이로 밀봉</b>하고 <b>분해 다이로 되열</b> 수 있어, 셀 재사용·사후 분석까지 한 대로 처리합니다.'),
 'D2-opening': dict(kind='die', crumb='개구형(Opening) 펠릿 다이', sub='die',
   nm='개구형 펠릿 다이',
   ans='몸통이 열리는 구조의 성형 다이입니다. 눌러 빼지 않고 옆으로 열어 꺼내 펠릿 파손이 적습니다.',
   why='일반 다이는 인덴터로 밀어내며 탈형해 얇거나 무른 펠릿이 깨집니다. 개구형은 <b>몸통을 열어 그대로 꺼내</b>므로 탈형 파손이 줄어듭니다.'),
 'D3-square': dict(kind='die', crumb='사각 펠릿 다이', sub='die',
   nm='사각 펠릿 다이',
   ans='정사각 단면 시료를 만드는 성형 다이입니다. 굽힘·인장 시험편처럼 각진 형상이 필요할 때 씁니다.',
   why='원형이 아닌 <b>정사각 단면</b>을 만듭니다. 기계 물성 시험편, 사각 홀더용 시료처럼 형상이 정해진 경우에 씁니다.'),
 'D4-special': dict(kind='die', crumb='특수 형상 펠릿 다이', sub='die',
   nm='특수 형상 펠릿 다이',
   ans='링·구형·다각형 등 특수 형상 성형 다이입니다. 표준 원판으로 안 되는 시료 형상에 대응합니다.',
   why='표준 원판 펠릿으로 해결되지 않는 형상 전용입니다. 형상별로 캐비티와 인덴터가 따로 설계됩니다.'),
 'D5-carbide': dict(kind='die', crumb='초경합금 펠릿 다이', sub='die',
   nm='초경합금 펠릿 다이',
   ans='초경합금(YT15)으로 만든 고경도 성형 다이입니다. 경도 HRC85~90으로 마모와 변형에 훨씬 강합니다.',
   why='재질이 <b>초경합금 YT15</b>, 경도 <b>HRC85~90</b>입니다. 공구강 다이(HRC60~70)보다 훨씬 단단해 고압 반복 사용과 경질 분말에서 캐비티 마모가 적습니다.'),
 'D6-hotdie': dict(kind='die', crumb='가열 펠릿 다이', sub='die',
   nm='가열 펠릿 다이',
   ans='다이 자체를 가열해 시료를 데우면서 성형하는 다이입니다. 가열 프레스와 함께 씁니다.',
   why='다이에 열원이 들어 있어 <b>시료를 데운 상태로 성형</b>합니다. 상온에서 성형되지 않는 고분자·필름 시료에 필요합니다.'),
 'D7-cellmold': dict(kind='die', crumb='버튼셀·전고체 전지 몰드', sub='pellet',
   nm='버튼셀 전지 몰드',
   ans='코인셀 실링·분해와 전고체 전지 가압 평가에 쓰는 전용 몰드입니다.',
   why='전지 조립·평가 전용 몰드입니다. 실링/분해용과, 전고체 전지처럼 <b>가압 상태를 유지한 채 측정</b>해야 하는 용도가 나뉩니다.'),
 'D8-fluorodie': dict(kind='die', crumb='형광분석(XRF)용 펠릿 다이', sub='die',
   nm='형광분석용 펠릿 다이',
   ans='XRF 시료 성형 전용 다이입니다. 붕산 링·스틸 링으로 시료 가장자리를 잡아 줍니다.',
   why='XRF는 시료가 커서 그대로 누르면 가장자리가 무너집니다. <b>붕산 또는 스틸 링으로 테두리를 지지</b>해 평탄한 분석면을 만듭니다.'),
}


def M(o):
    """화면 표기용 모델코드. 제조사가 2열 표를 한 칸에 붙였거나 값이 삼켜진 경우를 정리한다."""
    m = (o['model'] or '').strip()
    lead = re.match(r'([A-Z]{2,4}-\d{2,4}[A-Z]?)\s', o['name'] or '')
    if lead: return lead.group(1)                       # 이름이 모델로 시작하면 그게 정답
    if ' ' in m: m = m.split(' ')[0]                     # 'HMN-C Dual-purpose…' → HMN-C
    return m[:24]


BYFAM = collections.defaultdict(list)
for _o in F.out: BYFAM[_o['fam']].append(_o)

def variant(name):
    v = []
    if 'Protection' in name: v.append('보호커버')
    if '4 Columns' in name or '4 columns' in name.lower(): v.append('4컬럼')
    m = re.search(r'(\d{3})\s*°?[C℃]', name)
    if m: v.append('%s℃' % m.group(1))
    if 'Split' in name: v.append('분할형')
    if 'Double Hot Plates' in name: v.append('양면 열판')
    if 'Manual' in name and 'Split' in name: v.append('수동')
    if 'Electric' in name and 'Split' in name: v.append('전동')
    return ' · '.join(dict.fromkeys(v))

def head_bits(o, cfg, tail_txt):
    name, r = o['name'], o['row']
    vr = variant(name)
    h1 = '%s %s' % (M(o), cfg['nm'])
    t = ton_of(r)
    if t: h1 += ' %g T' % t
    if vr: h1 += ' (%s)' % vr
    return h1, vr, t

def xlinks_of(o, limit=8):
    sib = [x for x in BYFAM[o['fam']] if x['slug'] != o['slug']]
    return [('/brands/hench/%s/' % x['slug'],
             '%s%s' % (x['model'], (' %g T' % ton_of(x['row'])) if ton_of(x['row']) else '')) for x in sib[:limit]]

def common(o, cfg, h1, ans, summ, spec, feats, faqs, incl, warn, models, opt='', figs=()):
    slug = o['slug']; img = '/img/hench/%s-1.jpg' % slug; M2 = M(o)
    kwsub = cfg['crumb'].replace(' ', '')
    return dict(models=models, slug=slug, crumb=cfg['crumb'],
      title='Hench %s — %s | 실험셋업연구소' % (h1, cfg['crumb']),
      desc=re.sub(r'<[^>]+>', '', '%s — %s %s' % (h1, summ, ans))[:155],
      h1=h1, ans=ans, summ=summ, quote='Hench %s' % h1,
      kws=[('/product/', '#실험장비카탈로그'), ('/brands/hench/%s/' % slug, '#%s' % kwsub),
           ('/brands/hench/%s/' % slug, '#시료전처리'), ('/brands/hench/%s/' % slug, '#Hench')],
      img=img,
      thumbs=[(t, M2, lb) for t, lb in
              [(img, '제품'), ('/img/hench/%s-2.jpg' % slug, '상세'), ('/img/hench/%s-3.jpg' % slug, '구성')]
              if os.path.exists(os.path.join(H.ROOT, t.lstrip('/')))],
      feats=feats, incl=incl, spec=spec, opt_tbl=opt, figures=list(figs),
      price='<b>구성별 견적(문의)</b>입니다. 구성·수량·다이 규격을 알려주시면 함께 잡아 견적해 드립니다.',
      notes=notes_common(), warn_h=warn[0], warn_p=warn[1],
      xlinks=xlinks_of(o), faqs=faqs,
      ld={"@context":"https://schema.org","@type":"Product","name":h1,
          "brand":{"@type":"Brand","name":"Hench","alternateName":["HENCH","天津恒创立达"]},
          "category":"시료 전처리 · %s" % cfg['crumb'],
          "url":'https://rndsetup.com/brands/hench/%s/' % slug,
          "image":'https://rndsetup.com' + img, "model":M(o)})

def press_page(o):
    cfg = CFG[o['fam']]; r = o['row']
    h1, vr, t = head_bits(o, cfg, '')
    cyl = g(r,'Cylinder diameter','Piston diameter'); stab = g(r,'Pressure stability')
    space = g(r,'Effective space','Valid space','Available space','Work space')
    dim = g(r,'Dimensions','Size','Machine size'); wt = g(r,'Weight','Equipment weight')
    pwr = g(r,'Power supply','Device power supply'); heat = g(r,'Heating range','Heating temperature')
    dmax = H.max_dia(t, MPA) if t else 0
    summ = ' · '.join(x for x in [
        ('최대하중 <b>%g T</b>' % t) if t else '', ('실린더 %s' % cyl) if cyl!='—' else '',
        ('가열 %s' % heat) if heat!='—' else '', ('유효공간 %s' % space) if space!='—' else '',
        ('전원 %s' % pwr) if pwr!='—' else '', ('무게 %s' % wt) if wt!='—' else ''] if x)
    feats = [cfg['why']]
    if t: feats.append('<b>최대하중 %g T</b> — 성형압 700 MPa 기준으로 지름 <b>Φ%.1f mm</b>까지 낼 수 있습니다. IR 표준 Φ13 mm에는 약 9.5 T가 필요합니다.' % (t, dmax))
    if stab!='—': feats.append('<b>압력 안정도 %s</b> — 유지 구간에서 압력 강하가 작아 성형 조건을 재현하기 쉽습니다.' % stab)
    if heat!='—': feats.append('<b>가열 범위 %s</b> — 온도와 압력을 동시에 걸어야 하는 시료에 대응합니다.' % heat)
    if space!='—': feats.append('<b>유효공간 %s</b> — 다이 높이와 부속을 감안해 확인하십시오.' % space)
    if pwr!='—': feats.append('<b>전원 %s</b> — 국내 설치 시 전원 사양을 반드시 확인해 주십시오.' % pwr)
    feats.append('<b>다이 별매</b> — 목표 펠릿 규격에 맞는 다이를 함께 고르셔야 합니다.')
    incl = [('본체 1대','in','포함'), ('다이(몰드) — 규격에 맞춰 별도 선택','ex','미포함·별매'),
            ('사진 속 다이·시료는 연출용','ex','미포함')]
    faqs = [('계열', '%s는 어떤 프레스인가요?' % M(o), cfg['why'])]
    if t:
        faqs.append(('톤수 선택','이 모델로 만들 수 있는 펠릿 지름은 어디까지인가요?',
          '성형압 700 MPa 기준 최대 <b>Φ%.1f mm</b>입니다. 표준인 Φ13 mm(132.7 mm²)에는 약 <b>9.5 T</b>가 필요하므로 %s'
          % (dmax, '이 모델로 여유가 있습니다.' if t>=11 else '이 모델로는 부족합니다 — 상위 톤수를 권합니다.')))
        faqs.append(('압력 환산','최대하중을 Φ13 mm 다이에 걸면 시료 압력은?',
          '%g T = %.1f kN을 132.7 mm²에 걸면 <b>약 %.0f MPa</b>입니다. KBr 표준(700 MPa) 대비 %s'
          % (t, t*9.80665, H.sample_mpa(t,13), ('%.1f배로 여유가 큽니다.' % (H.sample_mpa(t,13)/700)) if H.sample_mpa(t,13)>700 else '못 미치므로 더 작은 직경을 쓰십시오.')))
    if stab!='—': faqs.append(('운용','압력 유지는 얼마나 되나요?','압력 안정도 사양이 <b>%s</b>입니다. 수 분 단위 유지 공정에서는 압력 강하가 사실상 무시할 수준입니다.' % stab))
    if pwr!='—': faqs.append(('설치','전원은 어떻게 되나요?','제조사 표기는 <b>%s</b>입니다. 국내 220 V 환경과 맞는지, 커스텀 전압이 필요한지 주문 전 확인해 드립니다.' % pwr))
    if heat!='—': faqs.append(('가열','승온과 온도 제어는 어떻게 되나요?','가열 범위는 <b>%s</b>이고 온도 정밀도는 <b>%s</b>입니다. 다이와 열판 규격은 사양표를 확인하십시오.' % (heat, g(r,'Temperature control accuracy','Pressure and temperature control accuracy'))))
    faqs.append(('구성','다이가 포함되나요?','포함되지 않습니다(별매). 목표 펠릿 규격을 알려주시면 <a href="/brands/hench/cylindrical-die-hmy-11-14/">원통형 다이</a> 등에서 함께 구성해 드립니다.'))
    faqs.append(('가격','가격이 왜 문의인가요?','제조사가 정가를 공개하지 않는 품목이라 구성·수량을 확인한 뒤 안내드립니다. 부가세 별도이며 해외 발주라 해외배송비가 주문당 1회 더해집니다.'))
    warn = ('안전 — 허용 하중과 전원을 확인하십시오',
      '다이의 허용 하중을 넘겨 가압하지 마십시오. 압력 해제는 단계적으로 진행하고, 성형 중에는 다이 정면에 서지 마십시오.'
      + (' 가열 계열은 열판·다이가 고온이므로 냉각 전 접촉을 피하십시오.' if heat!='—' else ''))
    models = [{"m": M(o), "s": summ.replace('<b>','').replace('</b>','')[:70]}]
    return common(o, cfg, h1, cfg['ans'], summ, spec_rows(r), feats, faqs, incl, warn, models)

def die_page(o):
    cfg = CFG[o['fam']]; r = o['row']
    ss = g(r,'Sample size'); mat = g(r,'Material'); hard = g(r,'Indenter hardness')
    dep = g(r,'Cavity depth'); dim = g(r,'Dimensions'); wt = g(r,'Weight')
    h1 = '%s %s' % (M(o), cfg['nm'])
    band = re.sub(r'\s*\(.*$','', ss) if ss!='—' else ''
    if band: h1 += ' %s' % band[:26]
    dmin, dmax = dias(r)
    summ = ' · '.join(x for x in [('성형 규격 <b>%s</b>' % ss) if ss!='—' else '',
        ('재질 %s' % mat) if mat!='—' else '', ('경도 <b>%s</b>' % hard) if hard!='—' else '',
        ('캐비티 깊이 %s' % dep) if dep!='—' else '', ('외형 %s' % dim) if dim!='—' else '',
        ('무게 %s' % wt) if wt!='—' else ''] if x)
    feats = [cfg['why']]
    if mat!='—': feats.append('<b>재질 %s</b> — 열처리 후 치수 안정성이 높아 캐비티와 인덴터의 클리어런스가 유지됩니다.' % mat)
    if hard!='—': feats.append('<b>인덴터 경도 %s</b> — 고압 성형에서도 인덴터 단면이 눌리지 않아 펠릿 표면이 평활합니다.' % hard)
    if dep!='—': feats.append('<b>캐비티 깊이 %s</b> — 분말 충전량 여유를 보고 고르십시오.' % dep)
    feats.append('<b>표준 유압 프레스 호환</b> — <a href="/brands/hench/pellet-press-yp-15/">YP 시리즈</a> 등에 올려 씁니다. 프레스는 별매입니다.')
    incl = [('다이 본체 1세트 (캐비티 · 인덴터 · 받침)','in','포함'), ('프레스 본체 — 별도 선택','ex','미포함·별매')]
    faqs = [('계열','%s는 어떤 다이인가요?' % M(o), cfg['why'])]
    if ss!='—': faqs.append(('규격','성형 규격이 어떻게 되나요?','<b>%s</b>입니다. 캐비티 깊이 %s, 외형 %s, 무게 %s.' % (ss, dep, dim, wt)))
    if dmax: faqs.append(('프레스 호환','몇 톤짜리 프레스가 필요한가요?',
        '성형압 700 MPa 기준으로 최대 규격 %g mm에 <b>약 %.1f T</b>가 필요합니다. %s'
        % (dmax, H.need_ton(dmax, MPA), '<a href="/brands/hench/pellet-press-yp-15/">YP-15</a>(15 T)로 소화됩니다.' if H.need_ton(dmax,MPA)<=15 else 'YP-15(15 T)로는 부족하므로 상위 톤수 프레스가 필요하거나, XRD용 저압 성형 전제로 쓰셔야 합니다.')))
    if hard!='—': faqs.append(('재질·경도','경도가 왜 중요한가요?','KBr 펠릿 성형압은 통상 0.7 GPa 이상입니다. 이 다이는 경도 <b>%s</b>라 그 압력대에서 인덴터가 영구변형되지 않습니다. Hench 다이는 밴드·계열마다 재질이 다르니 사양표를 확인하십시오.' % hard))
    faqs.append(('용도 구분','IR과 XRD 어느 쪽에 쓰나요?','둘 다 대응합니다. IR은 투광이 목적이라 고압·유지가 필요하고, XRD는 표면 평탄도가 목적이라 저압으로 충분합니다.'))
    faqs.append(('관리','청소와 보관은?','KBr은 흡습성이 강해 잔류 분말이 부식·고착의 원인이 됩니다. 사용 후 무수 알코올로 닦고 완전히 건조한 뒤 건조 보관하십시오.'))
    faqs.append(('구성','프레스가 포함되나요?','포함되지 않습니다. 다이는 단품이며 프레스는 <a href="/brands/hench/pellet-press-yp-15/">YP 시리즈</a>에서 별도로 고르십시오.'))
    faqs.append(('가격','가격이 왜 문의인가요?','제조사가 정가를 공개하지 않는 품목이라 구성·수량을 확인한 뒤 안내드립니다. 부가세 별도이며 해외 발주라 해외배송비가 주문당 1회 더해집니다.'))
    warn = ('안전 — 규격별 허용 하중이 다릅니다',
      '소구경 다이에 프레스 최대 하중을 그대로 가하면 시료면 압력이 수 GPa에 달해 인덴터·캐비티가 손상될 수 있습니다. 매 사용 후 잔류 분말을 청소하십시오.')
    models = [{"m": M(o), "s": (ss if ss!='—' else cfg['nm'])[:70]}]
    return common(o, cfg, h1, cfg['ans'], summ, spec_rows(r), feats, faqs, incl, warn, models)


SLICER = dict(kind='slicer', crumb='전극 슬라이서', sub='slicer', nm='수동 전극 슬라이서',
  ans='리튬 전극 시트와 분리막을 원판으로 타발하는 수동 슬라이서입니다. 코인셀 조립 전 단계에 씁니다.',
  why='코인셀을 만들려면 전극 시트를 정해진 지름으로 잘라야 합니다. 가위·펀치로 자르면 가장자리가 눌려 단락 원인이 되는데, 이 장비는 <b>레버 펀칭으로 깔끔한 단면</b>을 냅니다.')

def slicer_page(o):
    cfg = SLICER; r = o['row']
    h1 = '%s 수동 전극 슬라이서' % M(o)
    ss = g(r,'Slice size'); pf = g(r,'Punching pressure'); st = g(r,'Punch stroke')
    summ = '슬라이스 규격 <b>%s</b> · 펀칭 하중 %s · 스트로크 %s · 적용 시료 리튬 양·음극 시트, 분리막 · 무게 %s' % (ss, pf, st, g(r,'Weight'))
    feats = [cfg['why'],
      '<b>슬라이스 규격 %s</b> — 툴헤드 교체로 지름을 바꿉니다. 기본 툴헤드는 %s입니다.' % (ss, g(r,'Standard tool head')),
      '<b>펀칭 하중 %s · 스트로크 %s</b> — 수동 레버 구동이라 전원이 필요 없습니다.' % (pf, st),
      '<b>몰드 재질 %s</b> — 반복 타발에서 날 끝이 무뎌지는 것을 늦춥니다.' % g(r,'Mold material'),
      '<b>정전기 방지 수집함</b> — %s. 타발된 전극이 달라붙지 않게 받아 냅니다.' % g(r,'Receiving box')]
    incl = [('본체 1대 + 기본 툴헤드','in','포함'), ('추가 지름 툴헤드','ex','별매')]
    faqs = [
     ('용도','무엇에 쓰는 장비인가요?', cfg['why']),
     ('규격','자를 수 있는 지름 범위는?','<b>%s</b>입니다. 기본 툴헤드는 %s이며, 다른 지름은 툴헤드를 추가하면 됩니다.' % (ss, g(r,'Standard tool head'))),
     ('적용','어떤 시료에 쓰나요?','<b>%s</b>입니다. 집전체에 도포된 전극 시트와 분리막을 대상으로 합니다.' % g(r,'Suitable material')),
     ('운용','전원이 필요한가요?','필요 없습니다. 수동 레버 구동이며 펀칭 하중 %s, 스트로크 %s입니다.' % (pf, st)),
     ('구성','툴헤드는 몇 개 오나요?','기본 툴헤드 %s가 포함됩니다. 추가 지름은 별매이며, 필요한 지름을 알려주시면 함께 구성해 드립니다.' % g(r,'Standard tool head')),
     ('가격','가격이 왜 문의인가요?','제조사가 정가를 공개하지 않는 품목이라 구성·수량을 확인한 뒤 안내드립니다. 부가세 별도이며 해외 발주라 해외배송비가 주문당 1회 더해집니다.'),
    ]
    warn = ('안전 — 날 끝에 손을 대지 마십시오','타발 날은 매우 날카롭습니다. 시료를 놓거나 뺄 때 레버가 내려오지 않도록 고정하고, 툴헤드 교체는 반드시 하중을 완전히 해제한 뒤 진행하십시오.')
    return common(o, cfg, h1, cfg['ans'], summ, spec_rows(r), feats, faqs, incl, warn,
                  [{"m": o['model'], "s": '슬라이스 %s' % ss}])

def build_page(o):
    k = (CFG.get(o['fam']) or SLICER)['kind'] if o['fam'] != 'Z-slicer' else 'slicer'
    if k == 'press': return press_page(o)
    if k == 'die':   return die_page(o)
    return slicer_page(o)

# ── 허브(119장) ──────────────────────────────────────────────
def card_of(o):
    slug = o['slug']
    if o['done']:
        s = io.open(os.path.join(H.ROOT, 'brands', 'hench', slug, 'index.html'), encoding='utf-8').read()
        h1 = re.sub(r'<[^>]+>', '', re.search(r'<h1 class="dt-name">([\s\S]*?)</h1>', s).group(1)).strip()
        d = re.sub(r'<[^>]+>', '', re.search(r'<p class="dt-ans">([\s\S]*?)</p>', s).group(1)).strip()
        sub = 'pellet' if 'pellet-press' in slug else 'die'
        bdg = '펠릿 프레스' if sub == 'pellet' else '펠릿 다이'
    else:
        cfg = CFG.get(o['fam']) or SLICER
        pg = build_page(o); h1 = pg['h1']; d = re.sub(r'<[^>]+>', '', pg['ans'])
        sub = cfg['sub']; bdg = cfg['crumb']
    return dict(cat=sub, img='/img/hench/%s-1.jpg' % slug, bdg=bdg[:14],
                href='/brands/hench/%s/' % slug, title=h1, nm=M(o),
                d=d[:112],
                text=('%s %s %s hench 헨치 천진항창립달 시료 전처리 펠릿 프레스 다이 압편 kbr ir xrd %s'
                      % (h1, M(o), slug.replace('-', ' '), o['name'])).lower())

def main():
    made = 0
    for o in F.out:
        if o['done']: continue          # gen_models.py 가 담당(이미 중문 반영본으로 재생성됨)
        H.write(o['slug'], H.render(build_page(o))); made += 1
    cards = [card_of(o) for o in F.out]
    hp = os.path.join(H.ROOT, 'brands', 'hench', 'index.html')
    io.open(hp, 'w', encoding='utf-8', newline='\n').write(G.hub(cards))
    print('신규 %d장 · 허브 dscard %d장' % (made, len(cards)))

if __name__ == '__main__':
    main()
