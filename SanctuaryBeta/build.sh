#!/bin/bash

# Sanctuary VR Beta - Build Script
# Quick build and run script for development

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Sanctuary VR Beta - Build Script                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven is not installed. Please install Maven first."
    exit 1
fi

# Clean and package
echo "📦 Building application with Maven..."
mvn clean package -DskipTests

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "You can now run the application with:"
    echo "  java -jar target/sanctuary-beta-0.1.0-BETA.jar"
    echo ""
    echo "Or run directly with:"
    echo "  ./run.sh"
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
