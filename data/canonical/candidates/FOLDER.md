# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/canonical/candidates`  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---

## 1. 용도

**추천 candidate row** 등 구조적 추천 입력을 둔다. RAG chunk와 동일 구조로 취급하지 않는다.  
준비 단계에서는 형식 참고용 **`candidates.jsonl.example`** 만 두고, 실행·API 연결은 후속.

## 2. 담지 않는 것

벡터 임베딩 파일, 긴 설명 텍스트 단독 저장소.

## 3. 산출·연계

`FEATURE_SPEC.md`·`DATA_SCHEMA.md`의 candidate 계약을 따른다.

---

## 4. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.
