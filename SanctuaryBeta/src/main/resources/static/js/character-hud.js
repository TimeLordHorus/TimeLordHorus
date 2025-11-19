/**
 * Sanctuary Character HUD Controller
 * Manages character profile, stats, inventory, skills, spells, and credentials
 */

class CharacterHUD {
    constructor() {
        this.characterData = null;
        this.currentTab = 'stats';
        this.init();
    }

    /**
     * Initialize the HUD
     */
    async init() {
        console.log('[CharacterHUD] Initializing...');

        // Setup event listeners
        this.setupEventListeners();

        // Load character data
        await this.loadCharacterData();

        // Render HUD
        this.render();

        console.log('[CharacterHUD] Ready!');
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Quick actions
        document.getElementById('btn-meditate')?.addEventListener('click', () => this.startMeditation());
        document.getElementById('btn-create')?.addEventListener('click', () => this.openCreationModal());
        document.getElementById('btn-explore')?.addEventListener('click', () => this.openBiomeSelector());
        document.getElementById('btn-archive')?.addEventListener('click', () => this.openArchive());

        // Credential modal
        document.getElementById('btn-add-credential')?.addEventListener('click', () => this.openCredentialModal());
        document.getElementById('btn-cancel-credential')?.addEventListener('click', () => this.closeCredentialModal());
        document.getElementById('btn-submit-credential')?.addEventListener('click', () => this.submitCredential());

        // VR toggle
        document.getElementById('btn-toggle-vr')?.addEventListener('click', () => {
            window.location.href = '/index.html';
        });
    }

    /**
     * Load character data from API
     */
    async loadCharacterData() {
        try {
            // For demo, use mock data
            // In production, fetch from API: await apiClient.request('/character/profile')
            this.characterData = this.getMockCharacterData();

            console.log('[CharacterHUD] Character data loaded:', this.characterData);
        } catch (error) {
            console.error('[CharacterHUD] Failed to load character data:', error);
            this.characterData = this.getMockCharacterData();
        }
    }

    /**
     * Get mock character data for demo
     */
    getMockCharacterData() {
        return {
            profile: {
                characterName: 'Seeker of Truth',
                level: 5,
                experience: 350,
                experienceToNextLevel: 500,
                enlightenment: 42,
                wisdom: 38,
                creativity: 55,
                harmony: 30,
                knowledge: 45,
                essencePoints: 125,
                creationTokens: 3,
                meditationMinutes: 180,
                biomesVisited: 2,
                creationsMade: 7,
                textsRead: 12
            },
            inventory: [
                {
                    id: 1,
                    name: 'Crystal Tree',
                    type: 'CREATION',
                    rarity: 'RARE',
                    quantity: 1,
                    iconUrl: '🌳'
                },
                {
                    id: 2,
                    name: 'Walden Scroll',
                    type: 'BOOK',
                    rarity: 'UNCOMMON',
                    quantity: 1,
                    iconUrl: '📜'
                },
                {
                    id: 3,
                    name: 'Essence Crystal',
                    type: 'MATERIAL',
                    rarity: 'EPIC',
                    quantity: 5,
                    iconUrl: '💎'
                },
                {
                    id: 4,
                    name: 'Meditation Bell',
                    type: 'TOOL',
                    rarity: 'COMMON',
                    quantity: 1,
                    iconUrl: '🔔'
                }
            ],
            skills: [
                {
                    type: 'SCULPTURE',
                    name: '3D Modeling',
                    level: 12,
                    experience: 850,
                    experienceToNextLevel: 1000,
                    isActive: true
                },
                {
                    type: 'MEDITATION',
                    name: 'Mindfulness',
                    level: 8,
                    experience: 450,
                    experienceToNextLevel: 600,
                    isActive: true
                },
                {
                    type: 'PHILOSOPHY',
                    name: 'Philosophical Understanding',
                    level: 6,
                    experience: 300,
                    experienceToNextLevel: 400,
                    isActive: true
                },
                {
                    type: 'ENLIGHTENMENT',
                    name: 'Spiritual Wisdom',
                    level: 4,
                    experience: 120,
                    experienceToNextLevel: 200,
                    isActive: false
                }
            ],
            spells: [
                {
                    name: 'Manifest Creation',
                    school: 'CREATION',
                    level: 3,
                    essenceCost: 25,
                    isUnlocked: true,
                    isReady: true,
                    description: 'Summon a created object into existence'
                },
                {
                    name: 'Inner Peace',
                    school: 'HARMONY',
                    level: 2,
                    essenceCost: 15,
                    isUnlocked: true,
                    isReady: true,
                    description: 'Restore balance and clarity to the mind'
                },
                {
                    name: 'Illuminate Truth',
                    school: 'ILLUMINATION',
                    level: 1,
                    essenceCost: 20,
                    isUnlocked: true,
                    isReady: false,
                    description: 'Reveal hidden knowledge and wisdom'
                },
                {
                    name: 'Time Dilation',
                    school: 'TEMPORAL',
                    level: 1,
                    essenceCost: 50,
                    isUnlocked: false,
                    isReady: false,
                    description: 'Bend the flow of time (Locked: Reach Level 10)'
                }
            ],
            knowledge: [
                {
                    title: 'Walden - On Simplicity',
                    category: 'PHILOSOPHY',
                    source: 'BIOME_EDUCATION',
                    completionPercentage: 100,
                    isCompleted: true
                },
                {
                    title: 'Ethics - Part I: Concerning God',
                    category: 'PHILOSOPHY',
                    source: 'ARCHIVE_READING',
                    completionPercentage: 65,
                    isCompleted: false
                },
                {
                    title: 'Glacial Retreat & Climate Change',
                    category: 'SCIENCE',
                    source: 'BIOME_EDUCATION',
                    completionPercentage: 100,
                    isCompleted: true
                }
            ],
            credentials: [
                {
                    title: 'Bachelor of Arts',
                    type: 'UNIVERSITY_DEGREE',
                    issuingOrganization: 'State University',
                    verificationStatus: 'VERIFIED',
                    titleGranted: 'Scholar',
                    experienceBonus: 100
                }
            ]
        };
    }

    /**
     * Render the entire HUD
     */
    render() {
        this.renderProfile();
        this.renderStats();
        this.renderInventory();
        this.renderSkills();
        this.renderSpells();
        this.renderKnowledge();
        this.renderCredentials();
    }

    /**
     * Render profile card
     */
    renderProfile() {
        const profile = this.characterData.profile;

        document.getElementById('character-name').textContent = profile.characterName;
        document.getElementById('character-level').textContent = profile.level;
        document.getElementById('essence-display').textContent = profile.essencePoints;
        document.getElementById('tokens-display').textContent = profile.creationTokens;

        // XP bar
        const xpPercentage = (profile.experience / profile.experienceToNextLevel) * 100;
        document.getElementById('xp-bar').style.width = `${xpPercentage}%`;
        document.getElementById('xp-label').textContent = `${profile.experience} / ${profile.experienceToNextLevel} XP`;
    }

    /**
     * Render stats tab
     */
    renderStats() {
        const profile = this.characterData.profile;

        document.getElementById('stat-enlightenment').textContent = profile.enlightenment;
        document.getElementById('stat-wisdom').textContent = profile.wisdom;
        document.getElementById('stat-creativity').textContent = profile.creativity;
        document.getElementById('stat-harmony').textContent = profile.harmony;
        document.getElementById('stat-knowledge').textContent = profile.knowledge;
        document.getElementById('stat-creations').textContent = profile.creationsMade;
        document.getElementById('meditation-time').textContent = `${profile.meditationMinutes} min`;
        document.getElementById('biomes-visited').textContent = `${profile.biomesVisited} / 3`;
        document.getElementById('texts-read').textContent = profile.textsRead;
    }

    /**
     * Render inventory
     */
    renderInventory() {
        const container = document.getElementById('inventory-container');
        container.innerHTML = '';

        // Add items
        this.characterData.inventory.forEach(item => {
            const slot = document.createElement('div');
            slot.className = `inventory-slot rarity-${item.rarity.toLowerCase()}`;
            slot.innerHTML = `
                <div style="font-size: 2rem; display: flex; align-items: center; justify-content: center; height: 100%;">
                    ${item.iconUrl}
                </div>
                ${item.quantity > 1 ? `<div class="inventory-quantity">${item.quantity}</div>` : ''}
            `;
            slot.title = item.name;
            container.appendChild(slot);
        });

        // Add empty slots
        const emptySlots = 20 - this.characterData.inventory.length;
        for (let i = 0; i < emptySlots; i++) {
            const slot = document.createElement('div');
            slot.className = 'inventory-slot empty';
            container.appendChild(slot);
        }
    }

    /**
     * Render skills
     */
    renderSkills() {
        const container = document.getElementById('skills-container');
        container.innerHTML = '';

        this.characterData.skills.forEach(skill => {
            const node = document.createElement('div');
            node.className = `skill-node ${skill.isActive ? 'active' : 'locked'}`;

            const progressPercentage = (skill.experience / skill.experienceToNextLevel) * 100;

            node.innerHTML = `
                <div class="skill-header">
                    <div class="skill-name">${skill.name}</div>
                    <div class="skill-level">Lv ${skill.level}</div>
                </div>
                <div class="skill-description">
                    ${this.getSkillDescription(skill.type)}
                </div>
                <div class="progress-container" style="margin-top: 8px;">
                    <div class="progress-bar" style="width: ${progressPercentage}%;"></div>
                    <div class="progress-label">${skill.experience} / ${skill.experienceToNextLevel}</div>
                </div>
            `;

            container.appendChild(node);
        });
    }

    /**
     * Get skill description
     */
    getSkillDescription(skillType) {
        const descriptions = {
            SCULPTURE: 'Master the art of 3D modeling and sculpting',
            MEDITATION: 'Deepen your mindfulness and inner focus',
            PHILOSOPHY: 'Expand your philosophical understanding',
            ENLIGHTENMENT: 'Grow your spiritual wisdom and insight'
        };
        return descriptions[skillType] || 'Develop this skill through practice';
    }

    /**
     * Render spells
     */
    renderSpells() {
        const container = document.getElementById('spells-container');
        container.innerHTML = '';

        this.characterData.spells.forEach(spell => {
            const card = document.createElement('div');
            card.className = `spell-card ${spell.isReady ? 'ready' : 'cooldown'}`;

            card.innerHTML = `
                <div class="spell-school">${spell.school}</div>
                <div class="spell-name">${spell.name}</div>
                <div class="spell-description" style="font-size: 0.8rem; color: var(--concrete-light); margin: 8px 0; font-family: var(--font-victorian); font-style: italic;">
                    ${spell.description}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="spell-cost">Cost: ${spell.essenceCost} Essence</div>
                    <button class="industrial-button" style="padding: 6px 12px; font-size: 0.7rem;" ${!spell.isUnlocked || !spell.isReady ? 'disabled' : ''}>
                        ${spell.isUnlocked ? (spell.isReady ? 'Cast' : 'Cooldown') : 'Locked'}
                    </button>
                </div>
            `;

            container.appendChild(card);
        });
    }

    /**
     * Render knowledge library
     */
    renderKnowledge() {
        const container = document.getElementById('knowledge-container');
        container.innerHTML = '';

        this.characterData.knowledge.forEach(entry => {
            const div = document.createElement('div');
            div.className = `knowledge-entry ${entry.isCompleted ? 'completed' : ''}`;

            div.innerHTML = `
                <div class="knowledge-category">${entry.category}</div>
                <div class="knowledge-title">${entry.title}</div>
                <div class="progress-container" style="margin-top: 8px; height: 12px;">
                    <div class="progress-bar" style="width: ${entry.completionPercentage}%;"></div>
                    <div class="progress-label" style="font-size: 0.65rem;">${entry.completionPercentage}%</div>
                </div>
            `;

            container.appendChild(div);
        });
    }

    /**
     * Render credentials
     */
    renderCredentials() {
        const container = document.getElementById('credentials-container');

        if (this.characterData.credentials.length === 0) {
            return; // Keep the empty state message
        }

        container.innerHTML = '';

        this.characterData.credentials.forEach(credential => {
            const showcase = document.createElement('div');
            showcase.className = 'credential-showcase';

            showcase.innerHTML = `
                <div class="credential-badge">🎓</div>
                <div class="credential-title">${credential.title}</div>
                <div class="credential-org">${credential.issuingOrganization}</div>
                ${credential.verificationStatus === 'VERIFIED' ?
                    '<div class="verified-badge">✓ VERIFIED</div>' :
                    '<div style="text-align: center; color: var(--warning-copper); font-size: 0.75rem; margin-top: 8px;">Pending Verification</div>'}
                <div style="text-align: center; margin-top: 16px; font-size: 0.75rem; color: var(--brass-light);">
                    Grants: +${credential.experienceBonus} XP | Title: "${credential.titleGranted}"
                </div>
            `;

            container.appendChild(showcase);
        });
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });

        const activeTab = document.getElementById(`tab-${tabName}`);
        if (activeTab) {
            activeTab.style.display = 'block';
        }

        this.currentTab = tabName;
    }

    /**
     * Start meditation
     */
    startMeditation() {
        alert('Meditation feature coming soon!\n\nTrack your meditation time and gain Enlightenment.');
    }

    /**
     * Open creation modal
     */
    openCreationModal() {
        window.location.href = '/index.html#create';
    }

    /**
     * Open biome selector
     */
    openBiomeSelector() {
        alert('Biome Selection:\n\n1. Thoreau Woods\n2. Spinoza Plains\n3. Muir Glacier\n\nComing soon!');
    }

    /**
     * Open archive
     */
    openArchive() {
        alert('Infinite Archive:\n\nAccess to Archive.org, Project Gutenberg, and more.\n\nComing soon!');
    }

    /**
     * Open credential modal
     */
    openCredentialModal() {
        document.getElementById('credential-modal').style.display = 'block';
    }

    /**
     * Close credential modal
     */
    closeCredentialModal() {
        document.getElementById('credential-modal').style.display = 'none';
    }

    /**
     * Submit credential
     */
    async submitCredential() {
        const title = document.getElementById('cred-title').value;
        const type = document.getElementById('cred-type').value;
        const org = document.getElementById('cred-org').value;
        const file = document.getElementById('cred-file').files[0];

        if (!title || !org) {
            alert('Please fill in all required fields.');
            return;
        }

        if (!file) {
            alert('Please upload a document for verification.');
            return;
        }

        // In production, upload to API
        // For demo, show success message
        alert(`Credential Submitted!\n\nTitle: ${title}\nType: ${type}\nOrganization: ${org}\n\nYour credential has been submitted for verification. You'll receive an update within 24-48 hours.`);

        this.closeCredentialModal();

        // Clear form
        document.getElementById('cred-title').value = '';
        document.getElementById('cred-org').value = '';
        document.getElementById('cred-file').value = '';
    }
}

// Initialize HUD when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.characterHUD = new CharacterHUD();
    });
} else {
    window.characterHUD = new CharacterHUD();
}
