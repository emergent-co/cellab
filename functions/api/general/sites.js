// 일반회원 배송지 — 멤버십의 «납품지»와 같은 sites 테이블을 쓴다.
//   GET    /api/general/sites
//   POST   /api/general/sites      { org_name, address, postcode, address_detail, is_default }
//   DELETE /api/general/sites?id=
// /api/order/sites 와 다른 점: 실험실(labs)을 만들지 않는다. 일반회원에게는 없는 개념이다.
import { json, currentCustomer, kstISO, generalGate } from '../_lib.js';

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  const gate = generalGate(me); if (gate) return gate;

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT * FROM sites WHERE customer_id=? ORDER BY is_default DESC, id DESC'
    ).bind(me.id).all();
    return json({ sites: results || [] });
  }

  if (request.method === 'DELETE') {
    const id = new URL(request.url).searchParams.get('id');
    await env.DB.prepare('DELETE FROM sites WHERE id=? AND customer_id=?').bind(id, me.id).run();
    return json({ ok: true });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const org    = String(b.org_name || '').trim();
  const road   = String(b.address || '').trim();
  const post   = String(b.postcode || '').trim();
  const detail = String(b.address_detail || '').trim();
  if (!org)  return json({ error: 'no_org', message: '받는 곳(소속·이름)을 입력해주세요.' }, 400);
  if (!road) return json({ error: 'no_address', message: '주소 검색으로 주소를 선택해주세요.' }, 400);
  const addr = (post ? `[${post}] ` : '') + road + (detail ? ', ' + detail : '');

  const cnt = (await env.DB.prepare('SELECT COUNT(*) AS c FROM sites WHERE customer_id=?').bind(me.id).first())?.c || 0;
  if (cnt >= 10) return json({ error: 'too_many', message: '배송지는 최대 10개까지 저장할 수 있습니다.' }, 400);

  const isDefault = b.is_default || cnt === 0 ? 1 : 0;
  if (isDefault) await env.DB.prepare('UPDATE sites SET is_default=0 WHERE customer_id=?').bind(me.id).run();

  const r = await env.DB.prepare(
    `INSERT INTO sites (customer_id, org_name, address, postcode, address_detail, is_default, created_at)
     VALUES (?,?,?,?,?,?,?)`
  ).bind(me.id, org, addr, post, detail, isDefault, kstISO()).run();

  return json({ ok: true, id: r.meta.last_row_id });
}
