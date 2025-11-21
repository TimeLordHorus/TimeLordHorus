#!/bin/bash
###############################################################################
# TL Linux Quick Test ISO Builder
# Creates a minimal test ISO for quick validation (much faster than full build)
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TL Linux Quick Test ISO Builder         ║${NC}"
echo -e "${BLUE}║   (Minimal Build for Testing)             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

BUILD_DIR="$(pwd)/test-iso-build"
OUTPUT_DIR="$(pwd)/release"
ISO_NAME="tl-linux-test-amd64.iso"

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/iso/live" "$OUTPUT_DIR"

# Download a minimal live ISO as base (if not exists)
BASE_ISO="$OUTPUT_DIR/debian-base.iso"
if [ ! -f "$BASE_ISO" ]; then
    echo -e "${YELLOW}Downloading minimal Debian live ISO (~300MB)...${NC}"
    wget -O "$BASE_ISO" \
        "https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/debian-live-12.5.0-amd64-xfce.iso" \
        || {
            echo -e "${RED}Failed to download base ISO${NC}"
            echo "You can manually download from: https://www.debian.org/CD/live/"
            exit 1
        }
fi

# Extract base ISO
echo -e "${YELLOW}Extracting base ISO...${NC}"
mkdir -p "$BUILD_DIR/mount"
mount -o loop "$BASE_ISO" "$BUILD_DIR/mount"
rsync -a "$BUILD_DIR/mount/" "$BUILD_DIR/iso/"
umount "$BUILD_DIR/mount"
rmdir "$BUILD_DIR/mount"

# Customize ISO
echo -e "${YELLOW}Customizing for TL Linux...${NC}"

# Update boot menu
cat > "$BUILD_DIR/iso/boot/grub/grub.cfg" << 'EOF'
set default="0"
set timeout=10

menuentry "TL Linux Test Live" {
    linux /live/vmlinuz boot=live components username=tluser
    initrd /live/initrd
}

menuentry "TL Linux Test (Safe Graphics)" {
    linux /live/vmlinuz boot=live nomodeset components username=tluser
    initrd /live/initrd
}
EOF

# Create simple marker file
cat > "$BUILD_DIR/iso/TL-LINUX-TEST.txt" << 'EOF'
This is a TL Linux Test ISO
Version: 1.0.0-test
Built: $(date)

This is a minimal test ISO based on Debian Live.
For full TL Linux experience, use the full build-iso.sh script.

After booting:
1. Open terminal
2. Clone TL Linux: git clone https://github.com/YourRepo/TL-Linux.git
3. Run applications: python3 TL-Linux/apps/accessibility_hub.py

Default credentials:
Username: user
Password: live
EOF

# Rebuild ISO
echo -e "${YELLOW}Creating test ISO...${NC}"
cd "$BUILD_DIR"

genisoimage \
    -rational-rock \
    -volid "TL_LINUX_TEST" \
    -cache-inodes \
    -joliet \
    -full-iso9660-filenames \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -output "$OUTPUT_DIR/$ISO_NAME" \
    iso/

# Make hybrid for USB boot
isohybrid "$OUTPUT_DIR/$ISO_NAME" 2>/dev/null || true

cd - > /dev/null

# Checksums
cd "$OUTPUT_DIR"
sha256sum "$ISO_NAME" > "${ISO_NAME}.sha256"

ISO_SIZE=$(du -h "$ISO_NAME" | cut -f1)

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      TEST ISO BUILD COMPLETED!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}ISO File:${NC}     ${OUTPUT_DIR}/${ISO_NAME}"
echo -e "${BLUE}Size:${NC}         ${ISO_SIZE}"
echo ""
echo -e "${YELLOW}Test with QEMU:${NC}"
echo "  qemu-system-x86_64 -cdrom ${OUTPUT_DIR}/${ISO_NAME} -m 2048"
echo ""
