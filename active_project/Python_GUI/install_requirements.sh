#!/bin/bash

echo "🔧 Installiere Bertrandt Multimedia GUI Abhängigkeiten..."

# Python-Pakete installieren
echo "📦 Installiere Python-Pakete..."
/usr/local/bin/python3 -m pip install pyserial
/usr/local/bin/python3 -m pip install Pillow

echo "✅ Installation abgeschlossen!"
echo ""
echo "🎬 Bertrandt Multimedia GUI ist bereit!"
echo "Starten Sie mit: /usr/local/bin/python3 Bertrandt_GUI.py"