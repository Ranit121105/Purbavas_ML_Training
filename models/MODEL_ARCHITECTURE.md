# Purbavas Model Architecture & Weights Specification

## 1. Overview
This document describes the human-readable parameters and feature weights of the **Purbavas Multi-Hazard Early Warning Ensemble** exported from [`models/multi_hazard_model_bundle.pkl`](file:///C:\Users\RANIT\OneDrive\Desktop\Purbavas\models\multi_hazard_model_bundle.pkl).

- **Format**: JSON & Structured Markdown
- **JSON File**: [`models/multi_hazard_model_weights.json`](file:///C:\Users\RANIT\OneDrive\Desktop\Purbavas\models\multi_hazard_model_weights.json)
- **Total Input Features**: 30
- **Target Hazard Classes**: 7 (FLASH_FLOOD, FOREST_FIRE, HAZARDOUS_SMOG, INDUSTRIAL_CHEMICAL_LEAK, LANDSLIDE_PRECURSOR, NORMAL, WATER_QUALITY_CRISIS)
- **Continuous Risk Scores**: flood_risk_score, fire_risk_score, air_pollution_risk_score, landslide_risk_score, chemical_hazard_risk_score

---

## 2. Global Feature Importance Ranking (Classifier)

Features ranked by their contribution to disaster classification:

| Rank | Feature Name | Importance Weight | Primary Disaster Indicator |
| :--- | :--- | :--- | :--- |
| 1 | `dissolved_oxygen_mg_l` | **0.0663** | Raw Sensor |
| 2 | `co_ppm` | **0.0641** | Raw Sensor |
| 3 | `so2_ug_m3` | **0.0634** | Raw Sensor |
| 4 | `landslide_instability_index` | **0.0626** | Derived Index |
| 5 | `water_quality_deviance` | **0.0564** | Derived Index |
| 6 | `no2_ug_m3` | **0.0556** | Raw Sensor |
| 7 | `rainfall_1h_mm` | **0.0536** | Raw Sensor |
| 8 | `aqi_calculated` | **0.0511** | Raw Sensor |
| 9 | `water_level_rate_m_hr` | **0.0508** | Raw Sensor |
| 10 | `water_level_m` | **0.0498** | Raw Sensor |
| 11 | `soil_moisture_pct` | **0.0495** | Raw Sensor |
| 12 | `water_turbidity_ntu` | **0.0484** | Raw Sensor |
| 13 | `vibration_g` | **0.0465** | Raw Sensor |
| 14 | `elevation_m` | **0.0452** | Raw Sensor |
| 15 | `pm10` | **0.0424** | Raw Sensor |
| 16 | `pm25` | **0.0410** | Raw Sensor |
| 17 | `voc_ppb` | **0.0391** | Raw Sensor |
| 18 | `smoke_ppm` | **0.0281** | Raw Sensor |
| 19 | `rainfall_6h_mm` | **0.0189** | Raw Sensor |
| 20 | `humidity_pct` | **0.0167** | Raw Sensor |
| 21 | `rainfall_24h_mm` | **0.0125** | Raw Sensor |
| 22 | `heat_index_c` | **0.0106** | Raw Sensor |
| 23 | `fire_weather_index_proxy` | **0.0081** | Derived Index |
| 24 | `tilt_angle_deg` | **0.0070** | Raw Sensor |
| 25 | `pm_ratio` | **0.0050** | Derived Index |
| 26 | `rain_rate_ratio` | **0.0025** | Derived Index |
| 27 | `temperature_c` | **0.0023** | Raw Sensor |
| 28 | `water_ph` | **0.0022** | Raw Sensor |
| 29 | `signal_rssi_dbm` | **0.0000** | Raw Sensor |
| 30 | `battery_voltage_v` | **0.0000** | Raw Sensor |

---

## 3. Top Driving Features Per Continuous Risk Target

### `flood_risk_score`
- `water_level_rate_m_hr`: **0.3470**
- `pm10`: **0.2442**
- `rainfall_1h_mm`: **0.1991**
- `dissolved_oxygen_mg_l`: **0.0828**
- `humidity_pct`: **0.0628**

### `fire_risk_score`
- `water_level_rate_m_hr`: **0.3479**
- `aqi_calculated`: **0.2427**
- `rainfall_1h_mm`: **0.1962**
- `dissolved_oxygen_mg_l`: **0.0807**
- `so2_ug_m3`: **0.0620**

### `air_pollution_risk_score`
- `water_level_rate_m_hr`: **0.3497**
- `pm25`: **0.2455**
- `rainfall_1h_mm`: **0.1945**
- `dissolved_oxygen_mg_l`: **0.0866**
- `so2_ug_m3`: **0.0630**

### `landslide_risk_score`
- `water_level_rate_m_hr`: **0.3486**
- `pm10`: **0.2418**
- `rainfall_1h_mm`: **0.2003**
- `dissolved_oxygen_mg_l`: **0.0825**
- `elevation_m`: **0.0614**

### `chemical_hazard_risk_score`
- `water_level_rate_m_hr`: **0.3465**
- `pm10`: **0.2491**
- `rainfall_1h_mm`: **0.1991**
- `water_turbidity_ntu`: **0.0750**
- `water_level_m`: **0.0673**


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
