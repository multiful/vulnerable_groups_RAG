# FOLDER.md

> **파일명**: FOLDER.md
> **폴더 경로**: `experiments/reports/2026-04-27_isolation_survey_design`
> **최종 수정일**: 2026-04-27
> **문서 해시**: SHA256:TBD
> **문서 역할**: 본 리포트 폴더의 디렉터리 스캐폴드 — 파일 목록·역할·외부 연계
> **문서 우선순위**: reference (실험 보고서 폴더 내부)
> **연관 문서**: ../FOLDER.md, 00_README.md, PRD.md, SYSTEM_ARCHITECTURE.md
> **참조 규칙**: 본 폴더에 파일을 추가/제거할 때 본 문서와 `00_README.md` §2 산출물 목록을 함께 갱신한다.

---

## 1. 용도

서울시 고립은둔청년 실태조사(2022) 통계 분석 위에서 **앱 진입 설문 12문항 + 1~5단계 위험도 스코어링 규칙**을 설계한 작업의 산출물 묶음.

상세 입구는 `00_README.md`. 본 문서는 폴더 단위 스캐폴드만 다룬다.

## 2. 파일 목록

### 2.1 보고서 markdown
- `00_README.md` — 본 폴더 입구
- `01_statistical_analysis.md` — 변별력 산출 방법, 138문항 랭킹, 인사이트
- `02_survey_selection_rationale.md` — 12문항 선정 근거
- `03_scoring_design.md` — 점수·가중치·5단계 컷오프
- `04_validation_report.md` — AUC/단계 분포 검증, 한계점

### 2.2 데이터 산출
- `final_survey.csv` — 앱 구현용 12문항 (코드·옵션·점수·가중치·통계 메타)
- `survey_design.json` — `final_survey.csv`의 구조 보존 JSON
- `scoring_cutoffs.json` — 5단계 컷오프와 단계 정의
- `validation_summary.json` — 검증 지표 (AUC, 단계별 비율)
- `discrim_full.json` — 138문항 전체 변별력 메타
- `parsed_survey.json` — 원자료 cross-tab 파싱 결과 (재현·감사용)

### 2.3 시각화
- `figs/` — 분석·검증 시각화 묶음 (`figs/FOLDER.md` 참고)

## 3. 담지 않는 것

- 실제 운영 코드(`risk_stage_service` 등)는 본 폴더에 두지 않는다. 본 폴더의 결과를 입력으로 사용하는 운영 코드는 `backend/app/`에 위치한다.
- 정책적 단계 의미(2~4단계 라벨)는 본 폴더에서 확정하지 않는다. 후보 라벨만 제시하며, 확정은 `PRD.md` §17 오픈 이슈 처리 흐름을 따른다.
- 자격증 추천 로직은 본 폴더 범위 밖. 본 폴더는 그 입력이 되는 위험도 단계 판정만 다룬다.

## 4. 외부 연계

- 입력: `data/raw/csv/★TABLE_서울시 고립은둔청년 실태조사(청년조사)_전체_v1_230127.xlsx`
- 출력 → 후속 인입 후보:
  - `FEATURE_SPEC.md` "진입 설문 화면" 명세 (12문항)
  - `risk_stage_service` 입력 파라미터 (점수·가중치·컷오프)
  - `DATA_SCHEMA.md` `risk_stage` 엔티티 정합성 검토
- 재튜닝 시: 새 날짜 폴더(`yyyy-mm-dd_isolation_score_retune/`)를 만들고 본 폴더는 historical baseline으로 보존.

## 5. 비고

- 본 폴더의 `.json` 산출물은 보고서 재현·감사용이며, 실제 운영 데이터로는 사용하지 않는다(테스트 픽스처 용도로 한정).
- 시각화는 영문 라벨로 작성됐다. 한국어 폰트가 분석 환경에 미설치라 한국어 텍스트는 본 markdown 보고서에 보존됐다.
