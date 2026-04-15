# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: 블록 경계 유지 청킹 전략 — 표/일정/통계 문서용, 표 행 분리 절대 금지
"""
schedule / statistics 문서에 사용.

전략:
1. table 블록은 항상 단독 청크. 행 분리 절대 금지.
   - 표가 max_tokens 초과 시 의미 행 그룹 단위(섹션 구분 빈 행 기준)로만 분할.
2. heading/paragraph/list는 블록 경계를 유지하면서 누적.
3. overlap은 0 (schedule/statistics 문서는 중복 컨텍스트 불필요).
"""
from __future__ import annotations

import hashlib
import re

from ...parse.ir_schema import ParseBlock, ParseIR
from ..chunk_schema import ChunkConfig, ChunkMetadata, ChunkRecord
from ..token_utils import count_tokens


def chunk_with_blocks(
    ir: ParseIR,
    config: ChunkConfig,
    cert_id: str = "UNKNOWN",
    doc_type: str = "schedule",
) -> list[ChunkRecord]:
    """ParseIR를 block-boundary 전략으로 청킹한다."""
    records: list[ChunkRecord] = []
    seq = 0

    buffer_blocks: list[ParseBlock] = []
    current_section_path: list[str] = []

    def flush_buffer(section_path: list[str]) -> None:
        nonlocal seq
        if not buffer_blocks:
            return
        combined = "\n\n".join(b.text for b in buffer_blocks)
        if count_tokens(combined) >= config.min_tokens:
            _append_chunk(
                records, combined, buffer_blocks, section_path,
                ir, config, cert_id, doc_type, seq
            )
            seq += 1
        buffer_blocks.clear()

    for block in ir.blocks:
        if block.block_type == "heading":
            flush_buffer(current_section_path)
            current_section_path = list(block.section_path) + [block.text]

        elif block.block_type == "table":
            flush_buffer(current_section_path)
            # 표 단독 청크 처리
            table_chunks = _split_large_table(block, config, cert_id, doc_type, ir, seq)
            records.extend(table_chunks)
            seq += len(table_chunks)

        else:
            # 현재 블록 추가 시 초과 여부 체크
            test_combined = "\n\n".join(b.text for b in buffer_blocks + [block])
            if buffer_blocks and count_tokens(test_combined) > config.max_tokens:
                flush_buffer(current_section_path)
            buffer_blocks.append(block)

    flush_buffer(current_section_path)
    return records


# ---------------------------------------------------------------------------
# 표 분할
# ---------------------------------------------------------------------------

def _split_large_table(
    block: ParseBlock,
    config: ChunkConfig,
    cert_id: str,
    doc_type: str,
    ir: ParseIR,
    start_seq: int,
) -> list[ChunkRecord]:
    """표가 max_tokens 초과 시 의미 행 그룹으로 분할.

    분할 원칙:
    - 헤더 행(구분선 바로 위)은 모든 분할 청크에 복사.
    - 빈 행 또는 빈 구분 행 기준으로만 행 그룹 분리.
    - 단일 행도 초과 시 그대로 1청크로 유지 (행 내부 분리 금지).
    """
    text = block.text
    if count_tokens(text) <= config.max_tokens:
        records: list[ChunkRecord] = []
        _append_chunk(
            records, text, [block], block.section_path,
            ir, config, cert_id, doc_type, start_seq
        )
        return records

    lines = text.split("\n")
    # 헤더 행과 구분선 찾기
    header_lines: list[str] = []
    data_lines: list[str] = []
    header_done = False

    for line in lines:
        if not header_done:
            header_lines.append(line)
            if re.search(r"\|[-: ]+\|", line):
                header_done = True
        else:
            data_lines.append(line)

    # 데이터 행 그룹화
    groups: list[list[str]] = []
    current_group: list[str] = []

    for line in data_lines:
        if not line.strip() and current_group:
            groups.append(current_group)
            current_group = []
        else:
            current_group.append(line)
    if current_group:
        groups.append(current_group)

    if not groups:
        # 분할 불가, 단독 청크 반환
        records: list[ChunkRecord] = []
        _append_chunk(
            records, text, [block], block.section_path,
            ir, config, cert_id, doc_type, start_seq
        )
        return records

    # 행 그룹을 합쳐서 청크 생성
    records: list[ChunkRecord] = []
    seq = start_seq
    chunk_lines = list(header_lines)
    chunk_data_count = 0

    for group in groups:
        test_chunk = "\n".join(chunk_lines + group)
        if chunk_data_count > 0 and count_tokens(test_chunk) > config.max_tokens:
            # flush
            chunk_text = "\n".join(chunk_lines)
            _append_chunk(
                records, chunk_text, [block], block.section_path,
                ir, config, cert_id, doc_type, seq
            )
            seq += 1
            # 새 청크 시작 (헤더 유지)
            chunk_lines = list(header_lines) + group
            chunk_data_count = 1
        else:
            chunk_lines.extend(group)
            chunk_data_count += 1

    if chunk_data_count > 0:
        chunk_text = "\n".join(chunk_lines)
        _append_chunk(
            records, chunk_text, [block], block.section_path,
            ir, config, cert_id, doc_type, seq
        )

    return records


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _make_chunk_id(doc_id: str, source_loc: str, seq: int) -> str:
    page = source_loc.replace("page:", "p") if source_loc else "p0"
    return f"{doc_id}_{page}_c{seq}"


def _compute_chunk_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _append_chunk(
    records: list[ChunkRecord],
    text: str,
    blocks: list[ParseBlock],
    section_path: list[str],
    ir: ParseIR,
    config: ChunkConfig,
    cert_id: str,
    doc_type: str,
    seq: int,
) -> None:
    source_loc = blocks[0].source_loc if blocks else ""
    chunk_id = _make_chunk_id(ir.doc_id, source_loc, seq)
    chunk_hash = _compute_chunk_hash(text)

    metadata = ChunkMetadata(
        cert_id=cert_id,
        source_type="pdf",
        doc_type=doc_type,
        doc_id=ir.doc_id,
        chunk_id=chunk_id,
        chunk_hash=chunk_hash,
        section_path=list(section_path),
        source_loc=source_loc,
        doc_version=config.doc_version,
        chunk_seq=seq,
    )
    records.append(ChunkRecord(
        chunk_id=chunk_id,
        doc_id=ir.doc_id,
        text=text,
        metadata=metadata,
    ))
