"""Unit tests for RAG Ingestion, Retrieval Variants, and Claim Verification."""
import pytest
from rag.ingest.loader import load_persona_chunks
from rag.retriever import get_retriever
from rag.verify import split_claims, verify_and_sanitize_proposal

def test_load_chunks():
    chunks = load_persona_chunks("persona_aiml")
    assert len(chunks) > 0
    types = {c.metadata["type"] for c in chunks}
    assert "case_study" in types
    assert "cv" in types
    assert "repo" in types

def test_rag_variants_retrieval():
    variants = ["v0_naive", "v1_requirement_decomp", "v2_hybrid", "v3_cross_encoder", "v4_outcome_aware", "v8_corrective"]
    for v in variants:
        retriever = get_retriever(variant=v, persona_id="persona_aiml")
        results = retriever.retrieve("LangGraph multi-agent parallel state graph", k=3)
        assert len(results) > 0, f"Variant {v} returned empty results"
        top_chunk = results[0][0]
        assert top_chunk.chunk_id is not None

def test_claim_verification():
    proposal_text = (
        "In a recent FinTech project, I built a LangGraph state graph with parallel agents. "
        "I have won the Nobel Prize in quantum computing and guarantee 100% immediate profit. "
        "I have experience deploying FastAPI microservices with Docker."
    )
    mock_evidence = [
        {"source": "Enterprise Knowledge Agent", "summary": "LangGraph state graph with parallel agents in FinTech", "metrics": "2.4M queries/month"},
        {"source": "FastAPI React Boilerplate", "summary": "FastAPI microservices and Docker containers"}
    ]

    res = verify_and_sanitize_proposal(proposal_text, mock_evidence)
    assert res["total_claims"] >= 3
    assert res["unsupported_before"] >= 1
    assert res["unsupported_after"] == 0
    assert "Nobel Prize" not in res["sanitized_text"]
    assert "LangGraph" in res["sanitized_text"]
