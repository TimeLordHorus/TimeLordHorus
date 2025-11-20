#!/bin/bash
#
# TL Linux System Diagnostic Tool
# Checks your system and identifies issues
#

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TL Linux System Diagnostic${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Detect OS
echo -e "${YELLOW}System Information:${NC}"
echo ""

if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "  Distribution: $NAME"
    echo "  Version: $VERSION"
    echo "  ID: $ID"
    echo "  Codename: ${VERSION_CODENAME:-N/A}"
else
    echo -e "  ${RED}Cannot detect OS (no /etc/os-release)${NC}"
fi

echo "  Architecture: $(uname -m)"
echo "  Kernel: $(uname -r)"
echo ""

# Check package manager
echo -e "${YELLOW}Package Manager:${NC}"
echo ""

if command -v apt &>/dev/null; then
    echo -e "  ${GREEN}✓ apt (Debian/Ubuntu)${NC}"
    PKG_MGR="apt"
elif command -v dnf &>/dev/null; then
    echo -e "  ${GREEN}✓ dnf (Fedora/RHEL)${NC}"
    PKG_MGR="dnf"
elif command -v yum &>/dev/null; then
    echo -e "  ${GREEN}✓ yum (RHEL/CentOS)${NC}"
    PKG_MGR="yum"
elif command -v pacman &>/dev/null; then
    echo -e "  ${GREEN}✓ pacman (Arch Linux)${NC}"
    PKG_MGR="pacman"
elif command -v zypper &>/dev/null; then
    echo -e "  ${GREEN}✓ zypper (openSUSE)${NC}"
    PKG_MGR="zypper"
else
    echo -e "  ${RED}✗ No supported package manager found${NC}"
    PKG_MGR="none"
fi
echo ""

# Check required commands
echo -e "${YELLOW}Required Build Tools:${NC}"
echo ""

check_command() {
    if command -v "$1" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

MISSING=0

check_command debootstrap || ((MISSING++))
check_command mksquashfs || ((MISSING++))
check_command xorriso || check_command genisoimage || ((MISSING++))
check_command grub-mkstandalone || ((MISSING++))
check_command qemu-system-x86_64 || ((MISSING++))

echo ""

# Check for specific packages
if [ "$PKG_MGR" = "apt" ]; then
    echo -e "${YELLOW}Checking Debian/Ubuntu Packages:${NC}"
    echo ""

    PACKAGES=(
        "debootstrap"
        "squashfs-tools"
        "xorriso"
        "grub-pc-bin"
        "grub-efi-amd64-bin"
        "mtools"
        "dosfstools"
        "syslinux"
        "syslinux-utils"
        "isolinux"
    )

    for pkg in "${PACKAGES[@]}"; do
        if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            echo -e "  ${GREEN}✓${NC} $pkg (installed)"
        else
            echo -e "  ${RED}✗${NC} $pkg (not installed)"
        fi
    done
    echo ""
fi

# Check repositories (for apt)
if [ "$PKG_MGR" = "apt" ]; then
    echo -e "${YELLOW}APT Repository Configuration:${NC}"
    echo ""

    if [ ! -f /etc/apt/sources.list ]; then
        echo -e "  ${RED}✗ No /etc/apt/sources.list file${NC}"
    else
        REPO_COUNT=$(grep -c "^deb " /etc/apt/sources.list 2>/dev/null || echo 0)
        echo "  Active repositories: $REPO_COUNT"

        if [ $REPO_COUNT -eq 0 ]; then
            echo -e "  ${RED}✗ No active repositories configured!${NC}"
        fi
    fi

    # Check if sources.list.d exists
    if [ -d /etc/apt/sources.list.d ]; then
        EXTRA_REPOS=$(ls -1 /etc/apt/sources.list.d/*.list 2>/dev/null | wc -l)
        echo "  Extra repository files: $EXTRA_REPOS"
    fi

    # Test repository connectivity
    echo ""
    echo "  Testing connectivity to Debian repositories..."
    if ping -c 1 deb.debian.org &>/dev/null; then
        echo -e "  ${GREEN}✓ Can reach deb.debian.org${NC}"
    else
        echo -e "  ${RED}✗ Cannot reach deb.debian.org${NC}"
        echo "    Check your internet connection"
    fi
    echo ""
fi

# Disk space check
echo -e "${YELLOW}Disk Space:${NC}"
echo ""

CURRENT_DIR=$(pwd)
AVAILABLE=$(df -BG "$CURRENT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')

echo "  Available in current directory: ${AVAILABLE}GB"

if [ "$AVAILABLE" -lt 20 ]; then
    echo -e "  ${RED}✗ Insufficient space (need at least 20GB)${NC}"
else
    echo -e "  ${GREEN}✓ Sufficient space${NC}"
fi
echo ""

# Path check
echo -e "${YELLOW}Build Path:${NC}"
echo ""

if [[ "$CURRENT_DIR" =~ [[:space:]] ]]; then
    echo -e "  ${RED}✗ Path contains spaces: $CURRENT_DIR${NC}"
    echo "    This will cause build failures!"
else
    echo -e "  ${GREEN}✓ Path OK: $CURRENT_DIR${NC}"
fi
echo ""

# Summary and recommendations
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Summary & Recommendations${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All required tools are installed${NC}"
    echo ""
    echo "You can build the ISO with:"
    echo "  sudo make iso"
else
    echo -e "${RED}✗ Missing $MISSING required tools${NC}"
    echo ""
    echo "To install dependencies, run:"
    echo "  sudo ./install-build-deps.sh"
    echo ""
    echo "Or manually install with your package manager:"

    case "$PKG_MGR" in
        apt)
            echo "  sudo apt-get update"
            echo "  sudo apt-get install debootstrap squashfs-tools xorriso \\"
            echo "    grub-pc-bin grub-efi-amd64-bin mtools dosfstools \\"
            echo "    syslinux syslinux-utils isolinux syslinux-common"
            ;;
        dnf)
            echo "  sudo dnf install debootstrap squashfs-tools xorriso \\"
            echo "    grub2-pc grub2-efi-x64 mtools dosfstools syslinux"
            ;;
        pacman)
            echo "  sudo pacman -S debootstrap squashfs-tools libisoburn \\"
            echo "    grub efibootmgr mtools dosfstools syslinux"
            ;;
        *)
            echo "  (install appropriate packages for your distribution)"
            ;;
    esac
fi

# Additional warnings
if [[ "$CURRENT_DIR" =~ [[:space:]] ]]; then
    echo ""
    echo -e "${YELLOW}⚠ WARNING: Your current path contains spaces!${NC}"
    echo "  Move the project to a path without spaces:"
    echo "    mv \"$CURRENT_DIR\" ~/tl-linux"
fi

if [ "$AVAILABLE" -lt 20 ]; then
    echo ""
    echo -e "${YELLOW}⚠ WARNING: Insufficient disk space!${NC}"
    echo "  Free up at least 20GB before building"
fi

if [ "$PKG_MGR" = "apt" ]; then
    REPO_COUNT=$(grep -c "^deb " /etc/apt/sources.list 2>/dev/null || echo 0)
    if [ $REPO_COUNT -eq 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠ WARNING: No APT repositories configured!${NC}"
        echo "  Add Debian/Ubuntu repositories to /etc/apt/sources.list"
    fi
fi

echo ""
