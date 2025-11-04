# 🚀 Quick Reference - Logo Update System

## 🎯 Wichtigste Dateien

```
helpdesk/settings.py
├─ CACHES Configuration (Redis/LocMem)
├─ CACHE_TIMEOUT = 300
└─ context_processors (admin_settings_context)

apps/admin_panel/
├─ context_processors.py (Cache + Logo-Abruf)
├─ signals.py (Cache-Invalidation)
├─ apps.py (Signal Registration)
└─ models.py (SystemSettings.logo)

templates/
├─ base.html (Navbar Logo-Anzeige)
└─ main/admin_settings.html (Auto-Reload Script)
```

---

## 📋 Ablauf beim Logo-Upload

```
POST /settings/ mit Logo-Datei
  ↓
AdminSettingsForm.save()
  ↓
SystemSettings.logo = [Datei] + save()
  ↓
Signal: post_save(SystemSettings)
  ↓
cache.delete('admin_system_settings')
  ↓
Erfolgsmeldung: "erfolgreich"
  ↓
JavaScript: setTimeout(location.reload(), 2000)
  ↓
admin_settings_context() lädt neue Daten aus DB
  ↓
Template rendert mit admin_logo_url
  ↓
<img src="{{ admin_logo_url }}"> zeigt neues Logo
```

---

## 🔧 Commands für Debugging

```bash
# Cache manuell löschen
python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete('admin_system_settings')

# Cache-Inhalt prüfen
>>> cache.get('admin_system_settings')

# Alle Cache-Keys auflisten
>>> cache.keys('*')

# Signal-Test
>>> from apps.admin_panel import signals
>>> print("Signals loaded")

# SystemSettings ansehen
>>> from apps.admin_panel.models import SystemSettings
>>> s = SystemSettings.get_settings()
>>> print(s.logo.url)
```

---

## 🆘 Quick Fixes

| Problem | Lösung |
|---------|--------|
| Logo wird nicht angezeigt | `cache.delete('admin_system_settings')` |
| Seite reloaded nicht | Prüfen Sie Erfolgsmeldung und Browser-Console (F12) |
| Signal wird nicht ausgelöst | Django neu starten: `systemctl restart helpdesk` |
| Cache funktioniert nicht | Redis-Status: `redis-cli ping` sollte PONG zurückgeben |
| Media-Dateien nicht erreichbar | Überprüfen Sie MEDIA_ROOT Permissions: `ls -la media/` |

---

## 📊 Cache-Statistik

- **Cache-Key:** `admin_system_settings`
- **Timeout:** 300 Sekunden (5 Minuten)
- **Invalidation:** Automatisch bei SystemSettings Save
- **Backend:** Redis (oder LocMem als Fallback)

---

## ✨ Features

| Feature | Status |
|---------|--------|
| Logo hochladen | ✅ Funktioniert |
| In Datenbank speichern | ✅ Funktioniert |
| Cache mit Invalidation | ✅ Funktioniert |
| Auto-Reload nach Save | ✅ Funktioniert |
| Navbar-Update | ✅ Funktioniert |
| Fallback zu statischer URL | ✅ Funktioniert |

---

## 🚀 Production Checklist

- [ ] Django-Redis installiert: `pip install django-redis`
- [ ] Redis läuft: `redis-cli ping` → PONG
- [ ] REDIS_URL in .env gesetzt
- [ ] Media-Verzeichnis existiert: `mkdir -p media/logos/`
- [ ] Permissions korrekt: `chmod 755 media/logos/`
- [ ] Nginx /media/ Location konfiguriert
- [ ] Django Service neu gestartet
- [ ] Logo-Upload testen

---

Letzte Aktualisierung: November 2024
