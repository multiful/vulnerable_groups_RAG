# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `frontend/src/types`  
> **최종 수정일**: 2026-04-27  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서  
> **문서 우선순위**: reference  
> **연관 문서**: DIRECTORY_SPEC.md, DATA_SCHEMA.md

---

## 1. 용도

프론트엔드 TypeScript 타입 정의 파일. API 응답 형상과 도메인 엔티티 인터페이스를 담는다.

## 2. 현재 파일

- `cert.ts` — `CertCandidate` 인터페이스 (cert_candidates.json 행 타입)

## 3. 담지 않는 것

- 컴포넌트 props 타입 (각 컴포넌트 파일 내 정의)
- API 호출 로직 (`src/api/` 담당)

## 4. 연계

- `src/pages/Recommendation/index.tsx`에서 `CertCandidate` import
- 백엔드 `DATA_SCHEMA.md`의 candidate row 구조를 따른다
