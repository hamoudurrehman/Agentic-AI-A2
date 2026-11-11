"""Proposals and Proposal Studio Router."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from gigbid.agent.graphs.bid_graph import get_checkpoint
from gigbid.rag.verify import split_claims, check_claim_support
from gigbid.rag.ingest.loader import load_persona_chunks
from .jobs import JOB_THREADS
from .auth import CURRENT_SESSION

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.get("/{proposal_id}")
def get_proposal_studio(proposal_id: str):
    # Find matching checkpoint
    target_state = None
    for tid in JOB_THREADS.values():
        st = get_checkpoint(tid)
        if st and st.get("proposal_draft") and st["proposal_draft"].proposal_id == proposal_id:
            target_state = st
            break

    if not target_state:
        # Fallback search all checkpoints
        from gigbid.agent.graphs.bid_graph import _checkpoints
        for tid, st in _checkpoints.items():
            if st and st.get("proposal_draft") and st["proposal_draft"].proposal_id == proposal_id:
                target_state = st
                break

    if not target_state or not target_state.get("proposal_draft"):
        raise HTTPException(status_code=404, detail="Proposal draft not found")

    draft = target_state["proposal_draft"]
    price = target_state.get("price_quote")
    approval = target_state.get("approval_payload")

    # Build claim-level hover metadata
    chunks = load_persona_chunks(CURRENT_SESSION["persona_id"])
    evidence_texts = [c.text for c in chunks]

    claims = split_claims(draft.cover_letter)
    claim_details = []
    for c in claims:
        status, score, snippet = check_claim_support(c, evidence_texts)
        claim_details.append({
            "claim_text": c,
            "status": status,
            "grounding_score": round(score, 2),
            "evidence_source": snippet or "Direct Technical Specification"
        })

    return {
        "proposal_id": draft.proposal_id,
        "job_id": draft.job_id,
        "thread_id": target_state["thread_id"],
        "cover_letter": draft.cover_letter,
        "bid_amount": price.proposed_price if price else 1500.0,
        "connects_cost": price.connects_cost if price else 6,
        "evidence_citations": draft.evidence_citations,
        "claims_hover_data": claim_details,
        "dry_run_preview": approval.dry_run_preview if approval else None,
        "status": target_state.get("status_message")
    }
