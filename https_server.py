#!/usr/bin/env python3
"""
HTTPS Development Server für Django
Alternative zu django-sslserver
"""
import os
import sys
import ssl
import socket
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import BaseServer
from wsgiref.simple_server import WSGIRequestHandler

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.conf import settings


class HTTPSServer(WSGIServer):
    """HTTPS-fähiger WSGI Server"""
    
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        
        # SSL-Kontext erstellen
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Zertifikat und Key laden
        cert_file = Path('ssl/localhost.crt')
        key_file = Path('ssl/localhost.key')
        
        if not (cert_file.exists() and key_file.exists()):
            print("FEHLER: SSL-Zertifikate nicht gefunden!")
            print("Führe aus: python generate_ssl_cert.py")
            sys.exit(1)
        
        self.context.load_cert_chain(str(cert_file), str(key_file))
        
        # Socket erstellen und binden
        self.socket = socket.socket(self.address_family, self.socket_type)
        
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise
    
    def server_bind(self):
        """Socket binden"""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()
    
    def server_activate(self):
        """Server aktivieren mit SSL"""
        self.socket.listen(self.request_queue_size)
        # SSL-Wrapper um Socket
        self.socket = self.context.wrap_socket(self.socket, server_side=True)
    
    def get_request(self):
        """Request mit SSL-Support"""
        return self.socket.accept()


class QuietWSGIRequestHandler(WSGIRequestHandler):
    """Weniger verbose Request Handler"""
    
    def log_message(self, format, *args):
        """Nur wichtige Meldungen loggen"""
        if "GET" in format or "POST" in format:
            return  # Requests nicht loggen
        super().log_message(format, *args)


def run_https_server(host='0.0.0.0', port=8000):
    """HTTPS Development Server starten"""
    
    print("=" * 60)
    print(" Django HTTPS Development Server")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"URL:  https://localhost:{port}/")
    print()
    print("SSL-Zertifikat: Selbstsigniert für localhost")
    print("Browser-Warnung: 'Erweitert' -> 'Trotzdem fortfahren'")
    print()
    print("Drücke Ctrl+C zum Beenden")
    print("=" * 60)
    print()
    
    # Django WSGI Application
    application = get_wsgi_application()
    
    try:
        # HTTPS Server erstellen
        server = make_server(
            host, port, application,
            server_class=HTTPSServer,
            handler_class=QuietWSGIRequestHandler
        )
        
        print(f"[OK] HTTPS Server laeuft auf https://{host}:{port}/")
        print("Warte auf Requests...")
        print()
        
        # Server starten
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\\n\\n[OK] Server beendet")
    except Exception as e:
        print(f"\\n[ERROR] Server-Fehler: {e}")
        if "certificate verify failed" in str(e):
            print("Tipp: python generate_ssl_cert.py")
    finally:
        try:
            server.server_close()
        except:
            pass


def main():
    """Hauptfunktion"""
    port = 8000
    host = '0.0.0.0'
    
    # Port aus Argumenten lesen
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Ungültiger Port: {sys.argv[1]}")
            sys.exit(1)
    
    # Host aus Argumenten lesen
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_https_server(host, port)


if __name__ == '__main__':
    main()