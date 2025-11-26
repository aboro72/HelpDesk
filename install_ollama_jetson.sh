#!/bin/bash
#
# Ollama Installation Script für NVIDIA Jetson Orin NX
# Führe aus mit: sudo bash install_ollama_jetson.sh
#

set -e  # Exit on error

echo "========================================"
echo "Ollama Installation für Jetson Orin NX"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Bitte führe das Script mit sudo aus:"
    echo "   sudo bash install_ollama_jetson.sh"
    exit 1
fi

echo "✓ Running as root"

# Detect architecture
ARCH=$(uname -m)
echo "✓ Architecture: $ARCH"

if [ "$ARCH" != "aarch64" ]; then
    echo "⚠️  Warnung: Nicht auf ARM64-Architektur. Fortfahren? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Download Ollama for ARM64
echo ""
echo "📥 Downloading Ollama for ARM64..."
cd /tmp
wget -O ollama-linux-arm64 https://github.com/ollama/ollama/releases/latest/download/ollama-linux-arm64

# Install to /usr/local/bin
echo "📦 Installing Ollama..."
chmod +x ollama-linux-arm64
mv ollama-linux-arm64 /usr/local/bin/ollama

# Verify installation
if [ -f "/usr/local/bin/ollama" ]; then
    echo "✅ Ollama binary installed successfully"
    /usr/local/bin/ollama --version
else
    echo "❌ Installation failed"
    exit 1
fi

# Create ollama user
echo ""
echo "👤 Creating ollama user..."
if ! id -u ollama > /dev/null 2>&1; then
    useradd -r -s /bin/false -m -d /usr/share/ollama ollama
    echo "✅ User 'ollama' created"
else
    echo "✓ User 'ollama' already exists"
fi

# Create systemd service
echo ""
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="OLLAMA_HOST=127.0.0.1:11434"

[Install]
WantedBy=default.target
EOF

echo "✅ Systemd service created"

# Reload systemd
echo ""
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable and start service
echo "🚀 Enabling and starting Ollama service..."
systemctl enable ollama
systemctl start ollama

# Wait a moment for service to start
echo ""
echo "⏳ Waiting for service to start..."
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
systemctl status ollama --no-pager || true

# Test connection
echo ""
echo "🧪 Testing Ollama connection..."
sleep 2
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama is running and accessible!"
    echo ""
    echo "Version info:"
    curl -s http://localhost:11434/api/version | python3 -m json.tool || echo "API OK"
else
    echo "⚠️  Ollama service started but API not yet responding"
    echo "   This is normal - it may take a few more seconds"
fi

echo ""
echo "========================================"
echo "✅ Ollama Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Download LLAMA3 model:"
echo "   ollama pull llama3:8b"
echo ""
echo "2. Test it:"
echo "   ollama run llama3:8b 'Hallo'"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status ollama"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u ollama -f"
echo ""
