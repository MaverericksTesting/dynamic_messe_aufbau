#!/usr/bin/env python3
"""
Bertrandt ESP32 Monitor GUI
Professional GUI im Bertrandt Corporate Design
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import threading
import time
import queue
import sys
import argparse
import subprocess
import os
import glob

class BertrandtGUI:
    def __init__(self, esp32_port=None):
        self.root = tk.Tk()
        self.root.title("Bertrandt ESP32 Monitor")
        self.root.geometry("1920x1080")
        
        # Bertrandt Farben
        self.colors = {
            'primary': '#003366',      # Bertrandt Dunkelblau
            'secondary': '#0066CC',    # Bertrandt Blau
            'accent': '#FF6600',       # Bertrandt Orange
            'success': '#00AA44',      # Grün
            'warning': '#FFAA00',      # Gelb
            'error': '#CC0000',        # Rot
            'background': '#F5F5F5',   # Hellgrau
            'surface': '#FFFFFF',      # Weiß
            'text': '#333333',         # Dunkelgrau
            'text_light': '#666666'    # Mittelgrau
        }
        
        self.root.configure(bg=self.colors['background'])
        
        # Serial-Verbindung
        self.esp32_port = esp32_port or '/dev/ttyUSB0'
        self.serial_connection = None
        self.serial_thread = None
        self.running = False
        
        # Daten-Queue
        self.data_queue = queue.Queue()
        
        # Aktuelle Werte
        self.current_signal = 0
        self.client_count = 0
        self.signal_history = []
        
        # Signal-Definitionen
        self.signal_definitions = {
            1: {'name': 'System Start', 'color': self.colors['success'], 'icon': '🚀'},
            2: {'name': 'Beschleunigung', 'color': self.colors['accent'], 'icon': '⚡'},
            3: {'name': 'Stabilisierung', 'color': self.colors['secondary'], 'icon': '⚖️'},
            4: {'name': 'Überprüfung', 'color': self.colors['warning'], 'icon': '🔍'},
            5: {'name': 'Halbzeit', 'color': self.colors['primary'], 'icon': '⏱️'},
            6: {'name': 'Motorcheck', 'color': self.colors['accent'], 'icon': '🔧'},
            7: {'name': 'Sensoraktivierung', 'color': self.colors['secondary'], 'icon': '📡'},
            8: {'name': 'Bremsung', 'color': self.colors['error'], 'icon': '🛑'},
            9: {'name': 'Finalphase', 'color': self.colors['success'], 'icon': '🏁'},
            10: {'name': 'System Reset', 'color': self.colors['primary'], 'icon': '🔄'}
        }
        
        self.setup_styles()
        self.setup_gui()
        self.setup_serial()
        
    def setup_styles(self):
        """Bertrandt Corporate Design Styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Header Style
        self.style.configure('Header.TFrame', 
                           background=self.colors['primary'])
        
        # Card Style
        self.style.configure('Card.TFrame',
                           background=self.colors['surface'],
                           relief='raised',
                           borderwidth=2)
        
        # Button Styles
        self.style.configure('Primary.TButton',
                           background=self.colors['primary'],
                           foreground='white',
                           font=('Arial', 12, 'bold'))
        
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground='white',
                           font=('Arial', 12, 'bold'))
        
        self.style.configure('Warning.TButton',
                           background=self.colors['warning'],
                           foreground='white',
                           font=('Arial', 12, 'bold'))
        
    def setup_gui(self):
        """Hauptgui-Layout im Bertrandt Design"""
        
        # Header
        self.create_header()
        
        # Main Content Area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Status & Controls
        left_panel = ttk.Frame(main_frame, style='Card.TFrame')
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Right Panel - Signal Display
        right_panel = ttk.Frame(main_frame, style='Card.TFrame')
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.create_status_panel(left_panel)
        self.create_signal_display(right_panel)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Bertrandt Header mit Logo-Bereich"""
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Logo-Bereich (links)
        logo_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        logo_frame.pack(side='left', padx=20, pady=15)
        
        logo_label = tk.Label(logo_frame, 
                             text="BERTRANDT",
                             font=('Arial', 24, 'bold'),
                             fg='white',
                             bg=self.colors['primary'])
        logo_label.pack()
        
        subtitle_label = tk.Label(logo_frame,
                                 text="ESP32 Monitor System",
                                 font=('Arial', 12),
                                 fg=self.colors['accent'],
                                 bg=self.colors['primary'])
        subtitle_label.pack()
        
        # Status-Bereich (rechts)
        status_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        status_frame.pack(side='right', padx=20, pady=15)
        
        self.connection_status = tk.Label(status_frame,
                                         text="🔴 Nicht verbunden",
                                         font=('Arial', 14, 'bold'),
                                         fg='white',
                                         bg=self.colors['primary'])
        self.connection_status.pack()
        
        self.time_label = tk.Label(status_frame,
                                  text="",
                                  font=('Arial', 12),
                                  fg=self.colors['accent'],
                                  bg=self.colors['primary'])
        self.time_label.pack()
        
        # Zeit aktualisieren
        self.update_time()
        
    def create_status_panel(self, parent):
        """Status und Control Panel"""
        # Titel
        title_label = tk.Label(parent,
                              text="System Status",
                              font=('Arial', 18, 'bold'),
                              fg=self.colors['primary'],
                              bg=self.colors['surface'])
        title_label.pack(pady=20)
        
        # Verbindungsstatus
        conn_frame = tk.Frame(parent, bg=self.colors['surface'])
        conn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(conn_frame,
                text="ESP32 Verbindung:",
                font=('Arial', 12, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor='w')
        
        self.esp32_status = tk.Label(conn_frame,
                                    text=f"Port: {self.esp32_port}",
                                    font=('Arial', 11),
                                    fg=self.colors['text_light'],
                                    bg=self.colors['surface'])
        self.esp32_status.pack(anchor='w')
        
        # Client Count
        client_frame = tk.Frame(parent, bg=self.colors['surface'])
        client_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(client_frame,
                text="Verbundene Clients:",
                font=('Arial', 12, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor='w')
        
        self.client_label = tk.Label(client_frame,
                                    text="0",
                                    font=('Arial', 24, 'bold'),
                                    fg=self.colors['secondary'],
                                    bg=self.colors['surface'])
        self.client_label.pack()
        
        # Aktuelles Signal
        signal_frame = tk.Frame(parent, bg=self.colors['surface'])
        signal_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(signal_frame,
                text="Aktuelles Signal:",
                font=('Arial', 12, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor='w')
        
        self.current_signal_display = tk.Frame(signal_frame, 
                                              bg=self.colors['primary'],
                                              relief='raised',
                                              borderwidth=3)
        self.current_signal_display.pack(fill='x', pady=10)
        
        self.signal_number = tk.Label(self.current_signal_display,
                                     text="--",
                                     font=('Arial', 36, 'bold'),
                                     fg='white',
                                     bg=self.colors['primary'])
        self.signal_number.pack(pady=10)
        
        self.signal_name = tk.Label(self.current_signal_display,
                                   text="Warte auf Signal...",
                                   font=('Arial', 14),
                                   fg=self.colors['accent'],
                                   bg=self.colors['primary'])
        self.signal_name.pack(pady=(0, 10))
        
        # Flash Sektion für beide Geräte
        self.create_flash_section(parent)
        
        # Control Buttons
        btn_frame = tk.Frame(parent, bg=self.colors['surface'])
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame,
                  text="🔄 Verbindung neu starten",
                  style='Primary.TButton',
                  command=self.restart_connection).pack(fill='x', pady=5)
        
        ttk.Button(btn_frame,
                  text="📊 Signal Historie",
                  style='Success.TButton',
                  command=self.show_history).pack(fill='x', pady=5)
        
        ttk.Button(btn_frame,
                  text="⚙️ Einstellungen",
                  style='Warning.TButton',
                  command=self.show_settings).pack(fill='x', pady=5)
                  
    def create_flash_section(self, parent):
        """Arduino Flash-Sektion für ESP32 und GIGA erstellen"""
        flash_frame = tk.Frame(parent, bg=self.colors['surface'])
        flash_frame.pack(fill='x', padx=20, pady=20)
        
        # Titel
        tk.Label(flash_frame,
                text="Arduino Flash-Tool:",
                font=('Arial', 12, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor='w')
        
        # Flash Status
        self.flash_status = tk.Label(flash_frame,
                                    text="Bereit zum Flashen",
                                    font=('Arial', 10),
                                    fg=self.colors['text_light'],
                                    bg=self.colors['surface'])
        self.flash_status.pack(anchor='w', pady=(5, 10))
        
        # Geräte-Auswahl Tabs
        device_frame = tk.Frame(flash_frame, bg=self.colors['surface'])
        device_frame.pack(fill='x', pady=5)
        
        self.device_var = tk.StringVar(value="ESP32")
        
        tk.Radiobutton(device_frame,
                      text="📱 ESP32",
                      variable=self.device_var,
                      value="ESP32",
                      font=('Arial', 10),
                      bg=self.colors['surface'],
                      command=self.on_device_change).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(device_frame,
                      text="🔧 Arduino GIGA",
                      variable=self.device_var,
                      value="GIGA",
                      font=('Arial', 10),
                      bg=self.colors['surface'],
                      command=self.on_device_change).pack(side='left')
        
        # Port Auswahl
        port_frame = tk.Frame(flash_frame, bg=self.colors['surface'])
        port_frame.pack(fill='x', pady=5)
        
        tk.Label(port_frame,
                text="Port:",
                font=('Arial', 10),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side='left')
        
        self.flash_port_var = tk.StringVar()
        self.flash_port_combo = ttk.Combobox(port_frame, 
                                           textvariable=self.flash_port_var,
                                           width=15,
                                           state='readonly')
        self.flash_port_combo.pack(side='left', padx=(5, 0))
        
        ttk.Button(port_frame,
                  text="🔍",
                  width=3,
                  command=self.scan_ports).pack(side='left', padx=(5, 0))
        
        # Flash Buttons
        flash_btn_frame = tk.Frame(flash_frame, bg=self.colors['surface'])
        flash_btn_frame.pack(fill='x', pady=10)
        
        self.flash_btn = ttk.Button(flash_btn_frame,
                                   text="📱 ESP32 Flashen",
                                   style='Primary.TButton',
                                   command=self.flash_device)
        self.flash_btn.pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="📁 Sketch auswählen",
                  style='Success.TButton',
                  command=self.select_sketch).pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="🚀 Beide Geräte flashen",
                  style='Warning.TButton',
                  command=self.flash_both_devices).pack(fill='x', pady=2)
        
        # Boot Button Hinweis
        self.hint_frame = tk.Frame(flash_frame, 
                             bg=self.colors['warning'],
                             relief='raised',
                             borderwidth=2)
        self.hint_frame.pack(fill='x', pady=10)
        
        self.hint_title = tk.Label(self.hint_frame,
                text="💡 ESP32 WICHTIG:",
                font=('Arial', 10, 'bold'),
                fg='white',
                bg=self.colors['warning'])
        self.hint_title.pack(pady=(5, 0))
        
        self.hint_text = tk.Label(self.hint_frame,
                text="Boot-Button drücken wenn\n'Connecting...' erscheint!",
                font=('Arial', 9),
                fg='white',
                bg=self.colors['warning'],
                justify='center')
        self.hint_text.pack(pady=(0, 5))
        
        # Sketch Pfade
        self.esp32_sketch_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                             "Arduino", "ESP32_UDP_Receiver")
        self.giga_sketch_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                            "Arduino", "GIGA_UDP_Sender")
        self.current_sketch_path = self.esp32_sketch_path
        
        # Ports beim Start scannen
        self.scan_ports()
        
    def create_signal_display(self, parent):
        """Hauptanzeige für Signale"""
        # Titel
        title_label = tk.Label(parent,
                              text="Signal Monitor",
                              font=('Arial', 18, 'bold'),
                              fg=self.colors['primary'],
                              bg=self.colors['surface'])
        title_label.pack(pady=20)
        
        # Signal Grid
        self.signal_grid = tk.Frame(parent, bg=self.colors['surface'])
        self.signal_grid.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Signal Cards erstellen
        self.signal_cards = {}
        for i, (signal_id, signal_info) in enumerate(self.signal_definitions.items()):
            row = i // 5
            col = i % 5
            
            card = self.create_signal_card(self.signal_grid, signal_id, signal_info)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            self.signal_cards[signal_id] = card
        
        # Grid konfigurieren
        for i in range(5):
            self.signal_grid.columnconfigure(i, weight=1)
        for i in range(2):
            self.signal_grid.rowconfigure(i, weight=1)
            
    def create_signal_card(self, parent, signal_id, signal_info):
        """Einzelne Signal-Karte erstellen"""
        card = tk.Frame(parent,
                       bg=self.colors['surface'],
                       relief='raised',
                       borderwidth=2,
                       width=200,
                       height=150)
        
        # Icon
        icon_label = tk.Label(card,
                             text=signal_info['icon'],
                             font=('Arial', 32),
                             bg=self.colors['surface'])
        icon_label.pack(pady=10)
        
        # Signal Nummer
        number_label = tk.Label(card,
                               text=f"Signal {signal_id}",
                               font=('Arial', 14, 'bold'),
                               fg=signal_info['color'],
                               bg=self.colors['surface'])
        number_label.pack()
        
        # Signal Name
        name_label = tk.Label(card,
                             text=signal_info['name'],
                             font=('Arial', 10),
                             fg=self.colors['text'],
                             bg=self.colors['surface'],
                             wraplength=150)
        name_label.pack(pady=5)
        
        # Status Indikator
        status_indicator = tk.Frame(card,
                                   bg=self.colors['background'],
                                   height=5)
        status_indicator.pack(fill='x', side='bottom')
        
        # Referenzen speichern
        card.icon_label = icon_label
        card.number_label = number_label
        card.name_label = name_label
        card.status_indicator = status_indicator
        card.signal_info = signal_info
        
        return card
        
    def create_footer(self):
        """Footer mit Systeminformationen"""
        footer_frame = tk.Frame(self.root, bg=self.colors['primary'], height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_text = tk.Label(footer_frame,
                              text="© 2024 Bertrandt AG | ESP32 Monitor System v1.0",
                              font=('Arial', 10),
                              fg='white',
                              bg=self.colors['primary'])
        footer_text.pack(side='left', padx=20, pady=10)
        
        self.fps_label = tk.Label(footer_frame,
                                 text="FPS: --",
                                 font=('Arial', 10),
                                 fg=self.colors['accent'],
                                 bg=self.colors['primary'])
        self.fps_label.pack(side='right', padx=20, pady=10)
        
    def setup_serial(self):
        """Serial-Verbindung einrichten"""
        try:
            self.serial_connection = serial.Serial(self.esp32_port, 115200, timeout=1)
            time.sleep(2)
            self.connection_status.config(text="🟢 Verbunden", fg=self.colors['success'])
            self.start_serial_reading()
        except Exception as e:
            self.connection_status.config(text="🔴 Fehler", fg=self.colors['error'])
            messagebox.showerror("Verbindungsfehler", f"Kann nicht mit ESP32 verbinden:\n{e}")
            
    def start_serial_reading(self):
        """Serial-Daten lesen starten"""
        self.running = True
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        # GUI-Update-Loop starten
        self.process_serial_data()
        
    def read_serial_data(self):
        """Serial-Daten in separatem Thread lesen"""
        while self.running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line.startswith("SIGNAL:"):
                        signal_value = int(line.split(":")[1])
                        self.data_queue.put(('signal', signal_value))
                    elif line.startswith("Clients:"):
                        client_count = int(line.split(":")[1].strip())
                        self.data_queue.put(('clients', client_count))
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(0.1)
                
    def process_serial_data(self):
        """Serial-Daten verarbeiten (GUI-Thread)"""
        try:
            while not self.data_queue.empty():
                data_type, value = self.data_queue.get_nowait()
                
                if data_type == 'signal':
                    self.update_signal(value)
                elif data_type == 'clients':
                    self.update_client_count(value)
                    
        except queue.Empty:
            pass
        
        # Nächste Verarbeitung planen
        self.root.after(50, self.process_serial_data)
        
    def update_signal(self, signal_id):
        """Signal-Anzeige aktualisieren"""
        if signal_id in self.signal_definitions:
            self.current_signal = signal_id
            signal_info = self.signal_definitions[signal_id]
            
            # Hauptanzeige aktualisieren
            self.signal_number.config(text=str(signal_id))
            self.signal_name.config(text=signal_info['name'])
            self.current_signal_display.config(bg=signal_info['color'])
            self.signal_number.config(bg=signal_info['color'])
            self.signal_name.config(bg=signal_info['color'])
            
            # Signal-Karten aktualisieren
            for card_id, card in self.signal_cards.items():
                if card_id == signal_id:
                    # Aktive Karte hervorheben
                    card.config(bg=signal_info['color'], relief='solid', borderwidth=4)
                    card.status_indicator.config(bg=signal_info['color'])
                else:
                    # Andere Karten zurücksetzen
                    card.config(bg=self.colors['surface'], relief='raised', borderwidth=2)
                    card.status_indicator.config(bg=self.colors['background'])
            
            # Historie aktualisieren
            self.signal_history.append({
                'signal': signal_id,
                'name': signal_info['name'],
                'timestamp': time.time()
            })
            
            # Nur letzte 100 Einträge behalten
            if len(self.signal_history) > 100:
                self.signal_history.pop(0)
                
    def update_client_count(self, count):
        """Client-Anzahl aktualisieren"""
        self.client_count = count
        self.client_label.config(text=str(count))
        
        # Farbe je nach Anzahl
        if count == 0:
            color = self.colors['error']
        elif count == 1:
            color = self.colors['success']
        else:
            color = self.colors['warning']
            
        self.client_label.config(fg=color)
        
    def update_time(self):
        """Zeit im Header aktualisieren"""
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def restart_connection(self):
        """Verbindung neu starten"""
        if self.serial_connection:
            self.serial_connection.close()
        self.setup_serial()
        
    def show_history(self):
        """Signal-Historie anzeigen"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Signal Historie")
        history_window.geometry("600x400")
        history_window.configure(bg=self.colors['background'])
        
        # Historie-Liste
        listbox = tk.Listbox(history_window, 
                            font=('Arial', 11),
                            bg=self.colors['surface'])
        listbox.pack(fill='both', expand=True, padx=20, pady=20)
        
        for entry in reversed(self.signal_history[-20:]):  # Letzte 20 Einträge
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry['timestamp']))
            listbox.insert(0, f"{timestamp} - Signal {entry['signal']}: {entry['name']}")
            
    def show_settings(self):
        """Einstellungen anzeigen"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Einstellungen")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['background'])
        
        tk.Label(settings_window,
                text="ESP32 Port:",
                font=('Arial', 12),
                bg=self.colors['background']).pack(pady=10)
        
        port_entry = tk.Entry(settings_window, font=('Arial', 11))
        port_entry.insert(0, self.esp32_port)
        port_entry.pack(pady=5)
        
        def save_settings():
            self.esp32_port = port_entry.get()
            self.esp32_status.config(text=f"Port: {self.esp32_port}")
            settings_window.destroy()
            
        ttk.Button(settings_window,
                  text="Speichern",
                  command=save_settings).pack(pady=20)
                  
    def scan_ports(self):
        """Verfügbare Serial-Ports scannen"""
        ports = []
        
        # Linux/Mac Ports
        for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/cu.usbserial*', '/dev/cu.usbmodem*']:
            ports.extend(glob.glob(pattern))
        
        # Windows Ports (falls auf Windows)
        if sys.platform.startswith('win'):
            import serial.tools.list_ports
            ports.extend([port.device for port in serial.tools.list_ports.comports()])
        
        # Combobox aktualisieren
        self.flash_port_combo['values'] = ports
        if ports:
            self.flash_port_combo.set(ports[0])
            self.flash_status.config(text=f"Gefunden: {len(ports)} Port(s)")
        else:
            self.flash_status.config(text="Keine Ports gefunden")
    
    def on_device_change(self):
        """Geräte-Auswahl geändert"""
        device = self.device_var.get()
        if device == "ESP32":
            self.flash_btn.config(text="📱 ESP32 Flashen")
            self.current_sketch_path = self.esp32_sketch_path
            self.hint_title.config(text="💡 ESP32 WICHTIG:")
            self.hint_text.config(text="Boot-Button drücken wenn\n'Connecting...' erscheint!")
            self.hint_frame.config(bg=self.colors['warning'])
            self.hint_title.config(bg=self.colors['warning'])
            self.hint_text.config(bg=self.colors['warning'])
        else:  # GIGA
            self.flash_btn.config(text="🔧 GIGA Flashen")
            self.current_sketch_path = self.giga_sketch_path
            self.hint_title.config(text="💡 GIGA INFO:")
            self.hint_text.config(text="Automatisches Flashen\nkein Button nötig!")
            self.hint_frame.config(bg=self.colors['success'])
            self.hint_title.config(bg=self.colors['success'])
            self.hint_text.config(bg=self.colors['success'])
        
        sketch_name = os.path.basename(self.current_sketch_path)
        self.flash_status.config(text=f"Gerät: {device}, Sketch: {sketch_name}")

    def select_sketch(self):
        """Arduino Sketch auswählen"""
        initial_dir = os.path.dirname(self.current_sketch_path)
        sketch_dir = filedialog.askdirectory(
            title="Arduino Sketch Ordner auswählen",
            initialdir=initial_dir
        )
        if sketch_dir:
            self.current_sketch_path = sketch_dir
            sketch_name = os.path.basename(sketch_dir)
            device = self.device_var.get()
            self.flash_status.config(text=f"Gerät: {device}, Sketch: {sketch_name}")
    
    def check_arduino_cli(self):
        """Arduino CLI verfügbarkeit prüfen"""
        try:
            result = subprocess.run(['arduino-cli', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def install_arduino_cli(self):
        """Arduino CLI installieren"""
        self.flash_status.config(text="Installiere Arduino CLI...")
        try:
            # Download und Installation
            install_cmd = "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Core installieren
            subprocess.run(['arduino-cli', 'core', 'update-index'], check=True)
            subprocess.run(['arduino-cli', 'core', 'install', 'esp32:esp32'], check=True)
            
            return True
        except Exception as e:
            self.flash_status.config(text=f"Installation fehlgeschlagen: {e}")
            return False
    
    def flash_device(self):
        """Aktuell ausgewähltes Gerät flashen"""
        device = self.device_var.get()
        if device == "ESP32":
            self.flash_esp32()
        else:
            self.flash_giga()
    
    def flash_esp32(self):
        """ESP32 flashen"""
        if not self.flash_port_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Port aus!")
            return
        
        if not os.path.exists(self.current_sketch_path):
            messagebox.showerror("Fehler", "ESP32 Sketch-Pfad nicht gefunden!")
            return
        
        # Arduino CLI prüfen
        if not self.check_arduino_cli():
            response = messagebox.askyesno(
                "Arduino CLI nicht gefunden",
                "Arduino CLI ist nicht installiert. Soll es automatisch installiert werden?"
            )
            if response:
                if not self.install_arduino_cli():
                    return
            else:
                return
        
        # Flash-Thread starten
        self.flash_btn.config(state='disabled', text="⏳ Flashe ESP32...")
        flash_thread = threading.Thread(target=self._flash_esp32_worker)
        flash_thread.daemon = True
        flash_thread.start()
    
    def flash_giga(self):
        """Arduino GIGA flashen"""
        if not self.flash_port_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Port aus!")
            return
        
        if not os.path.exists(self.current_sketch_path):
            messagebox.showerror("Fehler", "GIGA Sketch-Pfad nicht gefunden!")
            return
        
        # Arduino CLI prüfen
        if not self.check_arduino_cli():
            response = messagebox.askyesno(
                "Arduino CLI nicht gefunden",
                "Arduino CLI ist nicht installiert. Soll es automatisch installiert werden?"
            )
            if response:
                if not self.install_arduino_cli():
                    return
            else:
                return
        
        # Flash-Thread starten
        self.flash_btn.config(state='disabled', text="⏳ Flashe GIGA...")
        flash_thread = threading.Thread(target=self._flash_giga_worker)
        flash_thread.daemon = True
        flash_thread.start()
    
    def flash_both_devices(self):
        """Beide Geräte nacheinander flashen"""
        response = messagebox.askyesno(
            "Beide Geräte flashen",
            "Sollen ESP32 und Arduino GIGA nacheinander geflasht werden?\n\n" +
            "1. Zuerst wird Arduino GIGA geflasht\n" +
            "2. Dann ESP32 (Boot-Button bereithalten!)"
        )
        if response:
            self.flash_btn.config(state='disabled', text="⏳ Flashe beide...")
            flash_thread = threading.Thread(target=self._flash_both_worker)
            flash_thread.daemon = True
            flash_thread.start()
    
    def _flash_esp32_worker(self):
        """ESP32 Flash-Prozess in separatem Thread"""
        try:
            port = self.flash_port_var.get()
            
            # Status Updates im GUI-Thread
            self.root.after(0, lambda: self.flash_status.config(text="Kompiliere ESP32 Sketch..."))
            
            # Kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: self.flash_status.config(text="ESP32 Kompilierung fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # Upload
            self.root.after(0, lambda: self.flash_status.config(text="ESP32 Upload... BOOT-BUTTON DRÜCKEN!"))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', port,
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ ESP32 Flash erfolgreich!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", "ESP32 erfolgreich geflasht!"))
                
                # Verbindung neu starten nach kurzer Pause
                self.root.after(3000, self.restart_connection)
            else:
                self.root.after(0, lambda: self.flash_status.config(text="❌ ESP32 Flash fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ ESP32 Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "ESP32 Flash-Prozess Timeout. Boot-Button gedrückt?"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ ESP32 Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="📱 ESP32 Flashen"))
    
    def _flash_giga_worker(self):
        """Arduino GIGA Flash-Prozess in separatem Thread"""
        try:
            port = self.flash_port_var.get()
            
            # Status Updates im GUI-Thread
            self.root.after(0, lambda: self.flash_status.config(text="Kompiliere GIGA Sketch..."))
            
            # Kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: self.flash_status.config(text="GIGA Kompilierung fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # Upload
            self.root.after(0, lambda: self.flash_status.config(text="GIGA Upload läuft..."))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', port,
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ GIGA Flash erfolgreich!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", "Arduino GIGA erfolgreich geflasht!"))
            else:
                self.root.after(0, lambda: self.flash_status.config(text="❌ GIGA Flash fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ GIGA Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "GIGA Flash-Prozess Timeout"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ GIGA Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🔧 GIGA Flashen"))
    
    def _flash_both_worker(self):
        """Beide Geräte nacheinander flashen"""
        try:
            # Ports automatisch erkennen
            ports = []
            for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/cu.usbserial*', '/dev/cu.usbmodem*']:
                ports.extend(glob.glob(pattern))
            
            if len(ports) < 2:
                self.root.after(0, lambda: messagebox.showerror("Fehler", 
                    f"Nicht genügend Ports gefunden!\nGefunden: {len(ports)}, Benötigt: 2\n" +
                    "Bitte beide Geräte anschließen."))
                return
            
            # Annahme: GIGA meist auf /dev/ttyACM*, ESP32 auf /dev/ttyUSB*
            giga_port = None
            esp32_port = None
            
            for port in ports:
                if '/dev/ttyACM' in port or '/dev/cu.usbmodem' in port:
                    giga_port = port
                elif '/dev/ttyUSB' in port or '/dev/cu.usbserial' in port:
                    esp32_port = port
            
            if not giga_port:
                giga_port = ports[0]
            if not esp32_port:
                esp32_port = ports[1] if len(ports) > 1 else ports[0]
            
            # 1. Arduino GIGA flashen
            self.root.after(0, lambda: self.flash_status.config(text="1/2: Flashe Arduino GIGA..."))
            
            # GIGA kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # GIGA uploaden
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', giga_port,
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Upload fehlgeschlagen:\n{result.stderr}"))
                return
            
            self.root.after(0, lambda: self.flash_status.config(text="✅ GIGA fertig! Warte 3 Sekunden..."))
            time.sleep(3)
            
            # 2. ESP32 flashen
            self.root.after(0, lambda: self.flash_status.config(text="2/2: Flashe ESP32..."))
            
            # ESP32 kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # ESP32 uploaden
            self.root.after(0, lambda: self.flash_status.config(text="ESP32 Upload... BOOT-BUTTON DRÜCKEN!"))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', esp32_port,
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ Beide Geräte erfolgreich geflasht!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", 
                    f"Beide Geräte erfolgreich geflasht!\n\n" +
                    f"GIGA Port: {giga_port}\n" +
                    f"ESP32 Port: {esp32_port}"))
                
                # ESP32 Verbindung neu starten
                self.esp32_port = esp32_port
                self.root.after(3000, self.restart_connection)
            else:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "Flash-Prozess Timeout. ESP32 Boot-Button gedrückt?"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🚀 Beide Geräte flashen"))
        
    def run(self):
        """GUI starten"""
        try:
            self.root.mainloop()
        finally:
            self.running = False
            if self.serial_connection:
                self.serial_connection.close()

def main():
    parser = argparse.ArgumentParser(description='Bertrandt ESP32 Monitor')
    parser.add_argument('--esp32-port', default='/dev/ttyUSB0',
                       help='ESP32 Serial Port')
    
    args = parser.parse_args()
    
    app = BertrandtGUI(esp32_port=args.esp32_port)
    app.run()

if __name__ == "__main__":
    main()