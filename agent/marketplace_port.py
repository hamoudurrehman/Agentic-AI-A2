"""Marketplace Port - Single internal interface for all marketplace operations.
Switches between GigSim simulator and Live Upwork via configuration without altering agent code.
"""
from typing import List, Dict, Any, Optional
from gigbid.mcp_servers.marketplace import server as mcp_marketplace

class MarketplacePort:
    def __init__(self, mode: str = "gigsim"):
        self.set_mode(mode)

    def set_mode(self, mode: str):
        self.mode = mode
        mcp_marketplace.set_mode(mode)

    def get_mode(self) -> str:
        return self.mode

    def search_jobs(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        res = mcp_marketplace.call_tool("search_jobs", {"query": query, "limit": limit})
        return res.get("raw", [])

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        res = mcp_marketplace.call_tool("get_job", {"job_id": job_id})
        return res.get("raw")

    def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]:
        res = mcp_marketplace.call_tool("get_client_history", {"client_id": client_id})
        return res.get("raw")

    def get_connects_balance(self, user_id: str = "default_user") -> int:
        res = mcp_marketplace.call_tool("get_connects_balance", {"user_id": user_id})
        return res.get("raw", {}).get("connects_balance", 0)

    def submit_proposal(
        self,
        proposal_id: str,
        job_id: str,
        bid_amount: float,
        cover_letter: str,
        evidence_citations: List[str],
        idempotency_key: str,
        dry_run: bool = False,
        user_id: str = "default_user",
        trace_id: str = "trace_001"
    ) -> Dict[str, Any]:
        payload = {
            "proposal_id": proposal_id,
            "job_id": job_id,
            "freelancer_id": user_id,
            "bid_amount": bid_amount,
            "cover_letter": cover_letter,
            "evidence_citations": evidence_citations,
            "idempotency_key": idempotency_key,
            "dry_run": dry_run
        }
        tool_name = "create_proposal_draft" if dry_run else "submit_proposal"
        res = mcp_marketplace.call_tool(tool_name, payload, user_id=user_id, trace_id=trace_id)
        return res.get("raw", {})

    def list_messages(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        res = mcp_marketplace.call_tool("list_messages", {"job_id": job_id})
        return res.get("raw", [])

    def send_message(self, job_id: str, proposal_id: str, content: str, idempotency_key: str, user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
        payload = {
            "job_id": job_id,
            "proposal_id": proposal_id,
            "content": content,
            "idempotency_key": idempotency_key
        }
        res = mcp_marketplace.call_tool("send_message", payload, user_id=user_id, trace_id=trace_id)
        return res.get("raw", {})

# Global singleton port
marketplace_port_instance = MarketplacePort("gigsim")
