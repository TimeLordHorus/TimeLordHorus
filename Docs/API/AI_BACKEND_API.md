# Sanctuary AI Backend API Documentation

## Overview

The Sanctuary AI Backend is a Python Flask microservice that interfaces between the Unity client and various AI services for generative content creation.

**Base URL**: `http://localhost:5000/api/v1` (development)
**Production URL**: TBD

---

## Authentication

All requests require an API key passed in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Text-to-3D Generation

Generate a 3D model from a text prompt.

**Endpoint**: `POST /generate/model`

**Request Body**:
```json
{
  "prompt": "A marble statue of a weeping angel holding a clock",
  "user_id": "user_12345",
  "quality": "medium",
  "style": "realistic"
}
```

**Parameters**:
- `prompt` (string, required): The text description of the model
- `user_id` (string, required): Unique user identifier
- `quality` (string, optional): "low" | "medium" | "high" (default: "medium")
- `style` (string, optional): "realistic" | "stylized" | "abstract" (default: "realistic")

**Response**:
```json
{
  "status": "success",
  "model_url": "https://cdn.sanctuary.ai/models/abc123.glb",
  "thumbnail_url": "https://cdn.sanctuary.ai/thumbnails/abc123.jpg",
  "generation_id": "gen_xyz789",
  "estimated_polycount": 15000,
  "created_at": "2025-11-19T12:34:56Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid prompt or parameters
- `401`: Unauthorized (invalid API key)
- `429`: Rate limit exceeded
- `500`: Server error

**Example (Unity C#)**:
```csharp
public async Task<ModelResponse> GenerateModel(string prompt, string userId)
{
    var request = new GenerateModelRequest
    {
        prompt = prompt,
        user_id = userId,
        quality = "medium"
    };

    string json = JsonUtility.ToJson(request);
    byte[] bodyRaw = Encoding.UTF8.GetBytes(json);

    var webRequest = new UnityWebRequest($"{API_BASE}/generate/model", "POST");
    webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
    webRequest.downloadHandler = new DownloadHandlerBuffer();
    webRequest.SetRequestHeader("Content-Type", "application/json");
    webRequest.SetRequestHeader("Authorization", $"Bearer {API_KEY}");

    await webRequest.SendWebRequest();

    if (webRequest.result == UnityWebRequest.Result.Success)
    {
        return JsonUtility.FromJson<ModelResponse>(webRequest.downloadHandler.text);
    }

    throw new Exception($"API Error: {webRequest.error}");
}
```

---

### 2. Speech-to-Text

Transcribe voice input to text using Whisper API.

**Endpoint**: `POST /transcribe/audio`

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**: Audio file (WAV, MP3, OGG)

**Form Data**:
```
audio_file: [binary audio data]
user_id: "user_12345"
language: "en" (optional)
```

**Response**:
```json
{
  "status": "success",
  "transcription": "a marble statue of a weeping angel holding a clock",
  "confidence": 0.95,
  "language_detected": "en",
  "duration_ms": 3200
}
```

**Example (Unity C#)**:
```csharp
public async Task<string> TranscribeAudio(byte[] audioData, string userId)
{
    var form = new WWWForm();
    form.AddBinaryData("audio_file", audioData, "recording.wav", "audio/wav");
    form.AddField("user_id", userId);

    var webRequest = UnityWebRequest.Post($"{API_BASE}/transcribe/audio", form);
    webRequest.SetRequestHeader("Authorization", $"Bearer {API_KEY}");

    await webRequest.SendWebRequest();

    if (webRequest.result == UnityWebRequest.Result.Success)
    {
        var response = JsonUtility.FromJson<TranscriptionResponse>(
            webRequest.downloadHandler.text
        );
        return response.transcription;
    }

    throw new Exception($"Transcription failed: {webRequest.error}");
}
```

---

### 3. Model Status Check

Check the status of a model generation request.

**Endpoint**: `GET /generate/status/{generation_id}`

**Response**:
```json
{
  "status": "processing" | "completed" | "failed",
  "progress": 75,
  "model_url": "https://cdn.sanctuary.ai/models/abc123.glb" (if completed),
  "error_message": null (if failed),
  "estimated_completion_seconds": 30
}
```

---

### 4. User Creations List

Retrieve all models created by a user.

**Endpoint**: `GET /users/{user_id}/creations`

**Query Parameters**:
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20, max: 100)

**Response**:
```json
{
  "status": "success",
  "creations": [
    {
      "generation_id": "gen_xyz789",
      "prompt": "A marble statue...",
      "model_url": "https://cdn.sanctuary.ai/models/abc123.glb",
      "thumbnail_url": "https://cdn.sanctuary.ai/thumbnails/abc123.jpg",
      "created_at": "2025-11-19T12:34:56Z",
      "polycount": 15000
    }
  ],
  "total_count": 45,
  "page": 1,
  "pages_total": 3
}
```

---

### 5. Content Moderation

Check if a prompt or generated model violates content policies.

**Endpoint**: `POST /moderate/content`

**Request**:
```json
{
  "content_type": "text" | "model_url",
  "content": "prompt text or model URL",
  "user_id": "user_12345"
}
```

**Response**:
```json
{
  "status": "success",
  "is_safe": true,
  "flags": [],
  "confidence": 0.99
}
```

**Possible Flags**:
- `nsfw_content`
- `hate_symbols`
- `violence`
- `copyright_violation`

---

## Flask Backend Implementation

### Server Setup

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv('SANCTUARY_API_KEY')

def require_auth(f):
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated
```

### Text-to-3D Integration

```python
# services/text_to_3d.py
import requests
from typing import Dict

SHAP_E_API_URL = "https://api.openai.com/v1/text-to-3d"  # Example
MESHY_API_URL = "https://api.meshy.ai/v1/text-to-3d"    # Example

def generate_model_shap_e(prompt: str, quality: str = "medium") -> Dict:
    """Generate 3D model using Shap-E API"""
    headers = {
        "Authorization": f"Bearer {os.getenv('SHAP_E_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "quality": quality,
        "format": "glb"
    }

    response = requests.post(SHAP_E_API_URL, json=payload, headers=headers)
    return response.json()

def generate_model_meshy(prompt: str, style: str = "realistic") -> Dict:
    """Generate 3D model using Meshy API"""
    headers = {
        "Authorization": f"Bearer {os.getenv('MESHY_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "art_style": style,
        "output_format": "glb"
    }

    response = requests.post(MESHY_API_URL, json=payload, headers=headers)
    return response.json()
```

### Main Route

```python
# routes/generate.py
from flask import Blueprint, request, jsonify
from services.text_to_3d import generate_model_shap_e
from database import save_creation
import uuid

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate/model', methods=['POST'])
@require_auth
def generate_model():
    data = request.json

    # Validate input
    if 'prompt' not in data or 'user_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    prompt = data['prompt']
    user_id = data['user_id']
    quality = data.get('quality', 'medium')
    style = data.get('style', 'realistic')

    # Generate unique ID
    generation_id = f"gen_{uuid.uuid4().hex[:12]}"

    # Call AI service
    try:
        result = generate_model_shap_e(prompt, quality)

        # Save to database
        creation_data = {
            'generation_id': generation_id,
            'user_id': user_id,
            'prompt': prompt,
            'model_url': result['model_url'],
            'thumbnail_url': result.get('thumbnail_url'),
            'polycount': result.get('polycount', 0)
        }
        save_creation(creation_data)

        return jsonify({
            'status': 'success',
            'generation_id': generation_id,
            'model_url': result['model_url'],
            'thumbnail_url': result.get('thumbnail_url'),
            'estimated_polycount': result.get('polycount', 0)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Rate Limiting

**Default Limits**:
- 10 model generations per hour per user
- 100 transcriptions per hour per user
- 1000 API calls per hour total

**Headers Included in Response**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1700000000
```

---

## Error Handling

**Standard Error Response**:
```json
{
  "error": "Error message description",
  "error_code": "INVALID_PROMPT",
  "details": {
    "field": "prompt",
    "reason": "Prompt exceeds maximum length of 500 characters"
  }
}
```

**Error Codes**:
- `INVALID_PROMPT`: Prompt validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `MODEL_GENERATION_FAILED`: AI service error
- `UNSUPPORTED_FORMAT`: Invalid file format
- `MODERATION_FAILED`: Content policy violation

---

## Development Setup

### Requirements

```txt
Flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
openai==1.3.0
Pillow==10.1.0
```

### Environment Variables

```env
SANCTUARY_API_KEY=your_api_key_here
SHAP_E_API_KEY=your_shap_e_key
MESHY_API_KEY=your_meshy_key
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:pass@localhost/sanctuary
CDN_BASE_URL=https://cdn.sanctuary.ai
```

### Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Testing

### Postman Collection

Import the [Sanctuary API Postman Collection](../Testing/sanctuary_api.postman_collection.json)

### Example cURL

```bash
curl -X POST http://localhost:5000/api/v1/generate/model \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A crystal tree with glowing leaves",
    "user_id": "test_user_123",
    "quality": "medium"
  }'
```

---

## Future Endpoints

- `POST /generate/texture` - Generate textures for existing models
- `POST /generate/animation` - Create animations from text
- `GET /biomes/{biome_id}/content` - Fetch biome educational content
- `POST /archive/search` - Search connected knowledge repositories
