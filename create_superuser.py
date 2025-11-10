#!/usr/bin/env python3
"""
Superuser für Django HelpDesk erstellen
Liest Standard-Einstellungen aus .env-Datei
"""
import os
import sys
import django
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from apps.accounts.models import User

def create_superuser():
    """Erstelle Superuser für HelpDesk"""
    
    print("=" * 50)
    print(" HelpDesk Superuser erstellen")
    print("=" * 50)
    
    # Prüfe ob bereits Superuser existiert
    if User.objects.filter(is_superuser=True).exists():
        print("✓ Superuser bereits vorhanden!")
        superuser = User.objects.filter(is_superuser=True).first()
        print(f"  Username: {superuser.username}")
        print(f"  Email: {superuser.email}")
        print()
        
        change = input("Neuen Superuser erstellen? (j/n): ").lower()
        if change != 'j':
            return
    
    print("\nSuperuser-Daten eingeben:")
    print("(Eingabe kann leer gelassen werden für .env-Standard-Werte)")
    print()
    
    # Standard-Werte aus .env lesen
    default_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    default_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@helpdesk.local')
    default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
    default_first_name = os.getenv('DEFAULT_ADMIN_FIRSTNAME', 'Admin')
    default_last_name = os.getenv('DEFAULT_ADMIN_LASTNAME', 'User')
    
    # Username
    username = input(f"Username [{default_username}]: ").strip()
    if not username:
        username = default_username
    
    # Email  
    email = input(f"Email [{default_email}]: ").strip()
    if not email:
        email = default_email
    
    # Password
    password = input(f"Password [{default_password}]: ").strip()
    if not password:
        password = default_password
    
    # Name
    first_name = input(f"Vorname [{default_first_name}]: ").strip()
    if not first_name:
        first_name = default_first_name
        
    last_name = input(f"Nachname [{default_last_name}]: ").strip()
    if not last_name:
        last_name = default_last_name
    
    print("\n" + "-" * 30)
    print("Erstelle Superuser...")
    
    try:
        # Lösche existierenden User falls vorhanden
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            print(f"Existierenden User '{username}' gelöscht")
        
        # Erstelle neuen Superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        
        print("✓ Superuser erfolgreich erstellt!")
        print()
        print("Login-Daten:")
        print(f"  URL: https://localhost:8000/auth/login/")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  Email: {email}")
        print()
        print("✓ Sie können sich jetzt einloggen!")
        
    except Exception as e:
        print(f"✗ Fehler beim Erstellen: {e}")
        return False
    
    return True

if __name__ == '__main__':
    create_superuser()