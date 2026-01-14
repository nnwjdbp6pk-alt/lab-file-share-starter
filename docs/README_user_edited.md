Lab File Share (R&D) — README

1. 개요

본 프로젝트는 사내 연구실(R&D) 환경에서 생산되는 다양한 문서 및 데이터 파일을 안전하게 공유하고 체계적으로 관리하기 위한 웹 기반 파일 공유 시스템입니다.
단순한 파일 저장을 넘어, 연구 데이터의 무결성(Integrity) 검증, 실험 문맥(Context) 연결, 버전 이력 관리를 통해 연구 자산의 신뢰성을 확보하는 것을 목표로 합니다.

구현 형태: Backend + Frontend 분리형 (RESTful API)

대상 파일: xlsx, docx, pptx, pdf, 이미지, Raw Data 등

운영 환경: 사내망(Intranet) / 폐쇄망

2. 핵심 기능 범위 (MVP + Essential)

2.1 파일 관리

업로드: 단일/복수 파일 업로드, Drag & Drop 지원, 대용량 파일 분할 업로드(Chunked Upload)

다운로드: 단일 다운로드, 선택 파일 일괄 다운로드(.zip 아카이빙)

파일 목록: 페이징, 정렬(최신순, 크기순, 이름순)

상세 정보: 파일명, 업로더, 버전, 해시값, 실험 정보 등 조회

파일 생명주기: 삭제 권한 제어, 보존 기한 만료 시 자동 비활성화/아카이빙

2.2 검색 및 필터

키워드 검색: 파일명, 태그, 실험 ID 검색

상세 필터:

업로더 / 부서 / 프로젝트

파일 유형 (확장자)

기간 (업로드 일자, 실험 일자)

2.3 데이터 무결성 및 동시성 제어 (R&D 특화)

무결성 검증: 업로드 시 SHA-256 해시 생성 및 중복/변조 방지

동시성 제어 (File Locking): 파일 수정(Checkout) 시 타 사용자 수정 제한 (Check-in/Unlock 방식)

2.4 권한/접근 제어

인증: 사내 LDAP/SSO 연동 또는 자체 JWT 세션 기반

Role 기반 접근 제어 (RBAC):

Admin: 시스템 설정, 사용자 관리, 감사 로그 조회

Manager: 프로젝트/폴더 생성, 삭제, 잠금 강제 해제

Researcher (Editor): 업로드, 수정, 본인 파일 삭제

Viewer: 조회, 다운로드만 가능

3. 확장 로드맵 (Recommended)

3.1 고도화된 버전 관리

Lineage Tracking: 파일의 파생 관계 추적 (Parent ID 기반 트리 구조 시각화)

변경 이력: 버전별 변경 사유(Change Log), 변경자 기록

3.2 R&D 메타데이터 심화

실험 연동: ELN(전자연구노트) 또는 LIMS 연동을 위한 Experiment ID, Test Case ID 매핑

상태 태깅: "초안(Draft)", "검토중(Review)", "승인(Approved)", "폐기(Deprecated)"

3.3 미리보기 (Preview)

PDF/Image: 브라우저 네이티브 미리보기

Office 문서: LibreOffice Server 또는 전용 변환 라이브러리를 통한 미리보기 지원

3.4 감사 추적 (Audit Trail)

누가, 언제, 어떤 파일을, 조회/다운로드/수정했는지에 대한 불변 로그 기록 (보안 감사 대응)

4. 시스템 아키텍처

4.1 구성 요소

Frontend: React/Vue.js (SPA), Axios (Chunked Upload 구현), File Saver

Backend API: Spring Boot / Node.js / Django / FastAPI (Multipart 처리, 비동기 작업 큐)

Database: PostgreSQL / MySQL (메타데이터, 관계형 데이터)

Storage: NAS Mount / AWS S3 / MinIO (사내 구축형 Object Storage 권장)

4.2 데이터 처리 흐름

업로드: Client가 파일 해시 계산 → Server 중복 체크 → (없으면) Chunked Upload 수행 → Storage 저장 → DB 메타데이터 및 해시 기록

수정: 수정 버튼 클릭(Locking) → 로컬 수정 후 업로드(Check-in) → 버전 Up (+ is_latest 갱신)

다운로드: 권한 체크 → Audit Log 기록 → Storage Stream 전송

5. API 명세 (초안)

Method

Endpoint

설명

AUTH

/api/auth/login

로그인 및 토큰 발급

FILE

/api/files

파일 목록 조회 (검색/필터)

FILE

/api/files/upload

파일 업로드 (Multipart/Chunk)

FILE

/api/files/{id}

파일 상세 정보 조회

FILE

/api/files/{id}/download

파일 스트리밍 다운로드

FILE

/api/files/batch-download

선택 파일 zip 다운로드

FILE

/api/files/{id}/lock

파일 수정 잠금 (Checkout)

FILE

/api/files/{id}/unlock

파일 잠금 해제 (Check-in)

ADMIN

/api/admin/audit-logs

감사 로그 조회

6. 데이터 모델 (Schema Proposal)

6.1 File Meta Table (files)

데이터 무결성과 버전을 관리하기 위한 핵심 테이블입니다.

id (PK, UUID/BigInt)

original_name (Varchar): 사용자 업로드 파일명

stored_path (Varchar): 스토리지 저장 경로/Object Key

file_size (BigInt): 바이트 단위 크기

mime_type (Varchar)

checksum_sha256 (Char[64]): 무결성 검증용 해시

version (Int): 파일 버전 (1, 2, 3...)

parent_file_id (FK): 이전 버전 파일 ID (계보 추적용)

is_latest (Boolean): 최신 버전 여부 (쿼리 최적화)

lock_status (Enum): UNLOCKED, LOCKED (동시성 제어)

locked_by (FK): 현재 수정 중인 사용자

uploader_id (FK): 업로더

created_at (Timestamp): 생성 일시

expiry_date (Date): 보존 기한 (자동 삭제/아카이빙 기준)

is_active (Boolean): 논리적 삭제 여부

6.2 Context Meta Table (file_contexts)

R&D 실험 정보와 파일을 매핑하는 테이블입니다.

file_id (FK)

project_code (Varchar): 프로젝트 코드

experiment_id (Varchar): 실험 ID (Test Run ID)

step_name (Varchar): 공정 단계 (예: 전처리, 분석, 결과도출)

tags (JSON/Array): 유동적인 태그 정보

7. 보안 및 운영 고려사항

7.1 보안 (Security)

업로드 제한: 실행 파일(.exe, .sh 등) 차단, 화이트리스트 기반 확장자 검사

접근 제어: 사내 IP 대역만 접근 허용 (Network Policy), API Rate Limiting

7.2 대용량 처리 (Performance)

Chunked Upload: 100MB 이상 파일은 프론트엔드에서 쪼개서 전송, 백엔드에서 병합

Nginx/Proxy 설정: client_max_body_size 및 Timeout 설정 최적화

7.3 데이터 보호 (Data Protection)

백업 정책: DB 일일 백업, 스토리지 스냅샷 (Ransomware 대응)

감사(Audit): 모든 다운로드 이력은 최소 1년간 보관

8. 프로젝트 폴더 구조 (권장)

lab-file-share/
├── backend/
│   ├── src/
│   │   ├── api/ (Controllers)
│   │   ├── core/ (Auth, Utils, Config)
│   │   ├── services/ (Business Logic, FileIO)
│   │   ├── models/ (DB Schemas)
│   │   └── tasks/ (Async Jobs: Virus Scan, Compression)
│   ├── tests/
│   └── requirements.txt (or package.json)
├── frontend/
│   ├── src/
│   │   ├── components/ (FileUploader, FileList, Previewer)
│   │   ├── hooks/ (useFileUpload, useAuth)
│   │   └── services/ (API Calls)
│   └── public/
├── docs/
│   ├── architecture.md
│   ├── db_schema_v1.sql
│   └── api_specification.md
├── infra/ (Docker, Nginx config)
└── README.md
