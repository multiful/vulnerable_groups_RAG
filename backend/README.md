# backend/README.md

> **파일명**: backend/README.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 백엔드 실행·개발 안내  
> **문서 우선순위**: reference  
> **연관 문서**: DIRECTORY_SPEC.md, API_SPEC.md, DEV_LOG.md  
> **참조 규칙**: 진입점은 `backend/app/main.py` 이다. import 경로는 저장소 루트를 `PYTHONPATH`에 둔 뒤 `backend.app` 패키지를 사용한다.

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

`data/index_ready/chunks/chunks.jsonl` 이 있을 때(사용자 생성 산출물):

```bash
set PYTHONPATH=%CD%
python -m backend.rag.ingest.cli
```

## Evidence API

`POST /api/v1/recommendations/evidence` — Supabase 미설정 시 `evidence: []` 로 성공 응답.

## 테스트

```bash
set PYTHONPATH=%CD%
pytest backend/tests -q
```
