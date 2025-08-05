#!/usr/bin/env python3
"""
ESP32 Serial Reader für Mini PC
Liest Signale vom ESP32 und startet entsprechende GUI-Screens
"""

import serial
import time
import subprocess
import sys
import threading
import queue

class ESP32SerialReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.running = False
        self.data_queue = queue.Queue()
        
        # Signal-zu-Aktion Mapping
        self.signal_actions = {
            1: self.start_gui_screen_1,
            2: self.start_gui_screen_2,
            3: self.start_gui_screen_3,
            4: self.start_gui_screen_4,
            5: self.start_gui_screen_5,
            6: self.start_gui_screen_6,
            7: self.start_gui_screen_7,
            8: self.start_gui_screen_8,
            9: self.start_gui_screen_9,
            10: self.start_gui_screen_10
        }
        
    def connect(self):
        """Verbindung zum ESP32 herstellen"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # ESP32 Zeit zum Starten geben
            print(f"✅ Verbunden mit ESP32 auf {self.port}")
            return True
        except serial.SerialException as e:
            print(f"❌ Fehler beim Verbinden: {e}")
            return False
    
    def start_reading(self):
        """Startet das kontinuierliche Lesen der seriellen Daten"""
        if not self.serial_connection:
            print("❌ Keine Verbindung zum ESP32")
            return
            
        self.running = True
        read_thread = threading.Thread(target=self._read_serial_data)
        read_thread.daemon = True
        read_thread.start()
        
        # Hauptschleife für die Verarbeitung der Signale
        self._process_signals()
    
    def _read_serial_data(self):
        """Thread-Funktion zum Lesen der seriellen Daten"""
        while self.running:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line.startswith("SIGNAL:"):
                        signal_value = int(line.split(":")[1])
                        self.data_queue.put(signal_value)
                        print(f"📡 Signal empfangen: {signal_value}")
            except Exception as e:
                print(f"❌ Fehler beim Lesen: {e}")
                time.sleep(0.1)
    
    def _process_signals(self):
        """Verarbeitet empfangene Signale und startet entsprechende Aktionen"""
        print("🎯 Warte auf Signale vom ESP32...")
        
        while self.running:
            try:
                # Auf Signal warten (mit Timeout)
                signal = self.data_queue.get(timeout=1)
                
                if signal in self.signal_actions:
                    print(f"🚀 Starte Aktion für Signal {signal}")
                    self.signal_actions[signal]()
                else:
                    print(f"⚠️ Unbekanntes Signal: {signal}")
                    
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                print("\n🛑 Programm beendet")
                self.stop()
                break
    
    def start_gui_screen_1(self):
        """Signal 1: Start-Screen"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=start"])
    
    def start_gui_screen_2(self):
        """Signal 2: Beschleunigung"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=acceleration"])
    
    def start_gui_screen_3(self):
        """Signal 3: Stabilisierung"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=stabilization"])
    
    def start_gui_screen_4(self):
        """Signal 4: Überprüfung"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=check"])
    
    def start_gui_screen_5(self):
        """Signal 5: Halbzeit"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=halftime"])
    
    def start_gui_screen_6(self):
        """Signal 6: Motorcheck"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=motorcheck"])
    
    def start_gui_screen_7(self):
        """Signal 7: Sensoraktivierung"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=sensors"])
    
    def start_gui_screen_8(self):
        """Signal 8: Bremsung"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=braking"])
    
    def start_gui_screen_9(self):
        """Signal 9: Finalphase"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=final"])
    
    def start_gui_screen_10(self):
        """Signal 10: Reset"""
        subprocess.Popen([sys.executable, "Test_Gui_01.py", "--screen=reset"])
    
    def stop(self):
        """Stoppt das Lesen und schließt die Verbindung"""
        self.running = False
        if self.serial_connection:
            self.serial_connection.close()
            print("🔌 Verbindung geschlossen")

def main():
    # ESP32 Serial Reader starten
    reader = ESP32SerialReader()
    
    if reader.connect():
        try:
            reader.start_reading()
        except KeyboardInterrupt:
            reader.stop()
    else:
        print("❌ Konnte keine Verbindung zum ESP32 herstellen")
        print("💡 Überprüfen Sie:")
        print("   - ESP32 ist angeschlossen")
        print("   - Richtiger Port (/dev/ttyUSB0, /dev/ttyACM0, etc.)")
        print("   - ESP32 läuft und sendet Daten")

if __name__ == "__main__":
    main()