# Sanctuary Beta - Conversion Guide

**From Java WebXR PWA to Native VR Platform**

This guide explains how to convert the Java Spring Boot + WebXR beta into a more robust native VR application using Unity or Unreal Engine.

---

## Overview

The Sanctuary Beta serves as a **prototype and proof-of-concept** that can be accessed via web browsers. For production and enhanced VR capabilities, you should convert to:

1. **Unity with XR Interaction Toolkit** (Recommended)
2. **Unreal Engine 5 with VR Templates**
3. **Native Quest Application** (C++ or C#)

---

## Why Convert?

### WebXR Limitations
- ❌ Limited performance (browser overhead)
- ❌ No native haptics support
- ❌ Restricted file system access
- ❌ Browser-dependent features
- ❌ Network latency for all assets

### Native VR Benefits
- ✅ Higher frame rates (90-120 FPS)
- ✅ Full haptics and controller support
- ✅ Offline capabilities
- ✅ Better graphics quality
- ✅ Access to platform SDKs
- ✅ App store distribution

---

## Conversion Option 1: Unity (Recommended)

### Step 1: Setup Unity Project

```bash
# Unity version: 2022.3 LTS or newer
# Already created in /Sanctuary folder!
```

The Unity project structure is **already prepared** in the main repository at `/Sanctuary`.

### Step 2: Map Java Backend to C# Services

**Java Spring Boot Controller → Unity C# API Client**

```java
// Java (existing)
@PostMapping("/generate")
public ResponseEntity<GenerateModelResponse> generateModel(@RequestBody GenerateModelRequest request) {
    // ...
}
```

```csharp
// C# (Unity) - Already implemented in Sanctuary/Assets/Scripts/AI/TextTo3DClient.cs
public async Task<ModelResponse> GenerateModel(string prompt, string userId) {
    // Use UnityWebRequest to call Java backend
}
```

### Step 3: Convert WebXR Scenes to Unity Scenes

**WebXR Three.js Scene → Unity Scene**

| WebXR Component | Unity Equivalent | Location |
|----------------|------------------|----------|
| `THREE.Scene` | Unity Scene | `Assets/Scenes/` |
| `THREE.Mesh` | GameObject + MeshFilter | Prefabs |
| `THREE.Material` | Unity Material | `Assets/Materials/` |
| `THREE.PointLight` | Light Component | Scene Hierarchy |
| `VRButton` | XR Rig | XR Interaction Toolkit |

**Central Hub Conversion:**

```javascript
// WebXR (main.js)
function createCentralHub() {
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    scene.add(ground);
}
```

```csharp
// Unity (HubManager.cs)
void CreateCentralHub() {
    GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
    ground.transform.localScale = new Vector3(10, 1, 10);
}
```

### Step 4: Convert Medusa Avatar

**WebXR MedusaAvatar.js → Unity MedusaAvatar.cs**

The Unity version is **already implemented** at:
`Sanctuary/Assets/Scripts/Avatar/MedusaAvatar.cs`

**Key Differences:**

| Feature | WebXR | Unity |
|---------|-------|-------|
| Tentacles | Manual vertex manipulation | Dynamic Bones / Cloth |
| Glow | `emissive` material | Emission shader + HDR |
| Physics | JavaScript Verlet | Unity Physics / Rigidbody |
| Audio | Web Audio API | AudioSource component |

### Step 5: Keep Java Backend Running

**Architecture:**
```
[Unity Client (C#)] ←→ [Java Spring Boot Backend] ←→ [AI Services]
      Quest 3              REST API                   Text-to-3D
```

- Unity handles rendering and VR interaction
- Java backend handles AI generation, database, user management
- Both communicate via REST API (already implemented!)

### Step 6: Build and Deploy

```bash
# In Unity:
# 1. File → Build Settings → Android
# 2. Switch Platform
# 3. Player Settings:
#    - Package Name: com.timelord.sanctuary
#    - Min API Level: 29 (Android 10)
#    - Target: ARM64
# 4. Build and Run

# Java backend stays the same
cd SanctuaryBeta
mvn package
java -jar target/sanctuary-beta-0.1.0-BETA.jar
```

---

## Conversion Option 2: Unreal Engine 5

### Step 1: Create UE5 VR Project

```
# Unreal Engine 5.3+
# Template: Virtual Reality
# Blueprint or C++: C++ (for better performance)
```

### Step 2: Map Components

| Java/WebXR | Unreal Engine 5 |
|------------|----------------|
| Spring Boot Controllers | REST API Plugin |
| Three.js Meshes | Static Meshes |
| Medusa Avatar | Skeletal Mesh + Animation BP |
| WebXR Controllers | VR Pawn + Motion Controllers |
| Bioluminescence | Emissive Materials + Niagara VFX |

### Step 3: Blueprint or C++

**HTTP Request to Java Backend (Blueprint):**

```
HTTP Request Node
├─ URL: http://your-server:8080/api/v1/creations/generate
├─ Method: POST
├─ Headers: Authorization: Bearer {token}
└─ Body: {"prompt": "crystal tree", "quality": "high"}
```

**C++ Alternative:**

```cpp
// Use UE5 HTTP Module
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"

void ACreationManager::GenerateModel(FString Prompt) {
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL("http://your-server:8080/api/v1/creations/generate");
    Request->SetVerb("POST");
    Request->SetHeader("Content-Type", "application/json");
    Request->SetContentAsString(FString::Printf(TEXT("{\"prompt\":\"%s\"}"), *Prompt));
    Request->OnProcessRequestComplete().BindUObject(this, &ACreationManager::OnResponseReceived);
    Request->ProcessRequest();
}
```

### Step 4: Import Assets

- Export WebXR 3D models as FBX
- Import to UE5 Content Browser
- Setup materials with PBR workflow
- Create Blueprints for interaction

---

## Conversion Option 3: Native Quest App (Advanced)

### Use Unity/Unreal Instead

For Meta Quest native apps, **Unity is strongly recommended** because:
- Meta provides official Unity SDKs
- Easier debugging and iteration
- Better documentation
- Community support

Only use C++ if you need:
- Maximum performance optimization
- Custom rendering pipelines
- Integration with existing C++ code

---

## Database & Backend Migration

### Keep Java Backend (Recommended)

**Pros:**
- Already implemented
- API-first architecture
- Easy to scale
- Language-agnostic clients

**Deployment:**
```
                 Internet
                    ↓
              [Load Balancer]
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    [Spring Boot]        [Spring Boot]
         ↓                     ↓
    [PostgreSQL Master] ← [Replica]
         ↓
    [AI Services]
```

### Alternative: Migrate to C# Backend

If you want a C#-only stack:

**Convert to ASP.NET Core:**

```csharp
// Java Spring Boot
@PostMapping("/generate")
public ResponseEntity<GenerateModelResponse> generateModel(...) { }

// C# ASP.NET Core
[HttpPost("generate")]
public async Task<ActionResult<GenerateModelResponse>> GenerateModel(...) { }
```

**Migration Steps:**
1. Create ASP.NET Core Web API project
2. Port models (Java → C# POCOs)
3. Port repositories (JPA → Entity Framework)
4. Port services (Spring → ASP.NET DI)
5. Keep API contracts identical

---

## Asset Pipeline

### From WebXR to Unity

**3D Models:**
```
WebXR GLB/GLTF → Blender → FBX → Unity
```

**Textures:**
```
Web (PNG/JPG) → Photoshop → Compressed PNG/TGA → Unity
                          → Normal Maps
                          → PBR Material
```

**Audio:**
```
Web Audio (MP3) → Audacity → OGG Vorbis → Unity
```

### Runtime Model Import

**Both platforms support runtime GLB import:**

**Unity:**
```csharp
// Already implemented in RuntimeModelImporter.cs
using GLTFast;
var gltf = new GltfImport();
await gltf.Load(modelUrl);
```

**Unreal:**
```cpp
// Use glTF Runtime Loader plugin
UglTFRuntimeAsset* Asset = UglTFRuntimeFunctionLibrary::glTFLoadAssetFromUrl(ModelUrl);
```

---

## Performance Comparison

| Metric | WebXR (Beta) | Unity (Native) | Unreal (Native) |
|--------|--------------|----------------|-----------------|
| **Frame Rate** | 60-72 FPS | 72-120 FPS | 72-90 FPS |
| **Draw Calls** | 200-300 | 100-150 (batched) | 50-100 (merged) |
| **Load Time** | 5-10s | 2-5s | 3-7s |
| **Model Polycount** | 10k max | 50k max | 100k max |
| **File Size** | ~20 MB (cached) | 500 MB - 2 GB | 1-3 GB |
| **Haptics** | ❌ Limited | ✅ Full | ✅ Full |

---

## Migration Checklist

### Phase 1: Preparation
- [ ] Audit all WebXR features
- [ ] Document custom logic
- [ ] Export all 3D assets
- [ ] Test Java backend independently

### Phase 2: Unity Setup
- [ ] Open existing Sanctuary Unity project
- [ ] Import XR Interaction Toolkit
- [ ] Configure Quest 3 build settings
- [ ] Setup networking (Photon/Netcode)

### Phase 3: Feature Parity
- [ ] Port Medusa avatar (already done!)
- [ ] Port Central Hub scene
- [ ] Port Biomes (Thoreau, Spinoza, Muir)
- [ ] Integrate API client (already done!)
- [ ] Test model import pipeline

### Phase 4: Enhancement
- [ ] Add advanced haptics
- [ ] Improve shaders (URP/HDRP)
- [ ] Optimize for Quest 3 (72+ FPS)
- [ ] Add hand tracking
- [ ] Implement voice input

### Phase 5: Testing & Deployment
- [ ] Test on Quest 3 hardware
- [ ] Load testing backend
- [ ] Beta testing with users
- [ ] Submit to App Lab / Quest Store

---

## Code Reuse Matrix

| Component | WebXR Beta | Unity | Unreal | Reusable |
|-----------|-----------|-------|--------|----------|
| **Java Backend** | ✅ | ✅ | ✅ | 100% |
| **Database Schema** | ✅ | ✅ | ✅ | 100% |
| **API Contracts** | ✅ | ✅ | ✅ | 100% |
| **3D Models** | ✅ | ✅ | ✅ | 80% (re-export) |
| **Textures** | ✅ | ✅ | ✅ | 90% |
| **Game Logic** | JS | C# | C++/BP | 50% (rewrite) |
| **Shaders** | GLSL | HLSL/ShaderGraph | HLSL | 30% (rewrite) |
| **Animations** | Code | Unity Animator | Sequencer | 0% (rebuild) |

---

## Recommended Path

**For Sanctuary VR Production:**

1. ✅ **Use the existing Unity project** (`/Sanctuary`)
2. ✅ **Keep Java Spring Boot backend** (mature, working)
3. ✅ **C# scripts are already implemented** (see `/Sanctuary/Assets/Scripts/`)
4. ⚙️ **Deploy backend to cloud** (AWS, Azure, GCP)
5. 📱 **Build for Quest 3** using Unity Android build
6. 🚀 **Submit to App Lab** for beta testing

**Timeline:**
- Week 1-2: Unity project setup and API integration
- Week 3-4: Port all biomes and features
- Week 5-6: Optimization and testing
- Week 7-8: Beta release and feedback

---

## Conclusion

The **WebXR Beta** provides a solid foundation that demonstrates all core concepts. The **Unity conversion** is the optimal path forward because:

1. Unity project is already initialized (`/Sanctuary`)
2. Core scripts are already written (Avatar, AI Client, Biomes)
3. Java backend can remain unchanged
4. Meta Quest officially supports Unity
5. Faster development cycle

The WebXR version remains valuable as:
- Quick demo tool
- Web-accessible preview
- Testing environment
- Mobile browser experience

---

## Further Reading

- [Unity XR Interaction Toolkit](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest)
- [Meta Quest Development](https://developer.oculus.com/documentation/unity/)
- [Spring Boot REST Best Practices](https://spring.io/guides/tutorials/rest/)
- [GLB/GLTF Format](https://www.khronos.org/gltf/)

---

**Next Steps:** Open the Unity project at `/Sanctuary` and start building! 🚀
