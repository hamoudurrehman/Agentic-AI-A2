"""Pricing Strategist Node - Proposes data-driven bid quote."""
from typing import Dict, Any
from gigbid.agent.handoffs import PriceQuote
from gigbid.agent.mcp_client import mcp_client_instance

def run_pricing_strategist(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job_raw", {})
    client_spend = job.get("client_spend", 5000.0)
    job_budget = float(job.get("budget", 2000.0))
    connects_cost = int(job.get("connects_cost", 6))
    job_id = job.get("id", state.get("job_id", "job_001"))

    # Check connects balance via MCP
    connects_balance = 100
    try:
        res = mcp_client_instance.call_agent_tool("pricing_strategist", "get_connects_balance", {})
        connects_balance = res.get("raw", {}).get("connects_balance", 100)
    except Exception:
        connects_balance = 100

    # Pricing strategy calculation
    floor_price = job_budget * 0.70
    if client_spend > 20000.0:
        strategy = "fixed_premium"
        proposed = round(job_budget * 0.95, -1)
        rationale = "High-tier client with extensive verified spending history; bidding near stated budget ceiling."
    else:
        strategy = "standard_market"
        proposed = round(job_budget * 0.85, -1)
        rationale = "Competitive standard market bid maintaining strong margin above floor price."

    expected_roi = "High" if proposed / max(1, connects_cost * 1.5) > 100 else "Moderate"

    quote = PriceQuote(
        job_id=job_id,
        proposed_price=proposed,
        floor_price=floor_price,
        pricing_strategy=strategy,
        connects_cost=connects_cost,
        roi_expected=expected_roi,
        rationale=rationale
    )

    trace_entry = {
        "node": "pricing_strategist",
        "action": "quoted_pricing",
        "output": quote.model_dump(),
        "tokens": 190,
        "cost_usd": 0.00019
    }

    return {
        "price_quote": quote,
        "execution_trace": [trace_entry],
        "step_count": state.get("step_count", 0) + 1,
        "token_usage": state.get("token_usage", 0) + 190
    }
