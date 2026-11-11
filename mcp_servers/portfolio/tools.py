"""Portfolio MCP Server Tools.
Provides read-only access to freelancer case studies, skills, past proposals, and code repos.
"""
from typing import List, Dict, Any, Optional
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "personas")

def _load_persona(persona_id: str = "persona_aiml") -> Dict[str, Any]:
    file_path = os.path.join(DATA_DIR, f"{persona_id}.json")
    if not os.path.exists(file_path):
        # Fallback to first available persona
        personas = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        if personas:
            file_path = os.path.join(DATA_DIR, personas[0])
        else:
            return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_evidence(requirement: str, k: int = 3, filters: Optional[Dict[str, Any]] = None, persona_id: str = "persona_aiml") -> List[Dict[str, Any]]:
    """Search portfolio for evidence supporting a given requirement or skill.
    
    Args:
        requirement: Natural language requirement or technology name
        k: Maximum number of evidence items to return
        filters: Optional filters (e.g. {'type': 'case_study', 'client_industry': 'FinTech'})
        persona_id: ID of the active persona
        
    Returns:
        List of evidence items with type, source, date, outcome, and content
    """
    persona = _load_persona(persona_id)
    items = []
    
    req_terms = requirement.lower().split()
    
    # 1. Search case studies
    for cs in persona.get("case_studies", []):
        score = sum(1 for term in req_terms if term in cs["title"].lower() or term in cs["full_text"].lower() or any(term in s.lower() for s in cs.get("skills", [])))
        if score > 0 or not requirement.strip():
            items.append({
                "id": cs["id"],
                "type": "case_study",
                "source": cs["title"],
                "date": "2025-2026",
                "outcome": "delivered_successfully",
                "skills": cs.get("skills", []),
                "summary": cs["deliverables"],
                "metrics": cs["metrics"],
                "score": score
            })
            
    # 2. Search repos
    for repo in persona.get("repos", []):
        score = sum(1 for term in req_terms if term in repo["name"].lower() or term in repo["description"].lower() or term in repo["readme"].lower())
        if score > 0 or not requirement.strip():
            items.append({
                "id": repo["name"],
                "type": "repo",
                "source": f"GitHub: {repo['name']}",
                "date": "2026",
                "outcome": "active_open_source",
                "skills": persona.get("skills", []),
                "summary": repo["description"],
                "metrics": "Production code with test coverage",
                "score": score
            })
            
    # 3. Search past proposals
    for prop in persona.get("past_proposals", []):
        score = sum(1 for term in req_terms if term in prop["job_title"].lower() or term in prop["proposal_text"].lower())
        if score > 0:
            items.append({
                "id": prop["id"],
                "type": "past_proposal",
                "source": prop["job_title"],
                "date": "2026",
                "outcome": prop.get("outcome", "unknown"),
                "skills": [],
                "summary": prop["proposal_text"][:140] + "...",
                "metrics": f"Outcome: {prop.get('outcome')}",
                "score": score
            })

    # Apply filters if provided
    if filters:
        if "type" in filters:
            items = [it for it in items if it["type"] == filters["type"]]
        if "outcome" in filters:
            items = [it for it in items if it["outcome"] == filters["outcome"]]
            
    # Sort by relevance score
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:k]

def get_case_study(id: str, persona_id: str = "persona_aiml") -> Optional[Dict[str, Any]]:
    """Retrieve full details of a specific case study by ID."""
    persona = _load_persona(persona_id)
    for cs in persona.get("case_studies", []):
        if cs["id"] == id:
            return cs
    return None

def list_skills(persona_id: str = "persona_aiml") -> List[str]:
    """List all verified skills associated with the active persona."""
    persona = _load_persona(persona_id)
    return persona.get("skills", [])
