"""FastAPI Pydantic Schemas for GigBid API."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserLoginRequest(BaseModel):
    username: str
    password: str
    persona_id: Optional[str] = "persona_aiml"

class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    persona_id: str
    active_profile: str
    connects_balance: int
    hourly_rate: float
    weekly_connects_budget: int

class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    skills: List[str]
    budget: float
    connects_cost: int
    client_spend: float
    client_hire_rate: float
    client_rating: float
    status: str

class ProposalDetailResponse(BaseModel):
    proposal_id: str
    job_id: str
    cover_letter: str
    bid_amount: float
    evidence_citations: List[str]
    status: str
    claims_verification: Optional[Dict[str, Any]] = None
    critic_notes: Optional[str] = None
    compliance_notes: Optional[str] = None
    dry_run_preview: Optional[Dict[str, Any]] = None

class ApprovalActionRequest(BaseModel):
    thread_id: str
    action: str # "approve", "reject", "edit"
    user_edited_text: Optional[str] = None
    rejection_reason: Optional[str] = None

class MessageSendRequest(BaseModel):
    thread_id: str
    content: str
