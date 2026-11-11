"""Critic Node - Assesses grounding, personalization, and conciseness with max 2 loop limit."""
from typing import Dict, Any
from gigbid.agent.handoffs import Critique

def run_critic(state: Dict[str, Any]) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    job = state.get("job_raw", {})
    loop_count = state.get("critic_loop_count", 0)

    issues = []
    text = draft.cover_letter if draft else ""
    
    # Grounding check: has citations
    grounding_score = 0.90 if draft and draft.evidence_citations else 0.60
    if not draft or not draft.evidence_citations:
        issues.append("Proposal lacks explicit citations to portfolio case studies.")

    # Personalization check: references job title or core skills
    skills = job.get("skills", [])
    has_skill = any(s.lower() in text.lower() for s in skills)
    personalization_score = 0.92 if has_skill else 0.65
    if not has_skill:
        issues.append("Proposal should explicitly name client required technologies.")

    # Length check: concise (< 300 words)
    word_count = len(text.split())
    conciseness_score = 0.95 if word_count <= 250 else 0.70

    # Decision on acceptance:
    # If this is iteration 1 and there are issues, trigger revision loop; if loop_count >= 2, force proceed to avoid infinite loops
    is_acceptable = (len(issues) == 0) or (loop_count >= 2)
    revision_instructions = "; ".join(issues) if not is_acceptable else None

    critique = Critique(
        is_acceptable=is_acceptable,
        personalization_score=personalization_score,
        grounding_score=grounding_score,
        conciseness_score=conciseness_score,
        issues_found=issues,
        revision_instructions=revision_instructions,
        iteration=loop_count + 1
    )

    trace_entry = {
        "node": "critic",
        "action": "critiqued_draft",
        "output": critique.model_dump(),
        "tokens": 280,
        "cost_usd": 0.00028
    }

    return {
        "critique": critique,
        "critic_loop_count": loop_count + 1,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 280
    }
