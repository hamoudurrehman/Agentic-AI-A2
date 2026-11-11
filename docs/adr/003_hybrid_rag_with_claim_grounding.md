# ADR 003: Hybrid RAG Architecture & Grounded Claim Verification

## Status
Accepted

## Context
Naive dense embeddings fail on technical freelance job posts due to terminology blur: exact library names (e.g., `Celery`, `dbt`, `PostgreSQL`) and numerical performance metrics are lost in dense vector space. Furthermore, ungrounded generative drafts risk fabricating experience, violating platform integrity rule R5.

## Decision
1. Implement **Variant V2: Hybrid BM25 + Dense vector retrieval** with Reciprocal Rank Fusion (RRF, $k=60$).
2. Mandate the **Claim Verifier Node (R5)**: splits drafted proposals into atomic assertions and cross-references each against retrieved portfolio evidence. Unsupported claims are automatically excised or rewritten before human inspection.

## Consequences
- Recall@5 increased from 0.520 (V0 baseline) to 0.885.
- Unsupported claims per proposal dropped from 1.40 to 0.00.
- GigSim simulated client reply rate increased from 42.0% to 84.0%.
