# Email-to-Ticket System - Scheduler Setup Guide

## Overview

The email-to-ticket system can be executed without Celery or Redis using Django's management command. This guide explains how to set it up for automatic execution via:
- Linux Cron Jobs
- Windows Task Scheduler
- Manual execution

## Quick Start

### Run Manually (Testing)

```bash
# Basic execution - process all unread emails
python manage.py process_emails

# Verbose mode - see detailed output
python manage.py process_emails --verbose

# Dry-run mode - test without creating tickets
python manage.py process_emails --verbose --dry-run

# Limit to specific folder
python manage.py process_emails --folder INBOX --verbose

# Limit number of emails processed
python manage.py process_emails --limit 5 --verbose
```

---

## Linux / Mac Setup

### Option 1: Cron Job (Recommended)

#### Step 1: Find Python path

```bash
which python
# Example output: /home/user/helpdesk/venv/bin/python
```

#### Step 2: Find Django project path

```bash
pwd
# Example: /home/user/helpdesk
```

#### Step 3: Edit crontab

```bash
crontab -e
```

#### Step 4: Add cron job

Add one of these lines to your crontab (in vim, press `i` to insert, then paste):

**Every 5 minutes:**
```cron
*/5 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails
```

**Every 10 minutes:**
```cron
*/10 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails
```

**Every hour at minute 0:**
```cron
0 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails
```

**Every 30 minutes during business hours (8am-6pm):**
```cron
*/30 8-18 * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails
```

#### Step 5: Save and verify

- In vim: Press `Esc`, then type `:wq` and press Enter
- Verify cron was added:
```bash
crontab -l
```

#### Step 6: Monitor logs

```bash
# View all cron logs
tail -f /var/log/syslog | grep process_emails

# Or check application logs
tail -f /home/user/helpdesk/logs/helpdesk.log | grep "Email processing"
```

---

### Option 2: Systemd Timer (Modern Linux)

If you prefer systemd instead of cron:

#### Step 1: Create service file

Create `/etc/systemd/system/helpdesk-process-emails.service`:

```ini
[Unit]
Description=Helpdesk Email Processing
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/home/user/helpdesk
Environment="PATH=/home/user/helpdesk/venv/bin"
ExecStart=/home/user/helpdesk/venv/bin/python manage.py process_emails
StandardOutput=journal
StandardError=journal
```

#### Step 2: Create timer file

Create `/etc/systemd/system/helpdesk-process-emails.timer`:

```ini
[Unit]
Description=Run Helpdesk Email Processing every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

#### Step 3: Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-process-emails.timer
sudo systemctl start helpdesk-process-emails.timer

# Check status
sudo systemctl status helpdesk-process-emails.timer

# View logs
journalctl -u helpdesk-process-emails.service -f
```

---

## Windows Setup

### Option 1: Task Scheduler (Recommended)

#### Step 1: Open Task Scheduler

- Press `Win + R`
- Type `taskschd.msc` and press Enter
- Or: Control Panel → Administrative Tools → Task Scheduler

#### Step 2: Create new task

1. Right-click on "Task Scheduler Library" → "Create Task..."
2. **General tab:**
   - Name: `Process Helpdesk Emails`
   - Description: `Automatically process incoming emails to create tickets`
   - Check: "Run whether user is logged in or not"
   - Check: "Run with highest privileges" (if needed)

#### Step 3: Configure triggers

1. Click **Triggers** tab
2. Click **New...**
3. Set up the schedule:
   - **Every 5 minutes:**
     - Begin the task: `On a schedule`
     - Recur every: `5 minutes`
     - Duration: `Indefinitely`
   - **Multiple times per day:**
     - Repeat task every: `30 minutes`
     - For a duration of: `23 hours 30 minutes`

#### Step 4: Configure action

1. Click **Actions** tab
2. Click **New...**
3. Configure the action:
   - Action: `Start a program`
   - Program/script: `C:\Python\pythonw.exe` (or path to your Python)
   - Add arguments: `manage.py process_emails`
   - Start in: `C:\path\to\helpdesk` (your project directory)

#### Step 5: Configure conditions

1. Click **Conditions** tab
2. Configure as needed:
   - Network: `Start only if connected to network`
   - Power: Adjust based on your needs

#### Step 6: Configure settings

1. Click **Settings** tab
2. Recommended settings:
   - Check: "Allow task to be run on demand"
   - Check: "Run task as soon as possible after a scheduled start is missed"
   - Check: "If the task fails, restart every: 5 minutes"
   - Retry count: `3`

#### Step 7: Test and save

1. Click **OK** to save
2. Right-click the task → **Run** to test
3. Check logs in `logs/helpdesk.log`

### Option 2: Batch Script + Task Scheduler

If you prefer a script approach:

#### Step 1: Create batch file

Create `process_emails.bat` in your project directory:

```batch
@echo off
REM Process Helpdesk Emails via Batch Script
cd /d "C:\path\to\helpdesk"
C:\Python\python.exe manage.py process_emails
```

#### Step 2: Configure Task Scheduler

Follow steps 1-2 above, then:

**Action:**
- Program/script: `C:\path\to\helpdesk\process_emails.bat`

---

## Environment Configuration

Ensure these are set in your `.env` file:

```env
# Email Configuration
IMAP_HOST=mail.aboro-it.net
IMAP_PORT=993
IMAP_USERNAME=support@aboro-it.net
IMAP_PASSWORD=your_password_here
IMAP_FOLDER=INBOX
IMAP_ENABLED=True

# For sending replies back to customers
SMTP_HOST=mail.aboro-it.net
SMTP_PORT=587
SMTP_USERNAME=support@aboro-it.net
SMTP_PASSWORD=your_password_here
EMAIL_HOST_USER=support@aboro-it.net
DEFAULT_FROM_EMAIL=support@aboro-it.net

# Site URL for email links
SITE_URL=https://help.aboro-it.net
```

---

## Monitoring & Logs

### View Recent Logs

```bash
# Last 50 lines of activity
tail -50 logs/helpdesk.log

# Follow logs in real-time
tail -f logs/helpdesk.log

# Filter for email processing only
grep "Email processing" logs/helpdesk.log

# Count processed emails
grep "Created new Ticket from email" logs/helpdesk.log | wc -l
```

### Check Last Run

```bash
# Linux/Mac
ls -lh logs/helpdesk.log

# Windows (from Command Prompt)
dir logs\helpdesk.log
```

### Database Query - See Email-Created Tickets

```bash
python manage.py shell

# In the shell:
from apps.tickets.models import Ticket

# Show all tickets created from email
email_tickets = Ticket.objects.filter(created_from_email=True).order_by('-created_at')
for ticket in email_tickets[:10]:
    print(f"{ticket.ticket_number}: {ticket.title} from {ticket.email_from}")

# Count total
email_tickets.count()

exit()
```

---

## Troubleshooting

### Problem: Command not found

```
Error: 'process_emails' is not a recognized command
```

**Solution:**
1. Verify `__init__.py` files exist:
   - `apps/tickets/management/__init__.py`
   - `apps/tickets/management/commands/__init__.py`
2. Restart Django application
3. Run: `python manage.py help` to list all commands

### Problem: IMAP Connection Failed

```
Error: Failed to connect to IMAP server: [Errno -3] name or service not known
```

**Solutions:**
1. Check credentials in `.env` file
2. Test connection manually:
   ```bash
   python manage.py shell
   from apps.tickets.email_handler import EmailToTicketHandler
   handler = EmailToTicketHandler()
   if handler.connect():
       print("Connection successful!")
       handler.disconnect()
   else:
       print("Connection failed!")
   exit()
   ```
3. Verify IMAP is enabled: `IMAP_ENABLED=True` in `.env`
4. Check firewall allows port 993 (SSL) or other configured port

### Problem: No Emails Processed

**Check:**
1. Verify IMAP_ENABLED=True in `.env`
2. Check for unread emails in the configured folder
3. Run with verbose flag: `python manage.py process_emails --verbose`
4. Check logs for errors: `tail logs/helpdesk.log`

### Problem: Tickets Not Being Created

**Solutions:**
1. Test with `--dry-run`: `python manage.py process_emails --dry-run --verbose`
2. Check database migrations: `python manage.py migrate`
3. Verify User model exists and can be created
4. Check logs for validation errors

### Problem: Windows Task Scheduler Not Running

**Solutions:**
1. Test manually first:
   ```cmd
   C:\path\to\helpdesk\process_emails.bat
   ```
2. Check task history in Task Scheduler
3. Verify Python path is correct
4. Verify working directory is set correctly
5. Run command prompt as Administrator and test
6. Check Event Viewer for system errors

### Problem: Cron Job Not Running (Linux)

**Solutions:**
1. Verify cron installed: `which cron`
2. Check if crond is running: `ps aux | grep crond`
3. Verify cron syntax: `sudo crontab -l`
4. Test command manually: `/home/user/helpdesk/venv/bin/python /home/user/helpdesk/manage.py process_emails`
5. Check mail for cron errors: `mail`
6. Redirect output to log file:
   ```cron
   */5 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails >> /var/log/helpdesk-emails.log 2>&1
   ```

---

## Advanced: Scheduling with Verbose Logging

### Save output to file (All platforms)

#### Linux/Mac:
```bash
# In crontab:
*/5 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails >> logs/cron-emails.log 2>&1
```

#### Windows (batch file):
```batch
@echo off
cd /d "C:\path\to\helpdesk"
C:\Python\python.exe manage.py process_emails >> logs\cron-emails.log 2>&1
```

### Use verbose mode for debugging

```cron
# Linux - verbose with timestamp
*/5 * * * * cd /home/user/helpdesk && /home/user/helpdesk/venv/bin/python manage.py process_emails --verbose >> logs/cron-emails-verbose.log 2>&1
```

---

## Performance Notes

- **Default behavior:** Processes all unread emails
- **Use `--limit`:** For high-volume mailboxes, limit emails per run:
  ```bash
  python manage.py process_emails --limit 10
  ```
- **Frequency:** Running every 5 minutes is good for most setups
- **Peak times:** Adjust frequency based on customer email volume
- **Database impact:** Each processed email = 1 ticket or comment creation (minimal impact)

---

## Summary

| Platform | Method | Command |
|----------|--------|---------|
| Linux/Mac | Cron | `*/5 * * * * cd /path && python manage.py process_emails` |
| Linux | Systemd | `systemctl enable helpdesk-process-emails.timer` |
| Windows | Task Scheduler | Create task with `pythonw.exe manage.py process_emails` |
| Windows | Batch | Create `.bat` file and schedule in Task Scheduler |
| All | Manual | `python manage.py process_emails --verbose` |

**No Celery required. No Redis required. Works everywhere.**
