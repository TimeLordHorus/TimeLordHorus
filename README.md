# Sanctuary VR Metaverse

![Unity](https://img.shields.io/badge/Unity-2022.3_LTS-black?logo=unity)
![Platform](https://img.shields.io/badge/Platform-Meta_Quest_3_%7C_PCVR-blue)
![XR Toolkit](https://img.shields.io/badge/XR-Interaction_Toolkit-green)
![Status](https://img.shields.io/badge/Status-In_Development-yellow)

**Sanctuary** is a persistent VR metaverse focused on creation, spirituality, and nature conservation. Built with Unity and the XR Interaction Toolkit, it features runtime generative AI for 3D asset creation, educational biomes, and integration with global knowledge repositories.

**Lead Architect:** Curtis G Kyle Junior

---

## Vision

Sanctuary combines cutting-edge VR technology with AI-powered creativity to create an immersive platform where users can:
- Sculpt 3D assets using voice and text prompts
- Explore educational biomes dedicated to philosophy and nature conservation
- Access the world's knowledge through immersive interfaces
- Connect with others in a secure, age-verified community

---

## Core Features

### The Gate: Age Verification System
- Biometric facial analysis for 18+ age verification
- Privacy-first approach with zero-knowledge proof
- Anti-bot questionnaire challenges

### Avatar System: The Medusa
- Default jellyfish avatar with physics-based locomotion
- Bioluminescent shaders reactive to voice
- Full customization options (tentacle length, transparency, colors)

### The Central Hub: "The Station"
- Solarpunk-inspired social lobby
- Portal gallery to Creation Realms and Protected Biomes
- Real-time visualization of connected archive data

### In-Game Creation: The Loom
- Voice-to-text input via Whisper API
- Text-to-3D generation (Shap-E, Meshy, Point-E integration)
- Runtime GLB import and manipulation
- Material painting and transformation tools

### Protected Biomes: Educational Zones
- **The Thoreau Woods**: New England forest with Walden audio excerpts
- **The Spinoza Geometric Plains**: Fractal landscapes with Ethics philosophy
- **The Muir Glacier**: Time-lapse climate awareness simulation

### The Infinite Archive
- Integration with Archive.org, Project Gutenberg, Biodiversity Heritage Library
- 3D Datacube visualization of search results
- Immersive reading and audio playback modes

---

## Technical Stack

### Platform
- **Engine**: Unity 2022.3 LTS
- **Renderer**: Universal Render Pipeline (URP)
- **XR Framework**: XR Interaction Toolkit
- **Target Devices**: Meta Quest 3, PCVR (Steam VR)

### Key Packages
- XR Interaction Toolkit 2.5.2
- OpenXR 1.9.1
- Universal Render Pipeline 14.0.9
- Netcode for GameObjects 1.7.1
- GLTFast (runtime model import)
- TextMeshPro, Shader Graph, VFX Graph

### Backend Services
- **AI Pipeline**: Python Flask server
- **Text-to-3D**: Shap-E / Meshy / Point-E APIs
- **Voice Input**: OpenAI Whisper API
- **Networking**: Photon Fusion / Normcore
- **Database**: Firebase for user profiles and state

---

## Project Structure

```
TimeLordHorus/
├── Sanctuary/                    # Main Unity project
│   ├── Assets/
│   │   ├── Scenes/              # VR scenes
│   │   ├── Scripts/             # C# scripts
│   │   │   ├── Core/            # Core systems
│   │   │   ├── AI/              # Generative AI integration
│   │   │   ├── Avatar/          # Medusa jellyfish system
│   │   │   ├── Biomes/          # Protected biome logic
│   │   │   ├── UI/              # User interfaces
│   │   │   ├── Networking/      # Multiplayer
│   │   │   ├── Verification/    # Age verification
│   │   │   └── Utils/           # Utilities
│   │   ├── Prefabs/             # Reusable objects
│   │   ├── Materials/           # Shaders and materials
│   │   ├── Models/              # 3D assets
│   │   ├── Audio/               # Sound effects & music
│   │   └── Resources/           # Runtime-loaded assets
│   ├── Packages/                # Package manifest
│   └── ProjectSettings/         # Unity settings
├── Docs/                        # Documentation
│   ├── Architecture/            # Technical architecture
│   ├── API/                     # API documentation
│   ├── Setup/                   # Installation guides
│   └── Guides/                  # User guides
└── README.md                    # This file
```

---

## Development Roadmap

### Phase 1: Core Systems (Weeks 1-4) ✅ **COMPLETE**
- [x] Unity URP configuration (High-Quality + Quest-optimized)
- [x] XR Rig with flight locomotion (jellyfish-style movement)
- [x] Unity Netcode multiplayer setup (32 players, client-server)
- [x] Basic Central Hub environment ("The Station" with portal system)

**[View Phase 1 Documentation](Docs/Phase1_CoreSystems.md)**

### Phase 2: AI Pipeline (Weeks 5-8) ✅ **COMPLETE**
- [x] Flask server for AI requests (Text-to-3D + Whisper services)
- [x] Text-to-3D API integration (Meshy AI, Shap-E via Replicate)
- [x] Runtime GLB import with glTFast (async loading, VR interaction)
- [x] Voice-to-text input system (Whisper backend ready)

**[View Phase 2 Documentation](Docs/Phase2_AI_Pipeline.md)**

### Phase 3: Content & Biomes (Weeks 9-12) ✅ **COMPLETE**
- [x] Medusa jellyfish avatar system (bioluminescent shaders, network sync, customization)
- [x] Protected Biomes: Thoreau Woods, Spinoza Plains, Muir Glacier
- [x] Firebase user profile system (authentication, XP/leveling, creation storage)
- [x] Archive.org API integration (3D datacube visualization, text search)

**[View Phase 3 Documentation](Docs/Phase3_Content_Biomes.md)**

### Phase 4: Security & Polish (Weeks 13-16) ✅ **COMPLETE**
- [x] The Gate age verification system (facial analysis, challenge questions, privacy-first)
- [x] LOD optimization for Quest 3 (dynamic quality, distance-based culling)
- [x] Audio reactivity for bioluminescent shaders (voice detection, frequency analysis)
- [x] Performance profiling and optimization (FPS tracking, memory monitoring, Quest targets)

**[View Phase 4 Documentation](Docs/Phase4_Security_Polish.md)**

---

## Getting Started

### Prerequisites
- Unity 2022.3 LTS or newer
- Meta Quest 3 headset (or compatible PCVR setup)
- Git LFS (for large asset files)
- Python 3.9+ (for backend services)

### Installation
See [Docs/Setup/INSTALLATION.md](Docs/Setup/INSTALLATION.md) for detailed setup instructions.

### Quick Start
1. Clone the repository
2. Open the `Sanctuary` folder in Unity Hub
3. Install XR Interaction Toolkit and OpenXR packages
4. Set build target to Android (Quest) or Windows (PCVR)
5. Open the `MainHub` scene in `Assets/Scenes/`

---

## Contributing

This project is currently in early development. Contribution guidelines will be published as the project matures.

---

## License

To be determined. All rights reserved to Curtis G Kyle Junior and contributors.

---

## Contact

**Lead Architect**: Curtis G Kyle Junior
**Project Repository**: [TimeLordHorus/TimeLordHorus](https://github.com/TimeLordHorus/TimeLordHorus)

---

## Acknowledgments

Inspired by the philosophies of:
- Henry David Thoreau (Walden)
- Baruch Spinoza (Ethics)
- John Muir (Nature Conservation)

Built with cutting-edge technologies from Unity, Meta, OpenAI, and the open-source community.

---

**Sanctuary** - Where creation meets consciousness.
