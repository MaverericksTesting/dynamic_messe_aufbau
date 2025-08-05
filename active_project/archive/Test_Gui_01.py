#!/usr/bin/env python3
"""
Python Tkinter GUI für ESP32 Serial Communication
Liest Daten vom ESP32 und zeigt entsprechende Screens an
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import queue
import re

class ESP32GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ESP32 Monitor")
        self.root.geometry("1920x1080")
        self.root.configure(bg='#2c3e50')
        
        # Serial-Verbindung
        self.serial_port = None
        self.serial_thread = None
        self.running = False
        
        # Daten-Queue für Thread-sichere Kommunikation
        self.data_queue = queue.Queue()
        
        # Aktuelle Werte
        self.current_signal = 0
        self.client_count = 0
        
        # Signal-Texte definieren
        self.signal_texts = {
            1: 'Start',
            2: 'Beschleunigung',
            3: 'Stabilisierung',
            4: 'Überprüfung',
            5: 'Halbzeit',
            6: 'Motorcheck',
            7: 'Sensoraktivierung',
            8: 'Bremsung',
            9: 'Finalphase',
            10: 'Reset'
        }
        
        self.setup_gui()
        self.setup_serial()
        
    def setup_gui(self):
        """GUI-Elemente erstellen"""
        # Hauptframe
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Oberer Frame für Client-Info
        top_frame = tk.Frame(main_frame, bg='#2c3e50')
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Client-Anzeige (rechts oben)
        self.client_label = tk.Label(
            top_frame,
            text="Clients: 0",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#34495e',
            padx=10,
            pady=5
        )
        self.client_label.pack(side=tk.RIGHT)
        
        # Verbindungsstatus (links oben)
        self.status_label = tk.Label(
            top_frame,
            text="Nicht verbunden",
            font=('Arial', 10),
            fg='#e74c3c',
            bg='#2c3e50'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Mittlerer Frame für Hauptinhalt
        center_frame = tk.Frame(main_frame, bg='#2c3e50')
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # Hauptlabel für Signal-Text
        self.main_label = tk.Label(
            center_frame,
            text="Warte auf Signal...",
            font=('Arial', 24, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50',
            wraplength=600
        )
        self.main_label.pack(expand=True)
        
        # Signal-Nummer Anzeige
        self.signal_label = tk.Label(
            center_frame,
            text="Signal: --",
            font=('Arial', 16),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        self.signal_label.pack(pady=(10, 0))
        
        # Unterer Frame für Steuerung
        bottom_frame = tk.Frame(main_frame, bg='#2c3e50')
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Serial Port Eingabe
        port_frame = tk.Frame(bottom_frame, bg='#2c3e50')
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            port_frame,
            text="Serial Port:",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        self.port_entry = tk.Entry(
            port_frame,
            font=('Arial', 10),
            width=20
        )
        self.port_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.port_entry.insert(0, "/dev/ttyUSB1")  # Standard-Port für Linux
        
        # Buttons
        button_frame = tk.Frame(bottom_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X)
        
        self.connect_button = tk.Button(
            button_frame,
            text="Verbinden",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            command=self.toggle_connection
        )
        self.connect_button.pack(side=tk.LEFT)
        
        tk.Button(
            button_frame,
            text="Beenden",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=5,
            command=self.quit_application
        ).pack(side=tk.RIGHT)
        
    def setup_serial(self):
        """Serial-Kommunikation vorbereiten"""
        # Queue-Verarbeitung starten
        self.root.after(100, self.process_queue)
        
    def toggle_connection(self):
        """Verbindung ein-/ausschalten"""
        if not self.running:
            self.connect_serial()
        else:
            self.disconnect_serial()
            
    def connect_serial(self):
        """Serial-Verbindung herstellen"""
        port = self.port_entry.get().strip()
        if not port:
            messagebox.showerror("Fehler", "Bitte Serial Port eingeben!")
            return
            
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=1
            )
            
            self.running = True
            self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.serial_thread.start()
            
            self.status_label.config(text=f"Verbunden mit {port}", fg='#27ae60')
            self.connect_button.config(text="Trennen", bg='#e74c3c')
            self.port_entry.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Verbindungsfehler", f"Fehler beim Verbinden:\n{str(e)}")
            
    def disconnect_serial(self):
        """Serial-Verbindung trennen"""
        self.running = False
        
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=2)
            
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            
        self.status_label.config(text="Nicht verbunden", fg='#e74c3c')
        self.connect_button.config(text="Verbinden", bg='#27ae60')
        self.port_entry.config(state='normal')
        
    def read_serial(self):
        """Serial-Daten in separatem Thread lesen"""
        while self.running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        self.data_queue.put(line)
                        
            except Exception as e:
                print(f"Serial-Lesefehler: {e}")
                self.data_queue.put("ERROR")
                break
                
            time.sleep(0.01)
            
    def process_queue(self):
        """Queue-Daten verarbeiten (GUI-Thread)"""
        try:
            while True:
                data = self.data_queue.get_nowait()
                self.parse_serial_data(data)
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Queue-Verarbeitungsfehler: {e}")
            
        # Nächste Verarbeitung planen
        self.root.after(50, self.process_queue)
        
    def parse_serial_data(self, data):
        """Serial-Daten analysieren und GUI aktualisieren"""
        if data == "ERROR":
            self.disconnect_serial()
            return
            
        # Client-Anzahl extrahieren (Format: "Clients: X")
        client_match = re.search(r'Clients:\s*(\d+)', data)
        if client_match:
            self.client_count = int(client_match.group(1))
            self.update_client_display()
            
        # Signal-Nummer extrahieren (einzelne Zahl 1-10)
        if data.isdigit():
            signal = int(data)
            if 1 <= signal <= 10:
                self.current_signal = signal
                self.update_main_display()
                
    def update_client_display(self):
        """Client-Anzeige aktualisieren"""
        self.client_label.config(text=f"Clients: {self.client_count}")
        
    def update_main_display(self):
        """Hauptanzeige aktualisieren"""
        if self.current_signal in self.signal_texts:
            text = self.signal_texts[self.current_signal]
            self.main_label.config(text=text)
            self.signal_label.config(text=f"Signal: {self.current_signal}")
            
            # Farbe je nach Signal ändern
            colors = {
                1: '#e74c3c',   # Start - Rot
                2: '#f39c12',   # Beschleunigung - Orange
                3: '#f1c40f',   # Stabilisierung - Gelb
                4: '#27ae60',   # Überprüfung - Grün
                5: '#3498db',   # Halbzeit - Blau
                6: '#9b59b6',   # Motorcheck - Lila
                7: '#1abc9c',   # Sensoraktivierung - Türkis
                8: '#e67e22',   # Bremsung - Orange-Rot
                9: '#34495e',   # Finalphase - Dunkelgrau
                10: '#95a5a6'   # Reset - Grau
            }
            
            color = colors.get(self.current_signal, '#ecf0f1')
            self.main_label.config(fg=color)
            
    def quit_application(self):
        """Anwendung beenden"""
        self.disconnect_serial()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """GUI starten"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_application()

if __name__ == "__main__":
    print("ESP32 Monitor GUI wird gestartet...")
    print("Stelle sicher, dass der ESP32 an den seriellen Port angeschlossen ist.")
    print("Standard-Port: /dev/ttyUSB1 (Linux) oder COM3 (Windows)")
    print("Baudrate: 115200")
    print("=" * 50)
    
    app = ESP32GUI()
    app.run()