"""Human Approval Gate Router."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.api_models import ApprovalActionRequest
from gigbid.agent.graphs.bid_graph import bid_graph_instance, get_checkpoint, _checkpoints

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("/pending")
def list_pending_approvals():
    pending = []
    for tid, st in _checkpoints.items():
        if st.get("status_message") == "PAUSED_PENDING_HUMAN_APPROVAL" and st.get("approval_payload"):
            payload = st["approval_payload"]
            pending.append({
                "thread_id": tid,
                "job_id": st["job_id"],
                "job_title": st.get("job_raw", {}).get("title", ""),
                "proposal_id": payload.proposal_id,
                "bid_amount": payload.price_quote.proposed_price if payload.price_quote else 0,
                "connects_cost": payload.price_quote.connects_cost if payload.price_quote else 6,
                "risk_level": payload.risk_report.risk_level if payload.risk_report else "low",
                "preview": payload.dry_run_preview
            })
    return pending

@router.post("/action")
def submit_approval_action(req: ApprovalActionRequest):
    st = get_checkpoint(req.thread_id)
    if not st:
        raise HTTPException(status_code=404, detail="Thread checkpoint not found")

    resumed = bid_graph_instance.resume_from_approval(
        thread_id=req.thread_id,
        action=req.action,
        user_edited_text=req.user_edited_text,
        rejection_reason=req.rejection_reason
    )

    return {
        "status": "success",
        "thread_id": req.thread_id,
        "action": req.action,
        "result_status": resumed.get("status_message")
    }
