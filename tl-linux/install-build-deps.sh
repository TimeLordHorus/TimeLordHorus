#!/bin/bash
#
# TL Linux - System Detector and Dependency Installer
# Detects your Linux distribution and installs correct packages
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TL Linux Dependency Installer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Must be run as root (use sudo)${NC}"
    exit 1
fi

# Detect distribution
echo -e "${YELLOW}Detecting your Linux distribution...${NC}"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
    echo -e "${GREEN}Found: $NAME $VERSION${NC}"
else
    echo -e "${RED}Cannot detect distribution${NC}"
    exit 1
fi

echo ""

# Install based on distribution
case "$DISTRO" in
    ubuntu|debian|pop|linuxmint|elementary)
        echo -e "${BLUE}Installing Debian/Ubuntu packages...${NC}"
        echo ""

        # Update package lists
        echo "Updating package lists..."
        apt-get update

        # Install dependencies
        echo "Installing build dependencies..."
        apt-get install -y \
            debootstrap \
            squashfs-tools \
            xorriso \
            genisoimage \
            grub-pc-bin \
            grub-efi-amd64-bin \
            mtools \
            dosfstools \
            syslinux \
            syslinux-utils \
            isolinux \
            syslinux-common \
            qemu-system-x86 \
            rsync \
            wget \
            2>&1 | tee /tmp/apt-install.log

        if [ ${PIPESTATUS[0]} -ne 0 ]; then
            echo ""
            echo -e "${RED}Package installation failed!${NC}"
            echo ""
            echo "Common issues:"
            echo "  1. Internet connection problem"
            echo "  2. Invalid package repositories"
            echo "  3. Out of date package lists"
            echo ""
            echo "Try these fixes:"
            echo ""
            echo "1. Check internet connection:"
            echo "   ping -c 3 deb.debian.org"
            echo ""
            echo "2. Update package lists:"
            echo "   sudo apt-get update"
            echo ""
            echo "3. Check /etc/apt/sources.list for valid repos"
            echo ""
            echo "Error log saved to: /tmp/apt-install.log"
            exit 1
        fi
        ;;

    fedora|rhel|centos|rocky|almalinux)
        echo -e "${BLUE}Installing Fedora/RHEL packages...${NC}"
        echo ""

        dnf install -y \
            debootstrap \
            squashfs-tools \
            xorriso \
            grub2-pc \
            grub2-efi-x64 \
            grub2-tools \
            mtools \
            dosfstools \
            syslinux \
            qemu-system-x86 \
            rsync \
            wget
        ;;

    arch|manjaro|endeavouros)
        echo -e "${BLUE}Installing Arch Linux packages...${NC}"
        echo ""

        pacman -Sy --needed --noconfirm \
            debootstrap \
            squashfs-tools \
            libisoburn \
            grub \
            efibootmgr \
            mtools \
            dosfstools \
            syslinux \
            qemu-full \
            rsync \
            wget
        ;;

    opensuse*|suse)
        echo -e "${BLUE}Installing openSUSE packages...${NC}"
        echo ""

        zypper install -y \
            debootstrap \
            squashfs \
            xorriso \
            grub2 \
            grub2-x86_64-efi \
            mtools \
            dosfstools \
            syslinux \
            qemu-x86 \
            rsync \
            wget
        ;;

    *)
        echo -e "${RED}Unsupported distribution: $DISTRO${NC}"
        echo ""
        echo "TL Linux ISO builder requires:"
        echo "  - debootstrap"
        echo "  - squashfs-tools"
        echo "  - xorriso or genisoimage"
        echo "  - grub-pc-bin and grub-efi-amd64-bin"
        echo "  - mtools, dosfstools"
        echo "  - syslinux, isolinux"
        echo ""
        echo "Please install these packages manually for your distribution."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ All dependencies installed successfully!${NC}"
echo ""
echo "You can now build the ISO with:"
echo "  sudo make iso"
echo ""

exit 0
