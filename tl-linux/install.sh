#!/bin/bash
# TL Linux Installation Script
# Installs and configures TL Linux and its dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Header
echo -e "${PURPLE}"
cat << "EOF"
    ████████╗██╗         ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
    ╚══██╔══╝██║         ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
       ██║   ██║         ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝
       ██║   ██║         ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗
       ██║   ███████╗    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
       ╚═╝   ╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝

                    TL Linux Installer v1.0.0
EOF
echo -e "${NC}"

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}\n"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please do not run this script as root${NC}"
    exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo -e "${GREEN}✓ Detected distribution: $PRETTY_NAME${NC}"
else
    echo -e "${YELLOW}⚠ Could not detect distribution${NC}"
    DISTRO="unknown"
fi

# Check Python version
echo -e "\n${CYAN}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION installed${NC}"

    # Check if version is 3.8 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo -e "${GREEN}✓ Python version is compatible${NC}"
    else
        echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Install system dependencies
echo -e "\n${CYAN}Installing system dependencies...${NC}"

case "$DISTRO" in
    ubuntu|debian|linuxmint|pop)
        echo -e "${YELLOW}Installing dependencies for Debian/Ubuntu...${NC}"
        sudo apt update
        sudo apt install -y python3-tk python3-pip git
        echo -e "${GREEN}✓ System dependencies installed${NC}"
        ;;
    arch|manjaro)
        echo -e "${YELLOW}Installing dependencies for Arch Linux...${NC}"
        sudo pacman -S --needed --noconfirm tk python-pip git
        echo -e "${GREEN}✓ System dependencies installed${NC}"
        ;;
    fedora|rhel|centos)
        echo -e "${YELLOW}Installing dependencies for Fedora/RHEL...${NC}"
        sudo dnf install -y python3-tkinter python3-pip git
        echo -e "${GREEN}✓ System dependencies installed${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠ Unknown distribution - please install python3-tk manually${NC}"
        ;;
esac

# Create necessary directories
echo -e "\n${CYAN}Creating directories...${NC}"
mkdir -p "$HOME/.config/tl-linux"
mkdir -p "$HOME/ROMs"
mkdir -p "$HOME/.local/share/tl-linux"
echo -e "${GREEN}✓ Directories created${NC}"

# Make scripts executable
echo -e "\n${CYAN}Setting permissions...${NC}"
chmod +x tl_linux.py
chmod +x boot/cephalopod_animation.py
chmod +x onboarding/onboarding_system.py
chmod +x desktop/desktop_environment.py
chmod +x apps/*.py
chmod +x settings/settings_manager.py
chmod +x compat/compatibility_layer.py
echo -e "${GREEN}✓ Permissions set${NC}"

# Optional: Install compatibility layers
echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Optional Compatibility Layers${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}\n"

read -p "Install Wine for Windows app support? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            sudo dpkg --add-architecture i386
            sudo apt update
            sudo apt install -y wine wine32 wine64 winetricks
            ;;
        arch|manjaro)
            sudo pacman -S --needed --noconfirm wine winetricks
            ;;
        fedora)
            sudo dnf install -y wine winetricks
            ;;
    esac
    echo -e "${GREEN}✓ Wine installed${NC}"
fi

read -p "Install Flatpak for universal apps? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            sudo apt install -y flatpak
            ;;
        arch|manjaro)
            sudo pacman -S --needed --noconfirm flatpak
            ;;
        fedora)
            sudo dnf install -y flatpak
            ;;
    esac
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    echo -e "${GREEN}✓ Flatpak installed${NC}"
fi

# Create desktop launcher
echo -e "\n${CYAN}Creating desktop launcher...${NC}"
INSTALL_DIR=$(pwd)
cat > "$HOME/.local/share/applications/tl-linux.desktop" << EOF
[Desktop Entry]
Name=TL Linux
Comment=Time Lord Operating System
Exec=python3 $INSTALL_DIR/tl_linux.py
Icon=computer
Terminal=false
Type=Application
Categories=System;
EOF

echo -e "${GREEN}✓ Desktop launcher created${NC}"

# Create launcher script in /usr/local/bin (optional)
read -p "Create system-wide launcher? (requires sudo) (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /usr/local/bin/tl-linux > /dev/null << EOF
#!/bin/bash
cd $INSTALL_DIR
python3 tl_linux.py "\$@"
EOF
    sudo chmod +x /usr/local/bin/tl-linux
    echo -e "${GREEN}✓ System launcher created${NC}"
    echo -e "${CYAN}  You can now run 'tl-linux' from anywhere${NC}"
fi

# Installation complete
echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}\n"

echo -e "${PURPLE}🐙 TL Linux has been installed successfully!${NC}\n"
echo -e "To launch TL Linux:"
echo -e "  ${CYAN}python3 $INSTALL_DIR/tl_linux.py${NC}"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "  ${CYAN}or simply: tl-linux${NC}"
fi

echo -e "\nTo launch with menu mode:"
echo -e "  ${CYAN}python3 $INSTALL_DIR/tl_linux.py --menu${NC}\n"

echo -e "${YELLOW}Note: On first launch, you'll go through onboarding.${NC}"
echo -e "${YELLOW}This will help customize TL Linux to your preferences.${NC}\n"

read -p "Launch TL Linux now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 tl_linux.py
fi

echo -e "\n${PURPLE}Thank you for choosing TL Linux! 🐙⏰💻${NC}\n"
