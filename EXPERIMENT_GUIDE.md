# EXPERIMENT_GUIDE.md

> **파일명**: EXPERIMENT_GUIDE.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:d3ca2f7e39170ebb2f4f31329d6f5b227fa9e04726947628a6f62c035832dd84
> **문서 역할**: 실험 설정, 파라미터, 재현 방법, 로그 위치 규칙 정의  
> **문서 우선순위**: 12  
> **연관 문서**: EVALUATION_GUIDELINE.md, EVALUATION.md, DIRECTORY_SPEC.md, DEV_LOG.md  
> **참조 규칙**: 새 실험 축을 열 때 설정·재현 절차를 여기에 먼저 적고, 산출물은 `experiments/` 하위에 둔다.

---

## 1. 문서 목적

노트북·스크립트·설정 파일이 흩어져 재현이 불가능해지는 것을 막는다.  
스캐폴딩 단계에서는 디렉터리 규칙만 고정하고, 상세 파라미터는 후속으로 보강한다.

---

## 2. 디렉터리 관례

- 설정: `experiments/configs/`
- 로그: `experiments/logs/`
- 보고: `experiments/reports/`
- baseline 산출물: `experiments/baselines/` (reserved 성격이 강할 수 있음)
- 분석 노트북: `experiments/notebooks/`

---

## 3. 재현 체크리스트 (TODO)

- 커밋 해시 또는 태그
- 사용한 `data/`·모델·embedding 버전
- 스크립트 진입점과 인자
