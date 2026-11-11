"""Data models for GigSim marketplace."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ClientProfile(BaseModel):
    id: str
    company_name: str
    total_spent: float
    jobs_posted: int
    hire_rate: float
    rating: float
    preferred_skills: List[str]
    disliked_phrases: List[str] = Field(default_factory=lambda: ["guarantee", "best developer", "100%", "cheap"])
    budget_ceiling: float

class JobPosting(BaseModel):
    id: str
    title: str
    description: str
    skills: List[str]
    budget: float
    connects_cost: int = 6
    client_id: str
    posted_at: str = "2026-11-10T10:00:00Z"
    status: str = "open"
    has_injection: bool = False

class ProposalSubmission(BaseModel):
    proposal_id: str
    job_id: str
    freelancer_id: str
    bid_amount: float
    cover_letter: str
    evidence_citations: List[str] = Field(default_factory=list)
    idempotency_key: str
    dry_run: bool = False

class ProposalResult(BaseModel):
    proposal_id: str
    status: str # "draft", "submitted", "viewed", "replied", "interview", "hired", "rejected"
    client_feedback: Optional[str] = None
    connects_deducted: int = 0
    reply_probability: float = 0.0
