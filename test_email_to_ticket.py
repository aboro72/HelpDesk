"""
Test script for email-to-ticket system

This script tests the email processing functionality without Celery.
It demonstrates:
1. IMAP connection
2. Email extraction
3. Ticket number detection
4. Dry-run mode
5. Verbose output
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from apps.tickets.email_handler import EmailToTicketHandler
from django.conf import settings


def test_imap_connection():
    """Test IMAP connection"""
    print("\n" + "="*60)
    print("TEST 1: IMAP Connection")
    print("="*60)

    handler = EmailToTicketHandler()

    print(f"IMAP Host: {handler.imap_host}")
    print(f"IMAP Port: {handler.imap_port}")
    print(f"IMAP Username: {handler.imap_username}")
    print(f"IMAP Folder: {handler.imap_folder}")
    print(f"IMAP Enabled: {settings.IMAP_ENABLED}")

    if not settings.IMAP_ENABLED:
        print("\nWARNING: IMAP is not enabled in settings!")
        print("To enable, set IMAP_ENABLED=True in your .env file")
        return False

    print("\nAttempting connection...")
    if handler.connect():
        print("SUCCESS: Connected to IMAP server")
        handler.disconnect()
        return True
    else:
        print("FAILED: Could not connect to IMAP server")
        print("Check your IMAP credentials in .env file")
        return False


def test_email_parsing():
    """Test email header parsing"""
    print("\n" + "="*60)
    print("TEST 2: Email Header Parsing")
    print("="*60)

    handler = EmailToTicketHandler()

    # Test ticket ID extraction
    test_subjects = [
        "[TICKET-001] Problem with account",
        "RE: [TICKET-123] - Follow up",
        "#42 - Support request",
        "Ticket #99 - Feature request",
        "RE: [TICKET-005]",
        "No ticket number here"
    ]

    print("Testing ticket number extraction from subjects:\n")
    for subject in test_subjects:
        ticket_id = handler.extract_ticket_id(subject)
        status = "FOUND" if ticket_id else "NOT FOUND"
        print(f"  {status}: '{subject}'")
        if ticket_id:
            print(f"          -> Ticket #{ticket_id}")


def test_dry_run():
    """Test dry-run mode"""
    print("\n" + "="*60)
    print("TEST 3: Dry-Run Mode")
    print("="*60)

    if not settings.IMAP_ENABLED:
        print("\nSkipping dry-run test (IMAP not enabled)")
        print("Enable IMAP_ENABLED=True in .env to test")
        return

    handler = EmailToTicketHandler(verbose=True, dry_run=True)

    print("\nProcessing emails in dry-run mode (no data will be saved)...")
    created, updated, errors = handler.process_emails()

    print(f"\nResults:")
    print(f"  Created: {created} (would have been created)")
    print(f"  Updated: {updated} (would have been updated)")
    print(f"  Errors: {errors}")


def test_management_command():
    """Test management command"""
    print("\n" + "="*60)
    print("TEST 4: Management Command")
    print("="*60)

    print("\nThe management command can be run with:")
    print("\n  python manage.py process_emails")
    print("    - Process all unread emails")
    print("\n  python manage.py process_emails --verbose")
    print("    - Show detailed output")
    print("\n  python manage.py process_emails --dry-run --verbose")
    print("    - Test without creating tickets")
    print("\n  python manage.py process_emails --limit 5 --verbose")
    print("    - Process only 5 emails")
    print("\n  python manage.py process_emails --folder INBOX --verbose")
    print("    - Process specific IMAP folder")

    print("\n\nFor scheduling (Linux/Mac cron):")
    print("  */5 * * * * cd /path/to/helpdesk && python manage.py process_emails")

    print("\n\nFor Windows Task Scheduler:")
    print("  Program: C:\\Python\\pythonw.exe")
    print("  Arguments: manage.py process_emails")
    print("  Start in: C:\\path\\to\\helpdesk")


def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("  Email-to-Ticket System Test Suite")
    print("*" * 60)

    # Test 1: IMAP Connection
    imap_ok = test_imap_connection()

    # Test 2: Email parsing
    test_email_parsing()

    # Test 3: Dry-run (only if IMAP enabled)
    if imap_ok:
        test_dry_run()

    # Test 4: Management command info
    test_management_command()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if imap_ok:
        print("\nIMPORTANT: Enable email processing by setting in .env:")
        print("  IMAP_ENABLED=True")
        print("\nThen schedule the management command to run automatically:")
        print("  - Via cron (Linux/Mac)")
        print("  - Via Task Scheduler (Windows)")
        print("\nSee SCHEDULER_SETUP.md for detailed instructions")
    else:
        print("\nTo enable email processing:")
        print("\n1. Check IMAP configuration in .env:")
        print(f"   IMAP_HOST={settings.IMAP_HOST}")
        print(f"   IMAP_PORT={settings.IMAP_PORT}")
        print(f"   IMAP_USERNAME={settings.IMAP_USERNAME}")
        print(f"   IMAP_PASSWORD=***")
        print(f"   IMAP_ENABLED={settings.IMAP_ENABLED}")
        print("\n2. Update credentials if needed")
        print("\n3. Run this test again: python test_email_to_ticket.py")
        print("\n4. See SCHEDULER_SETUP.md for complete setup guide")

    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
