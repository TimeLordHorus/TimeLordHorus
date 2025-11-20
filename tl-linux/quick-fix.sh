#!/bin/bash
# Quick fix for package installation on Ubuntu 24.04

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  TL Linux - Quick Package Fix for Ubuntu 24.04"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo bash quick-fix.sh"
    exit 1
fi

echo "[1/3] Updating package lists..."
apt-get update

echo ""
echo "[2/3] Installing build dependencies..."
apt-get install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    genisoimage \
    grub-pc-bin \
    grub-efi-amd64-bin \
    grub-efi-ia32-bin \
    mtools \
    dosfstools \
    syslinux \
    syslinux-utils \
    isolinux \
    syslinux-common \
    qemu-system-x86

echo ""
echo "[3/3] Verifying installation..."
MISSING=0

for pkg in debootstrap squashfs-tools xorriso grub-pc-bin mtools; do
    if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        echo "✓ $pkg installed"
    else
        echo "✗ $pkg FAILED"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  SUCCESS! All dependencies installed."
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "You can now build your ISO with:"
    echo "  sudo make iso"
    echo ""
else
    echo "═══════════════════════════════════════════════════════════"
    echo "  WARNING: $MISSING packages failed to install"
    echo "═══════════════════════════════════════════════════════════"
    exit 1
fi
