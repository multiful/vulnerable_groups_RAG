# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/raw/csv`  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---

## 1. 용도

마스터·매핑 등 **구조화 원본 CSV**. canonicalization의 입력이다. **Parse IR을 만들지 않는다.**

## 2. 담지 않는 것

PDF/HTML 원본, 임의 더미 row(정책 위반).

## 3. 산출·연계

`CSV_CANONICALIZATION_TEAM_GUIDE.md` → `data/canonical/` 산출.

---

## 4. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.
