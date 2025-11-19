// BlueDrop - Bluetooth Sharing Service for TimeLord Browser
class BlueDrop {
    constructor() {
        this.isBluetoothAvailable = 'bluetooth' in navigator;
        this.isConnected = false;
        this.currentDevice = null;
        this.characteristic = null;
        this.shareHistory = [];
        this.maxHistorySize = 50;

        // Bluetooth service UUID (custom UUID for TimeLord Browser)
        this.SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0';
        this.CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1';

        this.init();
    }

    async init() {
        await this.loadShareHistory();
        this.setupEventListeners();
        this.updateUI();

        // Check for Web Share API support as fallback
        this.isWebShareAvailable = 'share' in navigator;
    }

    setupEventListeners() {
        // BlueDrop button
        document.getElementById('blueDropBtn').addEventListener('click', () => {
            this.openBlueDropPanel();
        });

        // Close BlueDrop panel
        document.getElementById('closeBlueDrop').addEventListener('click', () => {
            this.closeBlueDropPanel();
        });

        // Click outside to close
        document.getElementById('blueDropPanel').addEventListener('click', (e) => {
            if (e.target.id === 'blueDropPanel') {
                this.closeBlueDropPanel();
            }
        });

        // Toggle Bluetooth
        document.getElementById('toggleBluetoothBtn').addEventListener('click', () => {
            if (this.isConnected) {
                this.disconnect();
            } else {
                this.connect();
            }
        });

        // Share current page
        document.getElementById('shareCurrentPageBtn').addEventListener('click', () => {
            this.shareCurrentPage();
        });

        // Share file
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.shareFiles(Array.from(e.target.files));
                e.target.value = ''; // Reset file input
            }
        });

        // Share text
        document.getElementById('shareTextBtn').addEventListener('click', () => {
            this.showTextShareModal();
        });

        // Text share modal
        document.getElementById('closeTextModal').addEventListener('click', () => {
            this.closeTextShareModal();
        });

        document.getElementById('cancelTextShare').addEventListener('click', () => {
            this.closeTextShareModal();
        });

        document.getElementById('confirmTextShare').addEventListener('click', () => {
            const text = document.getElementById('shareTextArea').value;
            if (text.trim()) {
                this.shareText(text);
                this.closeTextShareModal();
            }
        });

        // Scan devices
        document.getElementById('scanDevicesBtn').addEventListener('click', () => {
            this.scanDevices();
        });

        // Clear share history
        document.getElementById('clearShareHistoryBtn').addEventListener('click', () => {
            this.clearShareHistory();
        });
    }

    openBlueDropPanel() {
        const panel = document.getElementById('blueDropPanel');
        panel.classList.add('open');
        this.updateUI();
    }

    closeBlueDropPanel() {
        const panel = document.getElementById('blueDropPanel');
        panel.classList.remove('open');
    }

    showTextShareModal() {
        document.getElementById('textShareModal').classList.add('open');
        document.getElementById('shareTextArea').value = '';
        document.getElementById('shareTextArea').focus();
    }

    closeTextShareModal() {
        document.getElementById('textShareModal').classList.remove('open');
    }

    updateUI() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const toggleBtn = document.getElementById('toggleBluetoothBtn');
        const shareSection = document.getElementById('shareSection');
        const deviceSection = document.getElementById('deviceSection');

        if (!this.isBluetoothAvailable) {
            statusIndicator.textContent = '❌';
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Bluetooth not available in this browser';
            toggleBtn.disabled = true;
            toggleBtn.textContent = 'Bluetooth Not Supported';
            shareSection.style.display = 'none';
            deviceSection.style.display = 'none';

            // Show fallback to Web Share API
            if (this.isWebShareAvailable) {
                statusText.textContent += ' (Web Share API available as alternative)';
            }
        } else if (this.isConnected) {
            statusIndicator.textContent = '🟢';
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = `Connected to ${this.currentDevice ? this.currentDevice.name : 'device'}`;
            toggleBtn.textContent = 'Disconnect';
            shareSection.style.display = 'block';
            deviceSection.style.display = 'block';
        } else {
            statusIndicator.textContent = '⚫';
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Bluetooth disconnected';
            toggleBtn.textContent = 'Enable Bluetooth';
            shareSection.style.display = 'none';
            deviceSection.style.display = 'none';
        }

        this.renderShareHistory();
    }

    async connect() {
        if (!this.isBluetoothAvailable) {
            window.browser?.showToast('Bluetooth is not available in this browser', 'error');
            return;
        }

        try {
            window.browser?.showToast('Requesting Bluetooth device...', 'info');

            // Request Bluetooth device
            const device = await navigator.bluetooth.requestDevice({
                acceptAllDevices: true,
                optionalServices: [this.SERVICE_UUID]
            });

            window.browser?.showToast(`Connecting to ${device.name}...`, 'info');

            // Connect to GATT server
            const server = await device.gatt.connect();
            this.currentDevice = device;
            this.isConnected = true;

            // Try to get our custom service (may not exist on all devices)
            try {
                const service = await server.getPrimaryService(this.SERVICE_UUID);
                this.characteristic = await service.getCharacteristic(this.CHARACTERISTIC_UUID);
            } catch (e) {
                console.log('Custom service not found, basic connection established');
            }

            // Handle disconnect
            device.addEventListener('gattserverdisconnected', () => {
                this.onDisconnected();
            });

            window.browser?.showToast(`Connected to ${device.name}!`, 'success');
            this.updateUI();

        } catch (error) {
            console.error('Bluetooth connection error:', error);

            if (error.name === 'NotFoundError') {
                window.browser?.showToast('No device selected', 'error');
            } else if (error.name === 'SecurityError') {
                window.browser?.showToast('Bluetooth access denied', 'error');
            } else {
                window.browser?.showToast(`Connection failed: ${error.message}`, 'error');
            }
        }
    }

    disconnect() {
        if (this.currentDevice && this.currentDevice.gatt.connected) {
            this.currentDevice.gatt.disconnect();
        }
        this.onDisconnected();
    }

    onDisconnected() {
        this.isConnected = false;
        this.currentDevice = null;
        this.characteristic = null;
        this.updateUI();
        window.browser?.showToast('Bluetooth disconnected', 'info');
    }

    async scanDevices() {
        window.browser?.showToast('Device scanning initiated', 'info');

        // Web Bluetooth API doesn't have a separate scan function
        // Scanning happens when requesting a device
        // Show message to user
        const deviceList = document.getElementById('deviceList');
        deviceList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📡</div>
                <div class="empty-state-text">
                    Click "Enable Bluetooth" to scan and connect to devices.
                    You'll see a list of available Bluetooth devices.
                </div>
            </div>
        `;
    }

    async shareCurrentPage() {
        const tab = window.browser?.tabs.find(t => t.id === window.browser.activeTabId);
        if (!tab) return;

        const shareData = {
            title: tab.title,
            url: tab.url,
            text: `Check out: ${tab.title}`
        };

        await this.share(shareData, 'link');
    }

    async shareFiles(files) {
        for (const file of files) {
            const shareData = {
                files: [file],
                title: file.name,
                text: `Sharing file: ${file.name}`
            };

            await this.share(shareData, 'file', file.name, file.size);
        }
    }

    async shareText(text) {
        const shareData = {
            text: text,
            title: 'Shared Text'
        };

        await this.share(shareData, 'text');
    }

    async share(data, type, name = null, size = null) {
        // Try Web Share API first (works on mobile and some desktop browsers)
        if (this.isWebShareAvailable && navigator.canShare && navigator.canShare(data)) {
            try {
                await navigator.share(data);

                // Add to history
                this.addToHistory({
                    type: type,
                    name: name || data.title || 'Shared content',
                    size: size,
                    timestamp: Date.now(),
                    method: 'Web Share API'
                });

                window.browser?.showToast('Shared successfully!', 'success');
                this.showTransferProgress(name || data.title, 100);
                return;
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error('Share error:', error);
                }
            }
        }

        // Fallback: Try Bluetooth if connected
        if (this.isConnected && this.characteristic) {
            try {
                // Convert data to bytes
                const dataString = JSON.stringify({
                    type: type,
                    data: data,
                    timestamp: Date.now()
                });

                const encoder = new TextEncoder();
                const bytes = encoder.encode(dataString);

                // Bluetooth characteristics have a maximum size (typically 512 bytes)
                // For larger data, we'd need to chunk it
                if (bytes.length > 512) {
                    window.browser?.showToast('Data too large for Bluetooth transfer', 'error');
                    this.useAlternativeShare(data, type);
                    return;
                }

                await this.characteristic.writeValue(bytes);

                // Add to history
                this.addToHistory({
                    type: type,
                    name: name || data.title || 'Shared content',
                    size: size,
                    timestamp: Date.now(),
                    method: 'Bluetooth'
                });

                window.browser?.showToast('Sent via Bluetooth!', 'success');
                this.showTransferProgress(name || data.title, 100);

            } catch (error) {
                console.error('Bluetooth transfer error:', error);
                window.browser?.showToast('Bluetooth transfer failed', 'error');
                this.useAlternativeShare(data, type);
            }
        } else {
            // No sharing method available
            this.useAlternativeShare(data, type);
        }
    }

    useAlternativeShare(data, type) {
        // Fallback methods
        if (type === 'link' && data.url) {
            // Copy link to clipboard
            navigator.clipboard.writeText(data.url).then(() => {
                window.browser?.showToast('Link copied to clipboard!', 'success');
                this.addToHistory({
                    type: type,
                    name: data.title || 'Link',
                    timestamp: Date.now(),
                    method: 'Clipboard'
                });
            }).catch(() => {
                window.browser?.showToast('Unable to share. Please connect Bluetooth or use a supported browser.', 'error');
            });
        } else if (type === 'text' && data.text) {
            // Copy text to clipboard
            navigator.clipboard.writeText(data.text).then(() => {
                window.browser?.showToast('Text copied to clipboard!', 'success');
                this.addToHistory({
                    type: type,
                    name: 'Text',
                    timestamp: Date.now(),
                    method: 'Clipboard'
                });
            }).catch(() => {
                window.browser?.showToast('Unable to share text', 'error');
            });
        } else if (type === 'file') {
            window.browser?.showToast('File sharing requires Bluetooth connection or Web Share API support', 'error');
        }
    }

    showTransferProgress(name, progress) {
        const transferSection = document.getElementById('transferSection');
        const transferName = document.getElementById('transferName');
        const transferStatus = document.getElementById('transferStatus');
        const progressFill = document.getElementById('progressFill');

        transferSection.style.display = 'block';
        transferName.textContent = name;
        progressFill.style.width = progress + '%';
        transferStatus.textContent = progress === 100 ? 'Complete!' : `${progress}%`;

        if (progress === 100) {
            setTimeout(() => {
                transferSection.style.display = 'none';
            }, 3000);
        }
    }

    addToHistory(item) {
        this.shareHistory.unshift(item);

        // Limit history size
        if (this.shareHistory.length > this.maxHistorySize) {
            this.shareHistory = this.shareHistory.slice(0, this.maxHistorySize);
        }

        this.saveShareHistory();
        this.renderShareHistory();
    }

    async loadShareHistory() {
        try {
            const saved = localStorage.getItem('bluedrop_history');
            if (saved) {
                this.shareHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading share history:', error);
        }
    }

    saveShareHistory() {
        try {
            localStorage.setItem('bluedrop_history', JSON.stringify(this.shareHistory));
        } catch (error) {
            console.error('Error saving share history:', error);
        }
    }

    renderShareHistory() {
        const container = document.getElementById('shareHistory');

        if (this.shareHistory.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📤</div>
                    <div class="empty-state-text">No recent shares</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.shareHistory.map(item => {
            const icon = this.getTypeIcon(item.type);
            const timeAgo = this.getTimeAgo(item.timestamp);
            const sizeStr = item.size ? this.formatFileSize(item.size) : '';

            return `
                <div class="share-history-item">
                    <span class="history-icon">${icon}</span>
                    <div class="history-details">
                        <div class="history-item-name">${item.name}${sizeStr ? ` (${sizeStr})` : ''}</div>
                        <div class="history-item-time">${timeAgo} • ${item.method}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getTypeIcon(type) {
        const icons = {
            'link': '🔗',
            'file': '📁',
            'text': '📝',
            'image': '🖼️'
        };
        return icons[type] || '📤';
    }

    getTimeAgo(timestamp) {
        const seconds = Math.floor((Date.now() - timestamp) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

        return new Date(timestamp).toLocaleDateString();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    clearShareHistory() {
        if (confirm('Are you sure you want to clear all share history?')) {
            this.shareHistory = [];
            this.saveShareHistory();
            this.renderShareHistory();
            window.browser?.showToast('Share history cleared', 'success');
        }
    }
}

// Initialize BlueDrop when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.blueDrop = new BlueDrop();
});
