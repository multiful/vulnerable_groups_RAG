# EVALUATION_GUIDELINE.md

> **파일명**: EVALUATION_GUIDELINE.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:841c945cd38506dbf1aba14a04dc17299cbe00cc4f5aae3b53fdaf5ff89d0e13
> **문서 역할**: RAG·추천 평가 기준, metric 선택 이유, baseline·비교 원칙 정의  
> **문서 우선순위**: 10  
> **연관 문서**: CHANGE_CONTROL.md, RAG_PIPELINE.md, EVALUATION.md, EXPERIMENT_GUIDE.md, PRD.md  
> **참조 규칙**: 평가 지표나 baseline을 바꿀 때 먼저 이 문서를 수정한 뒤 `EVALUATION.md`에 결과를 기록한다.

---

## 1. 문서 목적

검색 품질·추천 적합성 등을 **어떤 기준으로 측정할지** 고정한다.  
구현 초기 스캐폴딩 단계에서는 본문을 최소로 두고, 파이프라인이 갖춰진 뒤 metric·데이터셋·합격 기준을 채운다.

---

## 2. 현재 단계

- **활성**: 문서 슬롯만 확보. 구체 metric·baseline은 TODO.
- **reserved**: reranker, hybrid(BM25 상시) 최적화는 프로젝트 규칙상 아직 범위 밖이면 본 문서에도 “미적용”으로 명시한다.

---

## 3. 후속 작업 (TODO)

- 검색: recall@k, nDCG 등 후보 metric과 선택 이유
- 추천: 구조적 후보와 설명 근거의 분리 평가 방식
- `EVALUATION.md`와의 역할 분리: 본 문서는 “기준”, `EVALUATION.md`는 “결과 기록”

---

## 4. Parse·인덱스 품질 측정 후보 (채택 전)

아래는 **심화 참고 자료**에서 흔히 쓰는 점검 축을, 본 프로젝트 목적(evidence 검색 안정화·증분 비용)에 맞게 **후보만** 옮긴 것이다.  
dataset·합격 기준이 없으면 수치 목표를 두지 않으며, `§2`의 reserved 항목과 혼동하지 않는다.

| 축 | 측정 후보 | 비고 |
|----|-----------|------|
| Parse | `reading_order_rebuilt=true` 비율, `fallback_used` 비율 | `DATA_SCHEMA.md` §11·manifest 연계 |
| Parse | `table_assisted_pages`·OCR 페이지 수 분포 | 페이지 예외 경로 비용 파악 |
| 메타 | `section_path`·`source_loc` 등 필수에 가까운 필드 채움률 | 필터·근거 추적 품질 |
| 인덱스(오프라인) | parse→chunk→embed 파이프라인 지연 P50/P95 | 전체 재처리 대신 병목 구간 식별 |
| 코퍼스 | 동일·유사 `file_hash` 또는 유사 청크 텍스트 비율 | `RAG_PIPELINE.md` §15 reserved “감사”와 연결 가능 |

자연어 질의·HyDE·reranker 품질 평가는 해당 기능이 `FEATURE_SPEC.md`/`API_SPEC.md`에서 **활성**으로 정의된 뒤 본 문서에 절을 추가한다.
