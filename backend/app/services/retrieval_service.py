# File: retrieval_service.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: LangChain + Supabase pgvector 기반 evidence 검색
from __future__ import annotations

from typing import Any

from backend.app.core.config import Settings
from backend.app.schemas.envelope import err_envelope, ok_envelope
from backend.rag.store.supabase_vector import evidence_filter, get_optional_vector_store

# TODO(reserved): reranker, BM25 상시 사용은 프로젝트 규칙상 별도 승인 전 구현하지 않는다.


def _build_query_text(body: dict[str, Any]) -> str:
    parts: list[str] = []
    if body.get("cert_id"):
        parts.append(str(body["cert_id"]))
    parts.extend(body.get("related_domains") or [])
    parts.extend(body.get("related_jobs") or [])
    q = " ".join(str(p) for p in parts if p).strip()
    return q or "자격증 공식 안내"


def _doc_to_evidence_row(doc: Any) -> dict[str, Any]:
    meta = dict(doc.metadata or {})
    return {
        "doc_id": str(meta.get("doc_id", "")),
        "chunk_id": str(meta.get("chunk_id", "")),
        "source_type": str(meta.get("source_type", "pdf")),
        "snippet": (doc.page_content or "")[:2000],
        "section_path": meta.get("section_path") or [],
        "source_url": meta.get("source_url"),
    }


def search_evidence(body: dict[str, Any], settings: Settings) -> dict[str, Any]:
    cert_id = body.get("cert_id")
    if not cert_id:
        return err_envelope(
            "MISSING_REQUIRED_FIELD",
            "cert_id는 필수입니다.",
            {"field": "cert_id"},
        )

    store = get_optional_vector_store(settings)
    if store is None:
        return ok_envelope({"cert_id": cert_id, "evidence": []})

    query = _build_query_text(body)
    flt = evidence_filter(str(cert_id))
    try:
        docs = store.similarity_search(
            query, k=settings.rag_top_k, filter=flt
        )
    except Exception as e:  # noqa: BLE001 — 런타임 진단용 메시지
        return err_envelope(
            "INTERNAL_ERROR",
            "벡터 검색 중 오류가 발생했습니다. Supabase RPC·차원·임베딩 모델을 확인하세요.",
            {"detail": str(e)},
        )

    rows = [_doc_to_evidence_row(d) for d in docs]
    return ok_envelope({"cert_id": cert_id, "evidence": rows})
