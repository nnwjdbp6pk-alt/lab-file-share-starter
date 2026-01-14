# Lab File Share (R&D)

사내 연구실(R&D) 환경에서 생산되는 다양한 문서/데이터 파일을 **안전하게 공유**하고 **체계적으로 관리**하기 위한 웹 기반 파일 공유 시스템입니다.  
단순 저장을 넘어 연구 데이터의 **무결성(Integrity) 검증**, **실험 문맥(Context) 연결**, **버전 이력 관리**를 통해 연구 자산의 신뢰성을 확보하는 것을 목표로 합니다.

- 구현 형태: **Backend + Frontend 분리형 (RESTful API)**
- 대상 파일: **xlsx, docx, pptx, pdf, 이미지, Raw Data 등**
- 운영 환경: **사내망(Intranet) / 폐쇄망**
- 문서 기준일: **2026-01-14**

---

## 1) 핵심 기능 범위 (MVP + Essential)

### 1.1 파일 관리
- 업로드: 단일/복수 업로드, Drag & Drop, 대용량 분할 업로드(Chunked Upload)
- 다운로드: 단일 다운로드, 선택 파일 일괄 다운로드(.zip 아카이빙)
- 파일 목록: 페이징, 정렬(최신/크기/이름)
- 상세 정보: 파일명, 업로더, 버전, 해시값, 실험 정보 등
- 파일 생명주기: 삭제 권한 제어, 보존 기한 만료 시 비활성화/아카이빙(권장)

### 1.2 검색 및 필터
- 키워드 검색: 파일명, 태그, 실험 ID
- 상세 필터: 업로더/부서/프로젝트, 파일 유형(확장자), 기간(업로드 일자/실험 일자)

### 1.3 데이터 무결성 및 동시성 제어 (R&D 특화)
- 무결성 검증: 업로드 시 **SHA-256** 생성/저장(중복/변조 감지)
- 동시성 제어: 파일 수정(Checkout) 시 잠금(File Locking) → 수정 후 Check-in/Unlock

### 1.4 권한/접근 제어
- 인증: 사내 LDAP/SSO 연동(권장) 또는 자체 JWT 세션 기반
- RBAC(Role Based Access Control)
  - Admin: 시스템 설정, 사용자 관리, 감사 로그 조회
  - Manager: 프로젝트/폴더 관리, 잠금 강제 해제
  - Researcher(Editor): 업로드/수정/본인 파일 삭제(또는 비활성 요청)
  - Viewer: 조회/다운로드

---

## 2) 확장 로드맵 (Recommended)

### 2.1 고도화된 버전 관리
- Lineage Tracking: Parent ID 기반 파생 관계(트리) 추적/시각화
- 변경 이력: 버전별 변경 사유(Change Log), 변경자 기록

### 2.2 R&D 메타데이터 심화
- ELN/LIMS 연동: Experiment ID, Test Case ID 매핑
- 상태 태깅: Draft / Review / Approved / Deprecated

### 2.3 미리보기(Preview)
- PDF/Image: 브라우저 네이티브 미리보기
- Office 문서: 변환(예: LibreOffice headless) 기반 미리보기(보안/리소스 고려)

### 2.4 감사 추적(Audit Trail)
- 조회/다운로드/수정 등 모든 행위를 불변 로그로 기록(보안 감사 대응)

---

## 3) 아키텍처 (권장 구성)

- Frontend: React/Vue (SPA), Axios, Chunked upload client
- Backend API: FastAPI/Django/Spring/Node 등(멀티파트/비동기 큐 처리)
- Database: PostgreSQL/MySQL
- Storage: NAS Mount 또는 사내 Object Storage(예: MinIO) 권장
- Reverse Proxy: Nginx(업로드 제한/타임아웃/인증 게이트)

자세한 설계는 `docs/architecture.md` 참고.

---

## 4) API (초안)

| 영역 | Method | Endpoint | 설명 |
|---|---:|---|---|
| AUTH | POST | /api/auth/login | 로그인 및 토큰 발급 |
| FILE | GET | /api/files | 파일 목록(검색/필터) |
| FILE | POST | /api/files/upload | 파일 업로드(Multipart/Chunk) |
| FILE | GET | /api/files/{id} | 파일 상세 |
| FILE | GET | /api/files/{id}/download | 다운로드(스트리밍) |
| FILE | POST | /api/files/batch-download | 선택 파일 zip 다운로드 |
| FILE | POST | /api/files/{id}/lock | 파일 잠금(Checkout) |
| FILE | POST | /api/files/{id}/unlock | 잠금 해제(Check-in) |
| ADMIN | GET | /api/admin/audit-logs | 감사 로그 조회 |

자세한 명세는 `docs/api_specification.md` 및 `docs/openapi.yaml` 참고.

---

## 5) 데이터 모델 (Schema Proposal)

### 5.1 files (File Meta)
- id (PK, UUID/BigInt)
- original_name, stored_path, file_size, mime_type
- checksum_sha256 (Char[64])
- version (Int), parent_file_id (FK), is_latest (Boolean)
- lock_status (Enum), locked_by (FK)
- uploader_id (FK), created_at (Timestamp)
- expiry_date (Date), is_active (Boolean)

### 5.2 file_contexts (Context Meta)
- file_id (FK)
- project_code, experiment_id, step_name
- tags (JSON/Array)

초안 SQL은 `docs/db_schema_v1.sql` 참고.

---

## 6) 보안 및 운영 고려사항 (필수)

- 업로드 제한: 실행 파일(.exe/.sh 등) 차단 + 확장자 화이트리스트
- 접근 제어: 사내 IP 대역 제한(네트워크 정책), API rate limit
- 대용량 처리: Chunk size 정책, Nginx `client_max_body_size`/timeout 최적화
- 백업: DB 일일 백업 + 스토리지 스냅샷(랜섬웨어 대응)
- 감사 로그: 다운로드 이력 최소 1년 보관(정책에 따라 조정)

---

## 7) 저장소 구조 (권장)

```
lab-file-share/
├── backend/
├── frontend/
├── docs/
├── infra/
├── docker-compose.yml
└── README.md
```

본 ZIP은 위 구조의 **초안 스캐폴드**를 제공합니다.
