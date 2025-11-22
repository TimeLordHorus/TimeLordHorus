// Split View Manager - Enable split screen browsing
class SplitView {
    constructor() {
        this.isSplit = false;
        this.splitType = null; // 'horizontal' or 'vertical'
        this.panes = [];

        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Toggle split view controls
        document.getElementById('splitViewBtn').addEventListener('click', () => {
            this.toggleSplitControls();
        });

        // Split horizontal
        document.getElementById('splitHorizontalBtn').addEventListener('click', () => {
            this.createSplit('horizontal');
        });

        // Split vertical
        document.getElementById('splitVerticalBtn').addEventListener('click', () => {
            this.createSplit('vertical');
        });

        // Close split
        document.getElementById('closeSplitBtn').addEventListener('click', () => {
            this.closeSplit();
        });
    }

    toggleSplitControls() {
        const controls = document.getElementById('splitViewControls');
        const isVisible = controls.style.display !== 'none';

        if (isVisible) {
            controls.style.display = 'none';
        } else {
            controls.style.display = 'flex';
            window.browser?.showToast('Split view enabled!', 'info');
        }
    }

    createSplit(type) {
        if (this.isSplit) {
            window.browser?.showToast('Already in split view', 'info');
            return;
        }

        this.splitType = type;
        this.isSplit = true;

        const contentArea = document.getElementById('contentArea');

        // Save current content
        const currentContent = contentArea.innerHTML;

        // Create split panes
        const pane1 = document.createElement('div');
        pane1.className = `split-pane ${type === 'horizontal' ? 'left' : 'top'}`;
        pane1.id = 'splitPane1';
        pane1.innerHTML = currentContent;

        const pane2 = document.createElement('div');
        pane2.className = `split-pane ${type === 'horizontal' ? 'right' : 'bottom'}`;
        pane2.id = 'splitPane2';

        // Clear content area and add panes
        contentArea.innerHTML = '';
        contentArea.classList.add(`split-${type}`);
        contentArea.appendChild(pane1);
        contentArea.appendChild(pane2);

        // Create new tab in second pane
        this.createTabInPane('splitPane2');

        // Add resize handle
        this.addResizeHandle(pane1, type);

        window.browser?.showToast(`Split view: ${type}`, 'success');

        this.panes = [pane1, pane2];
    }

    createTabInPane(paneId) {
        // Create a new browser tab in the specified pane
        const pane = document.getElementById(paneId);

        // Clone the welcome screen or create a new browsing area
        const welcomeScreen = document.getElementById('welcomeScreen').cloneNode(true);
        welcomeScreen.classList.add('active');
        welcomeScreen.id = `welcome-${paneId}`;

        // Add click handlers to quick links
        welcomeScreen.querySelectorAll('.quick-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.dataset.url;
                this.navigatePane(paneId, url);
            });
        });

        pane.appendChild(welcomeScreen);
    }

    navigatePane(paneId, url) {
        const pane = document.getElementById(paneId);

        // Clear pane
        pane.innerHTML = '';

        // Create iframe for the URL
        const iframe = document.createElement('iframe');
        iframe.className = 'browser-frame';
        iframe.sandbox = 'allow-same-origin allow-scripts allow-popups allow-forms allow-popups-to-escape-sandbox allow-top-navigation';
        iframe.src = url;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';

        pane.appendChild(iframe);
    }

    addResizeHandle(pane, type) {
        const handle = document.createElement('div');
        handle.className = `split-resize-handle ${type}`;

        pane.appendChild(handle);

        let isResizing = false;
        let startPos = 0;
        let startSize = 0;

        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startPos = type === 'horizontal' ? e.clientX : e.clientY;
            startSize = type === 'horizontal' ? pane.offsetWidth : pane.offsetHeight;

            document.body.style.cursor = type === 'horizontal' ? 'col-resize' : 'row-resize';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const currentPos = type === 'horizontal' ? e.clientX : e.clientY;
            const delta = currentPos - startPos;
            const newSize = startSize + delta;

            const contentArea = document.getElementById('contentArea');
            const totalSize = type === 'horizontal' ?
                contentArea.offsetWidth : contentArea.offsetHeight;

            // Limit resize to 20%-80%
            const minSize = totalSize * 0.2;
            const maxSize = totalSize * 0.8;

            if (newSize >= minSize && newSize <= maxSize) {
                const percentage = (newSize / totalSize) * 100;
                pane.style.flex = `0 0 ${percentage}%`;

                // Update second pane
                const pane2 = document.getElementById('splitPane2');
                pane2.style.flex = `0 0 ${100 - percentage}%`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
            }
        });

        // Show handle on hover
        pane.addEventListener('mouseenter', () => {
            handle.style.opacity = '0.3';
        });

        pane.addEventListener('mouseleave', () => {
            if (!isResizing) {
                handle.style.opacity = '0';
            }
        });
    }

    closeSplit() {
        if (!this.isSplit) {
            window.browser?.showToast('Not in split view', 'info');
            return;
        }

        const contentArea = document.getElementById('contentArea');

        // Get content from first pane
        const pane1 = document.getElementById('splitPane1');
        const content = pane1.innerHTML;

        // Remove split classes
        contentArea.classList.remove('split-horizontal', 'split-vertical');

        // Restore content
        contentArea.innerHTML = content;

        this.isSplit = false;
        this.splitType = null;
        this.panes = [];

        // Hide controls
        document.getElementById('splitViewControls').style.display = 'none';

        window.browser?.showToast('Split view closed', 'success');
    }

    switchPaneFocus(paneIndex) {
        if (!this.isSplit || !this.panes[paneIndex]) return;

        // Highlight active pane
        this.panes.forEach((pane, index) => {
            if (index === paneIndex) {
                pane.style.borderColor = 'var(--accent-color)';
                pane.style.borderWidth = '2px';
            } else {
                pane.style.borderColor = 'var(--border-color)';
                pane.style.borderWidth = '1px';
            }
        });
    }

    // Drag and drop tabs between panes (advanced feature)
    enableTabDragDrop() {
        // This would allow dragging tabs from one pane to another
        // Implementation would involve adding drag event listeners to tabs
        // and drop zones in panes
        console.log('Tab drag-drop feature coming soon');
    }

    // Synchronize scrolling between panes (optional feature)
    syncScroll(enable) {
        if (!this.isSplit) return;

        if (enable) {
            // Add scroll event listeners to sync scrolling
            this.panes.forEach((pane, index) => {
                const iframe = pane.querySelector('iframe');
                if (iframe) {
                    iframe.addEventListener('scroll', () => {
                        const otherPane = this.panes[1 - index];
                        const otherIframe = otherPane.querySelector('iframe');
                        if (otherIframe) {
                            otherIframe.scrollTop = iframe.scrollTop;
                        }
                    });
                }
            });
            window.browser?.showToast('Scroll sync enabled', 'success');
        }
    }

    // Save split layout
    saveLayout() {
        if (!this.isSplit) return;

        const layout = {
            type: this.splitType,
            panes: this.panes.map(pane => ({
                id: pane.id,
                flex: pane.style.flex
            }))
        };

        localStorage.setItem('timelord_split_layout', JSON.stringify(layout));
        window.browser?.showToast('Layout saved', 'success');
    }

    // Restore split layout
    restoreLayout() {
        const saved = localStorage.getItem('timelord_split_layout');
        if (saved) {
            const layout = JSON.parse(saved);
            this.createSplit(layout.type);

            // Restore pane sizes
            setTimeout(() => {
                layout.panes.forEach(paneData => {
                    const pane = document.getElementById(paneData.id);
                    if (pane && paneData.flex) {
                        pane.style.flex = paneData.flex;
                    }
                });
            }, 100);

            window.browser?.showToast('Layout restored', 'success');
        }
    }
}

// Initialize Split View when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.splitView = new SplitView();

    // Add keyboard shortcut for split view
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Shift + S: Toggle split view controls
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            window.splitView.toggleSplitControls();
        }

        // Ctrl/Cmd + Shift + H: Horizontal split
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'H') {
            e.preventDefault();
            window.splitView.createSplit('horizontal');
        }

        // Ctrl/Cmd + Shift + V: Vertical split
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            window.splitView.createSplit('vertical');
        }
    });
});
