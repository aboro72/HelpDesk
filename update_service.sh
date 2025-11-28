#!/bin/bash
#
# Update Script für HelpDesk Service
#

set -e

echo "Aktualisiere HelpDesk Service..."

# Service-Datei kopieren
echo "[1/3] Kopiere Service-Datei..."
cp /home/user/PycharmProjects/HelpDesk/helpdesk.service /etc/systemd/system/

# Systemd neu laden
echo "[2/3] Lade systemd neu..."
systemctl daemon-reload

# Service neu starten
echo "[3/3] Starte Service neu..."
systemctl restart helpdesk

echo ""
echo "Service aktualisiert und neu gestartet!"
echo ""
echo "Status prüfen mit: systemctl status helpdesk"
