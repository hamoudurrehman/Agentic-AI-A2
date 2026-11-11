"""Unit tests for Marketplace MCP Server and Adapters."""
import pytest
from gigbid.mcp_servers.marketplace import server

def test_list_marketplace_tools():
    tools = server.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "search_jobs" in tool_names
    assert "get_job" in tool_names
    assert "submit_proposal" in tool_names
    assert "create_proposal_draft" in tool_names

def test_search_jobs():
    res = server.call_tool("search_jobs", {"query": "LangGraph", "limit": 5})
    assert "raw" in res
    assert len(res["raw"]) > 0
    assert "LangGraph" in res["raw"][0]["title"]

def test_idempotent_proposal_submission():
    sub_data = {
        "proposal_id": "prop_test_01",
        "job_id": "job_gs_001",
        "freelancer_id": "default_user",
        "bid_amount": 3200.0,
        "cover_letter": "I have extensive experience with LangGraph agents and FastAPI from previous production projects.",
        "evidence_citations": ["cs_aiml_01"],
        "idempotency_key": "unique_key_123",
        "dry_run": False
    }
    
    # First call
    res1 = server.call_tool("submit_proposal", sub_data)
    assert res1["raw"]["status"] in ["submitted", "replied", "interview", "hired"]
    initial_remaining = res1["raw"]["remaining_connects"]

    # Second call with same idempotency key should return cached result without spending more connects
    res2 = server.call_tool("submit_proposal", sub_data)
    assert res2["raw"]["remaining_connects"] == initial_remaining

def test_dry_run_preview():
    sub_data = {
        "proposal_id": "prop_dry_01",
        "job_id": "job_gs_001",
        "freelancer_id": "default_user",
        "bid_amount": 3000.0,
        "cover_letter": "Dry run proposal to test preview calculation without spending connects.",
        "evidence_citations": ["cs_aiml_01"],
        "idempotency_key": "dry_key_001",
        "dry_run": True
    }
    res = server.call_tool("create_proposal_draft", sub_data)
    assert res["raw"]["dry_run"] is True
    assert "cover_letter_preview" in res["raw"]

def test_adapter_switching():
    server.set_mode("upwork_live")
    res = server.call_tool("search_jobs", {"query": "AI"})
    assert "Upwork Live" in res["raw"][0]["title"]
    server.set_mode("gigsim")
