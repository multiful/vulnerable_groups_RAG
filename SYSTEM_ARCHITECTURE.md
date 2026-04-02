# SYSTEM_ARCHITECTURE.md

## 1. 문서 목적

이 문서는 시스템의 **구성 요소**, **책임 분리**, **데이터 흐름**, **모듈 간 경계**를 정의한다.  
이 문서는 제품의 필요성과 기능 우선순위를 설명하는 문서가 아니라, 확정된 요구사항을 **구현 가능한 시스템 구조**로 변환하는 기준 문서다.

이 문서가 다루는 범위는 아래와 같다.

- 프론트엔드 / 백엔드 / RAG / canonicalization 계층의 역할
- source_type 기반 처리 경로
- ingest, retrieval, recommendation, roadmap 생성 흐름
- 저장소 계층과 인덱스 계층의 역할
- 현재 활성화 범위와 reserved 범위

이 문서는 다음을 직접 정의하지 않는다.

- 제품 문제 정의, 사용자 가치, 제품 범위 상세
- 기능별 입력/출력/예외처리 상세
- API endpoint 상세 명세
- DB 컬럼 단위 상세 정의
- 평가 지표와 실험 기준
- 프롬프트 세부 내용

위 항목은 각각 `PRD.md`, `FEATURE_SPEC.md`, `API_SPEC.md`, `DATA_SCHEMA.md`, `EVALUATION_GUIDELINE.md`, `PROMPT_DESIGN.md`에서 담당한다.

---

## 2. 아키텍처 목표

시스템은 다음 3개 축을 안정적으로 연결해야 한다.

1. **Recommendation Core**
   - 위험군 단계, 직무, 도메인, 자격증, 로드맵의 관계를 기반으로 추천 후보를 계산한다.

2. **Evidence Retrieval**
   - PDF / HTML 문서에서 추천 결과를 설명할 근거 텍스트를 검색한다.

3. **Delivery Layer**
   - 프론트 요청을 받아 추천 결과, 설명 근거, 로드맵을 조합하여 응답한다.

즉, 시스템은 “추천을 계산하는 구조적 기반”과 “추천을 설명하는 문서 기반 근거”를 분리하여 설계한다.

---

## 3. 최상위 구성

시스템은 크게 다음 6개 영역으로 구성된다.

1. **Frontend**
2. **Backend Application Layer**
3. **RAG Ingestion / Retrieval Layer**
4. **CSV Canonicalization Layer**
5. **Storage Layer**
6. **Batch / Evaluation Layer**

---

## 4. 상위 아키텍처 다이어그램

```text
[User]
   ↓
[Frontend]
   ↓
[Backend API / Service Layer]
   ├─ Recommendation Core
   │   └─ Canonical Relational Store
   │
   ├─ Roadmap Builder
   │   └─ Canonical Relational Store
   │
   └─ Evidence Retrieval
       ├─ Vector Store
       └─ Sparse/BM25 Store (optional)

────────────────────────────────────────────────────────

[Raw Knowledge Sources]
├─ Official PDF / HTML
├─ Structured CSV
└─ External API (후속 스프린트)

         ↓

[Source Routing & Profiling]
         ↓

┌────────────── PDF / HTML Lane ──────────────┐
│ HTML Direct Path                            │
│ Primary PDF Parser                          │
│ Table Assist / OCR / Fallback               │
│ Boilerplate Removal / Reading Order Fix     │
│ Chunk Builder / Metadata / Embedding        │
└─────────────────────────────────────────────┘

┌────────────── CSV / API Lane ───────────────┐
│ Dataset Type Registry                       │
│ Schema Mapping                              │
│ Canonicalization                            │
│ Entity Builder                              │
│ Relation Builder                            │
│ Candidate Row Builder                       │
└─────────────────────────────────────────────┘

         ↓

[Canonical Merge / Index Build]
   ├─ Canonical Relational Store
   ├─ Vector Store
   └─ Sparse/BM25 Store (optional)
```

---

## 5. 계층별 책임

## 5.1 Frontend

프론트엔드는 사용자 입력과 결과 표시를 담당한다.  
프론트는 가능한 한 얇게 유지하며, 도메인 판단과 추천 로직은 백엔드에 둔다.

### 주요 책임
- 위험군 진입 UI 제공
- 관심 직무 / 도메인 입력 수집
- 추천 결과 표시
- 로드맵 결과 표시
- 설명 근거 표시
- 추후 일정 / 접수 / 링크 결과 표시

### 현재 활성화 대상
- Home
- RiskAssessment
- Recommendation
- Roadmap

### reserved
- Schedule
- Admin

---

## 5.2 Backend Application Layer

백엔드 애플리케이션 계층은 전체 흐름의 조정자다.  
프론트 요청을 받아 입력을 해석하고, canonical store와 retrieval layer를 조합해 최종 응답을 생성한다.

### 주요 책임
- API endpoint 제공
- request/response schema 검증
- risk stage 기준 반영
- recommendation orchestration
- roadmap 생성
- retrieval 결과 결합
- 프론트 응답 포맷 생성

### 핵심 서비스
- `risk_stage_service`
- `recommendation_service`
- `roadmap_service`
- `retrieval_service`
- `metadata_service`

### reserved
- `schedule_service`

---

## 5.3 RAG Ingestion / Retrieval Layer

이 계층은 PDF / HTML 기반 지식 문서를 검색 가능한 상태로 변환하고, 이후 검색 요청에 대해 설명 근거를 반환한다.

이 계층의 목적은 “추천 계산”이 아니라 **설명 근거 검색**이다.

### 주요 책임
- source_type 기반 문서 라우팅
- PDF / HTML parse
- table assist / OCR / fallback 처리
- chunk 생성
- metadata tagging
- embedding 생성
- dense / sparse retrieval 수행

---

## 5.4 CSV Canonicalization Layer

이 계층은 CSV를 Parse IR로 바꾸지 않고, 추천 가능한 구조적 자산으로 변환한다.

### 주요 책임
- dataset type 판별
- schema mapping
- canonicalization
- entity 생성
- relation 생성
- recommendation candidate row 생성
- validation report 생성

### 처리 원칙
- CSV는 Parse IR 대상이 아니다.
- CSV는 structured no-parse 경로를 따른다.
- taxonomy 밖의 자유 라벨 생성을 허용하지 않는다.

---

## 5.5 Storage Layer

시스템은 저장 목적에 따라 저장소를 분리한다.

### Canonical Relational Store
구조화된 사실 기반 저장소

저장 대상 예:
- canonical entities
- canonical relations
- recommendation candidate rows
- risk stage / roadmap stage 기준 데이터

### Vector Store
PDF / HTML 설명 근거 검색용 dense retrieval 저장소

저장 대상 예:
- FAQ chunk
- 안내문 chunk
- 공고문 chunk
- 공식 HTML 설명 chunk

### Sparse / BM25 Store
exact match 보강용 선택 저장소

저장 대상 예:
- alias 기반 exact text
- 기관명 / 자격증명 / 직무명 / 고정 용어
- exact-sensitive 텍스트

현재는 optional로 둔다.

---

## 5.6 Batch / Evaluation Layer

운영 API와 분리된 배치 및 실험 계층이다.

### 주요 책임
- parse 배치 실행
- canonicalization 배치 실행
- index build
- validation
- retrieval / parse / chunk 평가
- 실험 로그 및 baseline 관리

---

## 6. source_type 기반 처리 구조

시스템은 source_type을 기준으로 처리 경로를 분기한다.

### PDF / HTML
설명형 문서 소스

- Parse 대상
- indexing 대상
- retrieval evidence 대상

### CSV
구조화된 마스터/매핑 소스

- Parse 비대상
- canonicalization 대상
- recommendation core 대상

### API
최신성 일정/링크 소스

- 현재는 reserved
- 후속 스프린트에서 canonical target schema로 병합

---

## 7. PDF / HTML 처리 구조

## 7.1 HTML Direct Path
HTML은 DOM / Main Content Parser 경로로 처리한다.

### 역할
- main content 추출
- heading / list / link 구조 유지
- FAQ / 공식 안내 페이지 정제

---

## 7.2 Primary PDF Parser
born-digital official PDF는 기본적으로 PDF 기본 parser 경로를 사용한다.

### 역할
- 텍스트 레이어 기반 본문 추출
- heading 구조 보존
- block 단위 중간 표현 생성

---

## 7.3 Table Assist
표 후보 페이지는 table assist 경로를 통해 보강한다.

### 역할
- 행/열 구조 보존
- 일정표 / 회차표 / 격자표 보강
- 표 block 단위 보존

---

## 7.4 OCR / Fallback
### OCR
저텍스트 / 스캔 페이지에만 page-level 적용

### Document-level Fallback
기본 parse + 보강 이후에도 구조 보존 실패가 반복되는 문서군에만 fallback 적용

---

## 7.5 Cleanup / Postprocess
- boilerplate 제거
- reading order 복원
- parse quality flag 생성

---

## 7.6 Parse 이후 산출물
PDF / HTML 경로의 최종 산출물은 아래와 같다.

- parse IR
- chunk
- metadata
- dense input
- sparse input(optional)

---

## 8. CSV 처리 구조

CSV는 recommendation core의 구조적 기반을 만드는 계층이다.

## 8.1 Dataset Type Registry
입력 CSV가 어떤 dataset type인지 식별한다.

예:
- cert_master
- cert_alias
- cert_domain_mapping
- cert_job_mapping
- roadmap_stage_master
- risk_stage_master

---

## 8.2 Schema Mapping
입력 컬럼명을 canonical field로 통일한다.

예:
- 자격증명 / qual_name / certificate_name → `cert_name`
- 기관 / issuer / 주관기관 → `issuer`

---

## 8.3 Canonicalization
값을 정규화한다.

예:
- alias 정리
- issuer 정규화
- cert_id 정규화
- domain / job 정규화
- risk stage id 정규화

---

## 8.4 Entity Builder
엔티티를 생성한다.

예:
- certificate
- domain_sub_label
- job_sub_label
- risk_stage
- roadmap_stage

---

## 8.5 Relation Builder
관계를 생성한다.

예:
- cert_to_domain
- cert_to_job
- cert_to_roadmap_stage
- risk_stage_to_domain
- risk_stage_to_roadmap_stage

---

## 8.6 Candidate Row Builder
추천에서 바로 사용할 수 있는 atomic recommendation record를 만든다.

핵심 row:
- `certificate_candidate_row`

이 row는 recommendation API의 가장 가까운 입력 자산이며, 구조적 추천의 기반이 된다.

---

## 9. Canonical Merge

서로 다른 source_type에서 온 데이터를 공통 조인 기준으로 맞추는 단계다.

### 목적
- 자격증 기준 통합
- alias 기준 통합
- taxonomy 기준 통합
- 버전 / 유효기간 기준 통합
- 추후 API 일정 데이터 병합 준비

### 핵심 정규화 항목
- `cert_id`
- `alias`
- `issuer`
- `job`
- `domain`
- `risk_stage`
- `roadmap_stage`
- `valid_from`
- `valid_to`
- `doc_version`

---

## 10. Chunk / Metadata / Embedding 구조

## 10.1 Chunk Builder
source_type에 따라 다른 방식으로 chunk를 만든다.

- PDF guide / FAQ: markdown-aware + heading propagation
- table docs: block chunking
- CSV/API: atomic record chunk

---

## 10.2 Metadata Tagging
각 chunk 또는 atomic record에는 최소한 아래 메타가 붙는다.

- `doc_id`
- `chunk_id`
- `source_type`
- `doc_type`
- `cert_id`
- `job_role_id`
- `domain_sub_label`
- `domain_top_label`
- `risk_stage_id`
- `roadmap_stage`
- `agency`
- `source_url`
- `section_path`
- `source_loc`
- `chunk_hash`
- `valid_from`
- `valid_to`
- `doc_version`

---

## 10.3 Embedding Layer
embedding 계층은 retrieval용 벡터 및 보조 텍스트를 만든다.

### 산출물
- `dense_vector`
- `text_for_sparse` (필요 시)
- `exact_terms`
- `emb_model_version`
- `emb_prompt_version`

### 원칙
- `text_for_sparse`는 반드시 항상 사용하는 기본값이 아니다.
- exact miss가 실제 문제로 재현될 때만 활성화한다.

---

## 11. Runtime Request Flow

## 11.1 추천 요청 흐름
1. 사용자가 프론트에서 입력을 제공한다.
2. 프론트가 recommendation API를 호출한다.
3. 백엔드는 risk stage를 확인하거나 입력 기준을 정리한다.
4. canonical relational store에서 candidate row를 조회한다.
5. 필요 시 retrieval layer에서 설명 근거를 검색한다.
6. recommendation_service가 추천 결과와 설명 근거를 조합한다.
7. 프론트가 결과를 렌더링한다.

---

## 11.2 로드맵 요청 흐름
1. 사용자가 추천 결과 또는 위험군 기준으로 로드맵을 요청한다.
2. 백엔드는 canonical relation을 조회한다.
3. roadmap_service가 단계형 결과를 생성한다.
4. 프론트가 단계 순서와 관련 자격증/도메인을 표시한다.

---

## 11.3 데이터 갱신 흐름
1. 운영자가 CSV 마스터/매핑 데이터를 교체한다.
2. canonicalization pipeline이 실행된다.
3. entity / relation / candidate row를 재생성한다.
4. index-ready 데이터와 retrieval 인덱스를 갱신한다.

---

## 12. 현재 MVP 활성 범위

현재 시스템에서 실제 활성화 기준은 아래와 같다.

### 활성화
- risk stage 기반 recommendation 진입
- certificate candidate row 기반 추천
- roadmap 제안
- PDF / HTML evidence retrieval
- CSV canonicalization
- parse / chunk / metadata / embedding 기본 파이프라인

### reserved
- 시험 일정 API
- 접수 일정 API
- 지원 링크 실연동
- reranker 활성화
- shared 공용 타입 계층
- full infra 배포 구조

---

## 13. 시스템 경계

이 문서는 시스템 구조만 정의하며, 아래 항목은 별도 문서에서 정의한다.

### PRD.md
- 해결할 문제
- 타깃 사용자
- 제품 범위 / 비범위

### FEATURE_SPEC.md
- 기능별 입력/출력/예외처리

### API_SPEC.md
- endpoint / request / response

### DATA_SCHEMA.md
- 실제 컬럼, 테이블, schema 구조

### RAG_PIPELINE.md
- retrieval 전략, fusion, sparse/dense 운영 기준

### EVALUATION_GUIDELINE.md
- metric, baseline, 채택/기각 기준

---

## 14. 디렉토리 매핑

시스템 구조는 다음 디렉토리와 대응된다.

- `frontend/` → 사용자 인터페이스
- `backend/app/` → API / 서비스 조정 계층
- `backend/rag/` → parse / retrieval 계층
- `backend/canonical/` → CSV canonicalization 계층
- `data/` → raw / canonical / index-ready 저장소
- `scripts/` → 배치 실행
- `experiments/` → 실험 / 로그 / 보고서

---

## 15. 핵심 아키텍처 결정

1. 추천의 구조적 기반과 설명 근거를 분리한다.
2. source_type에 따라 다른 처리 경로를 사용한다.
3. CSV는 Parse IR 대상이 아니다.
4. taxonomy 밖 자유 라벨 생성을 허용하지 않는다.
5. API 최신성 정보는 후속 병합 대상으로 둔다.
6. MVP에서는 구조 안정화가 우선이며, 고도화 기능은 reserved로 둔다.

---

## 16. 오픈 이슈

1. 위험군 2~4단계의 세부 의미와 판정 기준
2. roadmap stage의 최종 단계명과 단계 수
3. 일정 API 병합 시 canonical target schema 세부 구조
4. reranker 활성화 조건
5. sparse store 상시 사용 여부

---

## 17. 최종 요약

본 시스템은 아래 3개 계층의 결합으로 이해할 수 있다.

- **Canonical Recommendation Layer**
- **RAG Evidence Layer**
- **API Orchestration Layer**

즉, 구조적 추천은 canonicalization 계층이 담당하고, 설명 근거는 RAG 계층이 담당하며, 최종 사용자 응답은 backend application layer가 조립한다.

현재 MVP의 목표는 이 3개 계층을 먼저 안정적으로 연결하는 것이다.
