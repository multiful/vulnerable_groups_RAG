# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/index_ready/chunks`  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---

## 1. 용도

RAG용 **청크 JSONL** 등(예: `chunks.jsonl`). 검색 단위 텍스트와 메타.  
형식 참고용 **`chunks.jsonl.example`** (Git 추적, 더미 1줄).

## 2. 담지 않는 것

추천 candidate row(구조 레인).

## 3. 산출·연계

`RAG_PIPELINE.md` §7·§8, `backend/rag/ingest/chunk_loader.py` 스키마에 맞춘다.

---

## 4. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.

## Audit Findings (by Gemini CLI) - 2026-04-17
- **Issue**: `chunks.jsonl` 내의 각 청크 데이터에 `cert_id` 메타데이터가 명시적으로 포함되어 있는지 확인이 필요함. 현재 `recommendation_service.py`는 `cert_id` 필터를 통해 Evidence를 검색하므로, 이 값이 누락되면 검색 결과가 0건이 됨.
- **Required Action**: `chunks.jsonl`을 전수 조사하여 `metadata.cert_id`가 실제 자격증 ID와 매핑되어 있는지 검증할 것.
- **Note**: `chunks.jsonl.example`에도 `cert_id`가 포함된 표준 형식을 반영하여 Claude Code가 참고할 수 있게 할 것.

