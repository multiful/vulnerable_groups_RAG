# PROJECT_SUMMARY.md

> **파일명**: PROJECT_SUMMARY.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 저장소 한눈에 보기 — 목적·구조·문서 지도·청킹 개요  
> **문서 우선순위**: reference (세부 계약·스키마는 각 전용 문서가 우선)  
> **연관 문서**: README.md, PRD.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, DIRECTORY_SPEC.md  
> **참조 규칙**: 제품 범위·파이프라인 세부가 바뀌면 본 문서를 같은 턴에서 갱신한다.

---

## 1. 이 프로젝트가 하는 일

청년 **위험군 단계**(1~5단계)와 **관심 직무·도메인(taxonomy)** 을 입력으로, **자격증 후보**와 **로드맵**을 구조적으로 추천하고, **PDF/HTML 근거**로 설명(evidence)을 붙이는 시스템을 만든다.

- **구조적 추천**: canonical 데이터(엔티티·관계·candidate row). CSV는 여기로만 간다.
- **RAG**: 추천 엔진이 아니라 **설명 근거 검색** 레이어. PDF/HTML만 Parse→Chunk→Embed 경로.

---

## 2. 두 갈래 데이터 레인 (헷갈리지 않기)

| 레인 | 원본 | 하지 않는 것 | 산출(예) |
|------|------|--------------|----------|
| **CSV / structured** | `data/raw/csv/` | Parse IR·청킹·RAG 인덱스에 넣기 | `data/canonical/*` (영민·유빈 담당 범위는 `CSV_CANONICALIZATION_TEAM_GUIDE.md`) |
| **문서 PDF/HTML** | `data/raw/pdf/`, `data/raw/html/` | CSV처럼 canonical 테이블만으로 대체 | Parse IR → chunk JSONL → 임베딩 → 벡터 스토어 |

---

## 3. 기술 스택 (현재)

| 영역 | 선택 |
|------|------|
| 프론트 | React + Vite (`frontend/`) |
| API | FastAPI (`backend/`) |
| RAG 런타임 | LangChain + Supabase pgvector (`backend/rag/`) |
| 임베딩 | OpenAI 또는 HuggingFace (환경변수) |
| 배포(가정) | Vercel / Railway·Render 등 |

**reserved(문서상 미완으로 다룸)**: 일정·접수·지원 링크 실연동, reranker, BM25 상시, 상담 에이전트, full infra 등 — `PRD.md`·`FEATURE_SPEC.md`와 동일.

---

## 4. 디렉터리 요약

| 경로 | 역할 |
|------|------|
| 루트 `*.md` | 제품·스키마·API·파이프라인 **단일 기준선** |
| `docs/slides`, `docs/references`, `docs/architecture`, `docs/meeting_notes` | 발표·**긴 기법 문서**·구조도·회의록 |
| `data/raw/` | 원본 (pdf/html/csv/api) |
| `data/taxonomy/` | 허용 도메인·직무 라벨 (`domain_v2.txt`, `prefer_job.txt`) |
| `data/canonical/` | 엔티티·관계·후보·검증 산출 |
| `data/index_ready/chunks/` | **RAG용 청크 JSONL** (한 줄 = 한 청크) |
| `backend/` | FastAPI, RAG, canonical 코드 |
| `frontend/` | UI |
| `scripts/` | parse / canonicalize / build_* 등 배치 진입 |
| `experiments/`, `infra/`, `shared/` | 실험·배포·공용 타입 |

상세는 `DIRECTORY_SPEC.md`.

---

## 5. 문서 지도 (무엇을 먼저 읽나)

| 순서 | 문서 | 한 줄 |
|------|------|--------|
| 0 | `README.md` | 입구 |
| 1 | `CHANGE_CONTROL.md` | 문서 수정 규칙 |
| 2 | `PRD.md` | 문제·범위 |
| 3 | `SYSTEM_ARCHITECTURE.md` | 계층·흐름 |
| 이후 | `FEATURE_SPEC`, `DATA_SCHEMA`, `API_SPEC`, `PROMPT_DESIGN`, `RAG_PIPELINE`, `DIRECTORY_SPEC` | 작업 주제별 |
| 팀 CSV | `CSV_CANONICALIZATION_TEAM_GUIDE.md` | 영민·유빈 |
| 탐색 | `ROOT_DOC_GUIDE.md` | 문서 목록 안내 |

---

## 6. 청킹(Chunking) 단계 — 이 프로젝트에서 어떻게 하면 되나

### 6.1 전제

- 청킹 입력은 **CSV가 아니라 Parse 산출물(구조 보존 IR 또는 이에 준하는 중간 표현)** 이다.  
- Parse에서 **reading order·표 경계**가 무너지면, 청킹만으로는 회복이 어렵다 (`RAG_PIPELINE.md` Parse·Chunk 연결).

### 6.2 기준 문서

모든 규칙의 원본은 **`RAG_PIPELINE.md` §7 Chunk Layer**, §8 Metadata Layer 이다. 요약만 여기 적는다.

### 6.3 문서 유형별 전략 (프로젝트 고정안)

| 유형 | 청킹 방식 (`RAG_PIPELINE.md`) |
|------|--------------------------------|
| 안내·FAQ·설명형 (HTML/가이드) | **Markdown-aware**: heading propagation, 문단 의미 단위, 과도한 길이 확장 금지 |
| 표 중심 | **Block chunking**: 표/리스트/단락을 한 청크에 섞지 않음, block 경계 유지 |
| Parent–Child | **선택·MVP 비필수** (reserved 성격으로 단계적 도입) |

### 6.4 메타데이터 (청크마다 최소한)

`doc_id`, `chunk_id`, `source_type`, `doc_type`, `section_path`, `source_loc`, `chunk_hash`, `valid_from` / `valid_to`, `doc_version`  
선택: `cert_id`, 직무·도메인·위험군·기관 등 (`RAG_PIPELINE.md` §8).

### 6.5 이 저장소에서의 **실행 순서** (구현 관점)

1. **Parse** 완료 → IR 또는 정규화된 블록 시퀀스 확보.  
2. **Chunk builder** 실행: 위 §6.3 규칙에 따라 텍스트를 자르고 메타를 붙인다.  
3. **산출 파일**: `data/index_ready/chunks/chunks.jsonl` (또는 팀이 정한 동등 경로).  
   - 한 줄 = JSON 한 객체. 스키마는 `backend/rag/ingest/chunk_loader.py` 주석과 맞출 것 (`text`/`content`, `chunk_id`, `doc_id`, `metadata.cert_id` 등).  
4. **인제스트**: `python -m backend.rag.ingest.cli` (환경변수·Supabase 스키마는 `docs/architecture/supabase_langchain.sql`, `backend/README.md`).  
5. **버전**: `chunk_version` / `chunk_hash` 규칙은 `HASH_INCREMENTAL_BUILD_GUIDE.md` — 규칙이 바뀌면 버전 올리고 선택적 재처리.

### 6.6 심화 기법 문서와의 관계

아래 §7에 두는 **Indexing 고도화 가이드**처럼 긴 글에는 토큰·overlap·semantic chunking·Parent-Child·운영 런북 등이 실무 수준으로 나온다.  
**이 프로젝트에서 우선할 것**: `RAG_PIPELINE.md` + `CHANGE_CONTROL`의 reserved 규칙(BM25 상시·reranker 등).  
심화 문서는 **참고·실험 설계**용이며, 제품 기준선을 바꿀 때는 `RAG_PIPELINE.md`를 먼저 고친다.

---

## 7. 긴 기법·방법론 문서는 어디에 두나

`DIRECTORY_SPEC.md` 기준:

| 위치 | 넣기 좋은 것 |
|------|----------------|
| **`docs/references/`** | 논문·블로그·**엔터프라이즈 RAG Indexing 가이드**처럼 **일반론·레퍼런스**가 긴 Markdown. 붙여넣은 *Advanced RAG: Indexing 고도화…* 같은 문서 전체는 여기 파일명 예: `docs/references/advanced_rag_indexing_guide.md` |
| **`docs/architecture/`** | **이 저장소 전용** 다이어그램·시퀀스·“우리 파이프라인 결정” 요약 (슬라이드 PNG와 짝지은 짧은 설명 등) |
| **`docs/slides/`** | 발표용 원본 |
| **`docs/meeting_notes/`** | 회의·의사결정 |

**루트에는 두지 않는 것을 권장**: 루트는 `CHANGE_CONTROL`이 정한 **기준선 md**만 두고, 수십~수백 KB 방법론은 `docs/references/`로 분리하면 목록이 깨끗해진다.

**Git**: PNG·대형 MD도 `.gitignore`에 특별 제외가 없으면 일반적으로 추적 가능. 팀 공유용이면 `docs/references/`에 두고 `git add` 하면 된다.

---

## 8. 현재 구현 단계 (요약)

- FastAPI 헬스·evidence API 스켈, LangChain→Supabase 인제스트 CLI 존재.  
- **Parse→Chunk 자동 파이프라인**은 스크립트 수준에서 **후속 구현** (HTML DOM / PDF 라우터 등은 `RAG_PIPELINE.md`·슬라이드와 맞춰 확장).  
- 추천 본체 API·canonical 빌드는 문서·스키마 대비 **단계적 구현**.

---

## 9. 한 페이지 결론

1. **CSV** → canonical까지 (청킹 없음).  
2. **PDF/HTML** → Parse → **Chunk(`RAG_PIPELINE` §7)** → JSONL → Embed → Store.  
3. **법적·계약 기준**은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`.  
4. **긴 방법론**은 `docs/references/` (또는 아키텍처 전용 요약은 `docs/architecture/`).
