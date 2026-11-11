"""Variant V1: Requirement Decomposition Retrieval."""
import re
from typing import List, Tuple, Dict
from rag.ingest.loader import Chunk
from rag.index.dense import DenseVectorIndex

class V1RequirementDecompRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.index = DenseVectorIndex()
        self.index.fit(chunks)

    def extract_requirements(self, job_post: str) -> List[str]:
        # Split on sentences, bullet points, or semicolons
        raw_parts = re.split(r"[.\n;•-]\s+", job_post)
        reqs = [p.strip() for p in raw_parts if len(p.strip()) > 15]
        return reqs if reqs else [job_post]

    def retrieve(self, job_post: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        reqs = self.extract_requirements(job_post)
        chunk_scores: Dict[str, Tuple[Chunk, float]] = {}

        for req in reqs:
            ranked = self.index.score(req)
            for c, sc in ranked[:3]:
                if c.chunk_id not in chunk_scores:
                    chunk_scores[c.chunk_id] = (c, sc)
                else:
                    prev_c, prev_sc = chunk_scores[c.chunk_id]
                    chunk_scores[c.chunk_id] = (prev_c, prev_sc + sc)

        merged = sorted(chunk_scores.values(), key=lambda x: x[1], reverse=True)
        return merged[:k]
