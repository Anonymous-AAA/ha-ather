Here is the updated README with emojis added for better readability, along with the requested warnings and disclaimers placed prominently at the top.

---

# 🛵 Ather Scooter Integration for Home Assistant

A custom Home Assistant integration to monitor and track your Ather electric scooter(s) in real-time. This integration automatically discovers all scooters associated with your account, groups their sensors cleanly into individual device panels, and maintains a persistent, live connection.

> ⚠️ **IMPORTANT DISCLAIMER** > This integration is built using **reverse-engineered, unofficial APIs**. It is provided as-is and could break or stop working unexpectedly at any time if Ather updates their internal systems or API structures.
> *This project is a community effort and is **strictly not affiliated with, endorsed by, or connected to Ather Energy** in any way.*

---

## ✨ Features

* 🛵 **Multi-Scooter Support:** Automatically registers every vehicle linked to your account as a distinct device.
* ⚡ **Real-Time Streaming:** Uses a persistent WebSocket connection to ensure your data is always live.
* 📊 **Comprehensive Sensor Suite:**
* 🔋 Battery State of Charge (%)
* 🛣️ Odometer (km)
* 🎯 Current Range & Mode-Specific Ranges (Smart Eco, Eco, Ride, Sport, Warp)
* 🚦 Active Riding Mode & Vehicle State
* 📍 Device Tracker
* 🕵️ Incognito Status



---

## 🛠️ Installation

### 📦 Option 1: Via HACS (Recommended)

1. Ensure **HACS** is installed and working in your Home Assistant instance.
2. Go to **HACS** > **Integrations**.
3. Click the three dots in the top-right corner and select **Custom repositories**.
4. Paste the URL of this repository into the **Repository** field.
5. Select **Integration** as the Category and click **Add**.
6. Search for **Ather Scooter** in HACS and click **Download**.
7. Restart Home Assistant.

### 📂 Option 2: Manual Installation

1. Download the latest release or clone this repository.
2. Copy the `ather` directory from `custom_components/` into your Home Assistant `/config/custom_components/` directory.
3. The file structure should look exactly like this:

```text
config/
└── custom_components/
    └── ather/
        ├── __init__.py
        ├── api.py
        ├── binary_sensor.py
        ├── config_flow.py
        ├── const.py
        ├── device_tracker.py
        ├── manifest.json
        └── sensor.py

```

4. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **+ Add Integration** in the bottom right corner.
3. Search for **Ather Scooter** and select it.
4. Enter your account credentials (Email and OTP verification) when prompted.
5. Your scooter(s) will automatically populate under a unified device registry matching your official vehicle registration number.

---

## 📱 Dashboard Configuration

Entities are dynamically named using your vehicle's registration number to ensure unique routing and a clean dashboard layout.

---

## 🏗️ Development & Code Architecture

This integration utilizes a centralized Data Update Coordinator to manage downstream platforms efficiently:

* 🧠 **`__init__.py`**: Discovers hardware properties (Model/Registration) and coordinates data across all sensor platforms using recursive dictionary deep-merging.
* 🌐 **`api.py`**: Manages the persistent network connection layer, token authentication, `Set-Cookie` persistence headers, and regular WebSocket heartbeat intervals.
* 🎛️ **`sensor.py` / `binary_sensor.py` / `device_tracker.py**`: Maps incoming telemetry keys directly to individual frontend device state nodes.