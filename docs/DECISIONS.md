# DECISIONS (ADR Log)

본 문서는 설계/정책 결정을 ADR(Architecture Decision Record) 형태로 누적 기록합니다.

## ADR-001: Integrity checksum uses SHA-256
- Status: Accepted
- Reason:
  - 표준적이며 충돌 저항성이 충분
  - 파일 변조/중복 감지에 활용 가능
- Consequences:
  - 업로드 시 해시 계산 비용이 발생(대용량은 스트리밍 계산 필요)

## ADR-002: Prefer logical delete (is_active=false) over physical delete
- Status: Accepted
- Reason:
  - 감사 추적 및 실수 복구 용이
  - R&D 자산 보존 정책에 부합
- Consequences:
  - 스토리지 사용량 증가(보존/만료 정책 필요)

## ADR-003: Source of truth is OpenAPI then DB schema
- Status: Accepted
- Reason:
  - 협업 시 “계약”의 역할을 하는 문서가 필요
  - 구현체의 임의 확장을 억제
