// GET  /api/admin/settlement                → 후불 거래처 요약 목록
// GET  /api/admin/settlement?customer_id=   → 한 거래처 상세(원장 포함)
// POST /api/admin/settlement                → 입금/조정 기록 · 후불 전환
import { json, isAdmin, needAdmin, kstISO, kstDate } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

export async function onRequest({ request, env }) {
  if (!isAdmin(request, env)) return needAdmin();

  if (request.method === 'GET') {
    const cid = new URL(request.url).searchParams.get('customer_id');

    if (cid) {
      const c = await env.DB.prepare('SELECT * FROM customers WHERE id=?').bind(cid).first();
      if (!c) return json({ error: 'not_found' }, 404);
      const s = await settlement(env, c.id);
      const rows = await ledger(env, c.id);
      return json({ customer: c, ...s, ledger: rows });
    }

    if (new URL(request.url).searchParams.get('requests')) {
      const { results } = await env.DB.prepare(
        `SELECT s.*, c.name AS contact, c.company
           FROM settlements s JOIN customers c ON c.id = s.customer_id
          ORDER BY s.id DESC LIMIT 200`
      ).all();
      return json({ requests: (results || []).map((r) => ({ ...r, items: safeJson(r.items_json) })) });
    }

    const { results } = await env.DB.prepare(
      `SELECT c.id, c.name, c.company, c.phone, c.billing_mode,
              COALESCE((SELECT SUM(o.total_amount) FROM orders o
                         WHERE o.customer_id=c.id AND o.status<>'취소'),0) AS spent,
              COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS paid
         FROM customers c
        ORDER BY (c.billing_mode='후불') DESC, c.id DESC`
    ).all();
    const list = (results || []).map((r) => ({ ...r, due: (r.spent || 0) - (r.paid || 0) }));
    return json({ customers: list });
  }

  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);
  const b = await request.json().catch(() => ({}));

  // 후불/선불 전환
  if (b.action === 'mode') {
    const mode = b.billing_mode === '후불' ? '후불' : '선불';
    await env.DB.prepare('UPDATE customers SET billing_mode=?, updated_at=? WHERE id=?')
      .bind(mode, kstISO(), b.customer_id).run();
    return json({ ok: true, billing_mode: mode });
  }

  // 입금 / 조정 기록
  if (b.action === 'pay') {
    const amount = Math.round(Number(b.amount) || 0);
    if (!b.customer_id) return json({ error: 'no_customer' }, 400);
    if (!amount) return json({ error: 'no_amount', message: '금액을 입력해주세요.' }, 400);
    const kind = b.kind === '조정' ? '조정' : '입금';
    await env.DB.prepare(
      'INSERT INTO payments (customer_id, kind, amount, method, paid_at, memo, created_at, created_by) VALUES (?,?,?,?,?,?,?,?)'
    ).bind(b.customer_id, kind, amount, String(b.method || '통장'),
           String(b.paid_at || kstDate()), String(b.memo || ''), kstISO(), 'admin').run();
    const s = await settlement(env, b.customer_id);
    return json({ ok: true, ...s });
  }

  // 정산 요청 상태 변경
  if (b.action === 'settle_status') {
    const ok = ['정산요청', '처리중', '서류발급 완료', '입금완료', '반려'].includes(b.status);
    if (!ok) return json({ error: 'bad_status' }, 400);
    const done = b.status === '입금완료' ? kstISO() : null;
    await env.DB.prepare('UPDATE settlements SET status=?, admin_memo=?, done_at=?, updated_at=? WHERE id=?')
      .bind(b.status, String(b.admin_memo || ''), done, kstISO(), b.settlement_id).run();
    return json({ ok: true });
  }

  if (b.action === 'delete_pay') {
    await env.DB.prepare('DELETE FROM payments WHERE id=?').bind(b.payment_id).run();
    return json({ ok: true });
  }

  return json({ error: 'unknown_action' }, 400);
}

function safeJson(s) { try { return JSON.parse(s || '[]'); } catch { return []; } }
