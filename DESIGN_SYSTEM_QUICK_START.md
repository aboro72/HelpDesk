# 🎨 Design-System Quick Start

## ✨ Was wurde implementiert

### 1. **Theme Settings Model** ✅
- 8 neue Felder in SystemSettings Model
- Color Picker Felder
- Font-Auswahl  
- Border-Radius Einstellung
- Dark Mode Toggle

### 2. **Admin Settings Form** ✅
- Theme-Customization Section
- Color-Picker Inputs für Admins
- Font-Family Dropdown
- Border-Radius Slider

### 3. **CSS Theme System** ✅
- `static/css/theme.css` mit CSS Custom Properties
- 4 vordefinierte Theme-Varianten:
  - Default (Modern Blue)
  - Professional (Dark Blue)
  - Bright (Orange)
  - Custom (Admin-konfiguriert)
- Dark Mode Support
- Responsive Design

---

## 🚀 Wie man es benutzt

### Für Admins:
1. Gehen Sie zu `/settings/`
2. Scrollen Sie zur "Design Theme" Sektion
3. Wählen Sie ein vordefiniertes Theme
4. Oder wählen Sie "Custom" und passen Farben an
5. Speichern Sie

### Farben die angepasst werden können:
- **Primärfarbe:** Für Buttons, Links, Navbar
- **Sekundärfarbe:** Für Success States
- **Akzentfarbe:** Für wichtige CTAs
- **Warnfarbe:** Für Fehler/Warnungen

---

## 📋 Nächste Schritte (Für spätere Implementierung)

### Phase 2: Full Integration
1. [ ] base.html: `<link rel="stylesheet" href="{% static 'css/theme.css' %}">`
2. [ ] Theme Context Processor: Injiziert Colors als CSS Variables
3. [ ] JavaScript Theme Switcher: Live-Preview in Settings
4. [ ] Migration: Database Migration für neue Theme Felder

### Phase 3: Advanced Features  
1. [ ] Dark Mode Auto-Detect
2. [ ] Theme Export/Import
3. [ ] Custom Font Upload
4. [ ] Theme Preview Generator

---

## 💾 Database Migration

Bevor Sie die App starten, führen Sie folgendes aus:

```bash
python manage.py makemigrations admin_panel
python manage.py migrate
```

---

## 📄 Dateien die geändert/erstellt wurden

| Datei | Status |
|-------|--------|
| `apps/admin_panel/models.py` | ✏️ Geändert - 8 neue Theme-Felder |
| `apps/main/forms.py` | ✏️ Geändert - Theme-Customization Form Fields |
| `static/css/theme.css` | ✨ NEU - Komplettes Theme-System |

---

## 🎯 Defaults der Themes

### Default (Modern Blue)
```
Primary: #0066CC (Blau)
Secondary: #00B366 (Grün)
Accent: #FF6600 (Orange)
Danger: #CC0000 (Rot)
```

### Professional (Dark Blue)
```
Primary: #1C3A70 (Dunkelblau)
Secondary: #2E5090 (Marine)
Accent: #0066CC (Blau)
```

### Bright (Orange)
```
Primary: #FF6600 (Orange)
Secondary: #FFB300 (Gelb)
Accent: #FF3D00 (Rot-Orange)
```

---

## 🔧 Manueller Setup (Falls nötig)

### In base.html hinzufügen (im `<head>`):
```html
<link rel="stylesheet" href="{% static 'css/theme.css' %}">
<style>
  :root {
    --primary-color: {{ system_settings.primary_color }};
    --secondary-color: {{ system_settings.secondary_color }};
    --accent-color: {{ system_settings.accent_color }};
    --danger-color: {{ system_settings.danger_color }};
    --border-radius: {{ system_settings.border_radius }}px;
  }
</style>
```

### Oder Context Processor (später):
```python
def theme_context(request):
    settings = SystemSettings.get_settings()
    return {
        'theme_colors': {
            'primary': settings.primary_color,
            'secondary': settings.secondary_color,
            'accent': settings.accent_color,
        }
    }
```

---

## ⚠️ Wichtig für Production

1. **Cache löschen nach Theme-Änderung:**
   ```bash
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.delete('admin_system_settings')
   ```

2. **Statische Dateien sammeln:**
   ```bash
   python manage.py collectstatic
   ```

3. **Django neu starten:**
   ```bash
   sudo systemctl restart helpdesk
   ```

---

## 📚 Weitere Ressourcen

- CSS Custom Properties Docs: https://developer.mozilla.org/en-US/docs/Web/CSS/--*
- Django Template Context Processors: https://docs.djangoproject.com/en/5.0/ref/templates/api/
- Color Accessibility: https://webaim.org/articles/contrast/

---

**Status:** Alpha Version - Grundstruktur vorhanden, Integration im nächsten Sprint
**Nächste Phase:** Context Processor Integration, JS Live-Preview
