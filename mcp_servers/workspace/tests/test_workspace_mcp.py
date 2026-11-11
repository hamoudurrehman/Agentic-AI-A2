"""Unit tests for Workspace MCP Server."""
import pytest
from gigbid.mcp_servers.workspace import server, tools

def test_list_workspace_tools():
    tool_names = [t["name"] for t in server.list_tools()]
    assert "get_free_calendar_slots" in tool_names
    assert "create_tentative_interview_hold" in tool_names
    assert "create_email_draft" in tool_names

def test_get_free_calendar_slots():
    slots = tools.get_free_calendar_slots(days_ahead=2)
    assert len(slots) >= 4
    assert "PKT" in slots[0]

def test_create_hold_and_email():
    hold = tools.create_tentative_interview_hold("2026-11-12 10:00 AM PKT", "Apex FinTech", "job_gs_001")
    assert hold["status"] == "tentative_hold"
    
    draft = tools.create_email_draft("client@apex.com", "Interview Confirmation", "Looking forward to speaking.")
    assert draft["status"] == "draft_pending_human_review"
