# Sanctuary Technical Architecture

## Overview

Sanctuary is built as a distributed system with Unity as the client and Python-based microservices handling AI operations.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Unity Client (VR)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  XR Rig     │  │   Avatar     │  │  UI System   │       │
│  │ (Jellyfish) │  │   Manager    │  │   (Loom)     │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                  │               │
│  ┌──────▼─────────────────▼──────────────────▼──────┐       │
│  │           Scene Manager / Game Controller        │       │
│  └──────┬─────────────────┬──────────────────┬──────┘       │
│         │                 │                  │               │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐       │
│  │  Networking │   │ AI Pipeline │   │   Archive   │       │
│  │  (Photon)   │   │   Client    │   │   Client    │       │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘       │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          │                 │                 │
┌─────────▼──────┐ ┌────────▼────────┐ ┌─────▼────────────┐
│  Photon Fusion │ │  Flask AI       │ │  Archive.org     │
│  Cloud Server  │ │  Backend        │ │  API             │
└────────────────┘ │  ┌───────────┐  │ └──────────────────┘
                   │  │ Whisper   │  │
                   │  │ API       │  │
                   │  └───────────┘  │
                   │  ┌───────────┐  │
                   │  │ Shap-E /  │  │
                   │  │ Meshy API │  │
                   │  └───────────┘  │
                   └─────────────────┘
```

---

## Core Systems

### 1. XR Interaction System

**Components:**
- `XROrigin` - Camera rig for VR headset and controllers
- `LocomotionSystem` - Custom flight-based movement for jellyfish avatar
- `XRInteractionManager` - Handles grab, scale, rotate interactions
- `HandTrackingProvider` - Meta Quest hand tracking integration

**Physics:**
- Jellyfish movement uses Verlet integration for realistic floating
- Tentacles are procedurally animated using Dynamic Bones
- Collision detection for environmental boundaries

### 2. Avatar System

**Medusa Jellyfish Implementation:**

```csharp
// Core components
public class MedusaAvatar : MonoBehaviour
{
    public SkinnedMeshRenderer bellMesh;
    public Transform[] tentacles;
    public AudioSource voiceInput;
    public BioluminescentShader glowShader;

    void Update()
    {
        // Audio reactivity
        float volume = GetVoiceVolume();
        glowShader.SetIntensity(volume);

        // Verlet physics for tentacles
        UpdateTentaclePhysics();
    }
}
```

**Shader Graph:**
- Fresnel-based bioluminescence
- Voronoi noise for organic patterns
- Time-based pulse animation
- Audio amplitude input for reactivity

### 3. Generative AI Pipeline

**Request Flow:**

1. User speaks prompt → Whisper API transcription
2. Unity sends HTTP POST to Flask server
3. Flask forwards to Text-to-3D service
4. Generated GLB file URL returned
5. glTFast downloads and instantiates model
6. User can grab and manipulate in VR

**API Endpoints:**

```python
# Flask Backend
@app.route('/generate', methods=['POST'])
def generate_model():
    prompt = request.json['prompt']
    user_id = request.json['user_id']

    # Call Text-to-3D API
    model_url = call_text_to_3d(prompt)

    # Store in database
    save_creation(user_id, prompt, model_url)

    return {'model_url': model_url, 'status': 'success'}
```

**Runtime Import:**

```csharp
using GLTFast;

public class ModelImporter : MonoBehaviour
{
    public async Task<GameObject> ImportModel(string url)
    {
        var gltf = new GltfImport();
        bool success = await gltf.Load(url);

        if (success)
        {
            GameObject instantiatedModel = new GameObject();
            await gltf.InstantiateMainScene(instantiatedModel.transform);
            return instantiatedModel;
        }
        return null;
    }
}
```

### 4. Protected Biomes

**Biome Structure:**

Each biome is a separate Unity scene with:
- Environmental assets (terrain, vegetation, atmosphere)
- Interactive triggers (proximity audio, visual effects)
- Educational content nodes (text, images, 3D models)
- Portal back to Central Hub

**Example: Thoreau Woods**

```csharp
public class ThoreauWoods : BiomeController
{
    public AudioClip[] waldenExcerpts;
    public ProximityTrigger[] audioZones;

    protected override void OnPlayerEnter()
    {
        // Fade in forest ambience
        // Activate proximity triggers
    }
}
```

### 5. Age Verification System

**Verification Flow:**

```
User Launch → Void Space UI → Biometric Scan → Age Estimation
                                     ↓
                            [Age < 18] → Deny Access
                                     ↓
                            [Age >= 18] → Questionnaire
                                     ↓
                            [Pass] → Grant Token → Enter Hub
```

**Privacy Implementation:**
- Face data processed locally on device
- Verification result stored as boolean token
- No biometric data transmitted or stored
- Questionnaire randomized from pool

### 6. Networking Architecture

**Photon Fusion Setup:**

```csharp
public class SanctuaryNetworkManager : NetworkBehaviour
{
    public override void Spawned()
    {
        if (Object.HasInputAuthority)
        {
            // Local player
            SpawnAvatar();
        }
    }

    [Networked]
    public Vector3 AvatarPosition { get; set; }

    [Networked]
    public float GlowIntensity { get; set; }
}
```

**Network Features:**
- Synced avatar positions and animations
- Voice chat with spatial audio
- Shared creation instances
- Permission system for biome interactions

### 7. Archive Integration

**API Wrapper:**

```csharp
public class ArchiveClient : MonoBehaviour
{
    private const string API_BASE = "https://archive.org/advancedsearch.php";

    public async Task<ArchiveResult[]> Search(string query)
    {
        string url = $"{API_BASE}?q={query}&output=json";
        // HTTP request and JSON parsing
    }
}
```

**Datacube Visualization:**
- 3D cube spawns at user's hand
- Expand gesture opens holographic interface
- Spatial UI for browsing results
- Audio player for text-to-speech

---

## Performance Optimization

### Quest 3 Targets
- **Frame Rate**: 72 FPS minimum, 90 FPS preferred
- **Draw Calls**: < 200 per frame
- **Polycount**: 50k-100k total active triangles
- **Texture Memory**: < 512 MB active

### Optimization Strategies

1. **LOD Groups**: 3 levels for all generated models
2. **Occlusion Culling**: Pre-baked for biomes
3. **Object Pooling**: Reuse datacubes and UI elements
4. **Addressables**: Async loading for biome scenes
5. **Shader Variants**: Strip unused keywords
6. **Texture Atlasing**: Combine materials where possible

---

## Security Considerations

### Age Verification
- Device-local processing only
- No permanent storage of biometric data
- Encrypted token system

### User Data
- Firebase authentication with OAuth
- Encrypted player preferences
- GDPR-compliant data deletion

### Content Moderation
- AI-generated content filtered for NSFW
- User reporting system
- Admin moderation tools

---

## Scalability

### Current Capacity
- 20-30 concurrent users per Hub instance
- Unlimited biome instances (separate scenes)
- Cloud storage for generated assets

### Future Expansion
- Horizontal scaling via Photon regions
- CDN for generated model hosting
- Database sharding for user profiles

---

## Dependencies

### Unity Packages
- XR Interaction Toolkit 2.5.2
- Universal Render Pipeline 14.0.9
- Netcode for GameObjects 1.7.1
- glTFast (runtime import)

### External Services
- Photon Fusion (networking)
- Firebase (database)
- OpenAI Whisper (speech-to-text)
- Shap-E / Meshy (text-to-3D)
- Archive.org API

### Development Tools
- Unity 2022.3 LTS
- Visual Studio 2022
- Blender 3.6 (asset creation)
- Python 3.9+ (backend)

---

## Testing Strategy

### Unit Tests
- Avatar movement physics
- API client wrappers
- Networking synchronization

### Integration Tests
- AI pipeline end-to-end
- Biome scene transitions
- Multiplayer interactions

### VR Testing
- Quest 3 device testing
- PCVR compatibility
- Performance profiling

---

## Deployment Pipeline

1. **Development**: Local Unity Editor testing
2. **Staging**: Test builds to internal Quest devices
3. **Beta**: Limited user testing via SideQuest
4. **Production**: Meta Quest Store / Steam VR

---

## Future Architecture Enhancements

- WebXR support for browser-based access
- Blockchain integration for asset ownership
- Advanced haptics for compatible devices
- Eye-tracking for foveated rendering
- Cloud rendering for high-fidelity PCVR
