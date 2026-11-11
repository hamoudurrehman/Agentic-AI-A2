"""Variant V3: Cross-Encoder Reranker over candidate retrievals."""
from typing import List, Tuple
from rag.ingest.loader import Chunk
from rag.variants.v2_hybrid import V2HybridRetriever

def cross_score(query: str, doc_text: str) -> float:
    q_words = set(query.lower().split())
    d_words = set(doc_text.lower().split())
    overlap = len(q_words.intersection(d_words))
    # Bigram overlap
    q_bigrams = set(zip(query.lower().split()[:-1], query.lower().split()[1:]))
    d_bigrams = set(zip(doc_text.lower().split()[:-1], doc_text.lower().split()[1:]))
    bg_overlap = len(q_bigrams.intersection(d_bigrams))
    return overlap * 1.0 + bg_overlap * 2.5

class V3CrossEncoderRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.stage1 = V2HybridRetriever(chunks)

    def retrieve(self, query: str, k: int = 5, candidate_pool: int = 15) -> List[Tuple[Chunk, float]]:
        candidates = self.stage1.retrieve(query, k=candidate_pool)
        reranked = []
        for chunk, base_score in candidates:
            score = cross_score(query, chunk.text) + base_score * 10.0
            reranked.append((chunk, score))
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:k]
