# 🚀 Deployment Checklist - ML Gruppe Helpdesk

## 📋 Projektstruktur für Server-Upload

Hier ist eine komplette Übersicht aller Ordner und Dateien, die auf deinen Server hochgeladen werden müssen.

---

## 🗂️ Hauptordner (komplett hochladen)

### **Root-Level Ordner**

```
HelpDesk/
├── apps/                          # Django Apps (komplett hochladen)
│   ├── accounts/
│   ├── admin_panel/
│   ├── chat/
│   ├── knowledge/
│   ├── main/
│   ├── tickets/
│   └── api/                        # (optional, wenn REST API genutzt wird)
│
├── helpdesk/                       # Django Hauptkonfiguration (komplett hochladen)
│   ├── settings.py                 # WICHTIG: .env Variablen überprüfen!
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/                      # HTML Templates (komplett hochladen)
│   ├── base.html
│   ├── main/
│   ├── accounts/
│   ├── tickets/
│   ├── knowledge/
│   ├── chat/
│   └── admin/
│
├── static/                         # CSS, JavaScript, Images (komplett hochladen)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
│
├── manage.py                       # Django Management Script (WICHTIG)
│
├── requirements.txt                # Python Dependencies (WICHTIG)
│
├── .env                           # Environment Variables (NUR lokal, NICHT auf Server!)
│
├── .gitignore                     # Git ignore rules
│
├── db.sqlite3                     # SQLite DB (optional, wenn lokal)
│
├── media/                         # Benutzer hochgeladene Dateien
│   ├── logos/
│   └── uploads/
│
└── logs/                          # Anwendungs-Logs (wird automatisch erstellt)
```

---

## ⚙️ Wichtige Konfigurationsdateien

### **MUSS hochgeladen werden:**

| Datei | Beschreibung | Status |
|-------|-------------|--------|
| `manage.py` | Django Management Tool | ✅ KRITISCH |
| `requirements.txt` | Python Dependencies | ✅ KRITISCH |
| `helpdesk/settings.py` | Django Settings | ✅ KRITISCH |
| `helpdesk/urls.py` | URL Routing | ✅ KRITISCH |
| `helpdesk/wsgi.py` | WSGI Application | ✅ KRITISCH |
| `.env.example` | Environment Template | ✅ Empfohlen |
| `.gitignore` | Git Config | ⚠️ Optional |

### **DARF NICHT hochgeladen werden:**

| Datei | Grund |
|-------|-------|
| `.env` | Enthält Secrets/Passwörter |
| `db.sqlite3` | Lokal Datenbank |
| `.git/` | Git Repository |
| `__pycache__/` | Python Cache |
| `.pytest_cache/` | Test Cache |
| `*.pyc` | Kompilierte Python Files |
| `.venv/` oder `venv/` | Virtual Environment |

---

## 🔧 Ordner-Übersicht mit Inhalten

### **1. `apps/` - Django Applikationen**
```
apps/
├── accounts/              # Benutzer & Authentifizierung
│   ├── migrations/        # DB Migrations
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── signals.py
│   ├── middleware.py
│   └── templates/
│
├── admin_panel/           # Admin Settings & Dashboard
│   ├── migrations/        # DB Migrations (inkl. Theme Fields)
│   ├── models.py          # SystemSettings Model
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── signals.py         # Cache Invalidation
│   ├── context_processors.py
│   └── templates/
│
├── tickets/               # Ticket Management System
│   ├── migrations/        # DB Migrations
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│
├── chat/                  # Live Chat Widget
│   ├── migrations/        # DB Migrations
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── context_processors.py
│   └── templates/
│
├── knowledge/             # FAQ & Knowledge Base
│   ├── migrations/        # DB Migrations
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│
├── main/                  # Hauptseite & Settings
│   ├── models.py
│   ├── views.py           # admin_settings view
│   ├── forms.py           # AdminSettingsForm
│   ├── urls.py
│   ├── context_processors.py
│   └── templates/
│
└── api/                   # REST API (optional)
    ├── migrations/
    ├── models.py
    ├── views.py
    ├── serializers.py
    └── urls.py
```

### **2. `helpdesk/` - Konfiguration**
```
helpdesk/
├── settings.py            # WICHTIG: Database, Cache, Email Config
├── urls.py                # URL Routing
├── wsgi.py                # Production Server Entry Point
├── asgi.py                # Async Support (optional)
└── __init__.py
```

### **3. `templates/` - HTML Templates**
```
templates/
├── base.html              # Haupttemplate (inkl. CSS Variablen & Theme)
├── main/
│   ├── admin_settings.html    # Theme & Settings (mit JavaScript)
│   └── dashboard.html
├── accounts/
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── tickets/
│   ├── list.html
│   ├── detail.html
│   └── create.html
├── chat/
│   └── widget.html
├── knowledge/
│   ├── list.html
│   └── detail.html
└── admin/
    └── (Django Admin Templates)
```

### **4. `static/` - Frontend Assets**
```
static/
├── css/
│   ├── theme.css          # Theme System (CSS Variablen)
│   └── style.css
├── js/
│   ├── main.js
│   ├── admin-settings.js
│   └── widgets.js
├── images/
│   ├── logo.png
│   └── ...
└── fonts/
    └── (Custom Fonts wenn vorhanden)
```

### **5. `media/` - Benutzer-Uploads**
```
media/
├── logos/                 # Admin hochgeladene Logos
└── uploads/               # User uploaded Files
```

---

## 📥 Upload-Plan für deinen Server

### **Phase 1: Grundstruktur**
```bash
# FTP/SSH Upload in dieser Reihenfolge:

1. ✅ apps/              # (komplett)
2. ✅ helpdesk/          # (komplett)
3. ✅ templates/         # (komplett)
4. ✅ static/            # (komplett)
5. ✅ manage.py
6. ✅ requirements.txt
```

### **Phase 2: Konfiguration auf dem Server**
```bash
# Am Server ausführen:

1. pip install -r requirements.txt
2. python manage.py collectstatic --noinput
3. python manage.py migrate
4. python manage.py createsuperuser
```

### **Phase 3: Verzeichnisse erstellen**
```bash
# Folgende Ordner müssen existieren:

mkdir -p media/logos
mkdir -p media/uploads
mkdir -p logs
mkdir -p staticfiles
```

---

## 🔐 Environment Variables (.env)

**Datei: `.env` (NUR auf Server, nicht hochladen)**

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-min-50-chars

# Database
DATABASE_URL=postgresql://user:password@localhost/helpdesk
# oder für MySQL:
DATABASE_URL=mysql+pymysql://user:password@localhost/helpdesk
# oder für SQLite:
DATABASE_URL=sqlite:///helpdesk.db

# Email (SMTP)
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993

# Site Configuration
SITE_URL=https://your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Microsoft OAuth (optional)
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id

# Claude AI (optional)
CLAUDE_API_KEY=your-claude-api-key

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Microsoft Teams (optional)
TEAMS_WEBHOOK_URL=https://outlook.webhook.office.com/...

# Sentry (optional)
SENTRY_DSN=https://...

# Localization
LANGUAGE_CODE=de-de
TIMEZONE=Europe/Berlin
```

---

## ✅ Deployment Checklist

### **Vor dem Upload:**
- [ ] Alle `.pyc` Dateien löschen (`find . -type d -name __pycache__ -exec rm -r {} +`)
- [ ] `.env` Datei NICHT hochladen
- [ ] `.git/` Ordner NICHT hochladen
- [ ] `venv/` oder `.venv/` NICHT hochladen
- [ ] `db.sqlite3` NICHT hochladen (wenn du PostgreSQL/MySQL nutzt)

### **Beim Upload:**
- [ ] Alle `apps/` Ordner hochladen
- [ ] `helpdesk/` Ordner hochladen
- [ ] `templates/` Ordner hochladen
- [ ] `static/` Ordner hochladen
- [ ] `manage.py` hochladen
- [ ] `requirements.txt` hochladen
- [ ] `.env.example` hochladen (zur Referenz)

### **Nach dem Upload:**
- [ ] SSH in Server einloggen
- [ ] `pip install -r requirements.txt` ausführen
- [ ] `.env` Datei manuell erstellen mit deinen Werten
- [ ] `python manage.py collectstatic --noinput` ausführen
- [ ] `python manage.py migrate` ausführen
- [ ] Media-Ordner erstellen: `mkdir -p media/logos media/uploads logs staticfiles`
- [ ] Permissions setzen: `chmod 755 -R media logs staticfiles`
- [ ] Web Server konfigurieren (Nginx/Apache)
- [ ] SSL Zertifikat einrichten

---

## 🚀 Schnell-Referenz: Welche Ordner hochladen?

| Ordner | Upload | Grund |
|--------|--------|-------|
| `apps/` | ✅ JA | Django Applikationen |
| `helpdesk/` | ✅ JA | Konfiguration |
| `templates/` | ✅ JA | HTML Templates |
| `static/` | ✅ JA | CSS, JS, Bilder |
| `media/` | ⚠️ OPTIONAL | Nur wenn Dateien vorhanden |
| `logs/` | ❌ NEIN | Wird beim Start erstellt |
| `.venv/` oder `venv/` | ❌ NEIN | Virtual Environment |
| `.git/` | ❌ NEIN | Git Repository |
| `__pycache__/` | ❌ NEIN | Python Cache |
| `.env` | ❌ NEIN | Secrets! |

---

## 📝 Notizen für dich

- **Database Migration**: Nach Upload `python manage.py migrate` ausführen
- **Static Files**: `python manage.py collectstatic` für Production
- **Theme System**: Funktioniert direkt nach Upload - Farben aus Datenbank
- **Logo Upload**: `media/logos/` Ordner muss beschreibbar sein
- **Logs**: `logs/` Ordner muss beschreibbar sein
- **Email**: SMTP Einstellungen in `.env` konfigurieren

---

**Version:** 1.0
**Datum:** November 2025
**Status:** Ready for Production
