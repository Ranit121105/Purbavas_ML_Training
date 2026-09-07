# Purbavas Edge AI C/C++ Export

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
