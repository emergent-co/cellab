// functions/api/_barobill.js — 바로빌(전자세금계산서) 연동 바탕
//
// 환경변수 (Cloudflare Pages → Settings → Environment variables)
//   BAROBILL_MODE          'test' | 'live'   ← 비었거나 오타면 무조건 test
//   BAROBILL_CERTKEY       운영 인증키   (Secret)
//   BAROBILL_CERTKEY_TEST  테스트 인증키 (Secret)
//   BAROBILL_ID            바로빌 로그인 아이디
//   BAROBILL_CORPNUM       사업자번호 (하이픈 없이)
//   BAROBILL_ID_TEST / BAROBILL_CORPNUM_TEST   테스트베드가 별도 계정일 때만
//
// 키와 서버 주소는 반드시 짝으로 고른다. 사람이 따로 고르게 두면 언젠가 엇갈린다.

const HOST = {
  test: 'https://testws.baroservice.com',
  live: 'https://ws.baroservice.com',
};
// 바로빌 SOAP 서비스는 도메인별로 나뉜다. 지금 쓰는 건 세금계산서(TI) 하나다.
const SERVICE = { ti: '/TI.asmx' };
const NS = 'http://ws.baroservice.com/';

export function barobillConfig(env) {
  const mode = String(env.BAROBILL_MODE || '').trim().toLowerCase() === 'live' ? 'live' : 'test';
  const test = mode === 'test';
  const certkey = test ? (env.BAROBILL_CERTKEY_TEST || '') : (env.BAROBILL_CERTKEY || '');
  const id      = (test && env.BAROBILL_ID_TEST)      || env.BAROBILL_ID      || '';
  const corpNum = String((test && env.BAROBILL_CORPNUM_TEST) || env.BAROBILL_CORPNUM || '')
    .replace(/[^0-9]/g, '');
  return { mode, test, certkey, id, corpNum, host: HOST[mode] };
}

export function barobillReady(env) {
  const c = barobillConfig(env);
  return !!(c.certkey && c.id && c.corpNum.length === 10);
}

/** 설정 진단 — 키 자체는 절대 내보내지 않고, 들어왔는지와 길이만 알려준다. */
export function barobillDiag(env) {
  const c = barobillConfig(env);
  const has = (v) => (v ? `설정됨 (${String(v).length}자)` : '없음');
  return {
    mode: c.mode,
    endpoint: c.host + SERVICE.ti,
    certkey: has(c.certkey),
    certkey_source: c.test ? 'BAROBILL_CERTKEY_TEST' : 'BAROBILL_CERTKEY',
    id: c.id ? `설정됨 (${c.id.slice(0, 2)}${'*'.repeat(Math.max(0, c.id.length - 2))})` : '없음',
    corp_num: c.corpNum ? `${c.corpNum} (${c.corpNum.length}자리)` : '없음',
    ready: barobillReady(env),
    note: c.mode === 'test'
      ? '테스트 모드입니다. 국세청으로 실제 발행되지 않습니다.'
      : '운영 모드입니다. 발행하면 국세청으로 실제 전송됩니다.',
  };
}

const esc = (v) => String(v == null ? '' : v)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&apos;');

/** 값이 객체·배열이면 그대로 중첩해 XML 로 편다 (바로빌 구조체용). */
function toXml(v) {
  if (v == null) return '';
  if (Array.isArray(v)) return v.map((x) => toXml(x)).join('');
  if (typeof v === 'object') {
    return Object.keys(v).map((k) => {
      const val = v[k];
      if (Array.isArray(val)) return val.map((x) => `<${k}>${toXml(x)}</${k}>`).join('');
      return `<${k}>${toXml(val)}</${k}>`;
    }).join('');
  }
  return esc(v);
}

/**
 * 바로빌 SOAP 호출.
 * @param {object} env
 * @param {string} method  예) 'GetCorpState'
 * @param {object} args    CERTKEY·CorpNum·ID 는 여기서 채운다
 * @returns {Promise<{ok:boolean, raw?:string, value?:string, error?:string}>}
 */
export async function barobillCall(env, method, args = {}) {
  const c = barobillConfig(env);
  if (!barobillReady(env)) {
    return { ok: false, error: '바로빌 환경변수가 덜 채워졌습니다 (인증키·아이디·사업자번호).' };
  }
  const body = Object.assign({ CERTKEY: c.certkey, CorpNum: c.corpNum, ID: c.id }, args);
  const xml =
    '<?xml version="1.0" encoding="utf-8"?>'
    + '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    + ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
    + ' xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
    + `<${method} xmlns="${NS}">${toXml(body)}</${method}>`
    + '</soap:Body></soap:Envelope>';

  let r;
  try {
    r = await fetch(c.host + SERVICE.ti, {
      method: 'POST',
      headers: { 'content-type': 'text/xml; charset=utf-8', SOAPAction: NS + method },
      body: xml,
    });
  } catch (e) {
    return { ok: false, error: `바로빌 서버에 닿지 못했습니다: ${String(e?.message || e)}` };
  }
  const raw = await r.text();
  if (!r.ok) return { ok: false, error: `HTTP ${r.status}`, raw: raw.slice(0, 800) };

  const fault = raw.match(/<faultstring>([\s\S]*?)<\/faultstring>/);
  if (fault) return { ok: false, error: unesc(fault[1]), raw: raw.slice(0, 800) };

  // <XxxResult> 안이 결과다. 숫자 하나만 오는 메서드도 있고 구조체가 오기도 한다.
  const m = raw.match(new RegExp(`<${method}Result[^>]*>([\\s\\S]*?)</${method}Result>`));
  const value = m ? unesc(m[1]).trim() : '';
  // 바로빌은 음수 하나를 오류코드로 돌려준다.
  const n = Number(value);
  if (value !== '' && Number.isInteger(n) && n < 0) {
    return { ok: false, code: n, error: `바로빌 오류코드 ${n}`, raw: raw.slice(0, 800) };
  }
  return { ok: true, value, raw };
}

function unesc(t) {
  return String(t).replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&');
}
