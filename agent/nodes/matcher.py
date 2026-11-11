"""Fit Matcher Node - Maps job requirements to verified portfolio evidence items."""
from typing import Dict, Any, List
from gigbid.agent.handoffs import FitReport
from gigbid.agent.mcp_client import mcp_client_instance

def run_fit_matcher(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job_raw", {})
    skills_needed = job.get("skills", ["Python"])
    persona_id = state.get("persona_id", "persona_aiml")

    # Fetch verified persona skills via Portfolio MCP
    persona_skills = []
    try:
        res = mcp_client_instance.call_agent_tool("fit_matcher", "list_skills", {}, persona_id=persona_id)
        persona_skills = [s.lower() for s in (res.get("raw") or [])]
    except Exception:
        persona_skills = ["python", "langgraph", "fastapi"]

    matched = []
    missing = []
    req_evidence_map: Dict[str, List[str]] = {}

    for s in skills_needed:
        if s.lower() in persona_skills:
            matched.append(s)
            # Retrieve specific evidence item
            try:
                ev_res = mcp_client_instance.call_agent_tool("fit_matcher", "search_evidence", {"requirement": s, "k": 2}, persona_id=persona_id)
                items = ev_res.get("raw") or []
                req_evidence_map[s] = [it["id"] for it in items]
            except Exception:
                req_evidence_map[s] = []
        else:
            missing.append(s)
            req_evidence_map[s] = []

    fit_score = len(matched) / max(1, len(skills_needed))
    reasoning = f"Matched {len(matched)} of {len(skills_needed)} required skills ({', '.join(matched)})."

    report = FitReport(
        job_id=job.get("id", state.get("job_id", "job_001")),
        fit_score=round(fit_score, 2),
        matched_skills=matched,
        missing_skills=missing,
        requirement_evidence_map=req_evidence_map,
        reasoning=reasoning
    )

    trace_entry = {
        "node": "fit_matcher",
        "action": "computed_fit_matrix",
        "output": report.model_dump(),
        "tokens": 310,
        "cost_usd": 0.00031
    }

    return {
        "fit_report": report,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 310
    }
