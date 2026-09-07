# ESP32 + SX1276 LoRa Environmental Node Hardware Setup

Guide for connecting, configuring, and flashing the **Purbavas On-Device ML Early Warning Firmware** on an **ESP32** microcontroller with a **Semtech SX1276 LoRa transceiver**.

---

## 1. Pin Wiring Diagram

### A. ESP32 to SX1276 LoRa Module (SPI Interface)

| SX1276 Pin | ESP32 GPIO Pin | Function | Notes |
| :--- | :--- | :--- | :--- |
| **VCC** | `3.3V` | Power Supply | **Do NOT connect to 5V!** |
| **GND** | `GND` | Ground | Common system ground |
| **NSS / CS** | `GPIO 5` | SPI Chip Select | Software configurable |
| **RST** | `GPIO 14` | Radio Reset | Active Low |
| **DIO0** | `GPIO 26` | Tx/Rx Done Interrupt | Required for LoRa packet events |
| **SCK** | `GPIO 18` | SPI Clock | Hardware VSPI SCK |
| **MISO** | `GPIO 19` | Master In Slave Out | Hardware VSPI MISO |
| **MOSI** | `GPIO 27` | Master Out Slave In | Hardware VSPI MOSI |

---

### B. Sensor Pin Connections

| Sensor Type | Sensor Model | Interface | ESP32 GPIO Pin | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Water Level** | JSN-SR04T / HC-SR04 | GPIO Pulse | `Trig: GPIO 4`, `Echo: GPIO 34` | Ultrasonic distance / river gauge |
| **Rainfall Gauge** | Tipping Bucket | Digital Interrupt | `GPIO 13` (Pullup) | Pulse counter ($0.2\text{ mm}$/tip) |
| **Soil Moisture** | Capacitive V1.2 | Analog (ADC1) | `GPIO 32` | Volumetric soil water saturation |
| **Gas / Smoke** | MQ-2 / MQ-7 / SGP30 | Analog / I2C | `GPIO 33` / (`SDA 21`, `SCL 22`) | Smoke, CO, and VOC concentration |
| **Vibration / Tilt** | MPU6050 / ADXL345 | I2C | `SDA: GPIO 21`, `SCL: GPIO 22` | Seismic micro-tremor & slope angle |
| **Air Quality (PM)**| PMS5003 / SPS30 | UART (Serial2) | `RX: GPIO 16`, `TX: GPIO 17` | PM2.5 / PM10 particulate matter |
| **Battery Monitor** | 18650 Li-ion ($3.7\text{V}$) | Voltage Divider | `GPIO 35` (100k:100k) | Measures battery voltage ($3.0\text{V} - 4.2\text{V}$) |

---

## 2. Indian LoRa Band (IN865) Configuration

The firmware is pre-configured for the **India ISM Band (865 – 867 MHz)**:
- **Center Frequency**: `865.2 MHz` (or `866.5 MHz`)
- **Spreading Factor**: `SF7` (optimizes on-air transmission time to $\approx 35\text{ ms}$)
- **Bandwidth**: `125 kHz`
- **Coding Rate**: `4/5`
- **Tx Power**: `20 dBm` (maximum permissible EIRP boost for long-range remote valley penetration)

---

## 3. How to Compile & Flash via Arduino IDE

1. **Install Board Support**:
   - In Arduino IDE $\rightarrow$ **Tools** $\rightarrow$ **Board** $\rightarrow$ **Boards Manager**, search and install **`esp32 by Espressif Systems`**.
   - Select Board: **`ESP32 Dev Module`**.
2. **Install Required Library**:
   - In Arduino IDE $\rightarrow$ **Tools** $\rightarrow$ **Manage Libraries**, search and install **`LoRa by Sandeep Mistry`** (version 0.8.0 or newer).
3. **Open Project**:
   - Open [`edge/esp32_purbavas_node.ino`](file:///c:/Users/RANIT/OneDrive/Desktop/Purbavas/edge/esp32_purbavas_node.ino).
   - Ensure [`edge/purbavas_edge_model.h`](file:///c:/Users/RANIT/OneDrive/Desktop/Purbavas/edge/purbavas_edge_model.h) and [`edge/purbavas_edge_model.c`](file:///c:/Users/RANIT/OneDrive/Desktop/Purbavas/edge/purbavas_edge_model.c) are in the same folder.
4. **Compile & Upload**:
   - Connect your ESP32 board via USB.
   - Select the corresponding COM port and click **Upload** ($\rightarrow$).
   - Open Serial Monitor at **`115200 baud`** to observe real-time sensor ingestion, on-device AI inference, and LoRa packet transmissions.
