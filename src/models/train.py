"""
Multi-Hazard Model Training Pipeline
------------------------------------
Trains:
1. Multi-Class Hazard Classifier (Random Forest / Ensemble GBDT)
2. Unsupervised Edge Anomaly Detector (Isolation Forest)
3. Multi-Hazard Continuous Risk Regressor (Multi-output Regressor)
"""

import os
import sys
import json
import math
import pickle
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath("."))
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.metrics import classification_report, f1_score, confusion_matrix, mean_squared_error, mean_absolute_error

FEATURE_COLS = [
    "elevation_m", "water_level_m", "water_level_rate_m_hr",
    "rainfall_1h_mm", "rainfall_6h_mm", "rainfall_24h_mm",
    "temperature_c", "humidity_pct", "heat_index_c",
    "smoke_ppm", "co_ppm", "voc_ppb", "so2_ug_m3", "no2_ug_m3",
    "pm25", "pm10", "aqi_calculated",
    "soil_moisture_pct", "vibration_g", "tilt_angle_deg",
    "water_ph", "water_turbidity_ntu", "dissolved_oxygen_mg_l",
    "battery_voltage_v", "signal_rssi_dbm"
]

DERIVED_FEATURES = [
    "rain_rate_ratio", "fire_weather_index_proxy", "pm_ratio",
    "landslide_instability_index", "water_quality_deviance"
]

HAZARD_CLASSES = [
    "NORMAL",
    "FLASH_FLOOD",
    "FOREST_FIRE",
    "HAZARDOUS_SMOG",
    "LANDSLIDE_PRECURSOR",
    "INDUSTRIAL_CHEMICAL_LEAK",
    "WATER_QUALITY_CRISIS"
]

RISK_TARGETS = [
    "flood_risk_score",
    "fire_risk_score",
    "air_pollution_risk_score",
    "landslide_risk_score",
    "chemical_hazard_risk_score"
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract domain-specific edge-compatible features."""
    feat = df[FEATURE_COLS].copy()
    
    # Fill missing values if any
    feat = feat.fillna(feat.median())
    
    # 1. Rain acceleration ratio
    feat["rain_rate_ratio"] = feat["rainfall_1h_mm"] / (feat["rainfall_6h_mm"] + 1e-4)
    
    # 2. Fire Weather Index proxy
    feat["fire_weather_index_proxy"] = (feat["temperature_c"] * (100.0 - feat["humidity_pct"])) / 100.0
    
    # 3. Fine vs coarse particulate ratio
    feat["pm_ratio"] = feat["pm25"] / (feat["pm10"] + 1e-4)
    
    # 4. Landslide dynamic instability index (moisture x ground vibration x tilt)
    feat["landslide_instability_index"] = (feat["soil_moisture_pct"] / 100.0) * feat["vibration_g"] * (1.0 + feat["tilt_angle_deg"] / 10.0)
    
    # 5. Water quality deviance score
    ph_dev = (feat["water_ph"] - 7.0).abs()
    turb_norm = feat["water_turbidity_ntu"] / 50.0
    do_deficit = np.maximum(0.0, 7.0 - feat["dissolved_oxygen_mg_l"])
    feat["water_quality_deviance"] = ph_dev + turb_norm + do_deficit
    
    return feat

def train_and_export_models(
    train_csv_path="data/processed/train_data.csv",
    models_dir="models",
    results_dir="results"
):
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading training data from: {train_csv_path}")
    df_train = pd.read_csv(train_csv_path)

    X_train = engineer_features(df_train)
    y_train_class = df_train["hazard_type"].values
    y_train_risk = df_train[RISK_TARGETS].values

    # 1. Train Multi-Class Hazard Classifier
    print("Training Supervised Multi-Hazard Classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train_class)

    # 2. Train Unsupervised Edge Anomaly Detector (Isolation Forest)
    print("Training Unsupervised Edge Anomaly Detector...")
    iso = IsolationForest(
        n_estimators=75,
        contamination=0.03,
        random_state=42,
        n_jobs=-1
    )
    # Fit only on baseline normal conditions to learn true nominal boundaries
    normal_mask = (y_train_class == "NORMAL")
    iso.fit(X_train[normal_mask])

    # 3. Train Continuous Multi-Hazard Risk Regressor
    print("Training Continuous Multi-Hazard Risk Regressors...")
    reg = RandomForestRegressor(
        n_estimators=80,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    reg.fit(X_train, y_train_risk)

    # Save artifacts
    model_bundle = {
        "classifier": clf,
        "anomaly_detector": iso,
        "risk_regressor": reg,
        "feature_cols": list(X_train.columns),
        "hazard_classes": list(clf.classes_),
        "risk_targets": RISK_TARGETS
    }

    bundle_path = os.path.join(models_dir, "multi_hazard_model_bundle.pkl")
    with open(bundle_path, "wb") as f:
        pickle.dump(model_bundle, f)

    print(f"[SUCCESS] Trained models saved to {bundle_path}")
    return model_bundle

if __name__ == "__main__":
    train_and_export_models()
