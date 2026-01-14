# Architecture (Draft)

## 1. Goals
- Secure internal file sharing for R&D documents and raw data
- Integrity verification (SHA-256)
- Version history and file lineage
- Context linkage (Project / Experiment / Step / Tags)
- Audit trail for compliance

## 2. Components
### Frontend (SPA)
- Auth: login, token storage, RBAC-based UI gating
- File list/search/filter + pagination
- Upload:
  - Multipart upload for small files
  - Chunked upload for large files (configurable chunk size)
- Download:
  - Single file streaming download
  - Batch download (server-side zip streaming)

### Backend (REST API)
- AuthN/AuthZ: LDAP/SSO integration or JWT
- Metadata services: CRUD + filtering + full-text search (optional)
- Storage services:
  - NAS path-based storage OR object storage (MinIO/S3)
  - Streaming download endpoints
- Background tasks (optional):
  - Virus scan / file type validation
  - Office→PDF conversion for preview
  - Zip build for batch download
- Audit logging: immutable append-only policy

### Data Stores
- RDBMS (PostgreSQL recommended): files, file_contexts, users, roles, audit_logs
- Storage (NAS/Object): blob storage for file binaries

## 3. Deployment (Intranet)
- Reverse proxy (Nginx) in front of backend + static frontend
- Private network only
- Optional TLS termination on proxy (internal CA)

## 4. Non-functional requirements
- Upload reliability over unstable intranet connections (resume-friendly chunk upload)
- Content security (block executable types, scan, size limits)
- Observability: request logs + structured audit logs
