-- 2026-09-06: 멤버십 = 메일 요청 → 관리자 코드 발급 → 코드 입력으로 전환
--   카카오 «바로 시작»은 일반회원(access='일반')까지만 만든다.
--   멤버십(후불 장부)에는 사람이 한 번 확인한 뒤에만 올라간다.

-- 멤버십 요청 접수함 (비로그인도 남길 수 있다)
CREATE TABLE IF NOT EXISTS membership_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name     TEXT,
  org_name TEXT,
  email    TEXT,
  phone    TEXT,
  note     TEXT,
  status   TEXT DEFAULT '접수',   -- 접수 | 코드발급 | 가입완료 | 거절
  code     TEXT,                  -- 발급해 준 가입코드 (member_codes.code)
  code_issued_at TEXT,
  customer_id INTEGER,            -- 코드를 실제로 쓴 계정
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_mreq_status ON membership_requests(status, id);

-- 가입코드 — 요청 없이 관리자가 직접 만들어 줄 수도 있다
CREATE TABLE IF NOT EXISTS member_codes (
  code       TEXT PRIMARY KEY,
  request_id INTEGER,
  note       TEXT,        -- 누구에게 준 코드인지
  expires_at TEXT,        -- 비어 있으면 무기한
  used_by    INTEGER,     -- customers.id
  used_at    TEXT,
  created_at TEXT,
  created_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_mcode_req ON member_codes(request_id);

-- 기존 '대기' 계정은 일반회원으로 내린다.
--   '대기'는 «멤버십 심사 대기»라는 뜻이었는데, 이제 심사는 코드로 대체됐다.
--   승인·거래처·거절은 건드리지 않는다.
UPDATE customers SET access='일반' WHERE access='대기' OR access IS NULL OR access='';
