# EVALUATION_GUIDELINE.md

> **파일명**: EVALUATION_GUIDELINE.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
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
