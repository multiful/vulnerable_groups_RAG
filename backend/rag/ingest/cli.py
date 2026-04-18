# File: cli.py
# Last Updated: 2026-04-18
# Content Hash: SHA256:45683927c9c573451fc7f05d3ae834d4026a9d6478dc67ae43124af7cf864cd6
# Role: JSONL 청크 → Supabase pgvector 인제스트 CLI (python -m backend.rag.ingest.cli)
#       manifest의 embed_key_hash 기준 증분 적재 (RAG_PIPELINE.md §embed 증분 규칙)
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from backend.app.core.config import get_settings
from backend.rag.ingest.chunk_loader import iter_chunks_jsonl
from backend.rag.pipeline.manifest import PipelineManifest
from backend.rag.store.supabase_vector import create_vector_store, supabase_client_configured


DEFAULT_MANIFEST_RELATIVE = Path("data/index_ready/metadata/pipeline_manifest.json")


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
    parser.add_argument(
        "--manifest-file",
        type=Path,
        default=None,
        help=f"기본값: {DEFAULT_MANIFEST_RELATIVE} (project-root 기준)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="manifest의 embed_key_hash를 무시하고 전체 재임베딩.",
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

    manifest_path = args.manifest_file or (args.project_root / DEFAULT_MANIFEST_RELATIVE)
    manifest = PipelineManifest.load(manifest_path)

    docs = list(iter_chunks_jsonl(chunks_path))
    if not docs:
        print("문서 0건 — 내용 없음.", file=sys.stderr)
        return 1

    pending_texts: list[str] = []
    pending_metas: list[dict] = []
    pending_ids: list[str] = []
    pending_chunk_hashes: list[str] = []
    skipped = 0
    missing_hash = 0

    for i, d in enumerate(docs):
        meta = d.metadata
        chunk_id = str(meta.get("chunk_id", f"idx_{i}"))
        chunk_hash = meta.get("chunk_hash")
        if not chunk_hash:
            # chunk_hash가 없으면 증분 판정 불가 → 항상 적재 (단, manifest 기록 못함)
            missing_hash += 1
            pending_texts.append(d.page_content)
            pending_metas.append(meta)
            pending_ids.append(chunk_id)
            pending_chunk_hashes.append("")
            continue
        if not args.force and not manifest.is_embed_stale(chunk_id, chunk_hash):
            skipped += 1
            continue
        pending_texts.append(d.page_content)
        pending_metas.append(meta)
        pending_ids.append(chunk_id)
        pending_chunk_hashes.append(chunk_hash)

    if not pending_texts:
        print(
            f"재임베딩 대상 0건 (전체 {len(docs)}, 스킵 {skipped}). "
            f"embed_version={manifest.embed_version}"
        )
        return 0

    store = create_vector_store(settings)
    store.add_texts(pending_texts, metadatas=pending_metas, ids=pending_ids)

    embedded_at = datetime.now(timezone.utc).isoformat()
    for cid, chash in zip(pending_ids, pending_chunk_hashes):
        if chash:
            manifest.update_embed(cid, chash, embedded_at)
    manifest.save(manifest_path)

    total = len(docs)
    print(
        f"적재 완료: {len(pending_texts)}/{total} chunks "
        f"(스킵 {skipped}, hash 없음 {missing_hash}) → {settings.supabase_table_name}"
    )
    print(f"manifest 갱신: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
