"""Marketplace MCP Server wrapping GigSim and Upwork Live.
Exposes MCP read and write tools with schemas, annotations, idempotency, rate limiting, and audit logging.
"""
from typing import Dict, Any, List, Optional
import time
from pydantic import BaseModel, Field
from .adapters.gigsim import GigSimAdapter
from .adapters.upwork_live import UpworkLiveAdapter

SERVER_INFO = {
    "name": "gigbid-marketplace-server",
    "version": "1.0.0",
    "description": "Marketplace MCP Server providing unified access to GigSim simulator and Upwork live."
}

# Active Adapter Switcher
_gigsim_adapter = GigSimAdapter()
_upwork_adapter = UpworkLiveAdapter()
_current_mode = "gigsim" # "gigsim" or "upwork_live"

def set_mode(mode: str):
    global _current_mode
    if mode in ["gigsim", "upwork_live"]:
        _current_mode = mode

def get_adapter():
    return _gigsim_adapter if _current_mode == "gigsim" else _upwork_adapter

# Rate Limiter & Auth
VALID_BEARER_TOKENS = {"gigbid-secret-token-123", "test-token"}
_user_last_call: Dict[str, float] = {}

def check_auth(token: Optional[str]) -> bool:
    if not token:
        return True # Permissive in local dev / test runs if unset
    clean_token = token.replace("Bearer ", "").strip()
    return clean_token in VALID_BEARER_TOKENS

def check_rate_limit(user_id: str, min_interval_seconds: float = 0.2) -> bool:
    now = time.time()
    last = _user_last_call.get(user_id, 0.0)
    if now - last < min_interval_seconds:
        return False
    _user_last_call[user_id] = now
    return True

# Pydantic Schemas for Tools
class SearchJobsInput(BaseModel):
    query: str = Field(default="", description="Search keywords")
    limit: int = Field(default=10, ge=1, le=50, description="Max jobs to return")

class GetJobInput(BaseModel):
    job_id: str = Field(description="Unique job identifier")

class GetClientHistoryInput(BaseModel):
    client_id: str = Field(description="Unique client identifier")

class GetConnectsBalanceInput(BaseModel):
    user_id: str = Field(default="default_user", description="Freelancer user identifier")

class ListMessagesInput(BaseModel):
    job_id: Optional[str] = Field(default=None, description="Optional job ID filter")

class ProposalSubmissionInput(BaseModel):
    proposal_id: str = Field(description="Unique proposal identifier")
    job_id: str = Field(description="Target job identifier")
    freelancer_id: str = Field(default="default_user", description="Submitting freelancer ID")
    bid_amount: float = Field(gt=0, description="Proposed price in USD")
    cover_letter: str = Field(min_length=20, description="Detailed cover letter text")
    evidence_citations: List[str] = Field(default_factory=list, description="IDs of portfolio items cited as evidence")
    idempotency_key: str = Field(description="Unique key to prevent duplicate submissions")
    dry_run: bool = Field(default=False, description="Simulate without spending Connects")

class SendMessageInput(BaseModel):
    job_id: str = Field(description="Associated job ID")
    proposal_id: str = Field(description="Associated proposal ID")
    content: str = Field(min_length=1, description="Message text")
    idempotency_key: str = Field(description="Unique idempotency key")

TOOLS_MANIFEST = [
    {
        "name": "search_jobs",
        "description": "Search marketplace job feed with query and limit.",
        "inputSchema": SearchJobsInput.model_json_schema(),
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "get_job",
        "description": "Fetch detailed job posting including client history metrics.",
        "inputSchema": GetJobInput.model_json_schema(),
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "get_client_history",
        "description": "Retrieve comprehensive client spending, hiring rate, and review history.",
        "inputSchema": GetClientHistoryInput.model_json_schema(),
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "get_connects_balance",
        "description": "Check current available Connects balance for a freelancer.",
        "inputSchema": GetConnectsBalanceInput.model_json_schema(),
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "list_messages",
        "description": "List client communications and message history.",
        "inputSchema": ListMessagesInput.model_json_schema(),
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "create_proposal_draft",
        "description": "Draft a proposal locally or in dry_run mode without spending connects.",
        "inputSchema": ProposalSubmissionInput.model_json_schema(),
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "submit_proposal",
        "description": "Submit a finalized proposal to the marketplace. Spends Connects unless dry_run is true.",
        "inputSchema": ProposalSubmissionInput.model_json_schema(),
        "annotations": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
    },
    {
        "name": "send_message",
        "description": "Send a communication or interview response message to the client.",
        "inputSchema": SendMessageInput.model_json_schema(),
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
    }
]

def list_tools() -> List[Dict[str, Any]]:
    return TOOLS_MANIFEST

def call_tool(name: str, arguments: Dict[str, Any], user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
    adapter = get_adapter()
    
    if name == "search_jobs":
        validated = SearchJobsInput(**arguments)
        res = adapter.search_jobs(query=validated.query, limit=validated.limit)
    elif name == "get_job":
        validated = GetJobInput(**arguments)
        res = adapter.get_job(job_id=validated.job_id)
    elif name == "get_client_history":
        validated = GetClientHistoryInput(**arguments)
        res = adapter.get_client_history(client_id=validated.client_id)
    elif name == "get_connects_balance":
        validated = GetConnectsBalanceInput(**arguments)
        res = {"connects_balance": adapter.get_connects_balance(user_id=validated.user_id)}
    elif name == "list_messages":
        validated = ListMessagesInput(**arguments)
        res = adapter.list_messages(job_id=validated.job_id)
    elif name == "create_proposal_draft":
        args = dict(arguments)
        args["dry_run"] = True
        validated = ProposalSubmissionInput(**args)
        res = adapter.submit_proposal(validated.model_dump(), user_id=user_id, trace_id=trace_id)
    elif name == "submit_proposal":
        validated = ProposalSubmissionInput(**arguments)
        res = adapter.submit_proposal(validated.model_dump(), user_id=user_id, trace_id=trace_id)
    elif name == "send_message":
        validated = SendMessageInput(**arguments)
        res = adapter.send_message(validated.model_dump(), user_id=user_id, trace_id=trace_id)
    else:
        raise ValueError(f"Unknown marketplace tool: {name}")

    return {"content": [{"type": "text", "text": str(res)}], "raw": res}

def handle_jsonrpc(request: Dict[str, Any], token: Optional[str] = None, user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
    if not check_auth(token):
        return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32000, "message": "Unauthorized Bearer token"}}
    
    if not check_rate_limit(user_id):
        return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32001, "message": "Rate limit exceeded"}}

    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list_tools()}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = call_tool(name, args, user_id=user_id, trace_id=trace_id)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
