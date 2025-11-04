# Email-to-Ticket System - Quick Start Guide

## What It Does

Automatically converts incoming emails into support tickets:
- **New email** → Creates new ticket
- **Email with ticket number** → Adds as comment to existing ticket
- **No Celery/Redis required** → Works with simple scheduling (cron/Task Scheduler)

## Quick Setup (5 minutes)

### Step 1: Configure Email in `.env`

```env
# IMAP (for reading emails)
IMAP_ENABLED=True
IMAP_HOST=mail.aboro-it.net
IMAP_PORT=993
IMAP_USERNAME=support@aboro-it.net
IMAP_PASSWORD=your_password_here
IMAP_FOLDER=INBOX

# SMTP (for sending replies)
SMTP_HOST=mail.aboro-it.net
SMTP_PORT=587
SMTP_USERNAME=support@aboro-it.net
SMTP_PASSWORD=your_password_here
EMAIL_HOST_USER=support@aboro-it.net
DEFAULT_FROM_EMAIL=support@aboro-it.net
```

### Step 2: Test It

```bash
# Test with verbose output (no tickets created)
python manage.py process_emails --verbose --dry-run

# If you see emails being processed, it's working!
```

### Step 3: Schedule It

**Linux/Mac (Cron):**
```bash
crontab -e
# Add this line (every 5 minutes):
*/5 * * * * cd /path/to/helpdesk && python manage.py process_emails
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create New Task
3. Name: "Process Helpdesk Emails"
4. Trigger: Repeat every 5 minutes
5. Action: Run `pythonw.exe manage.py process_emails`
6. Start in: `C:\path\to\helpdesk`

## Available Commands

```bash
# Process all emails
python manage.py process_emails

# See what it would do (don't create tickets)
python manage.py process_emails --dry-run --verbose

# Process only 5 emails
python manage.py process_emails --limit 5

# Process specific folder
python manage.py process_emails --folder INBOX

# Detailed output
python manage.py process_emails --verbose
```

## Recognized Ticket Number Formats

Emails with these patterns automatically add as comments:
- `[TICKET-123]`
- `#123`
- `Ticket #123`
- `RE: [TICKET-123]`

## Monitoring

```bash
# View recent activity
tail -50 logs/helpdesk.log

# Filter for email processing
grep "Email processing" logs/helpdesk.log

# Count tickets created from email
grep "Created new Ticket from email" logs/helpdesk.log | wc -l
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not found | Check `__init__.py` files exist in `apps/tickets/management/commands/` |
| IMAP Connection fails | Verify credentials in `.env`, check firewall allows port 993 |
| No emails processed | Check IMAP_ENABLED=True, verify folder has unread emails |
| Task Scheduler not running | Test command manually first: `pythonw.exe manage.py process_emails` |
| Cron not running | Test: `/path/to/venv/bin/python /path/to/manage.py process_emails` |

## More Details

See `SCHEDULER_SETUP.md` for:
- Complete setup guide
- All scheduling options
- Production deployment
- Monitoring and logs
- Advanced configuration

---

**That's it! No Celery. No Redis. Just simple scheduling.** 🚀
