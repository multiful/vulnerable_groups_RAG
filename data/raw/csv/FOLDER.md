# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/raw/csv`  
> **최종 수정일**: 2026-04-17  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, DATA_SCHEMA.md, CSV_CANONICALIZATION_TEAM_GUIDE.md, MASTER_MERGE_PLAN.md  

> **참조 규칙**: 파일이 추가될 때 본 파일과 `MASTER_MERGE_PLAN.md §8`를 같은 작업에서 갱신한다. Parse IR을 만들지 않는다.

---

## 1. 용도

마스터·매핑 등 **구조화 원본 CSV**. canonicalization의 입력이다.

---

## 2. 파일 목록 (현황)

| 파일 | 행 수 | 역할 |
|---|---|---|
| `cert_master.csv` | — | Q-Net 자격증 원본 목록 |
| `data_cert_rows.csv` | 1,086 | 시험 상세(합격률·난이도·검정횟수 등) — `backfill_cert_master.py` 소스 |
| `data_jobs_rows.csv` | — | 직무 정보 원본 |
| `job_info_rows.csv` | — | 직무 추가 정보 |
| `job_raw_merged_rows.csv` | — | 직무 병합 원본 |
| `major_master.csv` | 8,113 | 전공 목록 원본 |
| `ncs_mapping_rows.csv` | — | NCS 매핑 원본 (`cert_ncs_mapping`, `cert_major_mapping` 소스) |
| `roadmap_stage_master.csv` | 5 | 로드맵 단계 원본 |
| `한국산업인력공단_국가기술자격 학과별 직무정_rows.csv` | — | 학과별 직무 정보 |
| `한국산업인력공단_연도별 회별 국가기술자격 _rows.csv` | — | 연도별 시험 통계 |
| `행정구역별연도별성별 취득현황_rows.csv` | — | 취득 현황 통계 |
| `전공별 취득 현황_rows.csv` | — | 전공별 취득 현황 |

> `data_cert_rows.csv` 주요 컬럼: `자격증명`, `검정 횟수`, `시험종류`, `필기`, `실기`, `면접`, `난이도`  
> 시험 일정·수수료·응시자격은 이 폴더에 없음 → `data/raw/pdf/` 또는 `data/raw/html/`의 RAG 레이어에서 제공.

---

## 3. 담지 않는 것

- PDF/HTML 원본 → `data/raw/pdf/`, `data/raw/html/`
- 임의 더미 row (정책 위반)
- Parse IR → `data/index_ready/parse_ir/`

## 4. 산출·연계

`CSV_CANONICALIZATION_TEAM_GUIDE.md` 절차 → `data/processed/master/` → `data/canonical/`

---

## 5. 비고

- 대용량 원본은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.
