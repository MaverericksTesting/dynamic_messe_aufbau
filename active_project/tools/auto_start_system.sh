#!/bin/bash
# 🚀 Bertrandt ESP32 GUI System - Automatischer Starter
# Findet Arduino GIGA, flasht ESP32, startet GUI

echo "🔧 Bertrandt ESP32 GUI System wird gestartet..."
echo "=================================================="

# Farben für bessere Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arbeitsverzeichnis setzen
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Funktionen
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Cleanup-Funktion für Ctrl+C
cleanup() {
    log_info "Beende alle Hintergrundprozesse..."
    jobs -p | xargs -r kill 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# 1. Abhängigkeiten prüfen
log_info "Prüfe Abhängigkeiten..."

# Arduino CLI prüfen und installieren
if ! command -v arduino-cli &> /dev/null; then
    log_warning "Arduino CLI nicht gefunden. Installiere..."
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
    export PATH=$PATH:$HOME/bin
    # Nach Installation nochmal prüfen
    if ! command -v arduino-cli &> /dev/null; then
        log_error "Arduino CLI Installation fehlgeschlagen!"
        exit 1
    fi
fi

# Python prüfen
if ! command -v python3 &> /dev/null; then
    log_error "Python3 ist nicht installiert!"
    exit 1
fi

# Python-Abhängigkeiten prüfen
log_info "Prüfe Python-Abhängigkeiten..."
python3 -c "import serial, tkinter" 2>/dev/null || {
    log_warning "Installiere fehlende Python-Abhängigkeiten..."
    pip3 install pyserial
    # Nach Installation nochmal prüfen
    python3 -c "import serial, tkinter" 2>/dev/null || {
        log_error "Python-Abhängigkeiten konnten nicht installiert werden!"
        exit 1
    }
}

log_success "Abhängigkeiten OK"

# 2. Arduino Cores installieren und konfigurieren
log_info "Konfiguriere Arduino CLI..."
arduino-cli config init 2>/dev/null || true
arduino-cli core update-index

log_info "Installiere Arduino Cores..."
arduino-cli core install esp32:esp32 2>/dev/null || log_warning "ESP32 Core bereits installiert"
arduino-cli core install arduino:mbed_giga 2>/dev/null || log_warning "GIGA Core bereits installiert"

# 3. Arduino GIGA finden
log_info "Suche Arduino GIGA..."
GIGA_PORT=""

# Verfügbare Ports anzeigen für Debugging
log_info "Verfügbare Ports:"
arduino-cli board list

# Ports scannen - erweiterte Suche
for port in /dev/ttyACM* /dev/ttyUSB* /dev/cu.usbmodem* /dev/cu.usbserial*; do
    if [ -e "$port" ]; then
        log_info "Prüfe Port: $port"
        # Versuche Board-Info zu bekommen
        BOARD_INFO=$(arduino-cli board list 2>/dev/null | grep "$port" || echo "")
        if [ -n "$BOARD_INFO" ]; then
            log_info "Board Info: $BOARD_INFO"
            # Suche nach GIGA oder Arduino Mbed
            if echo "$BOARD_INFO" | grep -qi "giga\|arduino.*mbed\|arduino.*r4"; then
                GIGA_PORT="$port"
                log_success "Arduino GIGA gefunden auf: $GIGA_PORT"
                break
            fi
        else
            # Fallback: Nimm ersten ACM Port als GIGA
            if [[ "$port" == /dev/ttyACM* ]] && [ -z "$GIGA_PORT" ]; then
                GIGA_PORT="$port"
                log_warning "Arduino GIGA vermutet auf: $GIGA_PORT (Fallback)"
            fi
        fi
    fi
done

if [ -z "$GIGA_PORT" ]; then
    log_error "Arduino GIGA nicht gefunden!"
    log_info "Verfügbare Ports:"
    ls -la /dev/tty* 2>/dev/null | grep -E "(ACM|USB|usbmodem)" || echo "Keine USB-Ports gefunden"
    log_info "Stellen Sie sicher, dass:"
    echo "   - Arduino GIGA per USB angeschlossen ist"
    echo "   - Treiber installiert sind"
    echo "   - Berechtigung für USB-Zugriff vorhanden ist (sudo usermod -a -G dialout \$USER)"
    exit 1
fi

# 4. ESP32 finden
log_info "Suche ESP32..."
ESP32_PORT=""

for port in /dev/ttyUSB* /dev/ttyACM* /dev/cu.usbserial* /dev/cu.SLAB_USBtoUART*; do
    if [ -e "$port" ] && [ "$port" != "$GIGA_PORT" ]; then
        log_info "Prüfe ESP32 Port: $port"
        BOARD_INFO=$(arduino-cli board list 2>/dev/null | grep "$port" || echo "")
        if [ -n "$BOARD_INFO" ]; then
            log_info "Board Info: $BOARD_INFO"
            if echo "$BOARD_INFO" | grep -qi "esp32\|esp\|unknown\|Unknown"; then
                ESP32_PORT="$port"
                log_success "ESP32 gefunden auf: $ESP32_PORT"
                break
            fi
        else
            # Fallback: Nimm ersten USB Port als ESP32
            if [[ "$port" == /dev/ttyUSB* ]] && [ -z "$ESP32_PORT" ]; then
                ESP32_PORT="$port"
                log_warning "ESP32 vermutet auf: $ESP32_PORT (Fallback)"
            fi
        fi
    fi
done

if [ -z "$ESP32_PORT" ]; then
    log_error "ESP32 nicht gefunden!"
    log_info "Verfügbare Ports (außer GIGA):"
    ls -la /dev/tty* 2>/dev/null | grep -E "(USB|usbserial)" | grep -v "$GIGA_PORT" || echo "Keine ESP32-Ports gefunden"
    log_info "Stellen Sie sicher, dass:"
    echo "   - ESP32 per USB angeschlossen ist"
    echo "   - ESP32 Treiber installiert sind"
    echo "   - ESP32 im Download-Modus ist (falls nötig)"
    exit 1
fi

# 5. USB-Berechtigungen setzen
log_info "Setze USB-Berechtigungen..."
sudo chmod 666 "$GIGA_PORT" "$ESP32_PORT" 2>/dev/null || {
    log_warning "Konnte Berechtigungen nicht setzen. Versuche ohne sudo..."
}

# 6. Arduino GIGA flashen
log_info "Flashe Arduino GIGA..."
log_info "Kompiliere GIGA Code..."
if arduino-cli compile --fqbn arduino:mbed_giga:giga Arduino/GIGA_UDP_Sender/; then
    log_info "Upload auf GIGA Port: $GIGA_PORT"
    if arduino-cli upload -p "$GIGA_PORT" --fqbn arduino:mbed_giga:giga Arduino/GIGA_UDP_Sender/; then
        log_success "Arduino GIGA erfolgreich geflasht"
    else
        log_error "Fehler beim Upload auf Arduino GIGA"
        log_info "Versuche alternativen Upload..."
        # Retry mit verbose output
        arduino-cli upload -p "$GIGA_PORT" --fqbn arduino:mbed_giga:giga Arduino/GIGA_UDP_Sender/ --verbose || {
            log_error "Upload fehlgeschlagen. Prüfen Sie die Verbindung."
            exit 1
        }
    fi
else
    log_error "Fehler beim Kompilieren des GIGA Codes"
    exit 1
fi

# 7. ESP32 flashen
log_info "Flashe ESP32..."
log_info "Kompiliere ESP32 Code..."
if arduino-cli compile --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/; then
    log_info "Upload auf ESP32 Port: $ESP32_PORT"
    if arduino-cli upload -p "$ESP32_PORT" --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/; then
        log_success "ESP32 erfolgreich geflasht"
    else
        log_error "Fehler beim Upload auf ESP32"
        log_info "Versuche ESP32 Reset..."
        # ESP32 oft problematisch - retry mit anderen Optionen
        arduino-cli upload -p "$ESP32_PORT" --fqbn esp32:esp32:esp32 Arduino/ESP32_UDP_Receiver/ --verbose || {
            log_error "ESP32 Upload fehlgeschlagen. Versuchen Sie manuellen Reset."
            exit 1
        }
    fi
else
    log_error "Fehler beim Kompilieren des ESP32 Codes"
    exit 1
fi

# 8. Warten bis Geräte bereit sind
log_info "Warte auf Geräte-Initialisierung..."
sleep 5

# 9. GUI starten
log_info "Starte Bertrandt GUI..."
if [ ! -f "Python_GUI/Bertrandt_GUI.py" ]; then
    log_error "Bertrandt_GUI.py nicht gefunden!"
    exit 1
fi

cd Python_GUI
log_info "Starte GUI mit ESP32 Port: $ESP32_PORT"
python3 Bertrandt_GUI.py --esp32-port="$ESP32_PORT" &
GUI_PID=$!

# 10. Kurz warten und prüfen ob GUI läuft
sleep 3
if ! kill -0 $GUI_PID 2>/dev/null; then
    log_error "GUI konnte nicht gestartet werden!"
    log_info "Versuche Fallback mit Test_Gui_01.py..."
    python3 Test_Gui_01.py &
    GUI_PID=$!
fi

# 11. Serial Monitor für Debugging (optional)
log_info "Starte Serial Monitor für ESP32..."
sleep 2
arduino-cli monitor -p "$ESP32_PORT" -c baudrate=115200 &
MONITOR_PID=$!

log_success "System erfolgreich gestartet!"
echo "=================================================="
echo "🎯 Arduino GIGA: $GIGA_PORT"
echo "🎯 ESP32: $ESP32_PORT"
echo "🎯 GUI läuft (PID: $GUI_PID)"
echo "🎯 Serial Monitor aktiv (PID: $MONITOR_PID)"
echo ""
echo "📊 Überwachung:"
echo "   - GUI-Fenster sollte sich öffnen"
echo "   - Serial Monitor zeigt ESP32 Ausgaben"
echo "   - GIGA sendet alle 2 Sekunden Signale 1-10"
echo ""
echo "🛑 Drücken Sie Ctrl+C zum Beenden"

# Warten auf Benutzer-Eingabe oder Prozess-Ende
wait