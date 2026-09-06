// functions/api/admin/clients.js — 거래처 관리
//   한 거래처를 통으로 본다: 기본정보 · 실험실 · 발행정보 · 주문 · 정산 · 문서 · 잔여금.
//   GET  ?q=&access=&mode=   목록
//   GET  ?id=<id>            상세
//   POST { id, action }      access · mode · memo · profile(연락처 수정)
//   권한(role)은 여기서 못 바꾼다 — DB에서 직접만. 화면을 타고 관리자가 번지지 않게.
import { json, needAdmin, adminOK, kstISO, logEvent } from '../_lib.js';
import { settlement, ledger } from '../_settle.js';

// '거래처' = 로그인 계정이 아니라 서류 발행용으로만 들고 있는 곳(기존 사이트에서 옮겨온 것).
// 멤버십 권한은 없다 — isMember() 는 '승인' 만 통과시킨다.
const ACCESS = ['승인', '일반', '대기', '거절', '거래처'];   // '대기'는 옛 값(= '일반')
const safe = (s) => { try { return JSON.parse(s || '[]'); } catch { return []; } };

export async function onRequest({ request, env }) {
  if (!(await adminOK(request, env))) return needAdmin();
  if (request.method === 'GET') return get(request, env);
  if (request.method === 'POST') return post(request, env);
  return json({ error: 'method_not_allowed' }, 405);
}

async function get(request, env) {
  const u = new URL(request.url).searchParams;

  // ---------------- 상세 ----------------
  if (u.get('id')) {
    const c = await env.DB.prepare(
      `SELECT c.*, l.name AS lab_name, l.code AS lab_code
         FROM customers c LEFT JOIN labs l ON l.id=c.lab_id WHERE c.id=?`).bind(u.get('id')).first();
    if (!c) return json({ error: 'not_found' }, 404);

    // 아래 다섯 개는 batch 한 번, 합계·원장은 각자 이미 batch 로 묶여 있다
    const [profiles, contacts, sites, orders, settles, docs, members, sum, led] = await Promise.all([
      env.DB.prepare('SELECT * FROM bill_profiles WHERE customer_id=? ORDER BY is_default DESC, id')
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(
        `SELECT ct.*, s.org_name AS site_name, s.address AS site_addr
           FROM contacts ct LEFT JOIN sites s ON s.id = ct.site_id
          WHERE ct.customer_id=? ORDER BY ct.is_default DESC, ct.id`)
        .bind(c.id).all().then((r) => r.results || []),
      // 고객은 사업자정보를 «계산서 발행 정보»에, 주소를 «납품지»에 넣는다.
      // 거래처 기본칸만 보면 늘 비어 보이므로 둘 다 함께 보낸다.
      env.DB.prepare('SELECT * FROM sites WHERE customer_id=? ORDER BY is_default DESC, id')
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, order_no, title, status, total_amount, manual, created_at
                        FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      // 수정 폼에서 그대로 쓸 수 있게 필요한 칸을 다 실어 보낸다
      env.DB.prepare(`SELECT id, status, items_json, supply, vat, total, method, manual,
                             quote_date, statement_date, taxinvoice_date, bill_profile_id,
                             memo, admin_memo, created_at
                        FROM settlements WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      env.DB.prepare(`SELECT id, type, doc_no, status, issue_date, access_token, payload_json
                        FROM documents WHERE customer_id=? ORDER BY id DESC LIMIT 20`)
        .bind(c.id).all().then((r) => r.results || []),
      c.lab_id
        ? env.DB.prepare('SELECT id, name, email, work_email, access FROM customers WHERE lab_id=? ORDER BY id')
            .bind(c.lab_id).all().then((r) => r.results || [])
        : Promise.resolve([]),
      settlement(env, c.id),
      ledger(env, c.id, 40),
    ]);

    const { role, kakao_id, ...safeCustomer } = c;   // 카카오 식별자·권한은 화면에 내보내지 않는다
    return json({
      client: { ...safeCustomer, is_admin: role === 'admin' },
      profiles, contacts, sites, orders, members, ledger: led, ...sum,
      settlements: settles.map((s) => ({ ...s, items: safe(s.items_json) })),
      documents: docs.map((d) => {
        let p = {}; try { p = JSON.parse(d.payload_json || '{}'); } catch { /* noop */ }
        // 열람 토큰은 링크로만 내보내고 원본 필드는 지운다
        const { payload_json, access_token, ...rest } = d;
        return { ...rest, title: p.title || '', total: p.totals?.total || 0,
                 view: `/doc/${d.id}?t=${access_token}` };
      }),
    });
  }

  // ---------------- 사업자 단위 목록 (거래처 추가에서 '기존 사업자 찾기') ----------------
  if (u.get('orgs')) {
    const q = (u.get('q') || '').trim();
    const w = ["c.biz_no IS NOT NULL", "c.biz_no <> ''"], bind = [];
    if (q) {
      w.push('(c.company LIKE ? OR c.alias LIKE ? OR c.biz_no LIKE ? OR c.ceo LIKE ?)');
      for (let i = 0; i < 4; i++) bind.push(`%${q}%`);
    }
    // 같은 사업자번호를 쓰는 곳들을 하나로 묶는다. 대표자·주소는 가장 최근에 적어둔 것.
    const { results } = await env.DB.prepare(
      `SELECT c.biz_no,
              MAX(c.company) AS company,
              MAX(c.ceo)     AS ceo,
              MAX(c.address) AS address,
              COUNT(*)       AS n,
              MIN(c.id)      AS any_id
         FROM customers c
        WHERE ${w.join(' AND ')}
        GROUP BY c.biz_no
        ORDER BY n DESC, company
        LIMIT 30`).bind(...bind).all();

    const orgs = [];
    for (const o of results || []) {
      const kids = (await env.DB.prepare(
        'SELECT id, alias, name, work_email FROM customers WHERE biz_no=? ORDER BY id LIMIT 20')
        .bind(o.biz_no).all()).results || [];
      orgs.push({ ...o, children: kids });
    }
    return json({ orgs });
  }

  // ---------------- 목록 ----------------
  const w = [], bind = [];
  const access = u.get('access');
  // '일반'을 고르면 옛 값 '대기'도 같이 보여준다 — 같은 뜻이고 데이터에 둘 다 남아 있다
  if (access === '일반') { w.push("c.access IN ('일반','대기')"); }
  else if (access && ACCESS.includes(access)) { w.push('c.access=?'); bind.push(access); }
  const mode = u.get('mode');
  if (mode === '후불' || mode === '선불') { w.push('c.billing_mode=?'); bind.push(mode); }
  const q = (u.get('q') || '').trim();
  if (q) {
    w.push('(c.name LIKE ? OR c.company LIKE ? OR c.alias LIKE ? OR c.email LIKE ?'
         + ' OR c.work_email LIKE ? OR c.phone LIKE ? OR c.biz_no LIKE ? OR c.memo LIKE ? OR l.name LIKE ?)');
    for (let i = 0; i < 9; i++) bind.push(`%${q}%`);
  }
  const where = w.length ? `WHERE ${w.join(' AND ')}` : '';

  const { results } = await env.DB.prepare(
    `SELECT c.id, c.name, c.company, c.alias, c.biz_no, c.phone, c.email, c.work_email, c.billing_mode,
            c.access, c.memo, c.created_at, l.name AS lab_name,
            COALESCE((SELECT SUM(o.total_amount) FROM orders o
                       WHERE o.customer_id=c.id AND o.status<>'취소'),0) AS spent,
            COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS paid,
            (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.id AND o.status<>'취소') AS orders_n,
            (SELECT MAX(o.created_at) FROM orders o WHERE o.customer_id=c.id) AS last_order,
            (SELECT COUNT(*) FROM documents d WHERE d.customer_id=c.id) AS docs_n
       FROM customers c LEFT JOIN labs l ON l.id=c.lab_id
       ${where}
      ORDER BY (c.access IN ('일반','대기')) DESC, c.company, c.id LIMIT 300`).bind(...bind).all();

  const clients = (results || []).map((r) => ({ ...r, due: (r.spent || 0) - (r.paid || 0) }));
  const stats = (await env.DB.prepare(
    `SELECT SUM(CASE WHEN access='승인' THEN 1 ELSE 0 END) AS ok,
            SUM(CASE WHEN access IN ('일반','대기') THEN 1 ELSE 0 END) AS wait,
            SUM(CASE WHEN access='거절' THEN 1 ELSE 0 END) AS no,
            SUM(CASE WHEN access='거래처' THEN 1 ELSE 0 END) AS client,
            SUM(CASE WHEN billing_mode='후불' THEN 1 ELSE 0 END) AS post,
            COUNT(*) AS all_ FROM customers`).first()) || {};
  return json({ clients, stats });
}

async function post(request, env) {
  const b = await request.json().catch(() => ({}));
  if (b.action === 'create') return create(env, b);
  if (!b.id) return json({ error: 'no_id' }, 400);
  const c = await env.DB.prepare(
    'SELECT id, name, company, billing_mode, role, access, kakao_id FROM customers WHERE id=?'
  ).bind(b.id).first();
  if (!c) return json({ error: 'not_found' }, 404);
  const now = kstISO();
  const who = c.company || c.name || `#${c.id}`;

  /* 담당자가 하나도 없으면 로그인 계정 정보로 첫 줄을 만들어 둔다.
     «계정 주인»을 따로 다루지 않기로 했으니, 그 사람도 그냥 담당자 한 명이어야 한다.
     여기가 아니면 발행 화면에서 보낼 사람이 없어 멈춘다. */
  const seedContact = async () => {
    const has = await env.DB.prepare('SELECT id FROM contacts WHERE customer_id=? LIMIT 1').bind(c.id).first();
    if (has) return;
    const nm = String(c.name || '').trim();
    const em = String(c.work_email || c.email || '').trim();
    if (!nm && !em) return;
    await env.DB.prepare(
      `INSERT INTO contacts (customer_id, name, email, phone, role, is_default, is_tax, created_at, updated_at)
       VALUES (?,?,?,?,'',1,0,?,?)`)
      .bind(c.id, nm || '담당자', em, String(c.phone || ''), now, now).run();
  };

  if (b.action === 'access') {
    if (!ACCESS.includes(b.access)) return json({ error: 'bad_access' }, 400);
    // 결제방식은 여기서 정하지 않는다 — 화면에서 «멤버십(후불)»과 «일반(선불)»을 사람이 골라 따로 보낸다.
    // 예전처럼 승인만 하면 후불로 밀어버리면, 선불로 받으려던 거래처가 조용히 후불 장부에 올라간다.
    await env.DB.prepare('UPDATE customers SET access=?, updated_at=? WHERE id=?')
      .bind(b.access, now, c.id).run();
    if (b.access === '승인') await seedContact();
    await logEvent(env, { action: 'member_access', actor: 'admin',
      detail: `${who} 멤버십 ${b.access}` });
    return json({ ok: true, access: b.access, billing_mode: toPostpaid ? '후불' : c.billing_mode });
  }

  if (b.action === 'mode') {
    const mode = b.billing_mode === '후불' ? '후불' : '선불';
    await env.DB.prepare('UPDATE customers SET billing_mode=?, updated_at=? WHERE id=?').bind(mode, now, c.id).run();
    await logEvent(env, { action: 'billing_mode', actor: 'admin', detail: `${who} ${mode} 전환` });
    await seedContact();
    return json({ ok: true, billing_mode: mode });
  }

  /* 고른 이력만 한 번에 지운다 — 주문 · 정산 요청 · 발행 문서를 섞어서 넘길 수 있다.
     남의 거래처 것이 섞여 들어오지 않도록, 모든 DELETE 에 customer_id 를 함께 건다. */
  if (b.action === 'purge') {
    const ids = (a) => (Array.isArray(a) ? a : []).map(Number)
      .filter((n) => Number.isInteger(n) && n > 0).slice(0, 300);
    const oi = ids(b.orders), si = ids(b.settlements), di = ids(b.documents);
    if (!oi.length && !si.length && !di.length) return json({ error: 'nothing' }, 400);

    const st = [];
    // ① 문서 먼저 — 주문을 지우기 전에 없애야 «연결만 끊기»가 헛돌지 않는다
    if (di.length) {
      const L = di.join(',');
      st.push(env.DB.prepare(`DELETE FROM outbox WHERE document_id IN (${L})`));
      st.push(env.DB.prepare(`UPDATE doc_events SET document_id=NULL WHERE document_id IN (${L})`));
      st.push(env.DB.prepare(`UPDATE todos SET document_id=NULL WHERE document_id IN (${L})`));
      st.push(env.DB.prepare(
        `DELETE FROM documents WHERE id IN (${L})
           AND (customer_id=?1 OR order_id IN (SELECT id FROM orders WHERE customer_id=?1)
                OR settlement_id IN (SELECT id FROM settlements WHERE customer_id=?1))`
      ).bind(c.id));
    }
    // ② 주문 — 남은 문서는 연결만 끊고 살려둔다 (이미 고객에게 나갔을 수 있다)
    if (oi.length) {
      const L = oi.join(',');
      const mine = `(SELECT id FROM orders WHERE id IN (${L}) AND customer_id=${c.id})`;
      st.push(env.DB.prepare(`DELETE FROM order_items WHERE order_id IN ${mine}`));
      st.push(env.DB.prepare(`UPDATE documents SET order_id=NULL, source='manual' WHERE order_id IN ${mine}`));
      st.push(env.DB.prepare(`UPDATE outbox SET order_id=NULL WHERE order_id IN ${mine}`));
      st.push(env.DB.prepare(`UPDATE doc_events SET order_id=NULL WHERE order_id IN ${mine}`));
      st.push(env.DB.prepare(`UPDATE todos SET order_id=NULL WHERE order_id IN ${mine}`));
      st.push(env.DB.prepare(`DELETE FROM orders WHERE id IN (${L}) AND customer_id=?`).bind(c.id));
    }
    // ③ 정산 요청
    if (si.length) {
      const L = si.join(',');
      const mine = `(SELECT id FROM settlements WHERE id IN (${L}) AND customer_id=${c.id})`;
      st.push(env.DB.prepare(`UPDATE documents SET settlement_id=NULL WHERE settlement_id IN ${mine}`));
      st.push(env.DB.prepare(`UPDATE todos SET settlement_id=NULL WHERE settlement_id IN ${mine}`));
      st.push(env.DB.prepare(`DELETE FROM settlements WHERE id IN (${L}) AND customer_id=?`).bind(c.id));
    }
    await env.DB.batch(st);
    const part = [];
    if (oi.length) part.push(`주문 ${oi.length}건`);
    if (si.length) part.push(`정산 ${si.length}건`);
    if (di.length) part.push(`문서 ${di.length}건`);
    await logEvent(env, { action: 'history_purged', actor: 'admin',
      detail: `${who} 이력 삭제 — ${part.join(' · ')}` });
    return json({ ok: true, removed: { orders: oi.length, settlements: si.length, documents: di.length } });
  }

  /* 거래처 삭제.
     이력이 한 건이라도 있으면 지우지 않는다 — 주문·정산·문서가 사라지면 장부가 어긋나고,
     이미 나간 서류의 발행처만 없어진다. 그럴 땐 «거절»로 돌려 목록에서 내리는 게 맞다. */
  if (b.action === 'delete') {
    if (c.role === 'admin') {
      return json({ error: 'is_admin', message: '관리자 계정은 지울 수 없습니다.' }, 400);
    }
    const n = await env.DB.prepare(
      `SELECT (SELECT COUNT(*) FROM orders      WHERE customer_id=?1) AS o,
              (SELECT COUNT(*) FROM settlements WHERE customer_id=?1) AS s,
              (SELECT COUNT(*) FROM documents   WHERE customer_id=?1) AS d,
              (SELECT COUNT(*) FROM payments    WHERE customer_id=?1) AS p`
    ).bind(c.id).first();
    const left = [];
    if (n.o) left.push(`주문 ${n.o}건`);
    if (n.s) left.push(`정산 ${n.s}건`);
    if (n.d) left.push(`발행 문서 ${n.d}건`);
    if (n.p) left.push(`입금 ${n.p}건`);
    if (left.length) {
      return json({ error: 'has_history',
        message: `${left.join(' · ')}이 남아 있어 지울 수 없습니다.\n`
               + '이력을 먼저 지우거나, 멤버십을 «거절»로 돌려 목록에서 내려주세요.' }, 400);
    }
    // 딸린 부속만 함께 정리한다. 이력이 없는 것은 위에서 확인했다.
    await env.DB.batch([
      env.DB.prepare('DELETE FROM bill_profiles WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM sites         WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM sessions      WHERE customer_id=?').bind(c.id),
      env.DB.prepare('UPDATE todos     SET customer_id=NULL WHERE customer_id=?').bind(c.id),
      env.DB.prepare('UPDATE inquiries SET customer_id=NULL WHERE customer_id=?').bind(c.id),
      env.DB.prepare('DELETE FROM customers WHERE id=?').bind(c.id),
    ]);
    await logEvent(env, { action: 'client_deleted', actor: 'admin',
      detail: `거래처 삭제 ${who}${c.kakao_id ? ' (카카오 계정 연결됨 — 다시 로그인하면 새로 만들어집니다)' : ''}` });
    return json({ ok: true, deleted: who });
  }

  if (b.action === 'memo') {
    await env.DB.prepare('UPDATE customers SET memo=?, updated_at=? WHERE id=?')
      .bind(String(b.memo || ''), now, c.id).run();
    return json({ ok: true });
  }

  // 연락처 오타 수정 — 권한(role)·카카오 식별자는 건드리지 않는다
  if (b.action === 'profile') {
    const email = String(b.work_email || '').trim();
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'bad_email', message: '업무 이메일 형식이 올바르지 않습니다.' }, 400);
    }
    await env.DB.prepare(
      `UPDATE customers SET name=?, company=?, alias=?, biz_no=?, ceo=?, phone=?, work_email=?, address=?, updated_at=? WHERE id=?`
    ).bind(String(b.name || ''), String(b.company || ''), String(b.alias || ''),
           String(b.biz_no || ''), String(b.ceo || ''), String(b.phone || ''),
           email, String(b.address || ''), now, c.id).run();
    await logEvent(env, { action: 'client_edit', actor: 'admin', detail: `${who} 거래처 정보 수정` });
    return json({ ok: true });
  }

  /* 담당자 — 한 거래처에 여러 명이 있다. 서류에 찍히는 이름과 메일이 사람마다 다르다.
     customers 한 줄에 우겨넣으면 «지난번엔 누구 앞으로 보냈더라»를 기억으로 때워야 한다. */
  if (b.action === 'contact_save') {
    const name = String(b.name || '').trim();
    const email = String(b.email || '').trim();
    if (!name) return json({ error: 'no_name', message: '담당자 이름을 입력해주세요.' }, 400);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'bad_email', message: '이메일 형식이 올바르지 않습니다.' }, 400);
    }
    const def = b.is_default ? 1 : 0;
    const tax = b.is_tax ? 1 : 0;
    // 랩실은 납품지(sites)를 그대로 쓴다 — 학교는 «랩실 = 받는 곳»이라 두 벌로 두면 어긋난다
    let siteId = Number(b.site_id) || null;
    if (siteId) {
      const own = await env.DB.prepare('SELECT id FROM sites WHERE id=? AND customer_id=?')
        .bind(siteId, c.id).first();
      if (!own) siteId = null;
    }
    let id = Number(b.contact_id) || null;
    if (id) {
      const own = await env.DB.prepare('SELECT id FROM contacts WHERE id=? AND customer_id=?')
        .bind(id, c.id).first();
      if (!own) return json({ error: 'not_found' }, 404);
      await env.DB.prepare(
        `UPDATE contacts SET name=?, email=?, phone=?, role=?, is_default=?, is_tax=?, site_id=?, updated_at=?
          WHERE id=?`)
        .bind(name, email, String(b.phone || ''), String(b.role || ''), def, tax, siteId, now, id).run();
    } else {
      const r = await env.DB.prepare(
        `INSERT INTO contacts (customer_id, name, email, phone, role, is_default, is_tax, site_id, created_at, updated_at)
         VALUES (?,?,?,?,?,?,?,?,?,?)`)
        .bind(c.id, name, email, String(b.phone || ''), String(b.role || ''), def, tax, siteId, now, now).run();
      id = r.meta.last_row_id;
    }
    // 기본도 계산서 메일도 한 명뿐이다
    if (def) {
      await env.DB.prepare('UPDATE contacts SET is_default=0 WHERE customer_id=? AND id<>?').bind(c.id, id).run();
    }
    if (tax) {
      await env.DB.prepare('UPDATE contacts SET is_tax=0 WHERE customer_id=? AND id<>?').bind(c.id, id).run();
      // 표시만 바꾸면 아무 일도 안 일어난다 — 실제로 계산서가 나가는 곳까지 옮겨준다
      if (email) {
        await env.DB.prepare(
          `UPDATE bill_profiles SET tax_email=?, updated_at=?
            WHERE customer_id=? AND id=(SELECT id FROM bill_profiles WHERE customer_id=?
                                         ORDER BY is_default DESC, id LIMIT 1)`)
          .bind(email, now, c.id, c.id).run();
      }
    }
    await logEvent(env, { action: 'contact_save', actor: 'admin',
      detail: `${who} 담당자 ${name} 저장`
        + (def ? ' · 기본' : '') + (tax ? ' · 계산서 메일' : '') });
    const rows = (await env.DB.prepare(
      `SELECT ct.*, s.org_name AS site_name, s.address AS site_addr
         FROM contacts ct LEFT JOIN sites s ON s.id = ct.site_id
        WHERE ct.customer_id=? ORDER BY ct.is_default DESC, ct.id`).bind(c.id).all()).results || [];
    return json({ ok: true, id, contacts: rows });
  }

  /* 랩실(납품지) 추가 — 담당자를 넣다가 그 방이 목록에 없어 멈추는 일을 없앤다.
     학교는 «랩실 = 받는 곳»이라, 여기서 만든 것이 곧 배송지가 된다. */
  if (b.action === 'site_save') {
    const org = String(b.org_name || '').trim();
    const addr = String(b.address || '').trim();
    if (!org) return json({ error: 'no_org', message: '소속 · 랩실명을 입력해주세요.' }, 400);
    if (!addr) return json({ error: 'no_addr', message: '주소를 입력해주세요.' }, 400);
    const first = await env.DB.prepare('SELECT id FROM sites WHERE customer_id=? LIMIT 1').bind(c.id).first();
    const r = await env.DB.prepare(
      'INSERT INTO sites (customer_id, org_name, address, is_default, created_at) VALUES (?,?,?,?,?)')
      .bind(c.id, org, addr, first ? 0 : 1, now).run();      // 첫 곳은 기본 납품지로
    await logEvent(env, { action: 'site_add', actor: 'admin', detail: `${who} 랩실 ${org} 추가` });
    const sites = (await env.DB.prepare(
      'SELECT id, org_name, address, is_default FROM sites WHERE customer_id=? ORDER BY is_default DESC, id')
      .bind(c.id).all()).results || [];
    return json({ ok: true, id: r.meta.last_row_id, sites });
  }

  if (b.action === 'contact_delete') {
    await env.DB.prepare('DELETE FROM contacts WHERE id=? AND customer_id=?')
      .bind(Number(b.contact_id) || 0, c.id).run();
    const rows = (await env.DB.prepare(
      `SELECT ct.*, s.org_name AS site_name, s.address AS site_addr
         FROM contacts ct LEFT JOIN sites s ON s.id = ct.site_id
        WHERE ct.customer_id=? ORDER BY ct.is_default DESC, ct.id`).bind(c.id).all()).results || [];
    return json({ ok: true, contacts: rows });
  }

  return json({ error: 'unknown_action' }, 400);
}

/* 거래처 추가.
   양식은 하나다 — 기존 사업자든 새 사업자든 같은 칸을 채운다.
   사업자번호가 이미 쓰이고 있으면, 상호·대표자·주소는 그 사업자에 맞춰 정리한다
   (화면에서 골라 채웠어도 손으로 고쳐 어긋나는 일이 생긴다). */
async function create(env, b) {
  const now = kstISO();
  const email = String(b.work_email || '').trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ error: 'bad_email', message: '업무 이메일 형식이 올바르지 않습니다.' }, 400);
  }

  let company = String(b.company || '').trim();
  let biz_no  = String(b.biz_no || '').trim();
  let ceo     = String(b.ceo || '').trim();
  let address = String(b.address || '').trim();
  if (!company) return json({ error: 'no_company', message: '거래처명을 입력해주세요.' }, 400);

  if (biz_no) {
    const twin = await env.DB.prepare(
      `SELECT company, ceo, address FROM customers
        WHERE biz_no=? AND company IS NOT NULL AND company <> '' ORDER BY id LIMIT 1`)
      .bind(biz_no).first();
    if (twin) {                       // 같은 사업자번호는 같은 상호를 쓴다
      company = twin.company;
      ceo     = ceo || twin.ceo || '';
      address = address || twin.address || '';
    }
  }

  const alias = String(b.alias || '').trim() || company;

  // 같은 사업자번호에 같은 별칭이 이미 있으면 막는다 — 목록에서 구분이 안 된다
  if (biz_no) {
    const dup = await env.DB.prepare(
      'SELECT id FROM customers WHERE biz_no=? AND alias=? LIMIT 1').bind(biz_no, alias).first();
    if (dup) {
      return json({ error: 'duplicate',
        message: `'${company}' 에 '${alias}' 별칭이 이미 있습니다. 다른 별칭을 써주세요.` }, 409);
    }
  }

  const r = await env.DB.prepare(
    `INSERT INTO customers (company, alias, biz_no, ceo, name, work_email, phone, address, memo,
                            access, role, billing_mode, created_at, updated_at)
     VALUES (?,?,?,?,?,?,?,?,?, '거래처','member',?,?,?)`
  ).bind(company, alias, biz_no || null, ceo || null,
         String(b.name || '').trim() || null, email || null,
         String(b.phone || '').trim() || null, address || null,
         String(b.memo || '').trim() || null,
         b.billing_mode === '후불' ? '후불' : '선불', now, now).run();

  const id = r.meta.last_row_id;

  // 사업자번호가 있으면 계산서 발행정보도 같이 만들어 둔다 — 견적서를 바로 뽑을 수 있게
  if (biz_no) {
    await env.DB.prepare(
      `INSERT INTO bill_profiles (customer_id, label, company, biz_no, ceo, tax_email, address, is_default, created_at, updated_at)
       VALUES (?, '기본', ?,?,?,?,?, 1, ?, ?)`
    ).bind(id, company, biz_no, ceo || null, String(b.tax_email || '').trim() || email || null,
           address || null, now, now).run();
  }

  await logEvent(env, { action: 'client_add', actor: 'admin',
    detail: `거래처 추가 ${company}${alias !== company ? ` (${alias})` : ''}` });

  // 만든 거래처를 그대로 돌려준다 — 문서 발행 화면에서 곧바로 골라 쓸 수 있게
  return json({ ok: true, id, client: {
    id, company, alias, biz_no, ceo, address,
    name: String(b.name || '').trim(),
    work_email: email, email: '', phone: String(b.phone || '').trim(),
    access: '거래처', billing_mode: b.billing_mode === '후불' ? '후불' : '선불',
    lab_id: null, lab_name: '', lab_code: '',
  } });
}
