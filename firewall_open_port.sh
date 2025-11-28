#!/bin/bash
#
# Öffnet Port 8000 in der Firewall für den Zugriff vom ISPConfig3-Server
#

set -e

echo "=========================================="
echo "Firewall-Konfiguration für Port 8000"
echo "=========================================="
echo ""

# Prüfe ob iptables existiert
if ! command -v iptables &> /dev/null; then
    echo "FEHLER: iptables nicht gefunden"
    exit 1
fi

echo "Öffne Port 8000 für Zugriffe vom lokalen Netzwerk..."
echo ""

# Erlaube Port 8000 von ISPConfig3 Server (192.168.0.20)
echo "[1/4] Erlaube Zugriff von 192.168.0.20..."
iptables -I INPUT -p tcp --dport 8000 -s 192.168.0.20 -j ACCEPT

# Erlaube Port 8000 vom gesamten lokalen Netzwerk (optional)
echo "[2/4] Erlaube Zugriff vom lokalen Netzwerk (192.168.0.0/24)..."
iptables -I INPUT -p tcp --dport 8000 -s 192.168.0.0/24 -j ACCEPT

# Zeige aktuelle Regeln
echo "[3/4] Aktuelle iptables-Regeln für Port 8000:"
iptables -L INPUT -n | grep 8000

# Speichere Regeln (falls iptables-persistent installiert ist)
echo "[4/4] Versuche Regeln zu speichern..."
if command -v netfilter-persistent &> /dev/null; then
    netfilter-persistent save
    echo "Regeln mit netfilter-persistent gespeichert"
elif command -v iptables-save &> /dev/null; then
    iptables-save > /etc/iptables/rules.v4 2>/dev/null && echo "Regeln gespeichert" || echo "WARNUNG: Konnte Regeln nicht speichern - werden nach Neustart verloren gehen"
else
    echo "WARNUNG: Keine Möglichkeit gefunden, Regeln dauerhaft zu speichern"
    echo "Regeln gehen nach Neustart verloren!"
fi

echo ""
echo "=========================================="
echo "Firewall-Konfiguration abgeschlossen!"
echo "=========================================="
echo ""
echo "Port 8000 ist jetzt geöffnet für:"
echo "  - ISPConfig3 Server (192.168.0.20)"
echo "  - Lokales Netzwerk (192.168.0.0/24)"
echo ""
echo "Testen Sie jetzt den Zugriff mit:"
echo "  http://192.168.0.211:8000"
echo ""
