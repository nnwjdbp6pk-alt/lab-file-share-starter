# ROADMAP

## Phase 1 — MVP (우선 구현)
- Auth (최소): 로그인 및 토큰 발급, RBAC 적용
- Files
  - 목록 조회 (검색/필터/페이징)
  - 업로드 (multipart 우선, chunk는 Phase 2로 미룰 수 있음)
  - 상세 조회
  - 다운로드 (stream)
  - 일괄 다운로드(zip streaming) — 필요 시 Phase 1.5로 분리
- Metadata
  - checksum(SHA-256) 저장/검증
  - project_code, experiment_id, step_name, tags 저장
- Audit
  - 업로드/다운로드/삭제(비활성 포함) 행위 로그 기록

## Phase 2 — 안정화/운영 기능
- Chunked upload (resume)
- Locking (checkout/check-in)
- Versioning (parent/lineage, is_latest 관리)
- Admin: audit_logs UI/검색

## Phase 3 — 편의 기능
- Preview (PDF/Image)
- Office→PDF 변환 기반 preview(보안/리소스 검토 후)
- 고도화된 검색(Full-text / indexing)
