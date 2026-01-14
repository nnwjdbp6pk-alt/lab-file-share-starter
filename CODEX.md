# CODEX.md — Working Rules for Codex

본 파일은 이 저장소에서 Codex(코드 생성/수정 에이전트)가 따라야 할 **작업 규칙(Constitution)** 입니다.
목표는 “자동화”가 아니라, **일관된 스펙 준수**와 **안전한 변경**입니다.

## 1. Project Status
- Status: ACTIVE DEVELOPMENT
- Primary environment: Intranet (closed network)
- Target: R&D document sharing system (xlsx/docx/pptx/pdf, images, raw data)
- Baseline date: 2026-01-14

## 2. Source of Truth (Priority Order)
아래 우선순위를 **절대적으로** 따른다:
1. `docs/openapi.yaml` (API contract)
2. `docs/db_schema_v1.sql` (DB schema)
3. `README.md` (product overview / non-binding descriptions)
4. 기타 문서(architecture, api_specification 등)

스펙 충돌 시:
- 먼저 충돌 지점을 명시하고,
- **1번(OPENAPI)과 2번(DB)** 을 기준으로 정합되게 정리한다.
- OPENAPI/DB 파일을 변경해야 할 경우, 변경 이유와 영향 범위를 문서에 남긴다(DECISIONS/ADR).

## 3. Allowed Actions (Codex가 수행해도 되는 작업)
- `backend/`, `frontend/` 아래에 신규 파일 생성 및 코드 스캐폴드 작성
- OpenAPI 기준으로 endpoint/controller/service/DTO 모델 생성
- DB schema 기준으로 ORM 모델/마이그레이션 초안 생성
- 보안/업로드 제한/로그 등 운영 상 필수 가드레일 구현 제안
- 변경 시 “패치(최소 변경)” 원칙 준수

## 4. Forbidden Actions (금지)
- 사용자의 명시적 요청 없이 `docs/openapi.yaml`의 endpoint/필드 의미를 변경
- DB 컬럼 이름/타입의 임의 변경(특히 `files`, `audit_logs`)
- 기존 파일/폴더의 대규모 리네이밍(구조 개편) — 사전 합의 필요
- 보안 정책을 약화시키는 변경(확장자 whitelist 제거 등)

## 5. Engineering Principles
- **Clarity > cleverness**: 명확한 구조와 주석, 예외 처리 우선
- “R&D 운영”을 전제로 한 감사 추적과 무결성 체크를 기본값으로
- 파일 업로드는 실패/재시도/부분 성공을 고려한 설계(Chunk, resume-friendly)

## 6. Working Style
- 작업 단위는 작게: 한 번에 하나의 목표(예: Phase 1의 Upload/List/Download)
- 변경 결과물은 반드시:
  - 어떤 파일이 바뀌었는지
  - 어떤 동작이 추가/변경되었는지
  - 스펙(OpenAPI/DB)과의 정합성
  를 요약한다.

## 7. Scope Guidance
- 구현 우선순위는 `docs/ROADMAP.md`의 Phase 1을 따른다.
