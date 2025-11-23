#!/bin/bash
#
# TL Linux - Repository Fixer
# Fixes missing or broken APT repositories
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TL Linux Repository Fixer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Must be run as root${NC}"
    echo "Usage: sudo $0"
    exit 1
fi

# Detect system
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}Cannot detect operating system${NC}"
    exit 1
fi

. /etc/os-release

echo "Detected system:"
echo "  Distribution: $NAME"
echo "  Version: $VERSION_ID"
echo "  Codename: ${VERSION_CODENAME:-unknown}"
echo ""

# Check if this is actually Debian/Ubuntu based
case "$ID" in
    debian|ubuntu|pop|linuxmint|elementary|neon)
        echo -e "${GREEN}✓ Debian/Ubuntu-based system detected${NC}"
        ;;
    *)
        echo -e "${RED}✗ This is not a Debian/Ubuntu system!${NC}"
        echo ""
        echo "Your system: $NAME ($ID)"
        echo ""
        echo "TL Linux ISO builder requires a Debian or Ubuntu host system."
        echo "You cannot build a Debian-based ISO from $ID."
        echo ""
        echo "Options:"
        echo "  1. Use a Debian 12 (Bookworm) or Ubuntu 22.04+ system"
        echo "  2. Run in a Debian/Ubuntu VM or container"
        echo "  3. Use a Debian/Ubuntu live USB to build"
        echo ""
        exit 1
        ;;
esac

echo ""

# Backup existing sources.list
if [ -f /etc/apt/sources.list ]; then
    echo "Backing up existing /etc/apt/sources.list..."
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d-%H%M%S)
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}No existing sources.list found${NC}"
fi

echo ""

# Configure repositories based on distribution
case "$ID" in
    debian)
        echo "Configuring Debian repositories..."

        # Determine Debian version
        if [ -z "$VERSION_CODENAME" ]; then
            if [ "$VERSION_ID" = "12" ]; then
                VERSION_CODENAME="bookworm"
            elif [ "$VERSION_ID" = "11" ]; then
                VERSION_CODENAME="bullseye"
            else
                VERSION_CODENAME="bookworm"
            fi
        fi

        cat > /etc/apt/sources.list << EOF
# Debian $VERSION_CODENAME - Main repositories
deb http://deb.debian.org/debian $VERSION_CODENAME main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian $VERSION_CODENAME main contrib non-free non-free-firmware

# Debian $VERSION_CODENAME - Security updates
deb http://security.debian.org/debian-security $VERSION_CODENAME-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security $VERSION_CODENAME-security main contrib non-free non-free-firmware

# Debian $VERSION_CODENAME - Updates
deb http://deb.debian.org/debian $VERSION_CODENAME-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian $VERSION_CODENAME-updates main contrib non-free non-free-firmware
EOF
        echo -e "${GREEN}✓ Debian repositories configured${NC}"
        ;;

    ubuntu|pop|neon)
        echo "Configuring Ubuntu repositories..."

        # Determine Ubuntu version codename
        if [ -z "$VERSION_CODENAME" ]; then
            case "$VERSION_ID" in
                "24.04") VERSION_CODENAME="noble" ;;
                "23.10") VERSION_CODENAME="mantic" ;;
                "23.04") VERSION_CODENAME="lunar" ;;
                "22.04") VERSION_CODENAME="jammy" ;;
                "20.04") VERSION_CODENAME="focal" ;;
                *) VERSION_CODENAME="jammy" ;;
            esac
        fi

        cat > /etc/apt/sources.list << EOF
# Ubuntu $VERSION_CODENAME - Main repositories
deb http://archive.ubuntu.com/ubuntu $VERSION_CODENAME main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu $VERSION_CODENAME main restricted universe multiverse

# Ubuntu $VERSION_CODENAME - Security updates
deb http://security.ubuntu.com/ubuntu $VERSION_CODENAME-security main restricted universe multiverse
deb-src http://security.ubuntu.com/ubuntu $VERSION_CODENAME-security main restricted universe multiverse

# Ubuntu $VERSION_CODENAME - Updates
deb http://archive.ubuntu.com/ubuntu $VERSION_CODENAME-updates main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu $VERSION_CODENAME-updates main restricted universe multiverse

# Ubuntu $VERSION_CODENAME - Backports
deb http://archive.ubuntu.com/ubuntu $VERSION_CODENAME-backports main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu $VERSION_CODENAME-backports main restricted universe multiverse
EOF
        echo -e "${GREEN}✓ Ubuntu repositories configured${NC}"
        ;;

    linuxmint)
        echo "Configuring Linux Mint repositories..."

        # Linux Mint is based on Ubuntu, find the base
        UBUNTU_CODENAME="jammy"  # Default to Ubuntu 22.04 base

        cat > /etc/apt/sources.list << EOF
# Ubuntu base repositories (Linux Mint)
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu $UBUNTU_CODENAME-security main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu $UBUNTU_CODENAME-security main restricted universe multiverse
EOF
        echo -e "${GREEN}✓ Linux Mint repositories configured${NC}"
        ;;

    elementary)
        echo "Configuring elementary OS repositories..."

        cat > /etc/apt/sources.list << EOF
# Ubuntu base repositories (elementary OS)
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF
        echo -e "${GREEN}✓ elementary OS repositories configured${NC}"
        ;;
esac

echo ""
echo "Repository configuration:"
cat /etc/apt/sources.list
echo ""

# Update package lists
echo -e "${YELLOW}Updating package lists...${NC}"
echo "This may take a minute..."
echo ""

if apt-get update; then
    echo ""
    echo -e "${GREEN}✓ Package lists updated successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Package update failed${NC}"
    echo ""
    echo "Possible issues:"
    echo "  1. No internet connection"
    echo "  2. Repository servers down"
    echo "  3. Firewall blocking access"
    echo ""
    echo "Test connectivity:"
    echo "  ping -c 3 deb.debian.org"
    echo "  ping -c 3 archive.ubuntu.com"
    echo ""
    exit 1
fi

echo ""
echo -e "${BLUE}Testing package availability...${NC}"
echo ""

# Test if build packages are now available
TEST_PACKAGES=("debootstrap" "squashfs-tools" "xorriso" "grub-pc-bin")
ALL_FOUND=true

for pkg in "${TEST_PACKAGES[@]}"; do
    if apt-cache show "$pkg" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg (available)"
    else
        echo -e "  ${RED}✗${NC} $pkg (still missing)"
        ALL_FOUND=false
    fi
done

echo ""

if $ALL_FOUND; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Repositories fixed successfully!                         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "You can now install build dependencies:"
    echo "  sudo make install-deps"
    echo ""
    echo "Or install manually:"
    echo "  sudo apt-get install debootstrap squashfs-tools xorriso \\"
    echo "    grub-pc-bin grub-efi-amd64-bin mtools dosfstools \\"
    echo "    syslinux syslinux-utils isolinux"
    echo ""
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  Some packages still unavailable                          ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "This might mean:"
    echo "  1. Your distribution version is too old"
    echo "  2. You need to enable additional repositories"
    echo "  3. Some packages have different names"
    echo ""
    echo "Recommended: Use Debian 12 (Bookworm) or Ubuntu 22.04+"
    echo ""
fi

# Show backup location
if [ -f /etc/apt/sources.list.backup.* ]; then
    BACKUP=$(ls -t /etc/apt/sources.list.backup.* | head -1)
    echo "Original sources.list backed up to:"
    echo "  $BACKUP"
    echo ""
fi

exit 0
