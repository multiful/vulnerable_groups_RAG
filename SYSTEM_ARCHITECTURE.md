# SYSTEM_ARCHITECTURE.md

> **파일명**: SYSTEM_ARCHITECTURE.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: 시스템 구성, 계층, 책임, 데이터 흐름 정의 문서  
> **문서 우선순위**: 3  
> **연관 문서**: README.md, CHANGE_CONTROL.md, PRD.md, FEATURE_SPEC.md, DATA_SCHEMA.md, DIRECTORY_SPEC.md  
> **참조 규칙**: 시스템 구조, 계층 책임, 데이터 흐름, 모듈 경계를 변경할 때 먼저 이 문서를 수정한다.

---

## 1. 문서 목적

이 문서는 시스템의 **구성 요소**, **계층별 책임**, **데이터 흐름**, **모듈 간 경계**를 정의한다.  
이 문서는 제품의 문제 정의나 사용자 가치가 아니라, 확정된 요구사항을 구현 가능한 시스템 구조로 변환하는 것을 목적으로 한다.

이 문서가 다루는 범위는 다음과 같다.

- 프론트엔드 / 백엔드 / RAG / canonicalization 계층 구조
- source_type 기반 처리 경로
- recommendation, roadmap, evidence retrieval 흐름
- 저장소 역할 분리
- 현재 활성화 범위와 reserved 범위

이 문서는 다음을 직접 정의하지 않는다.

- 제품 문제 정의와 사용자 가치
- 기능별 입력/출력/예외처리 상세
- API endpoint 상세
- DB 컬럼 단위 상세 정의
- 평가 지표와 실험 절차
- 프롬프트 세부 내용

위 항목은 각각 `PRD.md`, `FEATURE_SPEC.md`, `API_SPEC.md`, `DATA_SCHEMA.md`, `EVALUATION_GUIDELINE.md`, `PROMPT_DESIGN.md`에서 담당한다.

---

## 2. 시스템 설계 원칙

### 2.1 계층 분리 원칙
시스템은 아래 3개 축을 분리해서 설계한다.

1. **Recommendation Core**
   - 추천 후보와 로드맵 단계를 계산하는 구조적 기반

2. **Evidence Retrieval**
   - PDF / HTML 문서에서 설명 근거를 검색하는 계층

3. **Delivery Layer**
   - 프론트 요청을 받아 결과를 조합해 응답하는 계층

즉, 구조적 추천과 설명 근거 검색은 같은 계층에서 처리하지 않는다.

### 2.2 source_type 분리 원칙
데이터는 source_type에 따라 다른 처리 경로를 사용한다.

- PDF / HTML → Parse 및 indexing 대상
- CSV → structured no-parse canonicalization 대상
- API → 후속 스프린트에서 canonical target schema 병합 대상

### 2.3 taxonomy 고정 원칙
추천 결과의 정합성을 위해 자유 텍스트 라벨을 허용하지 않는다.

- `related_domains`는 도메인 taxonomy 세부 라벨만 사용
- `related_jobs`는 희망 직무 taxonomy 세부 직무만 사용

### 2.4 단계적 활성화 원칙
최종 구조를 먼저 고정하되, 모든 계층을 동시에 활성화하지 않는다.

- 일정 API
- reranker
- shared 공용 구조
- full infra

위 항목은 reserved 상태로 둘 수 있다.

---

## 3. 상위 구성 요소

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

## 5. Frontend 아키텍처

프론트엔드는 사용자 입력과 결과 표시를 담당하는 계층이다.  
프론트는 가능한 한 얇게 유지하며, 도메인 판단과 추천 계산은 백엔드에 둔다.

### 주요 책임
- 위험군 입력/진입 UX 제공
- 추천 결과 렌더링
- 로드맵 결과 렌더링
- 설명 근거 표시
- 추후 일정/링크 화면 제공

### 현재 활성 범위
- Home
- RiskAssessment
- Recommendation
- Roadmap

### reserved
- Schedule
- Admin

---

## 6. Backend Application Layer 아키텍처

백엔드 애플리케이션 계층은 전체 요청 흐름의 조정자다.  
프론트 요청을 받아 입력을 정리하고, recommendation core와 evidence retrieval 결과를 결합해 최종 응답을 만든다.

### 주요 책임
- API endpoint 제공
- request/response schema 검증
- 위험군 기준 반영
- recommendation orchestration
- roadmap 생성
- retrieval 결과 결합
- 응답 포맷 조립

### 핵심 서비스
- `risk_stage_service`
- `recommendation_service`
- `roadmap_service`
- `retrieval_service`
- `metadata_service`

### reserved
- `schedule_service`

---

## 7. RAG Layer 아키텍처

RAG 계층은 PDF / HTML 기반 공식 문서를 검색 가능한 상태로 변환하고, 이후 설명 근거를 검색하는 역할을 담당한다.

이 계층의 목적은 추천 계산이 아니라 **설명 근거 검색**이다.

### 7.1 입력 소스
- Official PDF
- Official HTML
- FAQ
- 공고문
- 공식 안내 페이지

### 7.2 처리 구조
#### HTML Direct Path
- DOM / Main Content Parser 경로
- main content / heading / list / link 추출

#### Primary PDF Parser
- born-digital PDF 기본 경로
- 본문 / heading / block 단위 추출

#### Table Assist
- 표 후보 페이지 보강
- 행/열 구조 보존

#### OCR / Fallback
- OCR: 저텍스트 / 스캔 페이지 page-level 처리
- Fallback: 기본 parse + 보강 실패 문서군에만 document-level 적용

#### Cleanup / Postprocess
- boilerplate 제거
- reading order 복원
- quality flag 생성

### 7.3 산출물
- parse IR
- chunk
- metadata
- dense input
- sparse input(optional)

---

## 8. CSV Canonicalization Layer 아키텍처

CSV는 Parse IR을 만들지 않고, 구조화된 추천 기반 자산으로 변환한다.

### 8.1 주요 책임
- dataset type 판별
- schema mapping
- canonicalization
- entity 생성
- relation 생성
- candidate row 생성
- validation report 생성

### 8.2 입력 예시
- cert_master
- cert_alias
- cert_domain_mapping
- cert_job_mapping
- roadmap_stage_master
- risk_stage_master

### 8.3 핵심 산출물
- canonical entities
- canonical relations
- recommendation candidate rows

### 8.4 처리 원칙
- CSV는 structured no-parse 경로를 따른다.
- 자유 텍스트 taxonomy 생성을 허용하지 않는다.
- recommendation core의 구조적 사실 기반을 만든다.

---

## 9. Storage Layer 아키텍처

저장 계층은 목적에 따라 분리한다.

### 9.1 Canonical Relational Store
구조화된 추천 기반 저장소

저장 대상 예:
- entities
- relations
- candidate rows
- risk stage / roadmap stage 기준 데이터

### 9.2 Vector Store
설명 근거 검색용 dense retrieval 저장소

저장 대상 예:
- FAQ chunk
- 안내문 chunk
- 공고문 chunk
- HTML 설명 chunk

### 9.3 Sparse / BM25 Store
exact match 보강용 선택 저장소

저장 대상 예:
- alias 기반 exact text
- 기관명 / 자격증명 / 직무명
- exact-sensitive 텍스트

현재는 optional이다.

---

## 10. Canonical Merge 구조

서로 다른 source_type에서 온 데이터를 공통 기준으로 맞추는 단계다.

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

## 11. Chunk / Metadata / Embedding 구조

### 11.1 Chunk Builder
source_type에 따라 다른 방식으로 chunk를 만든다.

- PDF guide / FAQ → markdown-aware + heading propagation
- table docs → block chunking
- CSV / API → atomic record chunk

### 11.2 Metadata Tagging
각 chunk 또는 atomic record에는 최소 아래 메타를 붙인다.

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

### 11.3 Embedding Layer
embedding 계층은 retrieval용 벡터 및 보조 텍스트를 만든다.

산출물:
- `dense_vector`
- `text_for_sparse` (필요 시)
- `exact_terms`
- `emb_model_version`
- `emb_prompt_version`

원칙:
- `text_for_sparse`는 항상 기본값이 아니다.
- exact miss가 실제 문제로 재현될 때만 활성화한다.

---

## 12. Runtime Request Flow

### 12.1 추천 요청 흐름
1. 사용자가 프론트에서 입력을 제공한다.
2. 프론트가 recommendation API를 호출한다.
3. 백엔드는 위험군 기준을 적용한다.
4. canonical relational store에서 candidate row를 조회한다.
5. 필요 시 retrieval layer에서 설명 근거를 검색한다.
6. recommendation service가 결과를 조합한다.
7. 프론트가 결과를 렌더링한다.

### 12.2 로드맵 요청 흐름
1. 사용자가 추천 결과 또는 위험군 기준으로 로드맵을 요청한다.
2. 백엔드는 canonical relation을 조회한다.
3. roadmap service가 단계형 결과를 생성한다.
4. 프론트가 단계 순서와 관련 자격증/도메인을 표시한다.

### 12.3 데이터 갱신 흐름
1. 운영자가 CSV 마스터/매핑 데이터를 교체한다.
2. canonicalization pipeline이 실행된다.
3. entity / relation / candidate row를 재생성한다.
4. index-ready 데이터와 retrieval 인덱스를 갱신한다.

---

## 13. 현재 활성 범위

### 활성화
- 위험군 기반 recommendation 진입
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

## 14. 시스템 경계

이 문서는 시스템 구조만 정의하며, 아래 항목은 별도 문서에서 정의한다.

### `PRD.md`
- 해결할 문제
- 타깃 사용자
- 제품 범위 / 비범위

### `FEATURE_SPEC.md`
- 기능별 입력 / 출력 / 예외처리

### `API_SPEC.md`
- endpoint / request / response

### `DATA_SCHEMA.md`
- 실제 컬럼, 테이블, schema 구조

### `RAG_PIPELINE.md`
- indexing / retrieval 세부 전략
- fusion / sparse / dense 운영 기준

### `EVALUATION_GUIDELINE.md`
- metric
- baseline
- 채택 / 기각 기준

---

## 15. 디렉토리 매핑

시스템 구조는 다음 디렉토리와 대응된다.

- `frontend/` → 사용자 인터페이스
- `backend/app/` → API / 서비스 조정 계층
- `backend/rag/` → parse / retrieval 계층
- `backend/canonical/` → CSV canonicalization 계층
- `data/` → raw / canonical / index-ready 저장소
- `scripts/` → 배치 실행
- `experiments/` → 실험 / 로그 / 보고서

---

## 16. 핵심 아키텍처 결정

1. 구조적 추천과 설명 근거 검색을 분리한다.
2. source_type에 따라 처리 경로를 분리한다.
3. CSV는 Parse IR 대상이 아니다.
4. taxonomy 밖 자유 라벨 생성을 허용하지 않는다.
5. API 최신성 정보는 후속 병합 대상으로 둔다.
6. MVP에서는 구조 안정화가 우선이며, 고도화 기능은 reserved로 둔다.

---

## 17. 오픈 이슈

1. 위험군 2~4단계의 세부 의미와 판정 기준
2. roadmap stage의 최종 단계명과 단계 수
3. 일정 API 병합 시 canonical target schema 세부 구조
4. reranker 활성화 조건
5. sparse store 상시 사용 여부

---

## 18. 최종 요약

본 시스템은 아래 3개 계층의 결합으로 이해할 수 있다.

- **Canonical Recommendation Layer**
- **RAG Evidence Layer**
- **API Orchestration Layer**

즉, 구조적 추천은 canonicalization 계층이 담당하고, 설명 근거는 RAG 계층이 담당하며, 최종 사용자 응답은 backend application layer가 조립한다.

현재 MVP의 목표는 이 3개 계층을 먼저 안정적으로 연결하는 것이다.
