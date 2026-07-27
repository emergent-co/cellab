// migrate-sh-images.mjs
// 삼흥(SH Scientific) 제품 이미지 → Cloudflare R2 이전 스크립트
// 실행: C:\dev\cellab_homepage 에서  ->  node migrate-sh-images.mjs
// 요구: Node 18+ (내장 fetch), wrangler 로그인 상태(npx wrangler login)

import { execSync } from 'node:child_process';
import { mkdirSync, existsSync, writeFileSync } from 'node:fs';
import path from 'node:path';

// ───────────────────────────── CONFIG ─────────────────────────────
const D1_DB       = 'rndsetup-products';      // D1 데이터베이스 이름
const R2_BUCKET   = 'rndsetup-images';        // R2 버킷 이름
const BRAND       = 'SH Scientific';
const IMG_DIR     = path.resolve('img', 'products');
const REMOTE      = '--remote';               // 프로덕션 대상
const DELAY_MS    = 1000;                      // 요청 간 딜레이
const REPORT_FILE = path.resolve('migration-report.json');
// R2 버킷에 연결한 커스텀 도메인. 아래 값이 실제 사용할 서브도메인인지 확인하세요.
let   PUBLIC_DOMAIN = 'https://img.rndsetup.com';
// ───────────────────────────────────────────────────────────────────

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function wr(cmd, opts = {}) {
  // wrangler 실행 (stdout 반환). 실패 시 throw.
  return execSync(`npx wrangler ${cmd}`, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'inherit'],
    maxBuffer: 64 * 1024 * 1024,
    ...opts,
  });
}

function extractJson(text) {
  const s = text.indexOf('[');
  const e = text.lastIndexOf(']');
  if (s === -1 || e === -1) throw new Error('D1 JSON 출력 파싱 실패:\n' + text.slice(0, 500));
  return JSON.parse(text.slice(s, e + 1));
}

async function main() {
  mkdirSync(IMG_DIR, { recursive: true });

  // 1) 버킷 생성 (이미 있으면 무시)
  console.log(`\n[1] R2 버킷 생성: ${R2_BUCKET}`);
  try {
    wr(`r2 bucket create ${R2_BUCKET}`);
    console.log('    → 생성 완료');
  } catch (e) {
    console.log('    → 이미 존재하거나 생성 스킵 (계속 진행)');
  }

  // 2) 공개 도메인 확인 (커스텀 도메인)
  //    커스텀 도메인은 Cloudflare 대시보드(R2 → 버킷 → Settings → Custom Domains)에서
  //    한 번 연결해두면 DNS 레코드가 자동 생성됩니다. rndsetup.com 이 Cloudflare 존에 있어야 합니다.
  PUBLIC_DOMAIN = PUBLIC_DOMAIN.replace(/\/+$/, '');
  console.log(`\n[2] 공개 도메인: ${PUBLIC_DOMAIN}`);

  // 3) D1 조회
  console.log(`\n[3] D1 조회 (${BRAND})`);
  const sql = `SELECT model, image_url FROM products WHERE brand='${BRAND}' AND image_url IS NOT NULL`;
  const raw = wr(`d1 execute ${D1_DB} ${REMOTE} --json --command "${sql}"`);
  const rows = extractJson(raw)[0].results;
  console.log(`    → ${rows.length}개 대상`);

  const results = { ok: [], downloadFail: [], uploadFail: [] };

  // 4~6) 다운로드 → 업로드
  for (let i = 0; i < rows.length; i++) {
    const { model, image_url } = rows[i];
    const fileName = `${model}.jpg`;
    const filePath = path.join(IMG_DIR, fileName);
    const tag = `[${i + 1}/${rows.length}] ${model}`;

    // 다운로드 (이미 있으면 스킵)
    if (!existsSync(filePath)) {
      const bigUrl = image_url.replace('/web/product/medium/', '/web/product/big/');
      let buf = null, usedUrl = null;
      for (const url of [bigUrl, image_url]) {
        try {
          const res = await fetch(url);
          if (res.ok) {
            const ct = res.headers.get('content-type') || '';
            if (!ct.startsWith('image')) throw new Error(`non-image (${ct})`);
            buf = Buffer.from(await res.arrayBuffer());
            usedUrl = url;
            break;
          }
        } catch (_) { /* 다음 URL 시도 */ }
        if (url === bigUrl) await sleep(DELAY_MS); // big 실패 후 medium 재시도 전 딜레이
      }
      if (!buf) {
        console.log(`${tag}  ✗ 다운로드 실패`);
        results.downloadFail.push({ model, image_url });
        await sleep(DELAY_MS);
        continue;
      }
      writeFileSync(filePath, buf);
      console.log(`${tag}  ↓ ${usedUrl === bigUrl ? 'big' : 'medium'} (${buf.length}B)`);
      await sleep(DELAY_MS);
    } else {
      console.log(`${tag}  = 로컬 존재, 다운로드 스킵`);
    }

    // 업로드
    try {
      wr(`r2 object put ${R2_BUCKET}/${fileName} --file="${filePath}" ${REMOTE} --content-type image/jpeg`,
         { stdio: ['ignore', 'ignore', 'inherit'] });
      results.ok.push(model);
      console.log(`${tag}  ↑ R2 업로드`);
    } catch (e) {
      console.log(`${tag}  ✗ 업로드 실패`);
      results.uploadFail.push({ model });
    }
  }

  // 7) D1 UPDATE (성공한 model 일괄)
  console.log(`\n[7] D1 UPDATE (${results.ok.length}개)`);
  if (results.ok.length) {
    const inList = results.ok.map((m) => `'${m.replace(/'/g, "''")}'`).join(',');
    const upd = `UPDATE products SET image_url='${PUBLIC_DOMAIN}/'||model||'.jpg' `
              + `WHERE brand='${BRAND}' AND model IN (${inList})`;
    wr(`d1 execute ${D1_DB} ${REMOTE} --command "${upd}"`);
    console.log('    → 완료');
  }

  // 8) 리포트
  writeFileSync(REPORT_FILE, JSON.stringify(results, null, 2), 'utf8');
  console.log(`\n───────── 결과 ─────────`);
  console.log(`성공: ${results.ok.length}`);
  console.log(`다운로드 실패: ${results.downloadFail.length}`);
  results.downloadFail.forEach((r) => console.log(`   - ${r.model}  (${r.image_url})`));
  console.log(`업로드 실패: ${results.uploadFail.length}`);
  results.uploadFail.forEach((r) => console.log(`   - ${r.model}`));
  console.log(`\n리포트 저장: ${REPORT_FILE}`);
  console.log(`공개 도메인: ${PUBLIC_DOMAIN}`);
}

main().catch((e) => { console.error('\n[FATAL]', e.message); process.exit(1); });
