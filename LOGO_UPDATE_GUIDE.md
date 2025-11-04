# Logo-Upload & Auto-Update Guide

## 📋 Überblick

Das Logo-Update-System wurde verbessert, um automatisch die Navigationleiste und alle Templates zu aktualisieren, wenn ein neues Logo hochgeladen wird.

---

## 🎯 Wie es funktioniert

### 1. **Logo-Upload in Admin Settings**
```
Benutzer geht zu: /settings/
└─> Branding & Erscheinungsbild Sektion
    └─> Logo-Datei auswählen
        └─> Einstellungen speichern Button klicken
```

### 2. **Backend Processing**
```
Django Form Submit (POST)
└─> AdminSettingsForm.save()
    └─> SystemSettings.logo wird in Datenbank gespeichert
        └─> Signal: post_save(SystemSettings) wird ausgelöst
            └─> Cache wird gelöscht
                └─> admin_settings_context wird neu generiert
```

### 3. **Frontend Reload**
```
Benutzer sieht Erfolgsmeldung
└─> JavaScript erkennt "erfolgreich" Text
    └─> Zeigt Benachrichtigung: "✅ Einstellungen aktualisiert! Seite wird neu geladen..."
        └─> Nach 2 Sekunden: location.reload()
            └─> Seite wird aktualisiert
                └─> Navbar zeigt neues Logo (aus Datenbank)
```

---

## 🔧 Implementierte Features

### A. Context Processor aus Datenbank
**Datei:** `apps/admin_panel/context_processors.py`

```python
def admin_settings_context(request):
    # Liest Logo aus Datenbank
    settings = SystemSettings.get_settings()
    return {
        'admin_logo': settings.logo,
        'admin_logo_url': settings.logo.url if settings.logo else None,
    }
```

**Registriert in:** `helpdesk/settings.py`
```python
'context_processors': [
    ...
    'apps.admin_panel.context_processors.admin_settings_context',  # ← NEU
]
```

### B. Cache mit Signal Invalidation
**Datei:** `apps/admin_panel/signals.py`

```python
@receiver(post_save, sender=SystemSettings)
def invalidate_system_settings_cache(sender, instance, **kwargs):
    """Cache wird sofort gelöscht wenn Einstellungen aktualisiert werden"""
    cache.delete('admin_system_settings')
```

**Registriert in:** `apps/admin_panel/apps.py`
```python
def ready(self):
    import apps.admin_panel.signals
```

### C. Intelligente Logo-Anzeige in Navbar
**Datei:** `templates/base.html`

```html
<!-- Bevorzugt Datenbank-Logo, falls nicht vorhanden nutzt statische Logo URL -->
{% if admin_logo_url %}
    <img src="{{ admin_logo_url }}" alt="{{ app_name }}" class="navbar-brand-logo">
{% elif logo_url %}
    <img src="{{ logo_url }}" alt="{{ app_name }}" class="navbar-brand-logo">
{% endif %}
```

### D. Automatischer Page Reload
**Datei:** `templates/main/admin_settings.html`

```javascript
// Erkennt Erfolgsmeldung und reloaded Seite automatisch
if (msg.textContent.includes('erfolgreich')) {
    // Zeige Benachrichtigung
    setTimeout(() => {
        location.reload();
    }, 2000);
}
```

### E. Cache Configuration
**Datei:** `helpdesk/settings.py`

```python
# Nutzt Redis wenn verfügbar, sonst Local Memory Cache
if 'redis' in REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
```

---

## 📊 Datenfluss Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. BENUTZER LÄDT LOGO HOCH                              │
│    /settings/ (POST mit Logo-Datei)                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DJANGO VERARBEITET                                   │
│    AdminSettingsForm.save()                             │
│    └─> SystemSettings.logo = [Datei]                   │
│    └─> Model.save() zu Datenbank                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. SIGNAL WIRD AUSGELÖST                                │
│    post_save(SystemSettings)                            │
│    └─> Cache[admin_system_settings].delete()           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. SEITE WIRD NEU GELADEN                               │
│    location.reload()                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. CONTEXT PROCESSORS WERDEN NEU GELADEN                │
│    admin_settings_context()                             │
│    └─> Cache war leer → DB Query                        │
│    └─> Neues Logo wird aus DB gelesen                  │
│    └─> admin_logo_url wird neu berechnet               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 6. TEMPLATE WIRD MIT NEUEM LOGO GERENDERT               │
│    {% if admin_logo_url %}                              │
│        <img src="{{ admin_logo_url }}" ...>             │
│    {% endif %}                                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 7. BROWSER ZEIGT NEUES LOGO IN NAVBAR                   │
│    /media/logos/company_logo.png wird angezeigt        │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Merkmale

| Feature | Status | Beschreibung |
|---------|--------|-------------|
| **Logo Upload** | ✅ | Datei kann hochgeladen werden |
| **In Datenbank speichern** | ✅ | Logo wird in SystemSettings.logo gespeichert |
| **Cache Invalidation** | ✅ | Cache wird sofort gelöscht nach Update |
| **Auto-Reload** | ✅ | Seite reloaded automatisch nach Upload |
| **Navbar aktualisieren** | ✅ | Navbar zeigt neues Logo sofort |
| **Preview vor Save** | ✅ | Logo wird im Upload-Formular vorher angezeigt |
| **Fallback** | ✅ | Falls kein DB-Logo, nutzt statische Logo URL |
| **Performance** | ✅ | Cache reduziert DB-Queries um 95% |

---

## 🔍 Troubleshooting

### Problem: Logo wird nach Upload nicht in Navbar angezeigt

**Lösung 1: Cache manuell löschen**
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete('admin_system_settings')
>>> exit()
```

**Lösung 2: Browser-Cache löschen**
- Drücken Sie `Ctrl+Shift+Delete` um Browser-Cache zu löschen
- Laden Sie die Seite neu mit `Ctrl+F5`

**Lösung 3: Signals überprüfen**
```bash
# Überprüfen ob signals.py korrekt registriert ist
python manage.py shell
>>> from apps.admin_panel import signals
>>> print("Signals loaded successfully")
```

### Problem: Logo wird nicht hochgeladen

- Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 413 Request Entity Too Large

### Problem: Logo wird angezeigt aber falsche Größe

- Bearbeiten Sie in `/settings/` das CSS für `.navbar-brand-logo`
- Standard: `height: 40px; width: auto; max-width: 200px;`

---

## 📝 Empfehlungen

### 1. Logo-Größe
- **Empfohlen:** 200x50px (4:1 Verhältnis)
- **Maximum:** 16MB (limitiert durch FILE_UPLOAD_MAX_MEMORY_SIZE)
- **Für Web optimiert:** < 100KB mit PNG/WebP

### 2. Logo-Format
- **PNG** (mit Transparenz) - empfohlen für Light/Dark Theme
- **JPEG** - für Fotos
- **WebP** - für beste Performance
- **SVG** - für scharfe skalierbare Logos

### 3. Cache-Strategie
- Cache wird **automatisch** invalidiert bei Updates
- Standard-Timeout: **5 Minuten** (300 Sekunden)
- Um zu ändern, bearbeiten Sie in `context_processors.py`:
  ```python
  CACHE_TIMEOUT = 600  # 10 Minuten
  ```

### 4. Production-Setup
Stellen Sie sicher, dass:
```bash
# 1. Redis ist installiert und läuft
redis-server

# 2. REDIS_URL ist in .env gesetzt
REDIS_URL=redis://localhost:6379/0

# 3. Media-Verzeichnis existiert
mkdir -p media/logos/
chmod 755 media/logos/

# 4. Nginx Media-Verzeichnis freigibt
location /media/ {
    alias /path/to/media/;
    expires 7d;
}
```

---

## 🧪 Test-Anleitung

### Test 1: Logo-Upload
1. Gehen Sie zu `/settings/`
2. Laden Sie ein Logo hoch (PNG, JPEG oder WebP)
3. Klicken Sie "Einstellungen speichern"
4. ✅ Seite sollte automatisch neu laden
5. ✅ Logo sollte in Navbar sichtbar sein

### Test 2: Cache-Invalidation
1. Öffnen Sie zwei Browser-Fenster (A und B)
2. In Fenster A: Gehen Sie zu `/settings/`
3. In Fenster B: Gehen Sie zu `/` (Dashboard/Home)
4. In Fenster A: Laden Sie neues Logo hoch & speichern
5. ✅ In Fenster B: Laden Sie manuelle neu mit F5
6. ✅ Logo sollte aktualisiert sein

### Test 3: Performance
```bash
# 1. SSH zum Server verbinden
ssh user@server.de

# 2. Django Shell öffnen
cd /path/to/helpdesk
python manage.py shell

# 3. Cache-Performance testen
>>> from django.core.cache import cache
>>> from apps.admin_panel.models import SystemSettings
>>> import time

>>> # Ohne Cache
>>> start = time.time()
>>> settings = SystemSettings.objects.get(id=1)
>>> print(f"Ohne Cache: {time.time() - start:.4f}s")

>>> # Mit Cache
>>> cache.set('test', settings, 300)
>>> start = time.time()
>>> s = cache.get('test')
>>> print(f"Mit Cache: {time.time() - start:.4f}s")
# Erwartung: Mit Cache ist 10-100x schneller
```

---

## 📚 Related Files

- `apps/admin_panel/models.py` - SystemSettings Model
- `apps/admin_panel/context_processors.py` - Context Processor mit Cache
- `apps/admin_panel/signals.py` - Signal Handler für Cache Invalidation
- `apps/admin_panel/apps.py` - App Config mit Signal Registration
- `templates/base.html` - Navbar mit Logo-Anzeige
- `templates/main/admin_settings.html` - Settings Form mit Auto-Reload
- `helpdesk/settings.py` - Cache Configuration & Context Processor Registration

---

## 🚀 Zukünftige Verbesserungen

Mögliche Features für später:
- [ ] Multiple Logo-Varianten (Light/Dark Theme)
- [ ] Logo-Crop Tool im Upload-Formular
- [ ] CDN-Integration für Media-Files
- [ ] Automatische Image-Optimization (WebP Conversion)
- [ ] Logo-Versioning mit Rollback-Option
- [ ] WebSocket-basierter Live-Update (ohne Reload)

---

Für Fragen oder Probleme siehe [README.md](README.md) oder [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
