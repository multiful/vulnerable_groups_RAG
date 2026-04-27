# FOLDER.md

> **파일명**: FOLDER.md
> **폴더 경로**: `experiments/reports/2026-04-27_isolation_survey_design/figs`
> **최종 수정일**: 2026-04-27
> **문서 해시**: SHA256:TBD
> **문서 역할**: 시각화 산출물 디렉터리 명시서
> **문서 우선순위**: reference
> **연관 문서**: ../00_README.md, ../01_statistical_analysis.md, ../03_scoring_design.md, ../04_validation_report.md
> **참조 규칙**: 시각화 추가/제거 시 본 문서와 상위 `00_README.md` 산출물 목록을 함께 갱신한다.

---

## 1. 용도

본 리포트 폴더(`2026-04-27_isolation_survey_design`)의 통계 분석·스코어링 검증 결과 시각화. 모든 figure는 영문 라벨로 작성됐다(분석 환경에 한국어 폰트 미설치).

## 2. 파일 목록

| 파일 | 산출 단계 | 내용 |
|---|---|---|
| `01_discriminative_power.png` | `01_statistical_analysis.md` §4 | 앱 후보 문항(28개)의 max\|h\| 변별력 랭킹 |
| `02_distributions_iso_vs_non.png` | `01_statistical_analysis.md` §4·`02_survey_selection_rationale.md` §4 | 최종 12문항의 응답 분포 비교 (고립군 n=486 vs 비고립군 n=5027) |
| `03_scoring_validation.png` | `04_validation_report.md` §3.1·3.2 | 점수 분포 히스토그램 + 5단계 컷오프 + ROC 곡선 (AUC 0.99) |
| `04_stage_distribution_by_group.png` | `04_validation_report.md` §3.3 | 1~5단계 분류 결과: 그룹별 비율 |
| `05_item_contributions.png` | `04_validation_report.md` §3.4 | 문항별 평균 가중 기여도 — 어느 문항이 단계 분리를 만드는지 |

## 3. 담지 않는 것

- 한국어 라벨 figure는 본 폴더에 두지 않는다. 한국어 표·텍스트는 상위 보고서 markdown 파일에 보존됐다.
- 실시간 대시보드형 결과물(HTML)은 본 폴더 범위 밖.

## 4. 비고

- figure는 `matplotlib` 기반, 140 DPI PNG로 산출. 재생성 절차는 상위 보고서의 §3·§4를 참조하면 동일 데이터/방법으로 재현 가능.
