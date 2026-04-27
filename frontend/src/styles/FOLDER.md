# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `frontend/src/styles`  
> **최종 수정일**: 2026-04-27  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다.

---

## 1. 용도

전역 CSS 토큰 및 컴포넌트 공통 유틸리티 클래스.

## 2. 현재 파일

- `index.css` — 라이트 테마 CSS 변수, Reset, 공통 컴포넌트 클래스 (`.card`, `.btn-primary`, `.badge`, `.input`, `.select` 등). `main.tsx`에서 import.

## 3. 담지 않는 것

컴포넌트 스코프 스타일은 해당 컴포넌트 파일 내 `<style>` 블록으로 관리.

## 4. 연계

`main.tsx`에서 `index.css` import 상태 유지 필요.

---

## 5. 비고

- 2026-04-27 라이트 테마로 전면 재작성 (다크 글래스모피즘 → 라이트 카드 기반).
- 2026-04-27 `global.css` 삭제 (import 없음 확인, 역할이 `index.css`와 중복).
