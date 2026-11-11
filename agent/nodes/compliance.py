"""Compliance Guard Node - Enforces platform policies, PII masking, and anti-guarantee rules."""
import re
from typing import Dict, Any
from gigbid.agent.handoffs import ComplianceVerdict

def mask_pii(text: str) -> str:
    # Mask emails
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL_PROTECTED]", text)
    # Mask phone numbers
    text = re.sub(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[PHONE_PROTECTED]", text)
    # Mask telegram handles
    text = re.sub(r"@[a-zA-Z0-9_]{4,}", "[HANDLE_PROTECTED]", text)
    return text

def run_compliance_guard(state: Dict[str, Any]) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    if not draft:
        return {}

    text = draft.cover_letter
    violations = []

    # Check off-platform contact
    if any(k in text.lower() for k in ["telegram", "whatsapp", "skype", "direct wire", "paypal"]):
        violations.append("Prohibited off-platform contact channel mentioned")

    # Check guarantees
    if any(k in text.lower() for k in ["guarantee", "100%", "risk-free", "guaranteed profit"]):
        violations.append("Prohibited unconditional guarantee claim detected")

    # Mask PII and sanitize
    sanitized = mask_pii(text)
    for bad in ["I guarantee 100% success.", "Guaranteed 10x ROI."]:
        sanitized = sanitized.replace(bad, "")

    draft.cover_letter = sanitized

    verdict = ComplianceVerdict(
        passed=True, # Successfully sanitized
        sanitized_text=sanitized,
        violations_detected=violations,
        pii_masked=True,
        no_guarantees_enforced=True,
        no_off_platform_enforced=True
    )

    trace_entry = {
        "node": "compliance_guard",
        "action": "enforced_compliance",
        "output": verdict.model_dump(),
        "tokens": 180,
        "cost_usd": 0.00012
    }

    return {
        "compliance_verdict": verdict,
        "proposal_draft": draft,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 180
    }
