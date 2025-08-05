#!/usr/bin/env python3
"""
🔧 Bertrandt ESP32 CLI Monitor & Flash Tool
Kommandozeilen-Version für Headless-Systeme
"""

import serial
import time
import subprocess
import sys
import argparse
import threading
from datetime import datetime

class BertrandtCLI:
    def __init__(self, esp32_port="/dev/ttyUSB0"):
        self.esp32_port = esp32_port
        self.serial_connection = None
        self.running = False
        self.signal_count = 0
        
        # Signal-Mapping
        self.signal_names = {
            1: "System Start 🚀",
            2: "Beschleunigung ⚡",
            3: "Stabilisierung ⚖️",
            4: "Überprüfung 🔍",
            5: "Halbzeit ⏱️",
            6: "Motorcheck 🔧",
            7: "Sensoraktivierung 📡",
            8: "Bremsung 🛑",
            9: "Finalphase 🏁",
            10: "System Reset 🔄"
        }
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[0;34m",
            "SUCCESS": "\033[0;32m", 
            "WARNING": "\033[1;33m",
            "ERROR": "\033[0;31m"
        }
        color = colors.get(level, "\033[0m")
        print(f"{color}[{timestamp}] {message}\033[0m")
    
    def check_arduino_cli(self):
        """Prüft ob Arduino CLI verfügbar ist"""
        try:
            result = subprocess.run(["arduino-cli", "version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Arduino CLI gefunden", "SUCCESS")
                return True
        except FileNotFoundError:
            pass
        
        self.log("Arduino CLI nicht gefunden - installiere...", "WARNING")
        return self.install_arduino_cli()
    
    def install_arduino_cli(self):
        """Installiert Arduino CLI"""
        try:
            self.log("Lade Arduino CLI herunter...", "INFO")
            subprocess.run([
                "curl", "-fsSL", 
                "https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh"
            ], stdout=subprocess.PIPE, check=True)
            
            subprocess.run(["sh", "-c", 
                "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"],
                check=True)
            
            # Cores installieren
            self.log("Installiere Arduino Cores...", "INFO")
            subprocess.run(["arduino-cli", "core", "update-index"], check=True)
            subprocess.run(["arduino-cli", "core", "install", "esp32:esp32"], check=True)
            subprocess.run(["arduino-cli", "core", "install", "arduino:mbed_giga"], check=True)
            
            self.log("Arduino CLI erfolgreich installiert", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Fehler bei Arduino CLI Installation: {e}", "ERROR")
            return False
    
    def scan_ports(self):
        """Scannt verfügbare Ports"""
        import glob
        ports = []
        
        # Linux/Mac Ports
        for pattern in ["/dev/ttyUSB*", "/dev/ttyACM*", "/dev/cu.usbserial*", "/dev/cu.usbmodem*"]:
            ports.extend(glob.glob(pattern))
        
        if ports:
            self.log(f"Gefundene Ports: {', '.join(ports)}", "SUCCESS")
        else:
            self.log("Keine Ports gefunden", "WARNING")
        
        return ports
    
    def flash_esp32(self, port="/dev/ttyUSB0"):
        """Flasht ESP32"""
        self.log("🔥 Flashe ESP32...", "INFO")
        self.log("⚠️  WICHTIG: Boot-Button am ESP32 gedrückt halten wenn 'Connecting...' erscheint!", "WARNING")
        
        try:
            # Kompilieren
            self.log("Kompiliere ESP32 Code...", "INFO")
            result = subprocess.run([
                "arduino-cli", "compile", 
                "--fqbn", "esp32:esp32:esp32",
                "Arduino/ESP32_UDP_Receiver/"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"Kompilier-Fehler: {result.stderr}", "ERROR")
                return False
            
            # Upload
            self.log(f"Lade auf Port {port} hoch...", "INFO")
            self.log("🔴 JETZT Boot-Button drücken und halten!", "WARNING")
            
            result = subprocess.run([
                "arduino-cli", "upload",
                "-p", port,
                "--fqbn", "esp32:esp32:esp32",
                "Arduino/ESP32_UDP_Receiver/"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("ESP32 erfolgreich geflasht! 🎉", "SUCCESS")
                return True
            else:
                self.log(f"Upload-Fehler: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler beim ESP32 Flash: {e}", "ERROR")
            return False
    
    def flash_giga(self, port="/dev/ttyACM0"):
        """Flasht Arduino GIGA"""
        self.log("🔥 Flashe Arduino GIGA...", "INFO")
        
        try:
            # Kompilieren
            self.log("Kompiliere GIGA Code...", "INFO")
            result = subprocess.run([
                "arduino-cli", "compile",
                "--fqbn", "arduino:mbed_giga:giga", 
                "Arduino/GIGA_UDP_Sender/"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log(f"Kompilier-Fehler: {result.stderr}", "ERROR")
                return False
            
            # Upload
            self.log(f"Lade auf Port {port} hoch...", "INFO")
            result = subprocess.run([
                "arduino-cli", "upload",
                "-p", port,
                "--fqbn", "arduino:mbed_giga:giga",
                "Arduino/GIGA_UDP_Sender/"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Arduino GIGA erfolgreich geflasht! 🎉", "SUCCESS")
                return True
            else:
                self.log(f"Upload-Fehler: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Fehler beim GIGA Flash: {e}", "ERROR")
            return False
    
    def connect_serial(self):
        """Verbindet mit ESP32 Serial"""
        try:
            self.serial_connection = serial.Serial(
                self.esp32_port, 
                115200, 
                timeout=1
            )
            self.log(f"Verbunden mit {self.esp32_port}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Serial-Verbindung fehlgeschlagen: {e}", "ERROR")
            return False
    
    def monitor_signals(self):
        """Überwacht eingehende Signale"""
        self.log("🔍 Starte Signal-Monitoring...", "INFO")
        self.log("Drücke Ctrl+C zum Beenden", "INFO")
        
        if not self.connect_serial():
            return
        
        self.running = True
        
        try:
            while self.running:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line.startswith("SIGNAL:"):
                        try:
                            signal_num = int(line.split(":")[1])
                            if 1 <= signal_num <= 10:
                                self.signal_count += 1
                                signal_name = self.signal_names.get(signal_num, f"Signal {signal_num}")
                                self.log(f"📡 Signal {signal_num}: {signal_name} (#{self.signal_count})", "SUCCESS")
                            else:
                                self.log(f"⚠️  Unbekanntes Signal: {signal_num}", "WARNING")
                        except ValueError:
                            self.log(f"⚠️  Ungültiges Signal-Format: {line}", "WARNING")
                    else:
                        self.log(f"📝 ESP32: {line}", "INFO")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.log("Monitoring beendet", "INFO")
        finally:
            if self.serial_connection:
                self.serial_connection.close()
            self.running = False

def main():
    parser = argparse.ArgumentParser(description="Bertrandt ESP32 CLI Tool")
    parser.add_argument("--esp32-port", default="/dev/ttyUSB0", help="ESP32 Serial Port")
    parser.add_argument("--giga-port", default="/dev/ttyACM0", help="Arduino GIGA Port")
    parser.add_argument("--action", choices=["monitor", "flash-esp32", "flash-giga", "flash-both", "scan"], 
                       default="monitor", help="Aktion ausführen")
    
    args = parser.parse_args()
    
    cli = BertrandtCLI(args.esp32_port)
    
    print("🚀 Bertrandt ESP32 CLI Tool")
    print("=" * 40)
    
    if args.action == "scan":
        cli.scan_ports()
    
    elif args.action == "flash-esp32":
        if cli.check_arduino_cli():
            cli.flash_esp32(args.esp32_port)
    
    elif args.action == "flash-giga":
        if cli.check_arduino_cli():
            cli.flash_giga(args.giga_port)
    
    elif args.action == "flash-both":
        if cli.check_arduino_cli():
            cli.log("Flashe beide Geräte sequenziell...", "INFO")
            if cli.flash_giga(args.giga_port):
                time.sleep(2)
                cli.flash_esp32(args.esp32_port)
    
    elif args.action == "monitor":
        cli.monitor_signals()

if __name__ == "__main__":
    main()