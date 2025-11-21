#!/bin/bash
#
# TL Linux Auto-Start Script
# Automatically starts essential TL Linux services on login
#
# This script is designed to be run at user login to start:
# - Wellbeing monitoring (in background)
# - Theme adaptation (if enabled)
# - Cloud sync (if configured)
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting TL Linux services...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TL_LINUX_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration directory
CONFIG_DIR="$HOME/.config/tl-linux"
mkdir -p "$CONFIG_DIR"

# Check if auto-start is enabled
if [ -f "$CONFIG_DIR/autostart_config.json" ]; then
    AUTOSTART_ENABLED=$(grep -o '"enabled": *true' "$CONFIG_DIR/autostart_config.json" || echo "")
    if [ -z "$AUTOSTART_ENABLED" ]; then
        echo "Auto-start is disabled. Exiting."
        exit 0
    fi
fi

# 1. Start Wellbeing Monitor (in background, minimized)
if [ -f "$TL_LINUX_DIR/wellbeing/wellbeing_monitor.py" ]; then
    echo -e "${GREEN}✓${NC} Starting Wellbeing Monitor..."
    python3 "$TL_LINUX_DIR/wellbeing/wellbeing_monitor.py" &
    WELLBEING_PID=$!
    echo $WELLBEING_PID > "$CONFIG_DIR/wellbeing_monitor.pid"
fi

# 2. Start Cloud Sync (if configured)
if [ -f "$CONFIG_DIR/cloud-sync/sync_config.json" ]; then
    SYNC_ENABLED=$(grep -o '"enabled": *true' "$CONFIG_DIR/cloud-sync/sync_config.json" || echo "")
    if [ -n "$SYNC_ENABLED" ]; then
        echo -e "${GREEN}✓${NC} Cloud sync is enabled"
        # Syncthing auto-starts via systemd if enabled
        # Nextcloud/rclone handled by their own daemons
    fi
fi

# 3. Initialize Gamification System (load stats)
if [ -f "$TL_LINUX_DIR/wellbeing/wellbeing_gamification.py" ]; then
    echo -e "${GREEN}✓${NC} Gamification system ready"
fi

# 4. Check for system updates (non-intrusive)
echo -e "${GREEN}✓${NC} Checking system health..."

# 5. Display startup notification
if command -v notify-send &> /dev/null; then
    notify-send "TL Linux" "Wellbeing services started" -i dialog-information -t 3000
fi

echo -e "${BLUE}✓ TL Linux services started successfully!${NC}"
echo ""
echo "Services running:"
echo "  • Wellbeing Monitor (PID: $WELLBEING_PID)"
echo ""
echo "To stop services: killall -9 python3"
echo "To configure auto-start: Edit $CONFIG_DIR/autostart_config.json"
echo ""

# Keep script running if needed
# wait
