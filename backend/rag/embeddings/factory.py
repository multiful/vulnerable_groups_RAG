# File: factory.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: OpenAI / HuggingFace 임베딩 인스턴스 생성 (LangChain)
from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.core.config import Settings

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings


def build_embeddings(settings: Settings) -> Embeddings:
    """환경에 따라 LangChain Embeddings를 만든다. LlamaIndex 경로는 별도 모듈에서 확장."""
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "embedding_provider=openai 인데 OPENAI_API_KEY 가 비어 있습니다."
            )
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=settings.hf_embedding_model)
