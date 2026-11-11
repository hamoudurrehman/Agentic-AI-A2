"""Unit tests for Portfolio MCP Server."""
import pytest
from gigbid.mcp_servers.portfolio import tools, server, resources

def test_list_skills():
    skills = tools.list_skills("persona_aiml")
    assert isinstance(skills, list)
    assert "Python" in skills
    assert "LangGraph" in skills

def test_search_evidence():
    items = tools.search_evidence("LangGraph agent", k=2, persona_id="persona_aiml")
    assert len(items) > 0
    assert any("LangGraph" in it["source"] or "LangGraph" in it.get("summary", "") for it in items)

def test_get_case_study():
    cs = tools.get_case_study("cs_aiml_01", persona_id="persona_aiml")
    assert cs is not None
    assert cs["id"] == "cs_aiml_01"
    assert "FinTech" in cs["client_industry"]

def test_jsonrpc_tools_list():
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    resp = server.handle_jsonrpc(req)
    assert resp["id"] == 1
    assert "tools" in resp["result"]
    tool_names = [t["name"] for t in resp["result"]["tools"]]
    assert "search_evidence" in tool_names
    assert "get_case_study" in tool_names

def test_resource_read():
    res = resources.read_resource("portfolio://case/cs_aiml_01", "persona_aiml")
    assert res is not None
    assert res["content"]["id"] == "cs_aiml_01"
