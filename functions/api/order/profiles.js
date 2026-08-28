// 고객이 직접 관리하는 "세금계산서 발행 정보" 프로필
//   GET    /api/order/profiles          → 내 프로필 목록
//   POST   /api/order/profiles          → 추가 (기본으로 지정 가능)
//   PUT    /api/order/profiles          → 수정 { id, ... }
//   DELETE /api/order/profiles?id=      → 삭제
// 연구원·대학원생 고객은 주문 시점엔 사업자정보를 모르는 경우가 많아,
// 정산 시점에 스스로 등록하고 다음 주문부터 골라 쓰도록 분리했다.
import { json, currentCustomer, kstISO, memberGate} from '../_lib.js';

const F = ['label', 'company', 'biz_no', 'ceo', 'tax_email', 'address'];

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);
  const gate = memberGate(me); if (gate) return gate;

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id DESC'
    ).bind(me.id).all();
    return json({ profiles: results || [] });
  }

  if (request.method === 'DELETE') {
    const id = new URL(request.url).searchParams.get('id');
    await env.DB.prepare('DELETE FROM bill_profiles WHERE id=? AND customer_id=?').bind(id, me.id).run();
    await env.DB.prepare('UPDATE orders SET bill_profile_id=NULL WHERE bill_profile_id=? AND customer_id=?').bind(id, me.id).run();
    return json({ ok: true });
  }

  const b = await request.json().catch(() => ({}));
  const company = String(b.company || '').trim();
  const bizNo = normBizNo(b.biz_no);
  if (!company) return json({ error: 'no_company', message: '상호(기관명)를 입력해주세요.' }, 400);
  if (bizNo && bizNo.replace(/-/g, '').length !== 10) {
    return json({ error: 'bad_biz_no', message: '사업자등록번호는 10자리입니다.' }, 400);
  }

  const vals = {};
  for (const f of F) vals[f] = String(b[f] || '').trim();
  vals.company = company;
  vals.biz_no = bizNo;
  vals.label = vals.label || company;

  if (request.method === 'POST') {
    const cnt = (await env.DB.prepare('SELECT COUNT(*) AS c FROM bill_profiles WHERE customer_id=?').bind(me.id).first())?.c || 0;
    if (cnt >= 10) return json({ error: 'too_many', message: '최대 10개까지 저장할 수 있습니다.' }, 400);
    const isDefault = b.is_default || cnt === 0 ? 1 : 0;
    if (isDefault) await env.DB.prepare('UPDATE bill_profiles SET is_default=0 WHERE customer_id=?').bind(me.id).run();
    const r = await env.DB.prepare(
      `INSERT INTO bill_profiles (customer_id, label, company, biz_no, ceo, tax_email, address, is_default, created_at, updated_at)
       VALUES (?,?,?,?,?,?,?,?,?,?)`
    ).bind(me.id, vals.label, vals.company, vals.biz_no, vals.ceo,
           vals.tax_email, vals.address, isDefault, kstISO(), kstISO()).run();
    return json({ ok: true, id: r.meta.last_row_id });
  }

  if (request.method === 'PUT') {
    const own = await env.DB.prepare('SELECT id FROM bill_profiles WHERE id=? AND customer_id=?').bind(b.id, me.id).first();
    if (!own) return json({ error: 'not_found' }, 404);
    if (b.is_default) await env.DB.prepare('UPDATE bill_profiles SET is_default=0 WHERE customer_id=?').bind(me.id).run();
    await env.DB.prepare(
      `UPDATE bill_profiles SET label=?, company=?, biz_no=?, ceo=?,
              tax_email=?, address=?, is_default=?, updated_at=? WHERE id=? AND customer_id=?`
    ).bind(vals.label, vals.company, vals.biz_no, vals.ceo,
           vals.tax_email, vals.address, b.is_default ? 1 : 0, kstISO(), b.id, me.id).run();
    return json({ ok: true });
  }

  return json({ error: 'method_not_allowed' }, 405);
}

// 000-00-00000 형태로 정규화
function normBizNo(v) {
  const d = String(v || '').replace(/[^0-9]/g, '');
  if (d.length !== 10) return String(v || '').trim();
  return `${d.slice(0, 3)}-${d.slice(3, 5)}-${d.slice(5)}`;
}
