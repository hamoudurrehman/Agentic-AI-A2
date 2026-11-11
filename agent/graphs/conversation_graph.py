"""Conversation Graph Orchestrator.
Manages client conversation threads, intent classification, calendar slot holds via Workspace MCP,
and gated human approval before sending replies.
"""
import uuid
from typing import Dict, Any, List, Optional
from gigbid.agent.state import ConversationState
from gigbid.agent.nodes.liaison import run_client_liaison
from gigbid.agent.marketplace_port import marketplace_port_instance

_conv_checkpoints: Dict[str, Dict[str, Any]] = {}

class ConversationGraph:
    def __init__(self):
        pass

    def initialize_state(
        self,
        job_id: str,
        proposal_id: str,
        incoming_messages: List[Dict[str, Any]],
        client_id: str = "client_unknown"
    ) -> ConversationState:
        tid = f"conv_{uuid.uuid4().hex[:8]}"
        state: ConversationState = {
            "thread_id": tid,
            "trace_id": f"trace_{uuid.uuid4().hex[:8]}",
            "client_id": client_id,
            "job_id": job_id,
            "proposal_id": proposal_id,
            "incoming_messages": incoming_messages,
            "classified_intent": None,
            "suggested_reply": None,
            "proposed_slots": [],
            "calendar_hold_id": None,
            "approval_status": "pending_human_approval",
            "execution_trace": [],
            "status_message": "INITIALIZED"
        }
        _conv_checkpoints[tid] = state
        return state

    def run_until_approval(self, state: ConversationState) -> ConversationState:
        tid = state["thread_id"]
        liaison_out = run_client_liaison(state)
        state["classified_intent"] = liaison_out["classified_intent"]
        state["suggested_reply"] = liaison_out["suggested_reply"]
        state["proposed_slots"] = liaison_out["proposed_slots"]
        state["calendar_hold_id"] = liaison_out["calendar_hold_id"]
        state["execution_trace"] += liaison_out["execution_trace"]
        state["status_message"] = liaison_out["status_message"]
        _conv_checkpoints[tid] = state
        return state

    def approve_and_send(self, thread_id: str, final_reply: Optional[str] = None) -> Dict[str, Any]:
        state = _conv_checkpoints.get(thread_id)
        if not state:
            raise ValueError(f"Conversation thread {thread_id} not found.")

        reply_content = final_reply or state["suggested_reply"]

        # Send via marketplace port
        res = marketplace_port_instance.send_message(
            job_id=state["job_id"],
            proposal_id=state["proposal_id"],
            content=reply_content,
            idempotency_key=f"idemp_{thread_id}",
            user_id="default_user",
            trace_id=state["trace_id"]
        )
        state["approval_status"] = "sent"
        state["status_message"] = "MESSAGE_SENT"
        return res

conv_graph_instance = ConversationGraph()
