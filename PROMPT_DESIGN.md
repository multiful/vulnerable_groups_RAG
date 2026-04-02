# PROMPT_DESIGN.md

> **파일명**: PROMPT_DESIGN.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: 시스템 프롬프트, 프롬프트 전략, 출력 계약 정의 문서  
> **문서 우선순위**: 7  
> **연관 문서**: PRD.md, SYSTEM_ARCHITECTURE.md, FEATURE_SPEC.md, RAG_PIPELINE.md, API_SPEC.md  
> **참조 규칙**: 프롬프트 역할, 입력 슬롯, 출력 형식, 근거 사용 규칙을 변경할 때 먼저 이 문서를 수정한다.

---

## 1. 문서 목적

이 문서는 LLM 또는 프롬프트 기반 구성 요소가 **무엇을 입력받고 어떤 원칙으로 응답을 만들어야 하는지**를 정의한다.  
시스템 내에서 프롬프트는 recommendation 결과를 직접 계산하는 핵심 엔진이 아니라, **설명 정리, 근거 결합, 로드맵 문장화, 응답 형식 제어**에 사용된다.

이 문서는 다음을 정의한다.

- 프롬프트 사용 위치
- 프롬프트 역할
- 입력 슬롯
- 출력 계약
- 전역 가드레일
- few-shot 예시
- reserved 프롬프트 범위

이 문서는 다음을 직접 정의하지 않는다.

- retrieval index 구조
- reranker 튜닝
- API endpoint 계약
- DB 필드 구조
- 제품 문제 정의

위 항목은 각각 `RAG_PIPELINE.md`, `API_SPEC.md`, `DATA_SCHEMA.md`, `PRD.md`에서 담당한다.

---

## 2. 프롬프트 사용 원칙

### 2.1 구조적 추천과 설명 생성 분리
추천 후보와 로드맵의 구조적 기반은 canonical data에서 오며, 프롬프트는 이를 문장으로 정리하거나 문서 근거와 결합하는 데 사용한다.

### 2.2 근거 우선
문서 기반 주장이나 사실 설명은 retrieval evidence를 우선 사용한다.

### 2.3 비확정 정보 추정 금지
위험군 2~4단계 의미, 일정 API, 미연동 링크 등 확정되지 않은 정보는 임의로 생성하지 않는다.

### 2.4 taxonomy 밖 표현 금지
`related_domains`, `related_jobs`는 내부 canonical 값 밖의 새 라벨을 생성하지 않는다.

### 2.5 결과 형식 고정
프롬프트 출력은 화면과 API가 기대하는 구조를 따라야 하며, 불필요한 산문형 장문 응답을 만들지 않는다.

---

## 3. 프롬프트 사용 위치

현재 프롬프트는 아래 4개 영역에서 사용한다.

1. 추천 결과 설명 생성
2. 로드맵 설명 생성
3. 문서 근거 요약
4. 사용자 응답 조립

reserved:
- taxonomy 정규화용 프롬프트
- 일정 요약용 프롬프트
- 대화형 상담 에이전트 프롬프트

---

## 4. 전역 가드레일

모든 프롬프트는 아래 규칙을 따른다.

1. canonical data를 사실 기반으로 사용한다.
2. retrieval evidence가 있을 때만 문서 근거성 설명을 단정적으로 쓴다.
3. evidence가 없으면 “설명 근거 없음”을 허용한다.
4. 일정/접수/링크는 현재 실제 연동 전이므로 임의 날짜를 생성하지 않는다.
5. 위험군 2~4단계 세부 의미를 추정하지 않는다.
6. taxonomy 밖 직무/도메인 라벨을 새로 만들지 않는다.
7. 답변은 사용자 행동에 도움이 되도록 간결하고 구조적으로 쓴다.

---

## 5. 활성 프롬프트 정의

## P-01. Recommendation Explanation Prompt

### 목적
구조적 추천 결과를 사용자에게 이해 가능한 설명 문장으로 변환한다.

### 입력 슬롯
- `risk_stage_id`
- `cert_name`
- `related_jobs`
- `related_domains`
- `roadmap_stages`
- optional `evidence_snippets`

### 출력 계약
아래 필드를 생성할 수 있어야 한다.

- `summary`
- `why_recommended`
- `job_domain_connection`

### 출력 원칙
- summary는 1~2문장으로 제한
- `related_jobs`, `related_domains`의 연결 이유를 설명
- evidence가 있으면 근거 기반 설명을 포함
- evidence가 없으면 구조적 추천 이유만 설명

### 예시 출력
```json
{
  "summary": "정보처리기사는 데이터/AI와 소프트웨어개발 영역 모두와 연결되는 대표 자격증입니다.",
  "why_recommended": "현재 입력한 직무·도메인과의 연관성이 높아 기초 단계 추천 후보로 적합합니다.",
  "job_domain_connection": "데이터 분석과 백엔드 개발 준비 맥락에서 함께 활용될 수 있습니다."
}
```

---

## P-02. Roadmap Explanation Prompt

### 목적
canonical roadmap stage 결과를 사용자 친화적인 단계 설명으로 정리한다.

### 입력 슬롯
- `risk_stage_id`
- `roadmap_stages`
- optional `cert_name`
- optional `related_domains`
- optional `related_jobs`

### 출력 계약
- `roadmap_overview`
- `stage_descriptions[]`

### 출력 원칙
- 단계별 설명은 짧고 명확하게 작성
- 행동 지시 수준으로 표현
- 위험군 2~4단계의 세부 정책을 임의로 해석하지 않음

### 예시 출력
```json
{
  "roadmap_overview": "현재 단계에서는 기초 이해를 먼저 확보한 뒤 실무 연결 단계로 넘어가는 흐름이 적합합니다.",
  "stage_descriptions": [
    "기초: 관련 직무와 자격증의 연결 구조를 이해합니다.",
    "실무: 실제 직무 준비에 필요한 자격증과 학습 순서를 정리합니다."
  ]
}
```

---

## P-03. Evidence Summary Prompt

### 목적
retrieval된 PDF / HTML 근거 snippet을 짧고 명확한 설명으로 정리한다.

### 입력 슬롯
- `cert_id`
- `cert_name`
- `evidence_snippets[]`
- optional `doc_titles[]`

### 출력 계약
- `evidence_summary`
- `evidence_points[]`

### 출력 원칙
- 원문을 길게 복사하지 않는다.
- 핵심 근거만 짧게 정리한다.
- 근거가 여러 개면 중복 설명을 제거한다.
- evidence가 없으면 빈 결과를 허용한다.

### 예시 출력
```json
{
  "evidence_summary": "공식 문서 기준으로 정보처리기사는 정보 시스템 구축 및 소프트웨어 개발 역량을 검증하는 자격으로 설명됩니다.",
  "evidence_points": [
    "국가기술자격으로 분류됩니다.",
    "소프트웨어 개발 및 정보 시스템 관련 역량과 연결됩니다."
  ]
}
```

---

## P-04. Final Response Composer Prompt

### 목적
추천 결과, 로드맵, 설명 근거를 하나의 응답 구조로 조립한다.

### 입력 슬롯
- `candidate`
- `recommendation_explanation`
- `roadmap_explanation`
- optional `evidence_summary`

### 출력 계약
- `headline`
- `body`
- `next_action`

### 출력 원칙
- 사용자에게 바로 보여줄 수 있는 결과 형태
- 장문 에세이 금지
- 현재 단계에서 할 수 있는 행동을 마지막에 제시
- 일정/링크 미연동 상태를 숨기지 않음

### 예시 출력
```json
{
  "headline": "정보처리기사 추천",
  "body": "현재 입력한 직무와 도메인 기준에서 정보처리기사는 기초-실무 흐름으로 연결하기 좋은 후보입니다.",
  "next_action": "먼저 관련 직무와 자격증의 연결 구조를 확인한 뒤 기초 단계 학습 순서를 정리해보세요."
}
```

---

## 6. reserved 프롬프트

아래 프롬프트는 현재 reserved로 둔다.

### R-01. Taxonomy Normalization Prompt
자유 텍스트를 taxonomy에 맞춰 정규화하는 프롬프트  
현재는 규칙 기반 또는 별도 로직 우선

### R-02. Schedule Summary Prompt
시험 일정 / 접수 일정 / 링크를 요약하는 프롬프트  
API 연동 이후 활성화

### R-03. Conversational Counseling Prompt
장기 대화형 상담 에이전트용 프롬프트  
현재 제품 범위 밖

---

## 7. Prompt Input Contract

프롬프트 입력은 가능한 한 이미 정규화된 데이터를 사용한다.

### 우선 입력
- `risk_stage_id`
- `cert_id`
- `cert_name`
- `related_jobs`
- `related_domains`
- `roadmap_stages`
- `evidence_snippets`

### 지양 입력
- 정규화되지 않은 자유 라벨
- 미확정 정책 값
- 원본 장문 문서 전체

---

## 8. Output Contract 원칙

모든 프롬프트 출력은 아래 조건을 만족해야 한다.

1. JSON 또는 구조화된 필드 형태로 파싱 가능해야 한다.
2. 화면/API에서 바로 쓸 수 있어야 한다.
3. 중복 표현을 줄여야 한다.
4. evidence 기반 주장과 구조 기반 설명을 혼합하더라도 출처 성격을 섞지 않아야 한다.
5. reserved 필드를 임의 생성하지 않아야 한다.

---

## 9. Few-shot 예시

## 예시 1. recommendation explanation

### 입력
```json
{
  "risk_stage_id": "risk_stage_1",
  "cert_name": "정보처리기사",
  "related_jobs": ["데이터 분석", "백엔드 개발"],
  "related_domains": ["데이터/AI", "소프트웨어개발"],
  "roadmap_stages": ["기초", "실무"]
}
```

### 출력
```json
{
  "summary": "정보처리기사는 데이터/AI와 소프트웨어개발 영역을 함께 연결할 수 있는 대표 자격증입니다.",
  "why_recommended": "현재 관심 직무와 도메인 기준에서 기초 단계부터 실무 단계까지 이어지는 구조를 만들기 좋습니다.",
  "job_domain_connection": "데이터 분석과 백엔드 개발 준비 흐름 모두에서 활용 가능한 후보입니다."
}
```

---

## 예시 2. evidence summary

### 입력
```json
{
  "cert_name": "정보처리기사",
  "evidence_snippets": [
    "정보처리기사는 정보 시스템 구축 및 소프트웨어 개발 관련 역량을 검정한다."
  ]
}
```

### 출력
```json
{
  "evidence_summary": "공식 문서 기준으로 정보처리기사는 정보 시스템 구축 및 소프트웨어 개발 역량과 연결되는 자격으로 설명됩니다.",
  "evidence_points": [
    "정보 시스템 구축 역량과 관련됩니다.",
    "소프트웨어 개발 역량과 관련됩니다."
  ]
}
```

---

## 10. 프롬프트 실패 처리 원칙

1. 프롬프트 출력이 파싱되지 않으면 fallback 템플릿 응답을 사용한다.
2. evidence가 없으면 evidence summary를 생략한다.
3. reserved 정보가 요청되면 “현재 미연동” 상태를 유지한다.
4. taxonomy 밖 라벨이 생성되면 응답을 폐기하거나 후처리 검증에서 차단한다.

---

## 11. 프롬프트 버전 관리

각 프롬프트는 버전 필드를 가진다.

예:
- `prompt_name`
- `prompt_version`
- `last_updated`
- `owner`

### 원칙
- breaking change가 있으면 version을 올린다.
- few-shot 변경만으로도 버전을 갱신할 수 있다.
- API 응답이 프롬프트 구조에 의존하면 계약도 함께 점검한다.

---

## 12. 후속 문서 연결

- 기능 사용 위치 → `FEATURE_SPEC.md`
- 시스템 흐름 → `SYSTEM_ARCHITECTURE.md`
- retrieval 전략 → `RAG_PIPELINE.md`
- API 출력 계약 → `API_SPEC.md`

---

## 13. 최종 요약

이 문서는 프롬프트가 시스템 안에서 어떤 역할을 하고, 어떤 입력을 받아 어떤 구조로 결과를 내야 하는지 정의한다.  
현재 활성 프롬프트는 recommendation 설명, roadmap 설명, evidence summary, final response 조립이며, taxonomy 정규화와 일정 요약은 reserved 상태다.

즉, 현재 프롬프트 계층의 목적은 아래 두 가지다.

1. **구조적 추천 결과를 사용자 친화적인 문장으로 변환**
2. **문서 근거를 짧고 안전하게 결합**
