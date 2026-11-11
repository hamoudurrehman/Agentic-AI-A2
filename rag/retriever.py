"""RAG Retriever Factory.
Instantiates the configured RAG variant (V0, V1, V2, V3, V4, V8).
"""
from typing import List, Tuple
from rag.ingest.loader import load_persona_chunks, Chunk
from rag.variants.v0_naive import V0NaiveRetriever
from rag.variants.v1_requirement_decomp import V1RequirementDecompRetriever
from rag.variants.v2_hybrid import V2HybridRetriever
from rag.variants.v3_cross_encoder import V3CrossEncoderRetriever
from rag.variants.v4_outcome_aware import V4OutcomeAwareRetriever
from rag.variants.v8_corrective import V8CorrectiveRetriever

def get_retriever(variant: str = "v2_hybrid", persona_id: str = "persona_aiml"):
    chunks = load_persona_chunks(persona_id)
    if variant == "v0_naive":
        return V0NaiveRetriever(chunks)
    elif variant == "v1_requirement_decomp":
        return V1RequirementDecompRetriever(chunks)
    elif variant == "v2_hybrid":
        return V2HybridRetriever(chunks)
    elif variant == "v3_cross_encoder":
        return V3CrossEncoderRetriever(chunks)
    elif variant == "v4_outcome_aware":
        return V4OutcomeAwareRetriever(chunks)
    elif variant == "v8_corrective":
        return V8CorrectiveRetriever(chunks)
    else:
        return V2HybridRetriever(chunks)
