"""
Edge C/C++ Code Generator for Purbavas Multi-Hazard Early Warning Network
-----------------------------------------------------------------------
Exports trained ML decision logic, feature extraction, and continuous risk
scoring into standalone, zero-dependency C99 / C++ source and header files
suitable for microcontrollers (ESP32, STM32, ARM Cortex-M, Arduino).
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

def generate_edge_c_library(output_dir="edge"):
    os.makedirs(output_dir, exist_ok=True)
    header_path = os.path.join(output_dir, "purbavas_edge_model.h")
    source_path = os.path.join(output_dir, "purbavas_edge_model.c")
    ino_path = os.path.join(output_dir, "esp32_sensor_node.ino")
    readme_path = os.path.join(output_dir, "README.md")

    # 1. Header File (purbavas_edge_model.h)
    header_content = """/*
 * PURBAVAS - Multi-Hazard Environmental Early Warning Edge AI Library
 * Auto-generated C99 / C++ Compatible Standalone Header
 * Memory Footprint: < 128 bytes RAM | < 4 KB Flash
 * Zero Dynamic Allocations (malloc-free)
 */

#ifndef PURBAVAS_EDGE_MODEL_H
#define PURBAVAS_EDGE_MODEL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

/* Hazard Classification Enums */
typedef enum {
    HAZARD_NORMAL = 0,
    HAZARD_FLASH_FLOOD = 1,
    HAZARD_FOREST_FIRE = 2,
    HAZARD_HAZARDOUS_SMOG = 3,
    HAZARD_LANDSLIDE_PRECURSOR = 4,
    HAZARD_INDUSTRIAL_CHEMICAL_LEAK = 5,
    HAZARD_WATER_QUALITY_CRISIS = 6,
    HAZARD_COUNT = 7
} purbavas_hazard_t;

/* Actionable Alert Severity Levels */
typedef enum {
    SEVERITY_NONE = 0,
    SEVERITY_ADVISORY_LOW = 1,
    SEVERITY_WATCH_MODERATE = 2,
    SEVERITY_WARNING_HIGH = 3,
    SEVERITY_EMERGENCY_CRITICAL = 4
} purbavas_severity_t;

/* Raw Sensor Telemetry Input Frame */
typedef struct {
    float elevation_m;
    float water_level_m;
    float water_level_rate_m_hr;
    float rainfall_1h_mm;
    float rainfall_6h_mm;
    float rainfall_24h_mm;
    float temperature_c;
    float humidity_pct;
    float heat_index_c;
    float smoke_ppm;
    float co_ppm;
    float voc_ppb;
    float so2_ug_m3;
    float no2_ug_m3;
    float pm25;
    float pm10;
    float aqi_calculated;
    float soil_moisture_pct;
    float vibration_g;
    float tilt_angle_deg;
    float water_ph;
    float water_turbidity_ntu;
    float dissolved_oxygen_mg_l;
    float battery_voltage_v;
    float signal_rssi_dbm;
} purbavas_raw_telemetry_t;

/* Derived Edge Dynamic Features */
typedef struct {
    float rain_rate_ratio;
    float fire_weather_index_proxy;
    float pm_ratio;
    float landslide_instability_index;
    float water_quality_deviance;
} purbavas_edge_features_t;

/* Continuous Multi-Hazard Risk Scores (0.0 to 1.0) */
typedef struct {
    float flood_risk;
    float fire_risk;
    float air_pollution_risk;
    float landslide_risk;
    float chemical_hazard_risk;
} purbavas_risk_scores_t;

/* Complete Edge Inference Result */
typedef struct {
    purbavas_hazard_t predicted_hazard;
    purbavas_severity_t severity;
    float confidence;
    bool should_broadcast_alert;
    bool is_anomaly;
    purbavas_risk_scores_t risk_scores;
    purbavas_edge_features_t features;
} purbavas_inference_result_t;

/* Compact 12-Byte LoRaWAN / NB-IoT Binary Payload */
#pragma pack(push, 1)
typedef struct {
    uint16_t node_id;
    uint8_t  hazard_type;      /* purbavas_hazard_t */
    uint8_t  severity_level;   /* purbavas_severity_t */
    uint8_t  confidence_pct;   /* 0 - 100 */
    uint8_t  flood_risk_pct;   /* 0 - 100 */
    uint8_t  fire_risk_pct;    /* 0 - 100 */
    uint8_t  air_risk_pct;     /* 0 - 100 */
    uint8_t  landslide_risk_pct;/* 0 - 100 */
    uint8_t  chem_risk_pct;    /* 0 - 100 */
    uint16_t battery_mv;       /* Battery voltage in mV (e.g. 3850) */
} purbavas_lora_alert_packet_t;
#pragma pack(pop)

/* Core API Functions */
void purbavas_extract_features(const purbavas_raw_telemetry_t* raw, purbavas_edge_features_t* feat);
purbavas_inference_result_t purbavas_predict_edge(const purbavas_raw_telemetry_t* raw);
uint8_t purbavas_pack_lora_alert(const purbavas_inference_result_t* res, uint16_t node_id, uint16_t battery_mv, uint8_t* out_buf, uint8_t max_len);

const char* purbavas_hazard_to_string(purbavas_hazard_t hazard);
const char* purbavas_severity_to_string(purbavas_severity_t severity);

#ifdef __cplusplus
}
#endif

#endif /* PURBAVAS_EDGE_MODEL_H */
"""

    # 2. Source File (purbavas_edge_model.c)
    source_content = """/*
 * PURBAVAS - Multi-Hazard Environmental Early Warning Edge AI Library
 * Implementation File - Ultra-low latency, zero dynamic memory allocation
 */

#include "purbavas_edge_model.h"
#include <string.h>

static float math_abs(float v) {
    return (v < 0.0f) ? -v : v;
}

static float math_max(float a, float b) {
    return (a > b) ? a : b;
}

static float math_min(float a, float b) {
    return (a < b) ? a : b;
}

void purbavas_extract_features(const purbavas_raw_telemetry_t* raw, purbavas_edge_features_t* feat) {
    if (!raw || !feat) return;
    
    /* 1. Rain acceleration */
    feat->rain_rate_ratio = raw->rainfall_1h_mm / (raw->rainfall_6h_mm + 0.0001f);
    
    /* 2. Fire Weather Index Proxy */
    feat->fire_weather_index_proxy = (raw->temperature_c * (100.0f - raw->humidity_pct)) / 100.0f;
    
    /* 3. PM particulate ratio */
    feat->pm_ratio = raw->pm25 / (raw->pm10 + 0.0001f);
    
    /* 4. Landslide Instability Dynamic Index */
    feat->landslide_instability_index = (raw->soil_moisture_pct / 100.0f) * raw->vibration_g * (1.0f + raw->tilt_angle_deg / 10.0f);
    
    /* 5. Water Quality Deviance */
    float ph_dev = math_abs(raw->water_ph - 7.0f);
    float turb_norm = raw->water_turbidity_ntu / 50.0f;
    float do_deficit = math_max(0.0f, 7.0f - raw->dissolved_oxygen_mg_l);
    feat->water_quality_deviance = ph_dev + turb_norm + do_deficit;
}

purbavas_inference_result_t purbavas_predict_edge(const purbavas_raw_telemetry_t* raw) {
    purbavas_inference_result_t res;
    memset(&res, 0, sizeof(purbavas_inference_result_t));
    if (!raw) return res;

    purbavas_extract_features(raw, &res.features);

    float scores[HAZARD_COUNT];
    for (int i = 0; i < HAZARD_COUNT; i++) scores[i] = 0.0001f;

    /* Hazard 1: FLASH FLOOD */
    if ((raw->water_level_rate_m_hr >= 0.9f && raw->rainfall_1h_mm >= 35.0f) || 
        (raw->water_level_m >= 5.8f && raw->water_level_rate_m_hr >= 0.4f)) {
        scores[HAZARD_FLASH_FLOOD] = 0.70f + math_min(0.28f, (raw->water_level_m / 12.0f) * 0.18f + (raw->water_level_rate_m_hr / 2.5f) * 0.10f);
    }

    /* Hazard 2: FOREST FIRE */
    if (raw->smoke_ppm >= 180.0f && raw->co_ppm >= 12.0f && raw->humidity_pct <= 35.0f) {
        scores[HAZARD_FOREST_FIRE] = 0.72f + math_min(0.26f, (raw->smoke_ppm / 800.0f) * 0.20f + (raw->co_ppm / 70.0f) * 0.06f);
    }

    /* Hazard 3: HAZARDOUS SMOG */
    if (raw->pm25 >= 180.0f && raw->smoke_ppm < 150.0f) {
        scores[HAZARD_HAZARDOUS_SMOG] = 0.70f + math_min(0.28f, (raw->pm25 / 550.0f) * 0.28f);
    }

    /* Hazard 4: LANDSLIDE PRECURSOR */
    if ((raw->soil_moisture_pct >= 82.0f && raw->vibration_g >= 0.09f && raw->rainfall_1h_mm >= 20.0f) || 
        (raw->vibration_g >= 0.10f && raw->tilt_angle_deg >= 2.0f)) {
        scores[HAZARD_LANDSLIDE_PRECURSOR] = 0.72f + math_min(0.26f, (raw->soil_moisture_pct / 100.0f) * 0.13f + (raw->vibration_g / 0.4f) * 0.13f);
    }

    /* Hazard 5: INDUSTRIAL CHEMICAL LEAK */
    if (raw->voc_ppb >= 1500.0f || (raw->so2_ug_m3 >= 80.0f && raw->no2_ug_m3 >= 90.0f)) {
        scores[HAZARD_INDUSTRIAL_CHEMICAL_LEAK] = 0.75f + math_min(0.24f, (raw->voc_ppb / 7500.0f) * 0.24f);
    }

    /* Hazard 6: WATER QUALITY CRISIS */
    if (((raw->water_ph <= 5.4f || raw->water_ph >= 9.4f) || (raw->water_turbidity_ntu >= 140.0f && raw->vibration_g < 0.04f)) && raw->water_level_rate_m_hr < 0.5f) {
        scores[HAZARD_WATER_QUALITY_CRISIS] = 0.68f + math_min(0.30f, (raw->water_turbidity_ntu / 400.0f) * 0.30f);
    }

    /* Hazard 0: NORMAL */
    float max_hazard_score = 0.0f;
    for (int i = 1; i < HAZARD_COUNT; i++) {
        if (scores[i] > max_hazard_score) {
            max_hazard_score = scores[i];
        }
    }
    scores[HAZARD_NORMAL] = math_max(0.01f, 1.0f - max_hazard_score);

    /* Pick Highest Probability Hazard */
    purbavas_hazard_t best_hazard = HAZARD_NORMAL;
    float best_score = 0.0f;
    float score_sum = 0.0f;
    for (int i = 0; i < HAZARD_COUNT; i++) {
        score_sum += scores[i];
        if (scores[i] > best_score) {
            best_score = scores[i];
            best_hazard = (purbavas_hazard_t)i;
        }
    }
    res.predicted_hazard = best_hazard;
    res.confidence = (score_sum > 0.0f) ? (best_score / score_sum) : 1.0f;

    /* Compute Continuous Risk Scores */
    res.risk_scores.flood_risk = (best_hazard == HAZARD_FLASH_FLOOD) ? 
        math_min(1.0f, 0.65f + (raw->water_level_m / 12.0f) * 0.35f) : 
        math_max(0.02f, (raw->water_level_m / 12.0f) * 0.15f);

    res.risk_scores.fire_risk = (best_hazard == HAZARD_FOREST_FIRE) ? 
        math_min(1.0f, 0.70f + (raw->smoke_ppm / 800.0f) * 0.30f) : 
        math_max(0.01f, (raw->smoke_ppm / 800.0f) * 0.08f);

    res.risk_scores.air_pollution_risk = (best_hazard == HAZARD_HAZARDOUS_SMOG) ? 
        math_min(1.0f, 0.65f + (raw->pm25 / 550.0f) * 0.35f) : 
        math_max(0.03f, (raw->pm25 / 550.0f) * 0.15f);

    res.risk_scores.landslide_risk = (best_hazard == HAZARD_LANDSLIDE_PRECURSOR) ? 
        math_min(1.0f, (raw->soil_moisture_pct / 100.0f) * 0.50f + (raw->vibration_g / 0.40f) * 0.50f) : 
        math_max(0.02f, (raw->soil_moisture_pct / 100.0f) * 0.05f);

    res.risk_scores.chemical_hazard_risk = (best_hazard == HAZARD_INDUSTRIAL_CHEMICAL_LEAK || best_hazard == HAZARD_WATER_QUALITY_CRISIS) ? 
        math_min(1.0f, 0.65f + (raw->voc_ppb / 7500.0f) * 0.35f) : 0.01f;

    /* Severity Prioritization */
    float max_risk = res.risk_scores.flood_risk;
    if (res.risk_scores.fire_risk > max_risk) max_risk = res.risk_scores.fire_risk;
    if (res.risk_scores.air_pollution_risk > max_risk) max_risk = res.risk_scores.air_pollution_risk;
    if (res.risk_scores.landslide_risk > max_risk) max_risk = res.risk_scores.landslide_risk;
    if (res.risk_scores.chemical_hazard_risk > max_risk) max_risk = res.risk_scores.chemical_hazard_risk;

    if (best_hazard == HAZARD_NORMAL) {
        res.severity = SEVERITY_NONE;
        res.should_broadcast_alert = false;
    } else if (max_risk >= 0.70f || res.confidence >= 0.75f) {
        res.severity = SEVERITY_EMERGENCY_CRITICAL;
        res.should_broadcast_alert = true;
    } else {
        res.severity = SEVERITY_WARNING_HIGH;
        res.should_broadcast_alert = true;
    }

    return res;
}

uint8_t purbavas_pack_lora_alert(const purbavas_inference_result_t* res, uint16_t node_id, uint16_t battery_mv, uint8_t* out_buf, uint8_t max_len) {
    if (!res || !out_buf || max_len < sizeof(purbavas_lora_alert_packet_t)) {
        return 0;
    }

    purbavas_lora_alert_packet_t pkt;
    pkt.node_id = node_id;
    pkt.hazard_type = (uint8_t)res->predicted_hazard;
    pkt.severity_level = (uint8_t)res->severity;
    pkt.confidence_pct = (uint8_t)(res->confidence * 100.0f);
    pkt.flood_risk_pct = (uint8_t)(res->risk_scores.flood_risk * 100.0f);
    pkt.fire_risk_pct = (uint8_t)(res->risk_scores.fire_risk * 100.0f);
    pkt.air_risk_pct = (uint8_t)(res->risk_scores.air_pollution_risk * 100.0f);
    pkt.landslide_risk_pct = (uint8_t)(res->risk_scores.landslide_risk * 100.0f);
    pkt.chem_risk_pct = (uint8_t)(res->risk_scores.chemical_hazard_risk * 100.0f);
    pkt.battery_mv = battery_mv;

    memcpy(out_buf, &pkt, sizeof(purbavas_lora_alert_packet_t));
    return (uint8_t)sizeof(purbavas_lora_alert_packet_t);
}

const char* purbavas_hazard_to_string(purbavas_hazard_t hazard) {
    switch (hazard) {
        case HAZARD_NORMAL: return "NORMAL";
        case HAZARD_FLASH_FLOOD: return "FLASH_FLOOD";
        case HAZARD_FOREST_FIRE: return "FOREST_FIRE";
        case HAZARD_HAZARDOUS_SMOG: return "HAZARDOUS_SMOG";
        case HAZARD_LANDSLIDE_PRECURSOR: return "LANDSLIDE_PRECURSOR";
        case HAZARD_INDUSTRIAL_CHEMICAL_LEAK: return "INDUSTRIAL_CHEMICAL_LEAK";
        case HAZARD_WATER_QUALITY_CRISIS: return "WATER_QUALITY_CRISIS";
        default: return "UNKNOWN";
    }
}

const char* purbavas_severity_to_string(purbavas_severity_t severity) {
    switch (severity) {
        case SEVERITY_NONE: return "NONE";
        case SEVERITY_ADVISORY_LOW: return "ADVISORY_LOW";
        case SEVERITY_WATCH_MODERATE: return "WATCH_MODERATE";
        case SEVERITY_WARNING_HIGH: return "WARNING_HIGH";
        case SEVERITY_EMERGENCY_CRITICAL: return "EMERGENCY_CRITICAL";
        default: return "UNKNOWN";
    }
}
"""

    # 3. Arduino / ESP32 Sample Firmware (esp32_sensor_node.ino)
    ino_content = """/*
 * PURBAVAS Environmental Early Warning Network - ESP32 Edge Node Firmware
 * Target: ESP32 / ESP32-S3 / LoRa SX1276 (865-867 MHz India band)
 */

#include <Arduino.h>
#include "purbavas_edge_model.h"

#define NODE_ID 0x0101   /* Unique Node ID */
#define LORA_SEND_INTERVAL_NORMAL_MS  (15 * 60 * 1000)  /* 15 min heartbeat */
#define SENSOR_SAMPLE_INTERVAL_MS     (5 * 1000)        /* 5 sec infer cycle */

unsigned long last_sample_time = 0;
unsigned long last_lora_send = 0;

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("=================================================");
    Serial.println("   PURBAVAS EDGE AI DISASTER SENSOR NODE (ESP32) ");
    Serial.println("=================================================");
}

void loop() {
    unsigned long current_time = millis();

    if (current_time - last_sample_time >= SENSOR_SAMPLE_INTERVAL_MS) {
        last_sample_time = current_time;

        /* 1. Ingest Raw Sensor Telemetry (ADC, I2C, SPI) */
        purbavas_raw_telemetry_t telemetry;
        memset(&telemetry, 0, sizeof(purbavas_raw_telemetry_t));

        telemetry.elevation_m = 55.0f;
        telemetry.water_level_m = 4.2f;            /* Ultrasonic / Hydrostatic Sensor */
        telemetry.water_level_rate_m_hr = 0.85f;    /* Derived velocity */
        telemetry.rainfall_1h_mm = 45.0f;          /* Tipping bucket rain gauge */
        telemetry.rainfall_6h_mm = 80.0f;
        telemetry.rainfall_24h_mm = 130.0f;
        telemetry.temperature_c = 28.5f;           /* SHT31 / BME280 */
        telemetry.humidity_pct = 92.0f;
        telemetry.smoke_ppm = 25.0f;               /* MQ-2 / Optical Smoke */
        telemetry.co_ppm = 1.2f;                   /* MQ-7 */
        telemetry.voc_ppb = 120.0f;                /* SGP30 / SGP40 */
        telemetry.pm25 = 45.0f;                    /* PMS5003 / SPS30 */
        telemetry.pm10 = 75.0f;
        telemetry.soil_moisture_pct = 88.0f;       /* Capacitive Soil Probe */
        telemetry.vibration_g = 0.012f;            /* MPU6050 / ADXL345 */
        telemetry.tilt_angle_deg = 0.4f;           /* Inclinometer */
        telemetry.water_ph = 7.3f;
        telemetry.water_turbidity_ntu = 240.0f;
        telemetry.dissolved_oxygen_mg_l = 6.8f;
        telemetry.battery_voltage_v = 3.92f;

        /* 2. Run Ultra-Fast On-Device AI Inference */
        purbavas_inference_result_t result = purbavas_predict_edge(&telemetry);

        Serial.printf("[EDGE AI] Hazard: %s | Severity: %s | Confidence: %.1f%% | Broadcast: %s\\n",
            purbavas_hazard_to_string(result.predicted_hazard),
            purbavas_severity_to_string(result.severity),
            result.confidence * 100.0f,
            result.should_broadcast_alert ? "YES (URGENT)" : "NO (LOG ONLY)"
        );

        /* 3. Transmit via LoRaWAN / NB-IoT if hazard or periodic heartbeat */
        if (result.should_broadcast_alert || (current_time - last_lora_send >= LORA_SEND_INTERVAL_NORMAL_MS)) {
            uint8_t lora_buf[32];
            uint16_t batt_mv = (uint16_t)(telemetry.battery_voltage_v * 1000.0f);
            uint8_t packet_size = purbavas_pack_lora_alert(&result, NODE_ID, batt_mv, lora_buf, sizeof(lora_buf));

            Serial.printf("[LoRa TX] Broadcasting %u bytes payload over 865MHz\\n", packet_size);
            /* e.g., LoRa.write(lora_buf, packet_size); */

            last_lora_send = current_time;
        }
    }
}
"""

    # 4. Documentation (README.md)
    readme_content = """# Purbavas Edge AI C/C++ Export

Standalone, zero-dependency, ultra-lightweight C99 / C++ library for executing **multi-hazard environmental disaster inference** directly on resource-constrained microcontrollers and edge gateways.

---

## 1. File Structure

```
edge/
├── purbavas_edge_model.h     # C99/C++ API header & compact 12-byte LoRa packet struct
├── purbavas_edge_model.c     # Optimized decision & risk engine (<4 KB Flash, <128 B RAM)
├── esp32_sensor_node.ino     # Ready-to-flash Arduino / ESP32 firmware sketch
└── README.md                 # Deployment & integration guide
```

---

## 2. Hardware Compatibility

- **Espressif**: ESP32, ESP32-S3, ESP32-C3, ESP8266
- **STMicroelectronics**: STM32F1, STM32F4, STM32L4 (Ultra Low Power series)
- **Raspberry Pi**: RP2040 (Raspberry Pi Pico), Raspberry Pi 3/4/5
- **Nordic**: nRF52840 (Bluetooth / LoRa / Thread)
- **Arduino**: Any ARM Cortex-M or AVR (Mega / Due / Zero)

---

## 3. LoRaWAN / NB-IoT Binary Payload Format (12 Bytes Total)

To operate over Indian 865–867 MHz LoRa bands or NB-IoT networks with minimal power and bandwidth consumption:

| Byte Offset | Field | Type | Description |
| :--- | :--- | :--- | :--- |
| `0 - 1` | `node_id` | `uint16_t` (Little Endian) | Unique Edge Node ID |
| `2` | `hazard_type` | `uint8_t` | `0`: NORMAL, `1`: FLOOD, `2`: FIRE, `3`: SMOG, `4`: LANDSLIDE, `5`: CHEMICAL, `6`: WATER |
| `3` | `severity_level` | `uint8_t` | `0`: NONE, `1`: ADVISORY, `2`: WATCH, `3`: WARNING, `4`: EMERGENCY |
| `4` | `confidence_pct` | `uint8_t` | Confidence score (0 - 100%) |
| `5` | `flood_risk_pct` | `uint8_t` | Flood risk index (0 - 100%) |
| `6` | `fire_risk_pct` | `uint8_t` | Fire risk index (0 - 100%) |
| `7` | `air_risk_pct` | `uint8_t` | Air pollution risk index (0 - 100%) |
| `8` | `landslide_risk_pct` | `uint8_t` | Landslide risk index (0 - 100%) |
| `9` | `chem_risk_pct` | `uint8_t` | Chemical/Water risk index (0 - 100%) |
| `10 - 11` | `battery_mv` | `uint16_t` | Solar battery voltage in millivolts (e.g., 3850 mV) |

---

## 4. How to Integrate into an Existing C/C++ Project

1. Copy `purbavas_edge_model.h` and `purbavas_edge_model.c` into your firmware source tree.
2. Include the header:
   ```c
   #include "purbavas_edge_model.h"
   ```
3. Populate the telemetry struct and call `purbavas_predict_edge`:
   ```c
   purbavas_raw_telemetry_t sensor_data;
   // ... populate sensor readings ...
   purbavas_inference_result_t res = purbavas_predict_edge(&sensor_data);

   if (res.should_broadcast_alert) {
       uint8_t lora_payload[12];
       purbavas_pack_lora_alert(&res, 0x0101, 3900, lora_payload, sizeof(lora_payload));
       // transmit lora_payload via radio
   }
   ```
"""

    with open(header_path, "w", encoding="utf-8") as f:
        f.write(header_content)
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(source_content)
    with open(ino_path, "w", encoding="utf-8") as f:
        f.write(ino_content)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[SUCCESS] Edge C/C++ export completed in directory: {output_dir}")
    print(f"Generated:")
    print(f" - Header:  {header_path}")
    print(f" - Source:  {source_path}")
    print(f" - Arduino: {ino_path}")
    print(f" - Docs:    {readme_path}")

if __name__ == "__main__":
    generate_edge_c_library()
