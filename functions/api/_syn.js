// 연관검색어(동의어) 사전 — 품명/모델명 검색 확장용.
//   같은 줄에 있는 말은 모두 서로의 동의어로 취급한다.
//   "퍼니스" 를 쳐도 데이터에 있는 "전기로" 가 걸리도록 하는 것이 목적.
//   ※ 여기 있는 말들은 실제 products 테이블의 대분/소분/브랜드 어휘에 맞춰 넣었다.

const GROUPS = [
  // ── 전기로 계열 ─────────────────────────────────────────────
  ['전기로','퍼니스','furnace','화로','소성로','열처리로','소결로','전기가마','가마'],
  ['머플로','머플','muffle','박스로','box furnace','챔버로'],
  ['튜브전기로','관상로','tube furnace','튜브로','튜뷸러','tubular','튜브퍼니스'],
  ['회전튜브전기로','로터리킬른','rotary kiln','회전로','킬른','kiln','로타리킬른'],
  ['엘리베이터','elevator','승강식','승강'],
  ['cvd','가스플로우','gas flow','증착','화학기상증착'],
  ['히팅존','heating zone','발열체','heating'],

  // ── 펌프 계열 ───────────────────────────────────────────────
  ['펌프','pump','펌푸'],
  ['연동펌프','페리스탈틱','peristaltic','튜빙펌프','tubing pump','정량펌프','호스펌프','롤러펌프'],
  ['시린지펌프','실린지펌프','syringe','주사기펌프','시린지','실린지'],
  ['기어펌프','gear pump','기어'],
  ['다이어프램','diaphragm','격막','무급유','oil free','오일프리'],
  ['진공펌프','vacuum','배큠','베큠','진공'],
  ['로터리','rotary','유회전','오일회전','회전펌프','rotary vane','베인'],
  ['드라이펌프','스크류','screw','건식펌프','dry pump'],
  ['고진공','터보','turbo','turbo molecular','확산펌프'],
  ['방폭','explosion proof','내압방폭'],

  // ── 유량 / 압력 ─────────────────────────────────────────────
  ['mfc','유량제어','유량제어기','mass flow controller','매스플로우','질량유량제어기','가스유량제어'],
  ['mfm','유량계','flow meter','질량유량계','매스플로우미터','플로우미터','유량측정'],
  ['액체유량계','liquid flow','액체유량','액체제어기'],
  ['압력','pressure','압력계','압력제어기','게이지','gauge','트랜스듀서','transducer','진공게이지','압력센서'],
  ['밸브','valve','멀티포트','multiport','multi port','분배밸브','로터리밸브','선택밸브','솔레노이드'],
  ['튜브','tube','튜빙','tubing','호스','hose','배관','실리콘튜브'],
  ['피팅','fitting','커넥터','connector','조인트'],

  // ── 교반 / 분쇄 / 혼합 ──────────────────────────────────────
  ['교반','교반기','stirrer','스터러','스터러기','믹싱','mixing','아지테이터'],
  ['마그네틱','자력교반기','magnetic stirrer','마그네틱바','자석교반기','magnetic'],
  ['핫플레이트','hotplate','hot plate','가열교반기','열판','핫플'],
  ['오버헤드','overhead','상부교반기','오버헤드스터러'],
  ['믹서','mixer','혼합기','혼합'],
  ['균질기','호모지나이저','homogenizer','homo','호모','디스퍼서','disperser','분산기'],
  ['플래너터리','planetary','행성믹서','유성믹서','플레너터리'],
  ['볼밀','ball mill','mill','밀링','분쇄기','분쇄','파쇄'],
  ['크러셔','crusher','죠크러셔','jaw crusher','조크러셔'],
  ['롤밀','roll mill','3롤밀','삼롤밀'],
  ['쉐이커','shaker','진탕기','셰이커','보텍스','vortex'],

  // ── 건조 / 항온 / 배양 ──────────────────────────────────────
  ['건조기','dryer','오븐','oven','드라이오븐','건조오븐','열풍건조기','드라이어'],
  ['진공건조기','vacuum oven','진공오븐','감압건조'],
  ['항온항습','항온항습기','항온항습챔버','chamber','챔버','환경시험기','constant temperature','온습도'],
  ['배양기','인큐베이터','incubator','인큐','co2 인큐베이터','세포배양','cell culture','shaking incubator'],
  ['항온수조','수조','water bath','워터배스','워터바스','항온조','배스','bath','칠러','chiller','냉각수조'],
  ['데시케이터','desiccator','건조함','방습함'],

  // ── 농축 / 증류 ─────────────────────────────────────────────
  ['농축기','회전농축기','증발기','evaporator','로터리이배퍼레이터','rotary evaporator','감압농축','회전증발기','로터리','rotavap','회전농축'],
  ['트랩','trap','콜드트랩','cold trap','용매회수','회수트랩'],
  ['증류','distillation','숏패스','short path','분별증류','정제'],

  // ── 세척 / 멸균 / 안전 ──────────────────────────────────────
  ['초음파세척기','ultrasonic','소니케이터','sonicator','초음파','세척기','washer'],
  ['멸균기','오토클레이브','autoclave','살균기','고압증기멸균기','스터리라이저','sterilizer'],
  ['후드','hood','흄후드','fume hood','드래프트','draft','배기후드'],
  ['클린벤치','무균','laminar','laminar flow','무균작업대','안전캐비닛','biosafety'],
  ['스팀제너레이터','steam generator','스팀','증기발생기'],

  // ── 계측 ────────────────────────────────────────────────────
  ['저울','balance','scale','전자저울','정밀저울','분석저울','천칭','정밀전자저울'],
  ['수분측정기','moisture','수분계','함수율'],
  ['캘리브레이터','calibrator','교정기','검교정'],
  ['드라이버','driver','스텝모터','step motor','모터드라이버','컨트롤러','controller','제어기'],

  // ── 브랜드 ──────────────────────────────────────────────────
  ['sh scientific','에스에이치','에스에이치사이언티픽','shscientific','sh사이언티픽'],
  ['leadfluid','리드플루이드','리드플루','리드'],
  ['runze','런제','룬제','런즈','runze fluid'],
  ['alicat','알리캣','앨리캣','알리캇','alicat scientific'],
];

// 정규화: 소문자 · 공백/구분자 제거 · 온도표기 통일
function norm(s) {
  return String(s == null ? '' : s)
    .toLowerCase()
    .replace(/[℃°]/g, '')
    .replace(/[\s\-_.,/()]/g, '');
}

// alias(정규화) → 그룹 index 목록
const INDEX = new Map();
GROUPS.forEach((g, gi) => {
  for (const term of g) {
    const k = norm(term);
    if (!INDEX.has(k)) INDEX.set(k, []);
    if (!INDEX.get(k).includes(gi)) INDEX.get(k).push(gi);
  }
});
const KEYS = Array.from(INDEX.keys());

// 숫자+온도/단위 표기를 느슨하게: "1200도" "1200℃" "1200c" → "1200"
function loosen(w) {
  const m = norm(w).match(/^(\d{2,4})(도|c|℃|deg|degree)?$/);
  return m ? m[1] : null;
}

/**
 * 검색어 한 단어를 → 실제로 LIKE 를 걸 후보 단어 배열로 확장한다.
 * 반환값의 [0] 은 항상 원본(문자 그대로)이다.
 */
export function expandWord(word) {
  const w = String(word || '').trim();
  if (!w) return [];
  const out = [w];
  const push = (t) => { if (t && !out.some((o) => norm(o) === norm(t))) out.push(t); };

  const n = norm(w);
  if (!n) return out;

  const loose = loosen(w);
  if (loose) { push(loose); return out; }          // 숫자는 동의어 확장하지 않는다

  const hits = new Set();
  if (INDEX.has(n)) for (const gi of INDEX.get(n)) hits.add(gi);

  // 2글자 이상이면 부분일치도 본다 ("연동펌" → 연동펌프, "퍼니" → 퍼니스)
  if (n.length >= 2) {
    for (const k of KEYS) {
      if (k === n) continue;
      if (k.length >= 2 && (k.includes(n) || n.includes(k))) {
        for (const gi of INDEX.get(k)) hits.add(gi);
      }
    }
  }

  // 그룹이 너무 많이 걸리면(= 너무 흔한 말) 확장을 줄인다
  const gis = Array.from(hits).slice(0, 6);
  for (const gi of gis) for (const t of GROUPS[gi]) push(t);

  return out.slice(0, 24);
}

/** 검색어 전체를 단어별 확장 배열로 */
export function expandQuery(q, maxWords = 4) {
  return String(q || '').trim().split(/\s+/).filter(Boolean).slice(0, maxWords).map(expandWord);
}

/** 사전에 어떤 말이 들어있는지 (관리/디버그용) */
export function synGroups() { return GROUPS; }
