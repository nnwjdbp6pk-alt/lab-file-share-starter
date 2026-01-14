# Glossary

- **File (Meta)**: DB에 저장되는 파일 메타데이터 레코드
- **Blob**: 실제 파일 바이너리(스토리지에 저장)
- **Checksum (SHA-256)**: 업로드 파일 무결성 검증을 위한 해시
- **Version**: 동일 문서 계열의 버전 번호(1,2,3...)
- **Parent File**: 파생 버전의 직전 파일 id
- **is_latest**: 해당 계열에서 최신 버전 여부
- **Locking (Checkout/Check-in)**: 동시 편집 충돌 방지를 위한 잠금/반납 흐름
- **Logical delete**: 실제 삭제가 아니라 is_active=false로 비활성 처리
- **Audit log**: 사용자 행위(업로드/다운로드/삭제/권한변경 등) 기록
