"""Variant V0: Naive Dense Retrieval on the whole job post (Baseline)."""
from typing import List, Tuple
from rag.ingest.loader import Chunk
from rag.index.dense import DenseVectorIndex

class V0NaiveRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.index = DenseVectorIndex()
        self.index.fit(chunks)

    def retrieve(self, job_post: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        ranked = self.index.score(job_post)
        return ranked[:k]
