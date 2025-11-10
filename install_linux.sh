#!/bin/bash

# HelpDesk Linux Installation Script
# Unterstützt Ubuntu/Debian, CentOS/RHEL/Rocky Linux

set -e

COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'

log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_NC} $1"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_NC} $1"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_NC} $1"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Dieses Skript muss als root ausgefuehrt werden."
        log_info "Verwenden Sie: sudo $0"
        exit 1
    fi
}

detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    else
        log_error "Kann Betriebssystem nicht erkennen."
        exit 1
    fi
    
    log_info "Erkanntes OS: $OS $OS_VERSION"
}

choose_webserver() {
    echo
    echo "========================================="
    echo "    Webserver Auswahl"
    echo "========================================="
    echo "1. Apache"
    echo "2. Nginx"
    echo "3. Ohne Webserver (nur PostgreSQL)"
    
    while true; do
        read -p "Ihre Wahl (1-3): " webserver_choice
        case $webserver_choice in
            1)
                WEBSERVER="apache"
                log_info "Apache wurde gewaehlt."
                break
                ;;
            2)
                WEBSERVER="nginx"
                log_info "Nginx wurde gewaehlt."
                break
                ;;
            3)
                WEBSERVER="none"
                log_info "Kein Webserver wurde gewaehlt."
                break
                ;;
            *)
                log_warning "Ungueltige Auswahl. Bitte 1, 2 oder 3 eingeben."
                ;;
        esac
    done
}

install_postgresql_debian() {
    log_info "Installiere PostgreSQL auf Debian/Ubuntu..."
    
    # Update package list
    apt-get update
    
    # Install PostgreSQL
    apt-get install -y postgresql postgresql-contrib
    
    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    log_success "PostgreSQL erfolgreich installiert."
}

install_postgresql_redhat() {
    log_info "Installiere PostgreSQL auf RedHat/CentOS..."
    
    # Install PostgreSQL repository
    if [[ "$OS_VERSION" == "8" ]] || [[ "$OS_VERSION" == "9" ]]; then
        dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-${OS_VERSION}-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        dnf install -y postgresql16-server postgresql16
    else
        yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        yum install -y postgresql16-server postgresql16
    fi
    
    # Initialize database
    /usr/pgsql-16/bin/postgresql-16-setup initdb
    
    # Start and enable PostgreSQL
    systemctl start postgresql-16
    systemctl enable postgresql-16
    
    # Add PostgreSQL to PATH
    echo 'export PATH=/usr/pgsql-16/bin:$PATH' >> /etc/profile
    
    log_success "PostgreSQL erfolgreich installiert."
}

configure_postgresql() {
    log_info "Konfiguriere PostgreSQL..."
    
    # Set postgres user password
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
    
    # Create helpdesk database
    sudo -u postgres createdb helpdesk || log_warning "Datenbank existiert moeglicherweise bereits."
    
    # Create helpdesk user
    sudo -u postgres psql -c "CREATE USER helpdesk_user WITH PASSWORD 'helpdesk123';" || log_warning "Benutzer existiert moeglicherweise bereits."
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE helpdesk TO helpdesk_user;"
    sudo -u postgres psql -d helpdesk -c "GRANT ALL ON SCHEMA public TO helpdesk_user;"
    
    # Configure PostgreSQL for local connections
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP 'PostgreSQL \K[0-9]+')
    
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        PG_CONFIG_DIR="/etc/postgresql/${PG_VERSION}/main"
    else
        PG_CONFIG_DIR="/var/lib/pgsql/${PG_VERSION}/data"
    fi
    
    # Enable password authentication
    if [[ -f "${PG_CONFIG_DIR}/pg_hba.conf" ]]; then
        cp "${PG_CONFIG_DIR}/pg_hba.conf" "${PG_CONFIG_DIR}/pg_hba.conf.backup"
        sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "${PG_CONFIG_DIR}/pg_hba.conf"
        sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' "${PG_CONFIG_DIR}/pg_hba.conf"
    fi
    
    # Restart PostgreSQL
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        systemctl restart postgresql
    else
        systemctl restart postgresql-16
    fi
    
    log_success "PostgreSQL erfolgreich konfiguriert."
    log_info "Datenbankname: helpdesk"
    log_info "Benutzer: helpdesk_user"
    log_info "Passwort: helpdesk123"
    log_info "Port: 5432"
}

install_apache_debian() {
    log_info "Installiere Apache auf Debian/Ubuntu..."
    
    apt-get install -y apache2
    
    # Enable required modules
    a2enmod rewrite
    a2enmod ssl
    
    # Start and enable Apache
    systemctl start apache2
    systemctl enable apache2
    
    # Configure firewall
    if command -v ufw >/dev/null 2>&1; then
        ufw allow 'Apache Full'
    fi
    
    log_success "Apache erfolgreich installiert und gestartet."
}

install_apache_redhat() {
    log_info "Installiere Apache auf RedHat/CentOS..."
    
    if [[ "$OS_VERSION" == "8" ]] || [[ "$OS_VERSION" == "9" ]]; then
        dnf install -y httpd
    else
        yum install -y httpd
    fi
    
    # Start and enable Apache
    systemctl start httpd
    systemctl enable httpd
    
    # Configure firewall
    if command -v firewall-cmd >/dev/null 2>&1; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
    fi
    
    log_success "Apache erfolgreich installiert und gestartet."
}

install_nginx_debian() {
    log_info "Installiere Nginx auf Debian/Ubuntu..."
    
    apt-get install -y nginx
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Configure firewall
    if command -v ufw >/dev/null 2>&1; then
        ufw allow 'Nginx Full'
    fi
    
    log_success "Nginx erfolgreich installiert und gestartet."
}

install_nginx_redhat() {
    log_info "Installiere Nginx auf RedHat/CentOS..."
    
    if [[ "$OS_VERSION" == "8" ]] || [[ "$OS_VERSION" == "9" ]]; then
        dnf install -y nginx
    else
        yum install -y epel-release
        yum install -y nginx
    fi
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Configure firewall
    if command -v firewall-cmd >/dev/null 2>&1; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
    fi
    
    log_success "Nginx erfolgreich installiert und gestartet."
}

configure_webserver() {
    if [[ "$WEBSERVER" == "none" ]]; then
        return
    fi
    
    echo
    echo "========================================="
    echo "    Webserver Installation"
    echo "========================================="
    
    if [[ "$WEBSERVER" == "apache" ]]; then
        if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
            install_apache_debian
        elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
            install_apache_redhat
        fi
        
        # Create a simple index page
        cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>HelpDesk Server</title>
</head>
<body>
    <h1>HelpDesk Server erfolgreich installiert!</h1>
    <p>Apache läuft erfolgreich.</p>
    <p>PostgreSQL ist verfügbar auf Port 5432.</p>
</body>
</html>
EOF
        
    elif [[ "$WEBSERVER" == "nginx" ]]; then
        if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
            install_nginx_debian
        elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
            install_nginx_redhat
        fi
        
        # Create a simple index page
        if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
            NGINX_ROOT="/var/www/html"
        else
            NGINX_ROOT="/usr/share/nginx/html"
        fi
        
        cat > ${NGINX_ROOT}/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>HelpDesk Server</title>
</head>
<body>
    <h1>HelpDesk Server erfolgreich installiert!</h1>
    <p>Nginx läuft erfolgreich.</p>
    <p>PostgreSQL ist verfügbar auf Port 5432.</p>
</body>
</html>
EOF
    fi
}

main() {
    echo "========================================="
    echo "    HelpDesk Linux Installation"
    echo "========================================="
    echo
    
    check_root
    detect_os
    choose_webserver
    
    echo
    echo "========================================="
    echo "    PostgreSQL Installation"
    echo "========================================="
    
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        install_postgresql_debian
    elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
        install_postgresql_redhat
    else
        log_error "Nicht unterstuetztes Betriebssystem: $OS"
        exit 1
    fi
    
    configure_postgresql
    configure_webserver
    
    echo
    echo "========================================="
    echo "    Installation abgeschlossen"
    echo "========================================="
    echo
    log_success "PostgreSQL:"
    echo "- Server: localhost:5432"
    echo "- Datenbank: helpdesk"
    echo "- Benutzer: helpdesk_user"
    echo "- Passwort: helpdesk123"
    echo
    
    if [[ "$WEBSERVER" != "none" ]]; then
        log_success "Webserver: $WEBSERVER"
        echo "- URL: http://$(hostname -I | awk '{print $1}')"
        echo "- URL: http://localhost (lokal)"
        echo
    fi
    
    log_success "Installation erfolgreich abgeschlossen!"
    
    if [[ "$WEBSERVER" != "none" ]]; then
        log_info "Webserver Status pruefen: systemctl status $([[ "$WEBSERVER" == "apache" ]] && ([[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]) && echo "apache2" || echo "httpd") $([[ "$WEBSERVER" == "nginx" ]] && echo "nginx")"
    fi
    log_info "PostgreSQL Status pruefen: systemctl status $([[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]] && echo "postgresql" || echo "postgresql-16")"
}

main "$@"