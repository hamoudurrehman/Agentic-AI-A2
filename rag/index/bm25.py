"""BM25 Index implementation with Okapi BM25 scoring."""
import math
import re
from typing import List, Dict, Tuple
from rag.ingest.loader import Chunk

def tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r"\b\w+\b", text)]

class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freq: Dict[str, int] = {}
        self.num_docs: int = 0

    def fit(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.num_docs = len(chunks)
        self.doc_len = []
        self.doc_freq = {}

        for chunk in chunks:
            tokens = tokenize(chunk.text)
            self.doc_len.append(len(tokens))
            seen = set()
            for t in tokens:
                if t not in seen:
                    self.doc_freq[t] = self.doc_freq.get(t, 0) + 1
                    seen.add(t)

        self.avg_doc_len = sum(self.doc_len) / max(1, self.num_docs)

    def score(self, query: str) -> List[Tuple[Chunk, float]]:
        query_tokens = tokenize(query)
        scores: List[float] = [0.0] * self.num_docs

        for token in query_tokens:
            if token not in self.doc_freq:
                continue
            df = self.doc_freq[token]
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
            
            for i, chunk in enumerate(self.chunks):
                doc_tokens = tokenize(chunk.text)
                tf = doc_tokens.count(token)
                if tf > 0:
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (self.doc_len[i] / max(1.0, self.avg_doc_len)))
                    scores[i] += idf * (tf * (self.k1 + 1.0)) / max(0.001, denom)

        ranked = sorted(zip(self.chunks, scores), key=lambda x: x[1], reverse=True)
        return ranked
