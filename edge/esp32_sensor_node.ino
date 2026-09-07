/*
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

        Serial.printf("[EDGE AI] Hazard: %s | Severity: %s | Confidence: %.1f%% | Broadcast: %s\n",
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

            Serial.printf("[LoRa TX] Broadcasting %u bytes payload over 865MHz\n", packet_size);
            /* e.g., LoRa.write(lora_buf, packet_size); */

            last_lora_send = current_time;
        }
    }
}
