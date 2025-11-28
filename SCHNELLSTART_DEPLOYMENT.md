# HelpDesk Deployment - Schnellstart für Apache2

## Übersicht

Diese Anleitung führt Sie durch die schnelle Einrichtung des HelpDesk Systems mit systemd und ISPConfig3 Apache2 als Reverse Proxy.

## Voraussetzungen

- Linux-Server (Ubuntu/Debian empfohlen)
- ISPConfig3 mit Apache2 auf 192.168.0.20 installiert
- Domain zeigt auf ISPConfig3-Server
- Python 3.10+ und Virtual Environment bereits eingerichtet
- Git-Repository bereits geklont

## Schnellstart (6 Schritte)

### Schritt 1: .env-Datei anpassen

```bash
cd /home/user/PycharmProjects/HelpDesk
nano .env
```

**Mindestens diese Werte ändern:**
```env
DEBUG=False
SECRET_KEY=IHR-SICHERER-GEHEIMER-SCHLUESSEL-HIER
ALLOWED_HOSTS=localhost,127.0.0.1,help.aboro-it.net,192.168.0.20
SITE_URL=https://help.aboro-it.net
```

**Tipp:** Secret Key generieren mit:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Schritt 2: Service installieren

```bash
sudo ./install_service.sh
```

Das Script:
- Installiert den systemd Service
- Aktiviert automatischen Start
- Sammelt statische Dateien
- Erstellt Log-Verzeichnisse

### Schritt 3: Service starten

```bash
# Service starten
sudo systemctl start helpdesk

# Status prüfen
sudo systemctl status helpdesk

# Bei Problemen: Logs anzeigen
journalctl -u helpdesk -f
```

### Schritt 4: Apache-Module aktivieren (auf ISPConfig3 Server)

**Wichtig:** Dies muss auf dem ISPConfig3-Server (192.168.0.20) ausgeführt werden!

```bash
# SSH auf ISPConfig3 Server
ssh root@192.168.0.20

# Apache Proxy-Module aktivieren
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod ssl
sudo a2enmod rewrite

# Apache neu starten
sudo systemctl restart apache2
```

### Schritt 5: ISPConfig3 Reverse Proxy konfigurieren

1. **ISPConfig3 öffnen:** https://192.168.0.20:8080

2. **Website erstellen:**
   - Websites → Website → Add new website
   - Domain: help.aboro-it.net
   - IPv4: 192.168.0.20
   - SSL: Let's Encrypt aktivieren
   - PHP: Deaktiviert (nicht benötigt)

3. **Apache Directives hinzufügen** (Options → Apache Directives):

```apache
# Reverse Proxy zu Django
ProxyPreserveHost On
ProxyRequests Off

# Header für Proxy
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-Port "443"

# Proxy zu Gunicorn
ProxyPass /static/ !
ProxyPass /media/ !
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/

# Statische Dateien direkt von Apache ausliefern
Alias /static /home/user/PycharmProjects/HelpDesk/staticfiles
<Directory /home/user/PycharmProjects/HelpDesk/staticfiles>
    Require all granted
    Options -Indexes +FollowSymLinks
    AllowOverride None

    <FilesMatch "\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$">
        Header set Cache-Control "public, max-age=2592000"
    </FilesMatch>
</Directory>

# Media-Dateien
Alias /media /home/user/PycharmProjects/HelpDesk/media
<Directory /home/user/PycharmProjects/HelpDesk/media>
    Require all granted
    Options -Indexes +FollowSymLinks
    AllowOverride None

    Header set Cache-Control "public, max-age=604800"
</Directory>
```

4. **HTTPS erzwingen** (in ISPConfig3):
   - Redirect Type: L (Permanent)
   - Rewrite HTTP to HTTPS: Aktivieren

5. **Speichern** - ISPConfig3 erstellt automatisch SSL-Zertifikat

### Schritt 6: Berechtigungen setzen

```bash
# Damit Apache auf Dateien zugreifen kann
chmod 755 /home/user
chmod 755 /home/user/PycharmProjects
chmod 755 /home/user/PycharmProjects/HelpDesk
chmod -R 755 /home/user/PycharmProjects/HelpDesk/staticfiles
chmod -R 755 /home/user/PycharmProjects/HelpDesk/media
```

## Fertig!

Ihr HelpDesk sollte jetzt unter https://help.aboro-it.net erreichbar sein.

## Falls Django auf ANDEREM Server läuft

Wenn Django **nicht** auf 192.168.0.20 läuft, sondern auf einem separaten Server:

### 1. Gunicorn-Config anpassen

Auf dem Django-Server in `gunicorn_config.py`:

```python
# Statt 127.0.0.1, auf alle Interfaces binden (oder spezifische IP)
bind = "0.0.0.0:8000"
```

### 2. Firewall auf Django-Server öffnen

```bash
# Zugriff von ISPConfig3 erlauben
sudo ufw allow from 192.168.0.20 to any port 8000
```

### 3. Apache Directives anpassen

In ISPConfig3, ersetze `127.0.0.1` mit der IP des Django-Servers:

```apache
ProxyPass / http://IP_DES_DJANGO_SERVERS:8000/
ProxyPassReverse / http://IP_DES_DJANGO_SERVERS:8000/
```

### 4. Static/Media-Files

Bei separaten Servern müssen die Dateien erreichbar sein:

**Option A:** NFS/SSHFS Mount
```bash
# Auf ISPConfig3 Server
sudo sshfs user@django-server:/home/user/PycharmProjects/HelpDesk/staticfiles \
  /home/user/PycharmProjects/HelpDesk/staticfiles
```

**Option B:** Über Django ausliefern (weniger performant)
```apache
# In Apache Directives - KEIN Alias verwenden
ProxyPass / http://IP_DES_DJANGO_SERVERS:8000/
ProxyPassReverse / http://IP_DES_DJANGO_SERVERS:8000/
# Static/Media werden dann von Gunicorn/Django ausgeliefert
```

## Nützliche Befehle

### Django-Server

```bash
# Service neu starten (nach Code-Updates)
sudo systemctl restart helpdesk

# Logs live anzeigen
journalctl -u helpdesk -f

# Service-Status prüfen
sudo systemctl status helpdesk

# Ist Port 8000 offen?
netstat -tlnp | grep 8000
```

### ISPConfig3/Apache-Server

```bash
# Apache-Logs prüfen
tail -f /var/log/apache2/error.log

# Apache-Konfiguration testen
sudo apache2ctl configtest

# Apache neu laden
sudo systemctl reload apache2

# Proxy-Module prüfen
apache2ctl -M | grep proxy
```

## Nach Code-Updates

```bash
# 1. Code aktualisieren
cd /home/user/PycharmProjects/HelpDesk
git pull

# 2. Dependencies installieren
.venv/bin/pip install -r requirements.txt

# 3. Migrations
.venv/bin/python manage.py migrate

# 4. Statische Dateien sammeln
.venv/bin/python manage.py collectstatic --noinput

# 5. Service neu starten
sudo systemctl restart helpdesk
```

## Troubleshooting

### Apache-Module fehlen (AH01144 Error)

```bash
# Auf ISPConfig3 Server
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo systemctl restart apache2
```

### 502 Bad Gateway

**Django-Server prüfen:**
```bash
sudo systemctl status helpdesk
journalctl -u helpdesk -n 50
netstat -tlnp | grep 8000
```

**Apache-Server prüfen:**
```bash
tail -f /var/log/apache2/error.log
curl http://127.0.0.1:8000  # Oder IP des Django-Servers
```

### Statische Dateien fehlen (404)

```bash
# Neu sammeln
.venv/bin/python manage.py collectstatic --noinput

# Berechtigungen prüfen
ls -la staticfiles/

# Apache-Config prüfen
sudo apache2ctl configtest
```

### Permission Denied (403)

```bash
# Home-Verzeichnis lesbar machen
chmod 755 /home/user /home/user/PycharmProjects /home/user/PycharmProjects/HelpDesk

# Static/Media lesbar machen
chmod -R 755 staticfiles media

# Apache Error-Log prüfen
tail -f /var/log/apache2/error.log
```

### Service startet nicht

```bash
# Detaillierte Fehler
journalctl -u helpdesk -n 100

# Manuell testen
cd /home/user/PycharmProjects/HelpDesk
.venv/bin/gunicorn --config gunicorn_config.py helpdesk.wsgi:application
```

### Django auf separatem Server - Keine Verbindung

```bash
# Auf Django-Server: Firewall prüfen
sudo ufw status
sudo ufw allow from 192.168.0.20 to any port 8000

# Auf ISPConfig3-Server: Verbindung testen
telnet IP_DES_DJANGO_SERVERS 8000
# oder
curl http://IP_DES_DJANGO_SERVERS:8000
```

## Wichtige Hinweise

### Sicherheit

- [ ] `DEBUG=False` in `.env`
- [ ] Starker `SECRET_KEY` (nicht Default!)
- [ ] `ALLOWED_HOSTS` korrekt
- [ ] SSL/HTTPS aktiviert
- [ ] Firewall: Nur 80/443 auf ISPConfig3 offen
- [ ] Django auf localhost (oder nur private IP wenn separater Server)

### Performance

- Worker-Anzahl in `gunicorn_config.py` anpassen
- Redis für Caching aktivieren (optional)
- Apache-Caching für Static-Files nutzen

### Monitoring

```bash
# Service-Status
sudo systemctl status helpdesk

# Live-Logs
journalctl -u helpdesk -f

# Apache-Logs
tail -f /var/log/apache2/error.log
tail -f /var/log/ispconfig/httpd/help.aboro-it.net/error.log
```

## Weitere Dokumentation

Detaillierte Informationen in: **DEPLOYMENT.md**

- Erweiterte Konfiguration
- Performance-Optimierung
- Backup-Strategien
- Sicherheits-Checkliste
- Troubleshooting-Guide

## Support

Bei Problemen:
1. `journalctl -u helpdesk -f` - Django-Logs
2. `tail -f /var/log/apache2/error.log` - Apache-Logs
3. `sudo systemctl status helpdesk` - Service-Status
4. `sudo apache2ctl configtest` - Apache-Config testen
