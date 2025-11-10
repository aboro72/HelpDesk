@echo off
echo.
echo ========================================
echo   Django HTTP Development Server
echo ========================================
echo.
echo Startet Django mit HTTP (Port 8000)
echo URL: http://localhost:8000/
echo.
echo WICHTIG: Verwende HTTP, nicht HTTPS!
echo HTTPS wird nur in Production unterstützt.
echo.
echo Drücke Ctrl+C zum Beenden
echo.

python manage.py runserver 0.0.0.0:8000