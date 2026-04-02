# DEV_LOG.md

> **파일명**: DEV_LOG.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:657997bccfb2aa996420723b6fd1624934d43686da25f0041cf15f43c88484eb  
> **문서 역할**: 날짜별 진행 로그, 변경 요약, 해결 이력  
> **문서 우선순위**: 14  
> **연관 문서**: CHANGE_CONTROL.md, PRD.md, DIRECTORY_SPEC.md, ERROR_ANALYSIS.md  
> **참조 규칙**: 구조·스캐폴딩·중요 결정은 날짜 역순으로 짧게 남긴다. 상세 실패 분석은 `ERROR_ANALYSIS.md`로 옮길 수 있다.

---

## 1. 문서 목적

구현과 문서 정렬 작업의 **타임라인**을 남겨, 이후 기여자가 맥락을 잃지 않게 한다.

---

## 2026-04-03 — RAG 보완(문서만): Parse 순서·IR 계약·평가 후보

### 수행

- **`RAG_PIPELINE.md`**: §6.0 Parse 실행 순서, §6.7 parse IR 최소 계약(청크 빌더 입력), §10.3 스토어 구현 vs 계약 구분, §13.3 질의 확장 reserved(MVP 비적용 명시), §15 reserved에 코퍼스 감사·rate limit 후보.
- **`DATA_SCHEMA.md`**: `SourceDocument`에 `file_hash`·`fetched_at`, §5.6·§11과 `RAG_PIPELINE` §6.7 역할 분리 명시, 메타데이터 블록에 `문서 해시` 줄 추가.
- **`EVALUATION_GUIDELINE.md`**: §4 Parse·인덱스 품질 측정 후보 표(채택 전).

### 비적용(의도적)

- HyDE·다단계 pre-retrieval·vendor 전환 등은 제품 목적·MVP 범위 밖이거나 별도 계약 필요 → 문서에 **reserved/후속**만 명시.

---

## 2026-04-03 — RAG 심화 참고(로컬) 정리

- 루트 문서: 인덱싱·Pre-retrieval **축 설명**만 유지, **특정 파일명·경로**는 적지 않음. 계약은 `RAG_PIPELINE.md` 우선, reserved는 범위 자동 확장 금지.
- `.gitignore`: `docs/references/_private/` 무시(개인·팀 미공유 참고 자료용).

---

## 2026-04-03 — `.cursor` Git 추적 제거

- 원인: `.gitignore`에 `.cursor/`가 있어도 **이미 한 번 커밋된 경로**는 계속 추적됨.
- 조치: `git rm -r --cached .cursor` 후 커밋 — 원격 반영은 `git push` 필요. 로컬 `.cursor/` 파일은 유지.

---

## 2026-04-03 — 데모 제출용 임시 절 (PRD §19, FEATURE_SPEC §11)

### 수행

- **PRD.md**: `문서 해시` 줄 추가; **§19 데모 제출용 범위·단계 (임시)** — 목적, 최소 시연 흐름, 얇게 둘 항목, D1~D6 체크리스트, 데모 완료 조건, 제출 후 조치.
- **FEATURE_SPEC.md**: `문서 해시` 줄 추가; **§11 데모 제출용 기능 단계 (임시)** — 단계·F-xx 매핑, 허용 스텁, 금지, 제출 후 정리.

---

## 2026-04-03 — 리프 폴더 `FOLDER.md` 스캐폴드 명시서

### 수행

- **`FOLDER.md`**: `docs/`, `data/`(리프), `frontend/src/`(리프), `scripts/*`, `experiments/*`, `infra/*`, `shared/*`, `data/taxonomy` 등 **63개** 리프 경로에 동일 메타데이터 양식(루트 md와 계열)으로 용도·금지·연계·비고 기술.
- **`scripts/maintenance/generate_folder_md.py`**: 위 경로 일괄 생성기. 저장소 루트는 `DIRECTORY_SPEC.md` 존재로 탐색.
- **`DIRECTORY_SPEC.md`**: §7 원칙 8번·§8 요약에 `FOLDER.md` 규칙 반영.

---

## 2026-04-03 — PROJECT_SUMMARY 및 청킹·레퍼런스 문서 위치 안내

### 수행

- **신규** `PROJECT_SUMMARY.md`: 프로젝트 목적, CSV vs 문서 레인, 스택·폴더 요약, 문서 지도, 청킹 절차(`RAG_PIPELINE.md` §7 연계, `chunks.jsonl`·인제스트 CLI), 긴 방법론 문서는 `docs/references/` 권장.
- **README.md**, **DIRECTORY_SPEC.md** §2·§3, **ROOT_DOC_GUIDE.md** §3·§4.1: `PROJECT_SUMMARY.md` 링크·트리 반영.

---

## 2026-04-03 — 문서·디렉터리 정렬 및 최소 스캐폴딩

### 수행

- **DIRECTORY_SPEC.md**: §2 루트 트리에 `ROOT_DOC_GUIDE.md`, `HASH_INCREMENTAL_BUILD_GUIDE.md` 추가; §3에 해당 파일 역할 및 Cursor 규칙(`.cursor/rules/`) 안내; §5 권장 루트 파일 목록 동기화; 문서 해시 라인 추가.
- **신규 루트 문서**: `EVALUATION_GUIDELINE.md`(10), `EVALUATION.md`(11), `EXPERIMENT_GUIDE.md`(12), `ERROR_ANALYSIS.md`(13), `DEV_LOG.md`(14) — 메타데이터 및 `SHA256:TBD`.
- **README.md**: 문서 해시 라인; §5 표에 `ROOT_DOC_GUIDE`, `HASH_INCREMENTAL_BUILD_GUIDE`, Cursor 규칙 위치; §7 트리 동기화.
- **Git**: `gitignore` → `.gitignore` 로 이름 정리(내용 유지).
- **디렉터리**: `docs/*`, `data/raw|canonical|index_ready|processed` 하위(기존 `data/taxonomy/*.txt` 유지), `experiments/*`, `infra/*`, `shared/*` — 비어 있는 leaf에는 Git 추적용 `.gitkeep`만 둠(데이터 파일 아님).
- **frontend**: `DIRECTORY_SPEC` §4.3 트리 + 각 leaf `.gitkeep`, `frontend/README.md`(후속 Next/Vite 안내).
- **backend**: FastAPI `backend.app.main:app`, `/api/v1/health` 활성(envelope 준수); `recommendations`/`roadmaps`/`admin`/`risk/stages`는 `NOT_IMPLEMENTED` envelope; 일정·링크 라우트는 HTTP **501** + envelope; `backend/rag/*`, `backend/canonical/*`, `services`, `requirements.txt`, `backend/README.md`, `backend/tests/test_health.py`.
- **scripts**: `parse`, `canonicalize`, `build_entities`, `build_relations`, `build_candidates`, `evaluation`, `maintenance` 각 `run.py` 스텁.

### 검증

- `PYTHONPATH=<저장소 루트>` 기준 `pytest backend/tests -q` — `test_health_ok` 통과.

### 의도적으로 하지 않은 것

- `risk_stage_master.csv` 및 기타 원본·taxonomy 파일의 임의 생성·더미 row
- raw PDF/HTML/CSV/API 실파일 추가
- reranker, BM25 상시, 일정 API 실연동, 프론트 완성 UI
- `docs/references` 내 참고 자료는 사용자 수동 배치

---

## 2026-04-03 — 스택 정렬 (Vite·LangChain·Supabase·파이프라인 연결)

### 수행

- **프론트**: React 19 + Vite 6 + TS — `frontend/package.json`, `vite.config.ts`(`/api`→8000 프록시), `src/` 홈에서 헬스 호출.
- **백엔드**: `pydantic-settings` 기반 `backend/app/core/config.py`, CORS, `POST /api/v1/recommendations/evidence` + `retrieval_service` + LangChain `SupabaseVectorStore` 경로(`backend/rag/store/supabase_vector.py`).
- **인제스트**: `backend/rag/ingest/chunk_loader.py`, `python -m backend.rag.ingest.cli` (JSONL만 사용, 더미 데이터 생성 없음).
- **SQL 템플릿**: `docs/architecture/supabase_langchain.sql`.
- **환경 템플릿**: `infra/env/.env.example`; `.gitignore`에 `!.env.example` 예외.
- **LlamaIndex**: `backend/rag/llamaindex/` 자리만.
- **문서**: `RAG_PIPELINE.md` §16.1, `SYSTEM_ARCHITECTURE.md` §2.1 스택 문단, `README.md` §10, `backend/README.md` / `frontend/README.md` 갱신.

### 검증

- `pytest backend/tests` (health + evidence missing cert_id).
- `frontend` `npm run build`.

---

## 2026-04-03 — CSV 담당 팀 지침서

- 루트에 `CSV_CANONICALIZATION_TEAM_GUIDE.md` 추가 (영민·유빈: 데이터 수집 슬라이드·Parse 슬라이드 기준 CSV 레인 전담 절차).
- `README.md` §5 표에 해당 문서 링크 한 줄 추가.
