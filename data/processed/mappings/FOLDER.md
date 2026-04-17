# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/processed/mappings`  
> **최종 수정일**: 2026-04-07  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, DATA_SCHEMA.md, CSV_CANONICALIZATION_TEAM_GUIDE.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 매핑 산출물의 스키마/이름 규칙이 바뀌면 본 파일과 `DATA_SCHEMA.md`를 같은 작업에서 갱신한다.

---

## 1. 용도

raw 자유 텍스트를 master ID로 연결한 **매핑 중간 산출물**을 둔다.

예:
- `job_alias_mapping.csv` — **직무명·별칭(`normalized_key`) → `job_role_id` 단일 사전**(원문 표기는 `alternate_raw_labels`에 병기)
- `job_row_alias_bridge.csv` — `job_raw_merged_rows.csv` **각 원천 행 → `job_alias_id`** (여기에는 `job_role_id`를 두지 않음; alias와 조인)
- `cert_domain_mapping.csv`
- `cert_job_mapping.csv`
- `major_job_mapping.csv`
- `job_domain_mapping.csv`

## 2. 담는 데이터

- `raw_*_name` 또는 원천 키
- 대상 master ID (`job_role_id`, `domain_sub_label_id`, `cert_id` 등) — 단, 행→alias 브리지는 **FK만** 두고 직무 ID는 alias에서 조인
- 매핑 상태(`unmapped`, `auto_exact`, `auto_partial`, `manual`)
- 출처/활성 여부 (`source_dataset`, `is_active`)

## 3. 담지 않는 것

- 원본 단일 소스 전체 복사본 (`data/raw/`에 보관)
- canonical 확정 엔티티/관계 최종본 (`data/canonical/`에 보관)

## 4. 산출·연계

- 검수 완료 매핑은 `data/canonical/relations/` 생성의 입력으로 사용한다.
- 추천 후보 생성 전 FK 정합성 검증(마스터 ID 존재 여부)을 통과해야 한다.

---

## 5. 비고

- 이 폴더는 “최종 진실 소스”가 아니라 **정규화/매핑 작업 공간**이다.
- 대용량 산출물은 Git 정책(`.gitignore`)과 증분 원칙(`HASH_INCREMENTAL_BUILD_GUIDE.md`)을 따른다.

## Audit Findings (by Gemini CLI) - 2026-04-17
- **Issue**: 매핑 파일(`job_alias_mapping.csv` 등) 생성 시, 원본 데이터의 `source_hash`가 포함되어 있지 않아 원본 데이터 업데이트 시 어떤 행이 재매핑이 필요한지 파악하기 어려움.
- **Required Action**: 모든 매핑 CSV 파일에 원본 행의 해시 또는 파일 해시 정보를 기록하는 `input_source_hash` 컬럼을 추가할 것.
- **Note**: `unmapped` 상태의 행들을 정기적으로 추출하여 Taxonomy에 반영하거나 매핑을 강제하는 **Maintenance 배치**가 필요함.

