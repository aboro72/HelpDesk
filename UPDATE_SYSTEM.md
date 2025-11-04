# Auto-Update System - Dokumentation

## Übersicht

Das Update-System überprüft automatisch auf neue Versionen in GitHub und lädt nur die geänderten Dateien herunter. Dies spart Bandbreite und Zeit.

**Features:**
- Automatische Überprüfung auf Updates (alle 6 Stunden)
- Nur geänderte Dateien werden heruntergeladen
- Automatische Benachrichtigung im Admin-Panel
- Manuelle oder automatische Installation
- Backup vor jedem Update
- Update-Verlauf verfügbar

---

## Installation

### Schritt 1: GitHub Repository konfigurieren

Gib dein GitHub-Repository in `.env` an:

```env
# Beispiel für öffentliches Repository
GITHUB_REPO=aborowczak/HelpDesk
GITHUB_BRANCH=main

# Optional: Automatische Updates alle Nacht um 2 Uhr
AUTO_UPDATE=False
AUTO_UPDATE_HOUR=2
```

### Schritt 2: Datenbank-Migration

Erstelle die UpdateNotification-Tabelle:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Schritt 3: Anforderungen

Das System benötigt:
- `requests` Python-Paket (zum Herunterladen von GitHub)
- Zugriff auf GitHub API (keine Authentifizierung für öffentliche Repos)

---

## Verwendung

### Manuelle Update-Überprüfung

```bash
# Nur überprüfen
python manage.py check_updates

# Überprüfen und verfügbare Dateien anzeigen
python manage.py check_updates --list-files

# Überprüfen und automatisch installieren
python manage.py check_updates --install

# Cache ignorieren und neu überprüfen
python manage.py check_updates --force
```

### Im Admin-Panel

1. Gehe zu: **Admin Panel** → **System-Einstellungen**
2. Klicke auf: **Updates verfügbar** (wenn Updates da sind)
3. Wähle: **Updates anzeigen**
4. Klicke: **Jetzt installieren**

### Automatische Überprüfung

Das System überprüft alle 6 Stunden automatisch auf Updates (wenn Celery läuft):

```bash
celery -A helpdesk worker -l info
celery -A helpdesk beat -l info
```

---

## Automatische Installation

### Aktivieren

Setze in `.env`:

```env
AUTO_UPDATE=True
AUTO_UPDATE_HOUR=2  # Installation um 2:00 Uhr nachts
```

### Deaktivieren

```env
AUTO_UPDATE=False
```

**Wichtig:** Ohne Celery läuft die automatische Installation nicht. Verwende stattdessen Cron:

```bash
# Jeden Tag um 2 Uhr nachts
0 2 * * * python manage.py check_updates --install
```

---

## Update-Prozess

### Was passiert beim Update?

1. **Überprüfung:** System verbindet sich mit GitHub
2. **Vergleich:** Vergleicht lokale vs. GitHub-Dateien
3. **Benachrichtigung:** Admin wird im Panel benachrichtigt
4. **Backup:** Originaldateien werden gesichert
5. **Download:** Nur geänderte Dateien werden heruntergeladen
6. **Installation:** Dateien werden ersetzt
7. **Bestätigung:** Status wird aktualisiert

### Geschützte Dateien

Diese Dateien werden NIEMALS automatisch aktualisiert:

```
.env
helpdesk/settings.py
db.sqlite3
manage.py
```

Diese Dateien könnten Konfigurationen oder Daten enthalten und müssen manuell aktualisiert werden, wenn nötig.

---

## Monitoring

### Update-Verlauf anschauen

```bash
# Im Admin-Panel
Admin Panel → Updates → Verlauf

# Oder in der Shell
python manage.py shell
from apps.admin_panel.models import UpdateNotification
for update in UpdateNotification.objects.all().order_by('-created_at'):
    print(f"{update.version}: {'Installiert' if update.installed else 'Verfügbar'}")
```

### Logs anschauen

```bash
# Update-Logs
tail -f logs/helpdesk.log | grep "Update"

# Spezifische Datei
grep "update_manager" logs/helpdesk.log
```

---

## Konfiguration

### Umgebungsvariablen

```env
# GitHub Repository
GITHUB_REPO=aborowczak/HelpDesk
GITHUB_BRANCH=main

# Automatische Updates
AUTO_UPDATE=False
AUTO_UPDATE_HOUR=2

# Update-Einstellungen (optional)
UPDATE_CHECK_INTERVAL=21600  # 6 Stunden in Sekunden
```

---

## Fehlerbehandlung

### Problem: "Connection refused" bei GitHub

**Ursache:** Netzwerk-Verbindungsproblem oder GitHub ist nicht erreichbar

**Lösung:**
```bash
# Teste GitHub-Verbindung
python -c "import requests; print(requests.get('https://github.com').status_code)"

# Sollte 200 zurückgeben
```

### Problem: "Repository not found"

**Ursache:** GITHUB_REPO ist falsch konfiguriert

**Lösung:**
```bash
# Überprüfe in .env
grep GITHUB_REPO .env

# Sollte sein: GITHUB_REPO=aborowczak/HelpDesk
```

### Problem: "Updates schlagen fehl"

**Überprüfe:**
1. Dateiberechtigungen im Projektordner
2. Logs: `tail logs/helpdesk.log`
3. Geschützte Dateien - diese können nicht aktualisiert werden

---

## Best Practices

### 1. Regelmäßige Backups

Bevor automatische Updates aktiviert werden:

```bash
# Backup erstellen
cp -r . backup_$(date +%Y%m%d)

# Oder nutze Git
git add .
git commit -m "Vor Auto-Update"
```

### 2. Updates testen

Vor der automatischen Installation:

```bash
# Im Test-Modus überprüfen
python manage.py check_updates --list-files

# Manuelle Installation mit Kontrolle
python manage.py check_updates --install
```

### 3. Update-Zeiten

Setze AUTO_UPDATE_HOUR auf eine Zeit mit niedrigem Traffic:

```env
# Nachts um 2 Uhr
AUTO_UPDATE_HOUR=2

# Oder Wochenende
# Nutze Cron für wöchentliche Updates statt täglich
```

### 4. Monitoring

Überprüfe Update-Verlauf regelmäßig:

```bash
python manage.py shell
from apps.admin_panel.models import UpdateNotification
print(f"Verfügbar: {UpdateNotification.objects.filter(installed=False).count()}")
print(f"Installiert: {UpdateNotification.objects.filter(installed=True).count()}")
```

---

## Troubleshooting

### Debug-Modus aktivieren

```bash
# Verbose Output
python manage.py check_updates --force -v 2

# Mit Dateien-Liste
python manage.py check_updates --list-files --force
```

### Update-Backups einsehen

```bash
ls -la .update_backups/
```

### Zu vorheriger Version zurück

```bash
# Backup überprüfen
ls -la .update_backups/

# Datei wiederherstellen
cp .update_backups/app_file_20231115_120000.backup apps/file.py
```

---

## API für Entwickler

### Manuelle Update-Überprüfung

```python
from apps.admin_panel.update_manager import UpdateChecker

checker = UpdateChecker()
result = checker.check_for_updates()

if result['has_updates']:
    print(f"Updates verfügbar: {result['file_count']} Dateien")
    for file_path in result['updates'].keys():
        print(f"  - {file_path}")
```

### Manuelle Installation

```python
from apps.admin_panel.update_manager import UpdateDownloader

downloader = UpdateDownloader()
results = downloader.install_updates(['apps/file.py', 'templates/base.html'])

print(f"Erfolgreich: {len(results['success'])}")
print(f"Fehlgeschlagen: {len(results['failed'])}")
```

---

## Sicherheit

### Überprüfungen beim Update

✅ **Dateivalidierung:** SHA256-Hashes werden überprüft
✅ **Backup:** Originaldateien werden immer gesichert
✅ **Geschützte Dateien:** Config-Dateien werden nicht berührt
✅ **Error Handling:** Fehler werden geloggt und nicht verschwiegen

### Netzwerk-Sicherheit

✅ **HTTPS:** GitHub API nutzt HTTPS
✅ **Keine Authentifizierung nötig:** Öffentliche Repositories
✅ **Rate Limiting:** GitHub API hat Rate-Limits

### Empfehlungen

1. **Regelmäßige Backups:** Vor automatischen Updates
2. **Update-Verlauf:** Überprüfe regelmäßig was installiert wurde
3. **Test vor Produktion:** Teste Updates zuerst lokal
4. **Logs kontrollieren:** Überprüfe auf Fehler nach Updates

---

## FAQ

**F: Kann ich Updates ablehnen?**
A: Ja, die Installation ist optional. Du wirst nur benachrichtigt.

**F: Werden meine Einstellungen überschrieben?**
A: Nein, `.env` und `settings.py` sind geschützt. Du musst sie manuell aktualisieren.

**F: Wie viel Bandbreite braucht das?**
A: Nur die geänderten Dateien werden heruntergeladen. Meist <1MB pro Update.

**F: Kann ich Updates automatisch installieren?**
A: Ja, mit `AUTO_UPDATE=True` in `.env`.

**F: Wie oft werden Updates überprüft?**
A: Alle 6 Stunden (konfigurierbar in settings.py).

**F: Was wenn ein Update fehlschlägt?**
A: Die Original-Dateien sind in `.update_backups/` gesichert.

---

## Support

Bei Problemen mit Updates:

1. Überprüfe Logs: `tail logs/helpdesk.log`
2. Test manuell: `python manage.py check_updates --force`
3. Überprüfe Berechtigungen: `ls -la` im Projektordner
4. Siehe Troubleshooting-Sektion oben

---

**Status:** Produktionsreife
**Benötigt:** requests Library, GitHub-Zugriff
**Tested:** Mit GitHub API v3
