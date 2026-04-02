# DATA_SCHEMA.md

> **파일명**: DATA_SCHEMA.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: 데이터 구조, 엔티티, 관계, 주요 필드 정의 문서  
> **문서 우선순위**: 5  
> **연관 문서**: PRD.md, SYSTEM_ARCHITECTURE.md, FEATURE_SPEC.md, API_SPEC.md, RAG_PIPELINE.md  
> **참조 규칙**: 데이터 구조, canonical schema, 주요 필드, 관계, 제약조건을 변경할 때 먼저 이 문서를 수정한다.

---

## 1. 문서 목적

이 문서는 시스템의 **데이터 구조 기준선**을 정의한다.  
주요 엔티티, 관계, recommendation candidate row, indexing용 메타데이터 구조를 문서화하여, 기능 구현과 API 설계가 같은 데이터 기준을 사용하도록 하는 것이 목적이다.

이 문서는 다음을 정의한다.

- 핵심 엔티티
- 핵심 관계
- canonical row 구조
- recommendation candidate row 구조
- indexing metadata 구조
- 제약 조건
- reserved 필드

이 문서는 다음을 직접 정의하지 않는다.

- 제품 문제 정의와 기능 우선순위
- 시스템 계층 구조
- API endpoint 상세
- retrieval 전략 및 reranker 정책
- 평가 기준

위 항목은 각각 `PRD.md`, `SYSTEM_ARCHITECTURE.md`, `API_SPEC.md`, `RAG_PIPELINE.md`, `EVALUATION_GUIDELINE.md`에서 담당한다.

---

## 2. 데이터 설계 원칙

### 2.1 source_type 분리
데이터는 source_type에 따라 다른 구조로 다뤄진다.

- PDF / HTML → 문서형 지식 데이터
- CSV → structured no-parse canonical data
- API → 후속 최신성 데이터

### 2.2 canonical 중심 설계
추천의 구조적 기반은 canonical data를 중심으로 설계한다.

- 원본 CSV를 그대로 recommendation 입력으로 사용하지 않는다.
- canonical entity / relation / candidate row를 생성해 사용한다.

### 2.3 taxonomy 제한
다음 필드는 자유 텍스트를 허용하지 않는다.

- `related_domains`
- `related_jobs`

### 2.4 reserved 필드 허용
현재 스프린트 범위 밖이지만 추후 API 병합을 위해 아래 종류의 필드는 reserved 상태로 유지할 수 있다.

- `exam_date`
- `apply_start_date`
- `apply_end_date`
- `support_url`
- `valid_from`
- `valid_to`

---

## 3. 핵심 엔티티

## 3.1 RiskStage

위험군 단계 엔티티

### 필드
- `risk_stage_id`
- `risk_stage_name`
- `risk_stage_order`
- `description`
- `is_active`

### 제약
- `risk_stage_id`는 유일해야 한다.
- 현재 허용 범위는 1단계 ~ 5단계다.
- `risk_stage_order`는 1~5의 정수다.

---

## 3.2 RoadmapStage

로드맵 단계 엔티티

### 필드
- `roadmap_stage_id`
- `roadmap_stage_name`
- `stage_order`
- `description`
- `is_active`

### 제약
- `roadmap_stage_id`는 유일해야 한다.
- 단계 순서는 정수형으로 관리한다.

---

## 3.3 Certificate

자격증 엔티티

### 필드
- `cert_id`
- `cert_name`
- `issuer`
- `canonical_name`
- `normalized_key`
- `aliases`
- `is_active`

### 제약
- `cert_id`는 유일해야 한다.
- `canonical_name`은 추천 표시에 사용할 대표 이름이다.
- `normalized_key`는 중복 제거와 canonicalization 기준에 사용한다.

---

## 3.4 DomainSubLabel

도메인 세부 라벨 엔티티

### 필드
- `domain_sub_label_id`
- `domain_sub_label_name`
- `domain_top_label_name`
- `normalized_key`
- `is_active`

### 제약
- 허용 값은 domain taxonomy 기준만 사용한다.
- 세부 라벨은 상위 라벨에 매핑 가능해야 한다.

---

## 3.5 JobSubLabel

직무 세부 라벨 엔티티

### 필드
- `job_role_id`
- `job_role_name`
- `job_top_group_name`
- `normalized_key`
- `is_active`

### 제약
- 허용 값은 job taxonomy 기준만 사용한다.
- 자유 텍스트 직무명을 저장하지 않는다.

---

## 3.6 SourceDocument

문서형 지식 엔티티(PDF / HTML)

### 필드
- `doc_id`
- `source_type`
- `doc_type`
- `title`
- `source_url`
- `agency`
- `doc_version`
- `valid_from`
- `valid_to`
- `freshness_level`
- `exact_sensitivity`

### 제약
- `source_type`은 `pdf`, `html`, `csv`, `api` 중 하나다.
- 현재 문서형 지식 엔티티는 주로 `pdf`, `html`에 사용한다.

---

## 4. 핵심 관계

## 4.1 cert_to_domain

자격증과 도메인 세부 라벨의 관계

### 필드
- `relation_id`
- `cert_id`
- `domain_sub_label_id`
- `weight`
- `source_id`
- `is_active`

### 제약
- 하나의 자격증은 여러 도메인 세부 라벨과 연결될 수 있다.
- 최소 1개의 primary domain이 정해질 수 있어야 한다.

---

## 4.2 cert_to_job

자격증과 직무 세부 라벨의 관계

### 필드
- `relation_id`
- `cert_id`
- `job_role_id`
- `weight`
- `source_id`
- `is_active`

### 제약
- 허용된 희망 직무 taxonomy 범위 안의 값만 사용한다.

---

## 4.3 cert_to_roadmap_stage

자격증과 로드맵 단계의 관계

### 필드
- `relation_id`
- `cert_id`
- `roadmap_stage_id`
- `weight`
- `source_id`
- `is_active`

---

## 4.4 risk_stage_to_domain

위험군과 도메인의 관계

### 필드
- `relation_id`
- `risk_stage_id`
- `domain_sub_label_id`
- `weight`
- `source_id`
- `is_active`

---

## 4.5 risk_stage_to_roadmap_stage

위험군과 로드맵 단계의 관계

### 필드
- `relation_id`
- `risk_stage_id`
- `roadmap_stage_id`
- `weight`
- `source_id`
- `is_active`

---

## 5. canonical entity table 구조

canonical entity table은 정규화된 엔티티를 저장하는 공통 테이블이다.

### 공통 필드
- `entity_type`
- `entity_id`
- `canonical_name`
- `normalized_key`
- `aliases`
- `source_id`
- `source_row_no`
- `canonical_fields_json`
- `quality_flags`
- `updated_at`
- `content_hash`

### `entity_type` 허용 값 예시
- `certificate`
- `domain_sub_label`
- `job_sub_label`
- `risk_stage`
- `roadmap_stage`

### 원칙
- 원본 CSV 컬럼을 그대로 저장하는 것이 아니라 정규화된 대표 필드를 저장한다.
- `canonical_fields_json`에는 타입별 추가 속성을 담을 수 있다.

---

## 6. canonical relation table 구조

canonical relation table은 정규화된 관계를 저장하는 공통 테이블이다.

### 공통 필드
- `relation_type`
- `src_entity_type`
- `src_entity_id`
- `dst_entity_type`
- `dst_entity_id`
- `weight`
- `source_id`
- `source_row_no`
- `quality_flags`
- `updated_at`

### `relation_type` 허용 값 예시
- `cert_to_domain`
- `cert_to_job`
- `cert_to_roadmap_stage`
- `risk_stage_to_domain`
- `risk_stage_to_roadmap_stage`

---

## 7. recommendation candidate row 구조

이 row는 recommendation core의 기본 검색 단위다.

## 7.1 certificate_candidate_row

### 필드
- `row_type`
- `candidate_id`
- `cert_id`
- `cert_name`
- `aliases`
- `issuer`
- `primary_domain`
- `related_domains`
- `related_jobs`
- `recommended_risk_stages`
- `roadmap_stages`
- `text_for_dense`
- `text_for_sparse`
- `valid_from`
- `valid_to`
- `source_ids`
- `quality_flags`
- `updated_at`
- `content_hash`

### 필드 설명
#### `candidate_id`
추천 row 고유 식별자

#### `primary_domain`
주 도메인 1개  
도메인 taxonomy 세부 라벨만 허용

#### `related_domains`
관련 도메인 배열  
taxonomy 밖 값 금지

#### `related_jobs`
관련 직무 배열  
taxonomy 밖 값 금지

#### `recommended_risk_stages`
이 candidate가 특히 연결되는 위험군 단계 배열

#### `roadmap_stages`
추천 결과와 연결 가능한 로드맵 단계 배열

#### `text_for_dense`
추천 의미 요약용 텍스트

#### `text_for_sparse`
exact match 보강용 텍스트  
현재는 optional이며 필요 시 활성화

### 제약
- `cert_id`, `cert_name`, `primary_domain`은 필수다.
- `related_domains`는 최소 1개 이상이어야 한다.
- `related_jobs`는 비어 있을 수 있으나, 추천 품질상 가능한 한 채운다.
- reserved 일정 필드는 현재 row 기본 필드에 포함하지 않는다.

---

## 8. 문서형 chunk 구조

PDF / HTML 지식 검색용 chunk 구조

### 공통 필드
- `doc_id`
- `chunk_id`
- `source_type`
- `doc_type`
- `text`
- `section_path`
- `source_loc`
- `chunk_hash`
- `valid_from`
- `valid_to`
- `doc_version`

### optional 메타 필드
- `cert_id`
- `job_role_id`
- `domain_sub_label`
- `domain_top_label`
- `risk_stage_id`
- `roadmap_stage`
- `agency`

### 원칙
- 문서형 chunk는 설명 근거 검색용이다.
- recommendation candidate row와 직접 동일 구조로 취급하지 않는다.

---

## 9. parse quality / provenance 구조

문서형 데이터에는 parse 품질과 provenance 메타를 유지한다.

### 예시 필드
- `has_text_layer`
- `ocr_applied_pages`
- `table_assisted_pages`
- `reading_order_rebuilt`
- `fallback_used`
- `parse_quality_flags`

### 목적
- parse 결과 품질 점검
- provenance 유지
- retrieval 결과 해석 보조

---

## 10. validation 구조

canonicalization 및 candidate 생성 과정의 품질 검증 결과를 저장한다.

### validation report 공통 필드
- `dataset_type`
- `check_name`
- `severity`
- `row_count`
- `sample_rows`
- `status`
- `generated_at`

### 주요 검증 항목
- PK 누락
- FK 연결 실패
- taxonomy 밖 값
- alias 충돌
- 날짜 역전
- invalid URL
- required field 누락
- 중복 candidate 생성

---

## 11. reserved 일정/링크 필드

현재는 후속 스프린트 범위지만, 추후 API 병합을 위해 아래 필드를 reserved로 유지할 수 있다.

### 일정 관련
- `exam_date`
- `exam_round`
- `apply_start_date`
- `apply_end_date`

### 링크 관련
- `support_url`
- `official_url`
- `apply_url`

### 원칙
- 현재 MVP 단계에서는 이 필드를 null 또는 비활성 상태로 둘 수 있다.
- 필드명을 미리 고정하면 후속 병합이 쉬워진다.

---

## 12. 주요 키 구조

### 식별자 예시
- `risk_stage_id`
- `roadmap_stage_id`
- `cert_id`
- `domain_sub_label_id`
- `job_role_id`
- `doc_id`
- `chunk_id`
- `candidate_id`

### 원칙
- 식별자는 안정적이고 재생성 가능해야 한다.
- row 생성 시 임시 표시용 이름보다 ID를 우선한다.

---

## 13. 데이터 제약 요약

1. CSV는 Parse IR을 만들지 않는다.
2. taxonomy 밖 라벨을 저장하지 않는다.
3. recommendation candidate row는 canonical data를 기반으로 생성한다.
4. 문서형 chunk와 recommendation candidate row는 같은 구조로 다루지 않는다.
5. 일정/링크 필드는 reserved 상태를 허용한다.
6. `최종 수정일`이 오래된 문서 기준으로 schema를 임의 변경하지 않는다.

---

## 14. 후속 문서 연결

- 기능별 사용 위치 → `FEATURE_SPEC.md`
- 시스템 흐름 위치 → `SYSTEM_ARCHITECTURE.md`
- API 계약 → `API_SPEC.md`
- retrieval / indexing 세부 → `RAG_PIPELINE.md`

---

## 15. 최종 요약

이 문서는 시스템이 사용하는 핵심 데이터 구조를 정의한다.  
현재 데이터 구조의 중심은 아래 두 가지다.

1. **canonical entity / relation**
2. **recommendation candidate row**

즉, 이 문서는 추천과 검색이 같은 기준 데이터 위에서 동작하도록 만드는 데이터 기준선이다.
