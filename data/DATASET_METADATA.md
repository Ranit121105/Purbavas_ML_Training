# Multi-Hazard Environmental Sensor Dataset for India (Purbavas)

## 1. Overview
This dataset contains high-frequency spatio-temporal environmental telemetry simulated across 7 disaster-prone geographic regions in India. It is designed to train and benchmark **Edge AI** and **Cloud Analytics** models for early detection, multi-hazard risk assessment, and proactive disaster prevention.

- **Total Telemetry Samples**: 30,240 records (90 days continuous at 30-minute intervals per node)
- **Sensor Nodes**: 7 distributed nodes representing distinct topographical/climatic zones
- **Data Format**: CSV (UTF-8)

---

## 2. Monitored Node Locations & Topographies

| Node ID | Region | Topography / Risk Profile | Primary Hazards |
| :--- | :--- | :--- | :--- |
| `NODE_ASSAM_01` | **Assam (Brahmaputra Basin)** | Riverine flood plain, high monsoon humidity | Flash Floods, River Spills |
| `NODE_BIHAR_02` | **Bihar (Kosi Basin)** | Flood-prone agricultural plain | River Inundation, Surge |
| `NODE_UK_FOREST_03` | **Uttarakhand (Garhwal Forest)** | Steep Himalayan forest slopes | Wildfires, Landslides |
| `NODE_HP_HILLS_04` | **Himachal Pradesh (Hills)** | High-altitude mountainous terrain | Slope Failure, Landslides, Forest Fires |
| `NODE_DELHI_NCR_05` | **Delhi-NCR (Urban)** | High-density urban sprawl | Severe Smog, Toxic Air Pollution (PM2.5/PM10) |
| `NODE_WG_WAYANAD_06` | **Western Ghats (Wayanad)** | Dense tropical hill slopes, heavy rain | Landslide Precursors, Torrential Flash Floods |
| `NODE_GUJ_IND_07` | **Gujarat Industrial Corridor** | Chemical manufacturing hub / coastal plain | Industrial Gas Leaks, VOCs, Water Pollution |

---

## 3. Telemetry Feature Schema

| Field Name | Type | Unit | Description / Range |
| :--- | :--- | :--- | :--- |
| `timestamp` | ISO 8601 String | UTC | Time of reading (e.g. `2026-06-01T00:00:00Z`) |
| `node_id` | String | - | Identifier of the edge sensor device |
| `region` | String | - | Indian administrative/geographic region |
| `latitude`, `longitude` | Float | Degrees | Geographic GPS coordinates |
| `elevation_m` | Float | Meters | Elevation above sea level (25m - 2100m) |
| `water_level_m` | Float | Meters | River / drain water surface level (0.5m - 12.0m) |
| `water_level_rate_m_hr` | Float | m/hour | Water level velocity $\frac{\Delta h}{\Delta t}$ |
| `rainfall_1h_mm` | Float | mm | Immediate 1-hour precipitation accumulation |
| `rainfall_6h_mm` | Float | mm | Rolling 6-hour rainfall accumulation |
| `rainfall_24h_mm` | Float | mm | Rolling 24-hour rainfall accumulation |
| `temperature_c` | Float | °C | Ambient air temperature (10°C - 49°C) |
| `humidity_pct` | Float | % | Relative humidity (12% - 100%) |
| `heat_index_c` | Float | °C | Calculated thermal heat index |
| `smoke_ppm` | Float | ppm | Optical smoke concentration (normal: <50, fire: 200-850) |
| `co_ppm` | Float | ppm | Carbon monoxide (normal: 0.5-2.0, fire/spill: 15-75) |
| `voc_ppb` | Float | ppb | Volatile Organic Compounds (normal: 50-200, leak: 1500-8500) |
| `so2_ug_m3` | Float | $\mu g/m^3$ | Sulfur Dioxide concentration |
| `no2_ug_m3` | Float | $\mu g/m^3$ | Nitrogen Dioxide concentration |
| `pm25` | Float | $\mu g/m^3$ | Particulate matter $\le 2.5\mu m$ (CPCB standard) |
| `pm10` | Float | $\mu g/m^3$ | Particulate matter $\le 10\mu m$ |
| `aqi_calculated` | Float | Index [0-500] | Indian National Air Quality Index |
| `soil_moisture_pct` | Float | % Volumetric | Soil water content (10% - 99% saturation) |
| `vibration_g` | Float | $g$ | RMS 3-axis ground acceleration / acoustic micro-slips |
| `tilt_angle_deg` | Float | Degrees | Inclinometer ground angle deviation from vertical |
| `water_ph` | Float | pH units [0-14] | River/runoff pH (normal: 6.5-8.5; acid: <5.5; caustic: >9.5) |
| `water_turbidity_ntu` | Float | NTU | Water clarity (normal: 5-30 NTU, silt/landslide runoff: >150 NTU) |
| `dissolved_oxygen_mg_l`| Float | mg/L | Dissolved oxygen (normal: >6.5 mg/L, hypoxic: <3.0 mg/L) |
| `battery_voltage_v` | Float | Volts | Edge node solar-battery voltage (3.3V - 4.2V) |
| `signal_rssi_dbm` | Float | dBm | LoRaWAN / NB-IoT network signal strength |

---

## 4. Ground Truth Labels & Target Variables

### A. Categorical Targets
1. `hazard_type`:
   - `NORMAL`: Baseline environmental conditions
   - `FLASH_FLOOD`: Extreme rainfall + rapid water rise + high turbidity
   - `FOREST_FIRE`: Elevated temperature + drop in humidity + smoke + CO spike
   - `HAZARDOUS_SMOG`: Severe PM2.5 / PM10 / $NO_2$ / $SO_2$ accumulation
   - `LANDSLIDE_PRECURSOR`: High soil saturation + seismic micro-vibrations + tilt displacement
   - `INDUSTRIAL_CHEMICAL_LEAK`: Massive VOC / toxic gas spike
   - `WATER_QUALITY_CRISIS`: Severe pH anomaly + depleted dissolved oxygen + high turbidity

2. `severity_level`:
   - `NONE`
   - `ADVISORY_LOW`
   - `WATCH_MODERATE`
   - `WARNING_HIGH`
   - `EMERGENCY_CRITICAL`

### B. Continuous Risk Targets (0.0 to 1.0)
- `flood_risk_score`
- `fire_risk_score`
- `air_pollution_risk_score`
- `landslide_risk_score`
- `chemical_hazard_risk_score`

---

## 5. Dataset File Structure

```
data/
├── raw/
│   └── environmental_sensor_telemetry.csv  (30,240 rows, 7.9 MB)
├── processed/
│   ├── train_data.csv                      (24,192 rows - 80% chronological train)
│   └── test_data.csv                       (6,048 rows - 20% chronological test)
└── DATASET_METADATA.md
```

---

## 6. How to Re-generate or Customize

You can run the generator at any time with custom parameters:

```powershell
powershell -ExecutionPolicy Bypass -File "src/data/generate_dataset.ps1"
```
Or with Python:
```bash
python src/data/generate_dataset.py
```
