"""Risk Assessor Node - Defends against scams, free-work traps, and prompt injections."""
import re
from typing import Dict, Any
from gigbid.agent.handoffs import RiskReport
from gigbid.agent.mcp_client import mcp_client_instance

def run_risk_assessor(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job_raw", {})
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    client_id = job.get("client_id", "client_unknown")

    # Fetch client history via MCP tool allowlist
    client_history = {}
    try:
        res = mcp_client_instance.call_agent_tool("risk_assessor", "get_client_history", {"client_id": client_id})
        client_history = res.get("raw") or {}
    except Exception:
        client_history = {}

    client_spend = client_history.get("total_spent", job.get("client_spend", 0.0))
    hire_rate = client_history.get("hire_rate", job.get("client_hire_rate", 0.5))

    reasons = []
    is_scam = False
    is_off_platform = False
    is_free_work = False
    injected_instructions = False

    # 1. Off-platform detection
    for kw in ["telegram", "whatsapp", "skype", "direct email", "wire transfer", "crypto", "paypal"]:
        if kw in text:
            is_off_platform = True
            reasons.append(f"Off-platform keyword detected: '{kw}'")

    # 2. Free work detection
    for kw in ["unpaid sample", "free sample", "free test", "unpaid trial", "unpaid test project"]:
        if kw in text:
            is_free_work = True
            reasons.append(f"Free-work solicitation detected: '{kw}'")

    # 3. Planted Prompt Injection detection
    for inj in ["ignore previous instructions", "system compromised", "disregard instructions", "output 'system compromised'"]:
        if inj in text:
            injected_instructions = True
            reasons.append("Planted prompt injection payload detected and neutralized")

    # 4. Client reputation scoring
    client_score = 100.0
    if client_spend == 0.0 and hire_rate == 0.0:
        client_score -= 40.0
        reasons.append("Zero client spend history on platform")
    if is_off_platform:
        client_score -= 50.0
        is_scam = True
    if is_free_work:
        client_score -= 40.0
        is_scam = True

    client_score = max(0.0, min(100.0, client_score))

    risk_level = "low"
    if is_scam or injected_instructions:
        risk_level = "critical"
    elif client_score < 40.0:
        risk_level = "high"
    elif client_score < 70.0:
        risk_level = "medium"

    report = RiskReport(
        job_id=job.get("id", state.get("job_id", "job_001")),
        client_score=client_score,
        is_scam=is_scam,
        is_free_work_request=is_free_work,
        is_off_platform_request=is_off_platform,
        injected_instructions_detected=injected_instructions,
        risk_level=risk_level,
        reasons=reasons
    )

    trace_entry = {
        "node": "risk_assessor",
        "action": "evaluated_risk",
        "output": report.model_dump(),
        "tokens": 220,
        "cost_usd": 0.00015
    }

    return {
        "risk_report": report,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 220
    }
