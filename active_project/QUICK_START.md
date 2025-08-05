# 🚀 Bertrandt ESP32 System - Schnellstart

## ⚡ Sofort loslegen

### 1️⃣ System starten
```bash
./start_system.sh
```

### 2️⃣ In der GUI
1. **Geräte anschließen**: ESP32 und Arduino GIGA per USB
2. **Port scannen**: 🔍 Button klicken
3. **Gerät auswählen**: ESP32 oder GIGA Radio-Button
4. **Flashen**: 
   - **ESP32**: Boot-Button bereithalten! 
   - **GIGA**: Automatisch
   - **Beide**: Sequenziell flashen

### 3️⃣ Monitoring
- Live-Signale von 1-10 werden angezeigt
- Signal-Karten leuchten bei Aktivierung
- Client-Anzahl wird überwacht

## 🎯 Wichtige Hinweise

### ESP32 Flashen
- **Boot-Button drücken** wenn "Connecting..." erscheint
- Gelbe Warnung in GUI beachten

### Arduino GIGA Flashen  
- Läuft automatisch
- Kein Button nötig
- Grüner Hinweis in GUI

### Beide Geräte flashen
1. Zuerst wird GIGA geflasht (automatisch)
2. Dann ESP32 (Boot-Button bereithalten!)

## 📁 Ordnerstruktur
```
📦 Bertrandt-ESP32-System/
├── 🚀 start_system.sh          # Hauptstarter
├── 📁 Arduino/                 # Arduino Sketches
├── 📁 Python_GUI/             # GUI mit Flash-Tool
├── 📁 archive/                # Alte Dateien
└── 📁 tools/                  # Erweiterte Tools
```

## 🆘 Probleme?
- **Keine Ports**: USB-Kabel und Treiber prüfen
- **Arduino CLI fehlt**: Wird automatisch in GUI installiert
- **ESP32 Flash-Fehler**: Boot-Button zur richtigen Zeit drücken
- **Permission denied**: `sudo chmod +x start_system.sh`