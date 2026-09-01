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
  // CERTKEY·CorpNum 만 공통이다. ID(ContactID)는 메서드마다 자리가 달라 호출부가 직접 넣는다.
  const body = Object.assign({ CERTKEY: c.certkey, CorpNum: c.corpNum }, args);
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
  //   구조체를 주는 메서드는 첫 원소에 코드를 실어 보내기도 한다 (<ContactName>-10001</ContactName> 처럼).
  const n = Number(value);
  if (value !== '' && Number.isInteger(n) && n < 0) return fail(n, raw);
  const inner = String(value).match(/>(-\d{4,5})</);
  if (inner) return fail(Number(inner[1]), raw);
  return { ok: true, value, raw };
}

function fail(n, raw) {
  return { ok: false, code: n, error: `${n} · ${BB_ERR[n] || '바로빌 오류'}`, raw: String(raw).slice(0, 800) };
}

/* 자주 만나는 오류코드 — 숫자만 보면 어디를 고쳐야 할지 알 수가 없다.
   전체 표: dev.barobill.co.kr/docs/references/바로빌-API-오류코드 */
export const BB_ERR = {
  '-10000': '알 수 없는 오류',
  '-10001': '해당 인증키와 연결된 연계사가 아닙니다 (파트너 전용 기능)',
  '-10002': '해당 인증키를 찾을 수 없습니다 — CERTKEY 확인',
  '-10003': '바로빌 연동서비스 점검 중',
  '-10008': '날짜 형식이 잘못되었습니다',
  '-11001': '공급자 아이디가 잘못되었습니다 (ContactID)',
  '-11002': '공급자 정보가 없습니다',
  '-11003': '공급받는자 정보가 없습니다',
  '-11005': '발행방향이 잘못되었습니다 (IssueDirection)',
  '-11006': '공급가액이 잘못되었습니다',
  '-11007': '영수/청구 구분이 잘못되었습니다 (PurposeType)',
  '-11009': '문서 형태가 잘못되었습니다 (TaxInvoiceType)',
  '-11101': '공급자 사업자번호가 잘못되었습니다',
  '-11102': '공급자 상호가 잘못되었습니다',
  '-11103': '공급자 대표자명이 잘못되었습니다',
  '-11104': '공급자 주소가 잘못되었습니다',
  '-11105': '공급자 업종이 잘못되었습니다 (BizType)',
  '-11106': '공급자 업태가 잘못되었습니다 (BizClass)',
  '-11107': '공급자 담당자명이 잘못되었습니다',
  '-11108': '공급자 이메일이 잘못되었습니다',
  '-11201': '공급받는자 사업자번호가 잘못되었습니다 — 거래처의 계산서 발행 정보를 확인하세요',
  '-11202': '공급받는자 상호가 잘못되었습니다',
  '-11203': '공급받는자 대표자명이 잘못되었습니다',
  '-11204': '공급받는자 주소가 잘못되었습니다',
  '-11207': '공급받는자 담당자명이 잘못되었습니다',
  '-11208': '공급받는자 이메일이 잘못되었습니다',
  '-24001': '공급자 사업자번호와 아이디가 맞지 않습니다 — BAROBILL_ID 를 확인하세요 (대소문자 구분)',
  '-24002': '공급받는자 사업자번호와 아이디가 맞지 않습니다',
  '-24005': '사업자번호와 아이디가 맞지 않습니다',
  '-30001': '지금 상태에서는 처리할 수 없는 요청입니다',
};



function unesc(t) {
  return String(t).replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&');
}


/* ===================== 전자세금계산서 =====================
   문서(dev.barobill.co.kr) 확인분 —
     RegistAndIssueTaxInvoice(CERTKEY, CorpNum, Invoice, SendSMS, ForceIssue, MailTitle) → 1 성공 / 음수 오류
     공급자의 공동인증서가 바로빌에 등록되어 있어야 한다.
   금액 칸은 전부 string(콤마 없이), 날짜는 YYYYMMDD. */
export const TI = {
  ISSUE_DIRECTION: { 정발급: 1, 역발행: 2 },
  TYPE: { 세금계산서: 1, 계산서: 2 },
  TAX: { 과세: 1, 영세: 2, 면세: 3 },
  PURPOSE: { 영수: 1, 청구: 2 },
};

// 바로빌 상태코드 → 사람이 읽는 말
export const TI_STATE = {
  1000: '임시저장', 2010: '발급예정 승인대기', 2011: '발급예정 승인완료',
  2020: '역발행요청 발급대기', 3011: '발급완료(발급예정)', 3021: '발급완료(역발행)',
  3014: '발급완료', 4012: '전송중', 6004: '국세청 전송완료',
};

const digits = (v) => String(v || '').replace(/[^0-9]/g, '');
const cut = (v, n) => String(v == null ? '' : v).trim().slice(0, n);
// 국세청은 특수문자를 싫어한다 — ㈜ 같은 글자가 그대로 가면 반려된다
const corpName = (v) => cut(String(v || '').replace(/㈜/g, '(주)').replace(/[<>&"']/g, ' '), 200);
const ymd = (v) => digits(v).slice(0, 8);

/**
 * 우리 문서(payload)를 바로빌 TaxInvoice 로 옮긴다.
 * @param {object} o { mgtKey, issuer, bill, payload, contactId, writeDate }
 */
export function buildTaxInvoice(o) {
  const p = o.payload || {};
  const t = p.totals || {};
  const bill = o.bill || {};
  const cli = p.client || {};
  const iss = o.issuer || {};

  const items = (p.items || []).map((i) => {
    const qty = Number(i.qty) || 0;
    const up = Math.round(Number(i.unit_price) || 0);
    const amt = Math.round(Number(i.amount) || qty * up);
    return {
      PurchaseExpiry: ymd(o.writeDate),
      Name: cut(i.name, 100),
      Information: cut(i.spec, 60),
      ChargeableUnit: String(qty),
      UnitPrice: String(up),
      Amount: String(amt),
      Tax: String(Math.round(amt * 0.1)),
      Description: cut(i.note, 40),
    };
  });

  return {
    InvoicerParty: {                       // 공급자 = 우리
      MgtNum: cut(o.mgtKey, 24),           // 관리번호는 공급자 쪽에 넣는다
      CorpNum: digits(iss.reg_no),
      CorpName: corpName(iss.company),
      CEOName: cut(iss.ceo, 100),
      Addr: cut(iss.address, 300),
      BizType: cut(iss.biz_type, 100),     // 업태
      BizClass: cut(iss.biz_item, 100),    // 업종
      ContactID: o.contactId,              // 바로빌 회원 아이디 (대소문자 구분)
      ContactName: cut(iss.ceo, 100),
      TEL: cut(iss.tel, 20),
      Email: cut(iss.email, 100),
    },
    InvoiceeParty: {                       // 공급받는자 = 거래처의 계산서 발행 정보
      CorpNum: digits(bill.biz_no || cli.biz_no),
      CorpName: corpName(bill.company || cli.company),
      CEOName: cut(bill.ceo || cli.ceo, 100),
      Addr: cut(bill.address || cli.address, 300),
      BizType: cut(bill.biz_type, 100),
      BizClass: cut(bill.biz_item, 100),
      ContactName: cut(cli.contact || bill.label, 100),
      TEL: cut(cli.tel, 20),
      HP: cut(cli.hp, 20),
      Email: cut(bill.tax_email || cli.email, 100),
    },
    IssueDirection: TI.ISSUE_DIRECTION.정발급,
    TaxInvoiceType: TI.TYPE.세금계산서,
    TaxType: TI.TAX.과세,
    PurposeType: TI.PURPOSE.청구,
    WriteDate: ymd(o.writeDate),
    AmountTotal: String(Math.round(t.supply || 0)),
    TaxTotal: String(Math.round(t.vat || 0)),
    TotalAmount: String(Math.round(t.total || 0)),
    Remark1: cut(p.note, 150),
    TaxInvoiceTradeLineItems: { TaxInvoiceTradeLineItem: items },
  };
}

/** 저장+발급 (국세청 전송까지 바로빌이 처리한다) */
export async function issueTaxInvoice(env, invoice, opts = {}) {
  return barobillCall(env, 'RegistAndIssueTaxInvoice', {
    Invoice: invoice,
    SendSMS: opts.sms ? 'true' : 'false',
    ForceIssue: opts.force ? 'true' : 'false',
    MailTitle: cut(opts.mailTitle, 200),
  });
}

/** 국세청으로 나간 그 한 건을 바로빌 양식으로 보는 주소.
 *  읽기 전용이고 오래 살지 않는다 — 저장하지 말고 볼 때마다 새로 받는다. */
export async function taxInvoiceViewUrl(env, mgtKey) {
  const c = barobillConfig(env);
  const r = await barobillCall(env, 'GetTaxInvoicePopUpURLReadonly', { MgtKey: cut(mgtKey, 24), ID: c.id });
  if (!r.ok) return r;
  const u = String(r.value || '').trim();
  if (!/^https?:\/\//i.test(u)) return { ok: false, error: '바로빌이 열람 주소를 주지 않았습니다.', raw: r.raw };
  return { ok: true, url: u };
}

/** 상태 조회 — BarobillState 가 양수면 성공 */
export async function taxInvoiceState(env, mgtKey) {
  const r = await barobillCall(env, 'GetTaxInvoiceStateEX', { MgtKey: cut(mgtKey, 24) });
  if (!r.ok) return r;
  const pick = (k) => {
    const m = String(r.raw || '').match(new RegExp(`<${k}>([\\s\\S]*?)</${k}>`));
    return m ? m[1].trim() : '';
  };
  const state = Number(pick('BarobillState') || 0);
  return {
    ok: state > 0, state,
    label: TI_STATE[state] || `상태 ${state}`,
    nts_confirm: pick('NTSConfirmNum'),
    mgt_key: pick('MgtKey') || mgtKey,
  };
}
