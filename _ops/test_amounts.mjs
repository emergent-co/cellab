/* 금액 규칙 회귀 테스트 — node _ops/test_amounts.mjs
   발행(compute) · 발송(calcTotals) · 서류(docTotals) · 장부(recalcOrder) · 국세청(바로빌) 이
   같은 품목에 대해 같은 답을 내는지 실제 소스에서 함수를 뽑아 대조한다. */
import fs from 'node:fs';

const read = (p) => fs.readFileSync(new URL('../' + p, import.meta.url), 'utf-8');
function grab(src, sig) {                       // 함수 하나를 소스에서 통째로 떼어낸다
  const i = src.indexOf(sig);
  if (i < 0) throw new Error('함수를 찾지 못함: ' + sig);
  let d = 0, j = src.indexOf('{', i);
  for (let k = j; k < src.length; k++) {
    if (src[k] === '{') d++;
    else if (src[k] === '}' && --d === 0) return src.slice(i, k + 1);
  }
  throw new Error('괄호가 안 닫힘: ' + sig);
}
const mk = (body, extra = '') => eval(`(() => { ${extra}\n${body}\n return ${body.match(/function (\w+)/)[1]}; })()`);

const ISSUE = read('functions/api/admin/issue.js');
const helpers = `const round10=(n)=>Math.round(Number(n||0)/10)*10;const floor10=(n)=>Math.floor(Number(n||0)/10)*10;`;
const compute     = mk(grab(ISSUE, 'function compute('), helpers);
const calcTotals  = mk(grab(read('functions/api/_send.js'), 'export function calcTotals(').replace('export ', ''));
const docTotals   = mk(grab(read('functions/api/_doctpl.js'), 'function docTotals('));

// 장부(recalcOrder)의 계산부만 옮겨 온 것 — 소스와 같은 식인지 문자열로 확인한다
const LIB = read('functions/api/_lib.js');
if (!/vat \+= Math\.floor\(line \* 0\.1 \/ 10\) \* 10;/.test(LIB)) throw new Error('recalcOrder 규칙이 바뀌었다 — 테스트를 고쳐라');
const ledger = (items) => { let supply = 0, vat = 0;
  for (const r of items) { const line = Math.round((r.qty||0)*(r.unit_price||0)); supply += line; vat += Math.floor(line*0.1/10)*10; }
  return { supply, vat, total: supply + vat }; };

// 바로빌 품목 — _barobill.js 와 같은 식
const nts = (items) => items.map((i) => { const qty = Number(i.qty)||0, up = Math.round(Number(i.unit_price)||0);
  const amt = Math.round(qty*up); return { amt, tax: Math.round(amt*0.1) }; });

const CASES = [
  ['단일 · 사이트 판매가',            [{ qty:1, price:350000 }]],
  ['단일 · 만원버림 전 값',           [{ qty:1, price:358900 }]],
  ['수량 3',                          [{ qty:3, price:358900 }]],
  ['수량 7 · 백만원대',               [{ qty:7, price:1234567 }]],
  ['1원짜리',                         [{ qty:1, price:1 }]],
  ['10원 미만 단가',                  [{ qty:9, price:7 }]],
  ['990원 × 11',                      [{ qty:11, price:990 }]],
  ['딱 떨어지는 백만원',              [{ qty:1, price:1000000 }]],
  ['3줄 혼합',                        [{ qty:1, price:990 }, { qty:7, price:1234560 }, { qty:3, price:358900 }]],
  ['10줄 잡값',                       Array.from({length:10}, (_,k) => ({ qty:k+1, price:12345*(k+1)+7 }))],
  ['큰 수량',                         [{ qty:999, price:87650 }]],
  ['0원 줄 포함',                     [{ qty:2, price:0 }, { qty:1, price:350000 }]],
];
for (let s = 0; s < 40; s++) {                     // 무작위 케이스
  const n = 1 + (s % 5);
  CASES.push([`무작위 #${s+1}`, Array.from({length:n}, () => ({ qty: 1 + Math.floor(Math.random()*20), price: Math.floor(Math.random()*9_000_000) + 100 }))]);
}

let fail = 0, run = 0;
const eq = (name, a, b, note) => { run++; if (a !== b) { fail++; console.log(`  ✗ ${name}: ${a} ≠ ${b} ${note||''}`); } };

for (const [name, raw] of CASES) {
  for (const vatIncluded of [false, true]) {
    const tag = `${name} [${vatIncluded ? '포함' : '별도'}]`;
    const { items, totals } = compute(raw.map((i) => ({ ...i, name:'x' })), vatIncluded);

    // 1) 서류 내부 정합 — 세 줄이 서로 더해서 맞아야 한다
    eq(`${tag} Σ금액=합계`, items.reduce((s,i)=>s+i.amount,0), totals.total);
    eq(`${tag} 합계−공급가=부가세`, totals.total - totals.supply, totals.vat);
    if (!vatIncluded) eq(`${tag} Σ(수량×단가)=공급가액`, items.reduce((s,i)=>s+Math.round(i.qty*i.unit_price),0), totals.supply);

    // 2) 발송·서류·장부의 «예비 계산»이 발행 결과와 같은가 (부가세 별도 기준)
    if (!vatIncluded) {
      for (const [who, fn] of [['발송(calcTotals)', calcTotals], ['서류(docTotals)', docTotals], ['장부(recalcOrder)', ledger]]) {
        const t = fn(items);
        eq(`${tag} ${who} 공급가`, t.supply, totals.supply);
        eq(`${tag} ${who} 부가세`, t.vat, totals.vat);
        eq(`${tag} ${who} 합계`,   t.total, totals.total);
      }
    }

    // 3) 국세청(바로빌) 품목 합 = 헤더 공급가액
    const rows = nts(items);
    if (!vatIncluded) eq(`${tag} 바로빌 Σ품목=공급가액`, rows.reduce((s,r)=>s+r.amt,0), totals.supply);
  }
}

// 3-b) 화면 줄 금액 = 서류 «금액(부가세포함)» 칸 · 수정 진입 왕복
const HTML = read('member/index.html');
const f10x = (n) => Math.floor(Number(n||0)/10)*10;
const front = eval(`(() => { const r10=(n)=>Math.round(Number(n||0)/10)*10, f10=(n)=>Math.floor(Number(n||0)/10)*10;
  let dqVat = false;
  ${grab(HTML, 'function dqLine(')}
  ${grab(HTML, 'function dqShowLine(')}
  return (vat, it) => { dqVat = vat; return dqShowLine(it); }; })()`);

for (const [name, raw] of CASES) {
  for (const vatIncluded of [false, true]) {
    const { items } = compute(raw.map((i) => ({ ...i, name:'x' })), vatIncluded);
    const tg = `${name} [${vatIncluded ? '포함' : '별도'}]`;
    items.forEach((it, k) => {
      eq(`${tg} 줄 ${k+1} 화면=서류`, front(vatIncluded, { qty: raw[k].qty, price: raw[k].price }), it.amount);
      const back = Number(it.price_in) > 0 ? Number(it.price_in)
                 : (vatIncluded ? Math.round((it.amount||0)/(it.qty||1)/10)*10 : Math.round(it.unit_price||0));
      eq(`${tg} 줄 ${k+1} 수정 왕복`, back, vatIncluded ? raw[k].price : f10x(raw[k].price));
    });
  }
}

// 4) 부가세 포함 ↔ 별도 토글 왕복에서 단가가 보존되는가 (화면 규칙)
const r10 = (n)=>Math.round(Number(n||0)/10)*10;
// 화면에 남는 단가는 언제나 10원 단위다(입력 blur·자동채움에서 r10/f10 을 건다).
// 그 범위에서 별도→포함→별도 왕복이 원값을 그대로 돌려주는지 전수 확인한다.
let drift = 0, tried = 0;
for (let p = 10; p <= 20_000_000; p += 10) { tried++; if (r10(r10(p*1.1)/1.1) !== p) drift++; }
run++; if (drift) { fail++; console.log(`  ✗ VAT 토글 왕복에서 ${drift}/${tried} 건 어긋남`); }
else console.log(`  · VAT 토글 왕복 ${tried.toLocaleString('en-US')}건 전부 원값 보존`);

// 5) 문서번호 채번 — 가운데를 지워도 번호가 되돌아가지 않는가
const pick = (list) => { let last = 0;
  for (const d of list) { const m = String(d).match(/^\d{8}(?:-(\d{2}))?-/); if (m) last = Math.max(last, m[1] ? Number(m[1]) : 1); }
  return last === 0 ? '20260905-Q' : `20260905-${String(last+1).padStart(2,'0')}-Q`; };
eq('채번 빈 상태', pick([]), '20260905-Q');
eq('채번 1건 뒤', pick(['20260905-Q']), '20260905-02-Q');
eq('채번 3건 뒤', pick(['20260905-Q','20260905-02-Q','20260905-03-Q']), '20260905-04-Q');
eq('채번 가운데 삭제 뒤', pick(['20260905-Q','20260905-03-Q']), '20260905-04-Q');

// 6) 예약 시각 형식 — 큐가 문자열로 비교하므로 형식이 어긋나면 영영 안 나간다
const validSendAt = mk(grab(read('functions/api/_lib.js'), 'export function validSendAt(').replace('export ', ''));
for (const [v, want] of [
  ['2026-09-05 14:00:00', '2026-09-05 14:00:00'],
  ['2026-09-05T14:00:00', null], ['2026-09-05 14:00', null], ['2026-9-5 14:00:00', null],
  ['2026-13-05 14:00:00', null], ['2026-09-05 24:00:00', null], ['', null], [null, null],
]) eq(`예약형식 ${JSON.stringify(v)}`, validSendAt(v), want);

// 7) 0원(무료 제공) 품목 — «빈칸» 과 구분되는가
const dqPriced = mk(grab(HTML, 'function dqPriced('));
[[{price:0, pset:true}, true,  '0 을 적은 무료 품목'],
 [{price:0},            false, '단가를 안 적은 줄'],
 [{price:0, pset:false},false, '적었다 지운 줄'],
 [{price:350000},       true,  '값이 있는 줄'],
 [{price:350000, pset:true}, true, '제품표에서 채운 줄']]
 .forEach(([it, want, name]) => eq('0원 판별 · ' + name, dqPriced(it), want));

// 서버 가드도 같은 판단을 하는가 (issue.js 의 unpriced 조건)
const SRC = read('functions/api/admin/issue.js');
if (!/const unpriced = raw\.filter\(\(i\) => !i\.price && !i\.priced\);/.test(SRC))
  { fail++; run++; console.log('  ✗ 서버 0원 허용 조건이 바뀌었다 — 테스트를 고쳐라'); }
else {
  const srv = (i) => !i.price && !i.priced;
  eq('서버 · 0원 표시된 품목 통과', srv({price:0, priced:true}), false);
  eq('서버 · 단가 없는 품목 거절', srv({price:0, priced:false}), true);
  eq('서버 · 값 있는 품목 통과', srv({price:350000, priced:false}), false);
}

// 0원 줄이 섞여도 서류 3줄 정합이 유지되는가
[[{qty:1,price:0,name:'x'},{qty:2,price:358900,name:'y'}],
 [{qty:3,price:0,name:'x'}]].forEach((raw, k) => {
  [false, true].forEach((vi) => {
    const { items, totals } = compute(raw, vi);
    eq(`0원 혼합 #${k+1} [${vi?'포함':'별도'}] Σ금액=합계`, items.reduce((s,i)=>s+i.amount,0), totals.total);
    eq(`0원 혼합 #${k+1} [${vi?'포함':'별도'}] 합계−공급가=부가세`, totals.total-totals.supply, totals.vat);
  });
});

console.log(fail ? `\n실패 ${fail} / 검사 ${run}` : `\n통과 — 검사 ${run}건 전부 일치 (케이스 ${CASES.length} × 2기준)`);
process.exit(fail ? 1 : 0);
