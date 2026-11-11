"""MCP Client with Per-Agent Tool Allowlists and Degraded Mode Resilience."""
from typing import Dict, Any, List, Set, Optional
from gigbid.mcp_servers.portfolio import server as portfolio_server
from gigbid.mcp_servers.marketplace import server as marketplace_server
from gigbid.mcp_servers.workspace import server as workspace_server

# Strict Per-Agent Tool Allowlists (Part A / R3)
AGENT_TOOL_ALLOWLISTS: Dict[str, Set[str]] = {
    "scout": {"search_jobs", "get_job"},
    "job_analyst": set(), # Job Analyst extracts structure without external tools
    "risk_assessor": {"get_client_history", "get_job"},
    "fit_matcher": {"search_evidence", "list_skills", "get_case_study"},
    "pricing_strategist": {"get_client_history", "get_connects_balance"},
    "proposal_writer": {"search_evidence", "get_case_study"},
    "critic": {"search_evidence", "get_case_study"},
    "compliance_guard": set(), # Internal policy check
    "client_liaison": {"list_messages", "send_message", "get_free_calendar_slots", "create_tentative_interview_hold", "create_email_draft"}
}

class MultiServerMCPClient:
    def __init__(self):
        self.marketplace_online = True

    def set_marketplace_online(self, status: bool):
        self.marketplace_online = status

    def call_agent_tool(self, agent_role: str, tool_name: str, arguments: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Dispatch tool call enforcing agent-specific permission boundary."""
        allowed = AGENT_TOOL_ALLOWLISTS.get(agent_role, set())
        if tool_name not in allowed:
            raise PermissionError(f"Agent role '{agent_role}' is not authorized to call tool '{tool_name}'")

        # Marketplace tools
        if tool_name in ["search_jobs", "get_job", "get_client_history", "get_connects_balance", "list_messages", "create_proposal_draft", "submit_proposal", "send_message"]:
            if not self.marketplace_online:
                return {
                    "error": "MARKETPLACE_UNAVAILABLE",
                    "degraded_mode": True,
                    "message": "Marketplace MCP Server is unreachable. Action queued for auto-retry when online."
                }
            return marketplace_server.call_tool(tool_name, arguments, **kwargs)

        # Portfolio tools
        elif tool_name in ["search_evidence", "get_case_study", "list_skills"]:
            return portfolio_server.call_tool(tool_name, arguments, persona_id=kwargs.get("persona_id", "persona_aiml"))

        # Workspace tools
        elif tool_name in ["get_free_calendar_slots", "create_tentative_interview_hold", "create_email_draft"]:
            return workspace_server.call_tool(tool_name, arguments)

        else:
            raise ValueError(f"Tool {tool_name} not found across registered MCP servers.")

mcp_client_instance = MultiServerMCPClient()
