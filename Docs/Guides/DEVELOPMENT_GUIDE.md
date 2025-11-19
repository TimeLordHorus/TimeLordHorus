# Sanctuary Development Guide

This guide provides workflows and best practices for developing Sanctuary.

---

## Development Environment Setup

### Required Tools
- Unity 2022.3 LTS
- Visual Studio 2022 or VS Code
- Git + Git LFS
- Python 3.9+
- Meta Quest Developer Hub (for Quest testing)

See [Installation Guide](../Setup/INSTALLATION.md) for detailed setup.

---

## Project Structure

```
Sanctuary/
├── Assets/
│   ├── Scenes/              # Unity scenes
│   ├── Scripts/             # C# codebase
│   │   ├── Core/            # Core game systems
│   │   ├── AI/              # AI integration
│   │   ├── Avatar/          # Medusa jellyfish
│   │   ├── Biomes/          # Protected biomes
│   │   ├── UI/              # User interfaces
│   │   ├── Networking/      # Multiplayer
│   │   ├── Verification/    # Age verification
│   │   └── Utils/           # Helper utilities
│   ├── Prefabs/             # Reusable GameObjects
│   ├── Materials/           # Shaders and materials
│   ├── Models/              # 3D assets
│   └── Audio/               # Sound effects
```

---

## Development Workflow

### 1. Starting a New Feature

```bash
# Pull latest changes
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name

# Work on your feature
# ... make changes ...

# Test in Unity Editor
# Test on Quest 3 (if VR-related)

# Commit your changes
git add .
git commit -m "Add: Brief description of feature"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### 2. Testing Workflow

**In Unity Editor:**
1. Open the relevant scene
2. Press Play
3. Use XR Device Simulator for VR testing
4. Check Console for errors

**On Quest 3:**
1. Connect Quest via USB
2. Enable Developer Mode
3. Build and Run from Unity
4. Test in headset
5. Check logcat for errors:
   ```bash
   adb logcat -s Unity
   ```

### 3. Code Review Checklist

Before submitting a PR:
- [ ] Code compiles without errors
- [ ] No warnings in Unity Console
- [ ] Tested in Editor
- [ ] Tested on Quest 3 (if VR feature)
- [ ] Frame rate maintained (72+ FPS on Quest)
- [ ] Documentation updated
- [ ] Comments added for complex logic
- [ ] Git commit messages are clear

---

## Coding Standards

### C# Style Guide

```csharp
// Namespace: Sanctuary.<Module>
namespace Sanctuary.Avatar
{
    /// <summary>
    /// Always include XML documentation for public classes
    /// </summary>
    public class ExampleClass : MonoBehaviour
    {
        // Use SerializeField for inspector-exposed private fields
        [SerializeField] private float speed = 5f;

        // Public properties use PascalCase
        public bool IsActive { get; private set; }

        // Private fields use camelCase
        private int currentHealth;

        /// <summary>
        /// Document public methods
        /// </summary>
        public void DoSomething()
        {
            // Implementation
        }

        // Private methods use camelCase
        private void updateState()
        {
            // Implementation
        }
    }
}
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `MedusaAvatar`)
- **Methods**: `PascalCase` for public, `camelCase` for private
- **Fields**: `camelCase` with `_` prefix for private (e.g., `_playerHealth`)
- **Properties**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Prefabs**: `PascalCase` with descriptor (e.g., `Player_Medusa`)
- **Scenes**: `PascalCase` (e.g., `CentralHub`, `ThoreauWoods`)

### Performance Best Practices

**DO:**
- Use object pooling for frequently spawned objects
- Cache component references in Awake/Start
- Use `CompareTag()` instead of string comparison
- Batch draw calls with Static Batching
- Use LOD groups for complex models
- Profile regularly with Unity Profiler

**DON'T:**
- Use `GetComponent()` in Update()
- Allocate memory in Update() (creates GC pressure)
- Use `Find()` or `FindObjectOfType()` frequently
- Create excessive draw calls
- Use unoptimized shaders on Quest

### VR-Specific Guidelines

1. **Frame Rate is Critical**
   - Maintain 72 FPS minimum on Quest 3
   - Target 90 FPS for smooth experience
   - Use Fixed Foveated Rendering

2. **User Comfort**
   - Avoid rapid camera movements
   - Use teleportation or smooth locomotion options
   - Minimize latency in interactions
   - Follow Meta's VR Best Practices

3. **Interaction Design**
   - Make interactive objects clearly visible
   - Provide haptic feedback for interactions
   - Use spatial audio for feedback
   - Test grab distances carefully

---

## Working with Key Systems

### Medusa Avatar System

Located in: `Assets/Scripts/Avatar/`

```csharp
// Access the player's avatar
MedusaAvatar avatar = FindObjectOfType<MedusaAvatar>();

// Set glow intensity
avatar.SetGlowIntensity(0.8f);

// Get current glow
float glow = avatar.GetGlowIntensity();
```

### AI Model Generation

Located in: `Assets/Scripts/AI/`

```csharp
// Generate a 3D model
var client = TextTo3DClient.Instance;
var response = await client.GenerateModel(
    "A crystal tree",
    userId: "player123"
);

// Import and spawn the model
var importer = RuntimeModelImporter.Instance;
GameObject model = await importer.ImportAndSpawnModel(response.model_url);
```

### Protected Biomes

Located in: `Assets/Scripts/Biomes/`

```csharp
// Create a new biome by extending BiomeController
public class MyCustomBiome : BiomeController
{
    protected override void OnPlayerEnter()
    {
        base.OnPlayerEnter();

        // Custom entry logic
        Debug.Log("Welcome to my biome!");
    }

    protected override void SetupEnvironment()
    {
        base.SetupEnvironment();

        // Custom environment setup
        RenderSettings.fogColor = Color.blue;
    }
}
```

---

## Debugging Tips

### Common Issues

**Issue: VR not working in Editor**
- Solution: Install XR Interaction Toolkit
- Enable XR Plug-in Management
- Use XR Device Simulator for testing

**Issue: Low frame rate on Quest**
- Check Unity Profiler for bottlenecks
- Reduce draw calls
- Optimize shaders
- Lower texture resolutions

**Issue: Model import fails**
- Verify glTFast is installed
- Check model URL is accessible
- Review Console for specific errors

### Useful Console Commands

```bash
# Check Quest connection
adb devices

# View Unity logs on Quest
adb logcat -s Unity

# Clear app data
adb shell pm clear com.timelord.sanctuary

# Take screenshot
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# Record video (Quest 3)
adb shell screenrecord /sdcard/demo.mp4
```

---

## Backend Development

### Python Flask Server

Located in: `Backend/` (create if doesn't exist)

```python
# app.py
from flask import Flask, request, jsonify
from services.text_to_3d import generate_model_shap_e

app = Flask(__name__)

@app.route('/api/v1/generate/model', methods=['POST'])
def generate():
    data = request.json
    result = generate_model_shap_e(data['prompt'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Running Backend Locally

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## Asset Creation Guidelines

### 3D Models
- **Format**: FBX or GLB
- **Polycount**: < 10k triangles for Quest
- **Textures**: Max 2048x2048
- **Materials**: Use URP-compatible shaders

### Audio
- **Format**: OGG Vorbis (compressed)
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit
- **Spatial Audio**: Use for 3D sounds

### Textures
- **Format**: PNG or JPG
- **Compression**: Enable for platforms
- **Mipmaps**: Generate for performance
- **Atlasing**: Combine when possible

---

## Version Control

### Commit Message Format

```
Type: Brief description

Detailed explanation (if needed)

- Bullet points for changes
- Use present tense
```

**Types:**
- `Add`: New feature
- `Fix`: Bug fix
- `Update`: Modify existing feature
- `Remove`: Delete code/assets
- `Refactor`: Code restructure
- `Docs`: Documentation only
- `Test`: Add/modify tests

**Examples:**
```
Add: Medusa jellyfish avatar system

Implemented physics-based floating locomotion and bioluminescent
shader reactivity to voice input.

- Created MedusaAvatar.cs controller
- Added Verlet integration for tentacles
- Implemented audio-reactive glow shader
```

---

## Resources

- [Unity XR Interaction Toolkit Docs](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest)
- [Meta Quest Developer Center](https://developer.oculus.com)
- [Universal Render Pipeline Guide](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@latest)
- [C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)

---

## Getting Help

- Check existing documentation in `Docs/`
- Review example scripts in `Assets/Scripts/`
- Open GitHub issue for bugs
- Contact Lead Architect: Curtis G Kyle Junior

---

**Happy coding! Welcome to the Sanctuary development team.**
