"""Agent Runs & Live SSE Telemetry Router."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from gigbid.agent.graphs.bid_graph import get_checkpoint, _checkpoints
from ..streaming import stream_agent_execution

router = APIRouter(prefix="/runs", tags=["runs"])

@router.get("")
def list_runs():
    runs = []
    for tid, st in _checkpoints.items():
        runs.append({
            "thread_id": tid,
            "trace_id": st.get("trace_id"),
            "job_id": st.get("job_id"),
            "status": st.get("status_message"),
            "tokens": st.get("token_usage", 0),
            "step_count": st.get("step_count", 0),
            "decision": st.get("bid_decision").decision if st.get("bid_decision") else None
        })
    return runs

@router.get("/{thread_id}")
def get_run_detail(thread_id: str):
    st = get_checkpoint(thread_id)
    if not st:
        raise HTTPException(status_code=404, detail="Run thread not found")
    return {
        "thread_id": thread_id,
        "trace_id": st.get("trace_id"),
        "status": st.get("status_message"),
        "execution_trace": st.get("execution_trace", []),
        "token_usage": st.get("token_usage", 0),
        "step_count": st.get("step_count", 0)
    }

@router.get("/{thread_id}/stream")
async def stream_run(thread_id: str):
    st = get_checkpoint(thread_id)
    if not st:
        raise HTTPException(status_code=404, detail="Run thread not found")
    return StreamingResponse(stream_agent_execution(st), media_type="text/event-stream")
