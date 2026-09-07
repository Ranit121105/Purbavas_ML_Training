/*
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
