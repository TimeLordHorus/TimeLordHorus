// Download Manager - Track and manage downloads
class DownloadManager {
    constructor() {
        this.downloads = [];
        this.downloadCounter = 0;

        this.init();
    }

    async init() {
        await this.loadDownloads();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open download manager
        document.getElementById('downloadsBtn').addEventListener('click', () => {
            this.openDownloadManager();
        });

        // Close download manager
        document.getElementById('closeDownloadManager').addEventListener('click', () => {
            this.closeDownloadManager();
        });

        // Intercept downloads from the page
        this.setupDownloadInterception();
    }

    openDownloadManager() {
        document.getElementById('downloadManagerPanel').classList.add('open');
        this.renderDownloads();
    }

    closeDownloadManager() {
        document.getElementById('downloadManagerPanel').classList.remove('open');
    }

    setupDownloadInterception() {
        // Monitor for download links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href && link.download) {
                this.trackDownload(link.href, link.download || 'file');
            }
        });
    }

    trackDownload(url, filename) {
        const download = {
            id: ++this.downloadCounter,
            url,
            filename,
            status: 'in_progress',
            progress: 0,
            startTime: Date.now(),
            size: 0
        };

        this.downloads.unshift(download);
        this.saveDownloads();
        this.renderDownloads();

        // Simulate progress (in real implementation, track actual download)
        this.simulateProgress(download.id);
    }

    simulateProgress(downloadId) {
        const download = this.downloads.find(d => d.id === downloadId);
        if (!download) return;

        const interval = setInterval(() => {
            download.progress += Math.random() * 20;

            if (download.progress >= 100) {
                download.progress = 100;
                download.status = 'completed';
                clearInterval(interval);
                window.browser?.showToast(`Download completed: ${download.filename}`, 'success');
            }

            this.saveDownloads();
            this.renderDownloads();
        }, 500);
    }

    renderDownloads() {
        const container = document.getElementById('downloadsList');

        if (this.downloads.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💾</div>
                    <div class="empty-state-text">No downloads yet</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.downloads.map(download => `
            <div class="download-item">
                <span class="download-icon">${download.status === 'completed' ? '✅' : '⏳'}</span>
                <div class="download-info">
                    <div class="download-name">${download.filename}</div>
                    <div class="download-status">
                        ${download.status === 'completed' ? 'Completed' : `Downloading... ${Math.round(download.progress)}%`}
                    </div>
                    ${download.status !== 'completed' ? `
                        <div class="download-progress">
                            <div class="download-progress-fill" style="width: ${download.progress}%"></div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    async loadDownloads() {
        const saved = localStorage.getItem('timelord_downloads');
        if (saved) {
            this.downloads = JSON.parse(saved);
        }
    }

    saveDownloads() {
        // Only save completed downloads
        const toSave = this.downloads.filter(d => d.status === 'completed');
        localStorage.setItem('timelord_downloads', JSON.stringify(toSave));
    }

    clearDownloads() {
        if (confirm('Clear all downloads?')) {
            this.downloads = [];
            this.saveDownloads();
            this.renderDownloads();
            window.browser?.showToast('Downloads cleared', 'success');
        }
    }
}

// Initialize Download Manager
document.addEventListener('DOMContentLoaded', () => {
    window.downloadManager = new DownloadManager();
});
