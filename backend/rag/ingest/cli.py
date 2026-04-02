# File: cli.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: JSONL 청크 → Supabase pgvector 인제스트 CLI (python -m backend.rag.ingest.cli)
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.app.core.config import get_settings
from backend.rag.ingest.chunk_loader import iter_chunks_jsonl
from backend.rag.store.supabase_vector import create_vector_store, supabase_client_configured


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RAG 청크(JSONL)를 Supabase에 적재")
    parser.add_argument(
        "--chunks-file",
        type=Path,
        default=None,
        help="기본값: 설정의 CHUNKS_JSONL_RELATIVE (저장소 루트 기준)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="chunks 상대 경로 기준 디렉터리 (기본 cwd)",
    )
    args = parser.parse_args(argv)
    settings = get_settings()

    if not supabase_client_configured(settings):
        print("SUPABASE_URL / SUPABASE_SERVICE_KEY 가 없어 인제스트를 건너뜁니다.", file=sys.stderr)
        return 1

    chunks_path = args.chunks_file or (args.project_root / settings.chunks_jsonl_relative)
    if not chunks_path.is_file():
        print(f"청크 파일 없음: {chunks_path}", file=sys.stderr)
        return 1

    docs = list(iter_chunks_jsonl(chunks_path))
    if not docs:
        print("문서 0건 — 내용 없음.", file=sys.stderr)
        return 1

    store = create_vector_store(settings)
    texts = [d.page_content for d in docs]
    metas = [d.metadata for d in docs]
    ids = [str(m.get("chunk_id", f"idx_{i}")) for i, m in enumerate(metas)]
    store.add_texts(texts, metadatas=metas, ids=ids)
    print(f"적재 완료: {len(docs)} chunks → {settings.supabase_table_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
