# 📤 Upload-Struktur - Was muss auf den Server?

## Kurze Übersicht

```
Hochladen MUSS:
├── apps/                     (gesamter Ordner)
├── helpdesk/                 (gesamter Ordner)
├── templates/                (gesamter Ordner)
├── static/                   (gesamter Ordner)
├── manage.py
└── requirements.txt

Hochladen KANN (optional):
├── media/                    (nur wenn Dateien vorhanden)
└── .env.example              (zur Referenz)

NICHT hochladen:
├── .env                      (nur auf Server erstellen!)
├── .venv/ oder venv/         (wird mit pip install erstellt)
├── .git/                     (nicht nötig)
├── __pycache__/              (wird automatisch erstellt)
├── *.pyc                     (Python Cache)
├── db.sqlite3                (alte lokale DB)
└── logs/                     (wird automatisch erstellt)
```

---

## 🎯 FTP/SSH Upload Befehl

### Option 1: Mit SCP (SSH)
```bash
scp -r apps helpdesk templates static manage.py requirements.txt user@server.com:/path/to/helpdesk/
```

### Option 2: Mit rsync (empfohlen)
```bash
rsync -avz --exclude='.env' --exclude='__pycache__' --exclude='.git' --exclude='venv' --exclude='.venv' --exclude='*.pyc' . user@server.com:/path/to/helpdesk/
```

### Option 3: Mit FTP/SFTP (Filezilla, WinSCP)
Einfach folgende Ordner/Dateien hochladen:
- apps/ ➜ Server
- helpdesk/ ➜ Server
- templates/ ➜ Server
- static/ ➜ Server
- manage.py ➜ Server
- requirements.txt ➜ Server

---

## ✅ Nach dem Upload auf dem Server

```bash
# 1. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. .env Datei erstellen (mit deinen Werten!)
nano .env

# 4. Migrations ausführen
python manage.py migrate

# 5. Static Files sammeln
python manage.py collectstatic --noinput

# 6. Ordner erstellen
mkdir -p media/logos media/uploads logs staticfiles

# 7. Permissions setzen
chmod 755 -R media logs staticfiles
chown www-data:www-data -R media logs staticfiles

# 8. Server starten
python manage.py runserver 0.0.0.0:8000

# Oder mit Gunicorn:
gunicorn helpdesk.wsgi:application --bind 0.0.0.0:8000
```

---

## 📊 Dateigröße Übersicht

Ungefähre Größe der Upload:
- `apps/` : ~500 KB
- `helpdesk/` : ~50 KB
- `templates/` : ~300 KB
- `static/` : ~200 KB
- `manage.py` : ~5 KB
- `requirements.txt` : ~2 KB

**Gesamt: ~1 MB** (sehr klein!)

---

## 🔒 Wichtige Sicherheit

1. **`.env` File NICHT hochladen!**
   - Enthält Passwörter und API Keys
   - Manuell auf dem Server erstellen

2. **`.git/` Ordner NICHT hochladen**
   - Nicht nötig auf Production
   - Unnötige Daten

3. **Virtual Environment NICHT hochladen**
   - `venv/` oder `.venv/`
   - Wird mit `pip install` neu erstellt

4. **Cache/Temp Dateien NICHT hochladen**
   - `__pycache__/`
   - `*.pyc`
   - `.pytest_cache/`

---

Das war's! Viel Erfolg beim Upload! 🚀
