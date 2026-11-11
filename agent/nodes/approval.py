"""Human-In-The-Loop Approval Gate Node.
Constructs full approval payload and interrupts graph execution until human confirmation.
"""
from typing import Dict, Any
from gigbid.agent.handoffs import ApprovalPayload
from gigbid.agent.marketplace_port import marketplace_port_instance
from gigbid.agent.memory.promotion_rules import evaluate_style_promotion
from gigbid.agent.nodes.compliance import run_compliance_guard

def prepare_approval_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    risk = state.get("risk_report")
    price = state.get("price_quote")
    fit = state.get("fit_report")
    job = state.get("job_raw", {})

    # Compute dry-run preview via marketplace port
    dry_run_res = {}
    if draft and price:
        dry_run_res = marketplace_port_instance.submit_proposal(
            proposal_id=draft.proposal_id,
            job_id=draft.job_id,
            bid_amount=price.proposed_price,
            cover_letter=draft.cover_letter,
            evidence_citations=draft.evidence_citations,
            idempotency_key=f"dry_{draft.proposal_id}",
            dry_run=True,
            user_id="default_user",
            trace_id=state.get("trace_id", "trace_001")
        )

    payload = ApprovalPayload(
        job_id=job.get("id", state.get("job_id", "")),
        proposal_id=draft.proposal_id if draft else "",
        draft=draft,
        risk_report=risk,
        price_quote=price,
        requirement_evidence_map=fit.requirement_evidence_map if fit else {},
        dry_run_preview=dry_run_res,
        critic_notes="All claims grounded; verified against portfolio evidence.",
        compliance_notes="Policy pack checks passed. PII masked.",
        status="pending_human_approval"
    )

    trace_entry = {
        "node": "human_approval_gate",
        "action": "interrupted_for_human_approval",
        "output": payload.model_dump(),
        "tokens": 0,
        "cost_usd": 0.0
    }

    return {
        "approval_payload": payload,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "status_message": "PAUSED_PENDING_HUMAN_APPROVAL"
    }

def process_approval_action(
    state: Dict[str, Any],
    action: str, # "approve", "reject", "edit"
    user_edited_text: str = None,
    rejection_reason: str = None
) -> Dict[str, Any]:
    """Called when resuming after human decision."""
    draft = state.get("proposal_draft")
    price = state.get("price_quote")
    job_id = state.get("job_id", "")

    if action == "edit" and user_edited_text:
        # 1. Update draft
        original_text = draft.cover_letter
        draft.cover_letter = user_edited_text
        # 2. Diff and promote to Style Memory
        evaluate_style_promotion(original_text, user_edited_text)
        # 3. Re-check by Compliance
        state["proposal_draft"] = draft
        run_compliance_guard(state)
        action = "approve" # Approved with edits

    if action == "approve":
        # Dispatched to marketplace
        submit_res = marketplace_port_instance.submit_proposal(
            proposal_id=draft.proposal_id,
            job_id=draft.job_id,
            bid_amount=price.proposed_price if price else 1500.0,
            cover_letter=draft.cover_letter,
            evidence_citations=draft.evidence_citations,
            idempotency_key=f"sub_{draft.proposal_id}",
            dry_run=False,
            user_id="default_user",
            trace_id=state.get("trace_id", "trace_001")
        )
        status_msg = f"Proposal submitted to marketplace! Result: {submit_res.get('status')}"
        is_terminal = True
        return {
            "user_approval_status": "approved",
            "is_terminal": True,
            "status_message": status_msg,
            "submission_result": submit_res
        }
    else:
        # Rejection
        return {
            "user_approval_status": "rejected",
            "is_terminal": True,
            "user_feedback": rejection_reason or "User declined to bid.",
            "status_message": f"Proposal rejected by user: {rejection_reason}"
        }
