// 실험실(랩) — 같은 랩끼리 주문 이력을 공유한다.
//   소속명 글자 비교는 오타 하나로 깨지므로 코드로 묶는다.
//   GET  /api/order/lab            → 내 랩 정보 + 구성원
//   POST /api/order/lab {name}     → 랩 생성(없을 때) 또는 이름 변경
//   POST /api/order/lab {code}     → 초대 코드로 합류
import { json, currentCustomer, kstISO, logEvent } from '../_lib.js';

export async function onRequest({ request, env }) {
  const me = await currentCustomer(request, env);
  if (!me) return json({ error: 'login_required' }, 401);

  if (request.method === 'GET') {
    // 합류하기 전에 "어떤 실험실인지"만 확인 — 이름과 인원수만 준다
    const peek = new URL(request.url).searchParams.get('peek');
    if (peek) {
      const lab = await env.DB.prepare('SELECT id, name FROM labs WHERE code=?')
        .bind(String(peek).trim().toUpperCase()).first();
      if (!lab) return json({ found: false });
      const n = (await env.DB.prepare('SELECT COUNT(*) AS c FROM customers WHERE lab_id=?').bind(lab.id).first())?.c || 0;
      return json({ found: true, name: lab.name, members: n, mine: me.lab_id === lab.id });
    }
    return json(await labInfo(env, me));
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);
  const b = await request.json().catch(() => ({}));

  // ---- 초대 코드로 합류 ----
  if (b.code) {
    const code = String(b.code).trim().toUpperCase();
    const lab = await env.DB.prepare('SELECT * FROM labs WHERE code=?').bind(code).first();
    if (!lab) return json({ error: 'bad_code', message: '초대 코드를 찾을 수 없습니다.' }, 404);
    if (me.lab_id === lab.id) return json({ ok: true, joined: false, ...(await labInfo(env, me)) });

    await env.DB.prepare('UPDATE customers SET lab_id=?, company=COALESCE(NULLIF(company,\'\'), ?), updated_at=? WHERE id=?')
      .bind(lab.id, lab.name, kstISO(), me.id).run();
    await logEvent(env, { action: 'lab_join', actor: 'customer', detail: `${me.name || ''} 님이 ${lab.name} 에 합류` });
    const fresh = await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(me.id).first();
    return json({ ok: true, joined: true, ...(await labInfo(env, fresh)) });
  }

  // ---- 서비스 추천으로 들어온 경우: 실험실에는 넣지 않는다 ----
  if (b.ref) {
    if (!me.referred_by) {
      await env.DB.prepare('UPDATE customers SET referred_by=?, updated_at=? WHERE id=?')
        .bind(String(b.ref).trim().toUpperCase(), kstISO(), me.id).run();
    }
    return json({ ok: true, referred: true });
  }

  // ---- 실험실에서 나가기 ----
  if (b.leave) {
    await env.DB.prepare('UPDATE customers SET lab_id=NULL, updated_at=? WHERE id=?').bind(kstISO(), me.id).run();
    return json({ ok: true, lab: null, members: [] });
  }

  // ---- 생성 / 이름 변경 ----
  const name = String(b.name || '').trim();
  if (!name) return json({ error: 'no_name', message: '실험실 이름을 입력해주세요.' }, 400);

  if (me.lab_id) {
    await env.DB.prepare('UPDATE labs SET name=? WHERE id=?').bind(name, me.lab_id).run();
  } else {
    const code = await freshCode(env);
    const r = await env.DB.prepare('INSERT INTO labs (code, name, created_by, created_at) VALUES (?,?,?,?)')
      .bind(code, name, me.id, kstISO()).run();
    await env.DB.prepare('UPDATE customers SET lab_id=?, updated_at=? WHERE id=?')
      .bind(r.meta.last_row_id, kstISO(), me.id).run();
  }
  const fresh = await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(me.id).first();
  return json({ ok: true, ...(await labInfo(env, fresh)) });
}

/**
 * 실험실이 없으면 만들어 붙인다.
 *   원래는 납품지를 처음 등록할 때만 만들었는데, 그때 실패하면 영영 실험실이 없는 상태가 된다
 *   (초대하기가 계속 막힌다). 그래서 납품지가 하나라도 있으면 언제든 다시 만들어준다.
 * 실패해도 호출한 쪽을 죽이지 않는다.
 */
export async function ensureLab(env, me) {
  if (!me || me.lab_id) return me?.lab_id || null;
  try {
    const site = await env.DB.prepare(
      'SELECT org_name FROM sites WHERE customer_id=? ORDER BY is_default DESC, id LIMIT 1'
    ).bind(me.id).first();
    if (!site) return null;                       // 납품지가 없으면 아직 만들 때가 아니다
    const code = await freshCode(env);
    const name = site.org_name || me.company || '내 실험실';
    const r = await env.DB.prepare(
      'INSERT INTO labs (code, name, created_by, created_at) VALUES (?,?,?,?)'
    ).bind(code, name, me.id, kstISO()).run();
    const labId = r.meta.last_row_id;
    await env.DB.prepare('UPDATE customers SET lab_id=?, updated_at=? WHERE id=?')
      .bind(labId, kstISO(), me.id).run();
    me.lab_id = labId;
    return labId;
  } catch (e) {
    return null;
  }
}

export async function labInfo(env, me) {
  if (!me.lab_id) await ensureLab(env, me);
  if (!me.lab_id) return { lab: null, members: [] };
  const lab = await env.DB.prepare('SELECT * FROM labs WHERE id=?').bind(me.lab_id).first();
  if (!lab) return { lab: null, members: [] };
  const members = (await env.DB.prepare(
    'SELECT id, name, email, created_at FROM customers WHERE lab_id=? ORDER BY id'
  ).bind(lab.id).all()).results || [];
  return { lab: { id: lab.id, code: lab.code, name: lab.name }, members };
}

// 사람이 부르기 쉬운 6자리 (헷갈리는 0/O/1/I 제외)
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

// 같은 랩 사람들의 customer_id — 이력 공유 기준
export async function labMateIds(env, me) {
  if (!me.lab_id) return [me.id];
  const { results } = await env.DB.prepare('SELECT id FROM customers WHERE lab_id=?').bind(me.lab_id).all();
  const ids = (results || []).map((r) => r.id);
  return ids.length ? ids : [me.id];
}
