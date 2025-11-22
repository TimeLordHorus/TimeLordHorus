/**
 * Sanctuary VR - Main Application Entry Point
 * Initializes Three.js scene, WebXR, and VR experience
 */

let scene, camera, renderer, vrButton;
let medusaAvatar;
let controllers = [];
let loadingScreen;

// Initialize the application
async function init() {
    console.log('🌟 Initializing Sanctuary VR...');

    loadingScreen = document.getElementById('loading-screen');
    updateLoadingStatus('Creating scene...');

    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(CONFIG.SCENE.FOG_COLOR);
    scene.fog = new THREE.FogExp2(CONFIG.SCENE.FOG_COLOR, CONFIG.SCENE.FOG_DENSITY);

    // Create camera
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(
        CONFIG.SPAWN_POINT.x,
        CONFIG.SPAWN_POINT.y,
        CONFIG.SPAWN_POINT.z
    );

    // Create renderer
    renderer = new THREE.WebGLRenderer({
        antialias: CONFIG.PERFORMANCE.ANTIALIAS,
        powerPreference: 'high-performance'
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.xr.enabled = true;
    renderer.shadowMap.enabled = CONFIG.PERFORMANCE.ENABLE_SHADOWS;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    document.getElementById('vr-container').appendChild(renderer.domElement);

    updateLoadingStatus('Setting up lighting...');

    // Add lights
    setupLighting();

    updateLoadingStatus('Creating Central Hub...');

    // Create Central Hub environment
    await createCentralHub();

    updateLoadingStatus('Initializing Medusa avatar...');

    // Create Medusa avatar (jellyfish)
    medusaAvatar = new MedusaAvatar(scene);

    updateLoadingStatus('Setting up VR controllers...');

    // Setup VR controllers
    setupVRControllers();

    // Add VR button
    vrButton = THREE.VRButton.createButton(renderer);
    document.body.appendChild(vrButton);

    updateLoadingStatus('Checking API connection...');

    // Test API connection
    try {
        const health = await apiClient.healthCheck();
        console.log('✅ API Health:', health);
    } catch (error) {
        console.warn('⚠️ API connection failed (offline mode):', error);
    }

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Hide loading screen
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        document.getElementById('ui-overlay').style.display = 'block';
    }, 1000);

    updateLoadingStatus('Sanctuary is ready! 🎉');

    // Start render loop
    renderer.setAnimationLoop(animate);

    console.log('✅ Sanctuary VR initialized successfully!');
}

/**
 * Setup scene lighting
 */
function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, CONFIG.SCENE.AMBIENT_LIGHT_INTENSITY);
    scene.add(ambientLight);

    // Directional light (sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, CONFIG.SCENE.DIRECTIONAL_LIGHT_INTENSITY);
    directionalLight.position.set(5, 10, 7.5);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    // Point light (mystical glow)
    const pointLight = new THREE.PointLight(0x00ffff, 1, 50);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);
}

/**
 * Create Central Hub environment
 */
async function createCentralHub() {
    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a2e,
        roughness: 0.8,
        metalness: 0.2
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Central energy beam (The Core)
    createCentralCore();

    // Portal gallery (placeholders)
    createPortalGallery();

    // Floating platforms
    createFloatingPlatforms();
}

/**
 * Create the central energy beam
 */
function createCentralCore() {
    const coreGeometry = new THREE.CylinderGeometry(0.5, 0.5, 10, 32);
    const coreMaterial = new THREE.MeshStandardMaterial({
        color: 0x00ffff,
        emissive: 0x00ffff,
        emissiveIntensity: 2,
        transparent: true,
        opacity: 0.6
    });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    core.position.set(0, 5, 0);
    scene.add(core);

    // Pulsing animation
    core.userData.update = (time) => {
        core.material.emissiveIntensity = 2 + Math.sin(time * 2) * 0.5;
        core.rotation.y += 0.01;
    };
}

/**
 * Create portal gallery
 */
function createPortalGallery() {
    const portals = [
        { name: 'Thoreau Woods', position: [-10, 0, -10], color: 0x228B22 },
        { name: 'Spinoza Plains', position: [10, 0, -10], color: 0x87CEEB },
        { name: 'Muir Glacier', position: [0, 0, -15], color: 0xE0FFFF }
    ];

    portals.forEach(portalData => {
        const portalGeometry = new THREE.RingGeometry(1, 1.5, 32);
        const portalMaterial = new THREE.MeshBasicMaterial({
            color: portalData.color,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.7
        });
        const portal = new THREE.Mesh(portalGeometry, portalMaterial);
        portal.position.set(...portalData.position, 2);
        portal.userData.biome = portalData.name;
        scene.add(portal);

        // Portal animation
        portal.userData.update = (time) => {
            portal.rotation.z += 0.01;
            portal.material.opacity = 0.7 + Math.sin(time * 3) * 0.2;
        };
    });
}

/**
 * Create floating platforms
 */
function createFloatingPlatforms() {
    const platformGeometry = new THREE.BoxGeometry(3, 0.2, 3);
    const platformMaterial = new THREE.MeshStandardMaterial({
        color: 0x16213e,
        metalness: 0.5,
        roughness: 0.5
    });

    const positions = [
        [-5, 1, 0],
        [5, 1, 0],
        [0, 1, -8]
    ];

    positions.forEach((pos, i) => {
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.set(...pos);
        platform.castShadow = true;
        platform.receiveShadow = true;
        scene.add(platform);

        // Floating animation
        platform.userData.initialY = pos[1];
        platform.userData.floatOffset = i * Math.PI / 3;
        platform.userData.update = (time) => {
            platform.position.y = platform.userData.initialY + Math.sin(time + platform.userData.floatOffset) * 0.2;
        };
    });
}

/**
 * Setup VR controllers
 */
function setupVRControllers() {
    const controllerModelFactory = new THREE.XRControllerModelFactory();

    // Controller 1
    const controller1 = renderer.xr.getController(0);
    controller1.addEventListener('selectstart', onSelectStart);
    controller1.addEventListener('selectend', onSelectEnd);
    scene.add(controller1);

    const controllerGrip1 = renderer.xr.getControllerGrip(0);
    scene.add(controllerGrip1);

    controllers.push({ controller: controller1, grip: controllerGrip1 });

    // Controller 2
    const controller2 = renderer.xr.getController(1);
    controller2.addEventListener('selectstart', onSelectStart);
    controller2.addEventListener('selectend', onSelectEnd);
    scene.add(controller2);

    const controllerGrip2 = renderer.xr.getControllerGrip(1);
    scene.add(controllerGrip2);

    controllers.push({ controller: controller2, grip: controllerGrip2 });
}

/**
 * Controller select start handler
 */
function onSelectStart(event) {
    console.log('Controller select start');
    // TODO: Implement object interaction
}

/**
 * Controller select end handler
 */
function onSelectEnd(event) {
    console.log('Controller select end');
}

/**
 * Handle window resize
 */
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

/**
 * Update loading status text
 */
function updateLoadingStatus(message) {
    const statusElement = document.getElementById('loading-status');
    if (statusElement) {
        statusElement.textContent = message;
    }
    console.log('[Loading]', message);
}

/**
 * Main animation loop
 */
function animate() {
    const time = performance.now() / 1000;

    // Update Medusa avatar
    if (medusaAvatar) {
        medusaAvatar.update(time);
    }

    // Update scene objects with update functions
    scene.traverse((obj) => {
        if (obj.userData.update) {
            obj.userData.update(time);
        }
    });

    renderer.render(scene, camera);
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
