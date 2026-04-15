# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: ParseIR → ChunkRecord 목록 생성 오케스트레이터
"""
build_chunks(ir, config) → list[ChunkRecord]

doc_type 기반 전략 분기:
    'schedule' | 'statistics'  → block_chunker (표 경계 유지, overlap=0)
    그 외                      → markdown_chunker (heading propagation)
"""
from __future__ import annotations

from ..parse.ir_schema import ParseIR
from .chunk_schema import ChunkConfig, ChunkRecord
from .strategies.block_chunker import chunk_with_blocks
from .strategies.markdown_chunker import chunk_with_markdown

# schedule/statistics 문서는 overlap 불필요
_BLOCK_DOC_TYPES = {"schedule", "statistics"}


def build_chunks(
    ir: ParseIR,
    config: ChunkConfig,
    cert_id: str = "UNKNOWN",
) -> list[ChunkRecord]:
    """ParseIR를 doc_type에 맞는 전략으로 청킹한다.

    Args:
        ir: 파서가 생성한 ParseIR.
        config: 청킹 파라미터 (max_tokens, overlap_tokens, doc_type 등).
        cert_id: 초기 cert_id. cert_mapper.map_cert_ids()가 나중에 덮어쓴다.

    Returns:
        ChunkRecord 목록.
    """
    if config.doc_type in _BLOCK_DOC_TYPES:
        # 표 경계 유지 전략: overlap 강제 0
        block_config = _override_overlap(config, overlap=0)
        return chunk_with_blocks(ir, block_config, cert_id=cert_id, doc_type=config.doc_type)
    else:
        return chunk_with_markdown(ir, config, cert_id=cert_id, doc_type=config.doc_type)


def select_strategy(doc_type: str) -> str:
    """doc_type에 따른 전략 이름 반환 (logging 용도)."""
    return "block_chunker" if doc_type in _BLOCK_DOC_TYPES else "markdown_chunker"


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _override_overlap(config: ChunkConfig, overlap: int) -> ChunkConfig:
    """overlap_tokens를 오버라이드한 새 ChunkConfig 반환."""
    from dataclasses import replace
    return replace(config, overlap_tokens=overlap)
