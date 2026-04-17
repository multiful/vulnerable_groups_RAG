# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `scripts/build_relations`  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---

## 1. 용도

**relation row 생성** 배치.

## 2. 담지 않는 것

엔티티 정의 변경 없이 relation만 돌릴 때 사용.

## 3. 산출·연계

`data/canonical/relations/`

---

## 4. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.

## Audit Findings (by Gemini CLI) - 2026-04-17
- **Issue**: 자격증 간 선후 관계(`cert_to_cert_relation`) 생성 시, "왜 이 순서인가?"에 대한 텍스트 근거(Reasoning)가 데이터에 포함되지 않아 추천의 신뢰성이 떨어짐.
- **Required Action**: `scripts/build_all_relations.py` (또는 전용 스크립트) 보완:
    1. `data/index_ready/parse_ir/` 내의 파싱된 JSONL 문서를 스캔.
    2. "로드맵", "권장 순서", "선행 학습", "이수 체계" 등의 키워드가 포함된 문맥에서 자격증 쌍(A -> B)의 관계 근거를 추출.
    3. 추출된 텍스트를 `cert_to_cert_relation.csv`의 `reasoning_evidence` 컬럼에 매핑하여 저장.
- **Feasibility**: 파싱된 데이터에서 자격증 명칭이 동시에 등장하는 문장을 우선적으로 필터링하여 NLP 기반(또는 정규표현식)으로 관계 문장을 선정하는 로직 구현 권장.

