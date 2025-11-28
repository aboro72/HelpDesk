"""
Gunicorn Konfiguration für ML Gruppe Helpdesk
"""
import multiprocessing
import os

# Pfad zum Projekt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Bind-Adresse
# 0.0.0.0 = von allen Netzwerk-Interfaces erreichbar
# Für Zugriff vom ISPConfig3-Server (192.168.0.20)
bind = "0.0.0.0:8000"

# Worker-Prozesse (empfohlen: 2-4 x CPU-Kerne)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker-Klasse
worker_class = "sync"

# Timeout für Worker
timeout = 120

# Max. Anzahl der Requests pro Worker, bevor er neu gestartet wird
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = os.path.join(BASE_DIR, "logs", "gunicorn_access.log")
errorlog = os.path.join(BASE_DIR, "logs", "gunicorn_error.log")
loglevel = "info"

# Prozess-Name
proc_name = "helpdesk"

# Daemon-Modus (False, da systemd den Prozess verwaltet)
daemon = False

# PID-Datei
pidfile = os.path.join(BASE_DIR, "gunicorn.pid")

# User/Group (wird von systemd überschrieben)
# user = "user"
# group = "user"

# Preload der Anwendung für bessere Performance
preload_app = True

# Umgebungsvariablen
raw_env = [
    f"DJANGO_SETTINGS_MODULE=helpdesk.settings",
]
