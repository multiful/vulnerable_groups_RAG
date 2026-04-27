# backend/README.md

> **파일명**: backend/README.md  
> **최종 수정일**: 2026-04-27  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 백엔드 실행·개발 안내 + 현행 파이프라인 병목 리스트  
> **문서 우선순위**: reference  
> **연관 문서**: DIRECTORY_SPEC.md, API_SPEC.md, PROJECT_SUMMARY.md, DEV_LOG.md, FEATURE_SPEC.md, RAG_PIPELINE.md  
> **참조 규칙**: 진입점은 `backend/app/main.py` 이다. import 경로는 저장소 루트를 `PYTHONPATH`에 둔 뒤 `backend.app` 패키지를 사용한다. 병목 리스트(§"파이프라인 병목")는 운영 관찰 기록이며, 정책·기능 변경은 루트 문서(`PRD.md` / `FEATURE_SPEC.md` 등)를 먼저 갱신한 뒤 본 문서로 동기화한다.

---

## 실행

저장소 루트에서:

```bash
pip install -r backend/requirements.txt
set PYTHONPATH=%CD%
uvicorn backend.app.main:app --reload
```

PowerShell:

```powershell
pip install -r backend/requirements.txt
$env:PYTHONPATH = (Get-Location).Path
uvicorn backend.app.main:app --reload
```

헬스 확인: `GET http://127.0.0.1:8000/api/v1/health`

## 환경 변수

템플릿: [`infra/env/.env.example`](../infra/env/.env.example)  
저장소 루트 또는 `backend/` 에 `.env` 를 두면 `load_dotenv()` 가 읽는다.

- `CORS_ORIGINS`: 쉼표 구분 (Vite `http://localhost:5173`, Vercel 도메인)
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`: 팀 pgvector 프로젝트 (클라이언트에 노출 금지)
- `EMBEDDING_PROVIDER`: `openai` | `huggingface`
- `OPENAI_API_KEY` 또는 HF 모델(`HF_EMBEDDING_MODEL`)

Supabase 테이블·`match_documents` RPC 는 [`docs/architecture/supabase_langchain.sql`](../docs/architecture/supabase_langchain.sql) 를 실행한다.

## RAG 인제스트 (오프라인)

`data/index_ready/chunks/chunks.jsonl` 이 있을 때(사용자 생성 산출물). 형식은 `chunks.jsonl.example` 참고.

```bash
set PYTHONPATH=%CD%
python -m backend.rag.ingest.cli
```

청크·Evidence·후보 데이터 계약은 루트 `PROJECT_SUMMARY.md` §8·§9, `DATA_SCHEMA.md`, `API_SPEC.md`를 본다.

`POST /api/v1/recommendations`는 현재 `NOT_IMPLEMENTED` 스텁이다. 후보 행 형식은 `DATA_SCHEMA.md` §9.1·`data/canonical/candidates/candidates.jsonl.example` 참고.

## Evidence API

`POST /api/v1/recommendations/evidence` — Supabase 미설정 시 `evidence: []` 로 성공 응답.

## 테스트

```bash
set PYTHONPATH=%CD%
pytest backend/tests -q
```

---

## 파이프라인 병목

> 본 절은 2026-04-27 기준 코드·문서 정합성 점검에서 식별한 **현행 파이프라인 병목**을 우선순위 라벨과 함께 정리한 운영 메모다. 본 절은 **정책 결정 문서가 아니다.** 항목별 수정은 반드시 관련 루트 문서(`PRD.md` / `FEATURE_SPEC.md` / `SYSTEM_ARCHITECTURE.md` / `RAG_PIPELINE.md` / `DATA_SCHEMA.md`)를 먼저 갱신한 뒤 코드·테스트로 내려간다. 우선순위 라벨은 `P0`(차단/요구사항 미충족), `P1`(상시 노출되는 결함), `P2`(데이터·정책 확정 대기), `P3`(품질·관측성 부채) 4단계.

### B-01 [P0] 위험군 자동 스코어링 부재
- **현황**: A7 외출 빈도, A8 은둔 기간, A9 과거 은둔, A10~A15 사회적 교류·고립, A18 외로움(UCLA), B12 우울(PHQ), B1 생활패턴, B2 수면, B7 식사, B9 자기관리, C1~C4 회복 의지/지원 9개 지표 → `risk_0001`~`risk_0005` 매핑 산출 로직이 코드/CSV/문서에 모두 없다.
- **증거**: `backend/app/services/risk_stage_service.py` 는 `risk_stage_master.csv` 메타 조회만 수행. `frontend/src/pages/RiskAssessment/index.tsx` 는 사용자가 1~5단계를 직접 라디오로 고르는 형태. 설문 원본 CSV(서울 고립·은둔 청년 실태조사)는 `data/raw/csv/`에 미적재.
- **영향**: F-01 위험군 기반 추천 진입의 입력 단계가 사실상 **수동 자기 진단**에 의존. 추천 결과의 개인화 근거가 사라지고 evaluation persona(P01~P21)와 실서비스 입력 분포가 괴리된다.
- **다음 단계**: ① 설문 CSV → canonical(`survey_response`) 정의를 `DATA_SCHEMA.md`에 신설. ② 9개 지표별 컷오프·가중치를 `FEATURE_SPEC.md` F-01 처리 규칙에 추가(2~4단계 의미는 `PRD.md` §17 오픈 이슈와 함께 확정). ③ `risk_score_service.py` 신규 + 단위테스트 + 골든 페르소나 6건과 매칭.

### B-02 [P0] `major_name` → `domain_sub_label_id` 매칭이 정확 일치만 지원
- **현황**: `recommendation_service._load_major_to_domain_map()`은 `normalized_key` 또는 `major_name` 의 **strict lower-case 일치**만 사용. `major_master.csv`에 등록된 5,200여 학과 중 사용자가 입력하는 자유 텍스트(예: "산업데이터공학과", "전자공학과")가 **그대로 일치하지 않으면 domain 보강 실패**.
- **증거**: `data/processed/master/major_master.csv` 검색 결과 `전자공학` 단어가 들어간 `major_qnet_*` 행은 다수지만 정확히 "전자공학"만으로는 normalized_key 일치 없음. "산업데이터공학"은 master에 부재(신생 학과명).
- **영향**: 사용자 시나리오 ②③(전자공학과/산업데이터공학과)에서 `domain_ids=[]` 로 fallthrough → `recommendations()` 가 `risk_stage_id` 단독 필터로 회귀, 도메인 personalization 손실.
- **다음 단계**: ① `major_alias.csv` 도입(루트 `DATA_SCHEMA.md` §6에 정식 등록). ② normalized_key의 부분 일치/접미사 정규화(`-과/-학과/-전공/-부` 제거). ③ "산업데이터공학"처럼 미등록 학과는 admin tool 또는 build pipeline에서 제안 후 운영자 confirm 단계 추가.

### B-03 [P0] 자유 텍스트 쿼리 → 추천 입력 정규화 계층 부재
- **현황**: `POST /api/v1/recommendations`는 `risk_stage_id`, `domain_ids|domain_names`, `job_ids`, `major_name`, `held_cert_ids` 만 수용. "컴퓨터, IT 관련 로드맵" 같은 자유 텍스트를 `domain_ids`(domain_0001~_0004)로 mapping해주는 NLU/router가 없다.
- **증거**: `backend/app/api/v1/routes/recommendation.py` 는 body를 그대로 `recommendations_placeholder`에 위임. 프론트(`Recommendation/index.tsx`)도 form 입력만 전송.
- **영향**: 시나리오 ③("컴퓨터, IT 관련 로드맵") 같은 광범위 키워드는 매핑되지 않아 결국 `risk_stage_id` 단독 추천이 된다. PRD §19.5 "데모에서 LLM 조립 임시 허용" 조항도 입력 정규화 계층이 있어야 안정.
- **다음 단계**: ① `query_router_service` 추가(키워드 → domain_ids 사전 + alias 사전). ② `domain_master.csv`의 `domain_top_label_name` ("IT/디지털") 단위 매칭 허용. ③ taxonomy 밖 라벨 차단 가드(`canonical/taxonomy_labels.py`) 동일 적용.

### B-04 [P1] `risk_0005` 진입 시 `roadmap_stage_0001/_0002` 콘텐츠 공백
- **현황**: `risk_stage_to_roadmap_stage.csv`는 `risk_0005 → roadmap_stage_0001`. 그러나 `_cert_level()`은 기능사를 모두 `roadmap_stage_0003` 이상으로 올리고, 비기술자격도 `roadmap_stage_0002` 이상에 떨어뜨려 stage_0001/stage_0002에 cert 0건이 빈번하다.
- **증거**: `data/canonical/relations/FOLDER.md` §5.3 "roadmap_stage_0001/0002 공백" 메모 + 골든셋 P21 평가에서 N5 미해결로 명시.
- **영향**: 5단계 사용자에게 "오늘 당장 할 수 있는 일" 안내가 비어 있다. 추천 결과는 stage_0003 이상부터 제시되어 PRD §3.4(추천 결과가 다음 행동으로 이어지지 않음) 문제를 부분적으로 재발.
- **다음 단계**: ① 비자격 준비 콘텐츠(생활 회복, 직무 탐색)를 `roadmap_stage_master`에 정식 등록. ② `_PASSRATE_STAGE_MAP`에 ≥60% bucket을 stage_0002로 분리하는 정책 결정(루트 `PRD.md`/`SYSTEM_ARCHITECTURE.md` §17 결정 #8과 일관성 점검).

### B-05 [P1] cross-domain redundancy 미적용 (P15 잔존 결함)
- **현황**: `_build_roadmap_sequence`는 `is_redundant`를 **동일 domain**에서만 판정. 보유 자격증으로 advanced entry가 `roadmap_stage_0005`로 올라간 사용자에게 다른 domain의 기능사·산업기사가 stage_0005로 clamp되어 노출됨.
- **증거**: `data/canonical/relations/FOLDER.md` §5.3 P15 FAIL 항목.
- **영향**: 추천 결과의 단계 정합성 위반(고급 단계에 하위 tier 혼입) → 사용자 혼란 + 평가 자동화에서 R5 회귀.
- **다음 단계**: `_build_roadmap_sequence`에 `starting_order` 기반 tier 하한 필터를 추가하고, 정책 변경 시 `SYSTEM_ARCHITECTURE.md` §17 결정 #8 갱신.

### B-06 [P1] `primary_domain=domain_unknown` 78건 candidate 게이트 탈락
- **현황**: taxonomy 게이트가 `domain_unknown`을 차단하면서 cert 78건이 `cert_candidates.jsonl`에 진입하지 못함(주로 언어/속기 등 `domain_0028` 계열).
- **증거**: `data/canonical/relations/FOLDER.md` §5.2 N4 항목.
- **영향**: candidate row 1,290건은 실제 cert_master 1,368건 대비 **약 5.7% 누락**. 사용자가 해당 자격을 검색하면 추천 0건.
- **다음 단계**: `cert_domain_mapping.csv` 보강 또는 `DATA_SCHEMA.md §9.1.2`에 `taxonomy_fallback` 정책 신설(언어/속기 카테고리만 한정 허용).

### B-07 [P1] `cert_to_cert_relation` parse_ir 행 224개 비활성
- **현황**: `_extract_parse_ir_evidence`의 키워드 근접성 검증이 미정교하여 노이즈가 많아 parse_ir에서 추출된 224개 row를 `is_active=False`로 격리.
- **증거**: `data/canonical/relations/FOLDER.md` §5.3 N1 항목.
- **영향**: NCS 기반 775개 edge에만 의존 → DAG 경로(cert_paths) 다양성 저하. 일부 도메인(예: 디자인, 콘텐츠)에서 `cert_paths=[]` 빈도가 높다.
- **다음 단계**: ① 키워드 window ±80자, cert 이름 간 거리 ≤50자 등 N1 재설계 spec 반영. ② 수작업 샘플 20건 검증 후 단계적 활성화.

### B-08 [P1] Evidence retrieval과 추천 결과 결합의 단일 경로
- **현황**: `retrieval_service.search_evidence`는 Supabase pgvector dense 단독. reranker/BM25는 `# TODO reserved` 상태(`backend/app/services/retrieval_service.py`). LangChain HuggingFace embedding 사용 시 cold start latency가 크고, Supabase 미설정 시 `evidence:[]`로 무성공 응답이 항상 반환되어 디버깅이 어렵다.
- **증거**: `backend/app/services/FOLDER.md` Audit Findings + 본 README "Evidence API" 절.
- **영향**: F-04 추천 이유/근거 조회의 신호 강도가 낮아 PROMPT_DESIGN의 "근거 없으면 사실 생성 금지" 가드와 충돌하기 쉬움 → 사용자에게 빈 근거가 자주 노출.
- **다음 단계**: ① Supabase 미설정 응답을 `degraded` 메타로 구분. ② `RAG_PIPELINE.md`에 reranker/BM25 활성 조건(SLA, 코퍼스 크기) 명문화 후 실험 분기 분리.

### B-09 [P2] 위험군 2~4단계 세부 정책 미확정 (`_RISK_TIER_MIN` 임계값 임시값)
- **현황**: `_RISK_TIER_MIN`(기능사 제외 threshold)이 `risk_0001=20`, `risk_0002=15`, 나머지 `=10`로 하드코딩. 이 임계값에 대한 정책 근거가 `PRD.md`/`SYSTEM_ARCHITECTURE.md`에 명시되지 않음.
- **증거**: `recommendation_service.py` L106~112 + `PRD.md` §17 오픈 이슈 #1.
- **영향**: 정책이 바뀌면 모든 페르소나 골든셋이 흔들린다. 임계값 변경 PR마다 추천 결과 재합의가 필요.
- **다음 단계**: 위험군 2~4단계 의미와 함께 tier 하한 임계값을 정책 문서로 승격. 임시값임을 코드 docstring에 명시.

### B-10 [P2] 추천 응답에 LLM 자연어 조립 단계 부재
- **현황**: `recommendations()` 응답은 candidate row + roadmap sequence + cert_paths + raw `text_for_dense`를 그대로 반환. PRD §19.2 D5 "LLM 조립 레이어"가 미구현.
- **증거**: `recommendation_service.py` 응답 envelope에 자연어 요약 hook 없음. `backend/rag/prompts/`는 `__init__.py` 단일 파일.
- **영향**: 사용자에게 "이 자격증이 왜 적합한가"를 즉시 보여주지 못함 → PRD §3.1 문제 미해결. 데모 시연에서도 별도 GPT 호출이 필요.
- **다음 단계**: `PROMPT_DESIGN.md` 입력 슬롯 정의 → `prompts/` 모듈에 단일 호출 함수 추가 → 응답 envelope에 `summary_text` 필드 신설(`API_SPEC.md` 갱신 동반).

### B-11 [P2] CSV 캐시 stale 위험 (`_invalidate_caches` 수동 호출 의존)
- **현황**: `_load_*` 들이 모두 `lru_cache(maxsize=1)` + 파일 직접 read. 운영자가 master/relation csv를 교체해도 `reload_from_changed_jsonl()`을 명시적으로 호출하지 않으면 서비스 캐시는 그대로 유지된다.
- **증거**: `recommendation_service.py` L826~841 `_invalidate_caches`.
- **영향**: F-06/F-07 운영자 갱신 흐름이 자동으로 추천 응답에 반영되지 않음. 무중단 배포 환경에서 stale 응답 가능.
- **다음 단계**: ① mtime/sha 기반 캐시 무효화 또는 ② startup 시 manifest hash 비교 + reload endpoint 노출. `HASH_INCREMENTAL_BUILD_GUIDE.md` §3 캐시 키 설계와 연계.

### B-12 [P3] 오프라인 인덱스 빌드 자동화/관측성 부족
- **현황**: `python -m backend.rag.ingest.cli`는 수동 실행 의존. parser/chunker/embedding version 표기가 manifest에 들어가는지 항상 보장되지 않으며, `print()` 기반 로그가 다수(`scripts/*.py`, `backend/rag/pipeline/runner.py`).
- **증거**: 루트 `FOLDER.md`의 "print → logging" 검토 항목.
- **영향**: 빌드 실패/지연 시 원인 추적 어려움. CLAUDE.md §12 증분 빌드 원칙(`input_hash + rule_version`) 준수 여부를 자동으로 확인하기 어렵다.
- **다음 단계**: 표준 `logging` 채택 + 빌드 manifest에 `ingest_version`, `chunk_version`, `embedding_version`, 입력 file_hash 강제 기록. CI에서 manifest schema 검증.

---

### 시나리오별 현재 동작 추적 메모

요청한 3개 시나리오를 코드 흐름상으로 추적한 결과(실서버 미실행, 정적 분석):

| 시나리오 | 입력 매핑 결과 | 예상 동작 | 주요 병목 |
|---|---|---|---|
| 2단계, 전자공학과 학생 — "취업 로드맵 제안해줘" | `risk_stage_id=risk_0002`. `major_name="전자공학"` 은 `_load_major_to_domain_map`에서 strict 일치 실패 가능성 큼 → `domain_ids=[]` 로 진입. 자유 텍스트 "취업 로드맵"은 NLU 부재로 무시. | `tier_min=15` 적용된 risk_0002 후보 전체에서 `recommended_risk_stages` 일치만으로 정렬. 도메인 personalization 미작동. | B-02, B-03, B-09 |
| 3단계, 산업데이터공학과 졸업생 | `major_master.csv`에 "산업데이터공학" 학과 부재. `_load_major_to_domain_map` 실패. `risk_0003` 단독 필터로 회귀. | risk_0003 매핑 candidate 전체가 stage_order×level_score로 정렬되어 반환. 데이터/AI(domain_0001) 자격이 우선 노출되지 않음. | B-02, B-03 |
| 5단계, "컴퓨터, IT 관련 로드맵 제안해줘" | `domain_names=["컴퓨터/IT"]`로 들어와도 domain_master에 정확히 일치하는 라벨 없음. domain_0001~_0004 중 하나로 매핑하는 라우터 없음. fallback으로 `risk_0005` direct 매핑이 narrow하면 `domain_only` fallback 후 fallback_used=true. | risk_0005 + fallback 동작 시 `roadmap_stage_0001/_0002` 공백 문제(B-04)와 합쳐져 stage_0003 이상부터만 결과 표시. | B-03, B-04 |

각 시나리오의 실제 응답 검증은 `scripts/eval_golden_set.py` 와 동일 형식으로 페르소나(예: `P_demo_risk2_elec`, `P_demo_risk3_ind_data`, `P_demo_risk5_it`)를 추가하고 `docs/evaluation/golden_set.jsonl`에 expected_cert_ids를 동결한 뒤 자동 비교하는 것을 권장한다.
