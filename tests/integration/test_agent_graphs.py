"""Integration tests for LangGraph multi-agent bid graph and conversation graph."""
import pytest
from gigbid.agent.graphs.bid_graph import bid_graph_instance, get_checkpoint
from gigbid.agent.graphs.conversation_graph import conv_graph_instance
from gigbid.agent.memory.store import memory_store_instance

def test_bid_graph_qualified_job():
    job_raw = {
        "id": "job_test_qual",
        "title": "Build LangGraph agent with PostgreSQL checkpointer",
        "description": "Looking for a seasoned AI engineer to build a LangGraph workflow with parallel agents and FastAPI.",
        "skills": ["Python", "LangGraph", "FastAPI", "PostgreSQL"],
        "budget": 3000.0,
        "connects_cost": 8,
        "client_spend": 35000.0,
        "client_hire_rate": 0.85
    }

    state = bid_graph_instance.initialize_state(job_raw, persona_id="persona_aiml")
    state = bid_graph_instance.run_until_interrupt(state)

    # Verify decision is BID
    assert state["bid_decision"].decision == "bid"
    # Verify pricing quote created
    assert state["price_quote"].proposed_price > 2000.0
    # Verify proposal draft is populated and verified
    assert state["proposal_draft"] is not None
    assert len(state["proposal_draft"].evidence_citations) > 0
    # Verify compliance checks passed
    assert state["compliance_verdict"].passed is True
    # Verify graph paused at approval gate
    assert state["status_message"] == "PAUSED_PENDING_HUMAN_APPROVAL"
    assert state["approval_payload"] is not None

    # Test Human Approval
    resumed = bid_graph_instance.resume_from_approval(state["thread_id"], action="approve")
    assert resumed["user_approval_status"] == "approved"
    assert resumed["is_terminal"] is True

def test_bid_graph_scam_skip():
    scam_job = {
        "id": "job_test_scam",
        "title": "URGENT Telegram task",
        "description": "Contact telegram @scamteam for free unpaid test. We pay via direct crypto.",
        "skills": ["Python"],
        "budget": 500.0,
        "connects_cost": 4,
        "client_spend": 0.0,
        "client_hire_rate": 0.0
    }

    state = bid_graph_instance.initialize_state(scam_job, persona_id="persona_aiml")
    state = bid_graph_instance.run_until_interrupt(state)

    # Must be skipped immediately without spending connects or writing proposal
    assert state["bid_decision"].decision == "skip"
    assert state["is_terminal"] is True
    assert state["proposal_draft"] is None

def test_crash_and_resume_durability():
    job_raw = {
        "id": "job_crash_test",
        "title": "Enterprise RAG Pipeline with ChromaDB",
        "description": "Build production RAG with claim verification and FastAPI.",
        "skills": ["Python", "FastAPI", "RAG"],
        "budget": 2500.0,
        "connects_cost": 6,
        "client_spend": 20000.0,
        "client_hire_rate": 0.80
    }

    state = bid_graph_instance.initialize_state(job_raw, persona_id="persona_aiml")
    state = bid_graph_instance.run_until_interrupt(state)
    tid = state["thread_id"]

    # Simulate process crash: reload state strictly from checkpoint store
    recovered_state = get_checkpoint(tid)
    assert recovered_state is not None
    assert recovered_state["status_message"] == "PAUSED_PENDING_HUMAN_APPROVAL"

    # Human approves post-restart
    resumed = bid_graph_instance.resume_from_approval(tid, action="approve")
    assert resumed["user_approval_status"] == "approved"

def test_conversation_graph_flow():
    incoming = [{"sender": "Apex FinTech", "content": "We loved your proposal. Can we schedule an interview call tomorrow?"}]
    state = conv_graph_instance.initialize_state(job_id="job_gs_001", proposal_id="prop_001", incoming_messages=incoming)
    state = conv_graph_instance.run_until_approval(state)

    assert state["classified_intent"] == "interview_request"
    assert len(state["proposed_slots"]) > 0
    assert "interview" in state["suggested_reply"].lower()

    # Approve and send
    res = conv_graph_instance.approve_and_send(state["thread_id"])
    assert res["status"] == "sent"
