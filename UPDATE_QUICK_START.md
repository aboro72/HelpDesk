# Auto-Update System - Quick Start

## 5-Minuten Setup

### Schritt 1: Konfigurieren (1 Min)

Füge zu `.env` hinzu:

```env
GITHUB_REPO=aborowczak/HelpDesk
GITHUB_BRANCH=main
```

### Schritt 2: Datenbank (1 Min)

```bash
python manage.py migrate
```

### Schritt 3: Testen (1 Min)

```bash
python manage.py check_updates
```

### Schritt 4: Install Celery (optional, 2 Min)

Für automatische Überprüfung alle 6 Stunden:

```bash
# Terminal 1
celery -A helpdesk worker -l info

# Terminal 2
celery -A helpdesk beat -l info
```

**Fertig!** System überprüft jetzt automatisch auf Updates.

---

## Häufige Befehle

| Befehl | Effekt |
|--------|--------|
| `python manage.py check_updates` | Überprüfe auf Updates |
| `python manage.py check_updates --install` | Installiere Updates automatisch |
| `python manage.py check_updates --list-files` | Zeige was aktualisiert wird |
| `python manage.py check_updates --force` | Ignoriere Cache, überprüfe neu |

---

## Automatische Installation

Setze in `.env`:

```env
AUTO_UPDATE=True
AUTO_UPDATE_HOUR=2
```

Dann lädt das System die Updates automatisch um 2 Uhr nachts.

---

## Im Admin-Panel

1. Gehe zu: **Settings**
2. Wenn Updates da sind: **Updates verfügbar** Button
3. Klicke: **Jetzt installieren**

**Fertig!**

---

## Was passiert?

1. System verbindet zu GitHub
2. Vergleicht Dateien
3. Lädt nur geänderte Dateien herunter
4. Erstellt Backup
5. Installiert Updates
6. Bestätigt Installation

---

## Sicherheit

✅ Nur öffentliche GitHub-Repositories (keine Login nötig)
✅ HTTPS-Verbindung
✅ Automatische Backups vor jedem Update
✅ Geschützte Dateien (.env, settings.py, etc.)

---

Für mehr Details siehe: [UPDATE_SYSTEM.md](UPDATE_SYSTEM.md)
