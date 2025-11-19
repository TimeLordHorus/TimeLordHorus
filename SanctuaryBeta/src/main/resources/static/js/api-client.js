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
}

// Global API client instance
const apiClient = new SanctuaryAPIClient();
