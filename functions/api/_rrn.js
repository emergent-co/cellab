// functions/api/_rrn.js — 주민등록번호 저장 암호화 (AES-GCM)
//
// 개인정보보호법 제24조의2 제2항 · 시행령 제21조의2 는 주민등록번호를
// «저장할 때» 암호화하도록 정하고 있다. DB 를 통째로 들여다봐도 번호가 안 보여야 한다.
//
// 키는 Cloudflare Secret 으로 넣는다:  RRN_KEY = base64 32바이트
//   node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
//
// 키를 바꾸면 기존 값을 못 읽는다 — 한 번 정하면 바꾸지 않는다.
// 키가 없으면 «암호화 없이 그대로» 동작한다. 기능이 멈추는 것보다 낫고,
// 관리자 화면이 «암호화 꺼짐»을 빨간 글씨로 알려준다.

const ENC = new TextEncoder();
const DEC = new TextDecoder();

export function rrnKeyOn(env) { return !!env.RRN_KEY; }

const b64e = (buf) => {
  let s = '';
  const b = new Uint8Array(buf);
  for (let i = 0; i < b.length; i += 1) s += String.fromCharCode(b[i]);
  return btoa(s);
};
const b64d = (str) => {
  const s = atob(str);
  const b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i += 1) b[i] = s.charCodeAt(i);
  return b;
};

let keyCache = null;
async function getKey(env) {
  if (keyCache) return keyCache;
  const raw = b64d(String(env.RRN_KEY || ''));
  if (raw.length !== 32) throw new Error('RRN_KEY 는 base64 32바이트여야 합니다');
  keyCache = await crypto.subtle.importKey('raw', raw, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
  return keyCache;
}

/** 숫자 13자리 → 'v1:<base64(iv|ct)>'. 키가 없거나 빈 값이면 그대로 돌려준다. */
export async function rrnEnc(env, plain) {
  const v = String(plain || '').replace(/[^0-9]/g, '');
  if (!v || !rrnKeyOn(env)) return v;
  try {
    const key = await getKey(env);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, ENC.encode(v));
    const out = new Uint8Array(iv.length + ct.byteLength);
    out.set(iv, 0); out.set(new Uint8Array(ct), iv.length);
    return `v1:${b64e(out)}`;
  } catch (e) {
    // 암호화가 안 되면 저장을 «포기»한다 — 평문으로 슬쩍 넣는 게 제일 나쁘다
    throw new Error(`주민번호 암호화 실패: ${e.message}`);
  }
}

/** 저장값 → 숫자 13자리. 예전에 평문으로 넣어 둔 값은 그대로 통과시킨다. */
export async function rrnDec(env, stored) {
  const s = String(stored || '');
  if (!s) return '';
  if (!s.startsWith('v1:')) return s.replace(/[^0-9]/g, '');   // 마이그레이션 전 평문
  if (!rrnKeyOn(env)) return '';                               // 키가 없으면 못 읽는다
  try {
    const key = await getKey(env);
    const all = b64d(s.slice(3));
    const pt = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: all.slice(0, 12) }, key, all.slice(12));
    return DEC.decode(pt);
  } catch (e) {
    return '';
  }
}

/** 880101-1****** — 뒤 6자리는 어디에도 내보내지 않는다 */
export function maskDigits(v) {
  const d = String(v || '').replace(/[^0-9]/g, '');
  if (!d) return '';
  if (d.length < 7) return `${d.slice(0, 6)}-*******`;
  return `${d.slice(0, 6)}-${d[6]}******`;
}
