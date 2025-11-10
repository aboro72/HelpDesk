@echo off
echo.
echo ========================================
echo   Django HTTPS Development Server
echo ========================================
echo.
echo Startet Django mit HTTPS (SSL/TLS)
echo URL: https://localhost:8000/
echo.
echo WICHTIG: 
echo - Selbstsigniertes Zertifikat wird verwendet
echo - Browser zeigt Sicherheitswarnung an
echo - Für Development: "Erweitert" -> "Trotzdem fortfahren"
echo.
echo Drücke Ctrl+C zum Beenden
echo.

python manage.py runsslserver 0.0.0.0:8000 --cert-file ssl/localhost.crt --key-file ssl/localhost.key