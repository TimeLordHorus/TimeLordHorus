/**
 * Sanctuary API Client
 * Handles all REST API calls to the Spring Boot backend
 */

class SanctuaryAPIClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.token = localStorage.getItem('sanctuary_token');
    }

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('sanctuary_token', token);
    }

    /**
     * Get authentication headers
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Generic API request method
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Generate 3D model from text prompt
     */
    async generateModel(prompt, quality = 'medium', style = 'realistic') {
        return await this.request('/creations/generate', {
            method: 'POST',
            body: JSON.stringify({ prompt, quality, style })
        });
    }

    /**
     * Get user's creations
     */
    async getMyCreations(page = 0, size = 20) {
        return await this.request(`/creations/my-creations?page=${page}&size=${size}`);
    }

    /**
     * Get public creations
     */
    async getPublicCreations(page = 0, size = 20) {
        return await this.request(`/creations/public?page=${page}&size=${size}`);
    }

    /**
     * Get creation by generation ID
     */
    async getCreation(generationId) {
        return await this.request(`/creations/${generationId}`);
    }

    /**
     * Health check
     */
    async healthCheck() {
        return await this.request('/health');
    }

    /**
     * Get service info
     */
    async getInfo() {
        return await this.request('/info');
    }

    // ===== Character API =====

    /**
     * Get complete character profile
     */
    async getCharacterProfile() {
        return await this.request('/character/profile');
    }

    /**
     * Get character stats
     */
    async getCharacterStats() {
        return await this.request('/character/stats');
    }

    /**
     * Update character name
     */
    async updateCharacterName(name) {
        return await this.request('/character/name', {
            method: 'PUT',
            body: JSON.stringify({ name })
        });
    }

    /**
     * Track meditation session
     */
    async trackMeditation(minutes) {
        return await this.request('/character/meditate', {
            method: 'POST',
            body: JSON.stringify({ minutes })
        });
    }

    /**
     * Award experience to character
     */
    async awardExperience(amount, reason) {
        return await this.request('/character/experience', {
            method: 'POST',
            body: JSON.stringify({ amount, reason })
        });
    }

    /**
     * Track biome visit
     */
    async trackBiomeVisit(biomeName, durationSeconds, nodesVisited) {
        return await this.request('/character/biome-visit', {
            method: 'POST',
            body: JSON.stringify({ biomeName, durationSeconds, nodesVisited })
        });
    }

    /**
     * Complete knowledge entry
     */
    async completeKnowledge(knowledgeId) {
        return await this.request(`/character/knowledge/${knowledgeId}/complete`, {
            method: 'POST'
        });
    }

    // ===== Credential API =====

    /**
     * Submit a credential for verification
     */
    async submitCredential(formData) {
        const url = `${this.baseURL}/credentials/submit`;
        const config = {
            method: 'POST',
            headers: {
                // Don't set Content-Type for FormData - browser will set it with boundary
                'Authorization': this.token ? `Bearer ${this.token}` : undefined
            },
            body: formData
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Upload failed' }));
                throw new Error(error.error || `Upload failed: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Credential submission failed:', error);
            throw error;
        }
    }

    /**
     * Get all user credentials
     */
    async getUserCredentials() {
        return await this.request('/credentials');
    }

    /**
     * Get verified credentials
     */
    async getVerifiedCredentials() {
        return await this.request('/credentials/verified');
    }

    /**
     * Get public credentials
     */
    async getPublicCredentials() {
        return await this.request('/credentials/public');
    }

    /**
     * Update credential visibility
     */
    async updateCredentialVisibility(credentialId, isPublic) {
        return await this.request(`/credentials/${credentialId}/visibility`, {
            method: 'PUT',
            body: JSON.stringify({ isPublic })
        });
    }

    /**
     * Delete credential
     */
    async deleteCredential(credentialId) {
        return await this.request(`/credentials/${credentialId}`, {
            method: 'DELETE'
        });
    }

    // ===== Skills & Spells API =====

    /**
     * Award skill experience
     */
    async awardSkillExperience(skillType, amount) {
        return await this.request(`/skills/${skillType}/award-xp`, {
            method: 'POST',
            body: JSON.stringify({ amount })
        });
    }

    /**
     * Cast a spell
     */
    async castSpell(spellId) {
        return await this.request(`/skills/spells/${spellId}/cast`, {
            method: 'POST'
        });
    }
}

// Global API client instance
const apiClient = new SanctuaryAPIClient();
