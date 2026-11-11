"""Workspace MCP Server implementation."""
from typing import Dict, Any, List
from . import tools

SERVER_INFO = {
    "name": "gigbid-workspace-server",
    "version": "1.0.0",
    "description": "Workspace MCP Server handling calendar slots, interview holds, and email drafts."
}

TOOLS_MANIFEST = [
    {
        "name": "get_free_calendar_slots",
        "description": "Get open calendar slots suitable for client interviews.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "default": 3}
            }
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "create_tentative_interview_hold",
        "description": "Place a tentative hold on the calendar for a client interview.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slot": {"type": "string"},
                "client_name": {"type": "string"},
                "job_id": {"type": "string"}
            },
            "required": ["slot", "client_name", "job_id"]
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
    },
    {
        "name": "create_email_draft",
        "description": "Create an email draft for client follow-up.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["recipient", "subject", "body"]
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}
    }
]

def list_tools() -> List[Dict[str, Any]]:
    return TOOLS_MANIFEST

def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "get_free_calendar_slots":
        res = tools.get_free_calendar_slots(days_ahead=arguments.get("days_ahead", 3))
    elif name == "create_tentative_interview_hold":
        res = tools.create_tentative_interview_hold(
            slot=arguments.get("slot", ""),
            client_name=arguments.get("client_name", ""),
            job_id=arguments.get("job_id", "")
        )
    elif name == "create_email_draft":
        res = tools.create_email_draft(
            recipient=arguments.get("recipient", ""),
            subject=arguments.get("subject", ""),
            body=arguments.get("body", "")
        )
    else:
        raise ValueError(f"Unknown workspace tool: {name}")

    return {"content": [{"type": "text", "text": str(res)}], "raw": res}

def handle_jsonrpc(request: Dict[str, Any]) -> Dict[str, Any]:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list_tools()}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = call_tool(name, args)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
