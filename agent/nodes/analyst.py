"""Job Analyst Node - Extracts structured JobSpec from raw postings."""
import re
from typing import Dict, Any
from gigbid.agent.handoffs import JobSpec

def run_analyst(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job_raw", {})
    title = job.get("title", "")
    desc = job.get("description", "")
    budget = float(job.get("budget", 1000.0))
    job_id = job.get("id", state.get("job_id", "job_001"))

    # Extract deliverables
    deliverables = []
    for line in (title + " " + desc).split("."):
        if any(k in line.lower() for k in ["build", "develop", "create", "implement", "design", "deliver", "optimize", "pipeline"]):
            deliverables.append(line.strip())
    if not deliverables:
        deliverables = [title]

    # Extract skills
    declared_skills = job.get("skills", [])
    if not declared_skills:
        skill_pool = ["Python", "LangGraph", "FastAPI", "PostgreSQL", "React", "Next.js", "Docker", "TypeScript", "SQL", "BigQuery", "dbt"]
        declared_skills = [s for s in skill_pool if s.lower() in (title + " " + desc).lower()]

    spec = JobSpec(
        job_id=job_id,
        deliverables=deliverables[:4],
        required_skills=declared_skills if declared_skills else ["Python"],
        budget=budget,
        estimated_timeline="2-3 weeks",
        screening_questions=[],
        hidden_needs=["Production reliability", "Clean architecture", "Comprehensive test coverage"]
    )

    trace_entry = {
        "node": "job_analyst",
        "action": "extracted_job_spec",
        "output": spec.model_dump(),
        "tokens": 280,
        "cost_usd": 0.00028
    }

    return {
        "job_spec": spec,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 280
    }
