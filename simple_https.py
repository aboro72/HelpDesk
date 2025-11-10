#!/usr/bin/env python3
"""
Einfacher HTTPS Development Server mit Werkzeug
Liest Einstellungen aus .env-Datei
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

import django
django.setup()

from werkzeug.serving import run_simple
from django.core.wsgi import get_wsgi_application


def main():
    """Starte HTTPS Development Server"""
    
    # Einstellungen aus .env lesen
    https_enabled = os.getenv('HTTPS_ENABLED', 'True').lower() == 'true'
    host = os.getenv('HTTPS_HOST', 'localhost')
    port = int(os.getenv('HTTPS_PORT', '8000'))
    cert_file = Path(os.getenv('SSL_CERT_FILE', 'ssl/localhost.crt'))
    key_file = Path(os.getenv('SSL_KEY_FILE', 'ssl/localhost.key'))
    
    # Port aus Argumenten überschreibt .env
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Ungültiger Port: {sys.argv[1]}")
            return
    
    # Host aus Argumenten
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    # Prüfe HTTPS-Einstellungen
    if not https_enabled:
        print("HTTPS ist in .env deaktiviert (HTTPS_ENABLED=False)")
        print("Verwende HTTP-Server stattdessen:")
        print(f"python manage.py runserver {host}:{port}")
        return
    
    # SSL-Zertifikate prüfen
    if not (cert_file.exists() and key_file.exists()):
        print("FEHLER: SSL-Zertifikate nicht gefunden!")
        print(f"Erwartet: {cert_file} und {key_file}")
        print("Erstelle Zertifikate mit: python generate_ssl_cert.py")
        return
    
    print("=" * 60)
    print(" Django HTTPS Development Server (.env konfiguriert)")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL: https://{host}:{port}/")
    print(f"SSL-Cert: {cert_file}")
    print(f"SSL-Key: {key_file}")
    print("SSL: Selbstsigniertes Zertifikat")
    print("Browser-Warnung: 'Erweitert' -> 'Trotzdem fortfahren'")
    print("Beenden: Ctrl+C")
    print("=" * 60)
    print()
    
    # Django WSGI App
    application = get_wsgi_application()
    
    # SSL-Kontext
    ssl_context = (str(cert_file), str(key_file))
    
    try:
        run_simple(
            hostname=host,
            port=port,
            application=application,
            ssl_context=ssl_context,
            use_reloader=False,  # Deaktiviert Auto-Reload
            use_debugger=False,  # Deaktiviert Werkzeug-Debugger
            threaded=True,       # Multi-Threading aktiviert
        )
    except KeyboardInterrupt:
        print("\n[OK] Server gestoppt")
    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == '__main__':
    main()