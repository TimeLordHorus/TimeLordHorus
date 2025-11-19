/**
 * Medusa Avatar - Jellyfish VR Avatar
 * Physics-based floating with bioluminescent glow
 */

class MedusaAvatar {
    constructor(scene) {
        this.scene = scene;
        this.mesh = null;
        this.tentacles = [];
        this.glowIntensity = CONFIG.AVATAR.GLOW_INTENSITY;
        this.floatSpeed = CONFIG.AVATAR.FLOAT_SPEED;
        this.floatAmplitude = CONFIG.AVATAR.FLOAT_AMPLITUDE;
        this.floatTime = 0;

        this.init();
    }

    /**
     * Initialize the Medusa avatar
     */
    init() {
        // Create bell (main body)
        this.createBell();

        // Create tentacles
        this.createTentacles();

        // Position relative to camera
        this.mesh.position.set(0, -0.5, -1);
    }

    /**
     * Create the jellyfish bell
     */
    createBell() {
        const bellGeometry = new THREE.SphereGeometry(0.3, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);

        // Bioluminescent material
        const bellMaterial = new THREE.MeshStandardMaterial({
            color: CONFIG.AVATAR.GLOW_COLOR,
            emissive: CONFIG.AVATAR.GLOW_COLOR,
            emissiveIntensity: this.glowIntensity,
            transparent: true,
            opacity: 0.7,
            roughness: 0.3,
            metalness: 0.1
        });

        this.mesh = new THREE.Mesh(bellGeometry, bellMaterial);
        this.scene.add(this.mesh);

        console.log('✅ Medusa bell created');
    }

    /**
     * Create jellyfish tentacles
     */
    createTentacles() {
        const tentacleCount = 8;
        const tentacleLength = 0.5;
        const tentacleSegments = 10;

        for (let i = 0; i < tentacleCount; i++) {
            const angle = (i / tentacleCount) * Math.PI * 2;
            const x = Math.cos(angle) * 0.2;
            const z = Math.sin(angle) * 0.2;

            // Create tentacle as chain of segments
            const segments = [];
            for (let j = 0; j < tentacleSegments; j++) {
                const segmentGeometry = new THREE.CylinderGeometry(0.02, 0.01, tentacleLength / tentacleSegments, 8);
                const segmentMaterial = new THREE.MeshStandardMaterial({
                    color: CONFIG.AVATAR.GLOW_COLOR,
                    emissive: CONFIG.AVATAR.GLOW_COLOR,
                    emissiveIntensity: this.glowIntensity * 0.5,
                    transparent: true,
                    opacity: 0.6
                });

                const segment = new THREE.Mesh(segmentGeometry, segmentMaterial);
                segment.position.set(
                    x,
                    -j * (tentacleLength / tentacleSegments),
                    z
                );

                this.mesh.add(segment);
                segments.push(segment);
            }

            this.tentacles.push({
                segments: segments,
                baseX: x,
                baseZ: z,
                velocity: new THREE.Vector3(0, 0, 0),
                phaseOffset: (i / tentacleCount) * Math.PI * 2
            });
        }

        console.log(`✅ Created ${tentacleCount} tentacles with ${tentacleSegments} segments each`);
    }

    /**
     * Update avatar (called every frame)
     */
    update(time) {
        this.floatTime = time;

        // Update floating motion
        this.updateFloatingMotion();

        // Update bioluminescence
        this.updateBioluminescence(time);

        // Update tentacle physics
        this.updateTentaclePhysics(time);
    }

    /**
     * Update floating motion
     */
    updateFloatingMotion() {
        if (!this.mesh) return;

        // Gentle vertical oscillation
        const verticalOffset = Math.sin(this.floatTime * this.floatSpeed) * this.floatAmplitude;
        this.mesh.position.y = -0.5 + verticalOffset * 0.1;

        // Gentle rotation sway
        const rotationOffset = Math.sin(this.floatTime * this.floatSpeed * 0.5) * 0.1;
        this.mesh.rotation.y = rotationOffset;
    }

    /**
     * Update bioluminescent glow
     */
    updateBioluminescence(time) {
        if (!this.mesh) return;

        // Pulsing glow effect
        const pulse = Math.sin(time * 2) * 0.3 + 0.7;
        this.mesh.material.emissiveIntensity = this.glowIntensity * pulse;

        // Update tentacles glow
        this.tentacles.forEach((tentacle, index) => {
            tentacle.segments.forEach((segment, segmentIndex) => {
                const delay = (index + segmentIndex) * 0.1;
                const segmentPulse = Math.sin(time * 2 + delay) * 0.2 + 0.8;
                segment.material.emissiveIntensity = this.glowIntensity * 0.5 * segmentPulse;
            });
        });
    }

    /**
     * Update tentacle physics with simple Verlet integration
     */
    updateTentaclePhysics(time) {
        this.tentacles.forEach((tentacle) => {
            // Simulate wave motion
            const wave = Math.sin(time * 2 + tentacle.phaseOffset) * 0.05;

            tentacle.segments.forEach((segment, index) => {
                if (index > 0) {
                    // Add wave motion
                    segment.position.x = tentacle.baseX + wave * index;
                    segment.position.z = tentacle.baseZ + wave * index * 0.5;

                    // Slight rotation for organic feel
                    segment.rotation.x = wave * 0.5;
                }
            });
        });
    }

    /**
     * Set glow intensity (for audio reactivity)
     */
    setGlowIntensity(intensity) {
        this.glowIntensity = Math.max(0, Math.min(2, intensity));
    }

    /**
     * Set position (attach to camera/controllers)
     */
    setPosition(x, y, z) {
        if (this.mesh) {
            this.mesh.position.set(x, y, z);
        }
    }

    /**
     * Destroy avatar
     */
    destroy() {
        if (this.mesh) {
            this.scene.remove(this.mesh);
            this.mesh.geometry.dispose();
            this.mesh.material.dispose();
        }

        this.tentacles.forEach((tentacle) => {
            tentacle.segments.forEach((segment) => {
                segment.geometry.dispose();
                segment.material.dispose();
            });
        });

        console.log('Medusa avatar destroyed');
    }
}
