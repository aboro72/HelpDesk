# LLAMA3 Integration - Quick Start Guide

**5-Minuten-Setup für Jetson Orin NX**

---

## 🚀 Schnellstart

### 1. Ollama installieren (2 Minuten)

```bash
# Installation
curl -fsSL https://ollama.com/install.sh | sh

# Service starten
sudo systemctl start ollama
sudo systemctl enable ollama

# Status prüfen
sudo systemctl status ollama
```

### 2. LLAMA3-Modell laden (3 Minuten)

```bash
# Empfohlenes Modell für Jetson Orin NX 16GB
ollama pull llama3:8b

# Test
ollama run llama3:8b "Hallo, funktioniert das?"
```

### 3. Python-Dependency installieren

```bash
cd /home/user/PycharmProjects/HelpDesk
source venv/bin/activate
pip install ollama
```

### 4. Django-Konfiguration

Füge in `helpdesk/settings.py` hinzu:

```python
# LLAMA3 Configuration
USE_LLAMA3 = True
LLAMA3_MODEL = 'llama3:8b'
AI_PREFERRED_PROVIDER = 'llama3'
```

### 5. Performance-Modus aktivieren

```bash
# Jetson in MAX-Performance
sudo nvpmodel -m 0
sudo jetson_clocks
```

### 6. Django-Server neu starten

```bash
sudo systemctl restart helpdesk
# oder
python manage.py runserver
```

### 7. Testen

```bash
# Test-Script ausführen
python test_llama3.py
```

---

## ✅ Fertig!

LLAMA3 ist jetzt aktiv und übernimmt:
- ✅ Ticket-Kategorisierung (automatisch)
- ✅ Prioritäts-Vorschläge
- ✅ Chat-Auto-Responses

---

## 📊 Verifizieren

```bash
# Ollama läuft?
sudo systemctl status ollama

# GPU-Auslastung (während Betrieb)
nvidia-smi

# Django-Logs
tail -f logs/django.log | grep LLAMA3
```

---

## 🐛 Probleme?

**LLAMA3 nicht verfügbar:**
```bash
sudo systemctl restart ollama
ollama list  # Modell installiert?
```

**Zu langsam:**
```bash
# Kleineres Modell verwenden
ollama pull llama3:3b

# In settings.py:
LLAMA3_MODEL = 'llama3:3b'
```

**Out of Memory:**
```bash
# Swap erweitern
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 Weitere Dokumentation

- **Vollständige Anleitung**: `LLAMA3_JETSON_SETUP.md`
- **Integration-Details**: `LLAMA3_INTEGRATION_COMPLETE.md`
- **Test-Script**: `test_llama3.py`

---

**Das war's! LLAMA3 läuft jetzt lokal auf deinem Jetson Orin NX! 🎉**
