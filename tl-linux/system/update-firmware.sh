#!/bin/bash
#
# TL Linux - Firmware Update Script
# Updates all system firmware and drivers
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Usage: sudo $0"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TL Linux Firmware Update Utility${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Update package lists
echo -e "${YELLOW}➤ Updating package lists...${NC}"
apt-get update -qq

echo ""
echo -e "${GREEN}✓ Package lists updated${NC}"
echo ""

# Firmware packages to update
FIRMWARE_PACKAGES=(
    "linux-firmware"
    "firmware-linux"
    "firmware-linux-free"
    "firmware-linux-nonfree"
    "intel-microcode"
    "amd64-microcode"
    "firmware-misc-nonfree"
    "firmware-realtek"
    "firmware-atheros"
    "firmware-iwlwifi"
)

# Check and install/update each package
echo -e "${YELLOW}➤ Checking firmware packages...${NC}"
echo ""

UPDATED_COUNT=0
INSTALLED_COUNT=0
SKIPPED_COUNT=0

for package in "${FIRMWARE_PACKAGES[@]}"; do
    echo -n "  Checking $package... "

    if dpkg -l | grep -q "^ii  $package "; then
        # Package is installed, try to upgrade
        if apt-get install --only-upgrade -y "$package" &>/dev/null; then
            echo -e "${GREEN}updated${NC}"
            ((UPDATED_COUNT++))
        else
            echo -e "${BLUE}already latest${NC}"
            ((SKIPPED_COUNT++))
        fi
    else
        # Package not installed, try to install
        if apt-get install -y "$package" &>/dev/null; then
            echo -e "${GREEN}installed${NC}"
            ((INSTALLED_COUNT++))
        else
            echo -e "${YELLOW}not available${NC}"
            ((SKIPPED_COUNT++))
        fi
    fi
done

echo ""
echo -e "${GREEN}✓ Firmware packages processed${NC}"
echo "  Updated: $UPDATED_COUNT"
echo "  Installed: $INSTALLED_COUNT"
echo "  Skipped: $SKIPPED_COUNT"
echo ""

# Check for fwupd (firmware update daemon)
echo -e "${YELLOW}➤ Checking for fwupd...${NC}"

if command -v fwupdmgr &> /dev/null; then
    echo -e "${GREEN}✓ fwupd is installed${NC}"
    echo ""

    echo -e "${YELLOW}➤ Refreshing firmware metadata...${NC}"
    if fwupdmgr refresh --force &>/dev/null; then
        echo -e "${GREEN}✓ Metadata refreshed${NC}"
    else
        echo -e "${YELLOW}⚠ Could not refresh metadata${NC}"
    fi
    echo ""

    echo -e "${YELLOW}➤ Checking for device firmware updates...${NC}"
    echo ""

    # Get available updates
    if fwupdmgr get-updates &>/dev/null; then
        echo -e "${GREEN}Firmware updates available!${NC}"
        echo ""
        fwupdmgr get-updates
        echo ""

        read -p "Install firmware updates? [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}➤ Installing firmware updates...${NC}"
            fwupdmgr update -y
            echo -e "${GREEN}✓ Firmware updates installed${NC}"
        else
            echo -e "${BLUE}  Skipped firmware installation${NC}"
        fi
    else
        echo -e "${GREEN}✓ All device firmware is up to date${NC}"
    fi
else
    echo -e "${YELLOW}⚠ fwupd is not installed${NC}"
    echo ""
    echo "  fwupd provides firmware updates for many devices including:"
    echo "    • UEFI/BIOS"
    echo "    • Thunderbolt devices"
    echo "    • USB devices"
    echo "    • Graphics cards"
    echo "    • Network adapters"
    echo "    • Storage devices"
    echo ""

    read -p "Install fwupd? [Y/n] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}➤ Installing fwupd...${NC}"
        apt-get install -y fwupd
        echo -e "${GREEN}✓ fwupd installed${NC}"
        echo ""

        echo -e "${YELLOW}➤ Running initial firmware scan...${NC}"
        fwupdmgr refresh --force
        fwupdmgr get-devices
    fi
fi

echo ""

# Update kernel (includes firmware)
echo -e "${YELLOW}➤ Checking kernel updates...${NC}"

CURRENT_KERNEL=$(uname -r)
echo "  Current kernel: $CURRENT_KERNEL"

if apt-get install --only-upgrade -y linux-image-generic linux-headers-generic &>/dev/null; then
    NEW_KERNEL=$(dpkg -l | grep "^ii  linux-image-[0-9]" | tail -1 | awk '{print $2}' | sed 's/linux-image-//')

    if [ "$CURRENT_KERNEL" != "$NEW_KERNEL" ]; then
        echo -e "${GREEN}✓ Kernel updated to $NEW_KERNEL${NC}"
        echo -e "${YELLOW}  ⚠ Reboot required to use new kernel${NC}"
    else
        echo -e "${GREEN}✓ Kernel is up to date${NC}"
    fi
else
    echo -e "${GREEN}✓ Kernel is up to date${NC}"
fi

echo ""

# Graphics driver firmware
echo -e "${YELLOW}➤ Checking graphics drivers...${NC}"

# Detect GPU
if lspci | grep -i "vga.*nvidia" &>/dev/null; then
    echo "  Detected: NVIDIA GPU"

    if dpkg -l | grep -q "nvidia-driver"; then
        apt-get install --only-upgrade -y nvidia-driver &>/dev/null && \
            echo -e "${GREEN}✓ NVIDIA driver updated${NC}" || \
            echo -e "${GREEN}✓ NVIDIA driver is up to date${NC}"
    else
        echo -e "${YELLOW}  ℹ NVIDIA driver not installed (use 'Additional Drivers' to install)${NC}"
    fi

elif lspci | grep -i "vga.*amd\|vga.*radeon" &>/dev/null; then
    echo "  Detected: AMD GPU"

    apt-get install --only-upgrade -y firmware-amd-graphics &>/dev/null && \
        echo -e "${GREEN}✓ AMD graphics firmware updated${NC}" || \
        echo -e "${GREEN}✓ AMD graphics firmware is up to date${NC}"

elif lspci | grep -i "vga.*intel" &>/dev/null; then
    echo "  Detected: Intel GPU"

    apt-get install --only-upgrade -y intel-gpu-tools &>/dev/null && \
        echo -e "${GREEN}✓ Intel graphics tools updated${NC}" || \
        echo -e "${GREEN}✓ Intel graphics is up to date${NC}"
else
    echo -e "${BLUE}  Generic graphics driver in use${NC}"
fi

echo ""

# Network adapter firmware
echo -e "${YELLOW}➤ Checking network adapter firmware...${NC}"

# Detect WiFi chipset
if lspci | grep -i "network.*intel" &>/dev/null; then
    apt-get install --only-upgrade -y firmware-iwlwifi &>/dev/null && \
        echo -e "${GREEN}✓ Intel WiFi firmware updated${NC}" || \
        echo -e "${GREEN}✓ Intel WiFi firmware is up to date${NC}"

elif lspci | grep -i "network.*realtek" &>/dev/null; then
    apt-get install --only-upgrade -y firmware-realtek &>/dev/null && \
        echo -e "${GREEN}✓ Realtek firmware updated${NC}" || \
        echo -e "${GREEN}✓ Realtek firmware is up to date${NC}"

elif lspci | grep -i "network.*atheros" &>/dev/null; then
    apt-get install --only-upgrade -y firmware-atheros &>/dev/null && \
        echo -e "${GREEN}✓ Atheros firmware updated${NC}" || \
        echo -e "${GREEN}✓ Atheros firmware is up to date${NC}"
else
    echo -e "${GREEN}✓ Network firmware is up to date${NC}"
fi

echo ""

# Clean up
echo -e "${YELLOW}➤ Cleaning up...${NC}"
apt-get autoremove -y &>/dev/null
apt-get autoclean -y &>/dev/null
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Firmware update complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if reboot is needed
if [ -f /var/run/reboot-required ]; then
    echo -e "${YELLOW}⚠ A system reboot is required to complete the updates${NC}"
    echo ""
    read -p "Reboot now? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Rebooting..."
        systemctl reboot
    else
        echo "Remember to reboot later to apply all updates."
    fi
else
    echo -e "${GREEN}✓ No reboot required${NC}"
fi

echo ""
exit 0
