#!/usr/bin/env python3
"""
HTTPS Development Server für Django
Löst die HTTPS-Fehlermeldungen beim Testen
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.management.base import BaseCommand

def main():
    """HTTPS Development Server starten"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
    
    # SSL-Zertifikat erstellen falls nicht vorhanden
    cert_file = 'localhost.crt'
    key_file = 'localhost.key'
    
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        print("Erstelle SSL-Zertifikat für HTTPS...")
        import subprocess
        try:
            # Selbstsigniertes Zertifikat erstellen
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', 
                '-keyout', key_file, '-out', cert_file, 
                '-days', '365', '-nodes', '-subj', 
                '/C=DE/ST=State/L=City/O=Organization/CN=localhost'
            ], check=True)
            print(f"SSL-Zertifikat erstellt: {cert_file}, {key_file}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("OpenSSL nicht gefunden. Installiere OpenSSL oder verwende HTTP.")
            print("Alternative: pip install django-sslserver")
            return
    
    # Django mit SSL starten
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '8000'
    
    print(f"\nStarting HTTPS Django Server on port {port}")
    print(f"URL: https://localhost:{port}/")
    print("Warnung: Selbstsigniertes Zertifikat - Browser wird Warnung anzeigen")
    print("Akzeptieren Sie die Warnung für Entwicklung\n")
    
    # Versuche django-sslserver zu verwenden
    try:
        from django_sslserver.management.commands.runsslserver import Command
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
        django.setup()
        
        # SSL Server starten
        command = Command()
        command.run_from_argv(['manage.py', 'runsslserver', f'0.0.0.0:{port}'])
        
    except ImportError:
        print("django-sslserver nicht installiert")
        print("Installiere mit: pip install django-sslserver")
        print("Oder verwende HTTP-Server mit: python manage.py runserver")

if __name__ == '__main__':
    main()