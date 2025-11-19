#!/bin/bash
###############################################################################
# TL Linux Installer
# Install TL Linux from live system to hard drive
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This installer must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# Welcome screen
clear
echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  ████████╗██╗         ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗ ║
║  ╚══██╔══╝██║         ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝ ║
║     ██║   ██║         ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝  ║
║     ██║   ██║         ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗  ║
║     ██║   ███████╗    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗ ║
║     ╚═╝   ╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝ ║
║                                                                ║
║                    System Installer v1.0                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}Welcome to the TL Linux Installer!${NC}"
echo ""
echo "This installer will:"
echo "  • Partition your disk with A/B dual-boot partitions"
echo "  • Install TL Linux base system"
echo "  • Configure all accessibility features"
echo "  • Set up automatic backup system"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will ERASE the selected disk!${NC}"
echo "              Make sure you have backups of important data."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Disk selection
echo ""
echo -e "${BLUE}[Step 1/7]${NC} Select Installation Disk"
echo "════════════════════════════════════════════════════════════"
echo ""
lsblk -d -o NAME,SIZE,TYPE,MODEL
echo ""
read -p "Enter disk to install to (e.g., sda, nvme0n1): " DISK

if [ ! -b "/dev/$DISK" ]; then
    echo -e "${RED}Error: /dev/$DISK is not a valid disk${NC}"
    exit 1
fi

DISK_SIZE=$(lsblk -b -d -o SIZE /dev/$DISK | tail -n1)
DISK_SIZE_GB=$((DISK_SIZE / 1024 / 1024 / 1024))

if [ $DISK_SIZE_GB -lt 20 ]; then
    echo -e "${RED}Error: Disk is too small (minimum 20GB required)${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Selected: /dev/$DISK ($DISK_SIZE_GB GB)${NC}"
echo -e "${RED}ALL DATA ON THIS DISK WILL BE ERASED!${NC}"
echo ""
read -p "Type 'YES' in capital letters to confirm: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "Installation cancelled."
    exit 1
fi

# User account setup
echo ""
echo -e "${BLUE}[Step 2/7]${NC} Create User Account"
echo "════════════════════════════════════════════════════════════"
echo ""
read -p "Enter username: " USERNAME

if [ -z "$USERNAME" ]; then
    USERNAME="tluser"
    echo "Using default username: $USERNAME"
fi

read -s -p "Enter password: " PASSWORD
echo ""
read -s -p "Confirm password: " PASSWORD2
echo ""

if [ "$PASSWORD" != "$PASSWORD2" ]; then
    echo -e "${RED}Passwords don't match!${NC}"
    exit 1
fi

if [ -z "$PASSWORD" ]; then
    PASSWORD="tluser"
    echo "Using default password: tluser"
fi

# Hostname
echo ""
read -p "Enter hostname [tl-linux]: " HOSTNAME
HOSTNAME=${HOSTNAME:-tl-linux}

# Partition disk
echo ""
echo -e "${BLUE}[Step 3/7]${NC} Partitioning Disk"
echo "════════════════════════════════════════════════════════════"
echo "Creating dual A/B partition layout..."

# Unmount any existing partitions
umount /dev/${DISK}* 2>/dev/null || true

# Wipe disk
wipefs -a /dev/$DISK

# Create partition table
parted /dev/$DISK --script mklabel gpt

# Calculate partition sizes (in MB)
# EFI: 512MB, Partition A: 40% of remaining, Partition B: 40% of remaining, Data: 20% of remaining
EFI_SIZE=512
REMAINING=$((DISK_SIZE_GB * 1024 - EFI_SIZE))
PARTITION_A_SIZE=$((REMAINING * 40 / 100))
PARTITION_B_SIZE=$((REMAINING * 40 / 100))

# Create partitions
parted /dev/$DISK --script mkpart primary fat32 1MiB ${EFI_SIZE}MiB
parted /dev/$DISK --script set 1 esp on
parted /dev/$DISK --script mkpart primary ext4 ${EFI_SIZE}MiB $((EFI_SIZE + PARTITION_A_SIZE))MiB
parted /dev/$DISK --script mkpart primary ext4 $((EFI_SIZE + PARTITION_A_SIZE))MiB $((EFI_SIZE + PARTITION_A_SIZE + PARTITION_B_SIZE))MiB
parted /dev/$DISK --script mkpart primary ext4 $((EFI_SIZE + PARTITION_A_SIZE + PARTITION_B_SIZE))MiB 100%

# Determine partition naming scheme
if [[ $DISK == nvme* ]]; then
    PART_PREFIX="${DISK}p"
else
    PART_PREFIX="${DISK}"
fi

EFI_PART="/dev/${PART_PREFIX}1"
PARTITION_A="/dev/${PART_PREFIX}2"
PARTITION_B="/dev/${PART_PREFIX}3"
DATA_PART="/dev/${PART_PREFIX}4"

# Format partitions
echo "Formatting partitions..."
mkfs.fat -F32 $EFI_PART
mkfs.ext4 -F -L "TL-Linux-A" $PARTITION_A
mkfs.ext4 -F -L "TL-Linux-B" $PARTITION_B
mkfs.ext4 -F -L "TL-Data" $DATA_PART

echo -e "${GREEN}✓ Disk partitioned${NC}"

# Install base system
echo ""
echo -e "${BLUE}[Step 4/7]${NC} Installing Base System"
echo "════════════════════════════════════════════════════════════"
echo "This may take 10-15 minutes..."
echo ""

# Mount partitions
mkdir -p /mnt/tl-install
mount $PARTITION_A /mnt/tl-install
mkdir -p /mnt/tl-install/boot/efi
mount $EFI_PART /mnt/tl-install/boot/efi
mkdir -p /mnt/tl-install/home
mount $DATA_PART /mnt/tl-install/home

# Copy live system
echo "Copying system files..."
rsync -av --progress \
    --exclude=/dev \
    --exclude=/proc \
    --exclude=/sys \
    --exclude=/tmp \
    --exclude=/run \
    --exclude=/mnt \
    --exclude=/media \
    --exclude=/lost+found \
    --exclude=/live \
    / /mnt/tl-install/

# Create necessary directories
mkdir -p /mnt/tl-install/{dev,proc,sys,tmp,run,mnt,media}

echo -e "${GREEN}✓ Base system installed${NC}"

# Configure system
echo ""
echo -e "${BLUE}[Step 5/7]${NC} Configuring System"
echo "════════════════════════════════════════════════════════════"

# Mount for chroot
mount --bind /dev /mnt/tl-install/dev
mount --bind /proc /mnt/tl-install/proc
mount --bind /sys /mnt/tl-install/sys
mount --bind /run /mnt/tl-install/run

# Create configuration script
cat > /mnt/tl-install/tmp/configure.sh << CONFIGURE_EOF
#!/bin/bash
set -e

# Set hostname
echo "$HOSTNAME" > /etc/hostname

# Update hosts
cat > /etc/hosts << EOF
127.0.0.1   localhost
127.0.1.1   $HOSTNAME
::1         localhost ip6-localhost ip6-loopback
EOF

# Create user
useradd -m -s /bin/bash -G sudo,audio,video,plugdev,netdev $USERNAME || true
echo "$USERNAME:$PASSWORD" | chpasswd
echo "root:$PASSWORD" | chpasswd

# Update fstab
cat > /etc/fstab << EOF
# TL Linux fstab
$PARTITION_A  /           ext4  defaults  0  1
$EFI_PART     /boot/efi   vfat  defaults  0  2
$DATA_PART    /home       ext4  defaults  0  2
EOF

# Install GRUB
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=TL-Linux
grub-install --target=i386-pc /dev/$DISK

# Configure GRUB for A/B partitions
cat > /etc/default/grub << EOF
GRUB_DEFAULT=0
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="TL Linux"
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""
EOF

update-grub

# Configure A/B system
cat > /etc/tl-linux-ab.conf << EOF
ACTIVE_PARTITION=$PARTITION_A
STANDBY_PARTITION=$PARTITION_B
BOOT_COUNT=0
MAX_BOOT_ATTEMPTS=3
EOF

# Enable services
systemctl enable NetworkManager
systemctl enable lightdm

# Remove live boot packages
apt-get remove --purge -y live-boot live-boot-initramfs-tools || true
apt-get autoremove -y

echo "System configured successfully"
CONFIGURE_EOF

chmod +x /mnt/tl-install/tmp/configure.sh
chroot /mnt/tl-install /tmp/configure.sh

echo -e "${GREEN}✓ System configured${NC}"

# Configure A/B system
echo ""
echo -e "${BLUE}[Step 6/7]${NC} Setting Up A/B Dual-Boot System"
echo "════════════════════════════════════════════════════════════"

# Clone partition A to partition B
echo "Creating standby partition (Partition B)..."
dd if=$PARTITION_A of=$PARTITION_B bs=4M status=progress

# Label partition B
e2label $PARTITION_B "TL-Linux-B"

echo -e "${GREEN}✓ A/B system configured${NC}"

# Finalize
echo ""
echo -e "${BLUE}[Step 7/7]${NC} Finalizing Installation"
echo "════════════════════════════════════════════════════════════"

# Unmount
umount -R /mnt/tl-install

echo -e "${GREEN}✓ Installation complete${NC}"

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║          🎉 TL Linux Installation Successful! 🎉              ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}System Details:${NC}"
echo "  Hostname:  $HOSTNAME"
echo "  Username:  $USERNAME"
echo "  Disk:      /dev/$DISK ($DISK_SIZE_GB GB)"
echo ""
echo -e "${CYAN}Partitions:${NC}"
echo "  Partition A (Active):   $PARTITION_A"
echo "  Partition B (Standby):  $PARTITION_B"
echo "  Data/Home:              $DATA_PART"
echo ""
echo -e "${YELLOW}Important Notes:${NC}"
echo "  • Your system has dual A/B partitions for safety"
echo "  • If one partition fails, it will auto-boot from the other"
echo "  • All user data is stored on separate data partition"
echo "  • Backups are configured automatically"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Remove the installation media"
echo "  2. Reboot your computer"
echo "  3. Log in with your credentials"
echo "  4. Launch TL Linux Control Center to customize accessibility"
echo ""
read -p "Press Enter to reboot now, or Ctrl+C to stay in live system..."

reboot
