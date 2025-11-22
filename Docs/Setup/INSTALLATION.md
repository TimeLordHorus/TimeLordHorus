# Sanctuary VR - Installation Guide

Complete setup instructions for developers and contributors.

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- Windows 10/11 PC or macOS 12+
- 16GB RAM
- NVIDIA GTX 1060 / AMD RX 580 or better
- 20GB free disk space
- Meta Quest 3 headset (or compatible PCVR headset)

**Recommended:**
- Windows 11 PC
- 32GB RAM
- NVIDIA RTX 3070 / AMD RX 6800 or better
- 50GB free SSD space
- Meta Quest 3 with Link Cable or Air Link

### Software Requirements

1. **Unity Hub** (latest version)
   - Download: https://unity.com/download

2. **Unity 2022.3 LTS**
   - Install via Unity Hub
   - Include modules:
     - Android Build Support
     - Android SDK & NDK Tools
     - OpenJDK
     - Windows Build Support (if on Mac)
     - Mac Build Support (if on Windows)

3. **Git** (2.40+)
   - Download: https://git-scm.com/downloads
   - Enable Git LFS during installation

4. **Visual Studio 2022** or **Visual Studio Code**
   - VS 2022: https://visualstudio.microsoft.com/
   - Include "Game development with Unity" workload
   - VS Code: https://code.visualstudio.com/
   - Install C# extension

5. **Python 3.9+** (for backend services)
   - Download: https://www.python.org/downloads/
   - Add to PATH during installation

6. **Meta Quest Developer Hub** (optional, for testing)
   - Download: https://developer.oculus.com/downloads/

---

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/TimeLordHorus/TimeLordHorus.git
cd TimeLordHorus

# Initialize Git LFS
git lfs install
git lfs pull
```

### 2. Open Project in Unity

1. Launch **Unity Hub**
2. Click **Add** → **Add project from disk**
3. Navigate to `TimeLordHorus/Sanctuary` folder
4. Select the folder and click **Open**
5. Unity will import the project (this may take 10-20 minutes)

### 3. Install Required Unity Packages

The package manifest (`Sanctuary/Packages/manifest.json`) contains all dependencies. Unity will auto-install them on first launch.

**Verify Packages:**
1. Open Unity Editor
2. Go to **Window** → **Package Manager**
3. Confirm these packages are installed:
   - XR Interaction Toolkit (2.5.2)
   - XR Plugin Management (4.4.0)
   - OpenXR Plugin (1.9.1)
   - Universal Render Pipeline (14.0.9)
   - TextMeshPro (3.0.6)

**Install glTFast (Runtime GLB Import):**
1. In Package Manager, click **+** → **Add package from git URL**
2. Enter: `https://github.com/atteneder/glTFast.git`
3. Click **Add**

### 4. Configure XR Settings

**Enable OpenXR:**
1. Go to **Edit** → **Project Settings** → **XR Plug-in Management**
2. Select **Android** tab (for Quest)
3. Check **OpenXR**
4. Click **OpenXR** under Android
5. Add **Oculus Touch Controller Profile**
6. Add **Hand Tracking Subsystem** (if using hand tracking)

**Repeat for Desktop/Standalone:**
1. Select **PC, Mac & Linux Standalone** tab
2. Check **OpenXR**
3. Add **Meta Quest Support** feature

### 5. Configure Build Settings

**For Meta Quest 3:**
1. **File** → **Build Settings**
2. Select **Android**
3. Click **Switch Platform**
4. In **Player Settings**:
   - **Company Name**: Your name
   - **Product Name**: Sanctuary
   - **Package Name**: `com.timelord.sanctuary`
   - **Minimum API Level**: Android 10.0 (API 29)
   - **Target API Level**: Android 13.0 (API 33)
   - **Install Location**: Automatic
   - **Scripting Backend**: IL2CPP
   - **Target Architectures**: ARM64 only

**Graphics Settings:**
1. **Edit** → **Project Settings** → **Graphics**
2. Verify **Scriptable Render Pipeline Settings** points to URP asset
3. Go to **Quality**
4. Create Android-specific quality preset (medium settings for Quest)

### 6. Setup Python Backend (Optional for AI Features)

```bash
# Navigate to backend directory (create if doesn't exist)
mkdir -p Backend
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install flask flask-cors python-dotenv requests openai pillow

# Create .env file
cat > .env << EOL
SANCTUARY_API_KEY=your_development_key_here
SHAP_E_API_KEY=your_shap_e_key
MESHY_API_KEY=your_meshy_key
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///sanctuary.db
CDN_BASE_URL=http://localhost:5000/static
EOL
```

### 7. Import Sample Assets (Optional)

Download starter assets from:
- **Medusa Jellyfish Model**: TBD
- **Central Hub Environment**: TBD
- **UI Prefabs**: TBD

Place in `Sanctuary/Assets/` appropriate folders.

---

## Verification

### Test Unity Setup

1. Open scene: `Assets/Scenes/TestScene.unity` (create if doesn't exist)
2. Press **Play** in Unity Editor
3. Verify no console errors
4. Check XR Device Simulator (if XR Interaction Toolkit installed)

### Test VR Build

**Quest 3 Device:**
1. Enable **Developer Mode** on Quest 3:
   - Install Meta Quest mobile app
   - Go to Settings → Developer → Enable Developer Mode
2. Connect Quest to PC via USB-C cable
3. In Unity: **File** → **Build and Run**
4. Accept USB debugging prompt on headset
5. App should launch automatically

**PCVR Test:**
1. Launch SteamVR or Oculus PC app
2. Connect headset
3. In Unity: **File** → **Build and Run** (Windows Standalone)
4. Launch generated .exe file

### Test Backend API

```bash
# Run Flask server
cd Backend
python app.py

# Test endpoint (in another terminal)
curl -X POST http://localhost:5000/api/v1/generate/model \
  -H "Authorization: Bearer your_development_key_here" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test cube", "user_id": "dev_test"}'
```

---

## Troubleshooting

### Unity Won't Open Project

**Solution:**
- Ensure Unity 2022.3 LTS is installed (not 2023.x or 2021.x)
- Delete `Sanctuary/Library` folder and reopen
- Check console for package import errors

### XR Packages Missing

**Solution:**
1. Go to **Window** → **Package Manager**
2. Click **+** → **Add package by name**
3. Enter: `com.unity.xr.interaction.toolkit`
4. Repeat for other missing packages

### Android Build Fails

**Common Issues:**
- **JDK not found**: Install OpenJDK via Unity Hub modules
- **NDK not found**: Install Android NDK via Unity Hub modules
- **Gradle errors**: Update to latest Gradle in Unity settings
- **Signing errors**: Create debug keystore or use Unity's auto-signing

### Quest 3 Not Detected

**Solution:**
- Install Meta Quest Developer Hub
- Update Quest 3 firmware
- Use official USB-C cable (not all cables support data)
- Enable Developer Mode in Meta Quest mobile app

### Performance Issues in VR

**Optimizations:**
- Lower quality settings: **Edit** → **Project Settings** → **Quality**
- Reduce shadow distance and resolution
- Enable **Static Batching** and **Dynamic Batching**
- Use **Occlusion Culling**
- Profile with Unity Profiler: **Window** → **Analysis** → **Profiler**

### Python Backend Not Starting

**Solution:**
```bash
# Verify Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check for port conflicts
# Windows:
netstat -ano | findstr :5000
# Mac/Linux:
lsof -i :5000
```

---

## Development Workflow

### Daily Development

1. Pull latest changes: `git pull origin main`
2. Open Unity project
3. Make changes
4. Test in Editor with XR Device Simulator
5. Build to Quest 3 for VR testing
6. Commit and push changes

### Before Committing

1. Ensure no console errors
2. Test build on target device
3. Update documentation if adding features
4. Run code formatter (if using)
5. Write descriptive commit message

---

## Next Steps

After installation:
1. Read [Architecture Documentation](../Architecture/TECHNICAL_ARCHITECTURE.md)
2. Review [API Documentation](../API/AI_BACKEND_API.md)
3. Explore example scripts in `Sanctuary/Assets/Scripts/`
4. Join development Discord (TBD)
5. Check Issues on GitHub for tasks

---

## Additional Resources

- **Unity XR Interaction Toolkit Manual**: https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest
- **Meta Quest Developer Docs**: https://developer.oculus.com/documentation/
- **Universal Render Pipeline**: https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@latest
- **glTFast Documentation**: https://github.com/atteneder/glTFast

---

## Support

For installation issues:
- Open GitHub Issue: https://github.com/TimeLordHorus/TimeLordHorus/issues
- Contact: Curtis G Kyle Junior (Lead Architect)

---

**Welcome to Sanctuary development! Let's build the future of VR together.**
