# HelpDesk Deployment Guide

## Übersicht

Dieses Dokument beschreibt die Deployment-Schritte für das ML Gruppe HelpDesk System mit:
- Systemd Service für automatischen Start
- Gunicorn als WSGI-Server
- ISPConfig3 (192.168.0.20) mit Apache2 als Reverse Proxy

## Architektur

```
Internet
   ↓
ISPConfig3 Apache2 (192.168.0.20)
   ↓ (Reverse Proxy)
Gunicorn (127.0.0.1:8000)
   ↓
Django HelpDesk
```

## 1. Systemd Service Installation

### 1.1 Installation durchführen

Führen Sie das Installations-Script mit sudo-Rechten aus:

```bash
cd /home/user/PycharmProjects/HelpDesk
sudo ./install_service.sh
```

Das Script führt folgende Schritte aus:
- Kopiert die Service-Datei nach `/etc/systemd/system/`
- Lädt systemd neu
- Aktiviert den Service für automatischen Start
- Erstellt das logs-Verzeichnis
- Sammelt statische Dateien

### 1.2 Konfiguration anpassen

**Wichtig:** Passen Sie die `.env` Datei an:

```bash
nano /home/user/PycharmProjects/HelpDesk/.env
```

Mindestens folgende Werte ändern:
- `SECRET_KEY` - Neuen zufälligen Secret Key generieren
- `ALLOWED_HOSTS` - Domain(s) hinzufügen
- `DEBUG=False` - In Production auf False setzen
- `DATABASE_URL` - Bei Bedarf auf MySQL umstellen

### 1.3 Service starten

```bash
# Service starten
sudo systemctl start helpdesk

# Service-Status prüfen
sudo systemctl status helpdesk

# Live-Logs anzeigen
journalctl -u helpdesk -f
```

### 1.4 Service-Befehle

```bash
# Service starten
sudo systemctl start helpdesk

# Service stoppen
sudo systemctl stop helpdesk

# Service neu starten
sudo systemctl restart helpdesk

# Service-Status anzeigen
sudo systemctl status helpdesk

# Service aktivieren (automatischer Start)
sudo systemctl enable helpdesk

# Service deaktivieren
sudo systemctl disable helpdesk

# Logs anzeigen
journalctl -u helpdesk -f

# Logs der letzten 100 Zeilen
journalctl -u helpdesk -n 100
```

## 2. ISPConfig3 Apache2 Reverse Proxy Konfiguration

### 2.1 Apache Module aktivieren (auf ISPConfig3 Server)

Stellen Sie sicher, dass die notwendigen Apache-Module aktiviert sind:

```bash
# Auf dem ISPConfig3 Server (192.168.0.20)
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod ssl
sudo a2enmod rewrite
sudo systemctl restart apache2
```

### 2.2 Website in ISPConfig3 erstellen

1. Melden Sie sich bei ISPConfig3 an: `https://192.168.0.20:8080`

2. Navigieren Sie zu: **Websites** → **Website**

3. Klicken Sie auf **Add new website**

4. Füllen Sie die Grundeinstellungen aus:
   - **Domain:** help.aboro-it.net (oder Ihre Domain)
   - **IPv4-Adresse:** 192.168.0.20
   - **Auto-Subdomain:** www
   - **PHP:** Deaktiviert (nicht benötigt für Reverse Proxy)
   - **SSL:** Aktiviert (Let's Encrypt)

### 2.3 Apache Directives für Reverse Proxy

Fügen Sie in ISPConfig3 unter **Options** → **Apache Directives** folgende Konfiguration ein:

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

    # Cache-Header für statische Dateien
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

    # Cache-Header für Media-Dateien
    Header set Cache-Control "public, max-age=604800"
</Directory>

# Websocket-Support (falls Django Channels verwendet wird)
RewriteEngine On
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteCond %{HTTP:Connection} upgrade [NC]
RewriteRule ^/?(.*) "ws://127.0.0.1:8000/$1" [P,L]
```

### 2.4 SSL-Konfiguration (für HTTPS vHost)

Falls Sie separate Directives für den SSL vHost benötigen, fügen Sie unter **Options** → **Apache Directives (SSL)** ein:

```apache
# HTTPS-spezifische Einstellungen
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"

# Reverse Proxy zu Django
ProxyPreserveHost On
ProxyRequests Off

# Header für HTTPS
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-Port "443"

# Proxy zu Gunicorn
ProxyPass /static/ !
ProxyPass /media/ !
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/

# Statische Dateien
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

### 2.5 Dateiberechtigungen setzen

Damit ISPConfig3/Apache auf die statischen Dateien zugreifen kann:

```bash
# Berechtigungen für staticfiles setzen
chmod -R 755 /home/user/PycharmProjects/HelpDesk/staticfiles

# Berechtigungen für media setzen
chmod -R 755 /home/user/PycharmProjects/HelpDesk/media

# Stelle sicher, dass das home-Verzeichnis lesbar ist
chmod 755 /home/user
chmod 755 /home/user/PycharmProjects
chmod 755 /home/user/PycharmProjects/HelpDesk

# Apache-User (www-data) muss Zugriff haben
# Prüfen Sie den Apache-User in ISPConfig3
ls -la /home/user/PycharmProjects/HelpDesk/staticfiles
```

### 2.6 Apache neu laden

Nach dem Speichern der Website-Konfiguration in ISPConfig3 wird Apache automatisch neu geladen.

Falls nötig, können Sie Apache manuell neu laden (auf ISPConfig3 Server):

```bash
sudo systemctl reload apache2
# oder
sudo systemctl restart apache2
```

## 3. Let's Encrypt SSL-Zertifikat

### 3.1 SSL in ISPConfig3 aktivieren

1. In der Website-Konfiguration: **SSL** → **Let's Encrypt SSL** aktivieren
2. **Let's Encrypt** Checkbox aktivieren
3. Speichern

ISPConfig3 generiert automatisch das SSL-Zertifikat mit certbot.

### 3.2 HTTPS erzwingen

In ISPConfig3:
- **Redirect Type:** L (Permanent Redirect)
- **SEO Redirect:** www to domain oder domain to www (nach Bedarf)
- **Rewrite HTTP to HTTPS:** Aktivieren

Oder manuell in den Apache Directives:

```apache
# HTTP zu HTTPS umleiten (nur im HTTP vHost)
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
```

## 4. Firewall-Einstellungen

Stellen Sie sicher, dass die Firewall korrekt konfiguriert ist:

```bash
# HTTP und HTTPS erlauben (auf ISPConfig3 Server)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Django läuft auf localhost:8000 - KEIN externer Zugriff nötig
# Port 8000 sollte NICHT von außen erreichbar sein
```

## 5. Verbindung zwischen Servern

Falls Django auf einem **anderen Server** läuft als ISPConfig3:

### 5.1 Firewall auf Django-Server

```bash
# Erlaube Zugriff von ISPConfig3-Server
sudo ufw allow from 192.168.0.20 to any port 8000
```

### 5.2 Gunicorn auf richtige IP binden

In `gunicorn_config.py`:

```python
# Wenn auf separatem Server, binde auf private IP
bind = "0.0.0.0:8000"  # ODER spezifische IP des Django-Servers
```

### 5.3 Apache Proxy anpassen

In ISPConfig3 Apache Directives:

```apache
# Ersetze 127.0.0.1 mit der IP des Django-Servers
ProxyPass / http://IP_DES_DJANGO_SERVERS:8000/
ProxyPassReverse / http://IP_DES_DJANGO_SERVERS:8000/
```

**WICHTIG:** Static/Media-Files müssen dann über NFS/SSHFS gemountet oder separat synchronisiert werden!

## 6. Systemüberwachung

### 6.1 Service-Status überwachen

```bash
# Status prüfen
sudo systemctl status helpdesk

# Ist der Service aktiv?
systemctl is-active helpdesk

# Ist der Service beim Boot aktiviert?
systemctl is-enabled helpdesk
```

### 6.2 Logs überwachen

```bash
# Alle Logs anzeigen
journalctl -u helpdesk

# Nur Fehler anzeigen
journalctl -u helpdesk -p err

# Logs seit heute
journalctl -u helpdesk --since today

# Live-Logs
journalctl -u helpdesk -f
```

### 6.3 Gunicorn-Logs

Zusätzlich zu den systemd-Logs schreibt Gunicorn in eigene Log-Dateien:

```bash
# Access-Log
tail -f /home/user/PycharmProjects/HelpDesk/logs/gunicorn_access.log

# Error-Log
tail -f /home/user/PycharmProjects/HelpDesk/logs/gunicorn_error.log
```

### 6.4 Apache-Logs (auf ISPConfig3 Server)

```bash
# Apache Error-Log
tail -f /var/log/apache2/error.log

# Apache Access-Log
tail -f /var/log/apache2/access.log

# ISPConfig Website-spezifische Logs
tail -f /var/log/ispconfig/httpd/help.aboro-it.net/error.log
tail -f /var/log/ispconfig/httpd/help.aboro-it.net/access.log
```

## 7. Wartung und Updates

### 7.1 Code-Updates deployen

```bash
cd /home/user/PycharmProjects/HelpDesk

# Code aktualisieren (z.B. via Git)
git pull

# Dependencies aktualisieren (falls nötig)
.venv/bin/pip install -r requirements.txt

# Migrations durchführen
.venv/bin/python manage.py migrate

# Statische Dateien sammeln
.venv/bin/python manage.py collectstatic --noinput

# Service neu starten
sudo systemctl restart helpdesk
```

### 7.2 Datenbank-Backup

```bash
# SQLite-Backup
cp /home/user/PycharmProjects/HelpDesk/helpdesk.db \
   /home/user/PycharmProjects/HelpDesk/backups/helpdesk_$(date +%Y%m%d_%H%M%S).db

# MySQL-Backup (falls MySQL verwendet wird)
mysqldump -u username -p helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 7.3 Performance-Optimierung

Die Gunicorn-Konfiguration (`gunicorn_config.py`) ist bereits optimiert:
- Worker-Anzahl basiert auf CPU-Kerne
- Preload-App für bessere Performance
- Auto-Restart der Worker nach 1000 Requests

Für weitere Optimierung:
- Redis für Session-Storage und Caching aktivieren
- Apache-Caching für statische Inhalte
- CDN für statische Dateien verwenden

## 8. Troubleshooting

### Service startet nicht

```bash
# Status und Fehler prüfen
sudo systemctl status helpdesk -l

# Logs prüfen
journalctl -u helpdesk -n 50

# Manuell starten für detaillierte Fehler
cd /home/user/PycharmProjects/HelpDesk
.venv/bin/gunicorn --config gunicorn_config.py helpdesk.wsgi:application
```

### 502 Bad Gateway / Proxy Error

**Auf Django-Server:**
- Prüfen Sie, ob der Gunicorn-Service läuft: `sudo systemctl status helpdesk`
- Prüfen Sie die Gunicorn-Logs: `tail -f logs/gunicorn_error.log`
- Prüfen Sie, ob Port 8000 offen ist: `netstat -tlnp | grep 8000`

**Auf ISPConfig3/Apache-Server:**
- Apache-Logs prüfen: `tail -f /var/log/apache2/error.log`
- Apache-Module aktiv?: `apache2ctl -M | grep proxy`
- Verbindung testen: `curl http://127.0.0.1:8000` (oder IP des Django-Servers)

### Statische Dateien werden nicht geladen

```bash
# Statische Dateien neu sammeln
.venv/bin/python manage.py collectstatic --noinput

# Berechtigungen prüfen
ls -la /home/user/PycharmProjects/HelpDesk/staticfiles

# Apache-Konfiguration testen (auf ISPConfig3 Server)
sudo apache2ctl configtest
```

### Permission Denied (403 Forbidden)

```bash
# Home-Verzeichnis lesbar machen
chmod 755 /home/user
chmod 755 /home/user/PycharmProjects
chmod 755 /home/user/PycharmProjects/HelpDesk

# Static/Media-Verzeichnisse
chmod -R 755 /home/user/PycharmProjects/HelpDesk/staticfiles
chmod -R 755 /home/user/PycharmProjects/HelpDesk/media

# Apache-Logs für Details prüfen
tail -f /var/log/apache2/error.log
```

### AH01144: No protocol handler was valid

Apache Proxy-Module fehlen:

```bash
# Auf ISPConfig3 Server
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
```

## 9. Sicherheits-Checkliste

- [ ] `DEBUG=False` in `.env`
- [ ] `SECRET_KEY` geändert (nicht den Default-Wert verwenden)
- [ ] `ALLOWED_HOSTS` korrekt konfiguriert
- [ ] SSL/HTTPS aktiviert
- [ ] Firewall konfiguriert (nur 80/443 offen auf ISPConfig3)
- [ ] Django läuft nur auf localhost oder private IP (nicht öffentlich)
- [ ] Apache Proxy-Module aktiviert
- [ ] Regelmäßige Backups eingerichtet
- [ ] Logs werden überwacht
- [ ] Updates regelmäßig eingespielt

## 10. Nützliche Links

- **Django-Admin:** https://help.aboro-it.net/admin/
- **ISPConfig3:** https://192.168.0.20:8080
- **Gunicorn-Docs:** https://docs.gunicorn.org/
- **Apache-Docs:** https://httpd.apache.org/docs/

## Support

Bei Problemen:
1. Prüfen Sie die Logs: `journalctl -u helpdesk -f`
2. Prüfen Sie den Service-Status: `sudo systemctl status helpdesk`
3. Prüfen Sie Apache-Logs: `tail -f /var/log/apache2/error.log`
4. Testen Sie die Apache-Konfiguration: `sudo apache2ctl configtest`
