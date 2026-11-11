"""Contract snapshot tests for MCP servers.
Ensures tool signatures and annotations do not drift unintentionally.
"""
import pytest
from gigbid.mcp_servers.portfolio.server import list_tools as list_portfolio_tools
from gigbid.mcp_servers.marketplace.server import list_tools as list_marketplace_tools
from gigbid.mcp_servers.workspace.server import list_tools as list_workspace_tools

EXPECTED_PORTFOLIO_TOOLS = {"search_evidence", "get_case_study", "list_skills"}
EXPECTED_MARKETPLACE_TOOLS = {
    "search_jobs", "get_job", "get_client_history", "get_connects_balance",
    "list_messages", "create_proposal_draft", "submit_proposal", "send_message"
}
EXPECTED_WORKSPACE_TOOLS = {"get_free_calendar_slots", "create_tentative_interview_hold", "create_email_draft"}

def test_portfolio_schema_snapshot():
    tools = list_portfolio_tools()
    tool_map = {t["name"]: t for t in tools}
    assert set(tool_map.keys()) == EXPECTED_PORTFOLIO_TOOLS
    for t in tools:
        assert "inputSchema" in t
        assert "annotations" in t
        assert t["annotations"]["readOnlyHint"] is True

def test_marketplace_schema_snapshot():
    tools = list_marketplace_tools()
    tool_map = {t["name"]: t for t in tools}
    assert set(tool_map.keys()) == EXPECTED_MARKETPLACE_TOOLS
    assert tool_map["submit_proposal"]["annotations"]["destructiveHint"] is True
    assert tool_map["search_jobs"]["annotations"]["readOnlyHint"] is True

def test_workspace_schema_snapshot():
    tools = list_workspace_tools()
    tool_map = {t["name"]: t for t in tools}
    assert set(tool_map.keys()) == EXPECTED_WORKSPACE_TOOLS
