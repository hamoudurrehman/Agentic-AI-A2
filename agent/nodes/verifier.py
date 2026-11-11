"""Claim Verifier Node - Enforces R5 grounded claims discipline."""
from typing import Dict, Any
from gigbid.rag.verify import verify_and_sanitize_proposal
from gigbid.rag.ingest.loader import load_persona_chunks

def run_claim_verifier(state: Dict[str, Any]) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    if not draft:
        return {}

    persona_id = state.get("persona_id", "persona_aiml")
    chunks = load_persona_chunks(persona_id)
    evidence_dicts = [c.to_dict() for c in chunks]

    verification_result = verify_and_sanitize_proposal(draft.cover_letter, evidence_dicts)

    # Update draft with sanitized text
    draft.cover_letter = verification_result["sanitized_text"]

    trace_entry = {
        "node": "claim_verifier",
        "action": "verified_claims",
        "output": {
            "total_claims": verification_result["total_claims"],
            "unsupported_before": verification_result["unsupported_before"],
            "unsupported_after": verification_result["unsupported_after"],
            "sanitized_text": verification_result["sanitized_text"]
        },
        "tokens": 260,
        "cost_usd": 0.00026
    }

    return {
        "proposal_draft": draft,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 260
    }
