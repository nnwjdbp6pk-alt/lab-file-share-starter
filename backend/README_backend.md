# Backend (Development)

FastAPI 기반으로 Phase 1 API 스켈레톤을 제공합니다.

## 구성
- FastAPI + Uvicorn
- PostgreSQL (기본)
- 로컬 파일 스토리지

## 사전 준비
1. PostgreSQL 실행 후 스키마 생성
   ```bash
   psql "$DATABASE_URL" -f docs/db_schema_v1.sql
   ```
2. 환경 변수 설정
   ```bash
   cp backend/.env.example backend/.env
   ```
   - `DEFAULT_USERS`에는 로그인 가능한 로컬 유저 목록(JSON 배열)을 지정합니다.
   - 기본 예시의 `admin/admin` 계정을 변경하세요.

## 실행
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 참고
- 업로드 확장자 허용 목록은 `ALLOWED_EXTENSIONS`로 관리합니다.
- 업로드 최대 용량은 `MAX_UPLOAD_SIZE_BYTES`로 제한합니다.
- 업로드 시 전달되는 `project_code`, `experiment_id`, `step_name`, `tags` 폼 필드가 있을 경우 `file_contexts` 테이블에 저장합니다.
