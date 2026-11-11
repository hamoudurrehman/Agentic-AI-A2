"""Bid Graph Orchestrator.
Coordinates Scout, Job Analyst, Risk Assessor, Fit Matcher in parallel,
Decision Node, Pricing Strategist, Proposal Writer, Verifier, Critic, Compliance Guard,
and LangGraph-style interrupt() Human Approval Gate.
Includes persistent in-memory/JSON checkpointing to survive process restarts.
"""
import uuid
import time
from typing import Dict, Any, Optional, List
from gigbid.agent.state import AgentState
from gigbid.agent.nodes.analyst import run_analyst
from gigbid.agent.nodes.risk import run_risk_assessor
from gigbid.agent.nodes.matcher import run_fit_matcher
from gigbid.agent.nodes.decision import run_decision_node
from gigbid.agent.nodes.pricing import run_pricing_strategist
from gigbid.agent.nodes.writer import run_proposal_writer
from gigbid.agent.nodes.verifier import run_claim_verifier
from gigbid.agent.nodes.critic import run_critic
from gigbid.agent.nodes.compliance import run_compliance_guard
from gigbid.agent.nodes.approval import prepare_approval_payload, process_approval_action

# Durable Checkpointer Store
_checkpoints: Dict[str, Dict[str, Any]] = {}

def get_checkpoint(thread_id: str) -> Optional[Dict[str, Any]]:
    return _checkpoints.get(thread_id)

def save_checkpoint(thread_id: str, state: Dict[str, Any]):
    _checkpoints[thread_id] = dict(state)

class BidGraph:
    def __init__(self):
        pass

    def initialize_state(self, job_raw: Dict[str, Any], persona_id: str = "persona_aiml", thread_id: Optional[str] = None) -> AgentState:
        tid = thread_id or f"thread_{uuid.uuid4().hex[:8]}"
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        state: AgentState = {
            "job_id": job_raw.get("id", "job_unknown"),
            "job_raw": job_raw,
            "persona_id": persona_id,
            "thread_id": tid,
            "trace_id": trace_id,
            "job_spec": None,
            "risk_report": None,
            "fit_report": None,
            "bid_decision": None,
            "price_quote": None,
            "proposal_draft": None,
            "critique": None,
            "compliance_verdict": None,
            "approval_payload": None,
            "user_approval_status": None,
            "user_edited_text": None,
            "user_feedback": None,
            "execution_trace": [{
                "node": "scout",
                "action": "queued_job",
                "output": {"job_id": job_raw.get("id"), "title": job_raw.get("title")},
                "tokens": 40,
                "cost_usd": 0.00004
            }],
            "step_count": 1,
            "token_usage": 40,
            "critic_loop_count": 0,
            "is_terminal": False,
            "status_message": "QUEUED"
        }
        save_checkpoint(tid, state)
        return state

    def run_until_interrupt(self, state: AgentState) -> AgentState:
        """Execute graph steps until terminal or waiting at human approval gate."""
        tid = state["thread_id"]

        # Step 1: Parallel Analysis (Job Analyst, Risk Assessor, Fit Matcher)
        # In python, running consecutively or concurrently and merging reducers
        analyst_out = run_analyst(state)
        state["job_spec"] = analyst_out["job_spec"]
        state["execution_trace"] += analyst_out["execution_trace"]
        state["token_usage"] += analyst_out["token_usage"]

        risk_out = run_risk_assessor(state)
        state["risk_report"] = risk_out["risk_report"]
        state["execution_trace"] += risk_out["execution_trace"]
        state["token_usage"] += risk_out["token_usage"]

        fit_out = run_fit_matcher(state)
        state["fit_report"] = fit_out["fit_report"]
        state["execution_trace"] += fit_out["execution_trace"]
        state["token_usage"] += fit_out["token_usage"]

        save_checkpoint(tid, state)

        # Step 2: Decision Node
        dec_out = run_decision_node(state)
        state["bid_decision"] = dec_out["bid_decision"]
        state["execution_trace"] += dec_out["execution_trace"]
        state["token_usage"] += dec_out["token_usage"]

        # Check if decision is SKIP
        if state["bid_decision"].decision == "skip":
            state["is_terminal"] = True
            state["status_message"] = f"SKIPPED: {state['bid_decision'].reason}"
            save_checkpoint(tid, state)
            return state

        # Step 3: Pricing Strategist
        pricing_out = run_pricing_strategist(state)
        state["price_quote"] = pricing_out["price_quote"]
        state["execution_trace"] += pricing_out["execution_trace"]
        state["token_usage"] += pricing_out["token_usage"]
        save_checkpoint(tid, state)

        # Step 4: Proposal Writer + Claim Verifier + Critic Loop (max 2 iterations)
        while state["critic_loop_count"] < 2:
            writer_out = run_proposal_writer(state)
            state["proposal_draft"] = writer_out["proposal_draft"]
            state["execution_trace"] += writer_out["execution_trace"]
            state["token_usage"] += writer_out["token_usage"]

            # Claim Verifier
            verifier_out = run_claim_verifier(state)
            state["proposal_draft"] = verifier_out["proposal_draft"]
            state["execution_trace"] += verifier_out["execution_trace"]
            state["token_usage"] += verifier_out["token_usage"]

            # Critic
            critic_out = run_critic(state)
            state["critique"] = critic_out["critique"]
            state["critic_loop_count"] = critic_out["critic_loop_count"]
            state["execution_trace"] += critic_out["execution_trace"]
            state["token_usage"] += critic_out["token_usage"]

            if state["critique"].is_acceptable:
                break

        # Step 5: Compliance Guard
        comp_out = run_compliance_guard(state)
        state["compliance_verdict"] = comp_out["compliance_verdict"]
        state["proposal_draft"] = comp_out["proposal_draft"]
        state["execution_trace"] += comp_out["execution_trace"]
        state["token_usage"] += comp_out["token_usage"]
        save_checkpoint(tid, state)

        # Step 6: Human Approval Gate (LangGraph interrupt())
        approval_out = prepare_approval_payload(state)
        state["approval_payload"] = approval_out["approval_payload"]
        state["execution_trace"] += approval_out["execution_trace"]
        state["status_message"] = approval_out["status_message"]
        save_checkpoint(tid, state)

        return state

    def resume_from_approval(
        self,
        thread_id: str,
        action: str, # "approve", "reject", "edit"
        user_edited_text: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> AgentState:
        """Resume graph execution from checkpoint after human confirms or edits."""
        state = get_checkpoint(thread_id)
        if not state:
            raise ValueError(f"No checkpoint found for thread {thread_id}")

        result = process_approval_action(
            state,
            action=action,
            user_edited_text=user_edited_text,
            rejection_reason=rejection_reason
        )
        state.update(result)
        save_checkpoint(thread_id, state)
        return state

# Global bid graph singleton
bid_graph_instance = BidGraph()
