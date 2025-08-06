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
from PIL import Image, ImageTk
import json

class BertrandtGUI:
    def __init__(self, esp32_port=None):
        self.root = tk.Tk()
        self.root.title("Bertrandt ESP32 Monitor")
        
        # 16:9 Format für verschiedene Bildschirmgrößen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Optimale 16:9 Größe basierend auf Bildschirm
        if screen_width >= 1920:
            window_width, window_height = 1920, 1080
        elif screen_width >= 1600:
            window_width, window_height = 1600, 900
        elif screen_width >= 1366:
            window_width, window_height = 1366, 768
        else:
            window_width, window_height = 1280, 720
        
        # Fenster zentrieren
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1280, 720)  # Minimum 16:9
        
        # Vollbild-Option
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.fullscreen = False
        
        # Modern Clean Design - Minimalistisch & Intuitiv (Inspired by Apple/Google/Notion)
        self.colors = {
            'background_primary': '#FFFFFF',     # Haupthintergrund (sauberes Weiß)
            'background_secondary': '#F8F9FA',   # Sekundär-Hintergrund (sehr helles Grau)
            'background_tertiary': '#F1F3F4',    # Karten/Widgets (dezentes Grau)
            'background_hover': '#E8F0FE',       # Hover-Zustand (sehr helles Blau)
            'text_primary': '#202124',           # Haupt-Text (fast schwarz, aber weicher)
            'text_secondary': '#5F6368',         # Sekundär-Text (mittleres Grau)
            'text_tertiary': '#9AA0A6',          # Tertiär-Text (helles Grau)
            'accent_primary': '#1A73E8',         # Google Blue (vertrauenswürdig)
            'accent_secondary': '#34A853',       # Google Green (Erfolg)
            'accent_tertiary': '#EA4335',        # Google Red (Warnung/Fehler)
            'accent_warning': '#FBBC04',         # Google Yellow (Warnung)
            'border_light': '#E8EAED',           # Helle Rahmen
            'border_medium': '#DADCE0',          # Mittlere Rahmen
            'shadow': 'rgba(60, 64, 67, 0.15)',  # Weiche Schatten
            'bertrandt_blue': '#003366',         # Bertrandt Corporate Blue
            'bertrandt_orange': '#FF6600',       # Bertrandt Corporate Orange
        }
        
        # Modern Typography - Clean & Readable (Cross-platform compatible)
        base_size = min(window_width, window_height) // 60  # Responsive Basis
        self.fonts = {
            'display': ('Helvetica Neue', max(32, base_size + 20), 'bold'),      # Große Headlines
            'title': ('Helvetica Neue', max(24, base_size + 12), 'bold'),        # Titel (Bold)
            'subtitle': ('Helvetica Neue', max(18, base_size + 6), 'normal'),    # Untertitel (Normal)
            'body': ('Helvetica Neue', max(14, base_size + 2), 'normal'),        # Fließtext
            'label': ('Helvetica Neue', max(13, base_size + 1), 'normal'),       # Labels (Normal)
            'button': ('Helvetica Neue', max(14, base_size + 2), 'bold'),        # Buttons (Bold)
            'caption': ('Helvetica Neue', max(12, base_size), 'normal'),         # Kleine Texte
            'nav': ('Helvetica Neue', max(15, base_size + 3), 'normal'),         # Navigation (Normal)
        }
        
        self.root.configure(bg=self.colors['background_primary'])
        
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
        
        # Multimedia-Seiten Definitionen (für Messestand)
        self.signal_definitions = {
            1: {'name': 'Willkommen', 'color': self.colors['accent_secondary'], 'icon': '🏠', 'content_type': 'welcome'},
            2: {'name': 'Unternehmen', 'color': self.colors['bertrandt_blue'], 'icon': '🏢', 'content_type': 'company'},
            3: {'name': 'Produkte', 'color': self.colors['bertrandt_orange'], 'icon': '⚙️', 'content_type': 'products'},
            4: {'name': 'Innovation', 'color': self.colors['accent_primary'], 'icon': '💡', 'content_type': 'innovation'},
            5: {'name': 'Technologie', 'color': self.colors['bertrandt_blue'], 'icon': '🔬', 'content_type': 'technology'},
            6: {'name': 'Referenzen', 'color': self.colors['accent_secondary'], 'icon': '⭐', 'content_type': 'references'},
            7: {'name': 'Team', 'color': self.colors['bertrandt_orange'], 'icon': '👥', 'content_type': 'team'},
            8: {'name': 'Karriere', 'color': self.colors['accent_primary'], 'icon': '🚀', 'content_type': 'career'},
            9: {'name': 'Kontakt', 'color': self.colors['bertrandt_blue'], 'icon': '📞', 'content_type': 'contact'},
            10: {'name': 'Danke', 'color': self.colors['accent_secondary'], 'icon': '🙏', 'content_type': 'thanks'}
        }
        
        # Multimedia Content Storage
        self.content_pages = {}
        self.current_page = 1
        self.media_player = None
        
        # Content-Ordner erstellen
        self.content_dir = os.path.join(os.path.dirname(__file__), "content")
        self.ensure_content_structure()
        
        # Multimedia-Komponenten
        self.current_image = None
        self.current_video = None
        
        # Dev Mode
        self.dev_mode = False
        self.dev_timer = None
        
        self.setup_styles()
        self.setup_gui()
        self.setup_serial()
        
        # GUI ist jetzt vollständig buttonbasiert - keine Tastatur-Shortcuts mehr nötig
        
    def setup_styles(self):
        """Modern Clean UI Styles - Minimalistisch & Intuitiv"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Clean Header Style
        self.style.configure('Header.TFrame', 
                           background=self.colors['background_primary'],
                           relief='flat',
                           borderwidth=0)
        
        # Modern Card Style mit subtilen Schatten
        self.style.configure('Card.TFrame',
                           background=self.colors['background_primary'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=self.colors['border_light'],
                           darkcolor=self.colors['border_light'])
        
        # Primary Button - Google Material Design inspiriert
        self.style.configure('Primary.TButton',
                           background=self.colors['accent_primary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Primary.TButton',
                      background=[('active', '#1557B0'),
                                ('pressed', '#1557B0'),
                                ('disabled', self.colors['border_medium'])])
        
        # Success Button - Clean Green
        self.style.configure('Success.TButton',
                           background=self.colors['accent_secondary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Success.TButton',
                      background=[('active', '#2E7D32'),
                                ('pressed', '#2E7D32')])
        
        # Warning Button - Clean Orange/Red
        self.style.configure('Warning.TButton',
                           background=self.colors['accent_tertiary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Warning.TButton',
                      background=[('active', '#C5221F'),
                                ('pressed', '#C5221F')])
        
        # Secondary Button - Outline Style
        self.style.configure('Secondary.TButton',
                           background=self.colors['background_primary'],
                           foreground=self.colors['accent_primary'],
                           font=self.fonts['button'],
                           relief='solid',
                           borderwidth=1,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['background_hover']),
                                ('pressed', self.colors['background_hover'])],
                      bordercolor=[('!active', self.colors['border_medium']),
                                 ('active', self.colors['accent_primary'])])
        
        # Chip Button - Moderne Pills
        self.style.configure('Chip.TButton',
                           background=self.colors['background_tertiary'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['caption'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(16, 8))
        
        self.style.map('Chip.TButton',
                      background=[('active', self.colors['accent_primary']),
                                ('pressed', self.colors['accent_primary'])],
                      foreground=[('active', 'white'),
                                ('pressed', 'white')])
        
        # Ghost Button - Sehr subtil
        self.style.configure('Ghost.TButton',
                           background=self.colors['background_primary'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(16, 8))
        
        self.style.map('Ghost.TButton',
                      background=[('active', self.colors['background_secondary']),
                                ('pressed', self.colors['background_tertiary'])],
                      foreground=[('active', self.colors['text_primary'])])
        
        # Modern Combobox
        self.style.configure('TCombobox',
                           fieldbackground=self.colors['background_primary'],
                           background=self.colors['background_primary'],
                           bordercolor=self.colors['border_medium'],
                           arrowcolor=self.colors['text_secondary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['body'],
                           padding=(12, 8))
        
        # Modern Entry
        self.style.configure('TEntry',
                           fieldbackground=self.colors['background_primary'],
                           bordercolor=self.colors['border_medium'],
                           focuscolor=self.colors['accent_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['body'],
                           padding=(12, 8))
        
    def setup_gui(self):
        """Hauptgui-Layout im Bertrandt Design"""
        
        # Header
        self.create_header()
        
        # Main Content Area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 16:9 Layout - Left Panel (1/10 Breite - wirklich minimal)
        left_panel = ttk.Frame(main_frame, style='Card.TFrame')
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.config(width=max(80, self.root.winfo_width() // 12))
        left_panel.pack_propagate(False)
        
        # Right Panel - Multimedia Display (90% Breite)
        right_panel = ttk.Frame(main_frame, style='Card.TFrame')
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.create_status_panel(left_panel)
        self.create_multimedia_display(right_panel)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Modern Clean Header - Minimalistisch & Intuitiv"""
        # Clean Header mit subtiler Trennung
        header_height = max(80, self.root.winfo_height() // 12)
        header_frame = tk.Frame(self.root, bg=self.colors['background_primary'], height=header_height)
        header_frame.pack(fill='x', pady=(0, 0))
        header_frame.pack_propagate(False)
        
        # Logo-Bereich (links) - Sticky Navigation
        logo_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        logo_frame.pack(side='left', padx=32, pady=16)
        
        # Bertrandt Logo - Bild laden (angepasst für hellen Hintergrund)
        self.load_bertrandt_logo(logo_frame)
        
        # Produktname - Clean Typography
        product_label = tk.Label(logo_frame,
                                text="ESP32 Monitor",
                                font=self.fonts['title'],
                                fg=self.colors['bertrandt_blue'],
                                bg=self.colors['background_primary'])
        product_label.pack(anchor='w')
        
        # Tagline - Subtil
        tagline_label = tk.Label(logo_frame,
                               text="Engineering tomorrow",
                               font=self.fonts['caption'],
                               fg=self.colors['text_tertiary'],
                               bg=self.colors['background_primary'])
        tagline_label.pack(anchor='w')
        
        # Navigation (Mitte) - Horizontal Navigation
        nav_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        nav_frame.pack(side='left', expand=True, padx=40, pady=16)
        
        # Navigation Buttons - Clean & Modern
        nav_buttons_frame = tk.Frame(nav_frame, bg=self.colors['background_primary'])
        nav_buttons_frame.pack()
        
        # Modern Navigation Buttons
        nav_btn_style = {
            'font': self.fonts['nav'],
            'bg': self.colors['background_primary'],
            'fg': self.colors['text_secondary'],
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 12,
            'activebackground': self.colors['background_hover'],
            'activeforeground': self.colors['accent_primary'],
            'cursor': 'hand2'
        }
        
        # Hauptnavigation - Übersichtliche Verlinkungen
        self.nav_buttons = {}
        
        # Home Button
        home_btn = tk.Button(nav_buttons_frame,
                 text="🏠 Home",
                 command=lambda: self.safe_page_select(1),
                 **nav_btn_style)
        home_btn.pack(side='left', padx=2)
        self.nav_buttons[1] = home_btn
        
        # Unternehmen Button
        company_btn = tk.Button(nav_buttons_frame,
                 text="🏢 Unternehmen", 
                 command=lambda: self.safe_page_select(2),
                 **nav_btn_style)
        company_btn.pack(side='left', padx=2)
        self.nav_buttons[2] = company_btn
        
        # Produkte Button
        products_btn = tk.Button(nav_buttons_frame,
                 text="⚙️ Produkte",
                 command=lambda: self.safe_page_select(3),
                 **nav_btn_style)
        products_btn.pack(side='left', padx=2)
        self.nav_buttons[3] = products_btn
        
        # Innovation Button
        innovation_btn = tk.Button(nav_buttons_frame,
                 text="💡 Innovation",
                 command=lambda: self.safe_page_select(4),
                 **nav_btn_style)
        innovation_btn.pack(side='left', padx=2)
        self.nav_buttons[4] = innovation_btn
        
        # Kontakt Button
        contact_btn = tk.Button(nav_buttons_frame,
                 text="Demo",
                 command=self.start_auto_demo,
                 **nav_btn_style).pack(side='left', padx=4)
        
        tk.Button(nav_buttons_frame,
                 text="Stop",
                 command=self.stop_auto_demo,
                 **nav_btn_style).pack(side='left', padx=4)
        
        tk.Button(nav_buttons_frame,
                 text="Content Creator",
                 command=self.show_content_creator,
                 **nav_btn_style).pack(side='left', padx=4)
        
        # Status & Actions (rechts)
        status_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        status_frame.pack(side='right', padx=32, pady=16)
        
        # Status Indicator - Subtil aber informativ
        status_container = tk.Frame(status_frame, bg=self.colors['background_primary'])
        status_container.pack(anchor='e')
        
        # Connection Status - Clean Design
        self.connection_status = tk.Label(status_container,
                                         text="● Offline",
                                         font=self.fonts['caption'],
                                         fg=self.colors['accent_tertiary'],
                                         bg=self.colors['background_primary'])
        self.connection_status.pack(anchor='e')
        
        # Zeit - Dezent
        self.time_label = tk.Label(status_container,
                                  text="",
                                  font=self.fonts['caption'],
                                  fg=self.colors['text_tertiary'],
                                  bg=self.colors['background_primary'])
        self.time_label.pack(anchor='e', pady=(4, 0))
        
        # Subtile Trennung - Moderne Border
        separator = tk.Frame(self.root, bg=self.colors['border_light'], height=1)
        separator.pack(fill='x')
        
        # Zeit aktualisieren
        self.update_time()
    
    def load_bertrandt_logo(self, parent):
        """Bertrandt Logo aus Datei laden"""
        logo_path = os.path.join(os.path.dirname(__file__), "Bertrandt_logo.svg.png")
        
        try:
            # Logo-Bild laden
            logo_image = Image.open(logo_path)
            
            # Logo zu Bertrandt Blau konvertieren für hellen Hintergrund
            logo_image = self.convert_logo_to_dark(logo_image)
            
            # Logo-Größe: 1/10 der Bildschirmbreite
            logo_width = max(120, self.root.winfo_width() // 10)
            # Proportional skalieren
            aspect_ratio = logo_image.width / logo_image.height
            logo_height = int(logo_width / aspect_ratio)
            
            # Bild skalieren
            logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Logo-Label erstellen
            logo_label = tk.Label(parent,
                                 image=self.logo_photo,
                                 bg=self.colors['background_secondary'])
            logo_label.pack()
            
            print(f"✅ Bertrandt Logo geladen: {logo_width}x{logo_height}px (original, weiß, 1/10 Breite)")
            
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")
            # Fallback: Text-Logo
            logo_label = tk.Label(parent, 
                                 text="BERTRANDT",
                                 font=self.fonts['display'],
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['background_secondary'])
            logo_label.pack()
    
    def convert_logo_to_dark(self, image):
        """Logo zu dunkel konvertieren für hellen Hintergrund"""
        # Zu RGBA konvertieren falls nötig
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Pixel-Daten laden
        data = image.getdata()
        new_data = []
        
        for item in data:
            # Transparente Pixel beibehalten
            if item[3] == 0:  # Alpha = 0 (transparent)
                new_data.append(item)
            else:
                # Alle anderen Pixel zu Bertrandt Blau machen, Alpha beibehalten
                # Bertrandt Corporate Blue: #003366
                new_data.append((0, 51, 102, item[3]))
        
        # Neue Pixel-Daten setzen
        image.putdata(new_data)
        return image
        
    def create_status_panel(self, parent):
        """Minimale Status Panel für schmale Sidebar"""
        # Kompakter Panel Header
        panel_height = max(30, self.root.winfo_height() // 25)
        panel_header = tk.Frame(parent, bg=self.colors['background_secondary'], height=panel_height)
        panel_header.pack(fill='x')
        panel_header.pack_propagate(False)
        
        title_label = tk.Label(panel_header,
                              text="STATUS",
                              font=self.fonts['caption'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        title_label.pack(pady=5)
        
        # Ultra-kompakte ESP32 Status Card
        conn_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        conn_card.pack(fill='x', padx=2, pady=3)
        
        # Sehr kompakter Header
        conn_header = tk.Frame(conn_card, bg=self.colors['accent_primary'], height=20)
        conn_header.pack(fill='x')
        conn_header.pack_propagate(False)
        
        tk.Label(conn_header,
                text="🔗",
                font=('Helvetica Neue', 10),
                fg=self.colors['text_primary'],
                bg=self.colors['accent_primary']).pack(pady=2)
        
        # Ultra-minimaler Content
        conn_content = tk.Frame(conn_card, bg=self.colors['background_tertiary'])
        conn_content.pack(fill='x', padx=2, pady=1)
        
        self.esp32_status = tk.Label(conn_content,
                                    text="OK",
                                    font=('Helvetica Neue', 6),
                                    fg=self.colors['text_primary'],
                                    bg=self.colors['background_tertiary'])
        self.esp32_status.pack()
        
        # Ultra-kompakte Client Count Card
        client_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        client_card.pack(fill='x', padx=2, pady=3)
        
        # Sehr kompakter Header
        client_header = tk.Frame(client_card, bg=self.colors['accent_secondary'], height=20)
        client_header.pack(fill='x')
        client_header.pack_propagate(False)
        
        tk.Label(client_header,
                text="👥",
                font=('Helvetica Neue', 10),
                fg=self.colors['text_primary'],
                bg=self.colors['accent_secondary']).pack(pady=2)
        
        # Kompakter Content
        client_content = tk.Frame(client_card, bg=self.colors['background_tertiary'])
        client_content.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.client_label = tk.Label(client_content,
                                    text="0",
                                    font=('Helvetica Neue', 18, 'bold'),
                                    fg=self.colors['accent_primary'],
                                    bg=self.colors['background_tertiary'])
        self.client_label.pack()
        
        # Client Status Text
        self.client_status_text = tk.Label(client_content,
                                          text="Keine Verbindung",
                                          font=self.fonts['label'],
                                          fg=self.colors['text_secondary'],
                                          bg=self.colors['background_tertiary'])
        self.client_status_text.pack()
        
        # Dark Theme Aktuelles Signal Card
        signal_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        signal_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        signal_header = tk.Frame(signal_card, bg=self.colors['accent_primary'], height=35)
        signal_header.pack(fill='x')
        signal_header.pack_propagate(False)
        
        tk.Label(signal_header,
                text="📡 AKTUELLES SIGNAL",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_primary']).pack(pady=8)
        
        # Signal Display mit Dark Theme
        self.current_signal_display = tk.Frame(signal_card, 
                                              bg=self.colors['background_secondary'],
                                              relief='flat',
                                              borderwidth=0)
        self.current_signal_display.pack(fill='x', padx=15, pady=15)
        
        # Signal Icon und Nummer
        signal_top = tk.Frame(self.current_signal_display, bg=self.colors['background_secondary'])
        signal_top.pack(fill='x', pady=10)
        
        self.signal_icon = tk.Label(signal_top,
                                   text="⏳",
                                   font=('Helvetica Neue', 24),
                                   fg=self.colors['text_primary'],
                                   bg=self.colors['background_secondary'])
        self.signal_icon.pack(side='left', padx=10)
        
        self.signal_number = tk.Label(signal_top,
                                     text="--",
                                     font=('Helvetica Neue', 32, 'bold'),
                                     fg=self.colors['text_primary'],
                                     bg=self.colors['background_secondary'])
        self.signal_number.pack(side='left', padx=10)
        
        # Signal Name
        self.signal_name = tk.Label(self.current_signal_display,
                                   text="WARTE AUF SIGNAL...",
                                   font=self.fonts['button'],
                                   fg=self.colors['accent_secondary'],
                                   bg=self.colors['background_secondary'])
        self.signal_name.pack(pady=(0, 15))
        
        # Flash Sektion für beide Geräte
        self.create_flash_section(parent)
        
        # Neue GUI-Steuerung Sektion (ersetzt Tastatureingaben)
        self.create_gui_control_section(parent)
        
        # Dark Theme Control Buttons
        btn_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        btn_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        btn_header = tk.Frame(btn_card, bg=self.colors['accent_primary'], height=35)
        btn_header.pack(fill='x')
        btn_header.pack_propagate(False)
        
        tk.Label(btn_header,
                text="⚙️ SYSTEM STEUERUNG",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_primary']).pack(pady=8)
        
        # Button Content
        btn_content = tk.Frame(btn_card, bg=self.colors['background_tertiary'])
        btn_content.pack(fill='x', padx=15, pady=15)
        
        ttk.Button(btn_content,
                  text="🔄 VERBINDUNG NEUSTARTEN",
                  style='Primary.TButton',
                  command=self.restart_connection).pack(fill='x', pady=3)
        
        ttk.Button(btn_content,
                  text="📊 SIGNAL HISTORIE",
                  style='Success.TButton',
                  command=self.show_history).pack(fill='x', pady=3)
        
        ttk.Button(btn_content,
                  text="⚙️ SYSTEM EINSTELLUNGEN",
                  style='Warning.TButton',
                  command=self.show_settings).pack(fill='x', pady=3)
        
        ttk.Button(btn_content,
                  text="🎬 CONTENT MANAGER",
                  style='Success.TButton',
                  command=self.show_content_manager).pack(fill='x', pady=3)
        
        # Dev Mode spezifische Buttons
        if self.dev_mode:
            dev_frame = tk.Frame(btn_content, bg=self.colors['accent_warning'], relief='solid', borderwidth=1)
            dev_frame.pack(fill='x', pady=(10, 0))
            
            tk.Label(dev_frame,
                    text="🔧 DEV MODE STEUERUNG",
                    font=self.fonts['button'],
                    fg=self.colors['background_primary'],
                    bg=self.colors['accent_warning']).pack(pady=5)
            
            dev_btn_frame = tk.Frame(dev_frame, bg=self.colors['accent_warning'])
            dev_btn_frame.pack(fill='x', padx=10, pady=(0, 10))
            
            ttk.Button(dev_btn_frame,
                      text="🤖 AUTO-DEMO",
                      command=self.start_auto_demo).pack(fill='x', pady=2)
            
            ttk.Button(dev_btn_frame,
                      text="⏹️ DEMO STOP",
                      command=self.stop_auto_demo).pack(fill='x', pady=2)
                  
    def create_flash_section(self, parent):
        """Dark Theme Arduino Flash-Sektion"""
        # Flash Card
        flash_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        flash_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        flash_header = tk.Frame(flash_card, bg=self.colors['accent_warning'], height=35)
        flash_header.pack(fill='x')
        flash_header.pack_propagate(False)
        
        tk.Label(flash_header,
                text="🔧 ARDUINO FLASH-TOOL",
                font=self.fonts['button'],
                fg=self.colors['background_primary'],
                bg=self.colors['accent_warning']).pack(pady=8)
        
        # Flash Content
        flash_content = tk.Frame(flash_card, bg=self.colors['background_tertiary'])
        flash_content.pack(fill='x', padx=15, pady=15)
        
        # Flash Status
        self.flash_status = tk.Label(flash_content,
                                    text="Bereit zum Flashen",
                                    font=self.fonts['label'],
                                    fg=self.colors['text_secondary'],
                                    bg=self.colors['background_tertiary'])
        self.flash_status.pack(anchor='w', pady=(0, 10))
        
        # Geräte-Auswahl Tabs
        device_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        device_frame.pack(fill='x', pady=5)
        
        self.device_var = tk.StringVar(value="ESP32")
        
        tk.Radiobutton(device_frame,
                      text="📱 ESP32",
                      variable=self.device_var,
                      value="ESP32",
                      font=self.fonts['label'],
                      bg=self.colors['background_tertiary'],
                      fg=self.colors['text_primary'],
                      selectcolor=self.colors['background_secondary'],
                      activebackground=self.colors['background_tertiary'],
                      command=self.on_device_change).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(device_frame,
                      text="🔧 Arduino GIGA",
                      variable=self.device_var,
                      value="GIGA",
                      font=self.fonts['label'],
                      bg=self.colors['background_tertiary'],
                      fg=self.colors['text_primary'],
                      selectcolor=self.colors['background_secondary'],
                      activebackground=self.colors['background_tertiary'],
                      command=self.on_device_change).pack(side='left')
        
        # Port Auswahl
        port_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        port_frame.pack(fill='x', pady=5)
        
        tk.Label(port_frame,
                text="Port:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_tertiary']).pack(side='left')
        
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
        flash_btn_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        flash_btn_frame.pack(fill='x', pady=10)
        
        self.flash_btn = ttk.Button(flash_btn_frame,
                                   text="📱 ESP32 FLASHEN",
                                   style='Primary.TButton',
                                   command=self.flash_device)
        self.flash_btn.pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="📁 SKETCH AUSWÄHLEN",
                  style='Success.TButton',
                  command=self.select_sketch).pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="🚀 BEIDE GERÄTE FLASHEN",
                  style='Warning.TButton',
                  command=self.flash_both_devices).pack(fill='x', pady=2)
        
        # Boot Button Hinweis
        self.hint_frame = tk.Frame(flash_content, 
                             bg=self.colors['accent_tertiary'],
                             relief='flat',
                             borderwidth=1)
        self.hint_frame.pack(fill='x', pady=10)
        
        self.hint_title = tk.Label(self.hint_frame,
                text="💡 ESP32 WICHTIG:",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_tertiary'])
        self.hint_title.pack(pady=(5, 0))
        
        self.hint_text = tk.Label(self.hint_frame,
                text="Boot-Button drücken wenn\n'Connecting...' erscheint!",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_tertiary'],
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
    
    def create_gui_control_section(self, parent):
        """Moderne GUI-Steuerung mit Buttons (ersetzt Tastatureingaben)"""
        # GUI Control Card
        gui_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
        gui_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        gui_header = tk.Frame(gui_card, bg=self.colors['accent_secondary'], height=35)
        gui_header.pack(fill='x')
        gui_header.pack_propagate(False)
        
        tk.Label(gui_header,
                text="🎮 MANUELLE STEUERUNG",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_secondary']).pack(pady=8)
        
        # GUI Content
        gui_content = tk.Frame(gui_card, bg=self.colors['background_tertiary'])
        gui_content.pack(fill='x', padx=15, pady=15)
        
        # Info Text
        info_label = tk.Label(gui_content,
                             text="Klicken Sie auf die Seiten-Buttons für direkte Navigation:",
                             font=self.fonts['label'],
                             fg=self.colors['text_secondary'],
                             bg=self.colors['background_tertiary'])
        info_label.pack(anchor='w', pady=(0, 10))
        
        # Seiten-Buttons Grid (2 Reihen à 5 Buttons)
        pages_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        pages_frame.pack(fill='x', pady=5)
        
        # Erste Reihe (Seiten 1-5)
        row1_frame = tk.Frame(pages_frame, bg=self.colors['background_tertiary'])
        row1_frame.pack(fill='x', pady=(0, 5))
        
        for i in range(1, 6):
            signal_info = self.signal_definitions[i]
            btn = ttk.Button(row1_frame,
                           text=f"{signal_info['icon']} {i}",
                           style='Chip.TButton',
                           command=lambda page=i: self.on_manual_page_select(page))
            btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Zweite Reihe (Seiten 6-10)
        row2_frame = tk.Frame(pages_frame, bg=self.colors['background_tertiary'])
        row2_frame.pack(fill='x')
        
        for i in range(6, 11):
            signal_info = self.signal_definitions[i]
            btn = ttk.Button(row2_frame,
                           text=f"{signal_info['icon']} {i}",
                           style='Chip.TButton',
                           command=lambda page=i: self.on_manual_page_select(page))
            btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Separator
        separator = tk.Frame(gui_content, bg=self.colors['background_secondary'], height=1)
        separator.pack(fill='x', pady=10)
        
        # Demo-Steuerung Buttons
        demo_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        demo_frame.pack(fill='x', pady=5)
        
        ttk.Button(demo_frame,
                  text="🤖 AUTO-DEMO STARTEN",
                  style='Success.TButton',
                  command=self.start_auto_demo).pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        ttk.Button(demo_frame,
                  text="⏹️ DEMO STOPPEN",
                  style='Warning.TButton',
                  command=self.stop_auto_demo).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Zusätzliche Steuerung
        extra_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        extra_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(extra_frame,
                  text="🏠 STARTSEITE",
                  style='Secondary.TButton',
                  command=lambda: self.on_manual_page_select(1)).pack(fill='x', expand=True)
        
        # Status für manuelle Steuerung
        self.manual_status = tk.Label(gui_content,
                                     text="Bereit für manuelle Steuerung",
                                     font=self.fonts['label'],
                                     fg=self.colors['text_secondary'],
                                     bg=self.colors['background_tertiary'])
        self.manual_status.pack(anchor='w', pady=(10, 0))
        
    def on_manual_page_select(self, page_id):
        """Manuelle Seitenauswahl über GUI-Button"""
        signal_info = self.signal_definitions.get(page_id, {})
        page_name = signal_info.get('name', f'Seite {page_id}')
        
        print(f"🎮 Manuelle Auswahl: Seite {page_id} - {page_name}")
        
        # Status aktualisieren
        self.manual_status.config(
            text=f"Seite {page_id} ausgewählt: {page_name}",
            fg=self.colors['accent_primary']
        )
        
        # Signal simulieren (funktioniert sowohl im Dev Mode als auch normal)
        if self.dev_mode:
            self.simulate_signal(page_id)
        else:
            # Auch im normalen Modus direkte Navigation ermöglichen
            self.update_signal(page_id)
    
    def show_content_creator(self):
        """Content Creator anzeigen - Erweiterte Content-Erstellung im Hauptfenster"""
        # Multimedia-Display temporär ausblenden
        if hasattr(self, 'content_frame'):
            self.content_frame.pack_forget()
        
        # Content Creator Frame erstellen
        self.creator_frame = tk.Frame(self.content_frame.master, bg=self.colors['background_tertiary'], relief='flat', borderwidth=2)
        self.creator_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Header
        header_frame = tk.Frame(self.creator_frame, bg=self.colors['background_secondary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="✨ CONTENT CREATOR",
                               font=self.fonts['title'],
                               fg=self.colors['accent_primary'],
                               bg=self.colors['background_secondary'])
        header_label.pack(pady=15)
        
        # Zurück Button
        back_btn = tk.Button(header_frame,
                            text="← Zurück",
                            font=self.fonts['button'],
                            bg=self.colors['background_tertiary'],
                            fg=self.colors['text_primary'],
                            relief='flat',
                            borderwidth=0,
                            padx=15,
                            pady=5,
                            activebackground=self.colors['accent_primary'],
                            activeforeground=self.colors['text_primary'],
                            command=self.hide_content_creator)
        back_btn.place(x=20, y=15)
        
        # Main Content Frame
        main_frame = tk.Frame(self.creator_frame, bg=self.colors['background_tertiary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Seiten-Auswahl
        left_panel = tk.Frame(main_frame, bg=self.colors['background_secondary'], width=200)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Seiten-Liste
        pages_label = tk.Label(left_panel,
                              text="📄 SEITEN",
                              font=self.fonts['button'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        pages_label.pack(pady=10)
        
        # Seiten-Buttons
        self.creator_selected_page = tk.IntVar(value=1)
        for signal_id, signal_info in self.signal_definitions.items():
            page_btn = tk.Radiobutton(left_panel,
                                     text=f"{signal_info['icon']} {signal_id}. {signal_info['name']}",
                                     variable=self.creator_selected_page,
                                     value=signal_id,
                                     font=self.fonts['label'],
                                     bg=self.colors['background_secondary'],
                                     fg=self.colors['text_primary'],
                                     selectcolor=signal_info['color'],
                                     activebackground=self.colors['background_secondary'],
                                     command=lambda: self.update_creator_content())
            page_btn.pack(fill='x', padx=10, pady=2)
        
        # Right Panel - Content Editor
        right_panel = tk.Frame(main_frame, bg=self.colors['background_secondary'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Editor Header
        editor_header = tk.Frame(right_panel, bg=self.colors['accent_primary'], height=40)
        editor_header.pack(fill='x')
        editor_header.pack_propagate(False)
        
        self.creator_page_title = tk.Label(editor_header,
                                          text="Seite 1 - Willkommen",
                                          font=self.fonts['button'],
                                          fg=self.colors['text_primary'],
                                          bg=self.colors['accent_primary'])
        self.creator_page_title.pack(pady=10)
        
        # Editor Content
        editor_content = tk.Frame(right_panel, bg=self.colors['background_secondary'])
        editor_content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Titel Editor
        tk.Label(editor_content,
                text="📝 Titel:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_title_entry = tk.Entry(editor_content,
                                           font=self.fonts['body'],
                                           bg=self.colors['background_tertiary'],
                                           fg=self.colors['text_primary'],
                                           insertbackground=self.colors['text_primary'])
        self.creator_title_entry.pack(fill='x', pady=(5, 15))
        
        # Untertitel Editor
        tk.Label(editor_content,
                text="📄 Untertitel:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_subtitle_entry = tk.Entry(editor_content,
                                              font=self.fonts['body'],
                                              bg=self.colors['background_tertiary'],
                                              fg=self.colors['text_primary'],
                                              insertbackground=self.colors['text_primary'])
        self.creator_subtitle_entry.pack(fill='x', pady=(5, 15))
        
        # Layout Auswahl
        tk.Label(editor_content,
                text="🎨 Layout:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_layout_var = tk.StringVar(value="text_only")
        layout_frame = tk.Frame(editor_content, bg=self.colors['background_secondary'])
        layout_frame.pack(fill='x', pady=(5, 15))
        
        layouts = [
            ("📝 Nur Text", "text_only"),
            ("🖼️ Bild + Text", "image_text"),
            ("🎬 Video + Text", "video_text"),
            ("🖼️ Vollbild Bild", "fullscreen_image"),
            ("🎬 Vollbild Video", "fullscreen_video")
        ]
        
        for i, (text, value) in enumerate(layouts):
            tk.Radiobutton(layout_frame,
                          text=text,
                          variable=self.creator_layout_var,
                          value=value,
                          font=self.fonts['label'],
                          bg=self.colors['background_secondary'],
                          fg=self.colors['text_primary'],
                          selectcolor=self.colors['background_tertiary'],
                          activebackground=self.colors['background_secondary']).pack(anchor='w')
        
        # Text Editor
        tk.Label(editor_content,
                text="📝 Inhalt:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        text_frame = tk.Frame(editor_content, bg=self.colors['background_secondary'])
        text_frame.pack(fill='both', expand=True, pady=(5, 15))
        
        self.creator_text_widget = tk.Text(text_frame,
                                          font=self.fonts['body'],
                                          bg=self.colors['background_tertiary'],
                                          fg=self.colors['text_primary'],
                                          insertbackground=self.colors['text_primary'],
                                          wrap=tk.WORD,
                                          height=10)
        
        text_scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.creator_text_widget.yview)
        self.creator_text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        self.creator_text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = tk.Frame(self.creator_frame, bg=self.colors['background_tertiary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="💾 SPEICHERN",
                  style='Success.TButton',
                  command=self.save_creator_content).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="👁️ VORSCHAU",
                  style='Primary.TButton',
                  command=self.preview_creator_content).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="📁 ORDNER ÖFFNEN",
                  style='Secondary.TButton',
                  command=self.open_creator_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="🏠 HAUPTANSICHT",
                  style='Warning.TButton',
                  command=self.hide_content_creator).pack(side='right')
        
        # Erste Seite laden
        self.creator_active = True
        self.update_creator_content()
    
    def hide_content_creator(self):
        """Content Creator ausblenden und zur Hauptansicht zurückkehren"""
        if hasattr(self, 'creator_frame'):
            self.creator_frame.destroy()
        
        # Multimedia-Display wieder anzeigen
        if hasattr(self, 'content_frame'):
            self.content_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.creator_active = False
        # Aktuelle Seite neu laden
        self.load_content_page(self.current_page)
    
    def update_creator_content(self):
        """Content Creator Inhalt aktualisieren"""
        if not hasattr(self, 'creator_active') or not self.creator_active:
            return
            
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        
        # Header aktualisieren
        self.creator_page_title.config(text=f"Seite {page_id} - {signal_info['name']}")
        
        # Content laden
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {
                "title": signal_info['name'],
                "subtitle": f"Seite {page_id} - {signal_info['name']}",
                "text_content": f"Inhalt für Seite {page_id}",
                "layout": "text_only"
            }
        
        # Felder füllen
        self.creator_title_entry.delete(0, tk.END)
        self.creator_title_entry.insert(0, config.get('title', ''))
        
        self.creator_subtitle_entry.delete(0, tk.END)
        self.creator_subtitle_entry.insert(0, config.get('subtitle', ''))
        
        self.creator_layout_var.set(config.get('layout', 'text_only'))
        
        self.creator_text_widget.delete('1.0', tk.END)
        self.creator_text_widget.insert('1.0', config.get('text_content', ''))
    
    def save_creator_content(self):
        """Content Creator Inhalt speichern"""
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        config = {
            "title": self.creator_title_entry.get(),
            "subtitle": self.creator_subtitle_entry.get(),
            "layout": self.creator_layout_var.get(),
            "text_content": self.creator_text_widget.get('1.0', tk.END).strip(),
            "background_image": "",
            "video": "",
            "images": []
        }
        
        config_path = os.path.join(page_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        messagebox.showinfo("Erfolg", f"Seite {page_id} wurde gespeichert!")
    
    def preview_creator_content(self):
        """Content Creator Vorschau anzeigen"""
        page_id = self.creator_selected_page.get()
        # Zur Hauptansicht wechseln und Seite anzeigen
        self.hide_content_creator()
        self.load_content_page(page_id)
    
    def open_creator_folder(self):
        """Content Creator Ordner öffnen"""
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        self.open_page_folder(page_dir)
        
    def create_multimedia_display(self, parent):
        """Multimedia-Anzeige für Messestand"""
        # Header
        panel_header = tk.Frame(parent, bg=self.colors['background_secondary'], height=50)
        panel_header.pack(fill='x')
        panel_header.pack_propagate(False)
        
        title_label = tk.Label(panel_header,
                              text="🎬 MULTIMEDIA PRÄSENTATION",
                              font=self.fonts['title'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        title_label.pack(pady=15)
        
        # Hauptcontainer für Content
        content_container = tk.Frame(parent, bg=self.colors['background_primary'])
        content_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Multimedia Content Area (Hauptbereich)
        self.content_frame = tk.Frame(content_container, bg=self.colors['background_tertiary'], relief='flat', borderwidth=2)
        self.content_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Navigation Panel (unten) - responsive Höhe
        nav_height = max(80, self.root.winfo_height() // 12)
        nav_panel = tk.Frame(content_container, bg=self.colors['background_secondary'], height=nav_height)
        nav_panel.pack(fill='x')
        nav_panel.pack_propagate(False)
        
        # Navigation Header
        nav_header = tk.Label(nav_panel,
                             text="📱 SEITEN-NAVIGATION",
                             font=self.fonts['subtitle'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_secondary'])
        nav_header.pack(pady=(8, 5))
        
        # Navigation Grid
        self.nav_grid = tk.Frame(nav_panel, bg=self.colors['background_secondary'])
        self.nav_grid.pack(fill='x', padx=20, pady=(0, 10))
        
        # Navigation Cards erstellen
        self.nav_cards = {}
        for i, (signal_id, signal_info) in enumerate(self.signal_definitions.items()):
            col = i % 10  # 10 Karten in einer Reihe
            
            card = self.create_nav_card(self.nav_grid, signal_id, signal_info)
            card.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
            self.nav_cards[signal_id] = card
            
            # GUI-Button Klick-Handler für alle Modi
            card.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
            card.icon_label.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
            card.number_label.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
        
        # Grid konfigurieren
        for i in range(10):
            self.nav_grid.columnconfigure(i, weight=1)
        
        # Initialen Content laden
        self.load_content_page(1)
        
    def ensure_content_structure(self):
        """Content-Ordnerstruktur erstellen"""
        if not os.path.exists(self.content_dir):
            os.makedirs(self.content_dir)
        
        # Unterordner für jeden Content-Typ erstellen
        for signal_id, signal_info in self.signal_definitions.items():
            content_type = signal_info['content_type']
            page_dir = os.path.join(self.content_dir, f"page_{signal_id}_{content_type}")
            if not os.path.exists(page_dir):
                os.makedirs(page_dir)
                
                # Beispiel-Konfiguration erstellen
                config = {
                    "title": signal_info['name'],
                    "subtitle": f"Seite {signal_id} - {signal_info['name']}",
                    "background_image": "",
                    "video": "",
                    "text_content": f"Willkommen auf Seite {signal_id}: {signal_info['name']}\n\nHier können Sie Inhalte hinzufügen:\n• Bilder\n• Videos\n• Texte\n\nBearbeiten Sie die config.json in:\n{page_dir}",
                    "images": [],
                    "layout": "text_only"  # text_only, image_text, video_text, fullscreen_image, fullscreen_video
                }
                
                config_path = os.path.join(page_dir, "config.json")
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_content_page(self, page_id):
        """Multimedia-Seite laden und anzeigen"""
        self.current_page = page_id
        
        # Alte Inhalte löschen
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Content-Konfiguration laden
        signal_info = self.signal_definitions.get(page_id, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            # Fallback-Konfiguration
            config = {
                "title": signal_info.get('name', f'Seite {page_id}'),
                "subtitle": f"Seite {page_id}",
                "text_content": f"Seite {page_id} - Inhalt wird geladen...",
                "layout": "text_only"
            }
        
        # Layout basierend auf Konfiguration erstellen
        self.create_content_layout(config, page_dir)
        
        # Navigation aktualisieren
        self.update_navigation(page_id)
    
    def create_content_layout(self, config, page_dir):
        """Content-Layout basierend auf Konfiguration erstellen"""
        layout = config.get('layout', 'text_only')
        
        # Header mit Titel
        header_frame = tk.Frame(self.content_frame, bg=self.colors['background_secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Titel - responsive
        title_label = tk.Label(header_frame,
                              text=config.get('title', 'Titel'),
                              font=self.fonts['display'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        title_label.pack(pady=15)
        
        # Untertitel
        if config.get('subtitle'):
            subtitle_label = tk.Label(header_frame,
                                     text=config.get('subtitle'),
                                     font=self.fonts['subtitle'],
                                     fg=self.colors['accent_primary'],
                                     bg=self.colors['background_secondary'])
            subtitle_label.pack()
        
        # Content Area - responsive Padding
        padding_x = max(10, self.root.winfo_width() // 80)
        padding_y = max(10, self.root.winfo_height() // 60)
        content_area = tk.Frame(self.content_frame, bg=self.colors['background_tertiary'])
        content_area.pack(fill='both', expand=True, padx=padding_x, pady=padding_y)
        
        # Layout-spezifische Inhalte
        if layout == 'text_only':
            self.create_text_layout(content_area, config)
        elif layout == 'image_text':
            self.create_image_text_layout(content_area, config, page_dir)
        elif layout == 'video_text':
            self.create_video_text_layout(content_area, config, page_dir)
        elif layout == 'fullscreen_image':
            self.create_fullscreen_image_layout(content_area, config, page_dir)
        elif layout == 'fullscreen_video':
            self.create_fullscreen_video_layout(content_area, config, page_dir)
        else:
            self.create_text_layout(content_area, config)
    
    def create_text_layout(self, parent, config):
        """Nur-Text Layout - responsive"""
        text_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        text_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Scrollbarer Text mit Scrollbar
        text_container = tk.Frame(text_frame, bg=self.colors['background_tertiary'])
        text_container.pack(fill='both', expand=True)
        
        # Text Widget
        text_widget = tk.Text(text_container,
                             font=self.fonts['label'],
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             wrap=tk.WORD,
                             relief='flat',
                             borderwidth=0,
                             padx=15,
                             pady=15)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_container, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Text einfügen
        text_content = config.get('text_content', 'Kein Text verfügbar.')
        text_widget.insert('1.0', text_content)
        text_widget.config(state='disabled')  # Nur lesen
    
    def create_image_text_layout(self, parent, config, page_dir):
        """Bild + Text Layout"""
        # Horizontal aufteilen
        left_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Bild laden
        self.load_image_to_frame(left_frame, config, page_dir)
        
        # Text
        self.create_text_layout(right_frame, config)
    
    def create_video_text_layout(self, parent, config, page_dir):
        """Video + Text Layout"""
        # Vertikal aufteilen
        top_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        top_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        bottom_frame = tk.Frame(parent, bg=self.colors['background_tertiary'], height=200)
        bottom_frame.pack(fill='x', pady=(10, 0))
        bottom_frame.pack_propagate(False)
        
        # Video-Platzhalter
        self.create_video_placeholder(top_frame, config, page_dir)
        
        # Text
        self.create_text_layout(bottom_frame, config)
    
    def create_fullscreen_image_layout(self, parent, config, page_dir):
        """Vollbild-Bild Layout"""
        self.load_image_to_frame(parent, config, page_dir, fullscreen=True)
    
    def create_fullscreen_video_layout(self, parent, config, page_dir):
        """Vollbild-Video Layout"""
        self.create_video_placeholder(parent, config, page_dir, fullscreen=True)
    
    def load_image_to_frame(self, parent, config, page_dir, fullscreen=False):
        """Bild in Frame laden"""
        image_path = None
        
        # Bild aus Konfiguration
        if config.get('background_image'):
            image_path = os.path.join(page_dir, config['background_image'])
        
        # Erstes Bild aus images-Liste
        elif config.get('images') and len(config['images']) > 0:
            image_path = os.path.join(page_dir, config['images'][0])
        
        # Fallback: Erstes gefundene Bild im Ordner
        if not image_path or not os.path.exists(image_path):
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                for file in os.listdir(page_dir):
                    if file.lower().endswith(ext):
                        image_path = os.path.join(page_dir, file)
                        break
                if image_path:
                    break
        
        if image_path and os.path.exists(image_path):
            try:
                # Bild laden und skalieren
                image = Image.open(image_path)
                
                if fullscreen:
                    # Vollbild-Größe - responsive
                    max_width = self.root.winfo_width() - 100
                    max_height = self.root.winfo_height() - 200
                else:
                    # Halbe Größe - responsive
                    max_width = (self.root.winfo_width() - 400) // 2
                    max_height = (self.root.winfo_height() - 300) // 2
                
                # Proportional skalieren
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Label für Bild
                image_label = tk.Label(parent, image=photo, bg=self.colors['background_tertiary'])
                image_label.image = photo  # Referenz behalten
                image_label.pack(expand=True)
                
            except Exception as e:
                # Fehler-Platzhalter
                error_label = tk.Label(parent,
                                      text=f"🖼️ Bild konnte nicht geladen werden\n{str(e)}",
                                      font=self.fonts['label'],
                                      fg=self.colors['accent_tertiary'],
                                      bg=self.colors['background_tertiary'])
                error_label.pack(expand=True)
        else:
            # Kein Bild gefunden
            placeholder_label = tk.Label(parent,
                                        text="🖼️ Kein Bild verfügbar\n\nFügen Sie Bilder in den Ordner hinzu:\n" + page_dir,
                                        font=self.fonts['label'],
                                        fg=self.colors['text_secondary'],
                                        bg=self.colors['background_tertiary'],
                                        justify='center')
            placeholder_label.pack(expand=True)
    
    def create_video_placeholder(self, parent, config, page_dir, fullscreen=False):
        """Video-Platzhalter erstellen"""
        # Video-Unterstützung würde hier implementiert werden
        # Für jetzt: Platzhalter
        video_frame = tk.Frame(parent, bg=self.colors['background_secondary'], relief='solid', borderwidth=2)
        video_frame.pack(fill='both', expand=True)
        
        placeholder_label = tk.Label(video_frame,
                                    text="🎬 VIDEO BEREICH\n\nVideo-Unterstützung wird implementiert\n\nUnterstützte Formate:\n• MP4\n• AVI\n• MOV",
                                    font=self.fonts['subtitle'],
                                    fg=self.colors['text_secondary'],
                                    bg=self.colors['background_secondary'],
                                    justify='center')
        placeholder_label.pack(expand=True)
    
    def safe_page_select(self, page_id):
        """Sichere Seitenauswahl mit Cleanup"""
        try:
            # Vorherige Seite cleanup
            if hasattr(self, 'current_page_id') and self.current_page_id != page_id:
                self.cleanup_current_page()
            
            # Neue Seite laden
            self.on_manual_page_select(page_id)
            self.current_page_id = page_id
            
            # Navigation aktualisieren
            self.update_navigation(page_id)
            
            print(f"🎯 Seite {page_id} erfolgreich geladen")
        except Exception as e:
            print(f"❌ Fehler beim Seitenwechsel: {e}")
    
    def cleanup_current_page(self):
        """Aktuelle Seite ordnungsgemäß schließen"""
        try:
            # Multimedia cleanup
            if hasattr(self, 'multimedia_frame'):
                for widget in self.multimedia_frame.winfo_children():
                    widget.destroy()
            
            # Timer cleanup falls vorhanden
            if hasattr(self, 'auto_demo_timer') and self.auto_demo_timer:
                self.root.after_cancel(self.auto_demo_timer)
                self.auto_demo_timer = None
                
        except Exception as e:
            print(f"⚠️ Cleanup Warnung: {e}")

    def update_navigation(self, active_page):
        """Navigation aktualisieren - Header und Sidebar"""
        # Header Navigation aktualisieren
        if hasattr(self, 'nav_buttons'):
            for page_id, button in self.nav_buttons.items():
                if page_id == active_page:
                    button.config(bg=self.colors['accent_primary'], 
                                fg=self.colors['text_primary'])
                else:
                    button.config(bg=self.colors['background_primary'], 
                                fg=self.colors['text_secondary'])
        
        # Sidebar Navigation aktualisieren
        if hasattr(self, 'nav_cards'):
            for page_id, card in self.nav_cards.items():
                if page_id == active_page:
                    # Aktive Seite hervorheben
                    card.config(bg=self.colors['background_secondary'], relief='solid', borderwidth=2)
                    card.card_header.config(bg=self.colors['accent_primary'])
                else:
                    # Andere Seiten zurücksetzen
                    card.config(bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
                    card.card_header.config(bg=card.signal_info['color'])
    
    def toggle_fullscreen(self, event=None):
        """Vollbild umschalten (F11)"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        if self.fullscreen:
            print("🖥️ Vollbild aktiviert (ESC zum Beenden)")
        else:
            print("🖥️ Fenstermodus aktiviert")
    
    def exit_fullscreen(self, event=None):
        """Vollbild beenden (ESC)"""
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
        print("🖥️ Vollbild beendet")
        
    def create_nav_card(self, parent, signal_id, signal_info):
        """Minimale Navigation-Karte für sehr schmale Sidebar (1/10)"""
        # Sehr kompakte Kartengröße für 1/10 Breite
        card_width = max(35, self.root.winfo_width() // 50)
        card_height = max(25, self.root.winfo_height() // 30)
        
        card = tk.Frame(parent,
                       bg=self.colors['background_tertiary'],
                       relief='flat',
                       borderwidth=1,
                       width=card_width,
                       height=card_height)
        
        # Minimaler Card Header
        card_header = tk.Frame(card, bg=signal_info['color'], height=2)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        # Minimaler Card Content
        card_content = tk.Frame(card, bg=self.colors['background_tertiary'])
        card_content.pack(fill='both', expand=True, padx=2, pady=1)
        
        # Kleines Icon
        icon_size = max(8, self.root.winfo_width() // 120)
        icon_label = tk.Label(card_content,
                             text=signal_info['icon'],
                             font=('Helvetica Neue', icon_size),
                             bg=self.colors['background_tertiary'])
        icon_label.pack()
        
        # Kleine Nummer
        number_label = tk.Label(card_content,
                               text=str(signal_id),
                               font=('Helvetica Neue', 8, 'bold'),
                               fg=signal_info['color'],
                               bg=self.colors['background_tertiary'])
        number_label.pack()
        
        # Referenzen speichern
        card.icon_label = icon_label
        card.number_label = number_label
        card.signal_info = signal_info
        card.card_header = card_header
        
        return card
    
            
    def create_signal_card(self, parent, signal_id, signal_info):
        """Dark Theme Signal-Karte"""
        card = tk.Frame(parent,
                       bg=self.colors['background_tertiary'],
                       relief='flat',
                       borderwidth=1,
                       width=220,
                       height=160)
        
        # Dark Theme Card Header mit Farbe
        card_header = tk.Frame(card, bg=signal_info['color'], height=8)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        # Card Content
        card_content = tk.Frame(card, bg=self.colors['background_tertiary'])
        card_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Icon
        icon_label = tk.Label(card_content,
                             text=signal_info['icon'],
                             font=('Helvetica Neue', 28),
                             bg=self.colors['background_tertiary'])
        icon_label.pack(pady=(5, 10))
        
        # Signal Nummer
        number_label = tk.Label(card_content,
                               text=f"SIGNAL {signal_id}",
                               font=self.fonts['button'],
                               fg=signal_info['color'],
                               bg=self.colors['background_tertiary'])
        number_label.pack()
        
        # Signal Name
        name_label = tk.Label(card_content,
                             text=signal_info['name'].upper(),
                             font=self.fonts['label'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_tertiary'],
                             wraplength=180,
                             justify='center')
        name_label.pack(pady=(5, 10))
        
        # Status Indikator
        status_indicator = tk.Frame(card,
                                   bg=self.colors['background_secondary'],
                                   height=4)
        status_indicator.pack(fill='x', side='bottom')
        
        # Referenzen speichern
        card.icon_label = icon_label
        card.number_label = number_label
        card.name_label = name_label
        card.status_indicator = status_indicator
        card.signal_info = signal_info
        card.card_header = card_header
        
        return card
        
    def create_footer(self):
        """Dark Theme Footer"""
        # Akzent-Linie über Footer
        separator = tk.Frame(self.root, bg=self.colors['accent_primary'], height=2)
        separator.pack(fill='x', side='bottom')
        
        footer_frame = tk.Frame(self.root, bg=self.colors['background_secondary'], height=45)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        # Copyright (links)
        footer_text = tk.Label(footer_frame,
                              text="© 2024 Bertrandt AG | ESP32 Monitor System v2.0 | Engineering tomorrow",
                              font=self.fonts['label'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        footer_text.pack(side='left', padx=30, pady=12)
        
        # System Info (rechts)
        info_frame = tk.Frame(footer_frame, bg=self.colors['background_secondary'])
        info_frame.pack(side='right', padx=30, pady=12)
        
        self.fps_label = tk.Label(info_frame,
                                 text="FPS: --",
                                 font=self.fonts['label'],
                                 fg=self.colors['accent_secondary'],
                                 bg=self.colors['background_secondary'])
        self.fps_label.pack(side='right', padx=(20, 0))
        
        # Standort
        location_label = tk.Label(info_frame,
                                 text="Standort: Deutschland",
                                 font=self.fonts['label'],
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['background_secondary'])
        location_label.pack(side='right')
        
    def setup_serial(self):
        """Serial-Verbindung einrichten oder Dev Mode aktivieren"""
        try:
            self.serial_connection = serial.Serial(self.esp32_port, 115200, timeout=1)
            time.sleep(2)
            self.connection_status.config(text="● Online", fg=self.colors['accent_secondary'])
            self.dev_mode = False
            self.start_serial_reading()
        except Exception as e:
            # Dev Mode aktivieren
            self.dev_mode = True
            self.connection_status.config(text="● Dev Mode", fg=self.colors['accent_warning'])
            self.start_dev_mode()
            print(f"🔧 Dev Mode aktiviert - Keine Hardware gefunden: {e}")
    
    def start_dev_mode(self):
        """Dev Mode starten - Simuliert Arduino-Signale"""
        print("🔧 Dev Mode gestartet - Simuliere Arduino-Signale...")
        
        # Dev Mode Info anzeigen
        self.show_dev_mode_info()
        
        # Automatische Demo starten (optional) - aber erst nach GUI-Initialisierung
        self.root.after(1000, self.start_auto_demo)
    
    def show_dev_mode_info(self):
        """Dev Mode Information anzeigen"""
        dev_info = tk.Toplevel(self.root)
        dev_info.title("🔧 Dev Mode")
        dev_info.geometry("500x400")
        dev_info.configure(bg=self.colors['background_primary'])
        
        # Header
        header_label = tk.Label(dev_info,
                               text="🔧 ENTWICKLERMODUS AKTIV",
                               font=self.fonts['title'],
                               fg=self.colors['accent_warning'],
                               bg=self.colors['background_primary'])
        header_label.pack(pady=20)
        
        # Info Text
        info_text = """
Keine Arduino/ESP32 Hardware gefunden!

Der Dev Mode ist aktiviert mit folgenden Features:

🎮 GUI-STEUERUNG:
• Klicken Sie auf die Seiten-Buttons (1-10)
• Nutzen Sie die Navigations-Karten
• Verwenden Sie die Schnellzugriff-Buttons

🤖 AUTO-DEMO:
• Automatischer Seitenwechsel alle 5 Sekunden
• Zeigt alle Multimedia-Inhalte
• Perfekt zum Testen und Präsentationen

🛠️ ENTWICKLUNG:
• Alle Multimedia-Features verfügbar
• Content Manager funktioniert normal
• Kein Arduino/ESP32 erforderlich
• Vollständig buttonbasierte Bedienung

Schließen Sie Hardware an und starten Sie neu
für den normalen Betrieb mit Arduino-Steuerung.
        """
        
        info_label = tk.Label(dev_info,
                             text=info_text,
                             font=self.fonts['label'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_primary'],
                             justify='left')
        info_label.pack(padx=20, pady=10)
        
        # Buttons
        button_frame = tk.Frame(dev_info, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="🤖 AUTO-DEMO STARTEN",
                  style='Success.TButton',
                  command=lambda: [self.start_auto_demo(), dev_info.destroy()]).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="⏹️ AUTO-DEMO STOPPEN",
                  style='Warning.TButton',
                  command=self.stop_auto_demo).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="✅ OK",
                  style='Primary.TButton',
                  command=dev_info.destroy).pack(side='right')
    
    def start_auto_demo(self):
        """Automatische Demo starten"""
        if self.dev_mode:
            self.stop_auto_demo()  # Vorherige Demo stoppen
            self.auto_demo_page = 1
            self.schedule_next_demo_page()
            print("🤖 Auto-Demo gestartet")
    
    def stop_auto_demo(self):
        """Automatische Demo stoppen"""
        if hasattr(self, 'dev_timer') and self.dev_timer:
            self.root.after_cancel(self.dev_timer)
            self.dev_timer = None
            print("⏹️ Auto-Demo gestoppt")
    
    def schedule_next_demo_page(self):
        """Nächste Demo-Seite planen"""
        if self.dev_mode:
            # Aktuelle Seite laden
            self.simulate_signal(self.auto_demo_page)
            
            # Nächste Seite vorbereiten
            self.auto_demo_page += 1
            if self.auto_demo_page > 10:
                self.auto_demo_page = 1
            
            # Timer für nächste Seite setzen (5 Sekunden)
            self.dev_timer = self.root.after(5000, self.schedule_next_demo_page)
    
    def simulate_signal(self, signal_id):
        """Arduino-Signal simulieren"""
        if self.dev_mode:
            print(f"🎮 Dev Mode: Simuliere Signal {signal_id}")
            self.update_signal(signal_id)
            
            # Client Count simulieren
            import random
            client_count = random.randint(0, 3)
            self.update_client_count(client_count)
            
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
        """Signal-Anzeige mit Bertrandt Design aktualisieren"""
        if signal_id in self.signal_definitions:
            self.current_signal = signal_id
            signal_info = self.signal_definitions[signal_id]
            
            # Hauptanzeige mit Bertrandt Styling aktualisieren
            self.signal_number.config(text=str(signal_id))
            self.signal_name.config(text=signal_info['name'].upper())
            self.signal_icon.config(text=signal_info['icon'])
            self.current_signal_display.config(bg=signal_info['color'])
            self.signal_number.config(bg=signal_info['color'])
            self.signal_name.config(bg=signal_info['color'])
            self.signal_icon.config(bg=signal_info['color'])
            
            # WICHTIG: Multimedia-Seite wechseln
            self.load_content_page(signal_id)
            
            # Navigation aktualisieren
            self.update_navigation(signal_id)
            
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
        """Client-Anzahl mit Bertrandt Styling aktualisieren"""
        self.client_count = count
        self.client_label.config(text=str(count))
        
        # Bertrandt Farben und Status je nach Anzahl
        if count == 0:
            color = self.colors['accent_tertiary']
            status_text = "KEINE VERBINDUNG"
        elif count == 1:
            color = self.colors['accent_secondary']
            status_text = "OPTIMAL VERBUNDEN"
        else:
            color = self.colors['accent_primary']
            status_text = f"{count} CLIENTS AKTIV"
            
        self.client_label.config(fg=color)
        self.client_status_text.config(text=status_text, fg=color)
        
    def update_time(self):
        """Zeit im Header mit Bertrandt Format aktualisieren"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        self.time_label.config(text=f"{current_date} | {current_time}")
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
        history_window.configure(bg=self.colors['background_primary'])
        
        # Historie-Liste
        listbox = tk.Listbox(history_window, 
                            font=self.fonts['label'],
                            bg=self.colors['background_tertiary'],
                            fg=self.colors['text_primary'],
                            selectbackground=self.colors['accent_primary'])
        listbox.pack(fill='both', expand=True, padx=20, pady=20)
        
        for entry in reversed(self.signal_history[-20:]):  # Letzte 20 Einträge
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry['timestamp']))
            listbox.insert(0, f"{timestamp} - Signal {entry['signal']}: {entry['name']}")
            
    def show_settings(self):
        """Einstellungen anzeigen"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Einstellungen")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['background_primary'])
        
        tk.Label(settings_window,
                text="ESP32 Port:",
                font=self.fonts['subtitle'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_primary']).pack(pady=10)
        
        port_entry = tk.Entry(settings_window, 
                             font=self.fonts['body'],
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             insertbackground=self.colors['text_primary'])
        port_entry.insert(0, self.esp32_port)
        port_entry.pack(pady=5)
        
        def save_settings():
            self.esp32_port = port_entry.get()
            self.esp32_status.config(text=f"Port: {self.esp32_port}")
            settings_window.destroy()
            
        ttk.Button(settings_window,
                  text="SPEICHERN",
                  style='Primary.TButton',
                  command=save_settings).pack(pady=20)
    
    def show_content_manager(self):
        """Content Manager anzeigen"""
        content_window = tk.Toplevel(self.root)
        content_window.title("Content Manager")
        content_window.geometry("800x600")
        content_window.configure(bg=self.colors['background_primary'])
        
        # Header
        header_label = tk.Label(content_window,
                               text="🎬 CONTENT MANAGER",
                               font=self.fonts['title'],
                               fg=self.colors['text_primary'],
                               bg=self.colors['background_primary'])
        header_label.pack(pady=20)
        
        # Info
        info_label = tk.Label(content_window,
                             text="Verwalten Sie Multimedia-Inhalte für alle 10 Seiten",
                             font=self.fonts['subtitle'],
                             fg=self.colors['accent_primary'],
                             bg=self.colors['background_primary'])
        info_label.pack(pady=(0, 20))
        
        # Content-Ordner anzeigen
        content_frame = tk.Frame(content_window, bg=self.colors['background_tertiary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollbare Liste
        canvas = tk.Canvas(content_frame, bg=self.colors['background_tertiary'])
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background_tertiary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content für jede Seite anzeigen
        for signal_id, signal_info in self.signal_definitions.items():
            self.create_content_item(scrollable_frame, signal_id, signal_info)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(content_window, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="📁 CONTENT-ORDNER ÖFFNEN",
                  style='Primary.TButton',
                  command=self.open_content_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="🔄 CONTENT NEULADEN",
                  style='Success.TButton',
                  command=lambda: self.load_content_page(self.current_page)).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="❌ SCHLIESSEN",
                  style='Warning.TButton',
                  command=content_window.destroy).pack(side='right')
    
    def create_content_item(self, parent, signal_id, signal_info):
        """Content-Item für eine Seite erstellen"""
        item_frame = tk.Frame(parent, bg=self.colors['background_secondary'], relief='solid', borderwidth=1)
        item_frame.pack(fill='x', pady=5, padx=10)
        
        # Header
        header_frame = tk.Frame(item_frame, bg=signal_info['color'], height=30)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text=f"{signal_info['icon']} Seite {signal_id}: {signal_info['name']}",
                               font=self.fonts['button'],
                               fg=self.colors['text_primary'],
                               bg=signal_info['color'])
        header_label.pack(pady=5)
        
        # Content Info
        content_frame = tk.Frame(item_frame, bg=self.colors['background_secondary'])
        content_frame.pack(fill='x', padx=10, pady=10)
        
        # Ordner-Pfad
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{signal_id}_{content_type}")
        
        path_label = tk.Label(content_frame,
                             text=f"📁 {page_dir}",
                             font=self.fonts['label'],
                             fg=self.colors['text_secondary'],
                             bg=self.colors['background_secondary'],
                             anchor='w')
        path_label.pack(fill='x')
        
        # Dateien auflisten
        if os.path.exists(page_dir):
            files = os.listdir(page_dir)
            if files:
                files_text = "📄 Dateien: " + ", ".join(files[:3])
                if len(files) > 3:
                    files_text += f" ... (+{len(files)-3} weitere)"
            else:
                files_text = "📄 Keine Dateien"
        else:
            files_text = "📄 Ordner nicht gefunden"
        
        files_label = tk.Label(content_frame,
                              text=files_text,
                              font=self.fonts['label'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'],
                              anchor='w')
        files_label.pack(fill='x')
        
        # Buttons
        btn_frame = tk.Frame(content_frame, bg=self.colors['background_secondary'])
        btn_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame,
                  text="📁 ÖFFNEN",
                  command=lambda: self.open_page_folder(page_dir)).pack(side='left', padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="👁️ VORSCHAU",
                  command=lambda: self.load_content_page(signal_id)).pack(side='left')
    
    def open_content_folder(self):
        """Haupt-Content-Ordner öffnen"""
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", self.content_dir])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", self.content_dir])
        else:  # Linux
            subprocess.run(["xdg-open", self.content_dir])
    
    def open_page_folder(self, page_dir):
        """Spezifischen Seiten-Ordner öffnen"""
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", page_dir])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", page_dir])
        else:  # Linux
            subprocess.run(["xdg-open", page_dir])
                  
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
            self.flash_btn.config(text="📱 ESP32 FLASHEN")
            self.current_sketch_path = self.esp32_sketch_path
            self.hint_title.config(text="💡 ESP32 WICHTIG:")
            self.hint_text.config(text="Boot-Button drücken wenn\n'Connecting...' erscheint!")
            self.hint_frame.config(bg=self.colors['accent_tertiary'])
            self.hint_title.config(bg=self.colors['accent_tertiary'])
            self.hint_text.config(bg=self.colors['accent_tertiary'])
        else:  # GIGA
            self.flash_btn.config(text="🔧 GIGA FLASHEN")
            self.current_sketch_path = self.giga_sketch_path
            self.hint_title.config(text="💡 GIGA INFO:")
            self.hint_text.config(text="Automatisches Flashen\nkein Button nötig!")
            self.hint_frame.config(bg=self.colors['accent_secondary'])
            self.hint_title.config(bg=self.colors['accent_secondary'])
            self.hint_text.config(bg=self.colors['accent_secondary'])
        
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
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="📱 ESP32 FLASHEN"))
    
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
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🔧 GIGA FLASHEN"))
    
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
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🚀 BEIDE GERÄTE FLASHEN"))
        
    def run(self):
        """GUI starten"""
        try:
            self.root.mainloop()
        finally:
            self.running = False
            if self.dev_mode:
                self.stop_auto_demo()
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