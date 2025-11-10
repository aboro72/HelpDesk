@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    HelpDesk Windows Installation
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Dieses Skript muss als Administrator ausgefuehrt werden.
    echo Rechtsklick auf die .bat Datei und "Als Administrator ausfuehren" waehlen.
    pause
    exit /b 1
)

echo Waehlen Sie Ihren Webserver:
echo 1. Apache
echo 2. Nginx
echo 3. Ohne Webserver (nur PostgreSQL)
set /p webserver_choice="Ihre Wahl (1-3): "

if "%webserver_choice%"=="1" (
    set WEBSERVER=apache
    echo Apache wurde gewaehlt.
) else if "%webserver_choice%"=="2" (
    set WEBSERVER=nginx
    echo Nginx wurde gewaehlt.
) else if "%webserver_choice%"=="3" (
    set WEBSERVER=none
    echo Kein Webserver wurde gewaehlt.
) else (
    echo Ungueltige Auswahl. Installation wird abgebrochen.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    PostgreSQL Installation
echo ========================================

REM Check if PostgreSQL is already installed
where psql >nul 2>&1
if %errorLevel% equ 0 (
    echo PostgreSQL ist bereits installiert.
    goto configure_postgresql
)

echo Lade PostgreSQL 16 herunter...
if not exist "%TEMP%\postgresql-16-x64.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-16.1-1-windows-x64.exe' -OutFile '%TEMP%\postgresql-16-x64.exe'"
    if !errorLevel! neq 0 (
        echo FEHLER: PostgreSQL Download fehlgeschlagen.
        pause
        exit /b 1
    )
)

echo Installiere PostgreSQL...
"%TEMP%\postgresql-16-x64.exe" --mode unattended --unattendedmodeui none --superpassword "postgres" --servicename "postgresql-x64-16" --servicepassword "postgres" --serverport 5432 --datadir "C:\Program Files\PostgreSQL\16\data"
if %errorLevel% neq 0 (
    echo FEHLER: PostgreSQL Installation fehlgeschlagen.
    pause
    exit /b 1
)

REM Wait for PostgreSQL to start
echo Warte auf PostgreSQL Start...
timeout /t 10

:configure_postgresql
echo.
echo ========================================
echo    PostgreSQL Konfiguration
echo ========================================

set PGPASSWORD=postgres

echo Erstelle HelpDesk Datenbank...
"C:\Program Files\PostgreSQL\16\bin\createdb" -U postgres -h localhost helpdesk
if %errorLevel% neq 0 (
    echo Warnung: Datenbank existiert moeglicherweise bereits.
)

echo Erstelle HelpDesk Benutzer...
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -h localhost -c "CREATE USER helpdesk_user WITH PASSWORD 'helpdesk123';"
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE helpdesk TO helpdesk_user;"
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -h localhost -d helpdesk -c "GRANT ALL ON SCHEMA public TO helpdesk_user;"

echo PostgreSQL erfolgreich konfiguriert.
echo Datenbankname: helpdesk
echo Benutzer: helpdesk_user
echo Passwort: helpdesk123
echo Port: 5432

if "%WEBSERVER%"=="none" goto end

echo.
echo ========================================
echo    Webserver Installation
echo ========================================

if "%WEBSERVER%"=="apache" goto install_apache
if "%WEBSERVER%"=="nginx" goto install_nginx

:install_apache
echo Installiere Apache...

REM Download Apache
if not exist "%TEMP%\httpd-2.4.58-240718-win64-VS17.zip" (
    echo Lade Apache herunter...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.apachelounge.com/download/VS17/binaries/httpd-2.4.58-240718-win64-VS17.zip' -OutFile '%TEMP%\httpd-2.4.58-240718-win64-VS17.zip'"
)

REM Extract Apache
echo Extrahiere Apache...
powershell -Command "Expand-Archive -Path '%TEMP%\httpd-2.4.58-240718-win64-VS17.zip' -DestinationPath 'C:\' -Force"
move "C:\Apache24" "C:\Apache" >nul 2>&1

REM Configure Apache
echo Konfiguriere Apache...
echo ServerRoot "C:/Apache" > "C:\Apache\conf\httpd.conf.new"
echo Listen 80 >> "C:\Apache\conf\httpd.conf.new"
echo ServerName localhost:80 >> "C:\Apache\conf\httpd.conf.new"
echo DocumentRoot "C:/Apache/htdocs" >> "C:\Apache\conf\httpd.conf.new"
echo LoadModule rewrite_module modules/mod_rewrite.so >> "C:\Apache\conf\httpd.conf.new"
echo ^<Directory "C:/Apache/htdocs"^> >> "C:\Apache\conf\httpd.conf.new"
echo     Options Indexes FollowSymLinks >> "C:\Apache\conf\httpd.conf.new"
echo     AllowOverride All >> "C:\Apache\conf\httpd.conf.new"
echo     Require all granted >> "C:\Apache\conf\httpd.conf.new"
echo ^</Directory^> >> "C:\Apache\conf\httpd.conf.new"
move "C:\Apache\conf\httpd.conf.new" "C:\Apache\conf\httpd.conf"

REM Install Apache service
"C:\Apache\bin\httpd.exe" -k install
if %errorLevel% neq 0 (
    echo Warnung: Apache Service Installation fehlgeschlagen.
)

REM Start Apache
net start Apache2.4
echo Apache erfolgreich installiert und gestartet.
echo Webserver verfuegbar unter: http://localhost
goto end

:install_nginx
echo Installiere Nginx...

REM Download Nginx
if not exist "%TEMP%\nginx-1.25.3.zip" (
    echo Lade Nginx herunter...
    powershell -Command "Invoke-WebRequest -Uri 'http://nginx.org/download/nginx-1.25.3.zip' -OutFile '%TEMP%\nginx-1.25.3.zip'"
)

REM Extract Nginx
echo Extrahiere Nginx...
powershell -Command "Expand-Archive -Path '%TEMP%\nginx-1.25.3.zip' -DestinationPath 'C:\' -Force"
ren "C:\nginx-1.25.3" "nginx"

REM Configure Nginx
echo Konfiguriere Nginx...
echo server { > "C:\nginx\conf\nginx.conf.new"
echo     listen 80; >> "C:\nginx\conf\nginx.conf.new"
echo     server_name localhost; >> "C:\nginx\conf\nginx.conf.new"
echo     root C:/nginx/html; >> "C:\nginx\conf\nginx.conf.new"
echo     index index.html index.htm; >> "C:\nginx\conf\nginx.conf.new"
echo     location / { >> "C:\nginx\conf\nginx.conf.new"
echo         try_files $uri $uri/ =404; >> "C:\nginx\conf\nginx.conf.new"
echo     } >> "C:\nginx\conf\nginx.conf.new"
echo } >> "C:\nginx\conf\nginx.conf.new"

echo events { >> "C:\nginx\conf\nginx.conf.final"
echo     worker_connections 1024; >> "C:\nginx\conf\nginx.conf.final"
echo } >> "C:\nginx\conf\nginx.conf.final"
echo http { >> "C:\nginx\conf\nginx.conf.final"
type "C:\nginx\conf\nginx.conf.new" >> "C:\nginx\conf\nginx.conf.final"
echo } >> "C:\nginx\conf\nginx.conf.final"
move "C:\nginx\conf\nginx.conf.final" "C:\nginx\conf\nginx.conf"
del "C:\nginx\conf\nginx.conf.new"

REM Start Nginx
start "Nginx" "C:\nginx\nginx.exe"
echo Nginx erfolgreich installiert und gestartet.
echo Webserver verfuegbar unter: http://localhost

:end
echo.
echo ========================================
echo    Installation abgeschlossen
echo ========================================
echo.
echo PostgreSQL:
echo - Server: localhost:5432
echo - Datenbank: helpdesk
echo - Benutzer: helpdesk_user
echo - Passwort: helpdesk123
echo.

if not "%WEBSERVER%"=="none" (
    echo Webserver: %WEBSERVER%
    echo - URL: http://localhost
    echo.
)

echo Installation erfolgreich abgeschlossen!
pause