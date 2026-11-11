"""Settings & Long-Term Memory Viewer Router."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from gigbid.agent.memory.store import memory_store_instance
from gigbid.agent.marketplace_port import marketplace_port_instance

router = APIRouter(prefix="/settings", tags=["settings"])

SYSTEM_SETTINGS = {
    "autonomy_level": "human_in_the_loop_mandatory", # "human_in_the_loop_mandatory", "auto_skip_low_fit"
    "weekly_connects_budget": 120,
    "min_connects_reserve": 10,
    "marketplace_mode": "gigsim", # "gigsim" or "upwork_live"
    "saved_searches": [
        "LangGraph multi agent",
        "FastAPI React full stack",
        "dbt BigQuery attribution"
    ]
}

@router.get("")
def get_settings():
    return {
        "settings": SYSTEM_SETTINGS,
        "style_memories": memory_store_instance.get_style_rules(),
        "outcome_memories": memory_store_instance.get_outcome_patterns()
    }

@router.post("/marketplace-mode")
def set_marketplace_mode(mode: str):
    if mode not in ["gigsim", "upwork_live"]:
        raise HTTPException(status_code=400, detail="Invalid marketplace mode")
    SYSTEM_SETTINGS["marketplace_mode"] = mode
    marketplace_port_instance.set_mode(mode)
    return {"status": "success", "mode": mode}

@router.delete("/memory/style/{rule_id}")
def delete_style_rule(rule_id: str):
    success = memory_store_instance.delete_style_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Style memory rule not found")
    return {"status": "deleted", "id": rule_id}

@router.delete("/memory/outcome/{pattern_id}")
def delete_outcome_pattern(pattern_id: str):
    success = memory_store_instance.delete_outcome_pattern(pattern_id)
    if not success:
        raise HTTPException(status_code=404, detail="Outcome memory pattern not found")
    return {"status": "deleted", "id": pattern_id}
