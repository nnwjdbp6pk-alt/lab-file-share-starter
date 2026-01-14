# API Specification (Draft)

본 문서는 사람이 읽기 쉬운 초안이며, 기계 가독(OpenAPI)은 `docs/openapi.yaml`에 제공합니다.

## Auth
- POST /api/auth/login
  - Request: { username, password }
  - Response: { access_token, token_type, expires_in, user: { id, name, role } }

## Files
- GET /api/files
  - Query: q, doc_type, project_code, uploader, date_from, date_to, page, page_size, sort
  - Response: { items: [...], page, page_size, total }

- POST /api/files/upload
  - Multipart upload for small files
  - Chunked upload for large files
  - Recommended headers: X-Checksum-SHA256, X-Project-Code, X-Experiment-Id, X-Step-Name

- GET /api/files/{id}
  - Response: metadata + context + version info + lock status

- GET /api/files/{id}/download
  - Streaming response

- POST /api/files/batch-download
  - Request: { file_ids: [...] }
  - Response: zip streaming (or async job id)

## Locking / Versioning
- POST /api/files/{id}/lock
- POST /api/files/{id}/unlock
  - Unlock may include new version upload (check-in flow)

## Admin
- GET /api/admin/audit-logs
  - Query: actor, action, file_id, date_from, date_to, page, page_size
