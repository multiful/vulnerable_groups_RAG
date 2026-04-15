# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
# Last Updated: 2026-04-13
# Role: tiktoken cl100k_base 기반 토큰 카운팅 및 분할 유틸
"""
count_tokens()  — 텍스트 → 토큰 수 (cl100k_base)
split_by_tokens() — 텍스트를 max_tokens 이하 청크로 분할, 문장 경계 우선

문자 수 기준 청킹 금지 (CLAUDE.md §12 / 계획 §4).
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

import tiktoken

_ENCODING_NAME = "cl100k_base"


@lru_cache(maxsize=1)
def _get_encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding(_ENCODING_NAME)


def count_tokens(text: str) -> int:
    """텍스트의 cl100k_base 토큰 수를 반환한다."""
    return len(_get_encoder().encode(text))


def split_by_tokens(
    text: str,
    max_tokens: int,
    overlap_tokens: int = 0,
) -> list[str]:
    """텍스트를 max_tokens 이하의 청크로 분할한다.

    분할 전략:
    1. 문장 경계(마침표/물음표/느낌표/줄바꿈) 우선 분할.
    2. 단일 문장이 max_tokens 초과 시 단어 경계 분할.
    3. overlap_tokens > 0이면 이전 청크 끝 토큰을 다음 청크 앞에 붙인다.

    Returns:
        토큰 기준으로 분할된 텍스트 조각 목록.
    """
    enc = _get_encoder()
    tokens = enc.encode(text)

    if len(tokens) <= max_tokens:
        return [text] if text.strip() else []

    # 문장 단위로 먼저 분리
    sentences = _split_sentences(text)
    chunks: list[str] = []
    current_tokens: list[int] = []

    for sentence in sentences:
        sent_tokens = enc.encode(sentence)

        # 문장 자체가 max_tokens 초과 → 강제 분할
        if len(sent_tokens) > max_tokens:
            # 현재 버퍼 먼저 flush
            if current_tokens:
                chunks.append(enc.decode(current_tokens))
                current_tokens = []
            # 긴 문장 강제 분할
            for sub in _force_split(sent_tokens, max_tokens, overlap_tokens, enc):
                chunks.append(sub)
            continue

        # 버퍼에 추가 시 한계 초과 → flush 후 재시작
        if len(current_tokens) + len(sent_tokens) > max_tokens:
            if current_tokens:
                chunks.append(enc.decode(current_tokens))
                # overlap
                if overlap_tokens > 0:
                    current_tokens = current_tokens[-overlap_tokens:]
                else:
                    current_tokens = []

        current_tokens.extend(sent_tokens)

    if current_tokens:
        chunks.append(enc.decode(current_tokens))

    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# 내부 유틸
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """문장 경계(마침표, 줄바꿈)로 텍스트 분할."""
    # 줄바꿈 기준 1차 분리 후 문장 종결 부호 기준 2차 분리
    parts: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 문장 종결 부호 분리 (뒤에 공백 있는 경우)
        sub = re.split(r"(?<=[.!?。])\s+", line)
        parts.extend(s.strip() for s in sub if s.strip())
    return parts


def _force_split(
    tokens: list[int],
    max_tokens: int,
    overlap_tokens: int,
    enc: tiktoken.Encoding,
) -> list[str]:
    """토큰 목록을 max_tokens 크기로 강제 분할."""
    result: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        result.append(enc.decode(tokens[start:end]))
        if end >= len(tokens):
            break
        start = end - overlap_tokens if overlap_tokens > 0 else end
    return result
