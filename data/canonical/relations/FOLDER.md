# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/canonical/relations`  
> **최종 수정일**: 2026-04-18  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, DATA_SCHEMA.md, MASTER_MERGE_PLAN.md, SYSTEM_ARCHITECTURE.md  

> **참조 규칙**: 파일이 추가·제거될 때 본 파일과 `MASTER_MERGE_PLAN.md §9`를 같은 작업에서 갱신한다.

---

[![Sylveon](https://img.pokemondb.net/sprites/sword-shield/normal/sylveon.png)](https://pokemondb.net/pokedex/sylveon)

## 1. 용도

엔티티 간 **관계(Relation) canonical 산출물**을 둔다. 추천 그래프·후보 생성의 직접 입력이 된다.

---

## 2. 파일 목록 (현황)

| 파일 | 행 수 | 상태 | 생성 스크립트 |
|---|---|---|---|
| `cert_domain_mapping.csv` | 1,290 | ✅ | `scripts/build_cert_domain_mapping.py` |
| `cert_to_roadmap_stage.csv` | 1,290 | ✅ | `scripts/build_all_relations.py` |
| `cert_prerequisite.csv` | 4,013 | 🔄 cross-domain 이슈 있음 | `scripts/build_all_relations.py` |
| `cert_ncs_mapping.csv` | 3,573 | ✅ cert 57.6% / ncs 95.0% | `scripts/build_all_relations.py` |
| `cert_job_mapping.csv` | 4,755 | ✅ cert 94.0% / job 100% | `scripts/build_all_relations.py` |
| `cert_major_mapping.csv` | 2,066 | ✅ | `scripts/build_cert_major_mapping.py` |
| `major_to_domain.csv` | 5,268 | ✅ | — |
| `job_to_domain.csv` | 151 | ✅ job 100% / domain 42/43 | `scripts/build_all_relations.py` |
| `risk_stage_to_roadmap_stage.csv` | 5 | ✅ | `scripts/build_all_relations.py` |
| `cert_to_cert_relation.csv` | 4,256 | ✅ parse_ir 243행 + NCS 4,013행 | `scripts/build_cert_to_cert_relation.py` |
| ~~`risk_stage_to_domain.csv`~~ | — | ❌ 삭제 — domain은 사용자 관심사로 결정 | — |

> 상세 생성 규칙·매핑 테이블은 `MASTER_MERGE_PLAN.md` 참조.

---

## 3. 담지 않는 것

- 원본 CSV 직접 복사본 → `data/raw/csv/`
- candidate row → `data/canonical/candidates/`
- 임베딩 벡터 파일

## 4. 산출·연계

`data/canonical/relations` → `data/canonical/candidates` → 추천 엔진 입력

---

## 5. 비고

- 각 파일의 스키마·의미는 `DATA_SCHEMA.md §6` 참조.
- 대용량 산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.

## Audit Findings (by Gemini CLI) - 2026-04-17
- **Issue**: 현재 관계 데이터는 자격증을 단계(Stage)에 소속시키는 일대다 관계에 치중되어 있어, "ADsP -> SQLD"와 같은 선후 관계(Sequential Roadmap) 표현이 불가능함.
- **Required Action**: `cert_to_cert_relation.csv`를 신규 생성하고, `relation_type` 컬럼을 통해 `recommended_next_step`, `prerequisite`, `synergy_pair` 등의 관계를 명시할 것.
- **Data Source**: `data/raw/pdf` 및 `html` 파싱 결과에서 "추천 로드맵", "함께 취득하면 좋은 자격증" 문구를 추출하여 이 관계 파일에 반영할 것.
- **Note**: Claude Code는 이 관계 데이터를 기반으로 `recommendation_service.py`가 단순 목록 나열이 아닌 '경로(Path)'를 생성할 수 있도록 로직 보완을 준비할 것.

### ✅ 해소 현황 (2026-04-18)
- `cert_to_cert_relation.csv` 4,256행 생성 완료. 스키마: `relation_id, from_cert_id, to_cert_id, relation_type, reasoning_evidence, source, is_active`.
- `relation_type` 값: `next_step` (parse_ir 243행) + NCS 기반 4,013행 포함.
- Audit Finding의 Required Action은 파일 생성 기준으로 완료. `recommendation_service.py` 경로 생성 로직은 미구현(다음 단계 §6 참조).

---

## 6. 미기재 파일 보충

| 파일 | 행 수 | 상태 | 비고 |
|---|---|---|---|
| `verified_ids.txt` | 37 | ✅ | 랜덤서치 검증 완료 relation_id 누적 목록. 다음 랜덤서치에서 제외 대상. |

---

## 7. 다음 단계 (as of 2026-04-18)

| 우선순위 | 항목 | 상태 | 비고 |
|---|---|---|---|
| P1 | `cert_prerequisite.csv` cross-domain 이슈 해결 | 🔄 | 동일 cert_id가 여러 도메인 걸쳐 연결되는 케이스 정리 필요 |
| P2 | `recommendation_service.py` 경로(Path) 생성 로직 구현 | ⬜ | `cert_to_cert_relation.csv` + `cert_prerequisite.csv` DAG 순회 기반 |
| P3 | downstream 인덱스 업데이트: `.build_manifest.json` diff → 변경 candidate만 반영 | ⬜ | C3 설계 완료, 실행 로직 미구현 |
| P4 | `verified_ids.txt` 랜덤서치 범위 확대 | ⬜ | 현재 37행; 주요 relation_type별 샘플링 추가 |

