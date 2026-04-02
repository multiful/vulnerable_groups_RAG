# FEATURE_SPEC.md

> **파일명**: FEATURE_SPEC.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: 기능별 입력, 출력, 예외처리, 상태 정의 문서  
> **문서 우선순위**: 4  
> **연관 문서**: PRD.md, SYSTEM_ARCHITECTURE.md, API_SPEC.md, DATA_SCHEMA.md  
> **참조 규칙**: 기능을 추가, 제거, 변경하거나 화면/API 동작을 바꿀 때 먼저 이 문서를 수정한다.

---

## 1. 문서 목적

이 문서는 시스템이 제공하는 기능을 **사용자 기능 단위**로 정의한다.  
각 기능에 대해 아래 항목을 기준으로 명세한다.

- 기능 목적
- 입력
- 출력
- 처리 규칙
- 예외 상황
- 현재 상태(활성 / reserved)

이 문서는 기능 정의 문서이며, 아래 항목은 직접 다루지 않는다.

- 제품 문제 정의와 사용자 가치
- 시스템 계층 구조와 모듈 책임
- DB 컬럼 단위 구조
- API endpoint 상세 형식
- retrieval 파이프라인 세부 전략

위 항목은 각각 `PRD.md`, `SYSTEM_ARCHITECTURE.md`, `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`에서 담당한다.

---

## 2. 기능 분류

현재 기능은 아래 6개 그룹으로 나눈다.

1. 사용자 입력 및 위험군 진입
2. 추천 결과 생성
3. 로드맵 생성
4. 설명 근거 조회
5. 관리자/배치 갱신
6. 후속 일정 기능(reserved)

---

## 3. 기능 목록 요약

| 기능 ID | 기능명 | 현재 상태 | 주 사용자 |
|---|---|---:|---|
| F-01 | 위험군 기반 추천 진입 | 활성 | 사용자 |
| F-02 | 관심 직무/도메인 기반 추천 요청 | 활성 | 사용자 |
| F-03 | 자격증 후보 결과 조회 | 활성 | 사용자 |
| F-04 | 추천 이유/설명 근거 조회 | 활성 | 사용자 |
| F-05 | 위험군 맞춤 로드맵 조회 | 활성 | 사용자 |
| F-06 | CSV canonicalization 실행 | 활성 | 운영자/배치 |
| F-07 | entity / relation / candidate 재생성 | 활성 | 운영자/배치 |
| F-08 | 시험 일정 조회 | reserved | 사용자 |
| F-09 | 접수 일정 / 링크 조회 | reserved | 사용자 |
| F-10 | 관리자 점검 화면 | reserved | 운영자 |

---

## 4. 기능 상세

## F-01. 위험군 기반 추천 진입

### 목적
사용자의 현재 상태를 recommendation 흐름에 연결할 수 있도록 위험군 단계 기준 입력을 받는다.

### 입력
- 위험군 단계 입력값 또는 위험군 판정에 필요한 최소 입력
- 선택 입력: 관심 직무, 관심 도메인, 자격증 탐색 의도

### 출력
- 내부 추천 요청에 사용할 `risk_stage_id`
- recommendation request context

### 처리 규칙
- 위험군은 1단계 ~ 5단계 구조를 따른다.
- 2~4단계의 세부 의미가 확정되기 전까지는 단계 ID 기준으로만 처리할 수 있다.
- 위험군 단계가 직접 주어지면 우선 사용한다.
- 위험군 판단 로직이 분리되어 있으면 그 결과를 recommendation request에 포함한다.

### 예외 상황
- 위험군 입력 누락
- 허용 범위를 벗어난 단계값
- 입력 형식 불일치

### 현재 상태
활성

---

## F-02. 관심 직무/도메인 기반 추천 요청

### 목적
사용자가 관심 직무 또는 도메인을 기준으로 추천 흐름을 시작할 수 있도록 한다.

### 입력
- `risk_stage_id`
- 관심 직무(선택)
- 관심 도메인(선택)
- 자유 텍스트 입력(선택, 후단에서 taxonomy 매핑 필요)

### 출력
- 정규화된 recommendation query context
- taxonomy 매핑 결과
- recommendation candidate search input

### 처리 규칙
- `related_jobs`는 허용된 희망 직무 taxonomy 세부 직무만 사용한다.
- `related_domains`는 허용된 domain taxonomy 세부 라벨만 사용한다.
- 자유 텍스트 입력은 허용하되, 최종 내부 표현은 taxonomy 기준으로 정규화해야 한다.
- 직무/도메인 입력이 모두 없으면 위험군 기준 기본 추천으로 진입한다.

### 예외 상황
- 직무/도메인 입력이 taxonomy에 매핑되지 않음
- 허용되지 않은 자유 라벨 생성 시도
- 필수 입력 맥락 부족

### 현재 상태
활성

---

## F-03. 자격증 후보 결과 조회

### 목적
정규화된 recommendation context를 바탕으로 자격증 후보를 반환한다.

### 입력
- `risk_stage_id`
- 정규화된 `related_jobs`
- 정규화된 `related_domains`
- recommendation query context

### 출력
추천 후보 리스트. 각 후보는 최소 아래 정보를 포함한다.
- `cert_id`
- `cert_name`
- `related_jobs`
- `related_domains`
- `roadmap_stages`
- `text_for_dense` 기반 요약 또는 추천 이유

### 처리 규칙
- 후보 검색은 canonical recommendation data를 우선 사용한다.
- 추천 결과는 taxonomy 밖 라벨을 포함하지 않아야 한다.
- 추천 결과가 다수일 경우 정렬 기준은 후속 상세 문서에서 고정한다.
- 일정 정보는 현재 단계에서 기본 출력 필드가 아니다.

### 예외 상황
- candidate row 미존재
- 추천 결과 0건
- canonical store 연결 실패
- 추천 결과에 taxonomy 밖 값 포함

### 현재 상태
활성

---

## F-04. 추천 이유 / 설명 근거 조회

### 목적
추천 결과에 대해 공식 PDF / HTML 문서 기반 설명 근거를 제공한다.

### 입력
- `cert_id`
- optional: `doc_type`, `source_type`, `domain`, `job`
- recommendation context

### 출력
- 근거 텍스트 snippet
- 관련 문서 식별자
- optional provenance metadata

### 처리 규칙
- 근거 검색은 PDF / HTML 기반 retrieval 계층을 사용한다.
- 구조적 추천 결과와 설명 근거는 분리된 계층에서 생성된다.
- 근거는 추천 이유를 보완하는 용도로 제공한다.
- 설명 근거가 없더라도 추천 결과 자체는 반환 가능해야 한다.

### 예외 상황
- retrieval 결과 0건
- 문서 파싱/인덱싱 누락
- source freshness 문제
- exact match 실패

### 현재 상태
활성

---

## F-05. 위험군 맞춤 로드맵 조회

### 목적
추천 결과 또는 위험군/도메인 기준으로 단계형 로드맵을 생성한다.

### 입력
- `risk_stage_id`
- optional: `cert_id`
- optional: `related_domains`
- optional: `related_jobs`

### 출력
- 로드맵 단계 리스트
- 단계별 설명
- 단계별 연결 자격증 또는 도메인 힌트

### 처리 규칙
- 로드맵은 위험군 단계 기준과 canonical relation 기준을 결합해 생성한다.
- 현재 단계에서는 일정/링크 없이도 로드맵 결과가 성립해야 한다.
- 로드맵 단계명은 roadmap master 기준을 따른다.

### 예외 상황
- roadmap stage 데이터 누락
- risk stage와 roadmap 연결 관계 없음
- 도메인/직무 기준 불충분

### 현재 상태
활성

---

## F-06. CSV canonicalization 실행

### 목적
원본 CSV를 canonical entity / relation / candidate 구조로 변환한다.

### 입력
- CSV 파일 세트
- dataset type registry
- schema mapping registry
- taxonomy 기준 파일

### 출력
- canonical entity table
- canonical relation table
- validation report

### 처리 규칙
- CSV는 Parse IR 대상이 아니다.
- dataset type 판별 후 schema mapping을 수행한다.
- 값 정규화, alias 정리, taxonomy 제한 검증을 수행한다.

### 예외 상황
- dataset type 미식별
- schema mapping 실패
- invalid field 값
- taxonomy 밖 값 생성
- source row 누락

### 현재 상태
활성

---

## F-07. entity / relation / candidate 재생성

### 목적
정규화된 canonical data를 바탕으로 recommendation candidate row를 재생성한다.

### 입력
- canonical entity table
- canonical relation table
- risk stage master
- roadmap stage master

### 출력
- `certificate_candidate_row`
- candidate validation report

### 처리 규칙
- candidate row는 recommendation core의 기본 검색 단위다.
- `related_domains`는 domain taxonomy 세부 라벨만 허용한다.
- `related_jobs`는 희망 직무 taxonomy 세부 직무만 허용한다.
- 일정 API 관련 필드는 현재 reserved/null 허용이다.

### 예외 상황
- entity / relation 누락
- candidate 생성 0건
- 중복 candidate 생성
- required field 누락

### 현재 상태
활성

---

## F-08. 시험 일정 조회

### 목적
추천된 자격증과 연결된 시험 일정을 보여준다.

### 입력
- `cert_id`

### 출력
- 시험 일정 목록

### 처리 규칙
- API 연동 후 활성화
- canonical target schema에 병합된 일정 데이터 사용

### 예외 상황
- API 미연동
- 일정 데이터 없음
- freshness 초과

### 현재 상태
reserved

---

## F-09. 접수 일정 / 링크 조회

### 목적
추천된 자격증과 연결된 접수 일정, 지원 링크를 보여준다.

### 입력
- `cert_id`

### 출력
- 접수 시작일 / 종료일
- 지원 링크

### 처리 규칙
- API 또는 정규화된 링크 데이터가 필요하다.
- 현재 단계에서는 reserved로 유지한다.

### 예외 상황
- API 미연동
- 링크 데이터 없음
- 만료된 링크

### 현재 상태
reserved

---

## F-10. 관리자 점검 화면

### 목적
정규화 결과, candidate 생성 결과, validation 결과를 확인할 수 있는 관리 기능을 제공한다.

### 입력
- 관리자 요청
- validation result 조회 기준

### 출력
- validation summary
- candidate build 상태
- 오류 목록

### 처리 규칙
- MVP에서는 파일/배치 기반으로 대체 가능하다.
- 화면 기능은 후속으로 둔다.

### 예외 상황
- 관리자 기능 미구현
- validation 데이터 미존재

### 현재 상태
reserved

---

## 5. 기능 간 의존성

| 선행 기능 | 후행 기능 | 설명 |
|---|---|---|
| F-01 | F-02 | 위험군 기준이 recommendation context에 포함됨 |
| F-02 | F-03 | 정규화된 직무/도메인 입력이 후보 검색으로 이어짐 |
| F-03 | F-04 | 추천 결과가 있어야 설명 근거를 조회할 수 있음 |
| F-03 | F-05 | 추천 결과 또는 context가 있어야 로드맵 생성 가능 |
| F-06 | F-07 | canonicalization 결과가 있어야 candidate 생성 가능 |
| F-07 | F-03 | candidate row가 recommendation core의 주요 입력 |
| F-08/F-09 | F-03 | 후속 일정/링크 기능은 추천 결과와 결합됨 |

---

## 6. 공통 예외처리 원칙

모든 사용자 기능은 아래 공통 원칙을 따른다.

1. 추천 결과가 0건이어도 시스템 오류와 구분해야 한다.
2. 문서 근거가 없더라도 추천 결과는 반환 가능해야 한다.
3. taxonomy 밖 값이 생성되면 validation error로 간주한다.
4. reserved 기능은 명시적으로 비활성 상태로 처리한다.
5. 현재 스프린트 범위 밖 기능을 임의로 fallback 구현하지 않는다.

---

## 7. 현재 MVP 활성 기능

현재 MVP에서 실제로 활성화해야 하는 기능은 아래와 같다.

- F-01 위험군 기반 추천 진입
- F-02 관심 직무/도메인 기반 추천 요청
- F-03 자격증 후보 결과 조회
- F-04 추천 이유 / 설명 근거 조회
- F-05 위험군 맞춤 로드맵 조회
- F-06 CSV canonicalization 실행
- F-07 entity / relation / candidate 재생성

---

## 8. 후속 문서 연결

이 문서의 각 기능은 아래 문서와 연결된다.

- API 요청/응답 형식 → `API_SPEC.md`
- 데이터 필드 구조 → `DATA_SCHEMA.md`
- retrieval 및 indexing 세부 → `RAG_PIPELINE.md`
- 시스템 계층 책임 → `SYSTEM_ARCHITECTURE.md`

---

## 9. 최종 요약

이 문서는 시스템이 제공해야 하는 기능을 **사용자 기능 단위**로 정의한다.  
핵심 기능은 추천 진입, 추천 결과 생성, 로드맵 생성, 설명 근거 제공, canonicalization 실행이며, 일정/링크 기능은 현재 reserved 상태다.

즉, 현재 단계의 기능 중심은 아래 두 축이다.

1. **추천 가능한 구조적 데이터 생성**
2. **추천 결과를 사용자 흐름으로 제공**
