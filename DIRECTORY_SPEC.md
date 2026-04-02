# DIRECTORY_SPEC.md

## 1. 문서 목적

이 문서는 프로젝트의 **최종 디렉토리 기준선**을 정의한다.  
앞으로 새로운 파일이나 폴더를 추가할 때는 이 문서를 먼저 확인하고, 기존 구조와 역할 충돌이 없는지 점검한 뒤 반영한다.

이 프로젝트는 다음 원칙으로 운영한다.

- 루트 md 문서가 프로젝트의 기준선이다.
- 기능 변경이나 구조 변경은 먼저 루트 문서를 수정한 뒤 구현에 반영한다.
- 현재는 MVP 단계이므로, 최종 구조를 먼저 고정하되 실제 활성화는 단계적으로 진행한다.
- `infra`, `shared`, 일정 API 관련 영역은 필요 시점까지 reserved 상태로 둘 수 있다.

---

## 2. 최종 결론

현재 프로젝트의 **최종 루트 디렉토리 구조는 아래와 같다.**

```text
project-root/
├─ .gitignore
├─ README.md
├─ PRD.md
├─ SYSTEM_ARCHITECTURE.md
├─ FEATURE_SPEC.md
├─ API_SPEC.md
├─ PROMPT_DESIGN.md
├─ DATA_SCHEMA.md
├─ RAG_PIPELINE.md
├─ EVALUATION_GUIDELINE.md
├─ EVALUATION.md
├─ EXPERIMENT_GUIDE.md
├─ ERROR_ANALYSIS.md
├─ DEV_LOG.md
│
├─ docs/
├─ data/
├─ frontend/
├─ backend/
├─ scripts/
├─ experiments/
├─ infra/
└─ shared/
```

---

## 3. 이 구조가 맞는 이유

이 프로젝트는 다음 흐름을 가진다.

1. **루트 문서**
   - 제품 요구사항, 시스템 구조, 기능 정의, 데이터 스키마, RAG 구조, 평가 기준을 관리

2. **데이터 파이프라인**
   - PDF / HTML / CSV / API를 source_type 기준으로 분리
   - PDF / HTML은 Parse 기반
   - CSV / API는 structured no-parse 기반

3. **서비스 구현**
   - frontend: 사용자 화면
   - backend: API / 추천 / 로드맵 / retrieval / canonicalization

4. **배치 및 실험**
   - scripts: 일회성 실행
   - experiments: 재현성과 로그 관리

즉, 이 구조는 **문서 / 데이터 / 서비스 / 실험 / 배포**를 분리한 최종 운영 구조로 적절하다.

---

## 4. 최종 루트 폴더 설명

### `.gitignore`
Git 추적 제외 대상 정의

### `README.md`
프로젝트 개요, 범위, 기능 요약, 기술 스택, 시작 가이드

### `PRD.md`
문제 정의, 타깃 사용자, 핵심 기능, 제품 범위

### `SYSTEM_ARCHITECTURE.md`
전체 시스템 흐름, 데이터 흐름, 프론트/백엔드/AI 역할

### `FEATURE_SPEC.md`
기능별 입력 / 출력 / 예외처리 명세

### `API_SPEC.md`
백엔드 API endpoint 명세

### `PROMPT_DESIGN.md`
시스템 프롬프트, few-shot, 프롬프트 전략, 체인/RAG 전략

### `DATA_SCHEMA.md`
DB 구조, canonical schema, 주요 테이블 및 컬럼 정의

### `RAG_PIPELINE.md`
Parse / Chunk / Embedding / Store와 retrieval 구조 명세

### `EVALUATION_GUIDELINE.md`
평가 기준 정의 문서  
예: baseline, metric 선택 이유, 비교 기준

### `EVALUATION.md`
실제 평가 결과와 실험 결과 기록

### `EXPERIMENT_GUIDE.md`
실험 세팅, 파라미터, 재현 절차, 로그 기록 방식

### `ERROR_ANALYSIS.md`
실패 사례, 공통 오류 패턴, 개선 방향

### `DEV_LOG.md`
날짜별 진행 로그, 문제 및 해결 기록

---

## 5. 최종 하위 디렉토리 구조

### 5.1 docs/

```text
docs/
├─ slides/
├─ references/
├─ architecture/
└─ meeting_notes/
```

#### 역할
- `slides/`: 발표 자료
- `references/`: 참고문헌, 논문, 기준 문서
- `architecture/`: 구조도, 설계도, 플로우차트
- `meeting_notes/`: 회의 기록, 의사결정 메모

---

### 5.2 data/

```text
data/
├─ raw/
│  ├─ pdf/
│  ├─ html/
│  ├─ csv/
│  └─ api/
│
├─ taxonomy/
│  ├─ domain_v2.txt
│  ├─ prefer_job.txt
│  └─ risk_stage_master.csv
│
├─ canonical/
│  ├─ entities/
│  ├─ relations/
│  ├─ candidates/
│  └─ validation/
│
├─ index_ready/
│  ├─ parse_ir/
│  ├─ chunks/
│  ├─ metadata/
│  ├─ dense_input/
│  └─ sparse_input/
│
└─ processed/
   ├─ merged/
   └─ snapshots/
```

#### 역할
- `raw/`: 원본 수집 데이터
- `taxonomy/`: 도메인/직무/위험군 기준 taxonomy
- `canonical/`: CSV canonicalization 결과
- `index_ready/`: RAG / retrieval 입력용 산출물
- `processed/`: 중간 병합본 및 스냅샷

#### 원칙
- PDF / HTML은 Parse IR 생성 가능
- CSV는 Parse IR이 아니라 canonicalization 대상
- API는 후속 스프린트에서 연결 예정

---

### 5.3 frontend/

```text
frontend/
├─ public/
│  └─ assets/
│
├─ src/
│  ├─ app/
│  ├─ pages/
│  │  ├─ Home/
│  │  ├─ RiskAssessment/
│  │  ├─ Recommendation/
│  │  ├─ Roadmap/
│  │  ├─ Schedule/
│  │  └─ Admin/
│  │
│  ├─ components/
│  │  ├─ layout/
│  │  ├─ cards/
│  │  ├─ charts/
│  │  ├─ forms/
│  │  └─ feedback/
│  │
│  ├─ features/
│  │  ├─ risk-stage/
│  │  ├─ recommendation/
│  │  ├─ roadmap/
│  │  └─ schedule/
│  │
│  ├─ api/
│  ├─ hooks/
│  ├─ store/
│  ├─ types/
│  ├─ utils/
│  ├─ constants/
│  └─ styles/
│
├─ tests/
└─ package.json
```

#### 역할
- 위험군 입력
- 추천 결과 표시
- 로드맵 결과 표시
- 추후 일정/링크 화면 제공

#### 현재 활성화 우선순위
- `Home`
- `RiskAssessment`
- `Recommendation`
- `Roadmap`

#### reserved 가능
- `Schedule`
- `Admin`

---

### 5.4 backend/

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  ├─ api/
│  │  ├─ deps.py
│  │  └─ v1/
│  │     ├─ routes/
│  │     │  ├─ health.py
│  │     │  ├─ risk.py
│  │     │  ├─ recommendation.py
│  │     │  ├─ roadmap.py
│  │     │  ├─ schedule.py
│  │     │  └─ admin.py
│  │     └─ schemas/
│  │
│  ├─ services/
│  │  ├─ risk_stage_service.py
│  │  ├─ recommendation_service.py
│  │  ├─ roadmap_service.py
│  │  ├─ schedule_service.py
│  │  ├─ retrieval_service.py
│  │  └─ metadata_service.py
│  │
│  ├─ repositories/
│  ├─ models/
│  ├─ schemas/
│  └─ utils/
│
├─ rag/
│  ├─ ingest/
│  ├─ retrieval/
│  ├─ prompts/
│  └─ evaluation/
│
├─ canonical/
│  ├─ registry/
│  ├─ pipeline/
│  ├─ schemas/
│  └─ outputs/
│
├─ tests/
└─ requirements.txt
```

#### 역할
- API 제공
- 위험군 분류 / 추천 / 로드맵 로직
- PDF/HTML RAG 처리
- CSV canonicalization 처리

#### backend/app/
사용자 기능과 API 담당

- `risk.py`: 위험군 관련 API
- `recommendation.py`: 추천 결과 API
- `roadmap.py`: 로드맵 API
- `schedule.py`: 후속 일정 API
- `admin.py`: 점검/운영 API

#### backend/rag/
PDF / HTML 기반 Parse / Chunk / Embedding / Retrieval 담당

```text
backend/rag/
├─ ingest/
│  ├─ source_router.py
│  ├─ parse_pdf.py
│  ├─ parse_html.py
│  ├─ table_assist.py
│  ├─ ocr_queue.py
│  ├─ fallback_docling.py
│  ├─ boilerplate_cleaner.py
│  ├─ reading_order.py
│  ├─ chunk_builder.py
│  ├─ metadata_tagger.py
│  └─ embedding_builder.py
│
├─ retrieval/
│  ├─ dense_retriever.py
│  ├─ sparse_retriever.py
│  ├─ fusion.py
│  ├─ filters.py
│  └─ reranker.py
│
├─ prompts/
└─ evaluation/
```

#### backend/canonical/
CSV structured no-parse 처리 전용

```text
backend/canonical/
├─ registry/
│  ├─ dataset_registry.yaml
│  ├─ schema_mapping_registry.yaml
│  ├─ domain_taxonomy_master.csv
│  └─ job_taxonomy_master.csv
│
├─ pipeline/
│  ├─ detect_dataset_type.py
│  ├─ schema_mapper.py
│  ├─ canonicalizer.py
│  ├─ entity_builder.py
│  ├─ relation_builder.py
│  ├─ candidate_builder.py
│  └─ validator.py
│
├─ schemas/
│  ├─ entity_schema.py
│  ├─ relation_schema.py
│  ├─ candidate_schema.py
│  └─ validation_schema.py
│
└─ outputs/
   ├─ canonical_entity_table.csv
   ├─ canonical_relation_table.csv
   ├─ certificate_candidate_row.csv
   └─ validation_report.csv
```

---

### 5.5 scripts/

```text
scripts/
├─ parse/
├─ canonicalize/
├─ build_entities/
├─ build_relations/
├─ build_candidates/
├─ evaluation/
└─ maintenance/
```

#### 역할
일회성 실행, 배치, 점검 스크립트

- `parse/`: PDF/HTML parse 실행
- `canonicalize/`: CSV canonicalization 실행
- `build_entities/`: entity 생성
- `build_relations/`: relation 생성
- `build_candidates/`: 추천 candidate row 생성
- `evaluation/`: 평가 실행
- `maintenance/`: 문서/데이터 일관성 점검

---

### 5.6 experiments/

```text
experiments/
├─ configs/
├─ logs/
├─ reports/
├─ baselines/
└─ notebooks/
```

#### 역할
- 실험 설정 관리
- 로그 저장
- baseline 비교
- 재현성 확보
- 분석 노트북 관리

---

### 5.7 infra/

```text
infra/
├─ docker/
├─ deploy/
└─ env/
```

#### 역할
배포/실행 환경 관련 설정

#### 현재 상태
reserved 가능  
MVP 단계에서는 최소만 유지해도 된다.

---

### 5.8 shared/

```text
shared/
├─ constants/
├─ schemas/
└─ types/
```

#### 역할
frontend / backend 공용 상수, schema, 타입 정의

#### 현재 상태
필수는 아님  
공용 구조가 많아질 때 활성화해도 된다.

---

## 6. 지금 바로 생성할 것

아래는 **즉시 생성 권장** 영역이다.

### 루트 문서
- `.gitignore`
- `README.md`
- `PRD.md`
- `SYSTEM_ARCHITECTURE.md`
- `FEATURE_SPEC.md`
- `API_SPEC.md`
- `PROMPT_DESIGN.md`
- `DATA_SCHEMA.md`
- `RAG_PIPELINE.md`
- `EVALUATION_GUIDELINE.md`
- `EVALUATION.md`
- `EXPERIMENT_GUIDE.md`
- `ERROR_ANALYSIS.md`
- `DEV_LOG.md`

### 핵심 폴더
- `docs/slides`
- `docs/references`
- `docs/architecture`
- `data/raw/pdf`
- `data/raw/html`
- `data/raw/csv`
- `data/taxonomy`
- `data/canonical`
- `data/index_ready`
- `frontend/src`
- `backend/app`
- `backend/rag`
- `backend/canonical`
- `scripts/parse`
- `scripts/canonicalize`
- `experiments/logs`
- `experiments/reports`

---

## 7. 나중에 생성해도 되는 것

아래는 **reserved 가능** 영역이다.

- `data/raw/api`
- `frontend/src/pages/Schedule`
- `frontend/src/pages/Admin`
- `backend/app/api/v1/routes/schedule.py`
- `backend/app/services/schedule_service.py`
- `backend/rag/retrieval/reranker.py`
- `infra/`
- `shared/`
- `experiments/baselines/`
- `experiments/notebooks/`
- `docs/meeting_notes/`

---

## 8. 운영 규칙

1. 구조 변경은 먼저 이 문서를 수정한다.
2. 기능 변경은 먼저 루트 md 문서를 수정한다.
3. CSV는 Parse IR 대상으로 처리하지 않는다.
4. `related_domains`는 도메인 taxonomy 세부 라벨만 허용한다.
5. `related_jobs`는 희망 직무 taxonomy 세부 직무만 허용한다.
6. 위험군은 1단계 ~ 5단계 구조로 관리한다.
7. 일정/링크 API는 후속 스프린트에서 canonical target schema에 병합한다.
8. 구현보다 문서가 먼저이며, 문서는 프로젝트의 단일 기준선 역할을 한다.

---

## 9. 최종 디렉토리

```text
project-root/
├─ .gitignore
├─ README.md
├─ PRD.md
├─ SYSTEM_ARCHITECTURE.md
├─ FEATURE_SPEC.md
├─ API_SPEC.md
├─ PROMPT_DESIGN.md
├─ DATA_SCHEMA.md
├─ RAG_PIPELINE.md
├─ EVALUATION_GUIDELINE.md
├─ EVALUATION.md
├─ EXPERIMENT_GUIDE.md
├─ ERROR_ANALYSIS.md
├─ DEV_LOG.md
│
├─ docs/
├─ data/
├─ frontend/
├─ backend/
├─ scripts/
├─ experiments/
├─ infra/
└─ shared/
```