// GET /api/admin/barobill              → 설정 진단 (키는 안 내보낸다)
// GET /api/admin/barobill?call=<메서드> → 임의 메서드 호출 (테스트 모드에서만)
//     추가 인자는 그대로 쿼리로: ?call=GetCorpState&CheckCorpNum=1234567890
//
// 스펙 문서를 받기 전까지 «키가 살아 있는지»를 눈으로 확인하는 용도다.
import { json, needAdmin, adminOK } from '../_lib.js';
import { barobillDiag, barobillCall, barobillConfig } from '../_barobill.js';

export async function onRequestGet({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  const u = new URL(request.url).searchParams;
  const method = (u.get('call') || '').trim();

  if (!method) return json({ ok: true, diag: barobillDiag(env) });

  // 운영 키로 아무 메서드나 쏘게 두지 않는다 — 발행 계열이 섞이면 실제 계산서가 나간다
  if (!barobillConfig(env).test) {
    return json({ error: 'live_mode',
      message: '운영 모드에서는 이 시험 호출을 막습니다. BAROBILL_MODE 를 test 로 두고 시도하세요.' }, 400);
  }
  if (!/^[A-Za-z][A-Za-z0-9_]{0,60}$/.test(method)) return json({ error: 'bad_method' }, 400);

  const args = {};
  u.forEach((v, k) => { if (k !== 'call') args[k] = v; });

  const r = await barobillCall(env, method, args);
  return json({ method, mode: 'test', ...r, raw: r.raw ? String(r.raw).slice(0, 1500) : undefined });
}
