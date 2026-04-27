# 00_README.md

> **파일명**: 00_README.md
> **최종 수정일**: 2026-04-27
> **문서 해시**: SHA256:1d8e854f55fd15e975058402ad97231c128307662bf4b54de170e74a9a541bb6
> **문서 역할**: 본 리포트 묶음의 입구 — 산출물 목록·작업 목적·후속 활용 안내
> **문서 우선순위**: reference (실험 보고서 폴더 내부)
> **연관 문서**: experiments/reports/FOLDER.md, PRD.md, SYSTEM_ARCHITECTURE.md, FEATURE_SPEC.md
> **참조 규칙**: 본 폴더의 결과를 `PRD.md`·`FEATURE_SPEC.md`·`DATA_SCHEMA.md`로 승격하기 전에 반드시 본 문서의 §3(범위·제약)을 확인한다.

---

## 1. 작업 목적

앱 사용자에게 받을 **고립도 진입 설문 10~15문항**과, 응답을 **위험군 1~5단계**로 매핑하는 **위험도 스코어링 규칙**을, 서울시 고립은둔청년 실태조사(2022) 통계 근거 위에서 설계한다. 본 폴더는 그 통계 분석·문항 선정·스코어링 설계·검증 결과를 한 묶음으로 보관한다.

본 작업은 추천 엔진 자체가 아니라, 추천 엔진의 입력이 되는 **위험군 단계 판정의 통계적 근거**를 만드는 단계다. 추천 로직, 자격증 매핑, 로드맵 단계는 본 작업의 결과물(위험군 단계)을 입력으로 사용하는 별도 모듈에서 다룬다.

## 2. 산출물 목록

| 파일 | 내용 |
|---|---|
| `00_README.md` | 본 문서 — 폴더 입구 |
| `01_statistical_analysis.md` | 원자료 구조, 변별력(Cohen's h, JS divergence) 산출 방법, 138개 문항 랭킹 결과 |
| `02_survey_selection_rationale.md` | 최종 12문항을 선정한 이유 — 문항별 통계 근거(효과크기·비율차) 표 |
| `03_scoring_design.md` | 응답 옵션별 점수, 가중치, 5단계 컷오프 규칙, 가중치 산정 근거 |
| `04_validation_report.md` | 스코어링 검증 결과 — AUC, 단계 분포, 한계와 가정(독립 표본 가정) |
| `final_survey.csv` | 앱 구현용 12문항 데이터 — 옵션별 점수·문항 가중치·통계 메타 포함 |
| `survey_design.json` | `final_survey.csv`의 JSON 버전 (구조 보존용) |
| `scoring_cutoffs.json` | 5단계 컷오프 수치와 단계 정의 |
| `validation_summary.json` | 검증 지표 수치 (AUC, 단계별 비율) |
| `discrim_full.json` | 138개 전체 문항의 변별력 메타 (모든 문항·옵션·iso/non %·Cohen's h) |
| `parsed_survey.json` | 원자료 cross-tab 파싱 결과 (재현·감사용) |
| `figs/01_discriminative_power.png` | 앱 후보 문항의 변별력 랭킹 |
| `figs/02_distributions_iso_vs_non.png` | 12문항 응답 분포: 고립군 vs 비고립군 |
| `figs/03_scoring_validation.png` | 점수 분포 + ROC 곡선 |
| `figs/04_stage_distribution_by_group.png` | 1~5단계 분류 결과: 고립군 vs 비고립군 |
| `figs/05_item_contributions.png` | 문항별 평균 기여도 — 어느 문항이 단계 분리를 만드는지 |

## 3. 범위와 제약

이 작업의 결과는 **고립은둔 차원에 한정된 위험도 판정**이다. PRD §7.1의 위험군 1~5단계 정의 중 "1단계=취업 안정권, 5단계=취업이 어려운 가장 높은 위험군" 양 끝점만 고정된 상태에서, **2~4단계 세부 의미는 본 분석에서도 임의 정의하지 않는다**. 본 폴더의 컷오프는 데이터 분포에서 도출된 후보값이며, 정책적 단계 정의와 만나기 전까지는 reserved 상태로 본다.

원자료는 **이미 cross-tab으로 집계된 표**이다(개인 응답 row가 아님). 이 때문에 §04 검증의 시뮬레이션은 **문항 간 독립** 가정을 사용한다. 실제 응답에는 문항 간 상관이 있으므로, 본 검증의 AUC·단계 분포는 **상한치에 가까운 추정**이며 실제 운영에서는 좀 더 보수적으로 해석해야 한다. 자세한 한계는 `04_validation_report.md` §5를 참고한다.

## 4. 후속 활용

본 폴더의 결과가 제품에 반영되는 흐름은 다음과 같다.

1. `02_survey_selection_rationale.md`의 12문항이 앱 진입 설문 화면 명세로 이동한다 → `FEATURE_SPEC.md` 갱신.
2. `03_scoring_design.md`의 점수·가중치·컷오프가 `risk_stage_service`(`SYSTEM_ARCHITECTURE.md` §7) 입력 파라미터로 인입된다.
3. 단계 출력 스키마는 `DATA_SCHEMA.md`의 `risk_stage` 관련 엔티티와 정합성을 검토한 뒤 결정한다.
4. 본 폴더의 컷오프는 추후 실사용 응답 분포가 모이면 재추정 대상이며, 그때 본 폴더에 새 날짜 폴더로 비교 분석을 추가한다(`experiments/reports/FOLDER.md` 원칙).

## 5. 데이터 출처

- 원자료: `data/raw/csv/★TABLE_서울시 고립은둔청년 실태조사(청년조사)_전체_v1_230127.xlsx` (서울시, 2022, n=5513)
- 비교 그룹: `고립은둔 청년 (n=486)` vs `미해당 (n=5027)` — 원자료에 이미 부여된 라벨 사용
- 팀원 1차 후보 초안: `청년설문실태조사.docx` (사전 제공)
