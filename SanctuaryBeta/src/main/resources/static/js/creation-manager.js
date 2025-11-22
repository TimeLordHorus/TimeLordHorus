/**
 * Creation Manager - Handles AI-generated 3D model creation and import
 */

class CreationManager {
    constructor(scene, apiClient) {
        this.scene = scene;
        this.apiClient = apiClient;
        this.gltfLoader = new THREE.GLTFLoader();
        this.creations = new Map();

        this.setupUI();
    }

    /**
     * Setup UI event listeners
     */
    setupUI() {
        const btnCreate = document.getElementById('btn-create');
        const btnGenerate = document.getElementById('btn-generate');
        const btnCancel = document.getElementById('btn-cancel');
        const modal = document.getElementById('creation-modal');

        if (btnCreate) {
            btnCreate.addEventListener('click', () => {
                modal.style.display = 'block';
            });
        }

        if (btnGenerate) {
            btnGenerate.addEventListener('click', () => this.handleGenerate());
        }

        if (btnCancel) {
            btnCancel.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
    }

    /**
     * Handle model generation request
     */
    async handleGenerate() {
        const promptInput = document.getElementById('prompt-input');
        const qualitySelect = document.getElementById('quality-select');
        const styleSelect = document.getElementById('style-select');
        const statusDiv = document.getElementById('generation-status');

        const prompt = promptInput.value.trim();
        const quality = qualitySelect.value;
        const style = styleSelect.value;

        if (!prompt) {
            statusDiv.textContent = 'Please enter a description';
            statusDiv.style.color = 'red';
            return;
        }

        statusDiv.textContent = 'Generating...';
        statusDiv.style.color = 'yellow';

        try {
            const response = await this.apiClient.generateModel(prompt, quality, style);

            console.log('Generation response:', response);

            statusDiv.textContent = `Model generated! ID: ${response.generationId}`;
            statusDiv.style.color = 'green';

            // Load and spawn the model
            if (response.modelUrl) {
                await this.loadAndSpawnModel(response.modelUrl, response.generationId);
            }

            // Clear form
            promptInput.value = '';

            // Close modal after delay
            setTimeout(() => {
                document.getElementById('creation-modal').style.display = 'none';
                statusDiv.textContent = '';
            }, 2000);

        } catch (error) {
            console.error('Generation failed:', error);
            statusDiv.textContent = 'Generation failed. Please try again.';
            statusDiv.style.color = 'red';
        }
    }

    /**
     * Load and spawn GLB model in VR scene
     */
    async loadAndSpawnModel(modelUrl, generationId) {
        return new Promise((resolve, reject) => {
            this.gltfLoader.load(
                modelUrl,
                (gltf) => {
                    const model = gltf.scene;

                    // Position in front of user
                    model.position.set(0, 1.5, -2);
                    model.scale.set(1, 1, 1);

                    // Make interactable
                    this.makeInteractable(model);

                    // Add to scene
                    this.scene.add(model);

                    // Store reference
                    this.creations.set(generationId, model);

                    console.log(`✅ Model ${generationId} loaded and spawned`);
                    resolve(model);
                },
                (progress) => {
                    const percent = (progress.loaded / progress.total) * 100;
                    console.log(`Loading model: ${percent.toFixed(2)}%`);
                },
                (error) => {
                    console.error('Model load error:', error);
                    reject(error);
                }
            );
        });
    }

    /**
     * Make model interactable in VR
     */
    makeInteractable(model) {
        model.traverse((child) => {
            if (child.isMesh) {
                // Enable shadows
                child.castShadow = true;
                child.receiveShadow = true;

                // Mark as interactive
                child.userData.interactive = true;
            }
        });

        // Add bounding box for interaction
        const box = new THREE.Box3().setFromObject(model);
        const helper = new THREE.Box3Helper(box, 0x00ffff);
        helper.visible = false; // Hidden by default
        model.add(helper);

        model.userData.boundingBox = box;
        model.userData.canGrab = true;
    }

    /**
     * Delete a creation from scene
     */
    deleteCreation(generationId) {
        const model = this.creations.get(generationId);
        if (model) {
            this.scene.remove(model);
            model.traverse((child) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(mat => mat.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            });

            this.creations.delete(generationId);
            console.log(`Deleted creation: ${generationId}`);
        }
    }

    /**
     * Get all loaded creations
     */
    getCreations() {
        return Array.from(this.creations.values());
    }
}
