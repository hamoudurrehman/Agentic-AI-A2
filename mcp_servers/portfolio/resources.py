"""Portfolio MCP Server Resource Templates.
Supports loading full case studies, proposals, and skill summaries via URI templates.
"""
from typing import Dict, Any, Optional
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "personas")

def read_resource(uri: str, persona_id: str = "persona_aiml") -> Optional[Dict[str, Any]]:
    """Read resource by URI template.
    Supported URI patterns:
      - portfolio://case/{id}
      - portfolio://proposal/{id}
      - portfolio://skills
    """
    file_path = os.path.join(DATA_DIR, f"{persona_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if uri.startswith("portfolio://case/"):
        case_id = uri.replace("portfolio://case/", "")
        for cs in data.get("case_studies", []):
            if cs["id"] == case_id:
                return {"uri": uri, "mime_type": "application/json", "content": cs}
    elif uri.startswith("portfolio://proposal/"):
        prop_id = uri.replace("portfolio://proposal/", "")
        for prop in data.get("past_proposals", []):
            if prop["id"] == prop_id:
                return {"uri": uri, "mime_type": "application/json", "content": prop}
    elif uri == "portfolio://skills":
        return {"uri": uri, "mime_type": "application/json", "content": data.get("skills", [])}
        
    return None
