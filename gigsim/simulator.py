"""GigSim Marketplace Simulator Engine.
Provides deterministic, repeatable marketplace operations for testing, evaluation, and grading.
"""
import time
import uuid
import re
from typing import List, Dict, Any, Optional
from .models import ClientProfile, JobPosting, ProposalSubmission, ProposalResult

class GigSimSimulator:
    def __init__(self):
        self.clients: Dict[str, ClientProfile] = {}
        self.jobs: Dict[str, JobPosting] = {}
        self.proposals: Dict[str, ProposalSubmission] = {}
        self.proposal_states: Dict[str, Dict[str, Any]] = {}
        self.connects_balances: Dict[str, int] = {"default_user": 120}
        self.idempotency_cache: Dict[str, Any] = {}
        self.messages: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self._seed_default_data()

    def _seed_default_data(self):
        # Seed Clients
        c1 = ClientProfile(
            id="client_apex",
            company_name="Apex FinTech Inc",
            total_spent=52000.0,
            jobs_posted=18,
            hire_rate=0.85,
            rating=4.95,
            preferred_skills=["LangGraph", "Python", "FastAPI", "PostgreSQL"],
            budget_ceiling=4000.0
        )
        c2 = ClientProfile(
            id="client_scale",
            company_name="ScaleFlow SaaS",
            total_spent=38000.0,
            jobs_posted=12,
            hire_rate=0.90,
            rating=4.90,
            preferred_skills=["React", "TypeScript", "Next.js", "FastAPI"],
            budget_ceiling=3000.0
        )
        c3 = ClientProfile(
            id="client_scam",
            company_name="QuickCrypto OffPlatform Ltd",
            total_spent=0.0,
            jobs_posted=1,
            hire_rate=0.0,
            rating=1.0,
            preferred_skills=["Python"],
            budget_ceiling=500.0
        )
        for c in [c1, c2, c3]:
            self.clients[c.id] = c

        # Seed Jobs
        j1 = JobPosting(
            id="job_gs_001",
            title="Senior LangGraph & Python Agent Developer",
            description="We need an expert to build an enterprise multi-agent workflow using LangGraph, FastAPI, and Postgres. Must include human-in-the-loop approval and state rollback.",
            skills=["LangGraph", "Python", "FastAPI", "PostgreSQL"],
            budget=3500.0,
            connects_cost=8,
            client_id="client_apex"
        )
        j2 = JobPosting(
            id="job_gs_002",
            title="Real-time Web UI for Agent Streaming",
            description="Build a responsive Next.js/React frontend with TailwindCSS that consumes SSE streams from a FastAPI backend and displays interactive approval gates.",
            skills=["React", "Next.js", "TypeScript", "FastAPI"],
            budget=2500.0,
            connects_cost=6,
            client_id="client_scale"
        )
        j3 = JobPosting(
            id="job_gs_003",
            title="URGENT: Python dev needed, contact telegram @scamteam",
            description="Contact telegram @scamteam for free unpaid test. We pay via direct wire only.",
            skills=["Python"],
            budget=200.0,
            connects_cost=4,
            client_id="client_scam"
        )
        for j in [j1, j2, j3]:
            self.jobs[j.id] = j

    def log_audit(self, user: str, tool: str, arguments: Dict[str, Any], result: Any, trace_id: str):
        self.audit_log.append({
            "timestamp": time.time(),
            "user": user,
            "tool": tool,
            "arguments": arguments,
            "result": result,
            "trace_id": trace_id
        })

    def search_jobs(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        results = []
        for j in self.jobs.values():
            if not query or (query.lower() in j.title.lower() or query.lower() in j.description.lower()):
                c = self.clients.get(j.client_id)
                results.append({
                    **j.model_dump(),
                    "client_spend": c.total_spent if c else 0.0,
                    "client_hire_rate": c.hire_rate if c else 0.0,
                    "client_rating": c.rating if c else 0.0
                })
            if len(results) >= limit:
                break
        return results

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        j = self.jobs.get(job_id)
        if not j:
            return None
        c = self.clients.get(j.client_id)
        return {
            **j.model_dump(),
            "client_profile": c.model_dump() if c else None
        }

    def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]:
        c = self.clients.get(client_id)
        return c.model_dump() if c else None

    def get_connects_balance(self, user_id: str = "default_user") -> int:
        return self.connects_balances.get(user_id, 100)

    def evaluate_proposal_fit(self, job: JobPosting, client: ClientProfile, proposal: ProposalSubmission) -> Dict[str, Any]:
        """Simulate client decision making based on proposal quality."""
        text = proposal.cover_letter.lower()
        score = 0.50 # base score

        # 1. Negative penalties for generic or spammy words
        for bad in client.disliked_phrases:
            if bad in text:
                score -= 0.25

        # 2. Positive boost for matching preferred skills
        matched_skills = [s for s in client.preferred_skills if s.lower() in text]
        score += 0.10 * len(matched_skills)

        # 3. Grounding boost: citations present
        if proposal.evidence_citations and len(proposal.evidence_citations) > 0:
            score += 0.25

        # 4. Budget ceiling check
        if proposal.bid_amount > client.budget_ceiling * 1.15:
            score -= 0.30

        score = max(0.05, min(0.98, score))
        
        replied = score >= 0.65
        interview = score >= 0.80
        hired = score >= 0.90

        if hired:
            status = "hired"
            feedback = "Exceptional proposal with verified evidence! We would love to work with you."
        elif interview:
            status = "interview"
            feedback = "Strong proposal. Can we schedule an interview this week?"
        elif replied:
            status = "replied"
            feedback = "Thanks for your proposal. Could you elaborate on your experience?"
        else:
            status = "viewed"
            feedback = "Proposal viewed by client."

        return {
            "score": score,
            "status": status,
            "feedback": feedback,
            "replied": replied,
            "interview": interview,
            "hired": hired
        }

    def submit_proposal(self, submission: ProposalSubmission, user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
        # Idempotency check
        if submission.idempotency_key in self.idempotency_cache:
            return self.idempotency_cache[submission.idempotency_key]

        job = self.jobs.get(submission.job_id)
        if not job:
            job = JobPosting(
                id=submission.job_id,
                title="Active Market Job",
                description="Live evaluated job",
                skills=["Python"],
                budget=submission.bid_amount,
                connects_cost=6,
                client_id="client_apex"
            )
            self.jobs[job.id] = job

        # Check dry run
        if submission.dry_run:
            preview = {
                "dry_run": True,
                "proposal_id": submission.proposal_id,
                "job_id": job.id,
                "bid_amount": submission.bid_amount,
                "connects_cost": job.connects_cost,
                "current_connects": self.get_connects_balance(user_id),
                "remaining_connects": self.get_connects_balance(user_id) - job.connects_cost,
                "cover_letter_preview": submission.cover_letter[:150] + "...",
                "evidence_citations": submission.evidence_citations
            }
            return preview

        # Deduct connects
        current_balance = self.get_connects_balance(user_id)
        if current_balance < job.connects_cost:
            raise ValueError(f"Insufficient Connects: required {job.connects_cost}, available {current_balance}")
        self.connects_balances[user_id] = current_balance - job.connects_cost

        # Evaluate against simulated client
        client = self.clients.get(job.client_id) or ClientProfile(
            id="unknown", company_name="Unknown", total_spent=0, jobs_posted=0, hire_rate=0.5, rating=4.0, preferred_skills=[], budget_ceiling=job.budget
        )
        eval_result = self.evaluate_proposal_fit(job, client, submission)

        result = {
            "dry_run": False,
            "proposal_id": submission.proposal_id,
            "job_id": job.id,
            "status": eval_result["status"],
            "client_feedback": eval_result["feedback"],
            "reply_probability": eval_result["score"],
            "connects_spent": job.connects_cost,
            "remaining_connects": self.connects_balances[user_id]
        }

        # Save to state and cache
        self.proposals[submission.proposal_id] = submission
        self.proposal_states[submission.proposal_id] = result
        self.idempotency_cache[submission.idempotency_key] = result

        # If client replied or invited to interview, add to messages stream
        if eval_result["replied"]:
            self.messages.append({
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "job_id": job.id,
                "proposal_id": submission.proposal_id,
                "sender": client.company_name,
                "content": eval_result["feedback"],
                "timestamp": time.time(),
                "intent": "interview_request" if eval_result["interview"] else "question"
            })

        self.log_audit(user_id, "submit_proposal", submission.model_dump(), result, trace_id)
        return result

    def list_messages(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if job_id:
            return [m for m in self.messages if m.get("job_id") == job_id]
        return self.messages

    def send_message(self, message: Dict[str, Any], user_id: str = "default_user", trace_id: str = "trace_001") -> Dict[str, Any]:
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        record = {
            "id": msg_id,
            "job_id": message.get("job_id"),
            "proposal_id": message.get("proposal_id"),
            "sender": "Freelancer",
            "content": message.get("content"),
            "timestamp": time.time()
        }
        self.messages.append(record)
        self.log_audit(user_id, "send_message", message, record, trace_id)
        return {"status": "sent", "message": record}

# Singleton simulator instance
gigsim_instance = GigSimSimulator()
