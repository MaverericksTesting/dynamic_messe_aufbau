#!/bin/bash

echo "🔧 Starte Bertrandt GUI im Dev Mode..."
echo ""
echo "📋 Dev Mode Features:"
echo "• 🎮 Klicken Sie auf Navigation-Karten"
echo "• ⌨️  Tastatur-Shortcuts: 1-0 für Seiten"
echo "• 🤖 Auto-Demo mit 'D' starten"
echo "• ⏹️  Demo mit 'S' stoppen"
echo "• 🎬 Content Manager mit 'C' öffnen"
echo ""

cd "$(dirname "$0")/Python_GUI"

# Abhängigkeiten prüfen und installieren
if ! /usr/local/bin/python3 -c "import PIL" 2>/dev/null; then
    echo "📦 Installiere fehlende Abhängigkeiten..."
    ./install_requirements.sh
fi

# GUI starten (Dev Mode aktiviert sich automatisch ohne Hardware)
echo "🚀 Starte GUI..."
/usr/local/bin/python3 Bertrandt_GUI.py

echo "✅ Dev Mode beendet"