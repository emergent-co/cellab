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
}
# 표에서 뺄 항목(장황하거나 카드에 무의미)
DROP = {'구성 안내', '비고'}
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
        v = U(v)
        if len(v) > 150: v = v[:147] + '…'
        out.setdefault(ko, v)
    rows = [(k, out[k]) for k in ORDER if k in out]
    rows += [(k, v) for k, v in out.items() if k not in ORDER]
    return rows + list(extra)

def g(r, *keys, **kw):
    sp = json.loads(r['spec'])
    for k in keys:
        for x in sp:
            if x.strip().lower() == k.lower():
                v = U(re.sub(r'\s+', ' ', sp[x]).strip())
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
 'P2-digital': dict(kind='press', crumb='디지털 수동 유압 펠릿 프레스', sub='pellet',
   nm='디지털 수동 유압 펠릿 프레스',
   ans='레버로 가압하되 압력을 디지털 게이지로 읽는 펠릿 프레스입니다. 지침식보다 판독 오차가 작아 성형압 재현이 쉽습니다.',
   why='수동 유압 구조는 같고 <b>압력 표시가 디지털</b>입니다. 눈금 사이를 읽어 어림하던 지침식과 달리 수치가 그대로 찍혀, 같은 성형압을 반복할 때 유리합니다.'),
 'P3-electric': dict(kind='press', crumb='전동 유압 펠릿 프레스', sub='press-e',
   nm='전동 유압 펠릿 프레스',
   ans='모터 유압으로 가압하는 펠릿 프레스입니다. 레버를 젓지 않아도 되고 설정 압력까지 자동으로 올라갑니다.',
   why='레버 펌핑이 없습니다. <b>PCB 프로그램 완충 가압</b>으로 설정값까지 올린 뒤, 가압 후 압력이 떨어지면 <b>실시간 자동 보정</b>합니다. 반복 작업량이 많을 때 손이 덜 갑니다.'),
 'P4-auto': dict(kind='press', crumb='자동 유압 펠릿 프레스', sub='press-a',
   nm='자동 유압 펠릿 프레스',
   ans='가압·유지·탈형을 프로그램으로 돌리는 자동 펠릿 프레스입니다. 터치 화면에서 압력과 유지 시간을 설정합니다.',
   why='가압 → 유지 → 감압을 <b>프로그램이 순서대로</b> 수행합니다. 작업자가 붙어 있지 않아도 되고, 같은 조건을 그대로 다시 불러 쓸 수 있습니다.'),
 'P5-isostatic': dict(kind='press', crumb='등온압축(Isostatic) 펠릿 프레스', sub='press-iso',
   nm='등온압축 펠릿 프레스',
   ans='시료를 유체로 감싸 사방에서 균일하게 누르는 등온압축 프레스입니다. 밀도 편차가 작은 성형체를 만듭니다.',
   why='단축 프레스는 위아래로만 눌러 시료 안에 밀도 구배가 생깁니다. 등온압축은 <b>압력 매체가 시료를 전방향으로 균일하게</b> 눌러 밀도 편차를 줄입니다. 세라믹·고체전해질처럼 소결 후 변형이 문제되는 시료에 씁니다.'),
 'P6-hot': dict(kind='press', crumb='가열(Hot) 펠릿 프레스', sub='press-hot',
   nm='가열 펠릿 프레스',
   ans='열판으로 다이를 데우면서 동시에 가압하는 프레스입니다. 상온에서 안 눌리는 고분자·복합재 시료에 씁니다.',
   why='열판이 다이를 데운 상태로 가압합니다. 상온 성형이 안 되는 <b>고분자 필름·복합재·박막</b>에서 온도와 압력을 함께 걸어야 할 때 필요합니다.'),
 'P7-fluoro': dict(kind='press', crumb='형광분석(XRF) 전용 자동 펠릿 프레스', sub='press-xrf',
   nm='형광분석 전용 자동 펠릿 프레스',
   ans='XRF 시료컵 규격에 맞춰 펠릿을 찍는 자동 프레스입니다. 압력·유지·탈형이 프로그램으로 돌아갑니다.',
   why='XRF는 시료 표면 상태가 결과를 좌우합니다. 이 계열은 <b>형광분석용 몰드 규격(40–32 mm 등)에 맞춰</b> 자동 가압·탈형까지 프로그램으로 처리해 표면 재현성을 확보합니다.'),
 'P8-cellseal': dict(kind='press', crumb='버튼셀 실링기', sub='cell',
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
 'D6-hotdie': dict(kind='die', crumb='가열 펠릿 다이', sub='die-hot',
   nm='가열 펠릿 다이',
   ans='다이 자체를 가열해 시료를 데우면서 성형하는 다이입니다. 가열 프레스와 함께 씁니다.',
   why='다이에 열원이 들어 있어 <b>시료를 데운 상태로 성형</b>합니다. 상온에서 성형되지 않는 고분자·필름 시료에 필요합니다.'),
 'D7-cellmold': dict(kind='die', crumb='버튼셀·전고체 전지 몰드', sub='cell',
   nm='버튼셀 전지 몰드',
   ans='코인셀 실링·분해와 전고체 전지 가압 평가에 쓰는 전용 몰드입니다.',
   why='전지 조립·평가 전용 몰드입니다. 실링/분해용과, 전고체 전지처럼 <b>가압 상태를 유지한 채 측정</b>해야 하는 용도가 나뉩니다.'),
 'D8-fluorodie': dict(kind='die', crumb='형광분석(XRF)용 펠릿 다이', sub='die',
   nm='형광분석용 펠릿 다이',
   ans='XRF 시료 성형 전용 다이입니다. 붕산 링·스틸 링으로 시료 가장자리를 잡아 줍니다.',
   why='XRF는 시료가 커서 그대로 누르면 가장자리가 무너집니다. <b>붕산 또는 스틸 링으로 테두리를 지지</b>해 평탄한 분석면을 만듭니다.'),
}
