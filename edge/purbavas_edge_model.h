/*
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
