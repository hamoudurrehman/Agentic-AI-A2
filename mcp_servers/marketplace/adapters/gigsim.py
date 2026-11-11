"""GigSim Adapter for Marketplace MCP Port."""
from typing import List, Dict, Any, Optional
from gigbid.gigsim.simulator import gigsim_instance
from gigbid.gigsim.models import ProposalSubmission

class GigSimAdapter:
    def __init__(self):
        self.sim = gigsim_instance

    def search_jobs(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        return self.sim.search_jobs(query, limit)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.sim.get_job(job_id)

    def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]:
        return self.sim.get_client_history(client_id)

    def get_connects_balance(self, user_id: str = "default_user") -> int:
        return self.sim.get_connects_balance(user_id)

    def submit_proposal(self, submission_data: Dict[str, Any], user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
        submission = ProposalSubmission(**submission_data)
        return self.sim.submit_proposal(submission, user_id=user_id, trace_id=trace_id)

    def list_messages(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.sim.list_messages(job_id)

    def send_message(self, message_data: Dict[str, Any], user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
        return self.sim.send_message(message_data, user_id=user_id, trace_id=trace_id)
