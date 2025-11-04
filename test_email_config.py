#!/usr/bin/env python
"""
Email Configuration Tester for Aboro-IT Helpdesk
Tests SMTP connection with different port and TLS configurations
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Email Configuration (ISPconfig Mail Server)
SMTP_HOST = "mail.aboro-it.net"  # Corrected from smtp.aboro-it.net
SENDER_EMAIL = "support@aboro-it.net"
SENDER_PASSWORD = "aokoTW#R2"
RECIPIENT_EMAIL = "a.borowczak@mlgruppe.de"

# Test configurations to try
TEST_CONFIGS = [
    {"name": "Port 587 mit TLS", "port": 587, "use_tls": True, "use_ssl": False},
    {"name": "Port 465 mit SSL", "port": 465, "use_tls": False, "use_ssl": True},
    {"name": "Port 25 mit TLS", "port": 25, "use_tls": True, "use_ssl": False},
    {"name": "Port 25 ohne TLS", "port": 25, "use_tls": False, "use_ssl": False},
    {"name": "Port 587 ohne TLS", "port": 587, "use_tls": False, "use_ssl": False},
]

def test_smtp_connection(config):
    """Test SMTP connection with given configuration"""
    print(f"\n{'='*70}")
    print(f"TEST: {config['name']}")
    print(f"{'='*70}")
    print(f"Host: {SMTP_HOST}")
    print(f"Port: {config['port']}")
    print(f"TLS: {config['use_tls']}")
    print(f"SSL: {config['use_ssl']}")
    print(f"Benutzer: {SENDER_EMAIL}")

    try:
        # Create SMTP connection
        if config['use_ssl']:
            print("\n-> Verbinde mit SSL...")
            server = smtplib.SMTP_SSL(SMTP_HOST, config['port'], timeout=10)
        else:
            print("\n-> Verbinde ohne SSL...")
            server = smtplib.SMTP(SMTP_HOST, config['port'], timeout=10)

        print("[OK] SMTP Verbindung erfolgreich!")

        # Test STARTTLS if configured
        if config['use_tls']:
            print("-> Starte TLS...")
            server.starttls()
            print("[OK] TLS erfolgreich gestartet!")

        # Login
        print(f"-> Melde mich an als {SENDER_EMAIL}...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("[OK] Login erfolgreich!")

        # Create test email
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECIPIENT_EMAIL
        message["Subject"] = f"Test Email - {config['name']}"

        body = f"""
Hallo,

Dies ist eine Test-Email von der Aboro-IT Helpdesk Konfiguration.

Konfiguration:
- Host: {SMTP_HOST}
- Port: {config['port']}
- TLS: {config['use_tls']}
- SSL: {config['use_ssl']}

Wenn du diese Email erhaeltst, funktioniert diese Konfiguration!

Viele Gruesse,
Helpdesk System
        """

        message.attach(MIMEText(body, "plain", "utf-8"))

        # Send email
        print(f"-> Sende Email an {RECIPIENT_EMAIL}...")
        server.send_message(message)
        print("[OK] Email erfolgreich versendet!")

        # Close connection
        server.quit()
        print("[OK] Verbindung geschlossen")

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[FEHLER] Authentifizierung fehlgeschlagen!")
        print(f"         Benutzername oder Passwort falsch?")
        print(f"         {str(e)}")
        return False
    except smtplib.SMTPException as e:
        print(f"[FEHLER] SMTP Fehler!")
        print(f"         {str(e)}")
        return False
    except ssl.SSLError as e:
        print(f"[FEHLER] SSL/TLS Fehler!")
        print(f"         {str(e)}")
        return False
    except ConnectionRefusedError:
        print(f"[FEHLER] Verbindung verweigert!")
        print(f"         Server antwortet nicht auf Port {config['port']}")
        return False
    except TimeoutError:
        print(f"[FEHLER] Timeout!")
        print(f"         Server antwortet nicht innerhalb von 10 Sekunden")
        return False
    except Exception as e:
        print(f"[FEHLER] {type(e).__name__}")
        print(f"         {str(e)}")
        return False

def main():
    print("=" * 70)
    print("EMAIL KONFIGURATION TESTER - Aboro-IT Helpdesk")
    print("=" * 70)

    print(f"\nZiel-Email: {RECIPIENT_EMAIL}")
    print(f"Absender: {SENDER_EMAIL}")
    print(f"\nTeste {len(TEST_CONFIGS)} verschiedene Konfigurationen...\n")

    results = []
    successful_configs = []

    for config in TEST_CONFIGS:
        success = test_smtp_connection(config)
        results.append((config['name'], success))
        if success:
            successful_configs.append(config)

    # Summary
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*70}\n")

    for config_name, success in results:
        status = "[OK] FUNKTIONIERT" if success else "[FEHLER] NICHT OK"
        print(f"{status:25} -> {config_name}")

    print(f"\n{'='*70}")

    if successful_configs:
        print(f"\nERFOLG! {len(successful_configs)} Konfiguration(en) funktionieren:\n")
        for config in successful_configs:
            print(f"  [OK] {config['name']}")
            print(f"       Port: {config['port']}")
            print(f"       TLS: {config['use_tls']}")
            print(f"       SSL: {config['use_ssl']}\n")

        # Django settings recommendation
        print("Django settings.py Konfiguration:")
        best_config = successful_configs[0]
        print(f"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '{SMTP_HOST}'
EMAIL_PORT = {best_config['port']}
EMAIL_USE_TLS = {best_config['use_tls']}
EMAIL_HOST_USER = '{SENDER_EMAIL}'
EMAIL_HOST_PASSWORD = '{SENDER_PASSWORD}'
DEFAULT_FROM_EMAIL = '{SENDER_EMAIL}'
""")
    else:
        print("\n[FEHLER] KEINE Konfiguration funktioniert!")
        print("\nMögliche Probleme:")
        print("  1. Benutzername oder Passwort falsch")
        print("  2. SMTP Server nicht erreichbar")
        print("  3. Firewall blockiert die Verbindung")
        print("  4. Server benötigt andere Authentifizierung")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen durch Benutzer.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)
