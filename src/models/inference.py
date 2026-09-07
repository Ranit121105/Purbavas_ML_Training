"""
Real-Time Edge & Cloud Multi-Hazard Inference Engine
---------------------------------------------------
Takes incoming raw sensor frames (from LoRaWAN / NB-IoT / Edge buffer),
computes real-time dynamic features, evaluates anomaly flags, predicts
hazard classes, assigns continuous risk indices, and determines prioritized
alert actions.
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("."))

@dataclass
class SensorPacket:
    elevation_m: float
    water_level_m: float
    water_level_rate_m_hr: float
    rainfall_1h_mm: float
    rainfall_6h_mm: float
    rainfall_24h_mm: float
    temperature_c: float
    humidity_pct: float
    heat_index_c: float
    smoke_ppm: float
    co_ppm: float
    voc_ppb: float
    so2_ug_m3: float
    no2_ug_m3: float
    pm25: float
    pm10: float
    aqi_calculated: float
    soil_moisture_pct: float
    vibration_g: float
    tilt_angle_deg: float
    water_ph: float
    water_turbidity_ntu: float
    dissolved_oxygen_mg_l: float
    battery_voltage_v: float = 3.85
    signal_rssi_dbm: float = -85.0

class MultiHazardInferenceEngine:
    def __init__(self, model_bundle_path: str = "models/multi_hazard_model_bundle.pkl"):
        self.model_bundle_path = model_bundle_path
        self.is_loaded = False
        self.clf = None
        self.iso = None
        self.reg = None
        self.feature_cols = None
        self.classes = None
        self.risk_targets = None
        self._load_bundle()

    def _load_bundle(self):
        if os.path.exists(self.model_bundle_path):
            with open(self.model_bundle_path, "rb") as f:
                bundle = pickle.load(f)
            self.clf = bundle["classifier"]
            self.iso = bundle["anomaly_detector"]
            self.reg = bundle["risk_regressor"]
            self.feature_cols = bundle["feature_cols"]
            self.classes = bundle["hazard_classes"]
            self.risk_targets = bundle["risk_targets"]
            self.is_loaded = True

    def extract_features(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        feat = df_raw.copy()
        feat["rain_rate_ratio"] = feat["rainfall_1h_mm"] / (feat["rainfall_6h_mm"] + 1e-4)
        feat["fire_weather_index_proxy"] = (feat["temperature_c"] * (100.0 - feat["humidity_pct"])) / 100.0
        feat["pm_ratio"] = feat["pm25"] / (feat["pm10"] + 1e-4)
        feat["landslide_instability_index"] = (feat["soil_moisture_pct"] / 100.0) * feat["vibration_g"] * (1.0 + feat["tilt_angle_deg"] / 10.0)
        ph_dev = (feat["water_ph"] - 7.0).abs()
        turb_norm = feat["water_turbidity_ntu"] / 50.0
        do_deficit = np.maximum(0.0, 7.0 - feat["dissolved_oxygen_mg_l"])
        feat["water_quality_deviance"] = ph_dev + turb_norm + do_deficit
        
        # Ensure correct column ordering
        if self.feature_cols:
            for col in self.feature_cols:
                if col not in feat.columns:
                    feat[col] = 0.0
            feat = feat[self.feature_cols]
        return feat

    def infer(self, packet: SensorPacket, node_id: str = "NODE_EDGE_01") -> Dict[str, Any]:
        """Perform on-device inference on a single live sensor packet."""
        df_single = pd.DataFrame([asdict(packet)])
        feat = self.extract_features(df_single)

        # 1. Anomaly Detection
        if self.iso:
            anomaly_code = self.iso.predict(feat)[0]
            is_anomaly = (anomaly_code == -1)
        else:
            is_anomaly = False

        # 2. Hazard Classification
        if self.clf:
            probs = self.clf.predict_proba(feat)[0]
            pred_idx = int(np.argmax(probs))
            predicted_hazard = self.classes[pred_idx]
            confidence = float(probs[pred_idx])
            all_class_probs = {cls_name: round(float(p), 4) for cls_name, p in zip(self.classes, probs)}
        else:
            predicted_hazard = "NORMAL"
            confidence = 0.99
            all_class_probs = {"NORMAL": 0.99}

        # 3. Continuous Risk Scores
        if self.reg:
            risk_preds = self.reg.predict(feat)[0]
            risk_scores = {k: round(float(v), 3) for k, v in zip(self.risk_targets, risk_preds)}
        else:
            risk_scores = {
                "flood_risk_score": 0.05,
                "fire_risk_score": 0.02,
                "air_pollution_risk_score": 0.08,
                "landslide_risk_score": 0.03,
                "chemical_hazard_risk_score": 0.01
            }

        # 4. Determine Actionable Priority & Severity
        max_risk = max(risk_scores.values())
        if predicted_hazard == "NORMAL" and not is_anomaly:
            severity = "NONE"
            action_code = "TELEMETRY_LOG_ONLY"
            should_broadcast = False
        elif predicted_hazard == "NORMAL" and is_anomaly:
            severity = "ADVISORY_LOW"
            action_code = "TRANSMIT_ANOMALY_SNAPSHOT"
            should_broadcast = True
        elif max_risk > 0.70 or confidence > 0.80:
            severity = "EMERGENCY_CRITICAL"
            action_code = "BROADCAST_IMMEDIATE_ALARM"
            should_broadcast = True
        else:
            severity = "WARNING_HIGH"
            action_code = "BROADCAST_HAZARD_ALERT"
            should_broadcast = True

        return {
            "node_id": node_id,
            "predicted_hazard": predicted_hazard,
            "confidence": round(confidence, 3),
            "severity_level": severity,
            "action_code": action_code,
            "should_broadcast_alert": should_broadcast,
            "is_out_of_distribution_anomaly": is_anomaly,
            "risk_scores": risk_scores,
            "class_probabilities": all_class_probs
        }
