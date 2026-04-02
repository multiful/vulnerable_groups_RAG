# 청년 위험군 맞춤형 자격증·로드맵 추천 시스템

청년 위험군 분류 결과를 바탕으로 관련 자격증·직무·도메인 후보를 추천하고, 단계에 맞는 로드맵을 제안하며, 이후 시험 일정·접수 일정·지원 링크까지 연결하는 AI 기반 추천 시스템입니다.

현재는 **지식 파이프라인과 추천 기반 데이터 구조를 먼저 안정화하는 단계**이며, 우선순위는 다음과 같습니다.

1. PDF / HTML / CSV 소스 구조 정리  
2. CSV canonicalization 및 entity / relation 구축  
3. RAG 파이프라인 기반 추천용 인덱스 설계  
4. 추후 일정 API 연동을 통한 시험일정/접수일정/링크 연결

---

## 1. 프로젝트 개요

이 프로젝트는 단순 자격증 검색 서비스가 아니라, **청년 위험군 단계(1단계 ~ 5단계)** 와 **전공/직무/도메인 연관성**을 함께 고려하여 다음을 수행하는 시스템을 목표로 합니다.

- 사용자 상태를 위험군 단계 구조로 관리
- 관련 자격증 / 직무 / 도메인 후보 추천
- 위험 단계에 맞는 로드맵 제안
- 추후 시험 일정 / 접수 일정 / 지원 링크 연결

### 위험군 단계 구조
- **1단계**: 취업 안정권
- **5단계**: 취업을 하고 싶어도 하기 어려운 가장 높은 위험군
- **2~4단계**: 단계형 위험군 체계로 관리하며, 세부 의미 정의는 후속 문서에서 확정

---

## 2. 해결하려는 문제

기존 자격증 추천 서비스는 다음과 같은 한계를 가집니다.

- 사용자의 취업 위험 수준을 반영하지 못함
- 자격증을 단일 키워드 검색 수준에서만 추천함
- 직무 / 도메인 / 자격증 / 로드맵의 관계가 분리되어 있음
- 일정 / 접수 / 공식 링크 정보가 분산되어 있음
- PDF, HTML, CSV, API 등 서로 다른 소스가 통합적으로 관리되지 않음

본 프로젝트는 이 문제를 해결하기 위해 다음 구조를 사용합니다.

- **PDF / HTML**: 설명·가이드·FAQ·공고형 지식 소스
- **CSV**: 추천과 연결에 필요한 구조화 데이터 소스
- **API**: 추후 일정·링크 갱신용 소스
- **RAG + Canonical Store**: 검색과 추천 모두를 위한 통합 기반

---

## 3. 핵심 기능 요약

### 3.1 위험군 기반 추천
- 위험군 단계별로 적합한 자격증 / 직무 / 도메인 후보를 제시
- 동일 자격증이라도 사용자 상태에 따라 추천 맥락을 다르게 구성

### 3.2 자격증-직무-도메인 연결
- 자격증을 단독 객체로 보지 않고 관련 직무, 관련 도메인과 함께 추천
- `related_domains`는 도메인 taxonomy의 **세부 라벨**만 사용
- `related_jobs`는 희망 직무 taxonomy의 **세부 직무**만 사용

### 3.3 로드맵 제안
- 위험군 단계와 자격증/도메인 관계를 바탕으로 단계형 로드맵 제안
- 로드맵 단계는 별도 master 데이터 기준으로 관리

### 3.4 지식 검색 / 설명 근거 제공
- PDF / HTML 문서를 구조 보존 기반으로 인덱싱
- FAQ, 시험안내, 공식 안내문 등에서 설명 근거를 검색 가능하게 구성

### 3.5 일정 / 링크 연결 (후속 스프린트)
- 시험 일정
- 접수 일정
- 지원 링크
- 공공/기관 API 기반 최신화

---

## 4. 현재 개발 범위 / 제외 범위

## 현재 개발 범위
- 데이터 소스 분류 및 source routing 설계
- PDF / HTML Parse 구조 설계
- CSV structured no-parse 경로 설계
- canonical entity / relation 모델 설계
- retriever용 candidate row 설계
- RAG indexing 구조 설계
- 루트 문서 체계 정리

## 현재 제외 범위
- 일정 API 실연동
- 시험일정 / 접수일정 실데이터 연결
- reranker 학습
- hybrid 가중치 최적화
- generation prompt 고도화
- 위험군 2~4단계 세부 의미 확정

---

## 5. 시스템 상위 아키텍처 요약

```text
[Raw Knowledge Sources]
├─ Official PDF / HTML
├─ Structured CSV
└─ External API (시험일정/접수일정/링크)   ※ 후속 스프린트

         ↓

[Source Routing & Profiling]
- source_type
- doc_type
- freshness_level
- exact_sensitivity
- layout signals(text_density, image_ratio, table_count, multi_column, scan_page_ratio)

         ↓

┌──────────────────────── PDF / HTML Lane ────────────────────────┐
│ [HTML Direct Path: DOM / Main Content Parser]                   │
│ [Primary Parser: PyMuPDF4LLM]                                    │
│ [Table Parser: pdfplumber]                                       │
│ [Fallback: OCR(page-level) / Docling(document-level)]            │
│ [Boilerplate Removal + Reading Order Fix]                        │
└──────────────────────────────────────────────────────────────────┘

┌───────────────────────── CSV / API Lane ────────────────────────┐
│ [Dataset Type Registry]                                          │
│ [Schema Mapping]                                                 │
│ [Canonicalization]                                               │
│ [Entity Builder]                                                 │
│ [Relation Builder]                                               │
│ [Atomic Record Doc Builder]                                      │
└──────────────────────────────────────────────────────────────────┘

         ↓

[Canonical Merge]
         ↓
[Chunk Builder]
         ↓
[Metadata Tagging]
         ↓
[Embedding Layer]
         ↓
[Index Store Layer]
├─ Canonical Relational Store
├─ Vector Store
└─ Sparse / BM25 Store (optional)
>>>>>>> Stashed changes
