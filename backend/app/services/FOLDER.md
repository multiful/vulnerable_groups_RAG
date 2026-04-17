# FOLDER.md

> **파일명**: FOLDER.md
> **최종 수정일**: 2026-04-17
> **문서 해시**: SHA256:TBD
> **문서 역할**: 백엔드 비즈니스 로직 서비스 계층 설명
> **연계 경로**: backend/app/api/v1/routes/

## 1. 개요
이 폴더는 애플리케이션의 핵심 비즈니스 로직을 처리하는 서비스 클래스들을 포함합니다. API 엔드포인트에서 전달된 요청을 처리하고, 데이터베이스(Supabase) 또는 로컬 파일(CSV, JSONL)과 상호작용합니다.

## 2. 주요 파일
- `recommendation_service.py`: 위험군 및 관심사 기반 자격증 추천 및 로드맵 조립 로직.
- `risk_stage_service.py`: 위험군 단계 정보 조회.
- `retrieval_service.py`: LangChain 기반의 RAG Evidence 검색 로직.
- `metadata_service.py`: 데이터 메타데이터 관리 및 조회.

## Audit Findings (by Gemini CLI) - 2026-04-17
- **Issue**: `recommendation_service.py`의 `_filter_candidates` 내 `_match` 함수 로직이 불명확함. `domain_ids`가 비어있고 `job_ids`만 있는 경우 필터링 결과가 의도치 않게 누락될 가능성이 있음.
- **Issue**: 위험군 2~4단계에 대한 로드맵 차별화 로직이 `starting_roadmap_id` 결정 외에는 부족함. 단계별 난이도 조절이나 추천 개수 조정 등의 정책 반영이 필요함.
- **Required Action**: `_match` 함수의 조건문을 `(domain_match OR job_match)` 형태로 명확히 리팩토링할 것.
- **Required Action**: `risk_stage_id`에 따른 추천 가중치(`_score` 함수) 고도화 계획을 수립할 것.
- **Required Action**: `_build_roadmap` 함수에서 자격증 간의 선후 관계(`cert_to_cert_relation.csv`)를 탐색하여, "A -> B -> C" 형태의 시퀀스 트랙을 생성하는 기능을 추가할 것. 단순 그룹화(Group by Stage)를 넘어 연결선(Edge)을 포함한 로드맵 UI용 데이터를 반환해야 함.

## Audit Findings (by Gemini CLI) - 2026-04-17 (Roadmap Inversion Issue)
- **Issue**: 추천 결과에서 난이도가 높은 자격증(SQLP, 합격률 20%)이 더 쉬운 자격증(빅데이터분석기사, 55%)보다 앞 단계에 배치되는 '난이도 역전' 현상 발생.
- **Issue**: 로드맵 스테이지 순서가 `0004 -> 0003 -> 0004`와 같이 단조 증가하지 않고 역행하는 로직 오류 식별.
- **Required Action**: `recommendation_service.py`의 `_score` 및 정렬 로직을 수정하여 `(stage_order, level_score, -pass_rate)` 순으로 정렬함으로써 로드맵의 단조 증가와 난이도 순차성을 보장할 것.
- **Required Action**: 합격률 기반 난이도 임계값(Threshold)을 재설정(예: 50% / 30% / 10%)하여 위계 구조를 명확히 할 것.


