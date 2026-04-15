# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: 파이프라인 증분 처리 manifest — load/save/is_stale 판정
"""
pipeline_manifest.json 스키마:
{
    "parse_version": "v1",
    "chunk_version": "v1",
    "embed_version": "text-embedding-3-small-v1",
    "documents": {
        "<doc_id>": {
            "file_hash": "sha256:...",
            "parse_hash": "sha256:...",
            "parser_used": "pymupdf4llm",
            "chunk_count": 142,
            "status": "done",
            "quality_flags": []
        }
    },
    "chunks": {
        "<chunk_id>": {
            "chunk_hash": "sha256:...",
            "embed_key_hash": "sha256:...",
            "embedded_at": "..."
        }
    }
}

증분 판정:
    parse 스킵:  file_hash 동일 AND parse_version 동일
    chunk 스킵:  parse_hash 동일 AND chunk_version 동일
    embed 스킵:  embed_key_hash (= chunk_hash + embed_version) 동일
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

PARSE_VERSION = "v1"
CHUNK_VERSION = "v1"
EMBED_VERSION = "text-embedding-3-small-v1"


class PipelineManifest:
    """파이프라인 manifest 관리 클래스."""

    def __init__(self) -> None:
        self.parse_version: str = PARSE_VERSION
        self.chunk_version: str = CHUNK_VERSION
        self.embed_version: str = EMBED_VERSION
        self.documents: dict[str, dict] = {}
        self.chunks: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # 로드 / 저장
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "PipelineManifest":
        """JSON 파일에서 manifest를 로드한다. 파일 없으면 빈 manifest 반환."""
        manifest = cls()
        if not path.exists():
            return manifest
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        manifest.parse_version = data.get("parse_version", PARSE_VERSION)
        manifest.chunk_version = data.get("chunk_version", CHUNK_VERSION)
        manifest.embed_version = data.get("embed_version", EMBED_VERSION)
        manifest.documents = data.get("documents", {})
        manifest.chunks = data.get("chunks", {})
        return manifest

    def save(self, path: Path) -> None:
        """manifest를 JSON 파일로 저장한다."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "parse_version": self.parse_version,
            "chunk_version": self.chunk_version,
            "embed_version": self.embed_version,
            "documents": self.documents,
            "chunks": self.chunks,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 증분 판정
    # ------------------------------------------------------------------

    def is_parse_stale(self, doc_id: str, file_hash: str) -> bool:
        """파싱이 필요한지 판정.

        스킵 조건: 동일 doc_id, 동일 file_hash, 동일 parse_version이 manifest에 존재.
        """
        doc = self.documents.get(doc_id)
        if not doc:
            return True
        return (
            doc.get("file_hash") != file_hash
            or doc.get("parse_version") != self.parse_version
            or doc.get("status") != "done"
        )

    def is_chunk_stale(self, doc_id: str, parse_hash: str) -> bool:
        """청킹이 필요한지 판정.

        스킵 조건: 동일 parse_hash, 동일 chunk_version.
        """
        doc = self.documents.get(doc_id)
        if not doc:
            return True
        return (
            doc.get("parse_hash") != parse_hash
            or doc.get("chunk_version") != self.chunk_version
        )

    def is_embed_stale(self, chunk_id: str, chunk_hash: str) -> bool:
        """임베딩이 필요한지 판정.

        스킵 조건: 동일 embed_key_hash.
        """
        embed_key_hash = _compute_embed_key_hash(chunk_hash, self.embed_version)
        chunk_rec = self.chunks.get(chunk_id)
        if not chunk_rec:
            return True
        return chunk_rec.get("embed_key_hash") != embed_key_hash

    # ------------------------------------------------------------------
    # 갱신
    # ------------------------------------------------------------------

    def update_parse(
        self,
        doc_id: str,
        file_hash: str,
        parse_hash: str,
        parser_used: str,
        chunk_count: int = 0,
        quality_flags: Optional[list[str]] = None,
        status: str = "done",
    ) -> None:
        self.documents[doc_id] = {
            "file_hash": file_hash,
            "parse_hash": parse_hash,
            "parse_version": self.parse_version,
            "chunk_version": self.chunk_version,
            "parser_used": parser_used,
            "chunk_count": chunk_count,
            "status": status,
            "quality_flags": quality_flags or [],
        }

    def update_embed(self, chunk_id: str, chunk_hash: str, embedded_at: str) -> None:
        embed_key_hash = _compute_embed_key_hash(chunk_hash, self.embed_version)
        self.chunks[chunk_id] = {
            "chunk_hash": chunk_hash,
            "embed_key_hash": embed_key_hash,
            "embedded_at": embedded_at,
        }


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def _compute_embed_key_hash(chunk_hash: str, embed_version: str) -> str:
    payload = f"{chunk_hash}::{embed_version}"
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()
