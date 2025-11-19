/**
 * Biome Controller - Handles Protected Biome scenes
 * Educational zones: Thoreau Woods, Spinoza Plains, Muir Glacier
 */

class BiomeController {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.currentBiome = null;
        this.biomeData = CONFIG.BIOMES;

        this.setupUI();
    }

    /**
     * Setup biome UI
     */
    setupUI() {
        const btnBiomes = document.getElementById('btn-biomes');
        if (btnBiomes) {
            btnBiomes.addEventListener('click', () => this.showBiomeMenu());
        }
    }

    /**
     * Show biome selection menu
     */
    showBiomeMenu() {
        alert('Biome Selection:\n\n1. Thoreau Woods\n2. Spinoza Plains\n3. Muir Glacier\n\nComing soon!');
    }

    /**
     * Load a biome scene
     */
    async loadBiome(biomeName) {
        console.log(`Loading biome: ${biomeName}`);

        const biome = this.biomeData[biomeName.toUpperCase().replace(/ /g, '_')];
        if (!biome) {
            console.error(`Biome not found: ${biomeName}`);
            return;
        }

        // Clear current scene (except lights and camera)
        this.clearScene();

        // Set spawn point
        this.camera.position.set(
            biome.spawnPoint.x,
            biome.spawnPoint.y + 1.6,
            biome.spawnPoint.z
        );

        // Load biome-specific environment
        switch (biomeName) {
            case 'THOREAU_WOODS':
                await this.createThoreauWoods();
                break;
            case 'SPINOZA_PLAINS':
                await this.createSpinozaPlains();
                break;
            case 'MUIR_GLACIER':
                await this.createMuirGlacier();
                break;
        }

        this.currentBiome = biomeName;
        console.log(`✅ Biome loaded: ${biomeName}`);
    }

    /**
     * Create Thoreau Woods environment
     */
    async createThoreauWoods() {
        // Forest ground
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x2d5016,
            roughness: 0.9
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        // Simple trees (placeholders)
        for (let i = 0; i < 50; i++) {
            const x = (Math.random() - 0.5) * 80;
            const z = (Math.random() - 0.5) * 80;

            if (Math.sqrt(x * x + z * z) > 5) { // Keep spawn area clear
                this.createSimpleTree(x, z);
            }
        }

        // Fog
        this.scene.fog = new THREE.FogExp2(0x1a3a1a, 0.05);

        console.log('🌲 Thoreau Woods created');
    }

    /**
     * Create Spinoza Plains environment
     */
    async createSpinozaPlains() {
        // Crystalline ground
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a5f8f,
            roughness: 0.2,
            metalness: 0.8
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        // Geometric structures
        for (let i = 0; i < 20; i++) {
            const x = (Math.random() - 0.5) * 60;
            const z = (Math.random() - 0.5) * 60;
            this.createFractalStructure(x, z);
        }

        this.scene.fog = new THREE.FogExp2(0x87CEEB, 0.02);

        console.log('🔷 Spinoza Plains created');
    }

    /**
     * Create Muir Glacier environment
     */
    async createMuirGlacier() {
        // Ice ground
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshStandardMaterial({
            color: 0xe0ffff,
            roughness: 0.1,
            metalness: 0.3
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);

        // Ice formations
        for (let i = 0; i < 15; i++) {
            const x = (Math.random() - 0.5) * 70;
            const z = (Math.random() - 0.5) * 70;
            this.createIceFormation(x, z);
        }

        this.scene.fog = new THREE.Fog(0xffffff, 1, 50);

        console.log('❄️ Muir Glacier created');
    }

    /**
     * Create simple tree
     */
    createSimpleTree(x, z) {
        // Trunk
        const trunkGeometry = new THREE.CylinderGeometry(0.2, 0.3, 3, 8);
        const trunkMaterial = new THREE.MeshStandardMaterial({ color: 0x4a3520 });
        const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
        trunk.position.set(x, 1.5, z);
        trunk.castShadow = true;
        this.scene.add(trunk);

        // Foliage
        const foliageGeometry = new THREE.ConeGeometry(1.5, 3, 8);
        const foliageMaterial = new THREE.MeshStandardMaterial({ color: 0x2d5016 });
        const foliage = new THREE.Mesh(foliageGeometry, foliageMaterial);
        foliage.position.set(x, 4, z);
        foliage.castShadow = true;
        this.scene.add(foliage);
    }

    /**
     * Create fractal structure
     */
    createFractalStructure(x, z) {
        const size = Math.random() * 2 + 1;
        const geometry = new THREE.OctahedronGeometry(size);
        const material = new THREE.MeshStandardMaterial({
            color: 0x4a5f8f,
            metalness: 0.8,
            roughness: 0.2,
            emissive: 0x4a5f8f,
            emissiveIntensity: 0.2
        });
        const structure = new THREE.Mesh(geometry, material);
        structure.position.set(x, size, z);
        structure.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
        structure.castShadow = true;
        this.scene.add(structure);
    }

    /**
     * Create ice formation
     */
    createIceFormation(x, z) {
        const height = Math.random() * 3 + 2;
        const geometry = new THREE.ConeGeometry(0.5, height, 6);
        const material = new THREE.MeshStandardMaterial({
            color: 0xe0ffff,
            metalness: 0.1,
            roughness: 0.2,
            transparent: true,
            opacity: 0.8
        });
        const ice = new THREE.Mesh(geometry, material);
        ice.position.set(x, height / 2, z);
        ice.castShadow = true;
        this.scene.add(ice);
    }

    /**
     * Clear scene objects (keep lights and camera)
     */
    clearScene() {
        const objectsToRemove = [];

        this.scene.traverse((object) => {
            if (object !== this.scene && object !== this.camera && !object.isLight) {
                objectsToRemove.push(object);
            }
        });

        objectsToRemove.forEach((object) => {
            this.scene.remove(object);
            if (object.geometry) object.geometry.dispose();
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(mat => mat.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
    }

    /**
     * Return to Central Hub
     */
    returnToHub() {
        this.clearScene();
        this.currentBiome = null;
        // Reload Central Hub
        window.location.reload();
    }
}
