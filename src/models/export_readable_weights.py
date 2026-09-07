"""
Export .pkl Model Bundle to Human-Readable Formats (JSON & Markdown)
-------------------------------------------------------------------
Converts the binary pickle bundle into transparent, human-readable JSON
containing model architecture, feature importances, hyperparameters,
decision parameters, and risk mapping equations.
"""

import os
import sys
import json
import pickle
import numpy as np

sys.path.insert(0, os.path.abspath("."))

def export_readable_model(
    pkl_path="models/multi_hazard_model_bundle.pkl",
    json_path="models/multi_hazard_model_weights.json",
    md_path="models/MODEL_ARCHITECTURE.md"
):
    print(f"Loading binary model from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

    clf = bundle["classifier"]
    iso = bundle["anomaly_detector"]
    reg = bundle["risk_regressor"]
    feature_cols = bundle["feature_cols"]
    hazard_classes = list(bundle["hazard_classes"])
    risk_targets = list(bundle["risk_targets"])

    # 1. Feature Importance Rankings (Classifier)
    feat_importances = {}
    raw_importances = clf.feature_importances_
    sorted_idx = np.argsort(raw_importances)[::-1]
    for idx in sorted_idx:
        feat_name = feature_cols[idx]
        feat_importances[feat_name] = round(float(raw_importances[idx]), 6)

    # 2. Risk Regressor Feature Importances
    risk_importances = {}
    for i, target in enumerate(risk_targets):
        estimator = reg.estimators_[i] if hasattr(reg, "estimators_") else reg
        imp = estimator.feature_importances_
        sorted_imp_idx = np.argsort(imp)[::-1][:5] # Top 5 features
        risk_importances[target] = {
            feature_cols[j]: round(float(imp[j]), 4) for j in sorted_imp_idx
        }

    # 3. Model Metadata & Parameters
    readable_model = {
        "model_name": "Purbavas Multi-Hazard Early Warning Ensemble",
        "version": "1.0.0",
        "serialization_format": "Human-Readable JSON",
        "input_features": {
            "total_count": len(feature_cols),
            "feature_names": feature_cols
        },
        "hazard_classes": {
            "total_count": len(hazard_classes),
            "class_names": hazard_classes
        },
        "continuous_risk_targets": risk_targets,
        "supervised_classifier_summary": {
            "algorithm": "RandomForestClassifier",
            "n_estimators": clf.n_estimators,
            "max_depth": clf.max_depth,
            "class_weight": "balanced",
            "total_decision_trees": len(clf.estimators_),
            "feature_importance_ranking": feat_importances
        },
        "unsupervised_anomaly_detector_summary": {
            "algorithm": "IsolationForest",
            "n_estimators": iso.n_estimators,
            "contamination_rate": iso.contamination,
            "offset_threshold": round(float(iso.offset_), 4)
        },
        "multi_target_risk_regressor_summary": {
            "algorithm": "RandomForestRegressor",
            "n_estimators": reg.n_estimators,
            "max_depth": reg.max_depth,
            "top_driving_features_per_hazard": risk_importances
        },
        "edge_decision_thresholds": {
            "FLASH_FLOOD": {
                "water_level_m_warning_threshold": 5.8,
                "water_level_rate_m_hr_threshold": 0.9,
                "rainfall_1h_mm_threshold": 35.0
            },
            "FOREST_FIRE": {
                "smoke_ppm_threshold": 180.0,
                "co_ppm_threshold": 12.0,
                "humidity_pct_max_threshold": 35.0
            },
            "HAZARDOUS_SMOG": {
                "pm25_critical_threshold": 180.0,
                "smoke_ppm_max_threshold": 150.0
            },
            "LANDSLIDE_PRECURSOR": {
                "soil_moisture_pct_threshold": 82.0,
                "vibration_g_threshold": 0.09,
                "tilt_angle_deg_threshold": 2.0
            },
            "INDUSTRIAL_CHEMICAL_LEAK": {
                "voc_ppb_threshold": 1500.0,
                "so2_ug_m3_threshold": 80.0,
                "no2_ug_m3_threshold": 90.0
            },
            "WATER_QUALITY_CRISIS": {
                "water_ph_acid_bound": 5.4,
                "water_ph_alkaline_bound": 9.4,
                "turbidity_ntu_threshold": 140.0
            }
        }
    }

    # Save to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(readable_model, f, indent=2)

    # Save to Markdown Document
    md_content = f"""# Purbavas Model Architecture & Weights Specification

## 1. Overview
This document describes the human-readable parameters and feature weights of the **Purbavas Multi-Hazard Early Warning Ensemble** exported from [`{pkl_path}`](file:///{os.path.abspath(pkl_path)}).

- **Format**: JSON & Structured Markdown
- **JSON File**: [`models/multi_hazard_model_weights.json`](file:///{os.path.abspath(json_path)})
- **Total Input Features**: {len(feature_cols)}
- **Target Hazard Classes**: {len(hazard_classes)} ({', '.join(hazard_classes)})
- **Continuous Risk Scores**: {', '.join(risk_targets)}

---

## 2. Global Feature Importance Ranking (Classifier)

Features ranked by their contribution to disaster classification:

| Rank | Feature Name | Importance Weight | Primary Disaster Indicator |
| :--- | :--- | :--- | :--- |
"""
    for rank, (feat, weight) in enumerate(feat_importances.items(), 1):
        md_content += f"| {rank} | `{feat}` | **{weight:.4f}** | {'Derived Index' if feat in ['fire_weather_index_proxy', 'landslide_instability_index', 'water_quality_deviance', 'rain_rate_ratio', 'pm_ratio'] else 'Raw Sensor'} |\n"

    md_content += """
---

## 3. Top Driving Features Per Continuous Risk Target

"""
    for target, feats in risk_importances.items():
        md_content += f"### `{target}`\n"
        for f_name, f_wt in feats.items():
            md_content += f"- `{f_name}`: **{f_wt:.4f}**\n"
        md_content += "\n"

    md_content += """
---

## 4. Edge Operational Decision Boundaries

| Hazard Type | Trigger Conditions | Action Severity |
| :--- | :--- | :--- |
| **Flash Flood** | `water_rate >= 0.9 m/hr` AND `rain_1h >= 35.0 mm` OR `water_level >= 5.8 m` | `EMERGENCY_CRITICAL` |
| **Forest Fire** | `smoke >= 180 ppm` AND `co >= 12 ppm` AND `humidity <= 35%` | `EMERGENCY_CRITICAL` |
| **Hazardous Smog** | `pm25 >= 180 ug/m3` AND `smoke < 150 ppm` | `EMERGENCY_CRITICAL` |
| **Landslide Precursor**| `soil_moisture >= 82%` AND `vibration >= 0.09 g` OR `tilt >= 2.0 deg` | `EMERGENCY_CRITICAL` |
| **Chemical Leak** | `voc >= 1500 ppb` OR (`so2 >= 80` AND `no2 >= 90`) | `EMERGENCY_CRITICAL` |
| **Water Quality Crisis**| `ph <= 5.4` OR `ph >= 9.4` OR `turbidity >= 140 NTU` | `WARNING_HIGH` |
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[SUCCESS] Exported human-readable weights to:")
    print(f" - JSON:     {json_path}")
    print(f" - Markdown: {md_path}")

if __name__ == "__main__":
    export_readable_model()
