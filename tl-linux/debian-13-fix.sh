#!/bin/bash
# Package installer for Debian 13 (Trixie) host systems
# This installs the tools needed to BUILD TL Linux ISOs

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  TL Linux - Debian 13 (Trixie) Package Installer"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo bash debian-13-fix.sh"
    exit 1
fi

# Verify this is actually Debian
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" != "debian" ]]; then
        echo "Warning: This script is designed for Debian 13"
        echo "Detected: $PRETTY_NAME"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "[1/4] Updating package lists..."
apt-get update || {
    echo ""
    echo "ERROR: Failed to update package lists"
    echo ""
    echo "Your /etc/apt/sources.list might be empty or misconfigured."
    echo "For Debian 13 (Trixie), you should have:"
    echo ""
    echo "deb http://deb.debian.org/debian/ trixie main contrib non-free non-free-firmware"
    echo "deb http://deb.debian.org/debian/ trixie-updates main contrib non-free non-free-firmware"
    echo "deb http://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware"
    echo ""
    exit 1
}

echo ""
echo "[2/4] Installing core build tools..."
apt-get install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    genisoimage \
    mtools \
    dosfstools \
    syslinux \
    syslinux-utils \
    isolinux \
    syslinux-common

echo ""
echo "[3/4] Installing bootloader packages..."
apt-get install -y \
    grub-pc-bin \
    grub-efi-amd64-bin \
    grub-efi-ia32-bin \
    grub-common

echo ""
echo "[4/4] Installing optional testing tools..."
apt-get install -y \
    qemu-system-x86 \
    qemu-utils \
    ovmf

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Verifying Installation"
echo "═══════════════════════════════════════════════════════════"

MISSING=0
CRITICAL_PACKAGES=(
    "debootstrap"
    "squashfs-tools"
    "xorriso"
    "grub-pc-bin"
    "mtools"
    "syslinux"
    "isolinux"
)

for pkg in "${CRITICAL_PACKAGES[@]}"; do
    if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
        echo "✓ $pkg"
    else
        echo "✗ $pkg MISSING"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
if [ $MISSING -eq 0 ]; then
    echo "═══════════════════════════════════════════════════════════"
    echo "  SUCCESS! All dependencies installed."
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Your Debian 13 system is ready to build TL Linux ISOs!"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure you're in a path WITHOUT spaces"
    echo "     Current: $(pwd)"
    echo ""
    echo "  2. Build your ISO with:"
    echo "     sudo make iso"
    echo ""
    echo "  3. The ISO will be created in:"
    echo "     iso-build/tl-linux.iso"
    echo ""
    echo "  4. Flash to USB with:"
    echo "     sudo dd if=iso-build/tl-linux.iso of=/dev/sdX bs=4M status=progress"
    echo "     (Replace /dev/sdX with your USB drive)"
    echo ""
else
    echo "═══════════════════════════════════════════════════════════"
    echo "  ERROR: $MISSING critical packages failed to install"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Please check your internet connection and APT configuration."
    exit 1
fi
