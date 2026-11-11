"""Portfolio MCP Server implementation.
Adheres to Model Context Protocol (MCP) JSON-RPC 2.0 specifications.
"""
from typing import Dict, Any, List
from . import tools, resources, prompts

SERVER_INFO = {
    "name": "gigbid-portfolio-server",
    "version": "1.0.0",
    "description": "Read-only portfolio MCP server exposing verified developer evidence, case studies, and skills."
}

TOOLS_MANIFEST = [
    {
        "name": "search_evidence",
        "description": "Search portfolio for verified evidence items supporting a technical requirement or skill.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requirement": {"type": "string", "description": "The client requirement or keyword"},
                "k": {"type": "integer", "default": 3, "description": "Number of items to retrieve"},
                "filters": {"type": "object", "description": "Optional filters such as type or outcome"}
            },
            "required": ["requirement"]
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True
        }
    },
    {
        "name": "get_case_study",
        "description": "Retrieve full case study text, metrics, and outcomes by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Case study unique identifier"}
            },
            "required": ["id"]
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True
        }
    },
    {
        "name": "list_skills",
        "description": "List all verified technical skills for the freelancer.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True
        }
    }
]

def list_tools() -> List[Dict[str, Any]]:
    return TOOLS_MANIFEST

def call_tool(name: str, arguments: Dict[str, Any], persona_id: str = "persona_aiml") -> Dict[str, Any]:
    if name == "search_evidence":
        res = tools.search_evidence(
            requirement=arguments.get("requirement", ""),
            k=arguments.get("k", 3),
            filters=arguments.get("filters"),
            persona_id=persona_id
        )
        return {"content": [{"type": "text", "text": str(res)}], "raw": res}
    elif name == "get_case_study":
        res = tools.get_case_study(id=arguments.get("id", ""), persona_id=persona_id)
        return {"content": [{"type": "text", "text": str(res)}], "raw": res}
    elif name == "list_skills":
        res = tools.list_skills(persona_id=persona_id)
        return {"content": [{"type": "text", "text": str(res)}], "raw": res}
    else:
        raise ValueError(f"Unknown tool: {name}")

def handle_jsonrpc(request: Dict[str, Any], persona_id: str = "persona_aiml") -> Dict[str, Any]:
    """Handle incoming MCP JSON-RPC 2.0 requests."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list_tools()}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = call_tool(name, args, persona_id=persona_id)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
    elif method == "resources/read":
        uri = params.get("uri")
        res = resources.read_resource(uri, persona_id=persona_id)
        if res:
            return {"jsonrpc": "2.0", "id": req_id, "result": {"contents": [res]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Resource not found"}}
    elif method == "prompts/get":
        name = params.get("name")
        args = params.get("arguments", {})
        prompt_text = prompts.get_prompt_template(name, args)
        return {"jsonrpc": "2.0", "id": req_id, "result": {"messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}]}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
