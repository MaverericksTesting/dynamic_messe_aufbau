# ESP32 UDP Kommunikationsprojekt

## Übersicht
Dieses Projekt implementiert eine UDP-basierte Kommunikation zwischen zwei Arduino-kompatiblen Mikrocontrollern: einem ESP32 (als Access Point und Empfänger) und einem Arduino GIGA (als Client und Sender).

## Projektstruktur

### 📁 Arduino/
Enthält die Arduino-Sketches für die Mikrocontroller-Programmierung:

#### 🔹 ESP32_UDP_Receiver/
- **Datei**: `ESP32_UDP_Receiver.ino`
- **Funktion**: ESP32 fungiert als WiFi Access Point und UDP-Server
- **Features**:
  - Erstellt ein WiFi-Netzwerk "TestNetz" (Passwort: "12345678")
  - Empfängt UDP-Pakete auf Port 4210
  - Zeigt die Anzahl verbundener Clients an
  - Gibt empfangene Zahlen über die serielle Schnittstelle aus

#### 🔹 GIGA_UDP_Sender/
- **Datei**: `GIGA_UDP_Sender.ino`
- **Funktion**: Arduino GIGA verbindet sich mit ESP32 und sendet UDP-Daten
- **Features**:
  - Verbindet sich mit dem ESP32 WiFi-Netzwerk
  - Sendet kontinuierlich Zahlen (1-10) via UDP
  - Sendeintervall: 2 Sekunden
  - Zeigt Verbindungsstatus und gesendete Daten an

#### 🔹 libraries/
- **Datei**: `readme.txt`
- **Inhalt**: Verweis auf Arduino-Bibliotheken-Installation

### 📁 esp32_project/
Python-Entwicklungsumgebung (derzeit leer, aber vorbereitet):
- **venv/**: Python Virtual Environment
- **bin/**: Ausführbare Dateien

## Funktionsweise

### Kommunikationsablauf:
1. **ESP32** startet als Access Point mit SSID "TestNetz"
2. **Arduino GIGA** verbindet sich mit diesem Netzwerk
3. **GIGA** sendet zyklisch Zahlen (1-10) via UDP an ESP32
4. **ESP32** empfängt die Pakete und gibt sie über Serial aus

### Technische Details:
- **Protokoll**: UDP (User Datagram Protocol)
- **Port**: 4210
- **ESP32 IP**: 192.168.4.1 (Standard SoftAP IP)
- **Datenformat**: Einfache Zahlenwerte als String
- **Übertragungsrate**: Alle 2 Sekunden

## Hardware-Anforderungen
- 1x ESP32 Entwicklungsboard
- 1x Arduino GIGA R1 WiFi
- USB-Kabel für Programmierung und Stromversorgung

## Software-Anforderungen
- Arduino IDE
- WiFi-Bibliotheken für ESP32 und Arduino GIGA
- WiFiUdp-Bibliothek

## Verwendung
1. ESP32 mit `ESP32_UDP_Receiver.ino` programmieren
2. Arduino GIGA mit `GIGA_UDP_Sender.ino` programmieren
3. Beide Geräte mit Strom versorgen
4. Serielle Monitore öffnen, um die Kommunikation zu verfolgen

## Anwendungsbereiche
- IoT-Prototyping
- Drahtlose Sensordatenübertragung
- Mesh-Netzwerk-Grundlagen
- Echtzeit-Kommunikation zwischen Mikrocontrollern