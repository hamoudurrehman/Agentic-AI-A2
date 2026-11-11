"""Client Messages and Pipeline Router."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from gigbid.mcp_servers.marketplace.server import get_adapter
from gigbid.agent.graphs.conversation_graph import conv_graph_instance, _conv_checkpoints
from ..schemas.api_models import MessageSendRequest

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("")
def list_messages(job_id: Optional[str] = None):
    adapter = get_adapter()
    return adapter.list_messages(job_id=job_id)

@router.post("/process-thread")
def process_conversation_thread(job_id: str, proposal_id: str):
    adapter = get_adapter()
    msgs = adapter.list_messages(job_id=job_id)
    if not msgs:
        msgs = [{"sender": "Client", "content": "Hello! We reviewed your proposal and would like to speak."}]

    state = conv_graph_instance.initialize_state(job_id=job_id, proposal_id=proposal_id, incoming_messages=msgs)
    state = conv_graph_instance.run_until_approval(state)

    return {
        "thread_id": state["thread_id"],
        "classified_intent": state["classified_intent"],
        "suggested_reply": state["suggested_reply"],
        "proposed_slots": state["proposed_slots"],
        "calendar_hold_id": state["calendar_hold_id"],
        "status": state["status_message"]
    }

@router.post("/approve-and-send")
def approve_and_send_message(req: MessageSendRequest):
    res = conv_graph_instance.approve_and_send(req.thread_id, final_reply=req.content)
    return {"status": "sent", "result": res}
