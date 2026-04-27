# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `experiments/reports`  
> **최종 수정일**: 2026-04-27  
> **문서 해시**: SHA256:7541cf009730f780b09bc07125eaa5834d9f9512d8aae57e3583ad5ba1a3fe54  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---

## 1. 용도

비교표, 그림, **리포트 Markdown/PDF**.

## 2. 담지 않는 것

미검증 가설을 확정 사실처럼 루트 문서에 붙이지 않는다.

## 3. 산출·연계

결론이 제품에 반영되면 `PRD.md`·`EVALUATION.md`를 갱신.

---

## 4. 하위 리포트 폴더

작업별 리포트는 `yyyy-mm-dd_<topic>/` 형식의 하위 폴더로 관리한다.

| 하위 폴더 | 내용 |
|---|---|
| `2026-04-27_isolation_survey_design/` | 앱 진입 설문 12문항 선정 + 위험도 1~5단계 스코어링 설계. 서울시 고립은둔청년 실태조사 cross-tab 통계 분석, Cohen's h·JS divergence 변별력 랭킹, 시뮬레이션 기반 컷오프(AUC 0.99). 12문항·점수·가중치는 후속 `FEATURE_SPEC.md`/`risk_stage_service` 입력 후보. (`00_README.md` 참고) |

## 5. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.
