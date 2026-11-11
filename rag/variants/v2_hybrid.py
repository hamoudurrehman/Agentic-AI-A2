"""Variant V2: Hybrid BM25 + Dense with Reciprocal Rank Fusion (RRF)."""
from typing import List, Tuple, Dict
from rag.ingest.loader import Chunk
from rag.index.bm25 import BM25Index
from rag.index.dense import DenseVectorIndex

class V2HybridRetriever:
    def __init__(self, chunks: List[Chunk], rrf_k: int = 60):
        self.bm25 = BM25Index()
        self.bm25.fit(chunks)
        self.dense = DenseVectorIndex()
        self.dense.fit(chunks)
        self.rrf_k = rrf_k

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        bm25_ranked = self.bm25.score(query)
        dense_ranked = self.dense.score(query)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        for rank, (chunk, _) in enumerate(bm25_ranked):
            chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        for rank, (chunk, _) in enumerate(dense_ranked):
            chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        fused = [(chunk_map[cid], score) for cid, score in rrf_scores.items()]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]
