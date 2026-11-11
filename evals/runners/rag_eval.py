"""Evaluation Runner for RAG Variants.
Computes Recall@5, MRR, nDCG@10 across V0, V1, V2, V3, V4, and V8.
Outputs results to evals/results/rag_metrics.json and .csv.
"""
import os
import sys
import json
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(BASE_DIR))
sys.path.insert(0, BASE_DIR)

from typing import List, Dict, Any
from gigbid.rag.retriever import get_retriever
DEV_JOBS_FILE = os.path.join(BASE_DIR, "evals", "datasets", "dev_jobs.json")
RESULTS_DIR = os.path.join(BASE_DIR, "evals", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def compute_ndcg_at_k(retrieved_ids: List[str], gold_ids: List[str], k: int = 10) -> float:
    dcg = 0.0
    for i, item_id in enumerate(retrieved_ids[:k]):
        if item_id in gold_ids:
            dcg += 1.0 / math.log2(i + 2)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(gold_ids))))
    return (dcg / idcg) if idcg > 0 else 0.0

def compute_mrr(retrieved_ids: List[str], gold_ids: List[str]) -> float:
    for i, item_id in enumerate(retrieved_ids):
        if item_id in gold_ids:
            return 1.0 / (i + 1)
    return 0.0

def run_rag_evaluation():
    with open(DEV_JOBS_FILE, "r", encoding="utf-8") as f:
        dev_jobs = json.load(f)

    variants = ["v0_naive", "v1_requirement_decomp", "v2_hybrid", "v3_cross_encoder", "v4_outcome_aware", "v8_corrective"]
    summary: Dict[str, Any] = {}

    for var in variants:
        recalls = []
        mrrs = []
        ndcgs = []

        for job in dev_jobs:
            gold = job.get("gold_label", {})
            gold_ids = gold.get("gold_evidence_ids", [])
            if not gold_ids:
                continue

            persona = job.get("target_persona", "persona_aiml")
            retriever = get_retriever(variant=var, persona_id=persona)
            query = job["title"] + " " + job["description"]
            results = retriever.retrieve(query, k=5)
            retrieved_ids = [c[0].chunk_id for c in results]

            # Compute recall@5
            hits = len(set(retrieved_ids).intersection(set(gold_ids)))
            recall = hits / max(1, len(gold_ids))
            recalls.append(recall)

            # Compute MRR & nDCG@10
            mrrs.append(compute_mrr(retrieved_ids, gold_ids))
            ndcgs.append(compute_ndcg_at_k(retrieved_ids, gold_ids, k=10))

        avg_recall = sum(recalls) / max(1, len(recalls))
        avg_mrr = sum(mrrs) / max(1, len(mrrs))
        avg_ndcg = sum(ndcgs) / max(1, len(ndcgs))

        summary[var] = {
            "evidence_recall_at_5": round(avg_recall, 4),
            "mrr": round(avg_mrr, 4),
            "ndcg_at_10": round(avg_ndcg, 4)
        }

    # Save to JSON
    json_path = os.path.join(RESULTS_DIR, "rag_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save to CSV
    csv_path = os.path.join(RESULTS_DIR, "rag_metrics.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("variant,evidence_recall_at_5,mrr,ndcg_at_10\n")
        for v, m in summary.items():
            f.write(f"{v},{m['evidence_recall_at_5']},{m['mrr']},{m['ndcg_at_10']}\n")

    print(f"RAG Evaluation complete. Results saved to {json_path}")
    return summary

if __name__ == "__main__":
    run_rag_evaluation()
