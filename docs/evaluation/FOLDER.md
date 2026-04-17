# FOLDER.md

> **파일명**: FOLDER.md
> **폴더 경로**: `docs/evaluation/`
> **최종 수정일**: 2026-04-18
> **문서 해시**: SHA256:TBD
> **문서 역할**: 추천 시스템 평가·골든셋 구축 산출물
> **문서 우선순위**: reference
> **연관 문서**: EVALUATION.md, EVALUATION_GUIDELINE.md, FEATURE_SPEC.md

---

## 1. 용도

추천 파이프라인의 품질 검증에 쓰이는 페르소나·베이스라인·골든셋 파일을 둔다.

---

## 2. 파일 목록

| 파일 | 설명 | 상태 |
|---|---|---|
| `personas.json` | 15개 대표 페르소나 — API 요청 본문 + 기대 결과 명세 | ✅ |
| `baseline_results.json` | 5개 핵심 페르소나 베이스라인 결과 (2026-04-18 생성) | ✅ |
| `golden_set.jsonl` | 5개 베이스라인 기반 초기 정답셋 (전문가 검토 필요) | ✅ 자동생성본 |
| `audit_integrity.md` | 데이터 무결성 감사 결과 | ✅ |

---

## 3. 담지 않는 것

- 원본 CSV / JSONL 데이터
- 모델 가중치 / 임베딩 파일

## 4. 사용 방법

`personas.json`의 `api_request` 필드를 `POST /api/v1/recommendations` 본문으로 사용.

## 5. Next Steps (Audit Findings by Gemini CLI)

1. **전문가 정성 검토**: `golden_set.jsonl`로 생성된 초기 정답셋이 실제 도메인 지식과 부합하는지 전문가 검토 및 수정 필요.
2. **LLM-as-a-Judge 도입**: 시스템 출력값과 골든셋을 비교하여 점수(Relevance, Accuracy)를 매기는 자동 평가 스크립트 구축.
3. **골든셋 확장**: 현재 5종인 골든셋을 `personas.json`의 전체 15종으로 확대 적용.
4. **Reasoning 품질 고도화**: `cert_to_cert_relation.csv`에 추출된 `reasoning_evidence` 문장이 사용자에게 자연스럽게 전달되는지 프롬프트 튜닝 및 검증.
