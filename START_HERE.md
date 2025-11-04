# Email-to-Ticket System - Start Here

## What This System Does

Automatically converts incoming emails into support tickets without requiring Celery, Redis, or any external dependencies.

**Email arrives** → **Automatically becomes a ticket** → **No manual work needed**

---

## Choose Your Path

### 🚀 Quick Start (5 Minutes)

**I just want it working as fast as possible**

1. Read: [EMAIL_SETUP_QUICK_START.md](EMAIL_SETUP_QUICK_START.md)
2. Follow the 5-step configuration
3. Done!

### 📖 Complete Guide (15 Minutes)

**I want to understand everything**

1. Start: [EMAIL_TO_TICKETS_README.md](EMAIL_TO_TICKETS_README.md)
2. Setup: [EMAIL_SETUP_QUICK_START.md](EMAIL_SETUP_QUICK_START.md)
3. Scheduling: [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)
4. Technical: [EMAIL_SYSTEM_IMPLEMENTATION.md](EMAIL_SYSTEM_IMPLEMENTATION.md)

### 🧪 Test First (Testing)

**I want to test before deploying**

1. Run: `python test_email_to_ticket.py`
2. This will verify your configuration
3. Follow the recommendations

---

## Files Overview

| File | Purpose | Read Time |
|------|---------|-----------|
| **START_HERE.md** | You are here! | 2 min |
| **EMAIL_TO_TICKETS_README.md** | Complete overview | 5 min |
| **EMAIL_SETUP_QUICK_START.md** | Fast configuration | 5 min |
| **SCHEDULER_SETUP.md** | Setup scheduling | 10 min |
| **EMAIL_SYSTEM_IMPLEMENTATION.md** | Technical details | 10 min |
| **test_email_to_ticket.py** | Run tests | 3 min |

---

## The Quickest Path

### 1. Add to `.env`:
```env
IMAP_ENABLED=True
IMAP_HOST=mail.aboro-it.net
IMAP_PORT=993
IMAP_USERNAME=support@aboro-it.net
IMAP_PASSWORD=your_password_here
```

### 2. Test:
```bash
python manage.py process_emails --verbose --dry-run
```

### 3. Schedule (pick one):

**Linux/Mac:**
```bash
crontab -e
# Add: */5 * * * * cd /path/to/helpdesk && python manage.py process_emails
```

**Windows:**
- Open Task Scheduler
- Create task → `pythonw.exe manage.py process_emails` → Every 5 minutes

### 4. Monitor:
```bash
tail -f logs/helpdesk.log
```

**That's it! Emails now become tickets automatically.**

---

## Quick Reference

```bash
# Test (no changes made)
python manage.py process_emails --verbose --dry-run

# Process all emails
python manage.py process_emails

# See detailed output
python manage.py process_emails --verbose

# Process only 5 emails
python manage.py process_emails --limit 5

# Process specific folder
python manage.py process_emails --folder INBOX
```

---

## Features

- ✅ No Celery needed
- ✅ No Redis needed
- ✅ No installation required
- ✅ Works on Linux, Mac, Windows
- ✅ Simple scheduling (cron/Task Scheduler)
- ✅ Production-ready
- ✅ Fully documented
- ✅ Tested and verified

---

## How It Works

**New email without ticket number:**
- Creates new ticket
- Creates customer user (if needed)
- Saves customer email address

**Email with ticket number in subject:**
- Finds existing ticket
- Adds email as comment
- Marks as from email

Supported patterns:
- `[TICKET-123]`
- `#123`
- `Ticket #123`
- `RE: [TICKET-123]`

---

## Need Help?

1. **Not sure where to start?** → Read [EMAIL_TO_TICKETS_README.md](EMAIL_TO_TICKETS_README.md)

2. **Want quick setup?** → Read [EMAIL_SETUP_QUICK_START.md](EMAIL_SETUP_QUICK_START.md)

3. **Need scheduling details?** → Read [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)

4. **Want technical details?** → Read [EMAIL_SYSTEM_IMPLEMENTATION.md](EMAIL_SYSTEM_IMPLEMENTATION.md)

5. **Want to test first?** → Run `python test_email_to_ticket.py`

6. **Having issues?** → Check [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md) "Troubleshooting" section

---

## What's Included

```
Django Management Command:
  ✓ apps/tickets/management/commands/process_emails.py

Email Processing:
  ✓ apps/tickets/email_handler.py
  ✓ apps/tickets/tasks.py (optional Celery)

Documentation:
  ✓ EMAIL_TO_TICKETS_README.md (main guide)
  ✓ EMAIL_SETUP_QUICK_START.md (fast setup)
  ✓ SCHEDULER_SETUP.md (complete setup)
  ✓ EMAIL_SYSTEM_IMPLEMENTATION.md (technical)
  ✓ START_HERE.md (this file)

Tests:
  ✓ test_email_to_ticket.py (test suite)
```

---

## Next Step

👉 **Go to [EMAIL_SETUP_QUICK_START.md](EMAIL_SETUP_QUICK_START.md) for fast setup!**

Or read [EMAIL_TO_TICKETS_README.md](EMAIL_TO_TICKETS_README.md) for complete overview.

---

*Status: Production Ready*
*Dependencies: None (Celery/Redis optional)*
*Platforms: Linux, Mac, Windows*
