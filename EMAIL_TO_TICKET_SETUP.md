# 📧 Email-to-Ticket System - Setup & Configuration

## Overview

Das Email-to-Ticket System konvertiert automatisch eingehende Emails zu Tickets:
- **Neue Emails** → Erstellen automatisch neue Tickets
- **Emails mit Ticket-Nummer** → Werden als Kommentare zu existierendem Ticket hinzugefügt
- **Automatische Verarbeitung** → Läuft alle 5 Minuten im Hintergrund (Celery Beat)

---

## 🔧 Installation & Setup

### Schritt 1: Abhängigkeiten installieren

```bash
pip install celery redis django-celery-beat
```

### Schritt 2: Redis Server starten

```bash
# Linux/Mac
redis-server

# Windows
redis-server.exe

# Oder mit Docker
docker run -d -p 6379:6379 redis:latest
```

### Schritt 3: Environment Variables konfigurieren

Füge diese Variablen zu deiner `.env` Datei hinzu:

```env
# IMAP Email Configuration (für Ticket-Erstellung aus Emails)
IMAP_HOST=mail.aboro-it.net
IMAP_PORT=993
IMAP_USERNAME=support@aboro-it.net
IMAP_PASSWORD=aokoTW#R2
IMAP_FOLDER=INBOX
IMAP_ENABLED=True

# SMTP Email Configuration (für Ticket-Antworten)
SMTP_HOST=mail.aboro-it.net
SMTP_PORT=587
SMTP_USERNAME=support@aboro-it.net
SMTP_PASSWORD=aokoTW#R2
EMAIL_HOST_USER=support@aboro-it.net
DEFAULT_FROM_EMAIL=support@aboro-it.net

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Site URL (für Links in Emails)
SITE_URL=https://your-domain.com
```

### Schritt 4: Datenbank migrationen ausführen

```bash
python manage.py migrate tickets
```

### Schritt 5: Celery Worker starten

```bash
# Terminal 1: Celery Worker
celery -A helpdesk worker -l info

# Terminal 2: Celery Beat (Scheduler)
celery -A helpdesk beat -l info
```

Oder als Service (Production):

```bash
# Mit Supervisor oder systemd
supervisord -c /etc/supervisor/conf.d/celery.conf
```

### Schritt 6: Django starten

```bash
python manage.py runserver
```

---

## 📧 Wie es funktioniert

### Szenario 1: Neue Email von Kunde ohne Ticket

**Email kommt an:**
```
Von: kunde@example.com
Betreff: Ich habe ein Problem mit meinem Account

Hallo,
Ich kann nicht auf mein Dashboard zugreifen. Bitte helfen Sie mir.
Danke!
```

**Was passiert:**
1. ✅ System liest Email via IMAP
2. ✅ Erstellt neues Ticket (z.B. TICKET-001)
3. ✅ Setzt Betreff als Ticket-Titel
4. ✅ Email-Inhalt wird Ticket-Beschreibung
5. ✅ Setzt `created_from_email=True`
6. ✅ Speichert Kunden-Email (`email_from`)

**Ergebnis:**
```
Neues Ticket: TICKET-001
Titel: Ich habe ein Problem mit meinem Account
Status: Open
Priorität: Medium
Customer: kunde@example.com (Automatisch erstellt)
```

---

### Szenario 2: Email-Antwort zu bestehendem Ticket

**Email kommt an:**
```
Von: kunde@example.com
Betreff: RE: [TICKET-001] - Ich habe ein Problem mit meinem Account

Danke für deine Antwort! Ich habe es jetzt versucht und es funktioniert.
Aber ich habe noch eine andere Frage...
```

**Was passiert:**
1. ✅ System erkennt `[TICKET-001]` im Betreff
2. ✅ Findet das existierende Ticket #001
3. ✅ Fügt Email-Inhalt als Kommentar hinzu
4. ✅ Markiert als `is_from_email=True`
5. ✅ Speichert Sender-Email als `author_email`
6. ✅ Markiert Email als gelesen

**Ergebnis:**
```
Ticket TICKET-001 - Kommentar hinzugefügt
Autor: kunde@example.com
Kommentar: "Danke für deine Antwort!..."
Von Email: ✓ Ja
```

---

## 🔍 Ticket-Nummer Erkennungsmuster

Das System erkennt Ticket-Nummern in folgenden Formaten:

```
Supported Patterns:
✓ [TICKET-123]          (Standard Format)
✓ #123                  (Kurz Format)
✓ Ticket #123           (Ausführlich)
✓ RE: [TICKET-123]      (Reply Format)
✓ [TICKET-001]          (Mit Nullen)
```

**Beispiele:**
```
"RE: [TICKET-001] - Problem gelöst"    ✓ Erkannt
"#42 - Frage zu Lizenz"                ✓ Erkannt
"Ticket #99 - Featurenanfrage"         ✓ Erkannt
"[TICKET-999]"                         ✓ Erkannt
"Problem mit Ticket 123"               ✗ NICHT erkannt
```

---

## 🤖 Automatische Verarbeitung

### Celery Beat Schedule

**Aktuell:**
```python
'process-email-to-tickets': {
    'schedule': crontab(minute='*/5'),  # Alle 5 Minuten
    ...
}
```

**Um die Frequenz zu ändern, bearbeite `helpdesk/settings.py`:**

```python
# Alle 1 Minute
'schedule': crontab(minute='*')

# Alle 10 Minuten
'schedule': crontab(minute='*/10')

# Alle Stunde um 15 Minuten nach der Stunde
'schedule': crontab(minute=15)

# Jeden Morgen um 8:00 Uhr
'schedule': crontab(hour=8, minute=0)
```

### Monitoring

**Logs anschauen:**
```bash
# Celery Worker Logs
tail -f celery-worker.log

# Celery Beat Logs
tail -f celery-beat.log
```

**Task-Status überprüfen (Django Shell):**
```bash
python manage.py shell

from celery.result import AsyncResult
from apps.tickets.models import Ticket

# Schau alle Tickets die aus Emails erstellt wurden
email_tickets = Ticket.objects.filter(created_from_email=True)
for ticket in email_tickets:
    print(f"{ticket.ticket_number}: {ticket.email_from}")

# Schau Kommentare von Emails
from apps.tickets.models import TicketComment
email_comments = TicketComment.objects.filter(is_from_email=True)
print(f"Total email comments: {email_comments.count()}")
```

---

## 🔒 Sicherheit & Best Practices

### 1. **Schütze IMAP-Zugangsdaten**
```env
# NICHT in .env Datei hardcoden!
# Verwende:
- Environment Variables
- Secrets Manager
- Docker Secrets
```

### 2. **Validiere Email-Adressen**
Das System erstellt automatisch Benutzer aus Emails. Das ist sicher, aber:
- Verzeichnis duplicate Emails
- Bestätige echte Kundennummern

### 3. **Rate Limiting**
```python
# In settings.py
CELERY_TASK_RATE_LIMIT = '100/m'  # Max 100 tasks pro Minute
```

### 4. **Error Handling**
Das System:
- ✓ Wird es erneut versuchen wenn es fehlt
- ✓ Loggt alle Fehler detailliert
- ✓ Kennzeichnet Problem-Emails als gelesen um Duplizierung zu vermeiden

---

## 🧪 Testing

### Test-Script ausführen

```bash
python manage.py shell

from apps.tickets.email_handler import EmailToTicketHandler

# Teste Verbindung
handler = EmailToTicketHandler()
if handler.connect():
    print("IMAP Connection successful!")
    handler.disconnect()
else:
    print("IMAP Connection failed!")

# Verarbeite Emails manuell (nicht über Celery)
from apps.tickets.email_handler import process_incoming_emails
result = process_incoming_emails()
print(f"Created: {result['created']}, Updated: {result['updated']}, Errors: {result['errors']}")
```

---

## 🐛 Troubleshooting

### Problem: "IMAP Connection failed"

```
Lösungen:
1. Überprüfe IMAP_HOST, IMAP_PORT, Benutzername, Passwort
2. Prüfe Firewall - Port 993 muss offen sein
3. Prüfe ob dein Email-Anbieter IMAP unterstützt
4. Teste mit: telnet mail.aboro-it.net 993
```

### Problem: "No unread emails found"

```
Das ist normal wenn:
- Alle Emails bereits gelesen sind
- Kein Emails im Postfach
- IMAP_FOLDER ist falsch konfiguriert

Lösungen:
1. Sende eine Test-Email
2. Überprüfe IMAP_FOLDER (Standard: INBOX)
3. Prüfe Logs: tail -f logs/helpdesk.log
```

### Problem: "Ticket not created"

```
Lösungen:
1. Überprüfe ob IMAP_ENABLED=True
2. Schau in Logs nach Fehlern
3. Teste manuell: python manage.py shell
4. Überprüfe ob Redis läuft: redis-cli ping
```

### Problem: "Celery Beat läuft nicht"

```bash
# Überprüfe ob Redis läuft
redis-cli ping
# Response: PONG

# Überprüfe Celery Worker
celery -A helpdesk inspect active

# Überprüfe Beat Scheduler
celery -A helpdesk inspect scheduled
```

---

## 📊 Datenbank-Schema

### Neue Felder in `Ticket`:
- `created_from_email` (Boolean) - Wurde aus Email erstellt?
- `email_from` (Email) - Absender-Email-Adresse

### Neue Felder in `TicketComment`:
- `author_name` (String) - Name des Email-Autors
- `author_email` (Email) - Email-Adresse des Autors
- `message` (Text) - Alias für content
- `is_from_email` (Boolean) - Kommentar aus Email?

---

## 📧 Email-Template Beispiel

Für das automatische Versenden von Ticket-Antworten brauchst du noch:

**`templates/tickets/email_reply.html`:**
```html
<h2>Ticket: {{ ticket_number }}</h2>
<p>{{ ticket_title }}</p>

<hr>

<h3>Neue Antwort von {{ author_name }}:</h3>
<p>{{ comment_content }}</p>

<hr>

<p>
    <a href="{{ ticket_url }}">Antworte auf diesem Ticket</a>
</p>
```

---

## 🚀 Production Deployment

### Mit Supervisor (Linux/Mac)

**`/etc/supervisor/conf.d/celery.conf`:**
```ini
[program:celery_worker]
command=celery -A helpdesk worker --loglevel=info
directory=/path/to/helpdesk
user=www-data
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600

[program:celery_beat]
command=celery -A helpdesk beat --loglevel=info
directory=/path/to/helpdesk
user=www-data
autostart=true
autorestart=true
startsecs=10
```

### Mit systemd (Modern Linux)

**`/etc/systemd/system/celery-worker.service`:**
```ini
[Unit]
Description=Helpdesk Celery Worker
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/helpdesk
Environment="PATH=/path/to/helpdesk/venv/bin"
ExecStart=/path/to/helpdesk/venv/bin/celery -A helpdesk worker

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
```

---

## 📝 Logs & Monitoring

**Standard Log-Pfad:**
```
logs/helpdesk.log
```

**Relevante Log-Einträge:**
```
"Processing email from customer@example.com: Ich brauche Hilfe"
"Created new Ticket #001 from email"
"Added comment to Ticket #001"
"Email processing completed: Created=1, Updated=0, Errors=0"
```

---

**Status:** Ready for Production
**Tested:** ✓ Getestet mit mail.aboro-it.net (ISPConfig)
**Support:** Falls Probleme auftreten, check das Troubleshooting-Section
