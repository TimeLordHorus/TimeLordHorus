# Sanctuary Character HUD System

## Overview

The Sanctuary Character HUD (Heads-Up Display) is a comprehensive character management system that bridges real-world achievements with virtual character progression. Built with a unique **Brutalist-Victorian-Utilitarian** design philosophy, it provides users with a powerful interface to track their spiritual growth, creative accomplishments, and verified credentials.

## Design Philosophy

### Brutalism
- **Raw Honesty**: Exposed concrete textures, honest materials
- **Functional First**: Grid-based layouts, clear hierarchy
- **Typography**: Monospace fonts (Courier New) for data and code

### Victorian
- **Craftsmanship**: Ornate brass borders and frames
- **Prestige**: Serif fonts (Georgia) for titles and descriptions
- **Elegance**: Gold/brass accent colors (#b87333)

### Utilitarian
- **Purpose-Driven**: Every element serves a function
- **Accessibility**: High contrast, readable fonts
- **Grid System**: Consistent 8px spacing throughout

## Core Features

### 1. Character Profile System

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/CharacterProfile.java`

The character profile tracks:
- **Level & Experience**: RPG-style progression system
- **Core Stats**: Enlightenment, Wisdom, Creativity, Harmony, Knowledge
- **Currency**: Essence Points, Creation Tokens
- **Tracking**: Meditation minutes, biomes visited, creations made, texts read

```java
CharacterProfile profile = CharacterProfile.builder()
    .level(1)
    .experience(0)
    .enlightenment(0)
    .wisdom(0)
    .creativity(0)
    .essencePoints(50) // Starting essence
    .build();
```

### 2. Real-World Credential Verification

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/Credential.java`

**Supported Credential Types**:
- University Degrees (+100 XP)
- Professional Certifications (+50 XP)
- Licenses (+75 XP)
- Publications (+80 XP)
- Patents (+150 XP)
- Language Proficiency (+30 XP)
- And more...

**Verification Workflow**:
1. User uploads credential document (PDF/Image)
2. System generates SHA-256 hash for integrity
3. Status: PENDING → Admin reviews → VERIFIED/REJECTED
4. Upon verification: XP awarded, skills unlocked, titles granted

**Privacy Features**:
- User-controlled visibility (public/private)
- Encrypted document storage
- Hash verification for authenticity

**Example Submission**:
```javascript
const formData = new FormData();
formData.append('title', 'Bachelor of Science');
formData.append('type', 'UNIVERSITY_DEGREE');
formData.append('issuingOrganization', 'State University');
formData.append('document', file);

await apiClient.submitCredential(formData);
```

### 3. Skills System

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/Skill.java`

**15+ Skill Types**:
- Creative: SCULPTURE, ARCHITECTURE, PAINTING, MUSIC, POETRY
- Intellectual: PHILOSOPHY, LITERATURE, SCIENCE, MATHEMATICS
- Spiritual: MEDITATION, ENLIGHTENMENT, TEACHING
- Technical: PROGRAMMING, ENGINEERING

**Skill Progression**:
```java
Skill sculpture = Skill.builder()
    .type(SkillType.SCULPTURE)
    .name("3D Modeling")
    .level(1)
    .experience(0)
    .experienceToNextLevel(50)
    .build();

skill.addExperience(25); // Returns true if leveled up
```

### 4. Spell System

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/Spell.java`

**8 Magical Schools**:
- CREATION: Manifest objects into existence
- HARMONY: Restore balance and peace
- ILLUMINATION: Reveal hidden knowledge
- TEMPORAL: Manipulate time flow
- TRANSMUTATION: Transform matter
- KNOWLEDGE: Access ancient wisdom
- NATURE: Connect with natural forces
- ETHEREAL: Travel between realms

**Spell Mechanics**:
- Essence Cost: Currency required to cast
- Cooldown: Time-based limitation
- Unlock Requirements: Level or quest-based

```java
Spell manifestCreation = Spell.builder()
    .name("Manifest Creation")
    .school(SpellSchool.CREATION)
    .essenceCost(25)
    .cooldownSeconds(60)
    .build();

spell.cast(); // Sets lastCastTime
boolean ready = spell.isReady(); // Checks cooldown
```

### 5. Inventory System

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/InventoryItem.java`

**Rarity Tiers**:
- COMMON (gray border)
- UNCOMMON (green border)
- RARE (blue border)
- EPIC (purple border)
- LEGENDARY (orange border)
- MYTHIC (red border)

**Item Types**:
- CREATION: User-made 3D objects
- BOOK: Educational texts
- MATERIAL: Crafting resources
- TOOL: Utility items
- ARTIFACT: Special quest items

### 6. Knowledge Library

**Location**: `SanctuaryBeta/src/main/java/com/sanctuary/model/AcquiredKnowledge.java`

**10 Knowledge Categories**:
- PHILOSOPHY, LITERATURE, SCIENCE, MATHEMATICS
- HISTORY, ART, MUSIC, LANGUAGE
- SPIRITUALITY, TECHNOLOGY

**Sources**:
- BIOME_EDUCATION: Learn from educational biomes
- ARCHIVE_READING: Internet Archive, Project Gutenberg
- MEDITATION_INSIGHT: Gained through meditation
- CREDENTIAL_BASED: From verified credentials

## Architecture

### Backend (Spring Boot)

```
SanctuaryBeta/src/main/java/com/sanctuary/
├── model/              # JPA Entities
│   ├── CharacterProfile.java
│   ├── Credential.java
│   ├── Skill.java
│   ├── Spell.java
│   ├── InventoryItem.java
│   └── AcquiredKnowledge.java
├── repository/         # JPA Repositories
│   ├── CharacterProfileRepository.java
│   ├── CredentialRepository.java
│   ├── SkillRepository.java
│   └── ...
├── service/            # Business Logic
│   ├── CharacterService.java
│   └── CredentialService.java
├── controller/         # REST API
│   ├── CharacterController.java
│   ├── CredentialController.java
│   └── SkillController.java
└── dto/                # Data Transfer Objects
    ├── CharacterProfileDTO.java
    ├── CredentialDTO.java
    └── ...
```

### Frontend (WebXR PWA)

```
SanctuaryBeta/src/main/resources/static/
├── hud.html                        # HUD interface
├── css/
│   └── brutalist-victorian.css     # Design system (800+ lines)
└── js/
    ├── character-hud.js            # HUD controller
    └── api-client.js               # REST API client
```

## REST API Reference

### Character Endpoints

```http
GET  /api/v1/character/profile        # Get complete character data
GET  /api/v1/character/stats          # Get statistics summary
PUT  /api/v1/character/name           # Update character name
POST /api/v1/character/meditate       # Track meditation session
POST /api/v1/character/experience     # Award XP
POST /api/v1/character/biome-visit    # Track biome exploration
POST /api/v1/character/knowledge/{id}/complete  # Complete knowledge entry
```

### Credential Endpoints

```http
POST   /api/v1/credentials/submit              # Submit credential
GET    /api/v1/credentials                     # Get all credentials
GET    /api/v1/credentials/verified            # Get verified credentials
GET    /api/v1/credentials/public              # Get public credentials
PUT    /api/v1/credentials/{id}/visibility     # Update visibility
DELETE /api/v1/credentials/{id}                # Delete credential
POST   /api/v1/credentials/{id}/verify         # Admin: verify credential
```

### Skill Endpoints

```http
POST /api/v1/skills/{skillType}/award-xp       # Award skill XP
POST /api/v1/skills/spells/{spellId}/cast      # Cast spell
```

## Usage Examples

### Track Meditation

```javascript
// Frontend
const result = await apiClient.trackMeditation(30);
// Returns: { success: true, xpGained: 60, minutes: 30 }

// Backend
characterService.trackMeditation(user, 30);
// Awards: 60 XP, +6 Enlightenment, Meditation skill XP
```

### Submit Credential

```javascript
// Frontend
const formData = new FormData();
formData.append('title', 'AWS Certified Developer');
formData.append('type', 'CERTIFICATION');
formData.append('issuingOrganization', 'Amazon Web Services');
formData.append('issueDate', '2024-01-15');
formData.append('document', fileInput.files[0]);

const result = await apiClient.submitCredential(formData);
// Returns: { success: true, credentialId: 123, status: 'PENDING', potentialXP: 50 }
```

### Cast Spell

```javascript
// Frontend
const result = await apiClient.castSpell(spellId);
// Returns: { success: true, message: "Spell cast successfully" }

// Backend checks:
// - Spell is unlocked
// - Spell is off cooldown
// - User has enough Essence Points
```

## Database Schema

### Character Profile
```sql
CREATE TABLE character_profile (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    character_name VARCHAR(100),
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    enlightenment INTEGER DEFAULT 0,
    wisdom INTEGER DEFAULT 0,
    creativity INTEGER DEFAULT 0,
    harmony INTEGER DEFAULT 0,
    knowledge INTEGER DEFAULT 0,
    essence_points INTEGER DEFAULT 50,
    creation_tokens INTEGER DEFAULT 1
);
```

### Credentials
```sql
CREATE TABLE credential (
    id BIGINT PRIMARY KEY,
    character_profile_id BIGINT,
    title VARCHAR(255),
    type VARCHAR(50),
    issuing_organization VARCHAR(255),
    verification_status VARCHAR(20),
    document_url VARCHAR(500),
    document_hash VARCHAR(64),  -- SHA-256
    experience_bonus INTEGER,
    title_granted VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE
);
```

## Benefits of Credential Verification

| Credential Type | XP Bonus | Example Title | Skill Unlock |
|----------------|----------|---------------|--------------|
| University Degree | 100 | Scholar | Philosophy |
| Certification | 50 | Certified Professional | Engineering |
| License | 75 | Licensed Practitioner | Programming |
| Publication | 80 | Author | Literature |
| Patent | 150 | Inventor | Engineering |
| Award | 40 | Award Recipient | - |
| Language Proficiency | 30 | Polyglot | - |

## Security Considerations

1. **Document Storage**: Files stored in `uploads/credentials/` with UUID filenames
2. **Hash Verification**: SHA-256 hash prevents document tampering
3. **Privacy Control**: Users control public/private visibility
4. **Authentication**: All endpoints require authentication (TODO: implement)
5. **File Validation**: 10MB limit, PDF/image only, content-type checking

## Future Enhancements

- [ ] OAuth2/JWT authentication
- [ ] Admin panel for credential verification
- [ ] Blockchain verification for credentials
- [ ] Real-time XP notifications via WebSocket
- [ ] Achievement system with badges
- [ ] Social features (view other users' public profiles)
- [ ] Quest system tied to credentials
- [ ] Leaderboards for different stats
- [ ] Integration with LinkedIn for auto-credential import
- [ ] Mobile app (React Native + WebXR)

## Development Setup

1. **Build and run backend**:
```bash
cd SanctuaryBeta
mvn clean install
mvn spring-boot:run
```

2. **Access HUD**:
```
http://localhost:8080/hud.html
```

3. **API Documentation**:
```
http://localhost:8080/swagger-ui.html  # (if configured)
```

## Design System Reference

### Color Palette

```css
/* Concrete (Brutalist) */
--concrete-dark: #2a2a2a
--concrete-medium: #3f3f3f
--concrete-light: #9a9a9a

/* Brass (Victorian) */
--brass-dark: #8b5a00
--brass-medium: #b87333
--brass-light: #daa520

/* Accent Colors */
--warning-copper: #cd7f32
--success-brass: #85bb65
```

### Typography

```css
/* Brutalist (Data/Code) */
font-family: 'Courier New', monospace;

/* Victorian (Titles/Descriptions) */
font-family: 'Georgia', serif;

/* Utilitarian (Body) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Grid System

- Base unit: **8px**
- Spacing: 8px, 16px, 24px, 32px
- Container max-width: 1400px
- Grid: 12-column layout

## Credits

**Lead Architect**: Curtis G Kyle Junior
**Project**: Sanctuary VR Metaverse
**Version**: Beta 1.0
**Last Updated**: 2024

## License

Proprietary - All rights reserved

---

**"Bridge the real and virtual. Your accomplishments matter, in every realm."**
