// GET  /api/admin/settlement                → 후불 거래처 요약 목록
// GET  /api/admin/settlement?customer_id=   → 한 거래처 상세(원장 포함)
// POST /api/admin/settlement                → 입금/조정 기록 · 후불 전환
import { json, isAdmin, needAdmin, kstISO, kstDate, adminOK, logEvent } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();

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
        `SELECT s.*, c.name AS contact, c.company, c.alias
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

  // 정산 요청을 관리자가 직접 만들거나 고친다 — 옮겨 적는 이력, 전화로 받은 요청 등
  if (b.action === 'settle_save') {
    if (!b.customer_id) return json({ error: 'no_client', message: '거래처를 선택해주세요.' }, 400);
    const items = (Array.isArray(b.items) ? b.items : [])
      .map((i) => ({ name: String(i.name || '').trim(),
                     qty: Math.max(1, Number(i.qty) || 1),
                     price: Math.round(Number(i.price) || 0) }))
      .filter((i) => i.name);
    if (!items.length) return json({ error: 'no_items', message: '항목을 1개 이상 넣어주세요.' }, 400);

    // 금액 규칙은 고객이 넣는 것과 똑같이 — 부가세 포함 총액을 먼저 확정하고 역산한다
    const r10 = (n) => Math.round(Number(n || 0) / 10) * 10;
    const total = items.reduce((s2, i) => s2 + r10(i.qty * i.price), 0);
    const supply = Math.round(total / 1.1);
    const vat = total - supply;

    const ok = ['정산요청', '처리중', '서류발급 완료', '입금완료', '반려'];
    const status = ok.includes(b.status) ? b.status : '정산요청';
    const method = b.method === '카드' ? '카드' : '통장';
    const day = String(b.trade_date || '').slice(0, 10);
    const at = /^\d{4}-\d{2}-\d{2}$/.test(day) ? `${day} 00:00:00` : kstISO();
    const done = status === '입금완료' ? kstISO() : null;

    // 발행정보는 그 거래처 것만
    let billId = Number(b.bill_profile_id) || null;
    if (billId) {
      const own = await env.DB.prepare('SELECT id FROM bill_profiles WHERE id=? AND customer_id=?')
        .bind(billId, b.customer_id).first();
      if (!own) billId = null;
    }

    if (b.settlement_id) {
      await env.DB.prepare(
        `UPDATE settlements SET customer_id=?, status=?, items_json=?, supply=?, vat=?, total=?, method=?,
                quote_date=?, statement_date=?, taxinvoice_date=?, reply_email=?, memo=?, admin_memo=?,
                bill_profile_id=?, created_at=?, done_at=?, updated_at=? WHERE id=?`
      ).bind(b.customer_id, status, JSON.stringify(items), supply, vat, total, method,
             b.quote_date || null, b.statement_date || null, b.taxinvoice_date || null,
             String(b.reply_email || ''), String(b.memo || ''), String(b.admin_memo || ''),
             billId, at, done, kstISO(), b.settlement_id).run();
      await logEvent(env, { action: 'settle_edit', actor: 'admin', detail: `정산 #${b.settlement_id} 수정` });
      return json({ ok: true, id: b.settlement_id, supply, vat, total });
    }

    const r = await env.DB.prepare(
      `INSERT INTO settlements (customer_id, status, items_json, supply, vat, total, method,
              quote_date, statement_date, taxinvoice_date, reply_email, memo, admin_memo,
              bill_profile_id, manual, created_at, updated_at, done_at)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, 1, ?,?,?)`
    ).bind(b.customer_id, status, JSON.stringify(items), supply, vat, total, method,
           b.quote_date || null, b.statement_date || null, b.taxinvoice_date || null,
           String(b.reply_email || ''), String(b.memo || ''), String(b.admin_memo || ''),
           billId, at, kstISO(), done).run();
    await logEvent(env, { action: 'settle_add', actor: 'admin',
      detail: `정산 직접 입력 ${items[0].name}${items.length > 1 ? ` 외 ${items.length - 1}건` : ''} · ${total.toLocaleString('ko-KR')}원` });
    return json({ ok: true, id: r.meta.last_row_id, supply, vat, total });
  }

  if (b.action === 'settle_delete') {
    if (!b.settlement_id) return json({ error: 'no_id' }, 400);
    await env.DB.prepare('DELETE FROM settlements WHERE id=?').bind(b.settlement_id).run();
    await logEvent(env, { action: 'settle_delete', actor: 'admin', detail: `정산 #${b.settlement_id} 삭제` });
    return json({ ok: true, deleted: true });
  }

  if (b.action === 'delete_pay') {
    await env.DB.prepare('DELETE FROM payments WHERE id=?').bind(b.payment_id).run();
    return json({ ok: true });
  }

  return json({ error: 'unknown_action' }, 400);
}

function safeJson(s) { try { return JSON.parse(s || '[]'); } catch { return []; } }
