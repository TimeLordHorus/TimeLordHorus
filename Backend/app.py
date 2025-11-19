"""
Sanctuary AI Backend Server
Flask microservice for Text-to-3D generation and content moderation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.getenv('SANCTUARY_API_KEY', 'dev_key_12345')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True') == 'True'


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'error_code': 'MISSING_AUTH'}), 401

        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({'error': 'Invalid API key', 'error_code': 'INVALID_KEY'}), 401

        return f(*args, **kwargs)

    return decorated


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Sanctuary AI Backend'}), 200


# Text-to-3D generation endpoint
@app.route('/api/v1/generate/model', methods=['POST'])
@require_auth
def generate_model():
    """Generate a 3D model from a text prompt"""
    try:
        data = request.json

        # Validate input
        if not data or 'prompt' not in data or 'user_id' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'error_code': 'INVALID_REQUEST'
            }), 400

        prompt = data['prompt']
        user_id = data['user_id']
        quality = data.get('quality', 'medium')
        style = data.get('style', 'realistic')

        # Validate prompt length
        if len(prompt) > 500:
            return jsonify({
                'error': 'Prompt exceeds maximum length of 500 characters',
                'error_code': 'INVALID_PROMPT'
            }), 400

        # TODO: Implement actual Text-to-3D generation
        # from services.text_to_3d import generate_model_shap_e
        # result = generate_model_shap_e(prompt, quality, style)

        # Placeholder response
        response = {
            'status': 'success',
            'model_url': 'https://example.com/models/placeholder.glb',
            'thumbnail_url': 'https://example.com/thumbnails/placeholder.jpg',
            'generation_id': 'gen_placeholder123',
            'estimated_polycount': 5000,
            'created_at': '2025-11-19T12:00:00Z'
        }

        print(f"[API] Model generation request: {prompt} from user {user_id}")

        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Generation failed: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'error_code': 'GENERATION_FAILED',
            'details': str(e)
        }), 500


# Transcription endpoint
@app.route('/api/v1/transcribe/audio', methods=['POST'])
@require_auth
def transcribe_audio():
    """Transcribe audio to text using Whisper API"""
    try:
        # Check if audio file is present
        if 'audio_file' not in request.files:
            return jsonify({
                'error': 'No audio file provided',
                'error_code': 'MISSING_FILE'
            }), 400

        audio_file = request.files['audio_file']
        user_id = request.form.get('user_id')

        # TODO: Implement actual transcription
        # from services.whisper import transcribe
        # result = transcribe(audio_file)

        # Placeholder response
        response = {
            'status': 'success',
            'transcription': 'Sample transcription text',
            'confidence': 0.95,
            'language_detected': 'en',
            'duration_ms': 3000
        }

        print(f"[API] Transcription request from user {user_id}")

        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Transcription failed: {str(e)}")
        return jsonify({
            'error': 'Transcription failed',
            'error_code': 'TRANSCRIPTION_FAILED'
        }), 500


# Content moderation endpoint
@app.route('/api/v1/moderate/content', methods=['POST'])
@require_auth
def moderate_content():
    """Check content for policy violations"""
    try:
        data = request.json

        if not data or 'content' not in data:
            return jsonify({
                'error': 'Missing content field',
                'error_code': 'INVALID_REQUEST'
            }), 400

        content = data['content']
        content_type = data.get('content_type', 'text')

        # TODO: Implement actual moderation
        # from services.moderation import check_content
        # result = check_content(content, content_type)

        # Placeholder response (always safe for development)
        response = {
            'status': 'success',
            'is_safe': True,
            'flags': [],
            'confidence': 0.99
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Moderation failed: {str(e)}")
        return jsonify({
            'error': 'Moderation failed',
            'error_code': 'MODERATION_FAILED'
        }), 500


# User creations endpoint
@app.route('/api/v1/users/<user_id>/creations', methods=['GET'])
@require_auth
def get_user_creations(user_id):
    """Get all models created by a user"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))

        # TODO: Implement actual database query
        # from database import get_creations
        # creations = get_creations(user_id, page, limit)

        # Placeholder response
        response = {
            'status': 'success',
            'creations': [],
            'total_count': 0,
            'page': page,
            'pages_total': 0
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Failed to get creations: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve creations',
            'error_code': 'DATABASE_ERROR'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'error_code': 'NOT_FOUND'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'error_code': 'INTERNAL_ERROR'
    }), 500


if __name__ == '__main__':
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   Sanctuary AI Backend Server         ║
    ║   Running on http://localhost:{PORT}    ║
    ║   Debug Mode: {DEBUG}                      ║
    ╚═══════════════════════════════════════╝
    """)

    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
