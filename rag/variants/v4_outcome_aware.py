"""Variant V4: Outcome-Aware Ranking.
Boosts evidence from case studies and past proposals that won jobs or achieved positive client replies.
"""
from typing import List, Tuple
from rag.ingest.loader import Chunk
from rag.variants.v2_hybrid import V2HybridRetriever

class V4OutcomeAwareRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.base = V2HybridRetriever(chunks)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        initial = self.base.retrieve(query, k=k*2)
        adjusted = []
        for chunk, score in initial:
            outcome = chunk.metadata.get("outcome", "none")
            boost = 1.0
            if outcome == "won":
                boost = 1.45
            elif outcome in ["replied", "delivered_successfully"]:
                boost = 1.25
            elif outcome == "ignored":
                boost = 0.70
            
            adjusted.append((chunk, score * boost))
        adjusted.sort(key=lambda x: x[1], reverse=True)
        return adjusted[:k]
