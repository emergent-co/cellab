-- 주문관리 시스템 스키마 (D1: rndsetup-products)
-- 기존 products 테이블은 건드리지 않음. 전부 신규 테이블.

CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kakao_id   TEXT UNIQUE,
  name       TEXT,
  email      TEXT,
  phone      TEXT,
  company    TEXT,
  biz_no     TEXT,
  ceo        TEXT,
  biz_type   TEXT,
  biz_item   TEXT,
  tax_email  TEXT,
  address    TEXT,
  memo       TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_no    TEXT UNIQUE,
  customer_id INTEGER,
  status      TEXT DEFAULT '요청접수',
  title       TEXT,
  want_date   TEXT,
  ship_address TEXT,
  request_note TEXT,
  admin_memo   TEXT,
  supply_amount INTEGER DEFAULT 0,
  vat_amount    INTEGER DEFAULT 0,
  total_amount  INTEGER DEFAULT 0,
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_orders_cust   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id   INTEGER NOT NULL,
  seq        INTEGER DEFAULT 0,
  product_id INTEGER,
  name       TEXT,
  spec       TEXT,
  unit       TEXT DEFAULT 'EA',
  qty        REAL DEFAULT 1,
  unit_price INTEGER DEFAULT 0,
  amount     INTEGER DEFAULT 0,
  cost_price INTEGER DEFAULT 0,
  note       TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  type     TEXT,
  doc_no   TEXT,
  version  INTEGER DEFAULT 1,
  status   TEXT DEFAULT '작성됨',
  issue_date TEXT,
  payload_json TEXT,
  pdf_key  TEXT,
  barobill_mgtkey TEXT,
  barobill_ncid   TEXT,
  barobill_state  TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_docs_order ON documents(order_id);

CREATE TABLE IF NOT EXISTS doc_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id    INTEGER,
  document_id INTEGER,
  action  TEXT,
  channel TEXT,
  actor   TEXT,
  to_addr TEXT,
  result  TEXT,
  detail  TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_ev_order ON doc_events(order_id);

CREATE TABLE IF NOT EXISTS outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER,
  order_id    INTEGER,
  to_addr TEXT,
  cc_addr TEXT,
  subject TEXT,
  body    TEXT,
  send_at TEXT,
  status  TEXT DEFAULT '대기',
  tries   INTEGER DEFAULT 0,
  last_error TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_outbox_due ON outbox(status, send_at);

CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  customer_id INTEGER,
  expires_at  TEXT,
  created_at  TEXT
);

-- 2026-08-25 추가: 세금계산서 발행 정보(고객이 정산 시점에 등록·재사용)
CREATE TABLE IF NOT EXISTS bill_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  label      TEXT,
  company    TEXT,
  biz_no     TEXT,
  ceo        TEXT,
  biz_type   TEXT,
  biz_item   TEXT,
  tax_email  TEXT,
  address    TEXT,
  is_default INTEGER DEFAULT 0,
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_bill_cust ON bill_profiles(customer_id);
ALTER TABLE orders ADD COLUMN bill_profile_id INTEGER;  -- 이 주문의 계산서 발행 정보
ALTER TABLE orders ADD COLUMN org_name TEXT;            -- 소속(기관·연구실) — 견적서 공급받는자
ALTER TABLE documents ADD COLUMN access_token TEXT;
ALTER TABLE documents ADD COLUMN sent_at TEXT;
ALTER TABLE documents ADD COLUMN opened_at TEXT;
ALTER TABLE outbox ADD COLUMN sent_at TEXT;

-- 2026-08-25: 주문 품목에 상품 링크
ALTER TABLE order_items ADD COLUMN link TEXT;

-- 2026-08-25: 후불(VIP) 정산
-- 지출금은 orders.total_amount 합계에서 파생한다(별도 저장 안 함). 입금·조정만 기록.
ALTER TABLE customers ADD COLUMN billing_mode TEXT DEFAULT '선불';   -- 선불 | 후불
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  kind    TEXT DEFAULT '입금',   -- 입금 | 조정(음수 가능)
  amount  INTEGER NOT NULL,
  method  TEXT,                  -- 통장 | 카드 | 기타
  paid_at TEXT,
  memo    TEXT,
  created_at TEXT,
  created_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_pay_cust ON payments(customer_id, paid_at);

-- 2026-08-25: 납품지(소속+주소) 저장 — 주문 시 라디오로 선택
CREATE TABLE IF NOT EXISTS sites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  org_name TEXT,
  address  TEXT,
  is_default INTEGER DEFAULT 0,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_sites_cust ON sites(customer_id);
