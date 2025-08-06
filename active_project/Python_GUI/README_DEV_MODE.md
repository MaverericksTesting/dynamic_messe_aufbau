# 🔧 Bertrandt GUI - Dev Mode

## Was ist der Dev Mode?

Der **Dev Mode** wird automatisch aktiviert, wenn keine Arduino/ESP32 Hardware angeschlossen ist. Er ermöglicht die vollständige Entwicklung und das Testen der Multimedia-Präsentation ohne Hardware.

## 🚀 Dev Mode Features

### 🎮 Manuelle Steuerung
- **Navigation-Karten klicken**: Direkt auf die kleinen Karten unten klicken
- **Tastatur-Shortcuts**: 
  - `1-9` = Seite 1-9
  - `0` = Seite 10
  - `D` = Auto-Demo starten
  - `S` = Auto-Demo stoppen
  - `C` = Content Manager öffnen

### 🤖 Auto-Demo
- Automatischer Seitenwechsel alle 5 Sekunden
- Zeigt alle 10 Seiten nacheinander
- Simuliert realistische Client-Zahlen
- Perfekt für Präsentationen

### 🛠️ Entwicklung
- Alle Multimedia-Features verfügbar
- Content Manager funktioniert normal
- Live-Reload von Inhalten
- Kein Arduino/ESP32 erforderlich

## 📁 Content hinzufügen (Dev Mode)

1. **GUI starten** (Dev Mode aktiviert sich automatisch)
2. **Content Manager öffnen** (Button oder `C` drücken)
3. **Seiten-Ordner öffnen** (📁 ÖFFNEN Button)
4. **Bilder/Videos hinzufügen**
5. **config.json bearbeiten** für Layout
6. **Content neuladen** (🔄 Button)

## 🎨 Layout-Konfiguration

Bearbeiten Sie die `config.json` in jedem Seiten-Ordner:

```json
{
  "title": "Meine Seite",
  "subtitle": "Untertitel",
  "layout": "image_text",
  "text_content": "Mein Text...",
  "background_image": "mein_bild.jpg",
  "images": ["bild1.jpg", "bild2.png"]
}
```

### Layout-Optionen:
- `"text_only"` - Nur Text
- `"image_text"` - Bild + Text nebeneinander  
- `"video_text"` - Video oben, Text unten
- `"fullscreen_image"` - Vollbild-Bild
- `"fullscreen_video"` - Vollbild-Video

## 🔄 Von Dev Mode zu Hardware

1. **Arduino/ESP32 anschließen**
2. **GUI neu starten**
3. **Hardware wird automatisch erkannt**
4. **Normaler Betrieb aktiviert**

## 🎯 Tipps für Entwicklung

- **Auto-Demo** für Präsentationen verwenden
- **Tastatur-Shortcuts** für schnelles Testen
- **Content Manager** für einfache Verwaltung
- **Live-Reload** für sofortige Änderungen

Der Dev Mode macht die Entwicklung super einfach! 🚀