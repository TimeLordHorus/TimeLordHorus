# TL Linux Makefile
# Simplifies building and testing TL Linux

.PHONY: all iso iso-debian13 test-iso clean check-deps install-deps diagnose fix-repos test-vm help

# Default target
all: help

help:
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  TL Linux Build System"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "Targets:"
	@echo "  make diagnose      - Diagnose system and check build requirements"
	@echo "  make install-deps  - Install required dependencies (auto-detects distro)"
	@echo "  make fix-repos     - Fix broken APT repositories (Debian/Ubuntu only)"
	@echo "  make iso           - Build full production ISO with Debian 12 (~20-30 min)"
	@echo "  make iso-debian13  - Build full production ISO with Debian 13 (~20-30 min)"
	@echo "  make test-iso      - Build quick test ISO (~5-10 min)"
	@echo "  make check-deps    - Check if all dependencies are installed"
	@echo "  make test-vm       - Test latest ISO in QEMU"
	@echo "  make clean         - Clean all build artifacts"
	@echo "  make verify        - Verify ISO checksums"
	@echo "  make usb           - Write ISO to USB (interactive)"
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  sudo make iso              # Build full ISO"
	@echo "  make test-vm               # Test in virtual machine"
	@echo "  sudo make clean iso        # Clean build from scratch"
	@echo ""

# Check if required packages are installed
check-deps:
	@echo "Checking dependencies..."
	@command -v debootstrap >/dev/null 2>&1 || { echo "  ✗ debootstrap not found"; exit 1; }
	@command -v mksquashfs >/dev/null 2>&1 || { echo "  ✗ squashfs-tools not found"; exit 1; }
	@command -v xorriso >/dev/null 2>&1 || command -v genisoimage >/dev/null 2>&1 || { echo "  ✗ xorriso/genisoimage not found"; exit 1; }
	@echo "  ✓ All dependencies satisfied"

# Diagnose system
diagnose:
	@chmod +x diagnose-system.sh
	@./diagnose-system.sh

# Install dependencies (auto-detects distribution)
install-deps:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make install-deps)"; \
		exit 1; \
	fi
	@chmod +x install-build-deps.sh
	@./install-build-deps.sh

# Fix APT repositories (Debian/Ubuntu only)
fix-repos:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make fix-repos)"; \
		exit 1; \
	fi
	@chmod +x fix-repositories.sh
	@./fix-repositories.sh

# Build full production ISO (Debian 12 by default)
iso:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make iso)"; \
		exit 1; \
	fi
	@echo "Building full production ISO (Debian 12 - bookworm)..."
	chmod +x build-iso.sh
	./build-iso.sh

# Build ISO with Debian 13 (Trixie)
iso-debian13:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make iso-debian13)"; \
		exit 1; \
	fi
	@echo "Building full production ISO (Debian 13 - trixie)..."
	chmod +x build-iso.sh
	DEBIAN_RELEASE=trixie ./build-iso.sh

# Build quick test ISO
test-iso:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make test-iso)"; \
		exit 1; \
	fi
	@echo "Building quick test ISO..."
	chmod +x quick-test-iso.sh
	./quick-test-iso.sh

# Test in QEMU
test-vm:
	@if [ ! -f "release/tl-linux-1.0.0-amd64.iso" ] && [ ! -f "release/tl-linux-test-amd64.iso" ]; then \
		echo "Error: No ISO found. Run 'make iso' or 'make test-iso' first."; \
		exit 1; \
	fi
	@echo "Starting QEMU virtual machine..."
	@if [ -f "release/tl-linux-1.0.0-amd64.iso" ]; then \
		qemu-system-x86_64 -cdrom release/tl-linux-1.0.0-amd64.iso -m 2048 -enable-kvm -smp 2; \
	else \
		qemu-system-x86_64 -cdrom release/tl-linux-test-amd64.iso -m 2048 -enable-kvm -smp 2; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Warning: Some files may require sudo to remove"; \
	fi
	rm -rf iso-build/
	rm -rf test-iso-build/
	@echo "✓ Build directories cleaned"
	@echo ""
	@echo "To also remove ISO files, run: rm -rf release/"

# Verify ISO checksums
verify:
	@if [ -f "release/tl-linux-1.0.0-amd64.iso" ]; then \
		echo "Verifying tl-linux-1.0.0-amd64.iso..."; \
		cd release && sha256sum -c tl-linux-1.0.0-amd64.iso.sha256; \
	fi
	@if [ -f "release/tl-linux-test-amd64.iso" ]; then \
		echo "Verifying tl-linux-test-amd64.iso..."; \
		cd release && sha256sum -c tl-linux-test-amd64.iso.sha256; \
	fi

# Write ISO to USB (interactive)
usb:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: Must be run as root (use sudo make usb)"; \
		exit 1; \
	fi
	@if [ ! -f "release/tl-linux-1.0.0-amd64.iso" ]; then \
		echo "Error: ISO not found. Run 'make iso' first."; \
		exit 1; \
	fi
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  WARNING: This will ERASE ALL DATA on the target device!"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
	@echo ""
	@read -p "Enter device (e.g., sdb): " device; \
	if [ -z "$$device" ]; then \
		echo "Cancelled."; \
		exit 1; \
	fi; \
	if [ ! -b "/dev/$$device" ]; then \
		echo "Error: /dev/$$device is not a valid block device"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Writing to /dev/$$device..."; \
	read -p "Are you SURE? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "Cancelled."; \
		exit 1; \
	fi; \
	dd if=release/tl-linux-1.0.0-amd64.iso of=/dev/$$device bs=4M status=progress conv=fsync oflag=direct; \
	sync; \
	echo ""; \
	echo "✓ ISO written to /dev/$$device"

# Package for distribution
package: iso
	@echo "Creating distribution package..."
	@cd release && tar -czf tl-linux-1.0.0-complete.tar.gz \
		tl-linux-1.0.0-amd64.iso \
		tl-linux-1.0.0-amd64.iso.sha256 \
		tl-linux-1.0.0-amd64.iso.md5
	@echo "✓ Package created: release/tl-linux-1.0.0-complete.tar.gz"

# Create release notes
release-notes:
	@echo "Generating release notes..."
	@mkdir -p release
	@echo "TL Linux 1.0.0 \"Chronos\" Release Notes" > release/RELEASE-NOTES.txt
	@echo "========================================" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "Release Date: $$(date +%Y-%m-%d)" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "TL Linux is the world's most accessible Linux distribution, designed" >> release/RELEASE-NOTES.txt
	@echo "specifically for users with ADHD, autism, motor impairments, and" >> release/RELEASE-NOTES.txt
	@echo "visual disabilities." >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "What's New in 1.0.0:" >> release/RELEASE-NOTES.txt
	@echo "--------------------" >> release/RELEASE-NOTES.txt
	@echo "• Complete ADHD/Autism support suite" >> release/RELEASE-NOTES.txt
	@echo "• Advanced motor accessibility (Sticky Keys, Mouse Keys, Slow Keys)" >> release/RELEASE-NOTES.txt
	@echo "• Dual A/B partition system (never brick your system!)" >> release/RELEASE-NOTES.txt
	@echo "• AI voice control and troubleshooting" >> release/RELEASE-NOTES.txt
	@echo "• Professional screen reader and magnification" >> release/RELEASE-NOTES.txt
	@echo "• Modern terminal emulator with tabs" >> release/RELEASE-NOTES.txt
	@echo "• Archive manager for all formats" >> release/RELEASE-NOTES.txt
	@echo "• Screenshot tool with annotations" >> release/RELEASE-NOTES.txt
	@echo "• System log viewer" >> release/RELEASE-NOTES.txt
	@echo "• Complete backup and restore system" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "System Requirements:" >> release/RELEASE-NOTES.txt
	@echo "--------------------" >> release/RELEASE-NOTES.txt
	@echo "• 64-bit processor (x86_64/AMD64)" >> release/RELEASE-NOTES.txt
	@echo "• 2 GB RAM minimum (4 GB recommended)" >> release/RELEASE-NOTES.txt
	@echo "• 20 GB free disk space" >> release/RELEASE-NOTES.txt
	@echo "• USB 2.0 or DVD drive for installation" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "Boot the Live System:" >> release/RELEASE-NOTES.txt
	@echo "---------------------" >> release/RELEASE-NOTES.txt
	@echo "Username: tluser" >> release/RELEASE-NOTES.txt
	@echo "Password: tluser" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "For full documentation, visit:" >> release/RELEASE-NOTES.txt
	@echo "https://github.com/TimeLordHorus/TL-Linux" >> release/RELEASE-NOTES.txt
	@echo "" >> release/RELEASE-NOTES.txt
	@echo "✓ Release notes created"

# Full release build
release: clean iso package release-notes
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  Release build complete!"
	@echo "═══════════════════════════════════════════════════════════"
	@ls -lh release/

# Run application tests (without building ISO)
test-apps:
	@echo "Testing TL Linux applications..."
	@echo "Testing imports..."
	@python3 -c "import tkinter; print('✓ tkinter')"
	@python3 -c "from PIL import Image; print('✓ PIL')" 2>/dev/null || echo "✗ PIL (install: pip3 install pillow)"
	@python3 -c "import pynput; print('✓ pynput')" 2>/dev/null || echo "✗ pynput (install: pip3 install pynput)"
	@echo "Checking app syntax..."
	@for app in apps/*.py system/*.py; do \
		python3 -m py_compile $$app && echo "✓ $$app" || echo "✗ $$app"; \
	done

# Development mode - mount ISO for inspection
inspect-iso:
	@if [ ! -f "release/tl-linux-1.0.0-amd64.iso" ]; then \
		echo "Error: ISO not found"; \
		exit 1; \
	fi
	@mkdir -p iso-mount
	@sudo mount -o loop release/tl-linux-1.0.0-amd64.iso iso-mount
	@echo "ISO mounted at: iso-mount/"
	@echo "To unmount: sudo umount iso-mount && rmdir iso-mount"

# Quick info about the project
info:
	@echo "TL Linux Project Information"
	@echo "═══════════════════════════════════════════════════════════"
	@echo "Version:        1.0.0 'Chronos'"
	@echo "Python Apps:    $$(ls -1 apps/*.py | wc -l)"
	@echo "System Scripts: $$(ls -1 system/*.py | wc -l)"
	@echo "Documentation:  $$(ls -1 docs/*.md 2>/dev/null | wc -l) files"
	@echo "Total Lines:    $$(find apps system -name '*.py' -exec cat {} \; | wc -l)"
	@echo ""
	@if [ -f "release/tl-linux-1.0.0-amd64.iso" ]; then \
		echo "Latest ISO:     $$(du -h release/tl-linux-1.0.0-amd64.iso | cut -f1)"; \
	else \
		echo "Latest ISO:     Not built yet (run 'make iso')"; \
	fi
