# Sanctuary VR - Beta (Progressive Web App)

**Java Spring Boot + WebXR Implementation**

A browser-based VR metaverse accessible via Meta Quest 3 Browser, Firefox Reality, and PCVR browsers.

**Lead Architect:** Curtis G Kyle Junior

---

## Overview

This is the **Beta PWA version** of Sanctuary, built with:
- **Backend**: Java 17 + Spring Boot 3.2
- **Frontend**: WebXR + Three.js
- **Database**: H2 (dev) / PostgreSQL (production)
- **Deployment**: Docker + Docker Compose

This version serves as a proof-of-concept and can later be converted to Unity/Unreal Engine for enhanced VR capabilities.

---

## Features

### Implemented
- ✅ WebXR VR support (Quest 3 browser compatible)
- ✅ Medusa jellyfish avatar with bioluminescent effects
- ✅ Central Hub with floating platforms
- ✅ AI model generation API (backend ready)
- ✅ Progressive Web App (offline capability)
- ✅ REST API with Spring Boot
- ✅ Protected Biomes framework
- ✅ Creation manager for 3D objects

### Coming Soon
- 🔲 Multiplayer WebSocket synchronization
- 🔲 Age verification system
- 🔲 Real AI integration (Text-to-3D)
- 🔲 Voice input (Whisper API)
- 🔲 Advanced biome content
- 🔲 Mobile optimization

---

## Quick Start

### Prerequisites
- Java 17 or higher
- Maven 3.6+
- Docker & Docker Compose (optional)

### Running Locally

```bash
# Clone the repository
cd SanctuaryBeta

# Build with Maven
mvn clean package

# Run the application
java -jar target/sanctuary-beta-0.1.0-BETA.jar

# Or use Maven directly
mvn spring-boot:run
```

The application will start on **http://localhost:8080**

### Access the VR Experience

**On PC:**
1. Open Chrome/Firefox
2. Navigate to `http://localhost:8080`
3. Click "Enter VR" button
4. Use a VR headset or XR emulator

**On Meta Quest 3:**
1. Open Quest Browser
2. Navigate to your server IP (e.g., `http://192.168.1.100:8080`)
3. Click "Enter VR"
4. Experience in native VR!

---

## Docker Deployment

```bash
# Build and run with Docker Compose
cd docker
docker-compose up -d

# View logs
docker-compose logs -f sanctuary-app

# Stop services
docker-compose down
```

Services:
- **sanctuary-app**: Main Spring Boot app (port 8080)
- **sanctuary-db**: PostgreSQL database (port 5432)
- **sanctuary-ai**: Python AI backend (port 5000)

---

## Project Structure

```
SanctuaryBeta/
├── src/
│   ├── main/
│   │   ├── java/com/sanctuary/
│   │   │   ├── model/              # JPA entities
│   │   │   ├── repository/         # Data repositories
│   │   │   ├── service/            # Business logic
│   │   │   ├── controller/         # REST controllers
│   │   │   ├── config/             # Configuration
│   │   │   └── dto/                # Data transfer objects
│   │   └── resources/
│   │       ├── static/             # WebXR frontend
│   │       │   ├── js/             # Three.js code
│   │       │   ├── css/            # Styles
│   │       │   ├── models/         # 3D assets
│   │       │   └── manifest.json   # PWA manifest
│   │       └── application.yml     # Spring config
│   └── test/                       # Unit tests
├── docker/                         # Docker configs
├── docs/                           # Documentation
├── pom.xml                         # Maven dependencies
├── Dockerfile                      # Production build
└── README.md                       # This file
```

---

## API Endpoints

### Health & Info
- `GET /api/v1/health` - Health check
- `GET /api/v1/info` - Service information

### Creations
- `POST /api/v1/creations/generate` - Generate 3D model
- `GET /api/v1/creations/my-creations` - Get user's creations
- `GET /api/v1/creations/public` - Get public creations
- `GET /api/v1/creations/{id}` - Get specific creation

### Documentation
- Swagger UI: `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON: `http://localhost:8080/api-docs`

---

## Development

### Run in Development Mode

```bash
# With auto-reload
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Run tests
mvn test

# Package without tests
mvn package -DskipTests
```

### Frontend Development

The WebXR frontend is located in `src/main/resources/static/`

Edit files directly - Spring Boot DevTools will auto-reload.

### Database

**Development (H2):**
- Console: `http://localhost:8080/h2-console`
- URL: `jdbc:h2:mem:sanctuarydb`
- Username: `sa`
- Password: (empty)

**Production (PostgreSQL):**
- Configured via `application.yml` profile

---

## Configuration

Edit `src/main/resources/application.yml`:

```yaml
sanctuary:
  ai:
    text-to-3d:
      api-url: http://your-ai-service:5000
      api-key: your_api_key

  security:
    jwt:
      secret: your_jwt_secret

  storage:
    type: local  # or s3, cloudinary
```

---

## Progressive Web App

The app includes:
- **Manifest**: `/manifest.json` for installability
- **Service Worker**: `/service-worker.js` for offline caching
- **Icons**: `/icons/` for home screen

To install on mobile:
1. Visit the site in Chrome/Safari
2. Click "Add to Home Screen"
3. Launch as standalone app

---

## Converting to Unity/Unreal

See [docs/CONVERSION_GUIDE.md](docs/CONVERSION_GUIDE.md) for detailed instructions on converting this WebXR prototype to:
- Unity with XR Interaction Toolkit
- Unreal Engine 5 with VR templates
- Native Quest applications

---

## Performance Optimization

### WebXR Performance Tips
- Enable fixed foveated rendering
- Reduce draw calls (combine meshes)
- Use LOD (Level of Detail) groups
- Compress textures
- Limit active lights

### Spring Boot Optimization
- Enable caching
- Use connection pooling
- Async processing for AI calls
- CDN for static assets

---

## Testing

### Manual Testing
1. Open in desktop browser
2. Test API endpoints with Swagger UI
3. Test VR mode with XR emulator
4. Test on actual Quest 3 device

### Automated Testing
```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=CreationServiceTest
```

---

## Troubleshooting

### WebXR not working
- Ensure HTTPS (or localhost)
- Check browser WebXR support
- Enable VR mode in browser flags

### Can't connect from Quest
- Check firewall rules
- Ensure Quest and server on same network
- Use IP address instead of localhost

### Build failures
- Check Java version: `java -version`
- Clear Maven cache: `mvn clean`
- Update dependencies: `mvn clean install -U`

---

## Contributing

This is a beta prototype. For production deployment:
1. Change JWT secret
2. Setup HTTPS/SSL
3. Configure production database
4. Enable CORS properly
5. Implement rate limiting

---

## License

Part of the Sanctuary VR Metaverse project.
All rights reserved to Curtis G Kyle Junior and contributors.

---

## Resources

- [Three.js Documentation](https://threejs.org/docs/)
- [WebXR Device API](https://immersiveweb.dev/)
- [Spring Boot Docs](https://spring.io/projects/spring-boot)
- [Meta Quest Browser](https://www.meta.com/quest/quest-browser/)

---

## Support

For issues and questions:
- Open GitHub Issue
- Contact: Curtis G Kyle Junior

---

**Sanctuary** - Where creation meets consciousness in VR.
