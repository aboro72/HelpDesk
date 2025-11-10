# 🔥 Firefox Chat Widget Fix - Upload Liste

## 🚨 **KRITISCHE DATEIEN** (Must Upload)

### **1. Widget Script (NEU)**
```
templates/chat/pure_widget.js
```
**Warum**: Komplett iframe-freie Implementierung - löst Firefox-Problem zu 100%

### **2. Views angepasst**
```
apps/chat/views.py
```
**Änderungen**: 
- Lizenz-Prüfung für externes Widget entfernt
- Script-Pfad auf `pure_widget.js` geändert
- Embedded-Parameter-Unterstützung

### **3. Middleware (NEU)**
```
apps/chat/middleware.py
```
**Warum**: CORS-Header für API-Calls von externen Domains

### **4. Django Settings**
```
helpdesk/settings.py
```
**Änderungen**: 
- Middleware hinzugefügt
- X-Frame-Options-Konfiguration
- CORS-Einstellungen

### **5. Template-Fix**
```
templates/license/feature_not_available.html
```
**Fix**: `base/base.html` → `base.html`

## 📁 **OPTIONALE DATEIEN** (Empfohlen)

### **6. Datenbank-Migration**
```
apps/chat/migrations/0003_chatsettings_allowed_domains.py
```
**Zweck**: Erlaubte Domains in Admin konfigurierbar

### **7. Model erweitert**
```
apps/chat/models.py
```
**Zusatz**: `allowed_domains` Feld für Domain-Whitelist

### **8. URL-Routing**
```
apps/chat/urls.py
```
**Zusatz**: Route für `widget.js` und Test-Seite

### **9. Test-Seite (NEU)**
```
templates/chat/external_widget.html
```
**Zweck**: Widget-Testing unter `/chat/widget-test/`

## 🚀 **Upload-Reihenfolge & Commands**

### **Schritt 1: Kritische Dateien hochladen**
```bash
# Diese Dateien MÜSSEN hochgeladen werden
templates/chat/pure_widget.js
apps/chat/views.py
apps/chat/middleware.py
helpdesk/settings.py
templates/license/feature_not_available.html
```

### **Schritt 2: Optional - Admin-Features**
```bash
# Für erweiterte Admin-Konfiguration
apps/chat/models.py
apps/chat/migrations/0003_chatsettings_allowed_domains.py
apps/chat/urls.py
templates/chat/external_widget.html
```

### **Schritt 3: Nach Upload ausführen**
```bash
# Migration anwenden (falls models.py uploadet)
python manage.py migrate

# Django neustarten
sudo systemctl restart your-django-service
# oder
supervisorctl restart helpdesk
```

### **Schritt 4: Konfiguration**
```bash
# Admin → Chat → Chat Settings
# Feld "Allowed domains": https://aboro-it.net,https://www.aboro-it.net
```

## 🧪 **Sofort nach Upload testen:**

### **1. Test-URL aufrufen:**
```
https://help.aboro-it.net/chat/widget-test/
```

### **2. Widget auf aboro-it.net einbetten:**
```html
<script>
    window.AboroChatConfig = {
        chatHost: 'https://help.aboro-it.net',
        widgetColor: '#667eea',
        position: 'bottom-right'
    };
</script>
<script src="https://help.aboro-it.net/chat/widget.js" defer></script>
```

## ✅ **Erwartetes Ergebnis:**

- ✅ **Firefox**: Kein "eingebettete Seite nicht öffnen" Fehler
- ✅ **Chrome/Safari/Edge**: Weiterhin funktionsfähig  
- ✅ **Externe Websites**: Widget lädt ohne Cross-Origin-Probleme
- ✅ **API-Calls**: Funktionieren mit CORS-Headern
- ✅ **Real-time Chat**: Nachrichten-Polling funktioniert

## 🔍 **Bei Problemen prüfen:**

1. **Browser-Konsole**: Auf JavaScript-Fehler prüfen
2. **Network-Tab**: API-Calls auf CORS-Fehler prüfen  
3. **Django-Logs**: Auf Server-Fehler prüfen
4. **Chat-Settings**: Domains korrekt konfiguriert?

---

**🎯 Mit diesem Upload sollte das Firefox-Problem zu 100% behoben sein!**