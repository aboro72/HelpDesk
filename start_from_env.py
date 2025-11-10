#!/usr/bin/env python3
"""
Universeller Server-Starter basierend auf .env-Konfiguration
Entscheidet automatisch zwischen HTTP und HTTPS
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def main():
    """Starte Server basierend auf .env-Einstellungen"""
    
    # .env-Datei laden
    load_dotenv()
    
    print("=" * 60)
    print(" HelpDesk Development Server (.env konfiguriert)")
    print("=" * 60)
    
    # Einstellungen aus .env lesen
    https_enabled = os.getenv('HTTPS_ENABLED', 'True').lower() == 'true'
    dev_host = os.getenv('DEV_HOST', 'localhost')
    dev_port = int(os.getenv('DEV_PORT', '8000'))
    
    # Argumente überschreiben .env
    host = sys.argv[1] if len(sys.argv) > 1 else dev_host
    port = int(sys.argv[2]) if len(sys.argv) > 2 else dev_port
    
    print(f"HTTPS aktiviert: {https_enabled}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("-" * 60)
    
    if https_enabled:
        # HTTPS-Server starten
        print("Starte HTTPS-Server...")
        cert_file = Path(os.getenv('SSL_CERT_FILE', 'ssl/localhost.crt'))
        key_file = Path(os.getenv('SSL_KEY_FILE', 'ssl/localhost.key'))
        
        # Prüfe SSL-Zertifikate
        if not (cert_file.exists() and key_file.exists()):
            print(f"WARNUNG: SSL-Zertifikate nicht gefunden!")
            print(f"Erstelle Zertifikate...")
            
            # Versuche Zertifikate zu erstellen
            result = subprocess.run([sys.executable, 'generate_ssl_cert.py'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("FEHLER: Zertifikat-Erstellung fehlgeschlagen!")
                print("Starte HTTP-Server als Fallback...")
                https_enabled = False
        
        if https_enabled:
            print(f"URL: https://{host}:{port}/")
            print("Browser-Warnung: 'Erweitert' -> 'Trotzdem fortfahren'")
            print("=" * 60)
            
            # HTTPS-Server ausführen
            subprocess.run([sys.executable, 'simple_https.py', str(port), host])
            return
    
    # HTTP-Server starten (Standard Django)
    print("Starte HTTP-Server...")
    print(f"URL: http://{host}:{port}/")
    print("=" * 60)
    
    # Standard Django-Server
    subprocess.run([sys.executable, 'manage.py', 'runserver', f'{host}:{port}'])

if __name__ == '__main__':
    main()