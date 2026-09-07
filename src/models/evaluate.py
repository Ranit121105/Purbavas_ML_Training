"""
Multi-Hazard Model Evaluation & Benchmarking
---------------------------------------------
Evaluates trained models against the unseen chronological test set (test_data.csv).
Generates classification reports, confusion matrix, continuous risk metrics, and edge latency.
"""

import os
import sys
import time
import json
import pickle
import numpy as np
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath("."))

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    mean_absolute_error,
    mean_squared_error
)
from src.models.train import engineer_features, RISK_TARGETS

def evaluate_models(
    test_csv_path="data/processed/test_data.csv",
    model_bundle_path="models/multi_hazard_model_bundle.pkl",
    results_dir="results"
):
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading test data from: {test_csv_path}")
    df_test = pd.read_csv(test_csv_path)

    print(f"Loading trained models from: {model_bundle_path}")
    with open(model_bundle_path, "rb") as f:
        bundle = pickle.load(f)

    clf = bundle["classifier"]
    iso = bundle["anomaly_detector"]
    reg = bundle["risk_regressor"]

    X_test = engineer_features(df_test)
    y_test_class = df_test["hazard_type"].values
    y_test_risk = df_test[RISK_TARGETS].values

    # 1. Classification Predictions & Timing
    start_t = time.perf_counter()
    y_pred_class = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)
    inference_time_total = time.perf_counter() - start_t
    avg_latency_ms = (inference_time_total / len(X_test)) * 1000.0

    # 2. Anomaly Detection
    anomaly_preds = iso.predict(X_test)
    anomaly_flags = (anomaly_preds == -1)

    # 3. Continuous Risk Regression
    y_pred_risk = reg.predict(X_test)

    # Classification Metrics
    macro_f1 = f1_score(y_test_class, y_pred_class, average="macro")
    weighted_f1 = f1_score(y_test_class, y_pred_class, average="weighted")
    weighted_precision = precision_score(y_test_class, y_pred_class, average="weighted")
    weighted_recall = recall_score(y_test_class, y_pred_class, average="weighted")

    cls_report_dict = classification_report(y_test_class, y_pred_class, output_dict=True)
    labels = sorted(list(set(y_test_class)))
    cm = confusion_matrix(y_test_class, y_pred_class, labels=labels)

    # Risk Metrics
    risk_metrics = {}
    for i, target in enumerate(RISK_TARGETS):
        mae = mean_absolute_error(y_test_risk[:, i], y_pred_risk[:, i])
        rmse = float(np.sqrt(mean_squared_error(y_test_risk[:, i], y_pred_risk[:, i])))
        risk_metrics[target] = {
            "MAE": round(float(mae), 4),
            "RMSE": round(rmse, 4)
        }

    # Critical Hazard False Negative Rate (Safety Check)
    critical_hazards = ["FLASH_FLOOD", "FOREST_FIRE", "LANDSLIDE_PRECURSOR", "INDUSTRIAL_CHEMICAL_LEAK"]
    critical_fn_counts = {}
    for ch in critical_hazards:
        mask = (y_test_class == ch)
        total_ch = int(np.sum(mask))
        missed = int(np.sum(y_pred_class[mask] != ch)) if total_ch > 0 else 0
        fn_rate = (missed / total_ch) if total_ch > 0 else 0.0
        critical_fn_counts[ch] = {
            "total_occurrences": total_ch,
            "missed_detections": missed,
            "false_negative_rate_pct": round(fn_rate * 100.0, 2)
        }

    # Assemble comprehensive evaluation report
    report = {
        "evaluation_summary": {
            "total_test_samples": len(X_test),
            "macro_f1_score": round(float(macro_f1), 4),
            "weighted_f1_score": round(float(weighted_f1), 4),
            "weighted_precision": round(float(weighted_precision), 4),
            "weighted_recall": round(float(weighted_recall), 4),
            "avg_single_sample_latency_ms": round(float(avg_latency_ms), 3),
            "edge_throughput_samples_per_sec": round(float(len(X_test) / inference_time_total), 1)
        },
        "critical_hazard_safety_audit": critical_fn_counts,
        "continuous_risk_regression_metrics": risk_metrics,
        "per_class_classification_metrics": cls_report_dict
    }

    # Save outputs
    json_path = os.path.join(results_dir, "evaluation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    cm_df = pd.DataFrame(cm, index=[f"Actual_{l}" for l in labels], columns=[f"Pred_{l}" for l in labels])
    cm_path = os.path.join(results_dir, "confusion_matrix.csv")
    cm_df.to_csv(cm_path)

    print("\n" + "="*60)
    print("           MODEL EVALUATION SUMMARY REPORT")
    print("="*60)
    print(f" Macro F1-Score:        {macro_f1:.4f}")
    print(f" Weighted F1-Score:     {weighted_f1:.4f}")
    print(f" Edge Latency / sample: {avg_latency_ms:.3f} ms")
    print(f" Critical Safety Audit: {json.dumps(critical_fn_counts, indent=2)}")
    print(f" Continuous Risk MAE:   {json.dumps(risk_metrics, indent=2)}")
    print(f"\nSaved Report: {json_path}")
    print(f"Saved Confusion Matrix: {cm_path}")
    print("="*60)

    return report

if __name__ == "__main__":
    evaluate_models()
