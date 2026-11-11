"""Portfolio MCP Server Prompts.
Offers reusable prompt templates for hosts like Claude Desktop or Cursor.
"""
from typing import Dict, Any

def get_prompt_template(name: str, arguments: Dict[str, Any]) -> str:
    """Render prompt template with provided arguments."""
    if name == "answer_screening_question":
        question = arguments.get("question", "")
        persona_name = arguments.get("persona_name", "Sarah Chen")
        return (
            f"You are {persona_name}. A prospective client asks:\n\n"
            f"\"{question}\"\n\n"
            "Using ONLY verified case studies and metrics from my portfolio MCP tools, "
            "provide a concise, high-impact 2-3 sentence answer with specific numbers and links to evidence."
        )
    elif name == "draft_evidence_summary":
        tech = arguments.get("technology", "LangGraph")
        return (
            f"Summarize all production projects where {tech} was deployed, "
            "listing client industry, deliverables, and quantitative results achieved."
        )
    return ""
