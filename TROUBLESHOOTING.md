# Troubleshooting Guide - Aboro-IT Helpdesk

## 🔴 Fehler: 413 Request Entity Too Large

### Problem
Beim Hochladen von Dateien (Logo, Anhänge, etc.) erscheint der Fehler:
```
413 Request Entity Too Large
```

### Ursachen
Der Fehler tritt auf, wenn die hochgeladene Datei größer ist als eines der konfigurierten Limits:

1. **Nginx `client_max_body_size` zu klein**
2. **Django `FILE_UPLOAD_MAX_MEMORY_SIZE` zu klein**
3. **Django `DATA_UPLOAD_MAX_MEMORY_SIZE` zu klein**
4. **LogoUploadHandler Limit zu klein**

---

## ✅ Lösung: Schritt-für-Schritt

### Schritt 1: Django Settings überprüfen und anpassen

Öffnen Sie `helpdesk/settings.py` und überprüfen Sie folgende Einstellungen:

```python
# Sollte auf mindestens 16MB gesetzt sein (oder höher)
FILE_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
```

**Speichern und fortfahren zu Schritt 2.**

### Schritt 2: Nginx konfigurieren (KRITISCH!)

Dies ist der **häufigste Grund** für den 413-Fehler!

1. SSH zum Server verbinden:
```bash
ssh user@your-server.de
```

2. Nginx-Konfigurationsdatei öffnen:
```bash
sudo nano /etc/nginx/sites-available/helpdesk
```

3. Überprüfen Sie, dass folgende Zeile im `server` Block existiert:
```nginx
server {
    listen 80;
    server_name ihre-domain.de;

    client_max_body_size 16M;  # ← DIESE ZEILE MUSS VORHANDEN SEIN

    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... weitere Einstellungen
    }
}
```

**Falls die Zeile fehlt oder kleiner als 16M ist:**
- Ergänzen oder ändern Sie sie zu `client_max_body_size 16M;`
- Mit `Ctrl+X`, dann `Y` speichern und `Enter` bestätigen

4. Nginx-Konfiguration testen:
```bash
sudo nginx -t
```

Output sollte sein:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration will be successful
```

5. Nginx neustarten:
```bash
sudo systemctl reload nginx
```

### Schritt 3: Django Application neustarten

Je nach Deployment-Methode:

**Wenn Sie systemd verwenden:**
```bash
sudo systemctl restart helpdesk
```

**Wenn Sie Gunicorn direkt verwenden:**
```bash
# Kill den Prozess
pkill -f gunicorn

# Starten Sie es neu
gunicorn --timeout 120 helpdesk.wsgi:application &
```

### Schritt 4: Logo-Upload testen

1. Gehen Sie zu https://ihre-domain.de/settings/
2. Scrollen Sie zum "Branding & Erscheinungsbild" Abschnitt
3. Versuchen Sie, ein Logo hochzuladen
4. Wenn es funktioniert, ist das Problem gelöst! ✅

---

## 🔍 Debugging

Falls das Problem noch besteht, führen Sie folgende Schritte durch:

### 1. Aktuelle Nginx-Konfiguration überprüfen
```bash
sudo nginx -T | grep client_max_body_size
```

Output sollte zeigen:
```
client_max_body_size 16M;
```

Falls nicht, wiederholen Sie **Schritt 2**.

### 2. Django Settings überprüfen
```bash
cd /path/to/helpdesk
python manage.py shell
```

Dann in der Python-Shell:
```python
from django.conf import settings
print(f"FILE_UPLOAD_MAX_MEMORY_SIZE: {settings.FILE_UPLOAD_MAX_MEMORY_SIZE}")
print(f"DATA_UPLOAD_MAX_MEMORY_SIZE: {settings.DATA_UPLOAD_MAX_MEMORY_SIZE}")
```

Sollte zeigen:
```
FILE_UPLOAD_MAX_MEMORY_SIZE: 16777216
DATA_UPLOAD_MAX_MEMORY_SIZE: 16777216
```

### 3. Nginx-Error-Log überprüfen
```bash
sudo tail -f /var/log/nginx/error.log
```

Versuchen Sie den Upload erneut und schauen Sie auf neue Fehler im Log.

### 4. Django-Error-Log überprüfen
```bash
# Falls systemd
sudo journalctl -u helpdesk -f

# Falls manueller Start
# Schauen Sie in die Console-Ausgabe
```

---

## 🎯 Häufige Szenarien

### Szenario 1: Logo ist größer als 16MB
**Lösung**: Komprimieren Sie das Logo auf < 16MB
- Mit Online-Tools wie https://imageoptimizer.net/
- Oder lokal: `convert input.png -quality 85 output.png`

### Szenario 2: Mehrere große Anhänge auf einmal
**Lösung**: Upload-Limit in Django Settings erhöhen:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024  # 32MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024  # 32MB
```

Dann Nginx aktualisieren:
```nginx
client_max_body_size 32M;
```

### Szenario 3: Nginx in Docker Container
Falls Sie Docker verwenden, passen Sie die Nginx-Konfiguration in der `docker-compose.yml` an:
```yaml
services:
  nginx:
    environment:
      - NGINX_CLIENT_MAX_BODY_SIZE=16M
```

---

## 📊 Empfohlene Limits

| Szenario | FILE_UPLOAD_MAX_MEMORY_SIZE | Nginx client_max_body_size |
|----------|------------------------------|---------------------------|
| Standard | 16MB | 16M |
| Mit großen Anhängen | 32MB | 32M |
| Mit sehr großen Dateien | 64MB | 64M |
| Datei-Sammlung | 128MB | 128M |

---

## 🆘 Falls alles fehlschlägt

1. **Neustarten Sie den Server:**
```bash
sudo reboot
```

2. **Überprüfen Sie alle Logs:**
```bash
sudo journalctl -u helpdesk -n 50
sudo tail -f /var/log/nginx/error.log
```

3. **Kontaktieren Sie Support**: support@ml-gruppe.de

---

## 💡 Best Practices

1. **Immer Nginx testen nach Änderungen:**
   ```bash
   sudo nginx -t
   ```

2. **Limits konsistent halten:**
   - Django-Settings = Nginx client_max_body_size

3. **Große Dateien komprimieren:**
   - Logo sollte < 5MB sein (optimiert für Web)
   - Anhänge sollten < 10MB sein

4. **Monitoring einrichten:**
   ```bash
   # Überwachen Sie große Uploads
   sudo tail -f /var/log/nginx/access.log | grep 413
   ```

---

## 📋 Checkliste zur Behebung

- [ ] Django FILE_UPLOAD_MAX_MEMORY_SIZE >= 16MB
- [ ] Django DATA_UPLOAD_MAX_MEMORY_SIZE >= 16MB
- [ ] Nginx client_max_body_size >= 16M
- [ ] Nginx Konfiguration mit `sudo nginx -t` überprüft
- [ ] Nginx mit `sudo systemctl reload nginx` neu geladen
- [ ] Django Application neu gestartet
- [ ] Test-Upload durchgeführt

---

Wenn Sie nach dieser Anleitung immer noch Probleme haben, lesen Sie die Hauptdokumentation in [README.md](README.md) oder kontaktieren Sie den Support.
