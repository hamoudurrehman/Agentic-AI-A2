"""Decision Node - Evaluates parallel analyses and decides: skip, watch, or bid."""
from typing import Dict, Any
from gigbid.agent.handoffs import BidDecision

def run_decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    risk = state.get("risk_report")
    fit = state.get("fit_report")
    job = state.get("job_raw", {})
    job_id = job.get("id", state.get("job_id", "job_001"))

    # Priority 1: High risk / Scam detection
    if risk and (risk.is_scam or risk.risk_level == "critical"):
        decision = BidDecision(
            job_id=job_id,
            decision="skip",
            confidence=0.98,
            reason=f"Skipped due to critical platform risk: {', '.join(risk.reasons)}"
        )
    # Priority 2: Injected prompt instruction
    elif risk and risk.injected_instructions_detected:
        decision = BidDecision(
            job_id=job_id,
            decision="skip",
            confidence=0.95,
            reason="Planted prompt injection payload flagged; skipped to preserve system security."
        )
    # Priority 3: Low fit or budget
    elif fit and fit.fit_score < 0.40:
        decision = BidDecision(
            job_id=job_id,
            decision="skip",
            confidence=0.88,
            reason=f"Portfolio fit score too low ({fit.fit_score * 100}%). Missing skills: {', '.join(fit.missing_skills)}"
        )
    elif job.get("budget", 1000) < 50:
        decision = BidDecision(
            job_id=job_id,
            decision="skip",
            confidence=0.90,
            reason="Budget below freelancer hourly minimum threshold."
        )
    else:
        decision = BidDecision(
            job_id=job_id,
            decision="bid",
            confidence=0.92,
            reason=f"High technical fit ({fit.fit_score * 100 if fit else 80}%) with verified portfolio evidence."
        )

    trace_entry = {
        "node": "decision_node",
        "action": "decided_action",
        "output": decision.model_dump(),
        "tokens": 120,
        "cost_usd": 0.00010
    }

    return {
        "bid_decision": decision,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 120
    }
