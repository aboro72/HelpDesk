#!/usr/bin/env python3
"""
SSL-Zertifikat Generator für HTTPS Development
Erstellt selbstsigniertes Zertifikat für localhost
"""
import os
import subprocess
import sys
from pathlib import Path

def check_openssl():
    """Prüfe ob OpenSSL verfügbar ist"""
    try:
        result = subprocess.run(['openssl', 'version'], 
                               capture_output=True, text=True, check=True)
        print(f"OpenSSL gefunden: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_certificate():
    """Generiere SSL-Zertifikat"""
    ssl_dir = Path('ssl')
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / 'localhost.crt'
    key_file = ssl_dir / 'localhost.key'
    
    # Prüfe ob Zertifikate bereits existieren
    if cert_file.exists() and key_file.exists():
        print(f"SSL-Zertifikate bereits vorhanden:")
        print(f"  - {cert_file}")
        print(f"  - {key_file}")
        
        response = input("Neue Zertifikate erstellen? (j/n): ").lower()
        if response != 'j':
            return True
    
    if not check_openssl():
        print("OpenSSL ist nicht verfügbar!")
        print("\nInstallationsoptionen:")
        print("1. Windows: choco install openssl")
        print("2. Windows: https://wiki.openssl.org/index.php/Binaries")
        print("3. Alternative: Verwende HTTP mit run_http.bat")
        return False
    
    print("Erstelle selbstsigniertes SSL-Zertifikat für localhost...")
    
    try:
        # OpenSSL Befehl für selbstsigniertes Zertifikat
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', str(key_file),
            '-out', str(cert_file),
            '-days', '365',
            '-nodes',
            '-subj', '/C=DE/ST=NRW/L=City/O=Development/CN=localhost'
        ]
        
        subprocess.run(cmd, check=True)
        
        print(f"\n[OK] SSL-Zertifikate erfolgreich erstellt:")
        print(f"  - Zertifikat: {cert_file}")
        print(f"  - Private Key: {key_file}")
        print(f"  - Gueltig fuer: localhost")
        print(f"  - Gueltigkeitsdauer: 365 Tage")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Erstellen der Zertifikate: {e}")
        return False

def create_config_file():
    """Erstelle OpenSSL Config für erweiterte Optionen"""
    config_content = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = DE
ST = NRW
L = Development
O = HelpDesk Development
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
"""
    
    with open('ssl/openssl.cnf', 'w') as f:
        f.write(config_content)

def generate_advanced_certificate():
    """Generiere erweiterte SSL-Zertifikate mit SAN"""
    ssl_dir = Path('ssl')
    ssl_dir.mkdir(exist_ok=True)
    
    create_config_file()
    
    cert_file = ssl_dir / 'localhost.crt'
    key_file = ssl_dir / 'localhost.key'
    config_file = ssl_dir / 'openssl.cnf'
    
    try:
        # Erstelle Private Key
        subprocess.run([
            'openssl', 'genrsa', '-out', str(key_file), '4096'
        ], check=True)
        
        # Erstelle Certificate Signing Request
        subprocess.run([
            'openssl', 'req', '-new', '-key', str(key_file),
            '-out', 'ssl/localhost.csr',
            '-config', str(config_file)
        ], check=True)
        
        # Erstelle selbstsigniertes Zertifikat
        subprocess.run([
            'openssl', 'x509', '-req', '-in', 'ssl/localhost.csr',
            '-signkey', str(key_file),
            '-out', str(cert_file),
            '-days', '365',
            '-extensions', 'v3_req',
            '-extfile', str(config_file)
        ], check=True)
        
        # Aufräumen
        os.remove('ssl/localhost.csr')
        
        print(f"\n✓ Erweiterte SSL-Zertifikate erstellt:")
        print(f"  - Zertifikat: {cert_file}")
        print(f"  - Private Key: {key_file}")
        print(f"  - Unterstützt: localhost, 127.0.0.1")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler: {e}")
        return False

def main():
    print("SSL-Zertifikat Generator für Django HTTPS Development")
    print("=" * 55)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--advanced':
        success = generate_advanced_certificate()
    else:
        success = generate_certificate()
    
    if success:
        print(f"\n🚀 Starte HTTPS-Server mit:")
        print(f"   python manage.py runsslserver 0.0.0.0:8000")
        print(f"   oder verwende: run_https.bat")
        print(f"\n📝 URL: https://localhost:8000/")
        print(f"\n⚠️  Browser-Warnung:")
        print(f"   Klicke 'Erweitert' -> 'Trotzdem zu localhost (unsicher)'")
        
        if '--auto-start' in sys.argv:
            print(f"\nStarte HTTPS-Server automatisch...")
            subprocess.run([sys.executable, 'manage.py', 'runsslserver', '0.0.0.0:8000'])
    else:
        print(f"\n❌ Zertifikat-Erstellung fehlgeschlagen")
        print(f"   Verwende HTTP-Server: python manage.py runserver")

if __name__ == '__main__':
    main()