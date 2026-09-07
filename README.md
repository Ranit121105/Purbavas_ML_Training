# Purbavas: Multi-Hazard Environmental Early Warning AI Network

An AI-powered environmental monitoring network that provides early detection, localized intelligence, and actionable alerts for floods, forest fires, hazardous pollution episodes, landslide precursors, and industrial chemical leaks across India.

---

## 📌 Repository Architecture

```
Purbavas/
├── data/
│   ├── raw/
│   │   └── environmental_sensor_telemetry.csv  # 30,240 records across 7 Indian zones
│   ├── processed/
│   │   ├── train_data.csv                      # Chronological train partition (80%)
│   │   └── test_data.csv                       # Unseen test partition (20%)
│   └── DATASET_METADATA.md                     # Comprehensive schema & parameter docs
├── edge/
│   ├── purbavas_edge_model.h                   # C99/C++ embedded API & LoRa packet struct
│   ├── purbavas_edge_model.c                   # Standalone zero-heap (<128B RAM) inference engine
│   ├── esp32_purbavas_node.ino                 # ESP32 + SX1276 LoRa firmware sketch
│   ├── HARDWARE_SETUP.md                       # Wiring pinouts & flashing manual
│   └── README.md                               # Microcontroller integration guide
├── models/
│   ├── multi_hazard_model_bundle.pkl           # Trained Python ensemble bundle
│   ├── multi_hazard_model_weights.json         # Transparent, human-readable model weights
│   └── MODEL_ARCHITECTURE.md                   # Feature importance rankings & decision logic
├── results/
│   ├── evaluation_report.json                  # Machine-readable test benchmark report
│   └── confusion_matrix.csv                    # 7x7 hazard confusion matrix
├── src/
│   ├── data/
│   │   ├── generate_dataset.py                 # Telemetry simulation script
│   │   └── generate_dataset.ps1                # PowerShell dataset generator
│   └── models/
│       ├── train.py                            # Supervised & Anomaly model training
│       ├── evaluate.py                         # Test set benchmarking & safety audit
│       ├── inference.py                        # Real-time streaming inference engine
│       ├── export_edge_c.py                    # Edge C/C++ code exporter
│       ├── export_readable_weights.py          # JSON weights exporter
│       └── train_and_evaluate.ps1              # Automated training runner
├── requirements.txt
└── README.md
```

---

## 🚀 Performance Benchmarks (6,048 Unseen Test Samples)

| Metric | Result | Benchmark Target |
| :--- | :--- | :--- |
| **Macro F1-Score** | **100.0%** ($1.0000$) | $\ge 95.0\%$ |
| **Weighted F1-Score** | **100.0%** ($1.0000$) | $\ge 95.0\%$ |
| **Edge Inference Latency** | **0.015 ms** ($15\ \mu\text{s}$) | $< 10.0\text{ ms}$ |
| **Critical Hazard False Negative Rate** | **0.00%** (Zero missed disasters) | $\le 2.0\%$ |

---

## ⚡ Quick Start

### 1. Python Environment Setup & Training
```bash
pip install -r requirements.txt
python src/models/train.py
python src/models/evaluate.py
```

### 2. Embedded Sensor Node Deployment (ESP32 / SX1276)
Copy `edge/purbavas_edge_model.h` and `edge/purbavas_edge_model.c` into your Arduino/PlatformIO firmware project.
Flash [`edge/esp32_purbavas_node.ino`](edge/esp32_purbavas_node.ino) to an ESP32 connected to an SX1276 LoRa transceiver configured for the Indian IN865 band (865.2 MHz).
