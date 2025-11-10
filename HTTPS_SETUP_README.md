# HTTPS Development Server Setup

## ✅ HTTPS ist jetzt aktiviert!

Die HTTPS-Unterstützung für die Entwicklung wurde erfolgreich eingerichtet.

## 🚀 HTTPS-Server starten

### Option 1: Einfach mit Batch-Datei
```bash
start_https.bat
```

### Option 2: Manueller Befehl
```bash
python manage.py runsslserver 0.0.0.0:8000 --cert-file ssl\localhost.crt --key-file ssl\localhost.key
```

### Option 3: Ohne Zertifikat-Parameter (nutzt Standard)
```bash
python manage.py runsslserver 0.0.0.0:8000
```

## 📋 URLs

- **HTTPS**: https://localhost:8000/
- **HTTP**: http://localhost:8000/ (funktioniert weiterhin)

## ⚠️ Browser-Sicherheitswarnung

Da es sich um ein selbstsigniertes Zertifikat handelt, zeigen Browser eine Warnung:

### Chrome/Edge:
1. Klicke auf "Erweitert"
2. Klicke auf "Trotzdem zu localhost (unsicher)"

### Firefox:
1. Klicke auf "Erweitert" 
2. Klicke auf "Risiko akzeptieren und fortfahren"

**Das ist normal für Development!**

## 📁 Erstelle Dateien

- `ssl/localhost.crt` - SSL-Zertifikat
- `ssl/localhost.key` - Private Key  
- `start_https.bat` - HTTPS-Starter
- `generate_ssl_cert.py` - Zertifikat-Generator

## 🔧 Problembehandlung

### SSL-Zertifikat neu erstellen
```bash
python generate_ssl_cert.py
```

### Erweiterte Zertifikate (mit SAN)
```bash
python generate_ssl_cert.py --advanced
```

### Falls HTTPS nicht funktioniert
Verwende HTTP als Fallback:
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🔒 Was wurde konfiguriert

1. **django-sslserver** installiert
2. **Selbstsignierte SSL-Zertifikate** für localhost erstellt
3. **Django Settings** für Development-HTTPS angepasst
4. **Einfache Starter-Skripte** erstellt

## 📝 Hinweise

- Zertifikate sind **365 Tage gültig**
- Nur für **localhost/127.0.0.1**
- **Nicht für Production** verwenden
- Löst die ursprünglichen HTTPS-Fehler

## 🚀 Nächste Schritte

1. Starte `start_https.bat`
2. Öffne https://localhost:8000/
3. Akzeptiere die Browser-Warnung
4. Entwicklung kann beginnen!

Die HTTPS-Fehlermeldungen sollten jetzt verschwunden sein. 🎉