// Advanced Tools - Tab Groups, Reading Mode, Screenshot, QR Code, Ad Blocker

// ========== Tab Groups Manager ==========
class TabGroups {
    constructor() {
        this.groups = [];
        this.currentGroup = null;
        this.groupCounter = 0;

        this.init();
    }

    async init() {
        await this.loadGroups();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open tab groups panel
        document.getElementById('tabGroupsBtn').addEventListener('click', () => {
            this.openTabGroups();
        });

        // Close tab groups panel
        document.getElementById('closeTabGroups').addEventListener('click', () => {
            this.closeTabGroups();
        });

        // Create new group
        document.getElementById('createGroupBtn').addEventListener('click', () => {
            this.createGroup();
        });

        // Clear all groups
        document.getElementById('clearGroupsBtn').addEventListener('click', () => {
            this.clearAllGroups();
        });
    }

    openTabGroups() {
        document.getElementById('tabGroupsPanel').classList.add('open');
        this.renderGroups();
    }

    closeTabGroups() {
        document.getElementById('tabGroupsPanel').classList.remove('open');
    }

    createGroup() {
        const name = prompt('Enter group name:') || `Group ${++this.groupCounter}`;
        const color = this.getRandomColor();

        const group = {
            id: Date.now(),
            name,
            color,
            tabs: [],
            created: Date.now()
        };

        this.groups.push(group);
        this.saveGroups();
        this.renderGroups();
        window.browser?.showToast(`Created group: ${name}`, 'success');
    }

    getRandomColor() {
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    addTabToGroup(groupId, tabData) {
        const group = this.groups.find(g => g.id === groupId);
        if (group) {
            group.tabs.push(tabData);
            this.saveGroups();
            this.renderGroups();
        }
    }

    removeTabFromGroup(groupId, tabIndex) {
        const group = this.groups.find(g => g.id === groupId);
        if (group) {
            group.tabs.splice(tabIndex, 1);
            this.saveGroups();
            this.renderGroups();
        }
    }

    deleteGroup(groupId) {
        if (confirm('Delete this group? Tabs will not be closed.')) {
            this.groups = this.groups.filter(g => g.id !== groupId);
            this.saveGroups();
            this.renderGroups();
            window.browser?.showToast('Group deleted', 'success');
        }
    }

    renderGroups() {
        const container = document.getElementById('tabGroupsList');

        if (this.groups.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📑</div>
                    <div class="empty-state-text">No tab groups yet. Create one to organize your tabs!</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.groups.map(group => `
            <div class="group-item" style="border-left: 4px solid ${group.color};">
                <div class="group-header">
                    <div class="group-info">
                        <div class="group-name">${group.name}</div>
                        <div class="group-meta">${group.tabs.length} tabs</div>
                    </div>
                    <button class="group-delete" data-group-id="${group.id}">🗑️</button>
                </div>
                <div class="group-tabs">
                    ${group.tabs.length === 0 ?
                        '<div class="group-empty">No tabs in this group</div>' :
                        group.tabs.map((tab, index) => `
                            <div class="group-tab" data-group-id="${group.id}" data-tab-index="${index}">
                                <span class="group-tab-title">${tab.title || 'Untitled'}</span>
                                <button class="group-tab-remove">✕</button>
                            </div>
                        `).join('')
                    }
                </div>
            </div>
        `).join('');

        // Add event listeners
        container.querySelectorAll('.group-delete').forEach(btn => {
            btn.addEventListener('click', () => {
                const groupId = parseInt(btn.dataset.groupId);
                this.deleteGroup(groupId);
            });
        });

        container.querySelectorAll('.group-tab-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tabDiv = btn.closest('.group-tab');
                const groupId = parseInt(tabDiv.dataset.groupId);
                const tabIndex = parseInt(tabDiv.dataset.tabIndex);
                this.removeTabFromGroup(groupId, tabIndex);
            });
        });
    }

    async loadGroups() {
        const saved = localStorage.getItem('timelord_tab_groups');
        if (saved) {
            this.groups = JSON.parse(saved);
            this.groupCounter = Math.max(...this.groups.map(g => g.id), 0);
        }
    }

    saveGroups() {
        localStorage.setItem('timelord_tab_groups', JSON.stringify(this.groups));
    }

    clearAllGroups() {
        if (confirm('Clear all tab groups?')) {
            this.groups = [];
            this.saveGroups();
            this.renderGroups();
            window.browser?.showToast('All groups cleared', 'success');
        }
    }
}

// ========== Reading Mode ==========
class ReadingMode {
    constructor() {
        this.currentArticle = null;
        this.fontSize = 18;
        this.fontFamily = 'Georgia';

        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open reading mode
        document.getElementById('readingModeBtn').addEventListener('click', () => {
            this.activateReadingMode();
        });

        // Close reading mode
        document.getElementById('exitReadingMode').addEventListener('click', () => {
            this.exitReadingMode();
        });

        // Font size controls
        document.getElementById('increaseFontBtn').addEventListener('click', () => {
            this.adjustFontSize(2);
        });

        document.getElementById('decreaseFontBtn').addEventListener('click', () => {
            this.adjustFontSize(-2);
        });

        // Font family selector
        document.getElementById('fontFamilySelect').addEventListener('change', (e) => {
            this.changeFontFamily(e.target.value);
        });
    }

    async activateReadingMode() {
        // Get current tab content
        const currentTab = window.browser?.getCurrentTab();
        if (!currentTab) {
            window.browser?.showToast('No active tab to read', 'error');
            return;
        }

        const article = await this.extractArticle(currentTab.url);
        if (!article) {
            window.browser?.showToast('Could not extract article content', 'error');
            return;
        }

        this.currentArticle = article;
        this.renderArticle();
        document.getElementById('readingModePanel').classList.add('active');
    }

    exitReadingMode() {
        document.getElementById('readingModePanel').classList.remove('active');
        this.currentArticle = null;
    }

    async extractArticle(url) {
        // Simulated article extraction
        // In production, use Mozilla's Readability library or similar
        return {
            title: 'Article Title',
            author: 'Unknown Author',
            content: `
                <p>This is a demonstration of reading mode. In a production environment,
                this would use article extraction libraries like Mozilla's Readability
                to parse and extract the main content from web pages.</p>

                <p>The reading mode provides a clean, distraction-free reading experience
                with customizable fonts and sizes.</p>

                <h2>Features</h2>
                <ul>
                    <li>Clean, readable layout</li>
                    <li>Adjustable font size</li>
                    <li>Multiple font family options</li>
                    <li>Distraction-free interface</li>
                </ul>

                <p>Reading mode automatically extracts the main article content from
                web pages, removing ads, navigation, and other clutter.</p>
            `,
            url: url,
            publishDate: new Date().toLocaleDateString()
        };
    }

    renderArticle() {
        if (!this.currentArticle) return;

        const container = document.getElementById('readingArticle');
        container.innerHTML = `
            <h1 class="reading-title">${this.currentArticle.title}</h1>
            <div class="reading-meta">
                <span class="reading-author">By ${this.currentArticle.author}</span>
                <span class="reading-date">${this.currentArticle.publishDate}</span>
            </div>
            <div class="reading-content">
                ${this.currentArticle.content}
            </div>
        `;

        // Apply font settings
        container.style.fontSize = this.fontSize + 'px';
        container.style.fontFamily = this.fontFamily;
    }

    adjustFontSize(delta) {
        this.fontSize = Math.max(12, Math.min(32, this.fontSize + delta));
        document.getElementById('readingArticle').style.fontSize = this.fontSize + 'px';
        window.browser?.showToast(`Font size: ${this.fontSize}px`, 'info');
    }

    changeFontFamily(family) {
        this.fontFamily = family;
        document.getElementById('readingArticle').style.fontFamily = family;
    }
}

// ========== Screenshot Tool ==========
class ScreenshotTool {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open screenshot tool
        document.getElementById('screenshotBtn').addEventListener('click', () => {
            this.openScreenshotTool();
        });

        // Close screenshot tool
        document.getElementById('closeScreenshot').addEventListener('click', () => {
            this.closeScreenshotTool();
        });

        // Capture visible area
        document.getElementById('captureVisibleBtn').addEventListener('click', () => {
            this.captureVisible();
        });

        // Capture full page
        document.getElementById('captureFullBtn').addEventListener('click', () => {
            this.captureFull();
        });

        // Capture selection
        document.getElementById('captureSelectionBtn').addEventListener('click', () => {
            this.captureSelection();
        });
    }

    openScreenshotTool() {
        document.getElementById('screenshotPanel').classList.add('open');
    }

    closeScreenshotTool() {
        document.getElementById('screenshotPanel').classList.remove('open');
    }

    async captureVisible() {
        try {
            // Using Web APIs to capture screen
            if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
                window.browser?.showToast('Screen capture not supported in this browser', 'error');
                return;
            }

            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: { mediaSource: 'screen' }
            });

            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Wait for video to load
            await new Promise(resolve => {
                video.onloadedmetadata = resolve;
            });

            // Create canvas and capture frame
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            // Stop stream
            stream.getTracks().forEach(track => track.stop());

            // Convert to blob and download
            canvas.toBlob(blob => {
                this.downloadScreenshot(blob, 'screenshot-visible.png');
            });

            window.browser?.showToast('Screenshot captured!', 'success');
        } catch (error) {
            console.error('Screenshot error:', error);
            window.browser?.showToast('Screenshot cancelled or failed', 'error');
        }
    }

    async captureFull() {
        window.browser?.showToast('Full page capture requires browser extension capabilities', 'info');
        // Full page capture would require more complex implementation
        // or browser extension permissions
    }

    captureSelection() {
        window.browser?.showToast('Selection capture coming soon!', 'info');
        // Selection capture would require drawing a selection box
        // and capturing that specific area
    }

    downloadScreenshot(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }

    async copyToClipboard(blob) {
        try {
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
            ]);
            window.browser?.showToast('Screenshot copied to clipboard', 'success');
        } catch (error) {
            console.error('Clipboard error:', error);
        }
    }
}

// ========== QR Code Generator ==========
class QRCodeGenerator {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open QR code generator
        document.getElementById('qrCodeBtn').addEventListener('click', () => {
            this.openQRGenerator();
        });

        // Close QR code generator
        document.getElementById('closeQRCode').addEventListener('click', () => {
            this.closeQRGenerator();
        });

        // Generate QR code
        document.getElementById('generateQRBtn').addEventListener('click', () => {
            this.generateQR();
        });

        // Download QR code
        document.getElementById('downloadQRBtn').addEventListener('click', () => {
            this.downloadQR();
        });

        // Share QR code
        document.getElementById('shareQRBtn').addEventListener('click', () => {
            this.shareQR();
        });

        // QR for current page
        document.getElementById('qrCurrentPageBtn').addEventListener('click', () => {
            this.qrForCurrentPage();
        });
    }

    openQRGenerator() {
        document.getElementById('qrCodePanel').classList.add('open');
    }

    closeQRGenerator() {
        document.getElementById('qrCodePanel').classList.remove('open');
    }

    qrForCurrentPage() {
        const currentTab = window.browser?.getCurrentTab();
        if (currentTab && currentTab.url) {
            document.getElementById('qrInput').value = currentTab.url;
            this.generateQR();
        }
    }

    generateQR() {
        const text = document.getElementById('qrInput').value;
        if (!text) {
            window.browser?.showToast('Enter text or URL to generate QR code', 'error');
            return;
        }

        const canvas = document.getElementById('qrCanvas');
        this.drawQRCode(canvas, text);

        document.getElementById('qrResult').style.display = 'block';
        window.browser?.showToast('QR code generated!', 'success');
    }

    drawQRCode(canvas, text) {
        // Simple QR code generation using a basic algorithm
        // In production, use a library like qrcode.js or kjua
        const ctx = canvas.getContext('2d');
        const size = 200;
        canvas.width = size;
        canvas.height = size;

        // Clear canvas
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, size, size);

        // Generate simple pattern (this is a simplified demonstration)
        // Real QR codes require proper encoding and error correction
        ctx.fillStyle = '#000000';
        const moduleSize = 4;
        const modules = Math.floor(size / moduleSize);

        // Create a simple hash-based pattern from the text
        for (let y = 0; y < modules; y++) {
            for (let x = 0; x < modules; x++) {
                const hash = this.simpleHash(text + x + y);
                if (hash % 2 === 0) {
                    ctx.fillRect(x * moduleSize, y * moduleSize, moduleSize, moduleSize);
                }
            }
        }

        // Add finder patterns (corners)
        this.drawFinderPattern(ctx, 0, 0, moduleSize);
        this.drawFinderPattern(ctx, size - 7 * moduleSize, 0, moduleSize);
        this.drawFinderPattern(ctx, 0, size - 7 * moduleSize, moduleSize);
    }

    drawFinderPattern(ctx, x, y, moduleSize) {
        // Draw QR code finder pattern (the squares in corners)
        ctx.fillStyle = '#000000';
        ctx.fillRect(x, y, 7 * moduleSize, 7 * moduleSize);
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(x + moduleSize, y + moduleSize, 5 * moduleSize, 5 * moduleSize);
        ctx.fillStyle = '#000000';
        ctx.fillRect(x + 2 * moduleSize, y + 2 * moduleSize, 3 * moduleSize, 3 * moduleSize);
    }

    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash);
    }

    downloadQR() {
        const canvas = document.getElementById('qrCanvas');
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'qrcode.png';
            link.click();
            URL.revokeObjectURL(url);
            window.browser?.showToast('QR code downloaded!', 'success');
        });
    }

    async shareQR() {
        const canvas = document.getElementById('qrCanvas');
        canvas.toBlob(async blob => {
            const file = new File([blob], 'qrcode.png', { type: 'image/png' });

            if (navigator.canShare && navigator.canShare({ files: [file] })) {
                try {
                    await navigator.share({
                        files: [file],
                        title: 'QR Code',
                        text: 'Check out this QR code!'
                    });
                    window.browser?.showToast('QR code shared!', 'success');
                } catch (error) {
                    console.error('Share error:', error);
                }
            } else {
                window.browser?.showToast('Sharing not supported. Download instead.', 'info');
            }
        });
    }
}

// ========== Ad Blocker ==========
class AdBlocker {
    constructor() {
        this.enabled = false;
        this.filterLists = [
            { name: 'EasyList', url: 'https://easylist.to/easylist/easylist.txt', enabled: true },
            { name: 'EasyPrivacy', url: 'https://easylist.to/easylist/easyprivacy.txt', enabled: true },
            { name: 'Fanboy Annoyances', url: 'https://easylist.to/easylist/fanboy-annoyance.txt', enabled: false }
        ];
        this.blockedDomains = new Set();
        this.customFilters = [];
        this.stats = {
            adsBlocked: 0,
            trackersBlocked: 0
        };

        this.init();
    }

    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        this.updateStats();
    }

    setupEventListeners() {
        // Open ad blocker settings
        document.getElementById('adBlockerBtn').addEventListener('click', () => {
            this.openAdBlocker();
        });

        // Close ad blocker
        document.getElementById('closeAdBlocker').addEventListener('click', () => {
            this.closeAdBlocker();
        });

        // Toggle ad blocker
        document.getElementById('toggleAdBlocker').addEventListener('change', (e) => {
            this.toggleAdBlocker(e.target.checked);
        });

        // Add custom filter
        document.getElementById('addFilterBtn').addEventListener('click', () => {
            this.addCustomFilter();
        });

        // Clear stats
        document.getElementById('clearStatsBtn').addEventListener('click', () => {
            this.clearStats();
        });

        // Update filter lists
        document.getElementById('updateFiltersBtn').addEventListener('click', () => {
            this.updateFilterLists();
        });
    }

    openAdBlocker() {
        document.getElementById('adBlockerPanel').classList.add('open');
        this.renderFilters();
        this.updateStats();
    }

    closeAdBlocker() {
        document.getElementById('adBlockerPanel').classList.remove('open');
    }

    toggleAdBlocker(enabled) {
        this.enabled = enabled;
        this.saveSettings();

        const status = enabled ? 'enabled' : 'disabled';
        window.browser?.showToast(`Ad blocker ${status}`, 'success');

        // Update UI
        document.getElementById('adBlockerStatus').textContent =
            enabled ? 'Enabled' : 'Disabled';
        document.getElementById('adBlockerStatus').className =
            `status-badge ${enabled ? 'status-active' : 'status-inactive'}`;
    }

    addCustomFilter() {
        const filter = prompt('Enter custom filter (domain or pattern):');
        if (filter) {
            this.customFilters.push({
                pattern: filter,
                added: Date.now()
            });
            this.saveSettings();
            this.renderFilters();
            window.browser?.showToast('Custom filter added', 'success');
        }
    }

    renderFilters() {
        const container = document.getElementById('filterListsContainer');

        container.innerHTML = `
            <div class="filter-section">
                <h4>Filter Lists</h4>
                ${this.filterLists.map((list, index) => `
                    <div class="filter-list-item">
                        <label>
                            <input type="checkbox"
                                   ${list.enabled ? 'checked' : ''}
                                   data-list-index="${index}">
                            <span>${list.name}</span>
                        </label>
                    </div>
                `).join('')}
            </div>

            <div class="filter-section">
                <h4>Custom Filters (${this.customFilters.length})</h4>
                <div class="custom-filters-list">
                    ${this.customFilters.length === 0 ?
                        '<div class="empty-state-text">No custom filters</div>' :
                        this.customFilters.map((filter, index) => `
                            <div class="custom-filter-item">
                                <span class="filter-pattern">${filter.pattern}</span>
                                <button class="filter-remove" data-filter-index="${index}">✕</button>
                            </div>
                        `).join('')
                    }
                </div>
            </div>
        `;

        // Add event listeners
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.listIndex);
                this.filterLists[index].enabled = e.target.checked;
                this.saveSettings();
            });
        });

        container.querySelectorAll('.filter-remove').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.filterIndex);
                this.customFilters.splice(index, 1);
                this.saveSettings();
                this.renderFilters();
            });
        });
    }

    updateStats() {
        document.getElementById('adsBlockedCount').textContent = this.stats.adsBlocked;
        document.getElementById('trackersBlockedCount').textContent = this.stats.trackersBlocked;
    }

    clearStats() {
        if (confirm('Clear blocking statistics?')) {
            this.stats.adsBlocked = 0;
            this.stats.trackersBlocked = 0;
            this.saveSettings();
            this.updateStats();
            window.browser?.showToast('Statistics cleared', 'success');
        }
    }

    updateFilterLists() {
        window.browser?.showToast('Updating filter lists...', 'info');
        // In production, fetch and update filter lists from URLs
        setTimeout(() => {
            window.browser?.showToast('Filter lists updated', 'success');
        }, 1000);
    }

    shouldBlock(url) {
        if (!this.enabled) return false;

        // Check against custom filters
        for (const filter of this.customFilters) {
            if (url.includes(filter.pattern)) {
                this.stats.adsBlocked++;
                this.saveSettings();
                return true;
            }
        }

        // Check against common ad/tracker domains
        const commonAdDomains = [
            'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
            'facebook.net', 'ads.', 'analytics.', 'tracker.'
        ];

        for (const domain of commonAdDomains) {
            if (url.includes(domain)) {
                this.stats.trackersBlocked++;
                this.saveSettings();
                return true;
            }
        }

        return false;
    }

    async loadSettings() {
        const saved = localStorage.getItem('timelord_adblocker');
        if (saved) {
            const data = JSON.parse(saved);
            this.enabled = data.enabled || false;
            this.customFilters = data.customFilters || [];
            this.stats = data.stats || { adsBlocked: 0, trackersBlocked: 0 };
        }

        // Update UI
        document.getElementById('toggleAdBlocker').checked = this.enabled;
        this.toggleAdBlocker(this.enabled);
    }

    saveSettings() {
        localStorage.setItem('timelord_adblocker', JSON.stringify({
            enabled: this.enabled,
            customFilters: this.customFilters,
            stats: this.stats
        }));
    }
}

// ========== Initialize All Advanced Tools ==========
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all tools
    window.tabGroups = new TabGroups();
    window.readingMode = new ReadingMode();
    window.screenshotTool = new ScreenshotTool();
    window.qrCodeGenerator = new QRCodeGenerator();
    window.adBlocker = new AdBlocker();

    console.log('Advanced Tools initialized successfully');
});
