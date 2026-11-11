"""Structured Pydantic hand-off models exchanged between agents."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class JobSpec(BaseModel):
    job_id: str
    deliverables: List[str]
    required_skills: List[str]
    budget: float
    estimated_timeline: str
    screening_questions: List[str] = Field(default_factory=list)
    hidden_needs: List[str] = Field(default_factory=list)

class RiskReport(BaseModel):
    job_id: str
    client_score: float = Field(ge=0.0, le=100.0)
    is_scam: bool
    is_free_work_request: bool
    is_off_platform_request: bool
    injected_instructions_detected: bool
    risk_level: str # "low", "medium", "high", "critical"
    reasons: List[str]

class FitReport(BaseModel):
    job_id: str
    fit_score: float = Field(ge=0.0, le=1.0)
    matched_skills: List[str]
    missing_skills: List[str]
    requirement_evidence_map: Dict[str, List[str]] # requirement -> list of evidence chunk_ids
    reasoning: str

class BidDecision(BaseModel):
    job_id: str
    decision: str # "bid", "skip", "watch"
    confidence: float
    reason: str

class PriceQuote(BaseModel):
    job_id: str
    proposed_price: float
    floor_price: float
    pricing_strategy: str # "fixed_premium", "standard_market", "competitive_discount"
    connects_cost: int
    roi_expected: str
    rationale: str

class ProposalDraft(BaseModel):
    proposal_id: str
    job_id: str
    cover_letter: str
    screening_answers: Dict[str, str] = Field(default_factory=dict)
    evidence_citations: List[str] = Field(default_factory=list)
    iteration: int = 1

class Critique(BaseModel):
    is_acceptable: bool
    personalization_score: float
    grounding_score: float
    conciseness_score: float
    issues_found: List[str] = Field(default_factory=list)
    revision_instructions: Optional[str] = None
    iteration: int

class ComplianceVerdict(BaseModel):
    passed: bool
    sanitized_text: str
    violations_detected: List[str] = Field(default_factory=list)
    pii_masked: bool = True
    no_guarantees_enforced: bool = True
    no_off_platform_enforced: bool = True

class ApprovalPayload(BaseModel):
    job_id: str
    proposal_id: str
    draft: ProposalDraft
    risk_report: RiskReport
    price_quote: PriceQuote
    requirement_evidence_map: Dict[str, List[str]]
    dry_run_preview: Dict[str, Any]
    critic_notes: Optional[str] = None
    compliance_notes: Optional[str] = None
    status: str = "pending_human_approval" # "pending_human_approval", "approved", "rejected", "edited"
