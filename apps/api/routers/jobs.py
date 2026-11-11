"""Jobs & Inbox Router."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from gigbid.mcp_servers.marketplace.server import get_adapter
from gigbid.agent.graphs.bid_graph import bid_graph_instance, get_checkpoint
from .auth import CURRENT_SESSION

router = APIRouter(prefix="/jobs", tags=["jobs"])

# In-memory thread registry for active jobs
JOB_THREADS: Dict[str, str] = {} # job_id -> thread_id

@router.get("")
def list_jobs(query: str = "", limit: int = 15):
    adapter = get_adapter()
    return adapter.search_jobs(query=query, limit=limit)

@router.get("/{job_id}")
def get_job_detail(job_id: str):
    adapter = get_adapter()
    job = adapter.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if analysis has run for this job
    thread_id = JOB_THREADS.get(job_id)
    analysis = None
    if thread_id:
        st = get_checkpoint(thread_id)
        if st:
            analysis = {
                "job_spec": st.get("job_spec").model_dump() if st.get("job_spec") else None,
                "risk_report": st.get("risk_report").model_dump() if st.get("risk_report") else None,
                "fit_report": st.get("fit_report").model_dump() if st.get("fit_report") else None,
                "bid_decision": st.get("bid_decision").model_dump() if st.get("bid_decision") else None,
                "price_quote": st.get("price_quote").model_dump() if st.get("price_quote") else None,
                "thread_id": thread_id,
                "status_message": st.get("status_message")
            }

    return {"job": job, "analysis": analysis}

@router.post("/{job_id}/run-agent")
def run_agent_on_job(job_id: str):
    adapter = get_adapter()
    job = adapter.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    state = bid_graph_instance.initialize_state(job, persona_id=CURRENT_SESSION["persona_id"])
    executed_state = bid_graph_instance.run_until_interrupt(state)
    JOB_THREADS[job_id] = executed_state["thread_id"]

    return {
        "thread_id": executed_state["thread_id"],
        "status": executed_state["status_message"],
        "decision": executed_state["bid_decision"].decision if executed_state.get("bid_decision") else "unknown",
        "has_approval_pending": executed_state.get("approval_payload") is not None
    }
