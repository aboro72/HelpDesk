@echo off
echo.
echo ==========================================
echo   HTTPS Server Neustart
echo ==========================================
echo.

REM Beende alle Python-Prozesse (falls Django läuft)
echo [INFO] Beende laufende Python-Prozesse...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1
timeout /t 2 >nul

echo [INFO] Starte HTTPS Development Server...
echo.
echo [WICHTIG] Verwende ab jetzt nur noch HTTPS:
echo           https://localhost:8000/
echo.
echo [WARNUNG] NICHT mehr http://localhost:8000/ verwenden!
echo.

REM Starte HTTPS-Server
python simple_https.py 8000

pause