/**
 * Sanctuary VR Configuration
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.origin + '/api/v1',

    // WebXR Settings
    WEBXR: {
        REFERENCE_SPACE: 'local-floor',
        FRAME_RATE: 72,
        FOVEATION_LEVEL: 1, // 0 = off, 1 = low, 2 = medium, 3 = high
    },

    // Scene Settings
    SCENE: {
        FOG_COLOR: 0x0a0e27,
        FOG_DENSITY: 0.01,
        AMBIENT_LIGHT_INTENSITY: 0.5,
        DIRECTIONAL_LIGHT_INTENSITY: 0.8,
    },

    // Avatar Settings
    AVATAR: {
        TYPE: 'medusa', // Jellyfish avatar
        GLOW_COLOR: 0x00ffff,
        GLOW_INTENSITY: 1.0,
        FLOAT_SPEED: 0.5,
        FLOAT_AMPLITUDE: 0.3,
    },

    // Central Hub Spawn Point
    SPAWN_POINT: {
        x: 0,
        y: 1.6,
        z: 5
    },

    // Performance
    PERFORMANCE: {
        MAX_POLYCOUNT: 50000,
        TEXTURE_MAX_SIZE: 2048,
        ENABLE_SHADOWS: true,
        ANTIALIAS: true,
    },

    // Biomes
    BIOMES: {
        THOREAU_WOODS: {
            name: 'The Thoreau Woods',
            scene: '/scenes/thoreau-woods.json',
            spawnPoint: { x: 0, y: 0, z: 0 }
        },
        SPINOZA_PLAINS: {
            name: 'The Spinoza Geometric Plains',
            scene: '/scenes/spinoza-plains.json',
            spawnPoint: { x: 0, y: 0, z: 0 }
        },
        MUIR_GLACIER: {
            name: 'The Muir Glacier',
            scene: '/scenes/muir-glacier.json',
            spawnPoint: { x: 0, y: 0, z: 0 }
        }
    }
};
