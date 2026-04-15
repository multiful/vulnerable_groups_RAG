# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: ChunkRecord → JSONL 직렬화 — chunk_loader.py 입력 계약 준수
"""
serialize_chunk(chunk) → JSON 문자열 (줄바꿈 없음)
write_chunks_jsonl(chunks, path) → JSONL 파일 저장

출력 형식은 backend/rag/ingest/chunk_loader.py 입력과 완전 호환해야 한다.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ..chunk.chunk_schema import ChunkRecord


def serialize_chunk(chunk: ChunkRecord) -> str:
    """ChunkRecord를 JSON 문자열 1줄로 직렬화한다."""
    data = {
        "chunk_id": chunk.chunk_id,
        "doc_id": chunk.doc_id,
        "text": chunk.text,
        "metadata": {
            "cert_id": chunk.metadata.cert_id,
            "source_type": chunk.metadata.source_type,
            "doc_type": chunk.metadata.doc_type,
            "doc_id": chunk.metadata.doc_id,
            "chunk_id": chunk.metadata.chunk_id,
            "chunk_hash": chunk.metadata.chunk_hash,
            "section_path": chunk.metadata.section_path,
            "source_loc": chunk.metadata.source_loc,
            "doc_version": chunk.metadata.doc_version,
            "chunk_seq": chunk.metadata.chunk_seq,
            "valid_from": chunk.metadata.valid_from,
            "valid_to": chunk.metadata.valid_to,
            "domain_sub_label": chunk.metadata.domain_sub_label,
            "domain_top_label": chunk.metadata.domain_top_label,
            "risk_stage_id": chunk.metadata.risk_stage_id,
        },
    }
    return json.dumps(data, ensure_ascii=False)


def write_chunks_jsonl(chunks: list[ChunkRecord], path: Path) -> int:
    """청크 목록을 JSONL 파일에 기록하고 기록된 청크 수를 반환한다.

    기존 파일이 있으면 덮어쓴다.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            line = serialize_chunk(chunk)
            f.write(line + "\n")
            written += 1
    return written


def append_chunks_jsonl(chunks: list[ChunkRecord], path: Path) -> int:
    """청크 목록을 기존 JSONL 파일에 추가(append)하고 추가된 청크 수를 반환한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with open(path, "a", encoding="utf-8") as f:
        for chunk in chunks:
            line = serialize_chunk(chunk)
            f.write(line + "\n")
            written += 1
    return written
