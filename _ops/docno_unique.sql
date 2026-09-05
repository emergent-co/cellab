-- 문서번호 중복 방지 (2026-09-05)
-- 채번은 «오늘 쓴 가장 큰 번호 + 1» 로 고쳤지만, documents.doc_no 에 제약이 없어
-- 어떤 경로로든 중복이 들어오면 조용히 저장된다. 바로빌 관리번호도 이 값을 쓴다.
--
-- 먼저 중복이 있는지 본다 (결과가 없어야 아래 인덱스가 걸린다):
--   npx wrangler d1 execute rndsetup-products --remote --command "SELECT doc_no, COUNT(*) c FROM documents GROUP BY doc_no HAVING c>1"
CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_doc_no ON documents(doc_no);
