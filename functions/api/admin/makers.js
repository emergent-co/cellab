// functions/api/admin/makers.js — 제조사(공급처) 담당자 명부
//   GET                     → 목록
//   POST {action:'save'}    → 등록·수정 (이름+이메일이 같으면 덮어쓴다)
//   POST {action:'delete'}  → 삭제
//
// 고객에게 견적서를 쓰기 전에 «재고·납기·가격»을 제조사에 물어보는데,
// 그때마다 담당자 이름·직책·메일을 다시 찾는 게 일이라 여기 모아 둔다.
import { json, needAdmin, adminOK, kstISO, logEvent } from '../_lib.js';

let ready = false;
async function ensure(env) {
  if (ready) return;
  // D1 에 마이그레이션 도구가 따로 없어 첫 호출 때 만든다 — 있으면 그냥 지나간다
  await env.DB.prepare(
    `CREATE TABLE IF NOT EXISTS makers (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL,        -- 제조사 이름
       contact TEXT,              -- 담당자
       title TEXT,                -- 직책
       email TEXT,
       phone TEXT,
       memo TEXT,
       created_at TEXT, updated_at TEXT)`).run().catch(() => {});
  ready = true;
}

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  await ensure(env);

  if (request.method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT * FROM makers ORDER BY name, contact').all();
    return json({ makers: results || [] });
  }
  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const now = kstISO();

  if (b.action === 'delete') {
    const r = await env.DB.prepare('SELECT name, contact FROM makers WHERE id=?').bind(b.id).first();
    if (!r) return json({ error: 'not_found' }, 404);
    await env.DB.prepare('DELETE FROM makers WHERE id=?').bind(b.id).run();
    await logEvent(env, { action: 'maker_delete', actor: 'admin',
      detail: `제조사 ${r.name} ${r.contact || ''} 삭제` });
    return json({ ok: true });
  }

  if (b.action === 'save') {
    const name = String(b.name || '').trim();
    const email = String(b.email || '').trim();
    if (!name) return json({ error: 'no_name', message: '제조사 이름을 입력해주세요.' }, 400);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'bad_email', message: '이메일 형식을 확인해주세요.' }, 400);
    }
    const args = [name, String(b.contact || '').trim(), String(b.title || '').trim(),
                  email, String(b.phone || '').trim(), String(b.memo || '').trim()];

    /* 같은 제조사에 담당자가 여럿일 수 있다(영업·기술).
       그래서 «이름»만으로 합치지 않고 «이름 + 메일»이 같을 때만 같은 사람으로 본다. */
    const hit = b.id
      ? await env.DB.prepare('SELECT id FROM makers WHERE id=?').bind(b.id).first()
      : (email
         ? await env.DB.prepare('SELECT id FROM makers WHERE name=? AND email=?').bind(name, email).first()
         : null);
    if (hit) {
      await env.DB.prepare(
        'UPDATE makers SET name=?, contact=?, title=?, email=?, phone=?, memo=?, updated_at=? WHERE id=?')
        .bind(...args, now, hit.id).run();
      await logEvent(env, { action: 'maker_edit', actor: 'admin', detail: `제조사 ${name} 수정` });
      return json({ ok: true, id: hit.id });
    }
    const r = await env.DB.prepare(
      `INSERT INTO makers (name, contact, title, email, phone, memo, created_at, updated_at)
       VALUES (?,?,?,?,?,?,?,?)`).bind(...args, now, now).run();
    await logEvent(env, { action: 'maker_add', actor: 'admin', detail: `제조사 ${name} 등록` });
    return json({ ok: true, id: r.meta.last_row_id });
  }

  return json({ error: 'unknown_action' }, 400);
}
