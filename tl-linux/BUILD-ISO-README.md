# TL Linux ISO Build Guide

## Overview

This guide explains how to build a bootable ISO image of TL Linux - The World's Most Accessible Linux Distribution.

## Prerequisites

### System Requirements

- **Host OS**: Debian, Ubuntu, or Debian-based distribution
- **Architecture**: x86_64 (amd64)
- **Free Disk Space**: At least 10GB
- **RAM**: 4GB minimum, 8GB recommended
- **Privileges**: Root access (sudo)

### Required Packages

The build script will automatically install these if missing:

- `debootstrap` - Bootstrap a basic Debian system
- `squashfs-tools` - Create compressed filesystem
- `xorriso` or `genisoimage` - Create ISO images
- `grub-pc-bin` - GRUB bootloader (BIOS)
- `grub-efi-amd64-bin` - GRUB bootloader (UEFI)
- `mtools` - MS-DOS filesystem tools
- `dosfstools` - FAT filesystem tools

Install manually if needed:
```bash
sudo apt-get update
sudo apt-get install debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools
```

## Build Methods

### Method 1: Full Production ISO (Recommended)

Creates a complete, production-ready TL Linux ISO with all features.

**Build Time**: 20-30 minutes (depending on internet speed and CPU)
**ISO Size**: ~2-3 GB

```bash
cd tl-linux
sudo ./build-iso.sh
```

**Output**: `release/tl-linux-1.0.0-amd64.iso`

### Method 2: Quick Test ISO (For Development)

Creates a minimal test ISO based on Debian Live for quick testing.

**Build Time**: 5-10 minutes
**ISO Size**: ~500 MB

```bash
cd tl-linux
sudo ./quick-test-iso.sh
```

**Output**: `release/tl-linux-test-amd64.iso`

## Build Process Steps

The full build process (`build-iso.sh`) performs these steps:

### 1. Dependency Check
- Verifies all required packages are installed
- Auto-installs missing dependencies

### 2. Clean Previous Build
- Removes old build artifacts
- Unmounts any mounted filesystems
- Creates fresh build directories

### 3. Bootstrap Base System
- Uses `debootstrap` to create minimal Debian bookworm system
- Installs core packages (kernel, systemd, live-boot)
- **Duration**: 5-10 minutes

### 4. Setup Chroot Environment
- Mounts /dev, /proc, /sys, /run for chroot operations
- Prepares for system configuration

### 5. Configure System
- Installs desktop environment (XFCE - lightweight & accessible)
- Installs Python 3 and TL Linux dependencies
- Configures accessibility tools (Orca, espeak, etc.)
- Creates default user (tluser/tluser)
- Enables required services
- **Duration**: 10-15 minutes

### 6. Install TL Linux Applications
- Copies all TL Linux apps to /opt/tl-linux/
- Creates desktop entries and autostart files
- Configures welcome message

### 7. Create Compressed Filesystem
- Uses `mksquashfs` to compress the root filesystem
- Compression: XZ with x86 optimization
- **Duration**: 5-10 minutes

### 8. Build Bootable ISO
- Creates GRUB bootloader configuration (UEFI + BIOS)
- Copies kernel and initrd
- Generates hybrid ISO (boots from CD/DVD or USB)
- Creates checksums (SHA256, MD5)

## Build Output

After successful build, you'll find:

```
release/
├── tl-linux-1.0.0-amd64.iso       # Bootable ISO image
├── tl-linux-1.0.0-amd64.iso.sha256  # SHA256 checksum
└── tl-linux-1.0.0-amd64.iso.md5     # MD5 checksum
```

## Testing the ISO

### Method 1: QEMU (Quick Virtual Test)

```bash
# Install QEMU
sudo apt-get install qemu-system-x86

# Test the ISO (2GB RAM)
qemu-system-x86_64 -cdrom release/tl-linux-1.0.0-amd64.iso -m 2048 -enable-kvm

# With more RAM (4GB)
qemu-system-x86_64 -cdrom release/tl-linux-1.0.0-amd64.iso -m 4096 -enable-kvm -smp 2
```

**Tip**: Enable KVM (`-enable-kvm`) for much better performance if your CPU supports it.

### Method 2: VirtualBox

1. Open VirtualBox
2. Create New VM:
   - Name: TL Linux
   - Type: Linux
   - Version: Debian (64-bit)
   - RAM: 2048 MB minimum, 4096 MB recommended
   - Storage: Create virtual hard disk (optional)
3. Settings → Storage → Add optical drive → Select ISO
4. Start the VM

### Method 3: VMware Workstation/Player

1. Create New Virtual Machine
2. Select "Installer disc image file (iso)" → Browse to ISO
3. Guest OS: Linux → Debian 11.x 64-bit
4. Allocate resources (2GB RAM, 20GB disk)
5. Power on the VM

### Method 4: Physical Hardware (USB Boot)

**Write ISO to USB drive:**

#### Linux:
```bash
# Find USB device (usually /dev/sdb, /dev/sdc, etc.)
lsblk

# Write ISO (DANGEROUS - double-check device name!)
sudo dd if=release/tl-linux-1.0.0-amd64.iso of=/dev/sdX bs=4M status=progress
sudo sync

# OR use safer method with confirmation:
sudo dd if=release/tl-linux-1.0.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync oflag=direct
```

#### Windows:
- Use [Rufus](https://rufus.ie/)
- Use [balenaEtcher](https://www.balena.io/etcher/)

#### macOS:
```bash
# Find disk
diskutil list

# Unmount (not eject)
diskutil unmountDisk /dev/diskN

# Write ISO
sudo dd if=tl-linux-1.0.0-amd64.iso of=/dev/rdiskN bs=4m
```

## Boot Options

The ISO includes multiple boot options:

### 1. TL Linux (Live) - **DEFAULT**
- Standard live boot with full TL Linux features
- No persistence (changes lost on reboot)
- Username: `tluser`, Password: `tluser`

### 2. TL Linux (Accessibility Mode)
- Boots with accessibility features pre-enabled
- Screen reader (Orca) auto-starts
- High contrast theme enabled
- Larger fonts

### 3. TL Linux (Safe Mode)
- Uses `nomodeset` for graphics compatibility
- Use if you have display issues
- Works with older graphics cards

### 4. TL Linux (Persistent Storage)
- Saves changes between reboots
- Requires USB with extra partition for persistence
- See persistence setup guide below

## Creating Persistent USB

To save changes between reboots:

```bash
# 1. Write ISO to USB as normal
sudo dd if=release/tl-linux-1.0.0-amd64.iso of=/dev/sdX bs=4M status=progress

# 2. Create persistence partition
# Find the USB device
lsblk

# Create new partition using remaining space
sudo fdisk /dev/sdX
# Press 'n' for new partition, accept defaults
# Press 'w' to write changes

# 3. Format persistence partition
sudo mkfs.ext4 -L persistence /dev/sdX3

# 4. Create persistence configuration
sudo mkdir /mnt/persistence
sudo mount /dev/sdX3 /mnt/persistence
echo "/ union" | sudo tee /mnt/persistence/persistence.conf
sudo umount /mnt/persistence
```

Now boot with "Persistent Storage" option to save changes!

## Customizing the Build

### Modify Package List

Edit the package installation section in `build-iso.sh`:

```bash
# Around line 150-200
apt-get install -y \
    your-custom-package \
    another-package
```

### Change Default User

Edit the user creation section:

```bash
# Around line 230
useradd -m -s /bin/bash -G sudo,audio,video youruser
echo "youruser:yourpassword" | chpasswd
```

### Add Custom Configurations

Add files to the chroot before squashfs creation:

```bash
# After line 250 (after chroot setup)
cp your-config-file "${ROOTFS_DIR}/etc/your-config"
```

## Troubleshooting

### Build fails: "Cannot find debootstrap"
```bash
sudo apt-get install debootstrap
```

### Build fails: "Permission denied"
Run with sudo:
```bash
sudo ./build-iso.sh
```

### Build fails: "No space left on device"
You need at least 10GB free space. Clean up:
```bash
# Remove previous build
sudo rm -rf iso-build/

# Clean APT cache
sudo apt-get clean
```

### ISO won't boot in VirtualBox
Enable EFI in VM settings:
- Settings → System → Enable EFI (special OSes only)

### ISO boots but no GUI appears
Try Safe Mode boot option, or check if system has enough RAM (minimum 2GB).

### "Kernel panic" on boot
- Try Safe Mode option
- Check if CPU supports x86_64 (64-bit)
- Verify ISO checksum wasn't corrupted

### Slow boot from USB
- USB 2.0 drives are very slow - use USB 3.0+
- Some older BIOSes have slow USB initialization

## Advanced: Manual ISO Customization

To manually customize an existing ISO:

```bash
# 1. Extract ISO
mkdir iso-extract
sudo mount -o loop tl-linux-1.0.0-amd64.iso iso-extract
mkdir iso-modify
sudo rsync -a iso-extract/ iso-modify/
sudo umount iso-extract

# 2. Extract squashfs
sudo unsquashfs -d squashfs-root iso-modify/live/filesystem.squashfs

# 3. Chroot and customize
sudo mount --bind /dev squashfs-root/dev
sudo mount --bind /proc squashfs-root/proc
sudo mount --bind /sys squashfs-root/sys
sudo chroot squashfs-root /bin/bash
# Make your changes
exit

# 4. Recreate squashfs
sudo rm iso-modify/live/filesystem.squashfs
sudo mksquashfs squashfs-root iso-modify/live/filesystem.squashfs -comp xz

# 5. Rebuild ISO
sudo genisoimage -o tl-linux-custom.iso \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "TL_LINUX_CUSTOM" \
    iso-modify/
```

## Distribution

### Sharing the ISO

1. **Upload to cloud storage** (Google Drive, Dropbox, etc.)
2. **Create torrent** for faster distribution
3. **Host on website** with checksums
4. **GitHub Release** (if under 2GB)

### Verify Checksums

Recipients should verify ISO integrity:

```bash
# Verify SHA256
sha256sum -c tl-linux-1.0.0-amd64.iso.sha256

# Should output: tl-linux-1.0.0-amd64.iso: OK
```

## Next Steps

After successfully building and testing:

1. ✅ Test all TL Linux applications
2. ✅ Verify accessibility features work
3. ✅ Test on physical hardware
4. ✅ Create installation guide for end users
5. ✅ Set up automatic builds (CI/CD)
6. ✅ Create installer (optional - for permanent installation)

## Support

For build issues:
- Check build logs in `iso-build/`
- Verify system meets prerequisites
- Search existing issues on GitHub
- Create new issue with full error output

## License

TL Linux is distributed under GPL v3 license.
See LICENSE file for details.

---

**Built with ❤️ for accessibility and inclusion**

*Making computing accessible to everyone, regardless of ability.*
