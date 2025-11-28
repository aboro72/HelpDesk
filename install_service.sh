#!/bin/bash
#
# Installations-Script für HelpDesk Systemd Service
#

set -e

echo "=========================================="
echo "HelpDesk Service Installation"
echo "=========================================="
echo ""

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then
    echo "Bitte als root ausführen (mit sudo)"
    exit 1
fi

PROJECT_DIR="/home/user/PycharmProjects/HelpDesk"

# Kopiere Service-Datei
echo "[1/5] Kopiere Service-Datei nach /etc/systemd/system/..."
cp "$PROJECT_DIR/helpdesk.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/helpdesk.service

# Systemd neu laden
echo "[2/5] Lade systemd-Daemon neu..."
systemctl daemon-reload

# Service aktivieren
echo "[3/5] Aktiviere helpdesk Service..."
systemctl enable helpdesk.service

# Stelle sicher, dass logs-Verzeichnis existiert
echo "[4/5] Erstelle logs-Verzeichnis..."
mkdir -p "$PROJECT_DIR/logs"
chown user:user "$PROJECT_DIR/logs"

# Sammle statische Dateien
echo "[5/5] Sammle statische Dateien..."
cd "$PROJECT_DIR"
sudo -u user .venv/bin/python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "Installation abgeschlossen!"
echo "=========================================="
echo ""
echo "Service-Befehle:"
echo "  sudo systemctl start helpdesk    - Service starten"
echo "  sudo systemctl stop helpdesk     - Service stoppen"
echo "  sudo systemctl restart helpdesk  - Service neu starten"
echo "  sudo systemctl status helpdesk   - Service-Status anzeigen"
echo "  journalctl -u helpdesk -f        - Live-Logs anzeigen"
echo ""
echo "WICHTIG:"
echo "  1. Passen Sie die .env Datei an (SECRET_KEY, ALLOWED_HOSTS, etc.)"
echo "  2. Konfigurieren Sie ISPConfig3 als Reverse Proxy (siehe DEPLOYMENT.md)"
echo "  3. Starten Sie den Service: sudo systemctl start helpdesk"
echo ""
