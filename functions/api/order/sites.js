// 납품지(소속 + 주소) 목록 — 고객이 라디오로 골라 쓰고, 필요할 때 추가한다.
//   GET    /api/order/sites
//   POST   /api/order/sites      { org_name, address, is_default }
//   DELETE /api/order/sites?id=
import { json, currentCustomer, kstISO } from '../_lib.js';

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

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
  const org = String(b.org_name || '').trim();
  const road = String(b.address || '').trim();          // 카카오(다음) 주소검색 결과
  const post = String(b.postcode || '').trim();
  const detail = String(b.address_detail || '').trim();
  if (!org) return json({ error: 'no_org', message: '소속(기관·연구실)을 입력해주세요.' }, 400);
  if (!road) return json({ error: 'no_address', message: '주소 검색으로 주소를 선택해주세요.' }, 400);
  // 표시·문서용 한 줄 주소
  const addr = (post ? `[${post}] ` : '') + road + (detail ? ', ' + detail : '');

  const cnt = (await env.DB.prepare('SELECT COUNT(*) AS c FROM sites WHERE customer_id=?').bind(me.id).first())?.c || 0;
  if (cnt >= 10) return json({ error: 'too_many', message: '납품지는 최대 10개까지 저장할 수 있습니다.' }, 400);

  const isDefault = b.is_default || cnt === 0 ? 1 : 0;
  if (isDefault) await env.DB.prepare('UPDATE sites SET is_default=0 WHERE customer_id=?').bind(me.id).run();

  const r = await env.DB.prepare(
    `INSERT INTO sites (customer_id, org_name, address, postcode, address_detail, is_default, created_at)
     VALUES (?,?,?,?,?,?,?)`
  ).bind(me.id, org, addr, post, detail, isDefault, kstISO()).run();

  // 아직 실험실이 없으면 이 소속으로 하나 만들고 소속시킨다(초대 코드가 여기서 생긴다)
  if (!me.lab_id) {
    const code = await freshCode(env);
    const lr = await env.DB.prepare('INSERT INTO labs (code, name, created_by, created_at) VALUES (?,?,?,?)')
      .bind(code, org, me.id, kstISO()).run();
    await env.DB.prepare('UPDATE customers SET lab_id=?, company=?, updated_at=? WHERE id=?')
      .bind(lr.meta.last_row_id, org, kstISO(), me.id).run();
  }

  return json({ ok: true, id: r.meta.last_row_id });
}

async function freshCode(env) {
  const AB = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  for (let t = 0; t < 12; t++) {
    const bytes = new Uint8Array(6);
    crypto.getRandomValues(bytes);
    const code = [...bytes].map((b) => AB[b % AB.length]).join('');
    const dup = await env.DB.prepare('SELECT id FROM labs WHERE code=?').bind(code).first();
    if (!dup) return code;
  }
  return 'L' + Date.now().toString(36).toUpperCase().slice(-5);
}
