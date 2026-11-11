"""LangGraph State Design with TypedDict, Reducers, and Trace Discipline."""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator
from .handoffs import (
    JobSpec, RiskReport, FitReport, BidDecision,
    PriceQuote, ProposalDraft, Critique, ComplianceVerdict, ApprovalPayload
)

def trace_reducer(existing: List[Dict[str, Any]], new_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return existing + new_items

class AgentState(TypedDict):
    # Core Job Context
    job_id: str
    job_raw: Dict[str, Any]
    persona_id: str
    thread_id: str
    trace_id: str
    
    # Structured Agent Artifacts
    job_spec: Optional[JobSpec]
    risk_report: Optional[RiskReport]
    fit_report: Optional[FitReport]
    bid_decision: Optional[BidDecision]
    price_quote: Optional[PriceQuote]
    proposal_draft: Optional[ProposalDraft]
    critique: Optional[Critique]
    compliance_verdict: Optional[ComplianceVerdict]
    
    # Human in the Loop / Interrupt State
    approval_payload: Optional[ApprovalPayload]
    user_approval_status: Optional[str] # "approved", "rejected", "edited"
    user_edited_text: Optional[str]
    user_feedback: Optional[str]

    # Execution Trace (Kept for audit & observability)
    execution_trace: Annotated[List[Dict[str, Any]], trace_reducer]
    
    # Budgets & Counters
    step_count: int
    token_usage: int
    critic_loop_count: int
    is_terminal: bool
    status_message: str

class ConversationState(TypedDict):
    thread_id: str
    trace_id: str
    client_id: str
    job_id: str
    proposal_id: str
    incoming_messages: List[Dict[str, Any]]
    classified_intent: Optional[str] # "question", "negotiation", "interview_request", "scam_signal"
    suggested_reply: Optional[str]
    proposed_slots: List[str]
    calendar_hold_id: Optional[str]
    approval_status: Optional[str]
    execution_trace: Annotated[List[Dict[str, Any]], trace_reducer]
    status_message: str
