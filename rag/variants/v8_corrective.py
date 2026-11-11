"""Variant V8: Corrective / Self-RAG Loop."""
from typing import List, Tuple
from rag.ingest.loader import Chunk
from rag.variants.v2_hybrid import V2HybridRetriever

class V8CorrectiveRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.base = V2HybridRetriever(chunks)

    def grade_evidence(self, query: str, chunks: List[Tuple[Chunk, float]]) -> float:
        """Returns evidence quality score between 0.0 and 1.0."""
        if not chunks:
            return 0.0
        top_score = chunks[0][1]
        return min(1.0, top_score * 30.0)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        initial = self.base.retrieve(query, k=k)
        quality = self.grade_evidence(query, initial)

        # If evidence quality is low, attempt expanded re-query
        if quality < 0.35:
            expanded_query = query + " production system deliverables metrics"
            re_queried = self.base.retrieve(expanded_query, k=k)
            return re_queried

        return initial
