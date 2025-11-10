@echo off
title HelpDesk Development Server (.env konfiguriert)
echo.
echo ==========================================
echo   HelpDesk Development Server
echo   (.env-Konfiguration)
echo ==========================================
echo.
echo [INFO] Liest Einstellungen aus .env-Datei
echo [INFO] Host, Port, HTTPS aus .env oder Argumenten
echo.
echo Verwendung:
echo   start_server.bat [host] [port]
echo.
echo Beispiele:
echo   start_server.bat
echo   start_server.bat localhost 9000
echo   start_server.bat 0.0.0.0 8000
echo.
echo ==========================================
echo.

cd /d "%~dp0"

REM Parameter an Python-Script weiterleiten
python start_from_env.py %*

echo.
echo [BEENDET] Development Server gestoppt.
pause