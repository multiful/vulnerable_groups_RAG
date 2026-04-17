# FOLDER.md

> **파일명**: FOLDER.md
> **최종 수정일**: 2026-04-18
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
- **✅ Resolved (2026-04-18)**: `_domain_job_match` 함수를 `(domain_match OR job_match)` 명확한 OR 조건으로 리팩토링 완료.
- **Deferred**: `risk_stage_id`에 따른 추천 가중치 고도화 — policy 확정 전 reserved.
- **Blocked (data)**: `_build_roadmap` 함수의 cert-to-cert 시퀀스 생성 — `cert_to_cert_relation.csv` 생성(데이터 전처리) 완료 후 착수 가능.

## Audit Findings (by Gemini CLI) - 2026-04-17 (Roadmap Inversion Issue)
- **Issue**: 추천 결과에서 난이도가 높은 자격증(SQLP, 합격률 20%)이 더 쉬운 자격증(빅데이터분석기사, 55%)보다 앞 단계에 배치되는 '난이도 역전' 현상 발생.
- **Issue**: 로드맵 스테이지 순서가 `0004 -> 0003 -> 0004`와 같이 단조 증가하지 않고 역행하는 로직 오류 식별.
- **✅ Resolved (2026-04-18)**: 정렬 키 `(stage_order, level_score, -pass_rate)` 확정, 단조 증가 검증 완료.
- **✅ Resolved (2026-04-18)**: `_PASSRATE_STAGE_MAP` 임계값 `(50/30/10)` 적용.
- **✅ Resolved (2026-04-18)**: `is_bottleneck` 플래그 + `bottleneck_note` 텍스트 (pass_rate < 10%) — sequence/by_stage 양쪽 추가.
- **✅ Resolved (2026-04-18)**: `held_cert_ids` 동적 진입점 + 보유 자격증 결과 제외 구현.
- **✅ Resolved (2026-04-18)**: `major_name` → domain 자동 추가 (major_master + major_to_domain 2단계 join).
- **✅ Resolved (2026-04-18)**: `risk_info` unhashable key 버그 수정.


