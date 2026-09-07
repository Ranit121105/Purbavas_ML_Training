"""
Multi-Hazard Environmental Sensor Telemetry Dataset Generator (High-Fidelity)
----------------------------------------------------------------------------
Simulates continuous, realistic spatio-temporal telemetry across 7 disaster-prone Indian regions.
"""

import os
import math
import random
from datetime import datetime, timedelta

def generate_environmental_dataset(
    output_raw_path="data/raw/environmental_sensor_telemetry.csv",
    output_train_path="data/processed/train_data.csv",
    output_test_path="data/processed/test_data.csv",
    num_days=90,
    interval_minutes=30,
    seed=42
):
    random.seed(seed)
    os.makedirs(os.path.dirname(output_raw_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_train_path), exist_ok=True)

    nodes = [
        {
            "node_id": "NODE_ASSAM_01", "region": "Assam_Brahmaputra_Basin",
            "lat": 26.1850, "lon": 91.7450, "elevation": 55.0, "hazards": ["FLASH_FLOOD"],
            "base_temp": 28.0, "base_hum": 82.0, "base_soil": 55.0, "base_water": 3.2
        },
        {
            "node_id": "NODE_BIHAR_02", "region": "Bihar_Kosi_Basin",
            "lat": 25.5941, "lon": 85.1376, "elevation": 53.0, "hazards": ["FLASH_FLOOD"],
            "base_temp": 30.0, "base_hum": 78.0, "base_soil": 50.0, "base_water": 2.8
        },
        {
            "node_id": "NODE_UK_FOREST_03", "region": "Uttarakhand_Garhwal_Forest",
            "lat": 30.3165, "lon": 78.0322, "elevation": 1450.0, "hazards": ["FOREST_FIRE", "LANDSLIDE_PRECURSOR"],
            "base_temp": 24.0, "base_hum": 45.0, "base_soil": 35.0, "base_water": 0.8
        },
        {
            "node_id": "NODE_HP_HILLS_04", "region": "Himachal_Pradesh_Hills",
            "lat": 31.1048, "lon": 77.1734, "elevation": 2100.0, "hazards": ["LANDSLIDE_PRECURSOR", "FOREST_FIRE"],
            "base_temp": 19.0, "base_hum": 50.0, "base_soil": 40.0, "base_water": 0.6
        },
        {
            "node_id": "NODE_DELHI_NCR_05", "region": "Delhi_NCR_Urban",
            "lat": 28.6139, "lon": 77.2090, "elevation": 216.0, "hazards": ["HAZARDOUS_SMOG"],
            "base_temp": 32.0, "base_hum": 58.0, "base_soil": 25.0, "base_water": 1.2
        },
        {
            "node_id": "NODE_WG_WAYANAD_06", "region": "Western_Ghats_Wayanad",
            "lat": 11.6854, "lon": 76.1320, "elevation": 820.0, "hazards": ["LANDSLIDE_PRECURSOR", "FLASH_FLOOD"],
            "base_temp": 23.0, "base_hum": 88.0, "base_soil": 60.0, "base_water": 1.5
        },
        {
            "node_id": "NODE_GUJ_IND_07", "region": "Gujarat_Industrial_Corridor",
            "lat": 21.6032, "lon": 72.9774, "elevation": 25.0, "hazards": ["INDUSTRIAL_CHEMICAL_LEAK", "WATER_QUALITY_CRISIS"],
            "base_temp": 34.0, "base_hum": 65.0, "base_soil": 30.0, "base_water": 1.1
        }
    ]

    headers = [
        "timestamp", "node_id", "region", "latitude", "longitude", "elevation_m",
        "water_level_m", "water_level_rate_m_hr", "rainfall_1h_mm", "rainfall_6h_mm", "rainfall_24h_mm",
        "temperature_c", "humidity_pct", "heat_index_c",
        "smoke_ppm", "co_ppm", "voc_ppb", "so2_ug_m3", "no2_ug_m3",
        "pm25", "pm10", "aqi_calculated",
        "soil_moisture_pct", "vibration_g", "tilt_angle_deg",
        "water_ph", "water_turbidity_ntu", "dissolved_oxygen_mg_l",
        "battery_voltage_v", "signal_rssi_dbm",
        "hazard_type", "severity_level",
        "flood_risk_score", "fire_risk_score", "air_pollution_risk_score", "landslide_risk_score", "chemical_hazard_risk_score"
    ]

    start_time = datetime(2026, 6, 1, 0, 0, 0)
    total_steps = int((num_days * 24 * 60) / interval_minutes)

    node_states = {}
    for node in nodes:
        node_states[node["node_id"]] = {
            "water": node["base_water"],
            "soil": node["base_soil"],
            "tilt": 0.2 + random.uniform(0, 0.2),
            "event": "NORMAL",
            "event_steps": 0,
            "normal_steps": random.randint(30, 80),
            "rain_hist": [0.0] * 12
        }

    records = []

    for step in range(total_steps):
        curr_dt = start_time + timedelta(minutes=step * interval_minutes)
        hour = curr_dt.hour
        diurnal_temp = math.sin(math.pi * (hour - 9) / 12.0) * 5.0
        diurnal_hum = -math.sin(math.pi * (hour - 9) / 12.0) * 12.0

        for node in nodes:
            nid = node["node_id"]
            st = node_states[nid]

            if st["event_steps"] > 0:
                st["event_steps"] -= 1
                if st["event_steps"] == 0:
                    st["event"] = "NORMAL"
                    st["normal_steps"] = random.randint(40, 100)
            else:
                st["normal_steps"] -= 1
                if st["normal_steps"] <= 0:
                    possible = node["hazards"]
                    st["event"] = random.choice(possible)
                    st["event_steps"] = random.randint(16, 40)

            event = st["event"]
            temp = max(10.0, node["base_temp"] + diurnal_temp + random.uniform(-1.0, 1.0))
            hum = min(100.0, max(15.0, node["base_hum"] + diurnal_hum + random.uniform(-2.0, 2.0)))
            heat_idx = temp + 0.05 * hum

            rain_1h = 0.0
            if node["base_hum"] > 60.0 and random.random() < 0.25:
                rain_1h = round(random.uniform(0.0, 3.5), 2)

            smoke = max(5.0, 25.0 + random.uniform(-5.0, 5.0))
            co = max(0.1, 1.2 + random.uniform(-0.3, 0.3))
            voc = max(30.0, 120.0 + random.uniform(-20.0, 20.0))
            so2 = max(2.0, 12.0 + random.uniform(-3.0, 3.0))
            no2 = max(5.0, 22.0 + random.uniform(-4.0, 4.0))
            pm25 = max(10.0, 45.0 + random.uniform(-10.0, 10.0))
            pm10 = pm25 * random.uniform(1.5, 1.9)
            vib = max(0.002, 0.008 + random.uniform(-0.002, 0.002))
            tilt = st["tilt"]
            ph = max(6.2, min(8.4, 7.3 + random.uniform(-0.2, 0.2)))
            turbidity = max(2.0, 12.0 + random.uniform(-3.0, 3.0))
            do2 = max(4.0, 7.5 + random.uniform(-0.4, 0.4))
            water_rate = 0.0

            severity = "NONE"
            flood_risk = 0.05
            fire_risk = 0.02
            air_risk = 0.08
            landslide_risk = 0.03
            chem_risk = 0.01

            if event == "FLASH_FLOOD":
                rain_1h = round(random.uniform(45.0, 105.0), 2)
                st["water"] = min(12.0, st["water"] + random.uniform(0.45, 0.90))
                water_rate = round(random.uniform(1.1, 2.6), 3)
                st["soil"] = min(98.0, st["soil"] + random.uniform(6.0, 12.0))
                turbidity = round(random.uniform(180.0, 530.0), 2)
                do2 = max(2.5, do2 - 2.0)
                flood_risk = min(1.0, 0.65 + (st["water"] / 12.0) * 0.35)
                severity = "EMERGENCY_CRITICAL" if st["water"] > 6.5 else "WARNING_HIGH"

            elif event == "FOREST_FIRE":
                temp = min(48.0, temp + random.uniform(12.0, 18.0))
                hum = max(12.0, hum - 25.0)
                smoke = round(random.uniform(280.0, 830.0), 2)
                co = round(random.uniform(22.0, 67.0), 2)
                pm25 = round(random.uniform(320.0, 720.0), 2)
                pm10 = pm25 * random.uniform(1.8, 2.3)
                fire_risk = min(1.0, 0.70 + (smoke / 800.0) * 0.3)
                air_risk = min(1.0, 0.60 + (pm25 / 750.0) * 0.4)
                severity = "EMERGENCY_CRITICAL" if smoke > 450.0 else "WARNING_HIGH"

            elif event == "HAZARDOUS_SMOG":
                pm25 = round(random.uniform(240.0, 560.0), 2)
                pm10 = round(random.uniform(410.0, 860.0), 2)
                so2 = round(random.uniform(55.0, 130.0), 2)
                no2 = round(random.uniform(85.0, 180.0), 2)
                co = round(random.uniform(6.5, 14.5), 2)
                air_risk = min(1.0, 0.65 + (pm25 / 550.0) * 0.35)
                severity = "EMERGENCY_CRITICAL" if pm25 > 320.0 else "WARNING_HIGH"

            elif event == "LANDSLIDE_PRECURSOR":
                rain_1h = round(random.uniform(30.0, 75.0), 2)
                st["soil"] = min(99.0, max(84.0, st["soil"] + random.uniform(4.0, 7.0)))
                vib = round(random.uniform(0.12, 0.47), 4)
                st["tilt"] = min(20.0, st["tilt"] + random.uniform(0.8, 2.3))
                tilt = st["tilt"]
                turbidity = round(random.uniform(160.0, 380.0), 2)
                landslide_risk = min(1.0, (st["soil"] / 100.0) * 0.5 + (vib / 0.4) * 0.5)
                severity = "EMERGENCY_CRITICAL" if (vib > 0.22 or tilt > 5.0) else "WARNING_HIGH"

            elif event == "INDUSTRIAL_CHEMICAL_LEAK":
                voc = round(random.uniform(2200.0, 7700.0), 2)
                so2 = round(random.uniform(110.0, 290.0), 2)
                no2 = round(random.uniform(120.0, 270.0), 2)
                co = round(random.uniform(16.0, 44.0), 2)
                chem_risk = min(1.0, 0.70 + (voc / 7500.0) * 0.3)
                severity = "EMERGENCY_CRITICAL" if voc > 3800.0 else "WARNING_HIGH"

            elif event == "WATER_QUALITY_CRISIS":
                ph = round(random.uniform(4.0, 5.2), 2) if random.random() < 0.5 else round(random.uniform(9.8, 11.3), 2)
                turbidity = round(random.uniform(180.0, 480.0), 2)
                do2 = max(1.0, round(random.uniform(1.5, 3.0), 2))
                chem_risk = min(1.0, 0.60 + (turbidity / 500.0) * 0.4)
                severity = "WARNING_HIGH"

            else:
                st["water"] = max(node["base_water"], st["water"] - 0.05)
                st["soil"] = max(node["base_soil"], st["soil"] - 0.2)
                st["tilt"] = max(0.2, st["tilt"] - 0.02)
                tilt = st["tilt"]

            st["rain_hist"].pop(0)
            st["rain_hist"].append(rain_1h)
            rain_6h = round(sum(st["rain_hist"]), 2)
            rain_24h = round(rain_6h * random.uniform(2.0, 3.0), 2)

            # AQI sub-index
            if pm25 <= 30: aqi = pm25 * (50.0/30.0)
            elif pm25 <= 60: aqi = 50.0 + (pm25 - 30.0) * (50.0/30.0)
            elif pm25 <= 90: aqi = 100.0 + (pm25 - 60.0) * (100.0/30.0)
            elif pm25 <= 120: aqi = 200.0 + (pm25 - 90.0) * (100.0/30.0)
            elif pm25 <= 250: aqi = 300.0 + (pm25 - 120.0) * (100.0/130.0)
            else: aqi = 400.0 + (pm25 - 250.0) * (100.0/130.0)
            aqi = min(500.0, max(15.0, round(aqi, 1)))

            batt = round(random.uniform(3.7, 4.15), 2)
            rssi = round(random.uniform(-105.0, -70.0), 1)

            rec = [
                curr_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                nid, node["region"], node["lat"], node["lon"], node["elevation"],
                round(st["water"], 2), water_rate, rain_1h, rain_6h, rain_24h,
                round(temp, 2), round(hum, 2), round(heat_idx, 2),
                round(smoke, 2), round(co, 2), round(voc, 2), round(so2, 2), round(no2, 2),
                round(pm25, 2), round(pm10, 2), aqi,
                round(st["soil"], 2), vib, round(tilt, 2),
                round(ph, 2), round(turbidity, 2), round(do2, 2),
                batt, rssi, event, severity,
                round(flood_risk, 3), round(fire_risk, 3), round(air_risk, 3), round(landslide_risk, 3), round(chem_risk, 3)
            ]
            records.append(rec)

    def write_csv(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")
            for r in rows:
                f.write(",".join(str(x) for x in r) + "\n")

    split_idx = int(len(records) * 0.8)
    train_rows = records[:split_idx]
    test_rows = records[split_idx:]

    write_csv(output_raw_path, records)
    write_csv(output_train_path, train_rows)
    write_csv(output_test_path, test_rows)
    print(f"Generated {len(records)} records. Train: {len(train_rows)}, Test: {len(test_rows)}")

if __name__ == "__main__":
    generate_environmental_dataset()
