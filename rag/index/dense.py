"""Dense Vector Index implementation with cosine similarity."""
import math
import re
from typing import List, Dict, Tuple
from rag.ingest.loader import Chunk

def get_dense_vector(text: str, vocab: Dict[str, int]) -> List[float]:
    words = [w.lower() for w in re.findall(r"\b\w+\b", text)]
    vec = [0.0] * len(vocab)
    for w in words:
        if w in vocab:
            vec[vocab[w]] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))

class DenseVectorIndex:
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.vocab: Dict[str, int] = {}
        self.vectors: List[List[float]] = []

    def fit(self, chunks: List[Chunk]):
        self.chunks = chunks
        vocab_set = set()
        for c in chunks:
            words = [w.lower() for w in re.findall(r"\b\w+\b", c.text)]
            vocab_set.update(words)
        self.vocab = {w: idx for idx, w in enumerate(sorted(vocab_set))}
        self.vectors = [get_dense_vector(c.text, self.vocab) for c in chunks]

    def score(self, query: str) -> List[Tuple[Chunk, float]]:
        q_vec = get_dense_vector(query, self.vocab)
        scores = [cosine_similarity(q_vec, d_vec) for d_vec in self.vectors]
        ranked = sorted(zip(self.chunks, scores), key=lambda x: x[1], reverse=True)
        return ranked
