# 🚀 Bertrandt ESP32 GUI-Steuerungsprojekt

## 📋 Systemübersicht
**Signalfluss:** Arduino GIGA → ESP32 → Mini PC → Bertrandt GUI

## 📁 Projektstruktur (Optimiert)

### 🔹 Hauptordner (Wichtige Dateien)
- **start_system.sh**: 🆕 Optimierter Starter mit Flash-Integration
- **Arduino/**: Arduino Sketches für ESP32 und GIGA
- **Python_GUI/Bertrandt_GUI.py**: Professionelle GUI mit integriertem Flash-Tool

### 🔹 Arduino/
- **ESP32_UDP_Receiver/**: ESP32 empfängt UDP-Signale und leitet sie an Mini PC weiter
- **GIGA_UDP_Sender/**: Arduino GIGA sendet Steuersignale (1-10) via UDP

### 🔹 Archiv & Tools
- **archive/**: Alte/nicht verwendete Dateien (Test_Gui_01.py, unused_scripts/)
- **tools/**: Erweiterte Tools (auto_start_system.sh)

## ⚡ Einfacher Start

### 🎯 Ein-Klick-Start (Empfohlen)
```bash
./start_system.sh
```

**Das Script macht automatisch:**
- ✅ Prüft Python3 und Abhängigkeiten
- ✅ Erkennt verfügbare Arduino-Ports automatisch
- ✅ Startet Bertrandt GUI mit Flash-Tool
- ✅ Zeigt alle verfügbaren Features an

### 🔧 Erweiterte Installation (Optional)
```bash
./tools/auto_start_system.sh
```

**Für vollautomatisches Setup:**
- ✅ Installiert Arduino CLI automatisch
- ✅ Flasht beide Geräte sofort
- ✅ Startet komplettes System

### 🔧 Manuelle Installation
```bash
# 1. Arduino CLI installieren
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# 2. Cores installieren
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli core install arduino:mbed_giga

# 3. Python-Abhängigkeiten
pip3 install pyserial

# 4. Geräte flashen
arduino-cli compile --fqbn arduino:mbed_giga:giga Arduino/GIGA_UDP_Sender/
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:mbed_giga:giga Arduino/GIGA_UDP_Sender/

arduino-cli compile --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/

# 5. GUI starten
cd Python_GUI
python3 Bertrandt_GUI.py --esp32-port=/dev/ttyUSB0
```

## 🎨 Bertrandt GUI Features

### 🔹 Corporate Design
- **Bertrandt Farben**: Dunkelblau (#003366), Blau (#0066CC), Orange (#FF6600)
- **Professional Layout**: Header, Status Panel, Signal Monitor, Footer
- **Responsive Design**: Passt sich verschiedenen Bildschirmgrößen an

### 🔹 Neue Flash-Funktionen
- **📱 ESP32 Flash-Tool**: Direktes Flashen mit Boot-Button Erinnerung
- **🔧 Arduino GIGA Flash-Tool**: Automatisches Flashen ohne Button
- **🚀 Beide Geräte flashen**: Sequenzielles Flashen beider Geräte
- **🔍 Port-Scanner**: Automatische Erkennung verfügbarer Ports
- **⚙️ Arduino CLI Integration**: Automatische Installation falls nötig

### 🔹 Monitoring-Funktionen
- **Real-time Signal Monitoring**: Live-Anzeige der ESP32-Signale
- **Signal Historie**: Aufzeichnung der letzten 100 Signale
- **Client-Überwachung**: Anzahl verbundener WiFi-Clients
- **Verbindungsstatus**: Live-Status der ESP32-Verbindung
- **Signal-Karten**: Visuelle Darstellung aller 10 Signale
- **Einstellungen**: Port-Konfiguration und Systemeinstellungen

### 🔹 Signal-Mapping
| Signal | Name | Icon | Beschreibung |
|--------|------|------|--------------|
| 1 | System Start | 🚀 | Startet das System |
| 2 | Beschleunigung | ⚡ | Beschleunigungsphase |
| 3 | Stabilisierung | ⚖️ | Stabilisierungsphase |
| 4 | Überprüfung | 🔍 | Systemcheck |
| 5 | Halbzeit | ⏱️ | Halbzeit-Pause |
| 6 | Motorcheck | 🔧 | Motor-Diagnose |
| 7 | Sensoraktivierung | 📡 | Sensor-Aktivierung |
| 8 | Bremsung | 🛑 | Bremsphase |
| 9 | Finalphase | 🏁 | Endphase |
| 10 | System Reset | 🔄 | System-Reset |

## 🛠 Technische Details

### Kommunikation
- **GIGA → ESP32**: UDP über WiFi (Port 4210)
- **ESP32 → Mini PC**: Serial USB (115200 Baud)
- **Format**: `SIGNAL:X` (X = 1-10)

### WiFi-Einstellungen
- **SSID**: TestNetz
- **Passwort**: 12345678
- **ESP32 IP**: 192.168.4.1

### Hardware-Anforderungen
- Arduino GIGA R1 WiFi
- ESP32 Entwicklungsboard
- Mini PC mit Ubuntu/Linux
- 2x USB-Kabel

## 🔍 Troubleshooting

### Arduino nicht gefunden
```bash
# Verfügbare Geräte anzeigen
arduino-cli board list

# USB-Berechtigung setzen
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*
```

### ESP32 Flash-Fehler
```bash
# ESP32 in Download-Modus versetzen
# Boot-Button gedrückt halten beim Einschalten

# Port manuell angeben
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/
```

### GUI startet nicht
```bash
# Abhängigkeiten prüfen
python3 -c "import tkinter, serial"

# Port anpassen
python3 Bertrandt_GUI.py --esp32-port=/dev/ttyACM1
```

## 📊 Monitoring & Debugging

### Serial Monitor
```bash
# ESP32 Monitor
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200

# Arduino GIGA Monitor  
arduino-cli monitor -p /dev/ttyACM0 -c baudrate=115200
```

### Log-Ausgabe
Das System gibt detaillierte Logs aus:
- 🔧 Setup-Informationen
- ✅ Erfolgreiche Aktionen
- ⚠️ Warnungen
- ❌ Fehler

## 📞 Support

Bei Problemen:
1. **Auto-Start-Script verwenden**: `./auto_start_system.sh`
2. **Logs prüfen**: Ausgabe des Scripts beachten
3. **Hardware prüfen**: USB-Verbindungen und Stromversorgung
4. **Ports prüfen**: `ls /dev/tty*` für verfügbare Ports