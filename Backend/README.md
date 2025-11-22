# Sanctuary AI Backend

Flask microservice for Sanctuary VR platform, handling Text-to-3D generation, speech transcription, and content moderation.

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

### Running the Server

```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The server will start on `http://localhost:5000`

## API Endpoints

See full documentation: [../Docs/API/AI_BACKEND_API.md](../Docs/API/AI_BACKEND_API.md)

### Health Check
```
GET /health
```

### Generate 3D Model
```
POST /api/v1/generate/model
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "prompt": "A crystal tree",
  "user_id": "user123",
  "quality": "medium",
  "style": "realistic"
}
```

### Transcribe Audio
```
POST /api/v1/transcribe/audio
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data

Form Data:
- audio_file: [WAV/MP3 file]
- user_id: "user123"
```

### Moderate Content
```
POST /api/v1/moderate/content
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "content_type": "text",
  "content": "Text to check",
  "user_id": "user123"
}
```

## Testing

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test model generation
curl -X POST http://localhost:5000/api/v1/generate/model \
  -H "Authorization: Bearer dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cube", "user_id": "test"}'
```

## Project Structure

```
Backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── services/           # Service modules
│   ├── text_to_3d.py   # Text-to-3D integration
│   ├── whisper.py      # Speech transcription
│   └── moderation.py   # Content moderation
└── database/           # Database utilities
```

## Next Steps

1. Implement actual Text-to-3D integration in `services/text_to_3d.py`
2. Set up database (PostgreSQL or MongoDB)
3. Add authentication/user management
4. Implement rate limiting
5. Set up CDN for model hosting

## License

Part of the Sanctuary VR project.
