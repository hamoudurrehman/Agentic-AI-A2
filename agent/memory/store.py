"""Long-Term Memory Store for GigBid.
Maintains two strictly segregated stores:
1. Style Memory (learned from human edits to agent drafts)
2. Outcome Memory (learned from market wins and replies)
Enforces delete capability and inspectability via the UI.
"""
from typing import Dict, Any, List, Optional
import time
import uuid

class MemoryStore:
    def __init__(self):
        self.style_memory: List[Dict[str, Any]] = [
            {
                "id": "style_001",
                "rule": "Avoid generic hype words like 'passionate' or 'rockstar'.",
                "source": "initial_preference",
                "created_at": time.time(),
                "weight": 1.0
            },
            {
                "id": "style_002",
                "rule": "Lead immediately with relevant client industry metric in sentence 1.",
                "source": "initial_preference",
                "created_at": time.time(),
                "weight": 1.0
            }
        ]
        self.outcome_memory: List[Dict[str, Any]] = [
            {
                "id": "outcome_001",
                "job_category": "AI / LangGraph",
                "effective_framing": "Emphasize parallel execution, error recovery, and PostgreSQL checkpointer.",
                "win_count": 4,
                "created_at": time.time()
            }
        ]

    # Style Memory
    def get_style_rules(self) -> List[Dict[str, Any]]:
        return self.style_memory

    def add_style_rule(self, rule: str, source: str) -> Dict[str, Any]:
        item = {
            "id": f"style_{uuid.uuid4().hex[:6]}",
            "rule": rule,
            "source": source,
            "created_at": time.time(),
            "weight": 1.0
        }
        self.style_memory.append(item)
        return item

    def delete_style_rule(self, rule_id: str) -> bool:
        initial = len(self.style_memory)
        self.style_memory = [r for r in self.style_memory if r["id"] != rule_id]
        return len(self.style_memory) < initial

    # Outcome Memory
    def get_outcome_patterns(self, job_category: Optional[str] = None) -> List[Dict[str, Any]]:
        if job_category:
            return [o for o in self.outcome_memory if job_category.lower() in o.get("job_category", "").lower()]
        return self.outcome_memory

    def record_outcome(self, job_category: str, framing: str, outcome: str):
        for o in self.outcome_memory:
            if o.get("job_category") == job_category:
                if outcome == "won":
                    o["win_count"] = o.get("win_count", 0) + 1
                    o["effective_framing"] = framing
                return
        self.outcome_memory.append({
            "id": f"outcome_{uuid.uuid4().hex[:6]}",
            "job_category": job_category,
            "effective_framing": framing,
            "win_count": 1 if outcome == "won" else 0,
            "created_at": time.time()
        })

    def delete_outcome_pattern(self, pattern_id: str) -> bool:
        initial = len(self.outcome_memory)
        self.outcome_memory = [o for o in self.outcome_memory if o["id"] != pattern_id]
        return len(self.outcome_memory) < initial

# Singleton memory store instance
memory_store_instance = MemoryStore()
