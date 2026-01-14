# Backend (Draft)

이 폴더는 백엔드 API 서버의 자리입니다.

## 권장 스택(예시)
- Python: FastAPI + Uvicorn
- DB: PostgreSQL
- Storage: NAS 또는 MinIO(S3 compatible)
- Reverse Proxy: Nginx

## TODO
- 인증/인가(RBAC) 구현
- 파일 업로드(멀티파트 + Chunked) 프로토콜 확정
- 무결성(SHA-256) 검증 및 중복 감지
- 잠금(Checkout/Check-in) 흐름 설계
- 감사 로그(Audit) 저장
