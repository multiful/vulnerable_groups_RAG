# CSV_CANONICALIZATION_TEAM_GUIDE.md

> **파일명**: CSV_CANONICALIZATION_TEAM_GUIDE.md  
> **최종 수정일**: 2026-04-04  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 영민,유빈용 — CSV 넣기·전처리·canonical까지 (청킹 제외)  
> **문서 우선순위**: reference (필드 정의는 `DATA_SCHEMA.md`가 더 위)  
> **연관 문서**: DATA_SCHEMA.md, DIRECTORY_SPEC.md, RAG_PIPELINE.md — CSV 정규화 시 참고 파일 전체 목록은 §9  
> **참조 규칙**: 컬럼·필드 정의를 바꾸면 먼저 `DATA_SCHEMA.md`를 고치고, 이 문서 설명을 맞춘다.

---

## 1. 한 줄로 요약

**영민**과 **유빈**은 **CSV 데이터를 직접 넣고**, 기획서·`DATA_SCHEMA.md`에 맞게 **손질(전처리)** 한 뒤 **canonical 형태**까지 만드는 것까지가 임무다.  
**청킹·임베딩·RAG 인덱스**는 이 단계가 아니다. (다른 사람/다음 단계)

---

## 2. 임무의 끝선 (여기까지만 하면 됨)

| 하는 것 | 안 하는 것 |
|--------|------------|
| 원본 CSV를 `data/raw/csv/`에 넣기 | PDF/HTML처럼 “파싱해서 IR” 만들기 |
| 필요한 컬럼 만들기, 쓸모없는 컬럼 빼기, 값 정리하기 | 청킹(chunk 나누기) |
| `DATA_SCHEMA.md`에 맞는 컬럼명·값으로 맞추기 (canonicalization) | 벡터 DB 넣기, 임베딩 |
| `data/canonical/` 아래에 엔티티·관계·(필요 시) 후보 파일로보내기 | 가짜 일정·가짜 URL 대량 만들기 (reserved) |

---

## 3. 역할 구분 (고정)

같은 CSV를 **동시에 두 명이 수정하지 않는다.** 파일(또는 dataset) 단위로 **오늘 누가 주인인지** 정하고 작업한다.

### 3.1 영민 — 담당

**“마스터” 한 장짜리 표**를 맡는다. (기준이 되는 목록)

- 자격증 마스터, 도메인 마스터, 직무 마스터  
- 로드맵 단계 마스터, 위험군(단계) 마스터, 주관 기관 마스터  
- 전공 마스터, 자격증 alias 표  
- 위 표들에 해당하는 원본을 **직접 수집해서** `data/raw/csv/`에 넣는다.  
- 각 파일에 대해: **필요한 컬럼만 남기고**, `DATA_SCHEMA.md`의 필드명에 맞게 **이름·값을 정리**한다.  
- 정리한 결과를 **`data/canonical/entities/`** 쪽 규칙(엔티티 형태)으로 맞춰 저장한다.  
- **ID(`cert_id`, `domain_sub_label_id` 등)는 영민이 만든 마스터가 기준**이다. 유빈이 나중에 이 ID를 그대로 쓴다.

### 3.2 유빈 — 담당

**“둘을 잇는 매핑 표”**를 맡는다. (교차표)

- 전공↔직무, 자격증↔직무, 자격증↔도메인, 직무↔도메인  
- 도메인↔위험군↔로드맵 단계 같은 조합 표  
- 자격증 선행/후속, 자격증–주관기관 연결 등  
- 위에 해당하는 원본을 **직접 수집해서** `data/raw/csv/`에 넣는다.  
- **영민이 만든 마스터의 ID가 맞는지** 보면서 전처리한다. (없는 `cert_id`로 연결하면 안 됨)  
- 필요 없는 컬럼은 빼고, `DATA_SCHEMA.md`의 관계(relationship) 필드에 맞게 컬럼을 맞춘다.  
- 정리한 결과를 **`data/canonical/relations/`** (및 기획상 필요하면 `candidates/`) 규칙에 맞게 저장한다.

### 3.3 둘 다 공통

- 도메인·직무 **세부 라벨(표시명)** 은 **`data/taxonomy/domain_v2.txt`**, **`data/taxonomy/prefer_job.txt`** 에 나온 것만 쓴다. **새 이름을 임의로 만들지 않는다.**  
- `DATA_SCHEMA.md`는 엔티티에 **`domain_sub_label_id`**, **`job_role_id`** 같은 **안정 ID**를 요구한다. 위 txt는 **허용 라벨 목록**이고, 실제 작업에서는 영민이 만든 **`domain_master` / `job_master`** 행에 **ID + 라벨 + (가능하면) 상위 그룹명**을 같이 둔다. **라벨만 있고 ID가 없으면** canonical에 넣지 말고 스키마·팀에 먼저 맞춘다.  
- 외부에서 받은 원본 CSV(통합학과·세부전공·자격증 통계 등)는 **`DATA_SCHEMA.md` §18(초기 원천 CSV 적재 범위와 한계)** 를 읽고, 어떤 필드가 **마스터/매핑/파이프라인 생성** 중 어디에 들어가는지 구분한 뒤 전처리한다.  
- **더미 데이터**(가짜 자격증 대량, 가짜 시험일정)는 넣지 않는다.  
- 막히면 코드 짜기 전에 **`DATA_SCHEMA.md`를 고쳐 달라고** 요청한다.

---

## 4. 실행 순서 (이 순서만 지키면 됨)

1. **넣기**  
   - 받은/만든 CSV를 `data/raw/csv/`에 복사한다.  
   - 파일 이름에 날짜나 출처가 보이게 해도 좋다. (예: `cert_master_20260403.csv`)

2. **전처리**  
   - 엑셀·스프레드시트에서: 빈 열 삭제, 헤더 한 줄로 통일, 이상한 공백·오타 정리  
   - **필요한 컬럼 추가** (`DATA_SCHEMA.md`에 있는데 원본에 없으면)  
   - **필요 없는 컬럼 삭제** (스키마에 없고 쓸 데도 없으면)

3. **canonicalization (정규화)**  
   - 컬럼 이름을 `DATA_SCHEMA.md`와 **같게** 맞춘다.  
   - 날짜는 `YYYY-MM-DD`, ID는 중복 없게, taxonomy 라벨은 파일에 있는 것만.

4. **보내기**  
   - 영민 → `data/canonical/entities/`  
   - 유빈 → `data/canonical/relations/` (필요 시 `candidates/`)  
   - 검증 메모(뭐가 맞았는지/이상한 줄)는 `data/canonical/validation/`에 짧게 적어도 된다.

5. **끝**  
   - 여기서 멈춘다. **청킹·JSONL·Supabase**는 하지 않는다.

---

## 5. 어떤 CSV가 있는지 (참고 표)

기획 슬라이드·`Indexing_Architecture.txt`와 맞춘 **논리적 dataset_type** 이름이다. 실제 수령 파일명(`integrated_major1.csv` 등)과 다를 수 있으니, §3·§4대로 전처리한 뒤 아래 **역할**에 편입하면 된다. **영민=마스터 쪽**, **유빈=매핑 쪽**으로 대략 갈린다.

| 구분 | dataset_type (파일 이름에 써도 됨) | 담당(기본) |
|------|-------------------------------------|------------|
| 마스터 | `cert_master`, `cert_alias`, `domain_master`, `job_master`, `roadmap_stage_master`, `risk_stage_master`, `hosting_org_master`, `major_master` | 영민 |
| 매핑 | `major_job_mapping`, `cert_job_mapping`, `cert_domain_mapping`, `job_domain_mapping`, `domain_risk_roadmap_mapping`, `cert_prerequisite`, `cert_hosting_org`, `cert_recommended_debut` | 유빈 |

**시험일정·접수일정·지원 링크 CSV**는 지금 단계에서 **실데이터로 채우지 않는다** (제품에서 reserved).

---

## 6. 자주 헷갈리는 것

- **“CSV도 RAG에 넣나?”** → **아니요.** CSV는 문서처럼 청크하지 않는다. (`RAG_PIPELINE.md`)  
- **“Parse 단계 슬라이드는?”** → 그건 **PDF/HTML**용이다. CSV는 **Parse 건너뛰고** 지금 문서대로만 하면 된다.

---

## 7. 인계 전 체크 (짧게)

- [ ] `data/raw/csv/`에 원본이 들어가 있음  
- [ ] 전처리·canonical 파일이 `data/canonical/entities/` 또는 `relations/` 등에 있음  
- [ ] taxonomy 밖 라벨 없음  
- [ ] 유빈 표의 `cert_id` 등이 영민 마스터와 모두 연결됨  
- [ ] 청킹·임베딩은 안 함

---

## 8. 더 자세한 필드 정의가 필요하면

항상 **`DATA_SCHEMA.md`** 를 연다. 이 문서는 **일하는 방법**만 적고, **컬럼 하나하나의 법적 정의**는 스키마 문서에 있다.

---

## 9. CSV 정규화 시 참고할 파일·경로

CSV를 **정규화(canonicalization)** 할 때 아래를 참고한다. **필드 정의·제약의 단일 기준**은 `DATA_SCHEMA.md`이고, 문서 간 충돌이 있으면 `CHANGE_CONTROL.md`의 우선순위에 따른다.

### 9.1 반드시 볼 것 (계약·절차)

| 참고 | 용도 |
|------|------|
| **`DATA_SCHEMA.md`** | 엔티티·관계·`certificate_candidate_row` 필드명, 필수/선택, taxonomy 제약, §18 원천 CSV 적재 범위·한계 |
| **`CSV_CANONICALIZATION_TEAM_GUIDE.md`** (본 문서) | raw 넣는 위치, 역할 분담, 실행 순서, 임무 끝선 |
| **`DIRECTORY_SPEC.md`** | `data/raw/csv/`, `data/canonical/entities`, `relations`, `candidates`, `validation`, `data/taxonomy/` 구조 |
| **`data/taxonomy/domain_v2.txt`** | 허용 **도메인** 세부 라벨(표시명 후보) |
| **`data/taxonomy/prefer_job.txt`** | 허용 **희망 직무** 세부 라벨(표시명 후보) |
| **`data/taxonomy/risk_stage_master.csv`** | 위험군 마스터. **아직 없으면** `DATA_SCHEMA.md`·`DIRECTORY_SPEC.md`에 맞춰 영민이 생성해 `data/taxonomy/`에 둔다(더미 행 금지). |

### 9.2 맥락·규칙 맞출 때

| 참고 | 용도 |
|------|------|
| **`CHANGE_CONTROL.md`** | 문서 우선순위, 갱신 절차, 해시·메타데이터 규칙 |
| **`README.md`** | CSV는 structured no-parse, 문서(PDF/HTML) 레인과 분리 |
| **`PRD.md`** | 현재 범위·비범위(reserved 일정·링크 등) |
| **`FEATURE_SPEC.md`** | 입력 정규화, taxonomy 밖 값 처리, validation 관점 |
| **`RAG_PIPELINE.md`** | CSV는 Parse IR을 만들지 않는다는 점 |

### 9.3 아키텍처·산출물이 어디로 가는지

| 참고 | 용도 |
|------|------|
| **`SYSTEM_ARCHITECTURE.md`** | canonical 데이터 → 추천·RAG 흐름 |
| **`API_SPEC.md`** | (정의되어 있으면) 응답 필드와 스키마 정합 |

### 9.4 보조·탐색용 (필수는 아님)

| 참고 | 용도 |
|------|------|
| **`PROJECT_SUMMARY.md`** | 저장소 한 장 요약, 문서 지도 |
| **`ROOT_DOC_GUIDE.md`** | 상황별로 어떤 루트 md를 열지 |
| **`Indexing_Architecture.txt`** | §5 dataset_type 이름과 맞춘 기획 참고 |
| **`HASH_INCREMENTAL_BUILD_GUIDE.md`** | 증분·해시·재처리 설계(스크립트·빌드 단계에서) |
| **`DEV_LOG.md`** | 최근 합의·주의(임의 더미 등) |

### 9.5 작업 폴더 (파일이 아님)

- **`data/raw/csv/`** — 넣는 원본 CSV  
- **`data/canonical/entities/`** — 마스터·엔티티 정리본  
- **`data/canonical/relations/`** — 관계(매핑) 정리본  
- **`data/canonical/candidates/`** — (필요 시) 추천 후보 행  
- **`data/canonical/validation/`** — 검증 메모·리포트  

**한 줄 요약**: 정규화의 **법적 기준**은 **`DATA_SCHEMA.md`**, **일하는 방법·경로**는 **본 문서 + `DIRECTORY_SPEC.md`**, **라벨 허용 범위**는 **`domain_v2.txt` / `prefer_job.txt`** (+ 위험군는 **`risk_stage_master.csv`** 또는 동급 마스터)이다.
