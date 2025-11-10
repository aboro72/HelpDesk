# ABoro-IT Chat Widget - Externe Integration

## 🚀 Problemlösung: Firefox Cross-Origin Fehler

Das Chat Widget wurde vollständig überarbeitet, um Cross-Origin-Probleme (insbesondere mit Firefox) zu beheben.

## ✅ Implementierte Lösungen

### 1. **Iframe-freie Widget-Implementierung** (Primary)
- Keine Abhängigkeit von iframes
- Direkte DOM-Erstellung der Chat-Oberfläche  
- CORS-kompatible API-Kommunikation
- Funktioniert in allen Browsern einschließlich Firefox

### 2. **Verbesserte Header-Konfiguration** (Fallback)
- Intelligente X-Frame-Options-Behandlung
- Content-Security-Policy-Optimierung für erlaubte Domains
- Domain-spezifische CORS-Header

### 3. **Lizenz-System-Anpassung**
- Widget funktioniert ohne Lizenz-Beschränkungen für externe Einbettung
- `embedded=true` Parameter umgeht interne Lizenz-Prüfungen

## 📋 Einbettungs-Code für externe Websites

```html
<!-- ABoro-IT Chat Widget (Firefox-kompatibel) -->
<script>
    // Optional: Widget Konfiguration
    window.AboroChatConfig = {
        chatHost: 'https://help.aboro-it.net',
        widgetColor: '#667eea',
        position: 'bottom-right',  // 'bottom-right' oder 'bottom-left'
        autoOpen: false,
        language: 'de'
    };
</script>
<script src="https://help.aboro-it.net/chat/widget.js" defer></script>
<!-- Ende Chat Widget -->
```

## 🔧 Technische Details

### **Widget-Architektur:**
1. **Iframe-freie Implementierung**: Erstellt Chat-Interface direkt im DOM
2. **API-basierte Kommunikation**: Verwendet `/chat/api/` Endpoints
3. **Real-time Polling**: Alle 3 Sekunden für neue Nachrichten
4. **Fallback-Mechanismus**: Bei iframe-Fehlern automatisch zur direkten Implementierung

### **Sicherheitsfeatures:**
- **Domain-Whitelist**: Konfigurierbar in Chat-Einstellungen
- **CORS-Beschränkungen**: Nur erlaubte Origins können API zugreifen
- **Origin-Validation**: Strikte Prüfung aller API-Requests

## ⚙️ Admin-Konfiguration

### **Erlaubte Domains verwalten:**
1. Django Admin → Chat → Chat Settings
2. Feld "Allowed domains" bearbeiten
3. Domains komma-getrennt eingeben: `https://domain1.com,https://domain2.com`

### **Widget-Einstellungen:**
- **Widget Color**: Hex-Farbcode für Buttons und Header
- **Widget Position**: `bottom-right` oder `bottom-left`
- **Offline Message**: Nachricht wenn keine Agents verfügbar
- **Welcome Message**: Begrüßungstext für neue Chats

## 🌐 Browser-Kompatibilität

| Browser | Status | Methode |
|---------|--------|---------|
| Firefox | ✅ Funktioniert | Iframe-freie Lösung |
| Chrome  | ✅ Funktioniert | Iframe-freie + Iframe |
| Safari  | ✅ Funktioniert | Iframe-freie + Iframe |
| Edge    | ✅ Funktioniert | Iframe-freie + Iframe |

## 🔍 Troubleshooting

### **Problem: Widget lädt nicht**
1. Prüfe Browser-Konsole auf Fehler
2. Prüfe ob Domain in erlaubten Domains steht
3. Teste mit `https://help.aboro-it.net/chat/widget-test/`

### **Problem: Chat startet nicht**
1. Prüfe Netzwerk-Tab auf API-Errors
2. Prüfe CORS-Header in Browser Developer Tools
3. Stelle sicher, dass Chat-Settings aktiviert sind

### **Problem: Nachrichten werden nicht übertragen**
1. Prüfe ob Polling funktioniert (alle 3 Sekunden API-Call)
2. Prüfe Session-ID in Local Storage
3. Prüfe ob CSRF-Exemption funktioniert

## 📡 API-Endpoints

| Endpoint | Methode | Zweck |
|----------|---------|-------|
| `/chat/widget/` | GET | Widget HTML (mit `embedded=true`) |
| `/chat/widget.js` | GET | Dynamisches Widget Script |
| `/chat/widget-data/` | GET | Widget-Konfiguration (JSON) |
| `/chat/api/start/` | POST | Chat-Session starten |
| `/chat/api/send/` | POST | Nachricht senden |
| `/chat/api/messages/{session_id}/` | GET | Nachrichten abrufen |

## 🧪 Testing

**Test-URL**: `https://help.aboro-it.net/chat/widget-test/`

Diese Seite zeigt:
- Widget-Status und Konfiguration
- Erlaubte Domains
- Steuerungsbuttons zum Testen
- Einbettungs-Code für externe Websites

## 🎯 Deployment-Checklist

- [ ] Domain zu erlaubten Domains hinzufügen
- [ ] Widget-Farbe und Position konfigurieren
- [ ] Einbettungs-Code auf Website einfügen
- [ ] Browser-Tests durchführen
- [ ] Agent-Dashboard für Chat-Betreuung einrichten

## 📞 Support

Bei Problemen:
- Test-Seite: `https://help.aboro-it.net/chat/widget-test/`
- Support: `support@aboro-it.net`
- Dokumentation: Diese Datei

---

**Version**: 2.0 (Firefox-kompatibel)  
**Letzte Aktualisierung**: November 2024