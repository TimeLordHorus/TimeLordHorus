#!/bin/bash

# Sanctuary VR Beta - Run Script
# Quick start script for development

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Sanctuary VR Beta - Starting Server                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if JAR exists
JAR_FILE="target/sanctuary-beta-0.1.0-BETA.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "❌ JAR file not found. Building first..."
    ./build.sh
fi

echo "🚀 Starting Sanctuary VR Beta..."
echo "📍 Server will be available at: http://localhost:8080"
echo "🌐 Access from Quest 3: http://YOUR_IP:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

java -jar $JAR_FILE
