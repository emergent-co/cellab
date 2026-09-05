/* member/index.html 안에서 «같은 이름 함수»가 두 번 선언됐는지 본다.
   호이스팅 때문에 뒤엣것이 조용히 이기고, 앞엣것을 부르던 자리가 통째로 죽는다.
   (실제로 dqSrcTag 가 겹쳐 발행 폼 전체가 멈춘 적이 있다) */
import fs from 'node:fs';
const t = fs.readFileSync(new URL('../member/index.html', import.meta.url), 'utf-8');
const blocks = [...t.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
let bad = 0;
blocks.forEach((b, bi) => {
  const seen = new Map();
  for (const m of b.matchAll(/^function (\w+)\s*\(/gm)) {
    const line = b.slice(0, m.index).split('\n').length;
    if (seen.has(m[1])) { bad++; console.log(`  ✗ block ${bi}: function ${m[1]} 이 ${seen.get(m[1])}줄과 ${line}줄에 중복 선언`); }
    else seen.set(m[1], line);
  }
});
console.log(bad ? `\n중복 ${bad}건` : '\n통과 — 최상위 함수 이름 중복 없음');
process.exit(bad ? 1 : 0);
