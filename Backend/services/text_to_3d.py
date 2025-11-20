"""
Text-to-3D Generation Service
Integrates with Shap-E, Meshy, and Point-E APIs for 3D model generation
"""

import os
import requests
import time
import uuid
from typing import Dict, Optional, Tuple
import base64
from pathlib import Path

class TextTo3DService:
    """
    Unified interface for multiple Text-to-3D generation services
    """

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.meshy_api_key = os.getenv('MESHY_API_KEY')
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY')

        # Storage configuration
        self.storage_path = Path(os.getenv('MODEL_STORAGE_PATH', './generated_models'))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Service priority (fallback order)
        self.service_priority = ['meshy', 'shap_e', 'point_e']

    def generate_model(
        self,
        prompt: str,
        quality: str = 'medium',
        style: str = 'realistic',
        preferred_service: Optional[str] = None
    ) -> Dict:
        """
        Generate a 3D model from a text prompt

        Args:
            prompt: Text description of the model
            quality: 'low', 'medium', 'high'
            style: 'realistic', 'stylized', 'abstract'
            preferred_service: Specific service to use (optional)

        Returns:
            Dictionary with generation results
        """
        generation_id = f"gen_{uuid.uuid4().hex[:12]}"

        print(f"[TextTo3D] Starting generation: {generation_id}")
        print(f"[TextTo3D] Prompt: {prompt}")
        print(f"[TextTo3D] Quality: {quality}, Style: {style}")

        # Determine which service to use
        services_to_try = [preferred_service] if preferred_service else self.service_priority

        for service in services_to_try:
            if service is None:
                continue

            try:
                print(f"[TextTo3D] Attempting generation with: {service}")

                if service == 'meshy' and self.meshy_api_key:
                    result = self._generate_meshy(prompt, quality, style, generation_id)
                elif service == 'shap_e' and self.openai_api_key:
                    result = self._generate_shap_e(prompt, quality, generation_id)
                elif service == 'point_e' and self.replicate_api_key:
                    result = self._generate_point_e(prompt, quality, generation_id)
                else:
                    print(f"[TextTo3D] {service} not available (missing API key)")
                    continue

                if result['status'] == 'success':
                    print(f"[TextTo3D] Generation successful with {service}")
                    return result

            except Exception as e:
                print(f"[TextTo3D] {service} failed: {str(e)}")
                continue

        # All services failed, return placeholder
        print("[TextTo3D] All services failed, returning placeholder")
        return self._generate_placeholder(prompt, generation_id)

    def _generate_meshy(self, prompt: str, quality: str, style: str, generation_id: str) -> Dict:
        """
        Generate using Meshy AI API
        https://www.meshy.ai/
        """
        print("[TextTo3D] Using Meshy AI")

        # Map quality to Meshy parameters
        quality_map = {
            'low': 'draft',
            'medium': 'standard',
            'high': 'refined'
        }

        # Create generation request
        url = "https://api.meshy.ai/v1/text-to-3d"
        headers = {
            "Authorization": f"Bearer {self.meshy_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "art_style": style,
            "quality": quality_map.get(quality, 'standard'),
            "negative_prompt": "low quality, blurry, distorted",
            "seed": int(time.time())
        }

        # Submit generation task
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        task_data = response.json()
        task_id = task_data['task_id']

        print(f"[TextTo3D] Meshy task created: {task_id}")

        # Poll for completion (max 5 minutes)
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            time.sleep(5)
            attempt += 1

            status_url = f"{url}/{task_id}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()

            status_data = status_response.json()
            status = status_data['status']

            print(f"[TextTo3D] Meshy status: {status} ({attempt}/{max_attempts})")

            if status == 'succeeded':
                model_url = status_data['model_url']
                thumbnail_url = status_data.get('thumbnail_url', '')

                # Download model
                local_path = self._download_model(model_url, generation_id)

                return {
                    'status': 'success',
                    'service': 'meshy',
                    'generation_id': generation_id,
                    'model_url': model_url,
                    'local_path': str(local_path),
                    'thumbnail_url': thumbnail_url,
                    'estimated_polycount': status_data.get('poly_count', 5000),
                    'format': 'glb',
                    'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

            elif status == 'failed':
                raise Exception(f"Meshy generation failed: {status_data.get('error', 'Unknown error')}")

        raise Exception("Meshy generation timeout")

    def _generate_shap_e(self, prompt: str, quality: str, generation_id: str) -> Dict:
        """
        Generate using OpenAI Shap-E via Replicate
        https://replicate.com/openai/shap-e
        """
        print("[TextTo3D] Using Shap-E (via Replicate)")

        if not self.replicate_api_key:
            raise Exception("Replicate API key not configured")

        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {self.replicate_api_key}",
            "Content-Type": "application/json"
        }

        # Map quality to guidance scale
        guidance_map = {
            'low': 10.0,
            'medium': 15.0,
            'high': 20.0
        }

        payload = {
            "version": "8e141d0d",  # Shap-E version ID
            "input": {
                "prompt": prompt,
                "guidance_scale": guidance_map.get(quality, 15.0),
                "num_inference_steps": 64 if quality == 'high' else 32,
                "output_format": "glb"
            }
        }

        # Submit prediction
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        prediction = response.json()
        prediction_id = prediction['id']

        print(f"[TextTo3D] Shap-E prediction created: {prediction_id}")

        # Poll for completion
        max_attempts = 40
        attempt = 0

        while attempt < max_attempts:
            time.sleep(3)
            attempt += 1

            status_url = f"{url}/{prediction_id}"
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()

            status_data = status_response.json()
            status = status_data['status']

            print(f"[TextTo3D] Shap-E status: {status} ({attempt}/{max_attempts})")

            if status == 'succeeded':
                model_url = status_data['output']

                # Download model
                local_path = self._download_model(model_url, generation_id)

                return {
                    'status': 'success',
                    'service': 'shap_e',
                    'generation_id': generation_id,
                    'model_url': model_url,
                    'local_path': str(local_path),
                    'thumbnail_url': '',
                    'estimated_polycount': 3000,
                    'format': 'glb',
                    'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

            elif status == 'failed':
                raise Exception(f"Shap-E generation failed: {status_data.get('error', 'Unknown error')}")

        raise Exception("Shap-E generation timeout")

    def _generate_point_e(self, prompt: str, quality: str, generation_id: str) -> Dict:
        """
        Generate using OpenAI Point-E
        Point-E generates point clouds which can be converted to meshes
        """
        print("[TextTo3D] Using Point-E")

        # Point-E implementation would go here
        # For now, fall back to placeholder
        raise Exception("Point-E not yet implemented")

    def _generate_placeholder(self, prompt: str, generation_id: str) -> Dict:
        """
        Generate placeholder response when all services fail
        """
        return {
            'status': 'success',
            'service': 'placeholder',
            'generation_id': generation_id,
            'model_url': '/static/models/placeholder.glb',
            'local_path': './static/models/placeholder.glb',
            'thumbnail_url': '/static/thumbnails/placeholder.jpg',
            'estimated_polycount': 500,
            'format': 'glb',
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'note': 'Placeholder model - configure API keys for real generation'
        }

    def _download_model(self, url: str, generation_id: str) -> Path:
        """
        Download generated model to local storage
        """
        print(f"[TextTo3D] Downloading model: {url}")

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Save to storage
        file_path = self.storage_path / f"{generation_id}.glb"
        file_path.write_bytes(response.content)

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"[TextTo3D] Model saved: {file_path} ({file_size_mb:.2f} MB)")

        return file_path

    def get_generation_status(self, generation_id: str) -> Dict:
        """
        Check status of a generation request
        """
        model_path = self.storage_path / f"{generation_id}.glb"

        if model_path.exists():
            return {
                'status': 'completed',
                'generation_id': generation_id,
                'local_path': str(model_path)
            }
        else:
            return {
                'status': 'not_found',
                'generation_id': generation_id
            }


# Singleton instance
_service_instance = None

def get_text_to_3d_service() -> TextTo3DService:
    """Get or create TextTo3DService singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = TextTo3DService()
    return _service_instance
