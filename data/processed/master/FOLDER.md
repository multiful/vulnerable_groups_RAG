# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `data/processed/master`  
> **최종 수정일**: 2026-04-07  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, DATA_SCHEMA.md, CSV_CANONICALIZATION_TEAM_GUIDE.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: master 산출물 규칙이 바뀌면 본 파일과 `DIRECTORY_SPEC.md`, `PROJECT_SUMMARY.md`를 같은 작업에서 갱신한다.

---

## 1. 용도

raw CSV에서 정제된 **master 중간 산출물**을 둔다.

예:
- `cert_master.csv`
- `domain_master.csv`
- `job_master.csv`
- `major_master.csv`

## 2. 담는 데이터

- 표준 ID
- 표준 라벨/표시명
- 정규화 키(`normalized_key`)
- 활성 여부(`is_active`)

## 3. 담지 않는 것

- 원천 원본 rows 데이터 (`data/raw/csv/*_rows.csv`)
- 엔티티/관계 canonical 최종본 (`data/canonical/*`)

## 4. 산출·연계

- `data/processed/master` → `data/processed/mappings` → `data/canonical/entities|relations` 순으로 연계한다.
- 매핑/관계 생성 시 master ID(FK) 기준 정합성 검증을 수행한다.

---

## 5. 비고

- 이 폴더는 협업용 중간 기준선으로 사용한다.
- 팀 합의 전까지 기존 `data/raw/csv/*_master.csv`와 병행할 수 있다.
