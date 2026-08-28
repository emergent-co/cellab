// GET /api/admin/orders?stats=1
// GET /api/admin/orders?status=&q=&page=&size=
import { json, isAdmin, needAdmin, STATUSES, adminOK} from '../../_lib.js';

export async function onRequestGet({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  const p = new URL(request.url).searchParams;

  if (p.get('stats')) {
    const { results } = await env.DB.prepare('SELECT status, COUNT(*) AS c FROM orders GROUP BY status').all();
    const byStatus = {};
    for (const s of STATUSES) byStatus[s] = 0;
    for (const r of results || []) byStatus[r.status] = r.c;
    const total = (results || []).reduce((s, r) => s + r.c, 0);
    return json({ total, byStatus });
  }

  const status = p.get('status') || '';
  const q = (p.get('q') || '').trim();
  const size = Math.min(Number(p.get('size') || 30), 100);
  const page = Math.max(Number(p.get('page') || 1), 1);

  const where = [], vals = [];
  if (status && status !== '전체') { where.push('o.status = ?'); vals.push(status); }
  if (q) {
    where.push('(o.order_no LIKE ? OR o.title LIKE ? OR c.company LIKE ? OR c.name LIKE ?)');
    const like = `%${q}%`; vals.push(like, like, like, like);
  }
  const sql = `SELECT o.id, o.order_no, o.status, o.title, o.want_date, o.total_amount, o.created_at, o.updated_at,
                      c.company, c.name AS contact, c.phone, c.email
                 FROM orders o LEFT JOIN customers c ON c.id = o.customer_id
                ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
                ORDER BY o.id DESC LIMIT ? OFFSET ?`;
  const { results } = await env.DB.prepare(sql).bind(...vals, size, (page - 1) * size).all();
  return json({ orders: results || [], page, size });
}
