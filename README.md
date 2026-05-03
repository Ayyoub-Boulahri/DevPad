# DevPad ⌨

> A programmable dev environment launcher — press a button, your whole dev setup opens automatically.

DevPad is an ESP32-powered macro pad that acts as a BLE keyboard. You define profiles (e.g. "Portfolio", "Snake Game") with sequences of terminal commands and keyboard shortcuts. Press a button on the device and it types everything for you.

A companion Python desktop app lets you create, edit, and sync profiles to the device over USB.

---

## Demo

```
[Button Press] → Opens terminal → cd ~/project → npm run dev → Opens browser
```

All of that happens automatically via BLE keyboard emulation.

---

## Hardware

| Component | Details |
|-----------|---------|
| Microcontroller | ESP32 (tested on ESP32-D0WD-V3) |
| Display | 128x64 OLED (SSD1306, I2C) |
| Buttons | 2x tactile push buttons |
| LEDs | 1x Yellow (running indicator), 1x Green (idle) |
| Connection | BLE HID Keyboard + USB Serial |

### Wiring

| Pin | Component |
|-----|-----------|
| GPIO 5 | BTN_NEXT |
| GPIO 18 | BTN_SELECT |
| GPIO 2 | Yellow LED |
| GPIO 4 | Green LED |
| SDA/SCL | OLED Display (I2C) |

---

## Project Structure

```
DevPad/
├── DevPad_UI/            ← Python desktop GUI
└── esp32/
    ├── DevPad.ino            ← Main entry point
    ├── display.cpp / .h      ← OLED screens (menu, running, BLE status)
    ├── buttons.cpp / .h      ← Physical button handling
    ├── storage.cpp / .h      ← SPIFFS profile storage + CRUD
    ├── ble_keyboard.cpp / .h ← BLE HID keyboard output
    ├── menu.cpp / .h         ← On-device navigation with scrolling
    ├── serial_api.cpp / .h   ← PC ↔ ESP32 JSON protocol
    ├── leds.cpp / .h         ← LED indicators
    └── data/
        └── config.json       ← Profile definitions (flashed to SPIFFS)
```

---

## Python App Setup

**Requirements:**
```bash
pip install pyserial
```

**Run:**
```bash
cd DevPad_UI
python3 main.py
```

**Features:**
- View profiles as cards with action previews
- Add / edit / delete profiles and actions
- Add keyboard shortcuts (e.g. `CTRL+ALT+T`) or terminal commands
- Load profiles from ESP32 over USB
- Save profiles to ESP32 over USB

---

## ESP32 Setup

### 1. Install Arduino Libraries

In Arduino IDE, install these libraries:
- `Adafruit SSD1306`
- `Adafruit GFX`
- `ArduinoJson`
- `ESP32 BLE Keyboard` (by T-vK, install from GitHub)

### 2. Flash the Firmware

Open `esp32/DevPad.ino` in Arduino IDE and upload normally.

### 3. Flash the Filesystem (config.json)

The profile config lives on SPIFFS — you need to flash it separately.

**Install mkspiffs (Linux):**
```bash
wget https://github.com/igrr/mkspiffs/releases/download/0.2.3/mkspiffs-0.2.3-arduino-esp32-linux64.tar.gz
tar -xzf mkspiffs-0.2.3-arduino-esp32-linux64.tar.gz
sudo mv mkspiffs-0.2.3-arduino-esp32-linux64/mkspiffs /usr/local/bin/mkspiffs
sudo chmod +x /usr/local/bin/mkspiffs
```

**Flash the data folder:**
```bash
cd esp32/
mkspiffs -c data/ -b 4096 -p 256 -s 0x160000 spiffs.bin
esptool --chip esp32 --port /dev/ttyUSB0 --baud 921600 write-flash 0x290000 spiffs.bin
```

> Make sure Arduino IDE is **closed** before running esptool, or the port will be busy.

**Linux port permissions (run once):**
```bash
sudo usermod -a -G dialout $USER
newgrp dialout
```

---

## Profile Config Format

Profiles are stored in `esp32/data/config.json`:

```json
{
  "profiles": [
    {
      "name": "Portfolio",
      "actions": [
        { "type": "keys", "data": ["CTRL", "ALT", "T"] },
        { "type": "text", "data": "cd ~/Desktop/portfolio" },
        { "type": "text", "data": "npm run dev" }
      ]
    },
    {
      "name": "Snake Game",
      "actions": [
        { "type": "keys", "data": ["CTRL", "ALT", "T"] },
        { "type": "text", "data": "cd ~/Desktop/projects/snake_game" },
        { "type": "text", "data": "source .venv/bin/activate" },
        { "type": "text", "data": "python3 game.py" }
      ]
    }
  ]
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `type` | `"keys"` | Keyboard shortcut |
| `type` | `"text"` | Terminal command (types + Enter) |
| `data` | `["CTRL","ALT","T"]` | Key combo for shortcuts |
| `data` | `"npm run dev"` | Command string for text actions |

---

## Serial Protocol

The Python app communicates with the ESP32 over USB serial (115200 baud) using JSON:

```
PC → ESP32:   {"cmd": "get"}
PC → ESP32:   {"cmd": "save", "data": { "profiles": [...] }}
PC → ESP32:   {"cmd": "delete", "index": 0}

ESP32 → PC:   {"status": "ok", "data": {...}}
ESP32 → PC:   {"status": "error", "message": "..."}
```

---

## How It Works

1. On boot, ESP32 loads `config.json` from SPIFFS into memory
2. OLED shows a scrollable list of profiles
3. **NEXT button** scrolls through profiles (with scroll indicator)
4. **SELECT button** runs the selected profile:
   - Yellow LED turns on
   - ESP32 acts as BLE keyboard and types each action
   - Green LED turns on when done
5. Over USB, the Python app can read/write profiles in real time

---

## Built With

- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [ESP32 BLE Keyboard](https://github.com/T-vK/ESP32-BLE-Keyboard)
- [ArduinoJson](https://arduinojson.org/)
- [Adafruit SSD1306](https://github.com/adafruit/Adafruit_SSD1306)
- Python `tkinter` + `pyserial`

---

## Author

**Ayyoub Boulahri** — built as a personal dev productivity tool.