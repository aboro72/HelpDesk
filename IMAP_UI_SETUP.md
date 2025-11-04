# IMAP-Konfiguration über Web-UI

## Übersicht

Die IMAP-Einstellungen können jetzt direkt im Admin-Panel unter `http://127.0.0.1:8000/settings/` konfiguriert werden - ohne `.env` Datei bearbeiten zu müssen!

## Zugriff auf die Einstellungen

1. **Öffne den Browser:** `http://127.0.0.1:8000/settings/`
2. **Scrolle nach unten** zum Abschnitt "📧 E-Mail Konfiguration"
3. **Du siehst zwei Sektionen:**
   - **📤 SMTP** (Ausgehende E-Mails) - Für das Versenden von Antworten
   - **📥 IMAP** (Eingehende E-Mails) - Für die automatische Ticket-Erstellung

## IMAP Konfigurieren

### Schritt 1: IMAP aktivieren

Unter "📥 IMAP (Eingehende E-Mails zu Tickets)":
- Aktiviere das Kontrollkästchen "IMAP aktivieren"

### Schritt 2: Server-Einstellungen eingeben

Gib folgende Werte ein:

**Für ISPConfig Mail Server (mail.aboro-it.net):**
```
IMAP Server: mail.aboro-it.net
IMAP Port: 993
IMAP Benutzername: support@aboro-it.net
IMAP Passwort: dein_passwort
IMAP Ordner: INBOX
SSL verwenden: aktiviert (Häkchen)
```

**Alternative Server:**

*Gmail:*
```
IMAP Server: imap.gmail.com
IMAP Port: 993
IMAP Benutzername: dein@gmail.com
IMAP Passwort: dein_app_passwort
IMAP Ordner: INBOX
SSL verwenden: aktiviert
```

*Office 365:*
```
IMAP Server: outlook.office365.com
IMAP Port: 993
IMAP Benutzername: dein@company.com
IMAP Passwort: dein_passwort
IMAP Ordner: INBOX
SSL verwenden: aktiviert
```

### Schritt 3: Speichern

Klicke auf "Speichern" am Ende der Seite.

Die Einstellungen werden in der Datenbank gespeichert und sind sofort aktiv.

## Wie es funktioniert

### Automatische Verarbeitung

Nach dem Speichern der Einstellungen:

1. **Alle 5 Minuten** (wenn geplant) wird das System überprüfen, ob neue E-Mails vorhanden sind
2. **Neue E-Mails** ohne Ticket-Nummer → Erstelle neues Ticket
3. **E-Mail-Antworten** mit `[TICKET-123]` → Füge als Kommentar hinzu

### Erkannte Ticket-Nummer-Formate

Das System erkennt automatisch:
- `[TICKET-123]` - Standard-Format
- `RE: [TICKET-123]` - Antwort-Format
- `#123` - Kurzformat
- `Ticket #123` - Ausführliches Format

## Passwort-Handling

**Wichtig:**
- Passwortfelder leer lassen = aktuelles Passwort behalten
- Neues Passwort eingeben = aktualisieren

So kannst du das Passwort aktualisieren ohne andere Einstellungen zu ändern.

## Einstellungen lesen / Priorität

Das System nutzt folgende Priorität (von hoch zu niedrig):

1. **Web-UI Einstellungen** (Datenbank) ← **EMPFOHLEN**
2. **Umgebungsvariablen** (.env oder System-Variablen)

Das bedeutet: Die Einstellungen aus der Web-UI überschreiben die `.env` Variablen.

## Fallback-Behavior

Falls die Datenbank nicht verfügbar ist:
- System verwendet Umgebungsvariablen aus `.env`
- Alle Funktionen funktionieren weiterhin
- Keine Unterbrechung des E-Mail-Prozesses

## Mehrere Mailboxen

Um mehrere Mailboxen zu verarbeiten:

**Option 1: Aufeinanderfolgende Ausführung**
```bash
# Mailbox 1
python manage.py process_emails --folder "INBOX"

# Mailbox 2
python manage.py process_emails --folder "Support"

# Mailbox 3
python manage.py process_emails --folder "Escalations"
```

**Option 2: Separate Cron-Jobs**
```bash
# Alle 5 Minuten - Haupt-Inbox
*/5 * * * * cd /path && python manage.py process_emails

# Jede halbe Stunde - Support-Ordner
*/30 * * * * cd /path && python manage.py process_emails --folder "Support"
```

## Testen der Einstellungen

### Schneller Test (ohne Tickets zu erstellen)

```bash
python manage.py process_emails --verbose --dry-run
```

Output zeigt:
- Verbindung zur IMAP-Server
- Anzahl der E-Mails gefunden
- Was würde passieren (ohne echte Änderungen)

### Vollständiger Test

```bash
python manage.py process_emails --limit 1 --verbose
```

Verarbeitet 1 E-Mail mit ausführlichem Output.

### Logs anschauen

```bash
tail -f logs/helpdesk.log | grep "Email processing"
```

## Troubleshooting

### Problem: "Connection failed"

**Überprüfe:**
1. Server-Adresse ist korrekt
2. Port ist richtig (normalerweise 993 für SSL)
3. Benutzername und Passwort sind korrekt
4. Firewall erlaubt Port 993
5. SSL ist aktiviert (normalerweise ja)

**Test:**
```bash
python test_email_to_ticket.py
```

### Problem: "IMAP is not enabled"

**Lösung:**
1. Gehe zu Settings
2. Aktiviere das "IMAP aktivieren" Kontrollkästchen
3. Speichere

### Problem: Keine Tickets werden erstellt

**Überprüfe:**
1. IMAP ist aktiviert in der Web-UI
2. Ungelesene E-Mails im Postfach vorhanden
3. Logs auf Fehler: `tail logs/helpdesk.log`
4. Scheduler läuft (Cron oder Task Scheduler)

## Sicherheit

**Passwörter sind:**
- Verschlüsselt in der Datenbank gespeichert (Django ORM)
- Nicht in Logs sichtbar
- Nur Admin kann sie sehen
- Nicht in der Web-UI-Vorschau sichtbar

**Best Practice:**
- Nutze App-spezifische Passwörter (nicht dein Haupt-Passwort)
- Für Gmail: Nutze "App-Passwörter"
- Für Office 365: Nutze eigenes Passwort oder App-Passwort

## Weitere Ressourcen

- **Setup-Anleitung:** [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)
- **Technische Details:** [EMAIL_SYSTEM_IMPLEMENTATION.md](EMAIL_SYSTEM_IMPLEMENTATION.md)
- **Quick Start:** [EMAIL_SETUP_QUICK_START.md](EMAIL_SETUP_QUICK_START.md)

## Zusammenfassung

✅ Keine `.env`-Bearbeitung nötig
✅ Einfache Web-Interface
✅ Passwort-Handling
✅ Fallback auf Umgebungsvariablen
✅ Test-Funktionalität
✅ Sicherheit durch Django ORM
