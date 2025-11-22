"""
Whisper Voice-to-Text Service
Transcribes audio to text using OpenAI Whisper API
"""

import os
import requests
import tempfile
from pathlib import Path
from typing import Dict, Optional
import time

class WhisperService:
    """
    Service for transcribing audio to text using OpenAI Whisper
    """

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
        self.model = "whisper-1"

        # Supported audio formats
        self.supported_formats = [
            'mp3', 'mp4', 'mpeg', 'mpga',
            'm4a', 'wav', 'webm', 'ogg', 'flac'
        ]

        # Max file size (25MB for Whisper API)
        self.max_file_size = 25 * 1024 * 1024

    def transcribe(
        self,
        audio_file,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> Dict:
        """
        Transcribe audio file to text

        Args:
            audio_file: File object or path to audio file
            language: ISO-639-1 language code (optional, auto-detected if not provided)
            prompt: Optional text to guide the model's style
            temperature: Sampling temperature (0-1)

        Returns:
            Dictionary with transcription results
        """
        if not self.api_key:
            print("[Whisper] OpenAI API key not configured, using placeholder")
            return self._placeholder_transcription()

        try:
            start_time = time.time()

            # Handle file input
            if isinstance(audio_file, str) or isinstance(audio_file, Path):
                # File path provided
                with open(audio_file, 'rb') as f:
                    file_content = f.read()
                    filename = Path(audio_file).name
            else:
                # File object provided (from Flask request)
                file_content = audio_file.read()
                filename = audio_file.filename

            # Validate file size
            file_size = len(file_content)
            if file_size > self.max_file_size:
                return {
                    'status': 'error',
                    'error': f'File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum (25 MB)',
                    'error_code': 'FILE_TOO_LARGE'
                }

            # Validate file format
            file_ext = filename.split('.')[-1].lower()
            if file_ext not in self.supported_formats:
                return {
                    'status': 'error',
                    'error': f'Unsupported audio format: {file_ext}',
                    'error_code': 'UNSUPPORTED_FORMAT',
                    'supported_formats': self.supported_formats
                }

            print(f"[Whisper] Transcribing audio: {filename} ({file_size / 1024:.2f} KB)")

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            files = {
                "file": (filename, file_content, f"audio/{file_ext}")
            }

            data = {
                "model": self.model,
                "response_format": "verbose_json",
                "temperature": temperature
            }

            if language:
                data["language"] = language

            if prompt:
                data["prompt"] = prompt

            # Call Whisper API
            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            elapsed_time = time.time() - start_time
            audio_duration = result.get('duration', 0)

            print(f"[Whisper] Transcription complete in {elapsed_time:.2f}s (audio: {audio_duration:.2f}s)")

            return {
                'status': 'success',
                'transcription': result.get('text', ''),
                'language_detected': result.get('language', 'unknown'),
                'duration_seconds': audio_duration,
                'confidence': self._estimate_confidence(result),
                'segments': result.get('segments', []),
                'processing_time_seconds': elapsed_time
            }

        except requests.exceptions.RequestException as e:
            print(f"[Whisper] API request failed: {str(e)}")
            return {
                'status': 'error',
                'error': f'Whisper API request failed: {str(e)}',
                'error_code': 'API_ERROR'
            }

        except Exception as e:
            print(f"[Whisper] Transcription failed: {str(e)}")
            return {
                'status': 'error',
                'error': f'Transcription failed: {str(e)}',
                'error_code': 'TRANSCRIPTION_FAILED'
            }

    def transcribe_with_timestamps(
        self,
        audio_file,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio with word-level timestamps

        Args:
            audio_file: File object or path
            language: ISO-639-1 language code

        Returns:
            Dictionary with transcription and timestamps
        """
        result = self.transcribe(audio_file, language=language)

        if result['status'] != 'success':
            return result

        # Extract segments with timestamps
        segments = result.get('segments', [])
        timestamped_words = []

        for segment in segments:
            timestamped_words.append({
                'text': segment.get('text', ''),
                'start': segment.get('start', 0.0),
                'end': segment.get('end', 0.0),
                'confidence': segment.get('confidence', 0.0)
            })

        result['timestamped_segments'] = timestamped_words
        return result

    def _estimate_confidence(self, whisper_result: Dict) -> float:
        """
        Estimate overall confidence from Whisper result

        Whisper doesn't provide direct confidence scores,
        so we estimate based on segment data and other factors
        """
        segments = whisper_result.get('segments', [])

        if not segments:
            return 0.95  # Default high confidence

        # Average segment probabilities if available
        probs = [seg.get('avg_logprob', 0.0) for seg in segments]

        if not probs:
            return 0.95

        # Convert log probabilities to confidence (rough estimate)
        # Typical range: -1.0 to 0.0, with higher being better
        avg_logprob = sum(probs) / len(probs)
        confidence = max(0.0, min(1.0, (avg_logprob + 1.0)))

        return round(confidence, 3)

    def _placeholder_transcription(self) -> Dict:
        """
        Return placeholder transcription when API key is not configured
        """
        return {
            'status': 'success',
            'transcription': 'Sample transcription text (configure OPENAI_API_KEY for real transcription)',
            'language_detected': 'en',
            'duration_seconds': 3.0,
            'confidence': 0.95,
            'segments': [],
            'processing_time_seconds': 0.1,
            'note': 'Placeholder - configure OpenAI API key for real transcription'
        }

    def translate_to_english(self, audio_file) -> Dict:
        """
        Transcribe and translate non-English audio to English

        Args:
            audio_file: File object or path

        Returns:
            Dictionary with English translation
        """
        if not self.api_key:
            return self._placeholder_transcription()

        try:
            # Handle file input
            if isinstance(audio_file, str) or isinstance(audio_file, Path):
                with open(audio_file, 'rb') as f:
                    file_content = f.read()
                    filename = Path(audio_file).name
            else:
                file_content = audio_file.read()
                filename = audio_file.filename

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            files = {
                "file": (filename, file_content)
            }

            data = {
                "model": self.model,
                "response_format": "json"
            }

            # Use translation endpoint
            translation_url = "https://api.openai.com/v1/audio/translations"

            response = requests.post(
                translation_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            return {
                'status': 'success',
                'translation': result.get('text', ''),
                'target_language': 'en'
            }

        except Exception as e:
            print(f"[Whisper] Translation failed: {str(e)}")
            return {
                'status': 'error',
                'error': f'Translation failed: {str(e)}',
                'error_code': 'TRANSLATION_FAILED'
            }


# Singleton instance
_whisper_instance = None

def get_whisper_service() -> WhisperService:
    """Get or create WhisperService singleton"""
    global _whisper_instance
    if _whisper_instance is None:
        _whisper_instance = WhisperService()
    return _whisper_instance
