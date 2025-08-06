# 📐 Bertrandt GUI - 16:9 Layout Optimierung

## 🎯 16:9 Format Features

### 📱 **Responsive Design**
- **Automatische Bildschirmerkennung**: Passt sich an verschiedene Auflösungen an
- **16:9 Seitenverhältnis**: Optimiert für moderne Bildschirme
- **Minimale Auflösung**: 1280x720 (HD ready)
- **Maximale Auflösung**: 1920x1080 (Full HD)

### 🖥️ **Unterstützte Auflösungen**
- **1920x1080** (Full HD) - Optimal für große Monitore
- **1600x900** (HD+) - Für mittlere Bildschirme
- **1366x768** (HD) - Standard Laptop-Auflösung
- **1280x720** (HD ready) - Minimum für kleine Bildschirme

### 🎨 **Layout-Struktur**

#### **Header (Responsive Höhe)**
- **Logo-Bereich**: Bertrandt Branding mit Slogan
- **Status-Bereich**: Verbindungsstatus und Zeit
- **Höhe**: 4-7% der Bildschirmhöhe

#### **Main Content (75/25 Split)**
- **Left Panel (25%)**: System Status & Controls
  - Mindestbreite: 300px
  - Responsive Breite: 25% des Bildschirms
- **Right Panel (75%)**: Multimedia-Präsentation
  - Hauptcontent-Bereich
  - Navigation unten

#### **Navigation (Responsive Höhe)**
- **10 Seiten-Karten**: Horizontal angeordnet
- **Kartengröße**: Responsive basierend auf Bildschirmbreite
- **Höhe**: 8-12% der Bildschirmhöhe

#### **Footer (Feste Höhe)**
- **Copyright & Branding**: Bertrandt Informationen
- **System-Info**: FPS, Standort
- **Höhe**: ~45px

### ⌨️ **Vollbild-Steuerung**
- **F11**: Vollbild ein/aus
- **ESC**: Vollbild beenden
- **Automatische Zentrierung**: Fenster wird zentriert

### 📏 **Responsive Elemente**

#### **Schriftgrößen**
- **Basis**: Bildschirmgröße ÷ 60
- **Header**: Basis + 12pt
- **Titel**: Basis + 6pt
- **Untertitel**: Basis + 2pt
- **Text**: Basis
- **Navigation**: Basis - 2pt

#### **Abstände & Größen**
- **Padding**: Responsive basierend auf Bildschirmgröße
- **Kartengröße**: Dynamisch skaliert
- **Bildgrößen**: Proportional zur verfügbaren Fläche

### 🎬 **Multimedia-Optimierung**

#### **Bilder**
- **Vollbild**: Bildschirmbreite - 100px
- **Split-Layout**: (Bildschirmbreite - 400px) ÷ 2
- **Proportionale Skalierung**: Seitenverhältnis beibehalten

#### **Text**
- **Scrollbare Bereiche**: Mit Scrollbar
- **Responsive Padding**: 15px Standard
- **Zeilenumbruch**: Automatisch

### 🔧 **Entwickler-Tipps**

#### **Testen verschiedener Auflösungen**
```bash
# Fenster-Größe ändern und testen
# GUI passt sich automatisch an
```

#### **Vollbild für Präsentationen**
- **F11** für Vollbild-Modus
- Ideal für Messestand-Präsentationen
- Keine Ablenkungen durch OS-Elemente

#### **Content-Optimierung**
- **Bilder**: Mindestens 1280px Breite empfohlen
- **Text**: Kurze Absätze für bessere Lesbarkeit
- **Videos**: 16:9 Format bevorzugt

### 📊 **Layout-Verhältnisse**
```
┌─────────────────────────────────────┐
│ Header (4-7% Höhe)                  │
├─────────┬───────────────────────────┤
│ Status  │ Multimedia Content        │
│ Panel   │ (75% Breite)              │
│ (25%)   │                           │
│         │                           │
│         ├───────────────────────────┤
│         │ Navigation (8-12% Höhe)   │
├─────────┴───────────────────────────┤
│ Footer (45px)                       │
└─────────────────────────────────────┘
```

Das 16:9 Layout sorgt für eine professionelle, moderne Darstellung auf allen Bildschirmgrößen! 🚀