# ROOT_DOC_GUIDE.md

> **파일명**: ROOT_DOC_GUIDE.md  
> **최종 수정일**: 2026-04-03  
> **문서 역할**: 루트 문서 사용 가이드 / 문서 탐색 안내 문서  
> **문서 우선순위**: reference  
> **연관 문서**: README.md, PROJECT_SUMMARY.md, CHANGE_CONTROL.md, PRD.md, SYSTEM_ARCHITECTURE.md, FEATURE_SPEC.md, DATA_SCHEMA.md, API_SPEC.md, PROMPT_DESIGN.md, RAG_PIPELINE.md, DIRECTORY_SPEC.md, DEV_LOG.md  
> **참조 규칙**: 어떤 문서를 먼저 열어야 할지 헷갈릴 때 이 문서를 먼저 확인한다.

---

## 1. 문서 목적

이 문서는 루트에 있는 핵심 md 문서들을 **한눈에 정리하고**,  
각 문서를 **언제**, **왜**, **어떤 상황에서** 열어야 하는지 빠르게 판단할 수 있도록 만든 운영 가이드다.

이 문서는 다음을 돕는다.

- 루트 문서 전체 구조 이해
- 작업 상황별 참조 문서 선택
- 문서 간 역할 구분
- 작업 순서에 맞는 문서 탐색
- 수정 시 어떤 문서를 먼저 고쳐야 하는지 판단

이 문서는 **요약/탐색 가이드**이며, 실제 기준선은 각 원본 문서가 담당한다.

---

## 2. 가장 먼저 읽는 문서

작업 시작 시 기본 순서는 아래와 같다.

1. `README.md`
2. `CHANGE_CONTROL.md`
3. `PRD.md`
4. `SYSTEM_ARCHITECTURE.md`
5. 작업 유형에 따라 상세 문서 선택

즉, 이 문서는 “길잡이”이고, 실제 기준 문서는 위 4개부터 순서대로 확인한다.

---

## 3. 루트 문서 한눈에 보기

| 문서명 | 역할 한 줄 요약 | 언제 여는가 |
|---|---|---|
| `README.md` | 프로젝트 입구 문서 | 프로젝트를 처음 열었을 때 |
| `PROJECT_SUMMARY.md` | 전체 요약·청킹 개요·긴 기법 문서 위치 | 한 페이지로 구조를 잡고 싶을 때 |
| `CHANGE_CONTROL.md` | 문서 수정 규칙과 작업 절차 | 구현 전에, 문서 수정 전에 |
| `PRD.md` | 현재 해결해야 하는 제품 문제와 범위 | 무엇을 만들지 확인할 때 |
| `SYSTEM_ARCHITECTURE.md` | 시스템 계층, 책임, 온라인/오프라인 흐름 | 어떻게 나눠서 만들지 볼 때 |
| `FEATURE_SPEC.md` | 기능별 입력/출력/예외/상태 | 특정 기능을 구현하거나 수정할 때 |
| `DATA_SCHEMA.md` | 엔티티/관계/필드/제약 구조 | 데이터 구조를 설계/수정할 때 |
| `API_SPEC.md` | endpoint / request / response / error 계약 | 프론트-백 연결 또는 API 수정 시 |
| `PROMPT_DESIGN.md` | 프롬프트 역할, 입력, 출력, 검증, fallback | 프롬프트/응답 생성 로직 수정 시 |
| `RAG_PIPELINE.md` | parse/chunk/metadata/embedding/retrieval 흐름 | 문서 검색 구조를 수정할 때 |
| `DIRECTORY_SPEC.md` | 디렉토리와 파일 책임 정의 | 폴더 구조/파일 위치를 바꿀 때 |
| `EVALUATION_GUIDELINE.md` | 평가 기준과 baseline | 실험 기준을 정할 때 |
| `EVALUATION.md` | 실제 평가 결과 기록 | 결과를 정리하거나 비교할 때 |
| `EXPERIMENT_GUIDE.md` | 실험 세팅과 재현 방법 | 실험을 재현하거나 넘길 때 |
| `ERROR_ANALYSIS.md` | 실패 사례와 개선 방향 | 왜 틀렸는지 분석할 때 |
| `DEV_LOG.md` | 날짜별 진행 로그와 변경 이력 | 무엇을 바꿨는지 기록/복기할 때 |
| `Indexing_Architecture.txt` | 초기/참고용 인덱싱 구조 메모 | 기존 구조 출발점을 확인할 때 |

---

## 4. 작업 상황별로 어떤 문서를 열어야 하는가

## 4.1 “이 프로젝트가 뭘 하는지”부터 보고 싶다
먼저 아래 순서로 연다.

1. `README.md`
2. `PROJECT_SUMMARY.md` (한 페이지 요약)
3. `PRD.md`
4. `SYSTEM_ARCHITECTURE.md`

---

## 4.2 “이 기능을 구현해도 되는지” 확인하고 싶다
아래 순서로 연다.

1. `PRD.md`
2. `FEATURE_SPEC.md`
3. `API_SPEC.md`
4. `DATA_SCHEMA.md`

질문 예시:
- 이 기능이 MVP 범위 안인가?
- reserved 기능인가?
- 어떤 입력/출력을 가져야 하나?

---

## 4.3 “데이터 구조를 바꾸고 싶다”
아래 순서로 연다.

1. `CHANGE_CONTROL.md`
2. `PRD.md`
3. `SYSTEM_ARCHITECTURE.md`
4. `DATA_SCHEMA.md`
5. 필요 시 `FEATURE_SPEC.md`, `API_SPEC.md`

질문 예시:
- 이 필드를 추가해도 되는가?
- entity / relation / candidate 중 어디에 넣어야 하는가?
- reserved 필드로 둘 것인가, 지금 활성화할 것인가?

---

## 4.4 “API를 수정하고 싶다”
아래 순서로 연다.

1. `FEATURE_SPEC.md`
2. `DATA_SCHEMA.md`
3. `API_SPEC.md`

질문 예시:
- request body에 뭐가 들어가야 하나?
- response에 어떤 필드를 노출해야 하나?
- status code와 error envelope은 어떻게 유지해야 하나?

---

## 4.5 “프롬프트를 수정하고 싶다”
아래 순서로 연다.

1. `PROMPT_DESIGN.md`
2. `API_SPEC.md`
3. `RAG_PIPELINE.md`
4. `DATA_SCHEMA.md`

질문 예시:
- 프롬프트가 추천을 직접 계산해도 되나?
- 어떤 입력 슬롯을 받아야 하나?
- output parser / validator / fallback은 어떻게 되는가?

---

## 4.6 “RAG 구조를 손보고 싶다”
아래 순서로 연다.

1. `SYSTEM_ARCHITECTURE.md`
2. `RAG_PIPELINE.md`
3. `DATA_SCHEMA.md`
4. `EVALUATION_GUIDELINE.md`

질문 예시:
- CSV도 RAG 대상인가?
- sparse/BM25를 지금 켜도 되는가?
- OCR을 어디까지 적용해야 하나?
- parse/chunking 변경 시 어떤 버전을 올려야 하나?

---

## 4.7 “폴더 구조나 파일 위치를 바꾸고 싶다”
아래 순서로 연다.

1. `CHANGE_CONTROL.md`
2. `DIRECTORY_SPEC.md`
3. 필요 시 `SYSTEM_ARCHITECTURE.md`

질문 예시:
- 이 파일을 루트에 둬야 하나?
- backend/rag에 둘지 backend/app에 둘지?
- 새 폴더를 만들어도 되는가?

---

## 4.8 “평가를 설계하거나 결과를 정리하고 싶다”
아래 순서로 연다.

1. `EVALUATION_GUIDELINE.md`
2. `EVALUATION.md`
3. `EXPERIMENT_GUIDE.md`
4. `ERROR_ANALYSIS.md`

질문 예시:
- baseline은 무엇인가?
- 어떤 metric을 써야 하나?
- 결과를 어디에 기록해야 하나?

---

## 4.9 “지금까지 뭘 바꿨는지 보고 싶다”
아래 순서로 연다.

1. `DEV_LOG.md`
2. `EVALUATION.md`
3. `ERROR_ANALYSIS.md`

---

## 5. 문서 간 역할 구분

문서가 겹치지 않게 보기 위해 아래처럼 이해하면 된다.

### 5.1 제품 관점
- `README.md`: 입구
- `PRD.md`: 무엇을 만들지

### 5.2 구조 관점
- `SYSTEM_ARCHITECTURE.md`: 어떻게 나눌지
- `DIRECTORY_SPEC.md`: 어디에 둘지

### 5.3 구현 관점
- `FEATURE_SPEC.md`: 기능이 어떻게 동작해야 하는지
- `DATA_SCHEMA.md`: 어떤 데이터 구조를 써야 하는지
- `API_SPEC.md`: 어떤 계약으로 연결하는지
- `PROMPT_DESIGN.md`: LLM이 어떤 형식으로 보조하는지
- `RAG_PIPELINE.md`: 문서 검색 계층이 어떻게 동작하는지

### 5.4 검증/운영 관점
- `EVALUATION_GUIDELINE.md`: 무엇으로 평가할지
- `EVALUATION.md`: 실제 결과가 어땠는지
- `EXPERIMENT_GUIDE.md`: 어떻게 재현하는지
- `ERROR_ANALYSIS.md`: 왜 실패했는지
- `DEV_LOG.md`: 언제 무엇을 바꿨는지

### 5.5 문서 운영 관점
- `CHANGE_CONTROL.md`: 문서를 어떤 순서와 규칙으로 갱신할지

---

## 6. 추천 작업 순서

새 작업을 시작할 때 권장 순서는 아래와 같다.

1. `README.md`로 전체 맥락 확인
2. `CHANGE_CONTROL.md`로 문서 수정 규칙 확인
3. `PRD.md`로 현재 범위 확인
4. `SYSTEM_ARCHITECTURE.md`로 구조 확인
5. 작업 종류에 따라 상세 문서 확인
6. 문서 수정
7. 구현
8. 검증
9. `DEV_LOG.md` 반영

---

## 7. 이 가이드가 특히 필요한 순간

이 문서는 아래 상황에서 가장 유용하다.

- 문서가 많아져서 어디부터 읽어야 할지 헷갈릴 때
- 같은 내용이 여러 문서에 있는 것처럼 느껴질 때
- 새 작업을 시작하기 전에 참조 순서를 정하고 싶을 때
- Cursor나 협업자가 어떤 문서를 먼저 봐야 할지 안내할 때
- reserved와 active 범위를 혼동할 때

---

## 8. 현재 문서 세트로 충분한가

현재 루트 문서 세트만으로도 **설계 → 구현 → 실험 → 평가 → 기록**까지 기본 운영은 가능하다.

즉, 지금 당장 **반드시 추가해야 하는 루트 문서**는 없다.

다만 아래 문서는 필요 시 선택적으로 추가할 수 있다.

### 선택 추가 후보 1. `TAXONOMY_SPEC.md`
도메인 taxonomy와 희망 직무 taxonomy를 별도 문서로 더 강하게 고정하고 싶을 때 사용한다.

추천 상황:
- taxonomy가 자주 바뀜
- related_domains / related_jobs 검토가 잦음
- 협업자가 taxonomy를 자주 수정함

### 선택 추가 후보 2. `CANONICALIZATION_SPEC.md`
CSV canonicalization 규칙을 더 세밀하게 분리하고 싶을 때 사용한다.

추천 상황:
- schema mapping 규칙이 복잡해짐
- alias 정책이 많아짐
- entity/relation build 규칙이 길어짐

### 선택 추가 후보 3. `RELEASE_CHECKLIST.md`
배포 전 체크리스트를 별도 문서로 고정하고 싶을 때 사용한다.

추천 상황:
- API, 프롬프트, 인덱스, 문서 버전 동기화 체크가 필요함
- 여러 사람이 배포 전 검수를 같이 함

하지만 현재 단계에서는 **필수는 아님**이다.

---

## 9. 최종 요약

이 문서는 루트 md 문서 전체를 빠르게 탐색하기 위한 운영 가이드다.

핵심 원칙은 아래 두 가지다.

1. **무엇을 만들지 → PRD**
2. **어떻게 만들지 → SYSTEM_ARCHITECTURE 이후 상세 문서**

즉, 문서가 많더라도 아래 순서만 기억하면 된다.

`README → CHANGE_CONTROL → PRD → SYSTEM_ARCHITECTURE → 작업별 상세 문서`
