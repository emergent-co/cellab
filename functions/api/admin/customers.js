// GET  /api/admin/customers            → 거래처 목록 (승인 대기가 위로)
// POST /api/admin/customers  {id, access}  → 승인 / 대기 / 거절
// GET  /api/admin/customers?inquiries=1   → 견적 문의 목록
import { json, isAdmin, needAdmin, kstISO, logEvent } from '../_lib.js';

export async function onRequest({ request, env }) {
  if (!isAdmin(request, env)) return needAdmin();
  const p = new URL(request.url).searchParams;

  if (request.method === 'GET') {
    if (p.get('inquiries')) {
      const { results } = await env.DB.prepare(
        'SELECT * FROM inquiries ORDER BY id DESC LIMIT 100'
      ).all();
      return json({ inquiries: (results || []).map((r) => ({ ...r, items: safe(r.items_json) })) });
    }
    const { results } = await env.DB.prepare(
      `SELECT c.id, c.name, c.email, c.work_email, c.phone, c.company, c.access,
              c.billing_mode, c.created_at, l.name AS lab_name, l.code AS lab_code,
              (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id) AS n_orders
         FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
        ORDER BY (c.access='대기') DESC, c.id DESC LIMIT 200`
    ).all();
    return json({ customers: results || [] });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  const b = await request.json().catch(() => ({}));
  const id = Number(b.id);
  const access = ['대기', '승인', '거절'].includes(b.access) ? b.access : null;
  if (!id || !access) return json({ error: 'bad_request' }, 400);

  const c = await env.DB.prepare('SELECT id, name, company FROM customers WHERE id=?').bind(id).first();
  if (!c) return json({ error: 'not_found' }, 404);

  await env.DB.prepare('UPDATE customers SET access=?, updated_at=? WHERE id=?')
    .bind(access, kstISO(), id).run();
  await logEvent(env, {
    action: 'access', actor: 'admin',
    detail: `${c.name || ''}${c.company ? ` (${c.company})` : ''} → ${access}`,
  });
  return json({ ok: true });
}

function safe(t) { try { return JSON.parse(t || '[]') || []; } catch (e) { return []; } }
