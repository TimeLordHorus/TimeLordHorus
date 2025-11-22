// Encryption Manager - End-to-End Data Encryption for Privacy
// Protects user data from host browser collection using AES-GCM encryption

class EncryptionManager {
    constructor() {
        this.encryptionEnabled = false;
        this.masterKey = null;
        this.salt = null;
        this.iv = null;
        this.privacyMode = false;

        // Encryption algorithm configuration
        this.algorithm = 'AES-GCM';
        this.keyLength = 256;
        this.iterations = 100000; // PBKDF2 iterations

        this.init();
    }

    async init() {
        await this.loadEncryptionSettings();
        this.setupEventListeners();

        // Check if encryption was previously enabled
        if (this.encryptionEnabled && !this.masterKey) {
            this.promptForPassword();
        }
    }

    setupEventListeners() {
        // Enable encryption button
        const enableBtn = document.getElementById('enableEncryptionBtn');
        if (enableBtn) {
            enableBtn.addEventListener('click', () => this.enableEncryption());
        }

        // Disable encryption button
        const disableBtn = document.getElementById('disableEncryptionBtn');
        if (disableBtn) {
            disableBtn.addEventListener('click', () => this.disableEncryption());
        }

        // Change password button
        const changePassBtn = document.getElementById('changePasswordBtn');
        if (changePassBtn) {
            changePassBtn.addEventListener('click', () => this.changePassword());
        }

        // Privacy mode toggle
        const privacyToggle = document.getElementById('privacyModeToggle');
        if (privacyToggle) {
            privacyToggle.addEventListener('change', (e) => this.togglePrivacyMode(e.target.checked));
        }
    }

    // Generate encryption key from password using PBKDF2
    async deriveKey(password, salt) {
        const encoder = new TextEncoder();
        const passwordBuffer = encoder.encode(password);

        // Import password as key material
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            passwordBuffer,
            { name: 'PBKDF2' },
            false,
            ['deriveBits', 'deriveKey']
        );

        // Derive AES-GCM key
        const key = await crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: this.iterations,
                hash: 'SHA-256'
            },
            keyMaterial,
            { name: this.algorithm, length: this.keyLength },
            true,
            ['encrypt', 'decrypt']
        );

        return key;
    }

    // Generate random salt
    generateSalt() {
        return crypto.getRandomValues(new Uint8Array(16));
    }

    // Generate random IV (Initialization Vector)
    generateIV() {
        return crypto.getRandomValues(new Uint8Array(12));
    }

    // Encrypt data
    async encrypt(data) {
        if (!this.encryptionEnabled || !this.masterKey) {
            return data; // Return unencrypted if encryption is disabled
        }

        try {
            const encoder = new TextEncoder();
            const dataBuffer = encoder.encode(JSON.stringify(data));

            // Generate new IV for each encryption
            const iv = this.generateIV();

            // Encrypt the data
            const encryptedBuffer = await crypto.subtle.encrypt(
                {
                    name: this.algorithm,
                    iv: iv
                },
                this.masterKey,
                dataBuffer
            );

            // Combine IV and encrypted data
            const encryptedArray = new Uint8Array(encryptedBuffer);
            const combined = new Uint8Array(iv.length + encryptedArray.length);
            combined.set(iv, 0);
            combined.set(encryptedArray, iv.length);

            // Convert to base64 for storage
            return {
                encrypted: true,
                data: this.arrayBufferToBase64(combined)
            };
        } catch (error) {
            console.error('Encryption error:', error);
            throw new Error('Failed to encrypt data');
        }
    }

    // Decrypt data
    async decrypt(encryptedData) {
        if (!encryptedData || !encryptedData.encrypted) {
            return encryptedData; // Return as-is if not encrypted
        }

        if (!this.masterKey) {
            throw new Error('Encryption key not available. Please enter password.');
        }

        try {
            // Convert from base64
            const combined = this.base64ToArrayBuffer(encryptedData.data);

            // Extract IV and encrypted data
            const iv = combined.slice(0, 12);
            const encryptedBuffer = combined.slice(12);

            // Decrypt the data
            const decryptedBuffer = await crypto.subtle.decrypt(
                {
                    name: this.algorithm,
                    iv: iv
                },
                this.masterKey,
                encryptedBuffer
            );

            // Convert back to original data
            const decoder = new TextDecoder();
            const decryptedString = decoder.decode(decryptedBuffer);
            return JSON.parse(decryptedString);
        } catch (error) {
            console.error('Decryption error:', error);
            throw new Error('Failed to decrypt data. Password may be incorrect.');
        }
    }

    // Enable encryption with password
    async enableEncryption() {
        const password = prompt('Enter a master password for encryption:\n\n⚠️ IMPORTANT: Remember this password! If you forget it, your data cannot be recovered.');

        if (!password || password.length < 8) {
            window.browser?.showToast('Password must be at least 8 characters', 'error');
            return;
        }

        const confirmPassword = prompt('Confirm your master password:');

        if (password !== confirmPassword) {
            window.browser?.showToast('Passwords do not match', 'error');
            return;
        }

        try {
            // Generate salt
            this.salt = this.generateSalt();

            // Derive encryption key from password
            this.masterKey = await this.deriveKey(password, this.salt);

            // Enable encryption
            this.encryptionEnabled = true;

            // Save settings (salt only, never save password or key)
            await this.saveEncryptionSettings();

            // Re-encrypt all existing data
            await this.reEncryptAllData();

            window.browser?.showToast('Encryption enabled successfully', 'success');
            this.updateUI();
        } catch (error) {
            console.error('Enable encryption error:', error);
            window.browser?.showToast('Failed to enable encryption', 'error');
        }
    }

    // Disable encryption (decrypt all data)
    async disableEncryption() {
        if (!this.encryptionEnabled) {
            window.browser?.showToast('Encryption is not enabled', 'info');
            return;
        }

        const confirm = window.confirm(
            'Are you sure you want to disable encryption?\n\n' +
            'This will decrypt all your data and store it unencrypted.\n' +
            'This cannot be undone.'
        );

        if (!confirm) return;

        try {
            // Decrypt all data before disabling
            await this.decryptAllData();

            // Clear encryption settings
            this.masterKey = null;
            this.salt = null;
            this.encryptionEnabled = false;

            await this.saveEncryptionSettings();

            window.browser?.showToast('Encryption disabled', 'success');
            this.updateUI();
        } catch (error) {
            console.error('Disable encryption error:', error);
            window.browser?.showToast('Failed to disable encryption', 'error');
        }
    }

    // Change encryption password
    async changePassword() {
        if (!this.encryptionEnabled) {
            window.browser?.showToast('Encryption is not enabled', 'info');
            return;
        }

        const currentPassword = prompt('Enter current password:');
        if (!currentPassword) return;

        try {
            // Verify current password
            const testKey = await this.deriveKey(currentPassword, this.salt);
            const testData = await this.encrypt({ test: 'data' });

            // Try to decrypt with current key
            this.masterKey = testKey;
            await this.decrypt(testData);

            // Current password is correct, get new password
            const newPassword = prompt('Enter new password (min 8 characters):');
            if (!newPassword || newPassword.length < 8) {
                window.browser?.showToast('New password must be at least 8 characters', 'error');
                return;
            }

            const confirmPassword = prompt('Confirm new password:');
            if (newPassword !== confirmPassword) {
                window.browser?.showToast('Passwords do not match', 'error');
                return;
            }

            // Generate new salt and key
            this.salt = this.generateSalt();
            this.masterKey = await this.deriveKey(newPassword, this.salt);

            // Re-encrypt all data with new key
            await this.reEncryptAllData();

            await this.saveEncryptionSettings();

            window.browser?.showToast('Password changed successfully', 'success');
        } catch (error) {
            console.error('Change password error:', error);
            window.browser?.showToast('Incorrect password or change failed', 'error');
        }
    }

    // Prompt for password on startup if encryption was enabled
    async promptForPassword() {
        const password = prompt('Enter your master password to unlock encrypted data:');

        if (!password) {
            window.browser?.showToast('Password required to access encrypted data', 'warning');
            return false;
        }

        try {
            // Derive key from password and stored salt
            this.masterKey = await this.deriveKey(password, this.salt);

            // Verify password by attempting to decrypt test data
            const testData = localStorage.getItem('timelord_encryption_test');
            if (testData) {
                await this.decrypt(JSON.parse(testData));
            }

            window.browser?.showToast('Encryption unlocked', 'success');
            this.updateUI();
            return true;
        } catch (error) {
            console.error('Password verification error:', error);
            window.browser?.showToast('Incorrect password', 'error');
            this.masterKey = null;
            return false;
        }
    }

    // Toggle privacy mode (encrypts everything automatically)
    togglePrivacyMode(enabled) {
        this.privacyMode = enabled;
        localStorage.setItem('timelord_privacy_mode', enabled.toString());

        if (enabled && !this.encryptionEnabled) {
            this.enableEncryption();
        }

        const status = enabled ? 'enabled' : 'disabled';
        window.browser?.showToast(`Privacy mode ${status}`, 'success');
        this.updateUI();
    }

    // Re-encrypt all existing data with new key
    async reEncryptAllData() {
        // Encrypt bookmarks
        const bookmarks = window.browser?.getBookmarks() || [];
        if (bookmarks.length > 0) {
            const encrypted = await this.encrypt(bookmarks);
            localStorage.setItem('timelord_bookmarks_encrypted', JSON.stringify(encrypted));
        }

        // Encrypt history
        const history = window.browser?.getHistory() || [];
        if (history.length > 0) {
            const encrypted = await this.encrypt(history);
            localStorage.setItem('timelord_history_encrypted', JSON.stringify(encrypted));
        }

        // Encrypt settings
        const settings = {
            theme: localStorage.getItem('timelord_theme'),
            searchEngine: localStorage.getItem('timelord_search_engine')
        };
        const encryptedSettings = await this.encrypt(settings);
        localStorage.setItem('timelord_settings_encrypted', JSON.stringify(encryptedSettings));

        // Store test data for password verification
        const testData = await this.encrypt({ verified: true, timestamp: Date.now() });
        localStorage.setItem('timelord_encryption_test', JSON.stringify(testData));
    }

    // Decrypt all data when disabling encryption
    async decryptAllData() {
        // Decrypt bookmarks
        const encBookmarks = localStorage.getItem('timelord_bookmarks_encrypted');
        if (encBookmarks) {
            const decrypted = await this.decrypt(JSON.parse(encBookmarks));
            localStorage.setItem('timelord_bookmarks', JSON.stringify(decrypted));
            localStorage.removeItem('timelord_bookmarks_encrypted');
        }

        // Decrypt history
        const encHistory = localStorage.getItem('timelord_history_encrypted');
        if (encHistory) {
            const decrypted = await this.decrypt(JSON.parse(encHistory));
            localStorage.setItem('timelord_history', JSON.stringify(decrypted));
            localStorage.removeItem('timelord_history_encrypted');
        }

        // Decrypt settings
        const encSettings = localStorage.getItem('timelord_settings_encrypted');
        if (encSettings) {
            const decrypted = await this.decrypt(JSON.parse(encSettings));
            localStorage.setItem('timelord_theme', decrypted.theme || 'light');
            localStorage.setItem('timelord_search_engine', decrypted.searchEngine || 'duckduckgo');
            localStorage.removeItem('timelord_settings_encrypted');
        }

        localStorage.removeItem('timelord_encryption_test');
    }

    // Helper: Convert ArrayBuffer to Base64
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    // Helper: Convert Base64 to ArrayBuffer
    base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }

    // Save encryption settings (salt only)
    async saveEncryptionSettings() {
        const settings = {
            enabled: this.encryptionEnabled,
            salt: this.salt ? this.arrayBufferToBase64(this.salt) : null,
            algorithm: this.algorithm,
            keyLength: this.keyLength,
            iterations: this.iterations
        };

        // Store in unencrypted localStorage (salt is not sensitive)
        localStorage.setItem('timelord_encryption_config', JSON.stringify(settings));
    }

    // Load encryption settings
    async loadEncryptionSettings() {
        const stored = localStorage.getItem('timelord_encryption_config');
        if (stored) {
            const settings = JSON.parse(stored);
            this.encryptionEnabled = settings.enabled || false;
            this.salt = settings.salt ? this.base64ToArrayBuffer(settings.salt) : null;
            this.algorithm = settings.algorithm || 'AES-GCM';
            this.keyLength = settings.keyLength || 256;
            this.iterations = settings.iterations || 100000;
        }

        const privacyMode = localStorage.getItem('timelord_privacy_mode');
        this.privacyMode = privacyMode === 'true';
    }

    // Update UI to reflect encryption status
    updateUI() {
        const statusBadge = document.getElementById('encryptionStatus');
        const privacyToggle = document.getElementById('privacyModeToggle');

        if (statusBadge) {
            if (this.encryptionEnabled && this.masterKey) {
                statusBadge.textContent = 'Enabled & Unlocked';
                statusBadge.className = 'status-badge status-active';
            } else if (this.encryptionEnabled && !this.masterKey) {
                statusBadge.textContent = 'Enabled & Locked';
                statusBadge.className = 'status-badge status-warning';
            } else {
                statusBadge.textContent = 'Disabled';
                statusBadge.className = 'status-badge status-inactive';
            }
        }

        if (privacyToggle) {
            privacyToggle.checked = this.privacyMode;
        }

        // Update button states
        const enableBtn = document.getElementById('enableEncryptionBtn');
        const disableBtn = document.getElementById('disableEncryptionBtn');
        const changePassBtn = document.getElementById('changePasswordBtn');

        if (enableBtn) enableBtn.style.display = this.encryptionEnabled ? 'none' : 'block';
        if (disableBtn) disableBtn.style.display = this.encryptionEnabled ? 'block' : 'none';
        if (changePassBtn) changePassBtn.style.display = this.encryptionEnabled ? 'block' : 'none';
    }

    // Public API for other modules to use
    async encryptData(data) {
        return await this.encrypt(data);
    }

    async decryptData(encryptedData) {
        return await this.decrypt(encryptedData);
    }

    isEncryptionEnabled() {
        return this.encryptionEnabled && this.masterKey !== null;
    }

    isPrivacyModeEnabled() {
        return this.privacyMode;
    }
}

// Initialize encryption manager
document.addEventListener('DOMContentLoaded', () => {
    window.encryptionManager = new EncryptionManager();
    console.log('Encryption Manager initialized');
});
