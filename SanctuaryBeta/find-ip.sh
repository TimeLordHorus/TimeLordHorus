#!/bin/bash

# Find Local IP Script
# Use this to get your IP address for Quest 3 access

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Sanctuary VR - Find Your Local IP Address              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo "🐧 Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0)
    echo "🍎 macOS detected"
else
    # Windows (Git Bash)
    LOCAL_IP=$(ipconfig | grep -i "IPv4" | grep -v "127.0.0.1" | awk '{print $NF}' | head -1)
    echo "🪟 Windows detected"
fi

echo ""
echo "📍 Your Local IP Address: $LOCAL_IP"
echo ""
echo "Access Sanctuary from:"
echo "  • This computer:    http://localhost:8080"
echo "  • Meta Quest 3:     http://$LOCAL_IP:8080"
echo "  • Other devices:    http://$LOCAL_IP:8080"
echo ""
echo "Make sure:"
echo "  1. Sanctuary server is running (./run.sh)"
echo "  2. Quest 3 is on the same WiFi network"
echo "  3. Firewall allows port 8080"
echo ""
