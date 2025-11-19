# TL Linux - IPFS Integration

## Overview

TL Linux includes a complete IPFS (InterPlanetary File System) integration, providing decentralized, peer-to-peer file storage and sharing capabilities. IPFS allows you to store and access files in a distributed network, making your data resilient, censorship-resistant, and permanently available.

## What is IPFS?

IPFS is a protocol and peer-to-peer network for storing and sharing data in a distributed file system. Instead of referring to files by their location (like traditional URLs), IPFS uses content-addressing to identify each file in a global namespace.

### Key Benefits

- **Decentralized**: No single point of failure
- **Permanent**: Content-addressed files are immutable
- **Efficient**: Deduplication saves storage space
- **Fast**: Retrieve data from the nearest peer
- **Resilient**: Files remain available even if the original source goes offline
- **Free**: No storage fees or subscriptions

## Components

### 1. IPFS Node Manager (`storage/ipfs_node.py`)

Core functionality for managing an IPFS daemon and performing operations.

**Features:**
- Start/stop IPFS daemon
- Initialize IPFS repository
- Add files and directories to IPFS
- Retrieve files from IPFS
- Pin/unpin content
- Publish to IPNS (InterPlanetary Name System)
- Query node statistics and peer information

**Key Functions:**

```python
from storage.ipfs_node import get_global_node

# Get IPFS node instance
ipfs = get_global_node()

# Start daemon
success, msg = ipfs.start_daemon()

# Add file to IPFS
ipfs_hash, error = ipfs.add_file('/path/to/file.txt')

# Retrieve file from IPFS
success, error = ipfs.get_file(ipfs_hash, '/path/to/output.txt')

# Pin file to keep it locally
success, error = ipfs.pin_file(ipfs_hash)

# Get gateway URL
url = ipfs.get_gateway_url(ipfs_hash)
```

### 2. IPFS Storage Manager (`apps/ipfs_storage.py`)

GUI application for managing files in IPFS with a user-friendly interface.

**Features:**
- Add files and folders to IPFS
- Import files from IPFS hashes
- View and manage stored content
- Pin/unpin files
- Download files from IPFS
- Copy IPFS hashes to clipboard
- Open files in web gateway
- Track local and IPFS media separately
- View pinned items
- Node statistics and peer information

**Usage:**

```bash
python tl-linux/apps/ipfs_storage.py
```

### 3. Media Player with IPFS Support (`apps/media_player.py`)

Full-featured media player that can play audio and video from both local storage and IPFS.

**Features:**
- Play audio files (MP3, WAV, OGG, FLAC, M4A)
- Video support (MP4, AVI, MKV, WebM)
- Stream media from IPFS gateway
- Organize media library
- Create and manage playlists
- Add media directly from IPFS hashes
- Volume control and playback controls
- Integration with IPFS Storage Manager

**Supported Formats:**
- **Audio**: MP3, WAV, OGG, FLAC, M4A
- **Video**: MP4, AVI, MKV, WebM

**Usage:**

```bash
python tl-linux/apps/media_player.py
```

### 4. IPFS Settings (`apps/ipfs_settings.py`)

Configuration interface for IPFS node settings and advanced operations.

**Features:**
- Configure auto-start behavior
- Set custom IPFS repository path
- Configure network ports (API, Gateway, Swarm)
- View node information and status
- Check IPFS installation
- Run garbage collection
- Reinitialize repository
- View IPFS configuration file

**Usage:**

```bash
python tl-linux/apps/ipfs_settings.py
```

## Installation

### 1. Install IPFS

TL Linux requires IPFS to be installed on your system. Choose one of the following methods:

#### Option A: Using Snap (Recommended for Ubuntu/Debian)

```bash
sudo snap install ipfs
```

#### Option B: Using Official Binary

```bash
# Download IPFS
wget https://dist.ipfs.tech/kubo/v0.21.0/kubo_v0.21.0_linux-amd64.tar.gz

# Extract
tar -xvzf kubo_v0.21.0_linux-amd64.tar.gz

# Install
cd kubo
sudo bash install.sh

# Verify installation
ipfs version
```

#### Option C: Using Package Manager

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install ipfs

# Fedora
sudo dnf install ipfs

# Arch Linux
sudo pacman -S kubo
```

### 2. Install Python Dependencies

```bash
# Optional: For enhanced IPFS functionality
pip install ipfshttpclient

# For media playback
pip install pygame

# For image/video thumbnails
pip install pillow
```

### 3. Initialize IPFS

The IPFS Storage Manager will automatically initialize IPFS on first run, or you can do it manually:

```bash
ipfs init
```

## Getting Started

### Quick Start Guide

1. **Launch IPFS Storage Manager**
   ```bash
   python tl-linux/apps/ipfs_storage.py
   ```

2. **Start IPFS Daemon**
   - Click "🚀 Start IPFS" in the toolbar
   - Wait for status indicator to turn green

3. **Add Files to IPFS**
   - Click "➕ Add Files" to add individual files
   - Click "📁 Add Folder" to add entire directories
   - Files are automatically pinned to your local node

4. **View Your Content**
   - Browse files in the "📄 Files" tab
   - Media files appear in "🎵 Media Library" tab
   - View all pinned content in "📌 Pinned Items" tab

5. **Share Content**
   - Select a file
   - Click "📋 Copy Hash" to copy IPFS hash
   - Share the hash with others to give them access

### Accessing Files

Files in IPFS can be accessed in multiple ways:

#### 1. IPFS Hash (CID)

Every file has a unique Content Identifier (CID):

```
QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
```

#### 2. Gateway URL

Access via HTTP through the IPFS gateway:

```
http://127.0.0.1:8080/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
```

Or use public gateways:

```
https://ipfs.io/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
https://gateway.pinata.cloud/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
```

#### 3. IPFS Protocol

Direct IPFS protocol access:

```
ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
```

## Common Use Cases

### 1. Personal File Backup

Store important files in IPFS for permanent, decentralized backup:

```python
from storage.ipfs_node import get_global_node

ipfs = get_global_node()
ipfs.start_daemon()

# Backup a folder
ipfs_hash, error = ipfs.add_directory('/home/user/Documents')
print(f"Backup hash: {ipfs_hash}")

# Pin to ensure it stays available
ipfs.pin_file(ipfs_hash)
```

### 2. Media Library

Store and stream your music/video collection:

1. Add media files via IPFS Storage Manager
2. Files automatically appear in Media Player
3. Stream from IPFS gateway (no local storage needed)
4. Share with friends using IPFS hashes

### 3. File Sharing

Share files with anyone without central servers:

1. Add file to IPFS Storage Manager
2. Copy IPFS hash
3. Share hash via email, chat, etc.
4. Recipients can download using the hash

### 4. Website Hosting

Host static websites on IPFS:

```bash
# Add website directory
ipfs add -r /path/to/website

# Publish to IPNS for updatable address
ipfs name publish <website-hash>

# Access at: http://127.0.0.1:8080/ipns/<your-peer-id>
```

### 5. Permanent Document Storage

Store documents that need to be permanently accessible:

- Academic papers
- Legal documents
- Historical records
- Open data
- Creative works

## Advanced Features

### Pinning

**Pinning** keeps content available on your node. Unpinned content may be garbage collected to free space.

**Pin a file:**
```python
ipfs.pin_file('QmHash...')
```

**Unpin a file:**
```python
ipfs.unpin_file('QmHash...')
```

**List all pins:**
```python
pins, error = ipfs.list_pins()
for pin in pins:
    print(f"{pin['hash']} - {pin['type']}")
```

### IPNS (InterPlanetary Name System)

IPNS allows you to create mutable pointers to IPFS content. This is useful for content that changes over time.

**Publish to IPNS:**
```python
ipns_name, error = ipfs.publish_to_ipns('QmHash...')
print(f"Published to: {ipns_name}")
```

**Resolve IPNS name:**
```python
ipfs_hash, error = ipfs.resolve_ipns('/ipns/QmPeerId...')
```

### Garbage Collection

Free up space by removing unpinned content:

1. Open IPFS Settings
2. Go to "Advanced" tab
3. Click "🗑️ Clean Repository (Garbage Collection)"

Or via command line:
```bash
ipfs repo gc
```

### Node Statistics

View repository statistics:

```python
stats, error = ipfs.get_stats()
print(f"Repo size: {stats['RepoSize']} bytes")
print(f"Objects: {stats['NumObjects']}")
```

### Peer Management

View connected peers:

```python
peers, error = ipfs.get_peers()
print(f"Connected to {len(peers)} peers")
```

## Configuration

### Default Ports

- **API**: 5001
- **Gateway**: 8080
- **Swarm**: 4001

### Change Ports

1. Open IPFS Settings
2. Modify port numbers in "General" tab
3. Save settings
4. Restart IPFS daemon

### Custom Repository Path

1. Open IPFS Settings
2. Set custom path in "IPFS Repository Path"
3. Save and reinitialize if needed

### Auto-Start

Enable auto-start to launch IPFS daemon automatically:

1. Open IPFS Settings
2. Check "Start IPFS daemon on application launch"
3. Save settings

## Troubleshooting

### IPFS Daemon Won't Start

1. Check if IPFS is installed: `ipfs version`
2. Check if another instance is running: `ipfs shutdown`
3. Check repository is initialized: `ipfs init`
4. Check logs: `ipfs log tail`

### Cannot Add Files

1. Ensure IPFS daemon is running (green indicator)
2. Check disk space
3. Verify file permissions
4. Check IPFS repository isn't corrupted

### Files Not Accessible

1. Ensure file is pinned
2. Check if daemon is running
3. Try accessing via gateway URL
4. Check if you're connected to peers

### Slow Performance

1. Check peer connections
2. Run garbage collection to free space
3. Ensure adequate network bandwidth
4. Try different gateway

### Repository Corruption

If repository becomes corrupted:

1. Backup important data
2. Open IPFS Settings → Advanced
3. Click "🔄 Reinitialize Repository"
4. Re-add your content

## Best Practices

### 1. Pin Important Content

Always pin content you want to keep available:
- Personal files
- Media library
- Documents you share

### 2. Regular Garbage Collection

Run garbage collection periodically to free space:
- Weekly for active users
- Monthly for light users

### 3. Backup Hashes

Keep a record of important IPFS hashes:
- Store in a text file
- Use the IPFS Storage Manager index
- Export to external backup

### 4. Use IPNS for Mutable Content

For content that updates:
- Publish to IPNS
- Update with new hash when content changes
- Share IPNS name instead of hash

### 5. Monitor Repository Size

Keep an eye on repository size:
- Check in IPFS Settings
- Unpin unused content
- Run garbage collection when needed

### 6. Connect to Reliable Peers

Better peer connections = better performance:
- Bootstrap to public nodes
- Connect to geographically close peers
- Join community-hosted nodes

## Security & Privacy

### What's Public?

- **Content**: All data added to IPFS is public by default
- **Hashes**: Anyone with a hash can access the content
- **Metadata**: File names, sizes, and structure are visible

### What's Private?

- **Your IP**: Can be hidden using Tor or VPN
- **Repository contents**: Unless you share hashes, others don't know what you have
- **Pinned items**: Your pin list is local

### Encryption

IPFS doesn't encrypt content by default. To store private data:

1. Encrypt files before adding to IPFS
2. Only share hashes with intended recipients
3. Use additional encryption tools (GPG, age, etc.)

### Best Practices

- Don't upload sensitive data without encryption
- Be careful what you pin (you're helping host it)
- Use VPN/Tor if anonymity is important
- Regularly review pinned content

## Resources

### Official Documentation

- IPFS Docs: https://docs.ipfs.tech/
- IPFS Concepts: https://docs.ipfs.tech/concepts/
- Command Reference: https://docs.ipfs.tech/reference/cli/

### Community

- IPFS Forums: https://discuss.ipfs.tech/
- Discord: https://discord.gg/ipfs
- Reddit: https://reddit.com/r/ipfs

### Tools

- IPFS Desktop: https://github.com/ipfs/ipfs-desktop
- IPFS Companion (Browser Extension): https://github.com/ipfs/ipfs-companion
- Public Gateways: https://ipfs.github.io/public-gateway-checker/

### Learning

- ProtoSchool Tutorials: https://proto.school/
- IPFS YouTube Channel: https://www.youtube.com/c/IPFSbot
- Awesome IPFS: https://awesome.ipfs.tech/

## API Reference

### IPFSNode Class

```python
from storage.ipfs_node import IPFSNode

ipfs = IPFSNode(ipfs_path='/custom/path')
```

#### Methods

**`is_ipfs_installed()`** → bool
- Check if IPFS is installed on system

**`is_initialized()`** → bool
- Check if IPFS repository is initialized

**`initialize()`** → (success: bool, message: str)
- Initialize IPFS repository

**`start_daemon(background=True)`** → (success: bool, message: str)
- Start IPFS daemon

**`stop_daemon()`** → (success: bool, message: str)
- Stop IPFS daemon

**`add_file(file_path)`** → (hash: str, error: str)
- Add file to IPFS, returns CID

**`add_directory(dir_path, recursive=True)`** → (hash: str, error: str)
- Add directory to IPFS, returns root CID

**`get_file(ipfs_hash, output_path=None)`** → (success: bool, error: str)
- Retrieve file from IPFS

**`cat_file(ipfs_hash)`** → (content: bytes, error: str)
- Read file content from IPFS

**`pin_file(ipfs_hash)`** → (success: bool, error: str)
- Pin file to local storage

**`unpin_file(ipfs_hash)`** → (success: bool, error: str)
- Unpin file from local storage

**`list_pins()`** → (pins: list, error: str)
- List all pinned files

**`get_stats()`** → (stats: dict, error: str)
- Get repository statistics

**`get_peers()`** → (peers: list, error: str)
- Get connected peers

**`get_gateway_url(ipfs_hash)`** → str
- Get HTTP gateway URL for hash

**`publish_to_ipns(ipfs_hash, key='self')`** → (ipns_name: str, error: str)
- Publish hash to IPNS

**`resolve_ipns(ipns_name)`** → (ipfs_hash: str, error: str)
- Resolve IPNS name to IPFS hash

## Frequently Asked Questions

### Q: Is IPFS free to use?
**A:** Yes, IPFS is completely free and open source. No subscriptions or fees.

### Q: How much storage do I need?
**A:** Only for files you pin. Unpinned files can be garbage collected. Storage is local to your machine.

### Q: Can I delete files from IPFS?
**A:** You can unpin files and run garbage collection to remove them from your node, but if others have pinned them, they remain on the network.

### Q: Is IPFS anonymous?
**A:** No, but you can use Tor or VPN for privacy. Your IP is visible to peers you connect to.

### Q: How fast is IPFS?
**A:** Speed depends on peer availability and network conditions. Popular files are faster. Local files are instant.

### Q: Can I use IPFS offline?
**A:** Yes, you can access locally pinned content offline. You need internet to access content from other peers.

### Q: What's the file size limit?
**A:** No hard limit, but very large files (>100GB) may be impractical. Consider splitting or chunking.

### Q: How do I permanently host content?
**A:** Pin it on your node and keep your node running, or use a pinning service like Pinata, Filebase, or Fleek.

### Q: Can IPFS replace cloud storage?
**A:** For some use cases, yes. It's great for public content, backups, and distribution. Not ideal for private data without encryption.

### Q: Is my data safe on IPFS?
**A:** Data is safe from censorship and loss (if widely pinned), but it's public unless encrypted. Don't share sensitive data without encryption.

---

## Support

For issues, questions, or contributions related to TL Linux IPFS integration:

- Open an issue on GitHub
- Check the TL Linux documentation
- Join the TL Linux community chat

**Happy decentralizing! 🌐**
