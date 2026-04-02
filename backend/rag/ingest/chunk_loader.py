# File: chunk_loader.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: data/index_ready/chunks JSONL → LangChain Document
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from langchain_core.documents import Document


def iter_chunks_jsonl(path: Path) -> Iterator[Document]:
    """
    한 줄당 하나의 청크. 필수 키: chunk_id, doc_id, text
    선택 metadata 객체는 그대로 합쳐진다 (cert_id 필터용으로 cert_id 권장).

    예:
    {"chunk_id":"c1","doc_id":"d1","text":"본문...","metadata":{"cert_id":"cert_013","source_type":"pdf"}}
    """
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSONL {path}:{line_no}: {e}") from e
            text = row.get("text") or row.get("content")
            if not text:
                raise ValueError(f"JSONL {path}:{line_no}: text/content 없음")
            chunk_id = row.get("chunk_id", f"line_{line_no}")
            doc_id = row.get("doc_id", "")
            meta = dict(row.get("metadata") or {})
            meta.setdefault("chunk_id", chunk_id)
            meta.setdefault("doc_id", doc_id)
            yield Document(page_content=text, metadata=meta)
