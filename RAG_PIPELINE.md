# RAG_PIPELINE.md

> **파일명**: RAG_PIPELINE.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: RAG 인덱싱 및 리트리벌 파이프라인 정의 문서  
> **문서 우선순위**: 8  
> **연관 문서**: SYSTEM_ARCHITECTURE.md, DATA_SCHEMA.md, API_SPEC.md, PROMPT_DESIGN.md, EVALUATION_GUIDELINE.md  
> **참조 규칙**: Parse, Chunking, Metadata, Embedding, Retrieval, Fusion, Sparse/Dense 사용 기준을 변경할 때 먼저 이 문서를 수정한다.

---

## 1. 문서 목적

이 문서는 시스템의 **RAG 파이프라인**을 정의한다.  
여기서 RAG 파이프라인은 PDF / HTML 기반 공식 문서를 검색 가능한 상태로 변환하고, 추천 결과에 설명 근거를 결합하기 위해 검색하는 전체 흐름을 의미한다.

이 문서는 다음을 정의한다.

- source_type 기준 RAG 적용 범위
- Parse → Chunk → Metadata → Embedding → Store 흐름
- Retrieval 계층의 역할
- Dense / Sparse / Fusion의 사용 기준
- 현재 활성 범위와 reserved 범위
- 운영 및 품질 점검 포인트

이 문서는 다음을 직접 정의하지 않는다.

- 제품 문제 정의와 사용자 가치
- 기능별 입력/출력/예외처리
- API endpoint 계약 상세
- canonical entity / relation 구조
- 프롬프트 문구 자체
- 평가 지표의 최종 채택 기준

위 항목은 각각 `PRD.md`, `FEATURE_SPEC.md`, `API_SPEC.md`, `DATA_SCHEMA.md`, `PROMPT_DESIGN.md`, `EVALUATION_GUIDELINE.md`에서 담당한다.

---

## 2. RAG의 역할

본 시스템에서 RAG는 **추천 자체를 계산하는 엔진**이 아니다.  
RAG의 역할은 아래로 한정한다.

1. PDF / HTML 문서 기반 설명 근거 검색
2. 추천 결과에 대한 FAQ / 안내문 / 설명 텍스트 보강
3. 자격증, 직무, 도메인, 로드맵과 관련된 공식 문서 근거 제공

즉, 구조적 추천은 canonical data가 담당하고, RAG는 그 추천을 설명하는 **evidence layer** 역할을 한다.

---

## 3. 적용 범위

### 3.1 RAG 적용 대상
- Official PDF
- Official HTML
- FAQ
- 공고문
- 공식 안내 페이지
- 시험안내 브로슈어
- 문서형 설명 자료

### 3.2 RAG 비적용 대상
- CSV 원본
- canonical entity table
- canonical relation table
- recommendation candidate row
- 위험군 stage master
- roadmap stage master

CSV 계열은 RAG 인덱싱 대상이 아니라 structured no-parse canonicalization 대상이다.

---

## 4. 파이프라인 상위 구조

```text
[Raw Knowledge Sources]
├─ Official PDF
└─ Official HTML

        ↓

[Source Routing & Profiling]
- source_type
- doc_type
- freshness_level
- exact_sensitivity
- layout signals
  - text_density
  - image_ratio
  - table_count
  - multi_column
  - scan_page_ratio

        ↓

[Parse Layer]
- HTML Direct Path
- Primary PDF Parser
- Table Assist
- OCR(page-level)
- Fallback(document-level)
- Boilerplate Removal
- Reading Order Fix

        ↓

[Chunk Layer]
- markdown-aware chunking
- block chunking
- heading propagation
- atomic chunk rules

        ↓

[Metadata Layer]
- doc_id
- chunk_id
- source_type
- doc_type
- cert_id (optional)
- domain/job/risk metadata (optional)
- section_path
- source_loc
- valid_from / valid_to / doc_version

        ↓

[Embedding Layer]
- dense vector
- exact terms
- text_for_sparse(optional)

        ↓

[Index Store Layer]
- Vector Store
- Sparse/BM25 Store(optional)

        ↓

[Retrieval Layer]
- Dense Retriever
- Sparse Retriever(optional)
- Fusion
- Filters
- Reranker(optional)

        ↓

[Evidence Output]
- evidence snippets
- provenance metadata
```

---

## 5. Source Routing & Profiling

RAG 파이프라인은 수집 직후 모든 문서를 동일하게 처리하지 않는다.  
먼저 source profiling을 통해 처리 경로를 결정한다.

### 기본 신호
- `source_type`
- `doc_type`
- `freshness_level`
- `exact_sensitivity`

### layout signals
- `text_density`
- `image_ratio`
- `table_count`
- `multi_column`
- `scan_page_ratio`

### 목적
- HTML direct path 여부 결정
- PDF 기본 경로 여부 결정
- table assist 필요 여부 결정
- OCR 대상 페이지 결정
- fallback 필요 문서군 판정

---

## 6. Parse Layer

### 6.1 HTML Direct Path
HTML은 DOM / Main Content Parser 경로로 처리한다.

#### 역할
- main content 추출
- heading / list / link 유지
- FAQ / 공식 안내 구조 보존

### 6.2 Primary PDF Parser
born-digital official PDF의 기본 경로다.

#### 역할
- 텍스트 레이어 기반 본문 추출
- heading 구조 보존
- block 단위 중간 표현 생성

#### 원칙
- 가능한 한 기본 경로로 유지한다.
- 문서 전체를 고비용 fallback으로 바로 보내지 않는다.

### 6.3 Table Assist
표 후보 페이지 보강 경로다.

#### 역할
- 일정표 / 격자표 / 회차표 구조 보존
- 행/열 관계 유지
- 표 block 단위 추출

#### 적용 기준
- `table_count`가 높은 페이지
- 표 문서로 판정된 페이지
- 행/열 구조 보존 필요 페이지

### 6.4 OCR
저텍스트 / 스캔 페이지 예외 처리 경로다.

#### 역할
- page-level 텍스트 복원
- 스캔 페이지 보강

#### 원칙
- 문서 전체 기본 경로가 아니라 페이지 단위 예외 처리다.
- born-digital PDF 전체에 OCR을 적용하지 않는다.

### 6.5 Document-level Fallback
기본 parse + 보강 이후에도 구조 보존 실패가 반복될 때만 사용하는 문서 단위 fallback이다.

#### 역할
- 복잡한 표/다단/순서 오류 문서군 재처리

#### 원칙
- 전체 문서 기본 경로로 사용하지 않는다.
- 실패 문서군에만 제한 적용한다.

### 6.6 Parse Cleanup
parse 이후 후처리를 수행한다.

#### 주요 처리
- boilerplate 제거
- reading order 복원
- parse quality flag 생성

#### 산출물
- parse IR
- parse_quality_flags
- optional provenance metadata

---

## 7. Chunk Layer

Chunk는 retrieval의 기본 검색 단위다.  
문서 유형별로 다른 chunking 규칙을 사용한다.

### 7.1 Markdown-aware Chunking
대상:
- guide
- FAQ
- 설명형 문서

규칙:
- heading propagation 유지
- 문단 의미 단위 우선
- 과도한 길이 확장 금지

### 7.2 Block Chunking
대상:
- 표 중심 문서
- block 분리가 중요한 문서

규칙:
- block boundary 유지
- 표/리스트/단락을 섞지 않는다

### 7.3 Parent-Child
현재는 선택 사항이다.  
기본 MVP에서는 필수 활성화 대상이 아니다.

---

## 8. Metadata Layer

각 chunk에는 retrieval과 provenance를 위해 메타데이터를 부여한다.

### 최소 메타 필드
- `doc_id`
- `chunk_id`
- `source_type`
- `doc_type`
- `section_path`
- `source_loc`
- `chunk_hash`
- `valid_from`
- `valid_to`
- `doc_version`

### 선택 메타 필드
- `cert_id`
- `job_role_id`
- `domain_sub_label`
- `domain_top_label`
- `risk_stage_id`
- `roadmap_stage`
- `agency`

### 원칙
- recommendation candidate row와 같은 구조를 강제하지 않는다.
- 문서 provenance와 filter 가능성을 우선한다.

---

## 9. Embedding Layer

### 9.1 Dense Vector
기본 검색 수단이다.

#### 역할
- 의미 기반 검색
- FAQ / 설명 문서 검색
- 추천 결과에 대한 근거 검색

#### 산출물
- `dense_vector`
- `emb_model_version`
- `emb_prompt_version`

### 9.2 Exact Terms
exact match에 민감한 용어를 보조 필드로 유지할 수 있다.

예:
- 자격증명
- 기관명
- 도메인명
- 직무명
- 회차 표현
- 고정 용어

### 9.3 text_for_sparse
선택적 sparse 입력 텍스트다.

#### 원칙
- 항상 기본값으로 사용하지 않는다.
- exact miss가 실제로 재현될 때만 활성화한다.
- 활성화 시 BM25 / sparse store 입력으로 사용한다.

---

## 10. Index Store Layer

### 10.1 Vector Store
dense retrieval용 저장소

저장 대상 예:
- chunk text
- dense vector
- metadata

### 10.2 Sparse / BM25 Store
exact retrieval 보강용 선택 저장소

저장 대상 예:
- sparse text
- exact-sensitive terms
- metadata

#### 원칙
- optional이다.
- 초기 MVP에서는 dense 중심 운영 가능하다.

---

## 11. Retrieval Layer

### 11.1 Dense Retriever
기본 검색기다.

#### 역할
- 의미 기반 evidence 검색
- 추천 이유 보강용 snippet 검색

### 11.2 Sparse Retriever
선택적 검색기다.

#### 역할
- alias
- 기관명
- 자격증명
- exact 용어 보강

### 11.3 Fusion
dense / sparse 결과를 결합한다.

#### 현재 원칙
- sparse가 비활성 상태면 dense 단독 운영 가능
- fusion 방식의 세부 튜닝은 후속 최적화 범위로 둔다

### 11.4 Filters
메타데이터 기반 검색 범위를 제한한다.

예:
- `source_type`
- `doc_type`
- `cert_id`
- `agency`
- `valid_from / valid_to`

### 11.5 Reranker
현재는 reserved 가능하다.

#### 역할
- 후보 정렬 개선
- 근거 우선순위 재조정

#### 원칙
- MVP 필수 기능은 아니다.

---

## 12. Evidence Output 구조

retrieval 결과는 evidence bundle 형태로 후단에 전달한다.

### 최소 필드
- `doc_id`
- `chunk_id`
- `source_type`
- `snippet`
- `section_path`
- `source_url`

### 선택 필드
- `score`
- `agency`
- `valid_from`
- `valid_to`
- `doc_version`

---

## 13. Runtime 흐름

### 13.1 Evidence Retrieval 요청 흐름
1. 백엔드 서비스가 `cert_id` 및 context를 전달한다.
2. retrieval 계층이 filter 조건을 구성한다.
3. dense retriever를 기본으로 검색한다.
4. sparse가 활성화되어 있으면 결합한다.
5. 필요 시 reranker를 적용한다.
6. evidence snippet과 provenance를 반환한다.

### 13.2 Recommendation과의 연결
- canonical recommendation 결과가 먼저 생성된다.
- 이후 RAG가 explanation/evidence를 보강한다.
- 구조적 추천과 evidence는 별도 계층에서 만들어진다.

---

## 14. 현재 활성 범위

### 활성화
- HTML direct path
- primary PDF parser
- table assist
- OCR page-level 예외 처리
- chunk builder
- metadata tagging
- dense embedding
- vector store
- dense retrieval
- optional filter 사용

### reserved
- sparse/BM25 상시 사용
- text_for_sparse 상시 사용
- reranker
- parent-child 고도화
- 일정/링크 문서 retrieval

---

## 15. 운영 원칙

1. born-digital PDF 전체에 OCR을 기본 적용하지 않는다.
2. CSV는 RAG Parse 대상이 아니다.
3. retrieval 결과가 0건이어도 추천 결과 자체는 실패로 간주하지 않는다.
4. exact miss가 문제로 재현되기 전까지 sparse를 강제하지 않는다.
5. reserved 기능은 문서 갱신 후 활성화한다.

---

## 16. 문서 경계

이 문서는 RAG 파이프라인만 정의하며 아래는 별도 문서에서 정의한다.

### `SYSTEM_ARCHITECTURE.md`
- 전체 계층 구조
- API orchestration
- frontend/backend 책임

### `DATA_SCHEMA.md`
- entity / relation / candidate 구조
- metadata 필드 기준

### `API_SPEC.md`
- evidence endpoint 계약

### `PROMPT_DESIGN.md`
- evidence summary prompt
- final response composer prompt

### `EVALUATION_GUIDELINE.md`
- parse / retrieval / chunk 품질 평가 기준

---

## 17. 최종 요약

본 시스템에서 RAG는 추천 엔진이 아니라 **설명 근거 검색 계층**이다.  
현재 파이프라인의 중심은 아래 두 가지다.

1. **문서형 소스를 검색 가능한 구조로 안정적으로 변환**
2. **추천 결과에 근거 snippet을 결합할 수 있도록 retrieval 제공**

즉, 현재 단계의 RAG는 dense 중심 evidence retrieval 구조를 먼저 안정화하는 것이 목표다.
