"""Client Liaison Node - Manages client communications and interview scheduling."""
from typing import Dict, Any, List
from gigbid.agent.mcp_client import mcp_client_instance

def run_client_liaison(state: Dict[str, Any]) -> Dict[str, Any]:
    msgs = state.get("incoming_messages", [])
    latest_msg = msgs[-1] if msgs else {"content": "Hello, can we discuss this?"}
    content = latest_msg.get("content", "").lower()

    # 1. Classify intent
    if any(k in content for k in ["interview", "call", "meet", "schedule", "zoom", "chat"]):
        intent = "interview_request"
    elif any(k in content for k in ["discount", "rate", "budget", "cheaper", "price"]):
        intent = "negotiation"
    elif any(k in content for k in ["telegram", "whatsapp", "crypto", "pay outside"]):
        intent = "scam_signal"
    else:
        intent = "question"

    proposed_slots = []
    calendar_hold = None

    if intent == "interview_request":
        # Call Workspace MCP
        try:
            res = mcp_client_instance.call_agent_tool("client_liaison", "get_free_calendar_slots", {"days_ahead": 3})
            proposed_slots = (res.get("raw") or [])[:3]
            if proposed_slots:
                hold_res = mcp_client_instance.call_agent_tool(
                    "client_liaison",
                    "create_tentative_interview_hold",
                    {"slot": proposed_slots[0], "client_name": latest_msg.get("sender", "Client"), "job_id": state.get("job_id", "")}
                )
                calendar_hold = hold_res.get("raw", {}).get("hold_id")
        except Exception:
            proposed_slots = ["Tomorrow 10:00 AM PKT", "Thursday 02:00 PM PKT"]

        suggested_reply = (
            f"Thank you for reaching out! I would be delighted to schedule an interview and speak in detail. "
            f"Here are a few slots that work well for me:\n" +
            "\n".join([f"- {s}" for s in proposed_slots]) +
            "\nPlease let me know if any of these suit your schedule."
        )
    elif intent == "negotiation":
        suggested_reply = (
            "Thank you for following up on the budget. The scope outlined requires rigorous testing, "
            "complete test coverage, and PostgreSQL checkpointing. I can offer a 10% milestone discount "
            "if we streamline the initial delivery cycle."
        )
    elif intent == "scam_signal":
        suggested_reply = "To comply with marketplace policy, all communications and payments must remain strictly on-platform."
    else:
        suggested_reply = (
            "Thank you for your question. Yes, my previous deployment in this category achieved "
            "sub-second retrieval and 94% grounding using LangGraph and hybrid RAG. I would be happy to detail the exact architecture."
        )

    trace_entry = {
        "node": "client_liaison",
        "action": "drafted_liaison_reply",
        "output": {
            "intent": intent,
            "suggested_reply": suggested_reply,
            "proposed_slots": proposed_slots
        },
        "tokens": 240,
        "cost_usd": 0.00024
    }

    return {
        "classified_intent": intent,
        "suggested_reply": suggested_reply,
        "proposed_slots": proposed_slots,
        "calendar_hold_id": calendar_hold,
        "execution_trace": [trace_entry],
        "status_message": "PAUSED_PENDING_MESSAGE_APPROVAL"
    }
