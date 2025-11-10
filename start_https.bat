@echo off
title Django HTTPS Development Server
echo.
echo ==========================================
echo   Django HTTPS Development Server
echo ==========================================
echo.
echo [INFO] Starte Django mit HTTPS/SSL...
echo [INFO] URL: https://localhost:8000/
echo.
echo [WARNUNG] Selbstsigniertes Zertifikat
echo - Browser zeigt Sicherheitswarnung an
echo - Klicke "Erweitert" -> "Trotzdem fortfahren"
echo - Dies ist normal fuer Development
echo.
echo [STEUERUNG]
echo - Druecke Ctrl+C zum Beenden
echo - Fenster schliessen stoppt Server
echo.
echo ==========================================
echo.

cd /d "%~dp0"

REM Pruefe ob SSL-Zertifikate existieren
if not exist "ssl\localhost.crt" (
    echo [FEHLER] SSL-Zertifikat nicht gefunden!
    echo Erstelle Zertifikat...
    python generate_ssl_cert.py
    if errorlevel 1 (
        echo.
        echo [FALLBACK] Verwende HTTP-Server stattdessen...
        python manage.py runserver 0.0.0.0:8000
        pause
        exit
    )
)

REM Starte HTTPS-Server
echo [START] Django HTTPS-Server wird gestartet...
echo.
python simple_https.py 8000

echo.
echo [BEENDET] Django HTTPS-Server gestoppt.
pause