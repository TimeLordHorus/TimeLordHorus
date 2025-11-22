// File Manager with Cloud Storage Integration
class FileManager {
    constructor() {
        this.currentProvider = 'local';
        this.currentPath = '/';
        this.files = [];
        this.storageQuota = {
            usage: 0,
            quota: 0
        };

        // Cloud storage tokens (would need OAuth in production)
        this.cloudTokens = {
            google: null,
            dropbox: null,
            onedrive: null
        };

        this.init();
    }

    async init() {
        await this.loadFiles();
        await this.updateStorageQuota();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Open file manager
        document.getElementById('fileManagerBtn').addEventListener('click', () => {
            this.openFileManager();
        });

        // Close file manager
        document.getElementById('closeFileManager').addEventListener('click', () => {
            this.closeFileManager();
        });

        // Click outside to close
        document.getElementById('fileManagerPanel').addEventListener('click', (e) => {
            if (e.target.id === 'fileManagerPanel') {
                this.closeFileManager();
            }
        });

        // Provider selection
        document.querySelectorAll('.provider-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const provider = e.currentTarget.dataset.provider;
                this.switchProvider(provider);
            });
        });

        // File operations
        document.getElementById('uploadFileBtn').addEventListener('click', () => {
            document.getElementById('fileUploadInput').click();
        });

        document.getElementById('fileUploadInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFiles(Array.from(e.target.files));
                e.target.value = '';
            }
        });

        document.getElementById('newFolderBtn').addEventListener('click', () => {
            this.createFolder();
        });

        document.getElementById('refreshFilesBtn').addEventListener('click', () => {
            this.refreshFiles();
        });
    }

    openFileManager() {
        document.getElementById('fileManagerPanel').classList.add('open');
        this.refreshFiles();
    }

    closeFileManager() {
        document.getElementById('fileManagerPanel').classList.remove('open');
    }

    async switchProvider(provider) {
        // Update UI
        document.querySelectorAll('.provider-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.provider === provider);
        });

        this.currentProvider = provider;
        this.currentPath = '/';

        if (provider !== 'local') {
            // Check if connected to cloud provider
            if (!this.cloudTokens[provider]) {
                window.browser?.showToast(`Connecting to ${provider}...`, 'info');
                await this.connectToCloud(provider);
            }
        }

        this.refreshFiles();
    }

    async connectToCloud(provider) {
        // Simulated OAuth flow (in production, implement proper OAuth)
        window.browser?.showToast(`${provider} connection not yet configured. Using demo mode.`, 'info');

        // For demo purposes, create sample cloud files
        this.cloudTokens[provider] = 'demo_token';
    }

    async uploadFiles(files) {
        for (const file of files) {
            try {
                const fileData = {
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    lastModified: file.lastModified,
                    path: this.currentPath,
                    provider: this.currentProvider,
                    data: await this.readFileAsBase64(file)
                };

                // Save to IndexedDB
                await this.saveFile(fileData);

                window.browser?.showToast(`Uploaded: ${file.name}`, 'success');
            } catch (error) {
                console.error('Upload error:', error);
                window.browser?.showToast(`Failed to upload: ${file.name}`, 'error');
            }
        }

        this.refreshFiles();
        this.updateStorageQuota();
    }

    readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async saveFile(fileData) {
        const transaction = window.browser.db.transaction(['files'], 'readwrite');
        const store = transaction.objectStore('files');

        // Create files object store if it doesn't exist
        return new Promise((resolve, reject) => {
            try {
                const request = store.add(fileData);
                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            } catch (error) {
                // Store might not exist, create it
                this.createFilesStore().then(() => {
                    this.saveFile(fileData).then(resolve).catch(reject);
                });
            }
        });
    }

    async createFilesStore() {
        // This would need to be done during database initialization
        // For now, we'll store files in localStorage as a fallback
        const files = JSON.parse(localStorage.getItem('timelord_files') || '[]');
        files.push(fileData);
        localStorage.setItem('timelord_files', JSON.stringify(files));
    }

    async loadFiles() {
        try {
            // Try IndexedDB first
            const transaction = window.browser.db.transaction(['files'], 'readonly');
            const store = transaction.objectStore('files');
            const request = store.getAll();

            request.onsuccess = () => {
                this.files = request.result.filter(f =>
                    f.provider === this.currentProvider &&
                    f.path === this.currentPath
                );
                this.renderFiles();
            };
        } catch (error) {
            // Fallback to localStorage
            const allFiles = JSON.parse(localStorage.getItem('timelord_files') || '[]');
            this.files = allFiles.filter(f =>
                f.provider === this.currentProvider &&
                f.path === this.currentPath
            );
            this.renderFiles();
        }
    }

    renderFiles() {
        const container = document.getElementById('fileList');

        if (this.files.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📂</div>
                    <div class="empty-state-text">No files yet. Upload files or connect to cloud storage.</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.files.map((file, index) => `
            <div class="file-item" data-file-id="${index}">
                <span class="file-item-icon">${this.getFileIcon(file.type)}</span>
                <div class="file-item-info">
                    <div class="file-item-name">${file.name}</div>
                    <div class="file-item-meta">
                        <span>${this.formatFileSize(file.size)}</span>
                        <span>${new Date(file.lastModified).toLocaleDateString()}</span>
                    </div>
                </div>
                <div class="file-item-actions">
                    <button class="file-action-btn" title="Download" data-action="download">💾</button>
                    <button class="file-action-btn" title="Share" data-action="share">📤</button>
                    <button class="file-action-btn" title="Delete" data-action="delete">🗑️</button>
                </div>
            </div>
        `).join('');

        // Add event listeners to file items
        container.querySelectorAll('.file-item').forEach(item => {
            const fileId = parseInt(item.dataset.fileId);
            const file = this.files[fileId];

            item.addEventListener('dblclick', () => {
                this.openFile(file);
            });

            item.querySelectorAll('.file-action-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = btn.dataset.action;
                    this.handleFileAction(file, action);
                });
            });
        });
    }

    getFileIcon(type) {
        if (type.startsWith('image/')) return '🖼️';
        if (type.startsWith('video/')) return '🎥';
        if (type.startsWith('audio/')) return '🎵';
        if (type.includes('pdf')) return '📕';
        if (type.includes('text')) return '📄';
        if (type.includes('zip') || type.includes('rar')) return '📦';
        if (type.includes('javascript') || type.includes('python')) return '💻';
        return '📄';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    handleFileAction(file, action) {
        switch (action) {
            case 'download':
                this.downloadFile(file);
                break;
            case 'share':
                this.shareFile(file);
                break;
            case 'delete':
                this.deleteFile(file);
                break;
        }
    }

    downloadFile(file) {
        const link = document.createElement('a');
        link.href = file.data;
        link.download = file.name;
        link.click();
        window.browser?.showToast(`Downloading: ${file.name}`, 'success');
    }

    shareFile(file) {
        if (window.blueDrop) {
            window.blueDrop.shareFiles([{
                name: file.name,
                type: file.type,
                size: file.size
            }]);
        } else {
            window.browser?.showToast('BlueDrop not available', 'error');
        }
    }

    deleteFile(file) {
        if (confirm(`Delete ${file.name}?`)) {
            // Remove from array
            this.files = this.files.filter(f => f.name !== file.name);

            // Update storage
            const allFiles = JSON.parse(localStorage.getItem('timelord_files') || '[]');
            const updated = allFiles.filter(f => f.name !== file.name);
            localStorage.setItem('timelord_files', JSON.stringify(updated));

            this.renderFiles();
            this.updateStorageQuota();
            window.browser?.showToast(`Deleted: ${file.name}`, 'success');
        }
    }

    openFile(file) {
        // Open file in new tab based on type
        const newTab = window.open();
        newTab.document.write(`
            <html>
                <head><title>${file.name}</title></head>
                <body style="margin:0;padding:20px;font-family:sans-serif;">
                    <h2>${file.name}</h2>
                    ${file.type.startsWith('image/') ?
                        `<img src="${file.data}" style="max-width:100%;">` :
                        `<p>File preview not available for this type.</p>`
                    }
                </body>
            </html>
        `);
    }

    createFolder() {
        const name = prompt('Enter folder name:');
        if (name) {
            // Create folder entry
            const folder = {
                name: name,
                type: 'folder',
                size: 0,
                lastModified: Date.now(),
                path: this.currentPath,
                provider: this.currentProvider,
                data: null
            };

            this.files.push(folder);
            this.renderFiles();
            window.browser?.showToast(`Created folder: ${name}`, 'success');
        }
    }

    refreshFiles() {
        this.loadFiles();
        window.browser?.showToast('Files refreshed', 'info');
    }

    async updateStorageQuota() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            this.storageQuota.usage = estimate.usage || 0;
            this.storageQuota.quota = estimate.quota || 0;

            const percent = (this.storageQuota.usage / this.storageQuota.quota) * 100;

            document.getElementById('storageUsed').style.width = percent + '%';
            document.getElementById('storageText').textContent =
                `${this.formatFileSize(this.storageQuota.usage)} / ${this.formatFileSize(this.storageQuota.quota)} used`;
        }
    }
}

// Initialize File Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait for browser to be initialized
    setTimeout(() => {
        window.fileManager = new FileManager();
    }, 500);
});
