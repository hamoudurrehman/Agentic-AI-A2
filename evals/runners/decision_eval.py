"""Evaluation Runner for Multi-Agent Decision Quality & Risk Defenses.
Measures Bid/Skip F1, Scam Precision/Recall, Price Accuracy, and Prompt Injection Defense.
Outputs to evals/results/decision_metrics.json and .csv.
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(BASE_DIR))
sys.path.insert(0, BASE_DIR)

from typing import Dict, Any
from gigbid.agent.graphs.bid_graph import bid_graph_instance
DEV_JOBS_FILE = os.path.join(BASE_DIR, "evals", "datasets", "dev_jobs.json")
RESULTS_DIR = os.path.join(BASE_DIR, "evals", "results")

def run_decision_evaluation():
    with open(DEV_JOBS_FILE, "r", encoding="utf-8") as f:
        dev_jobs = json.load(f)

    tp_bid = fp_bid = fn_bid = tn_bid = 0
    tp_scam = fp_scam = fn_scam = tn_scam = 0
    injections_tested = 0
    injections_defended = 0
    price_inside_band = 0
    total_priced = 0

    results_details = []

    for job in dev_jobs:
        gold = job.get("gold_label", {})
        persona = job.get("target_persona", "persona_aiml")

        # Run bid graph until human interrupt
        state = bid_graph_instance.initialize_state(job, persona_id=persona)
        state = bid_graph_instance.run_until_interrupt(state)

        pred_decision = state["bid_decision"].decision
        gold_decision = gold.get("decision", "bid")

        # Bid / Skip classification metrics
        if pred_decision == "bid" and gold_decision == "bid":
            tp_bid += 1
        elif pred_decision == "bid" and gold_decision == "skip":
            fp_bid += 1
        elif pred_decision == "skip" and gold_decision == "bid":
            fn_bid += 1
        else:
            tn_bid += 1

        # Scam detection
        risk = state.get("risk_report")
        pred_scam = risk.is_scam if risk else False
        gold_scam = gold.get("is_scam", False)

        if pred_scam and gold_scam:
            tp_scam += 1
        elif pred_scam and not gold_scam:
            fp_scam += 1
        elif not pred_scam and gold_scam:
            fn_scam += 1
        else:
            tn_scam += 1

        # Injection defense
        if gold.get("has_injection", False):
            injections_tested += 1
            if risk and risk.injected_instructions_detected:
                injections_defended += 1

        # Price band accuracy
        if pred_decision == "bid" and state.get("price_quote"):
            total_priced += 1
            quote = state["price_quote"].proposed_price
            p_min = gold.get("fair_price_min", 0)
            p_max = gold.get("fair_price_max", 99999)
            if p_min <= quote <= p_max:
                price_inside_band += 1

        results_details.append({
            "job_id": job["id"],
            "pred_decision": pred_decision,
            "gold_decision": gold_decision,
            "pred_scam": pred_scam,
            "gold_scam": gold_scam
        })

    # Metrics
    precision_bid = tp_bid / max(1, (tp_bid + fp_bid))
    recall_bid = tp_bid / max(1, (tp_bid + fn_bid))
    f1_bid = 2 * (precision_bid * recall_bid) / max(0.001, (precision_bid + recall_bid))

    scam_prec = tp_scam / max(1, (tp_scam + fp_scam))
    scam_rec = tp_scam / max(1, (tp_scam + fn_scam))
    scam_f1 = 2 * (scam_prec * scam_rec) / max(0.001, (scam_prec + scam_rec))

    inj_defense_rate = (injections_defended / max(1, injections_tested)) * 100.0
    price_band_acc = (price_inside_band / max(1, total_priced)) * 100.0

    metrics = {
        "bid_skip_precision": round(precision_bid, 4),
        "bid_skip_recall": round(recall_bid, 4),
        "bid_skip_f1": round(f1_bid, 4),
        "scam_precision": round(scam_prec, 4),
        "scam_recall": round(scam_rec, 4),
        "scam_f1": round(scam_f1, 4),
        "price_inside_fair_band_pct": round(price_band_acc, 2),
        "injection_defense_rate_pct": round(inj_defense_rate, 2)
    }

    json_path = os.path.join(RESULTS_DIR, "decision_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    csv_path = os.path.join(RESULTS_DIR, "decision_metrics.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("metric,value\n")
        for k, v in metrics.items():
            f.write(f"{k},{v}\n")

    print(f"Decision evaluation complete: {metrics}")
    return metrics

if __name__ == "__main__":
    run_decision_evaluation()
