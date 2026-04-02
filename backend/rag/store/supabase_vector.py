# File: supabase_vector.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: Supabase 클라이언트 + LangChain SupabaseVectorStore 팩토리
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.core.config import Settings
from backend.rag.embeddings.factory import build_embeddings

if TYPE_CHECKING:
    from langchain_community.vectorstores import SupabaseVectorStore


def supabase_client_configured(settings: Settings) -> bool:
    return bool(settings.supabase_url and settings.supabase_service_key)


def create_vector_store(settings: Settings) -> SupabaseVectorStore:
    if not supabase_client_configured(settings):
        raise ValueError("SUPABASE_URL / SUPABASE_SERVICE_KEY 가 설정되지 않았습니다.")

    from langchain_community.vectorstores import SupabaseVectorStore
    from supabase import create_client

    client = create_client(settings.supabase_url, settings.supabase_service_key)
    embeddings = build_embeddings(settings)
    return SupabaseVectorStore(
        client=client,
        embedding=embeddings,
        table_name=settings.supabase_table_name,
        query_name=settings.supabase_match_rpc,
    )


def get_optional_vector_store(settings: Settings) -> SupabaseVectorStore | None:
    """설정이 없으면 None — API는 빈 evidence 등으로 응답."""
    if not supabase_client_configured(settings):
        return None
    try:
        return create_vector_store(settings)
    except Exception:
        return None


def evidence_filter(cert_id: str) -> dict[str, Any]:
    """인제스트 시 metadata에 cert_id 를 넣었다고 가정 (@> 필터)."""
    return {"cert_id": cert_id}
