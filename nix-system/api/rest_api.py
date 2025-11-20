"""
NIX REST API

Secure REST API for healthcare information exchange.
Implements HIPAA-compliant endpoints with OAuth 2.0 authentication.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import hashlib
import secrets


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class APIEndpoint:
    """
    API endpoint definition

    All endpoints require:
    - OAuth 2.0 Bearer token authentication
    - TLS 1.3 encryption
    - Rate limiting
    - Audit logging
    """

    def __init__(self, path: str, method: HTTPMethod,
                 description: str, requires_consent: bool = True):
        self.path = path
        self.method = method
        self.description = description
        self.requires_consent = requires_consent


class NIXAPI:
    """
    NIX REST API implementation

    Base URL: https://api.nix.gov/v1

    Authentication: OAuth 2.0 Bearer Token
    Header: Authorization: Bearer {token}

    Rate Limiting: 1000 requests/hour per entity
    """

    VERSION = "v1"
    BASE_URL = "https://api.nix.gov"

    # Define API endpoints
    ENDPOINTS = {
        # Patient endpoints
        "get_patient": APIEndpoint(
            "/patients/{patient_id}",
            HTTPMethod.GET,
            "Get patient demographics and basic info",
            requires_consent=True
        ),
        "update_patient": APIEndpoint(
            "/patients/{patient_id}",
            HTTPMethod.PUT,
            "Update patient information",
            requires_consent=False  # Patient updating own info
        ),

        # Medical records endpoints
        "get_medical_records": APIEndpoint(
            "/patients/{patient_id}/records",
            HTTPMethod.GET,
            "Get patient medical records",
            requires_consent=True
        ),
        "get_medical_record": APIEndpoint(
            "/patients/{patient_id}/records/{record_id}",
            HTTPMethod.GET,
            "Get specific medical record",
            requires_consent=True
        ),
        "create_medical_record": APIEndpoint(
            "/patients/{patient_id}/records",
            HTTPMethod.POST,
            "Create new medical record",
            requires_consent=True
        ),

        # Prescriptions endpoints
        "get_prescriptions": APIEndpoint(
            "/patients/{patient_id}/prescriptions",
            HTTPMethod.GET,
            "Get patient prescriptions",
            requires_consent=True
        ),
        "create_prescription": APIEndpoint(
            "/patients/{patient_id}/prescriptions",
            HTTPMethod.POST,
            "Create new prescription (provider only)",
            requires_consent=True
        ),
        "fill_prescription": APIEndpoint(
            "/prescriptions/{prescription_id}/fill",
            HTTPMethod.POST,
            "Mark prescription as filled (pharmacy only)",
            requires_consent=True
        ),

        # Diagnoses endpoints
        "get_diagnoses": APIEndpoint(
            "/patients/{patient_id}/diagnoses",
            HTTPMethod.GET,
            "Get patient diagnoses",
            requires_consent=True
        ),
        "create_diagnosis": APIEndpoint(
            "/patients/{patient_id}/diagnoses",
            HTTPMethod.POST,
            "Create new diagnosis (provider only)",
            requires_consent=True
        ),

        # Chart notes endpoints
        "get_chart_notes": APIEndpoint(
            "/patients/{patient_id}/chart-notes",
            HTTPMethod.GET,
            "Get patient chart notes",
            requires_consent=True
        ),
        "create_chart_note": APIEndpoint(
            "/patients/{patient_id}/chart-notes",
            HTTPMethod.POST,
            "Create chart note (provider only)",
            requires_consent=True
        ),

        # Birth certificate endpoints
        "get_birth_certificate": APIEndpoint(
            "/patients/{patient_id}/birth-certificate",
            HTTPMethod.GET,
            "Get patient birth certificate",
            requires_consent=True
        ),

        # Consent endpoints
        "get_consents": APIEndpoint(
            "/patients/{patient_id}/consents",
            HTTPMethod.GET,
            "Get patient consent records",
            requires_consent=False  # Patient viewing own consents
        ),
        "grant_consent": APIEndpoint(
            "/patients/{patient_id}/consents",
            HTTPMethod.POST,
            "Grant new consent",
            requires_consent=False
        ),
        "revoke_consent": APIEndpoint(
            "/consents/{consent_id}/revoke",
            HTTPMethod.POST,
            "Revoke consent",
            requires_consent=False
        ),

        # Document sharing endpoints
        "share_document": APIEndpoint(
            "/patients/{patient_id}/share",
            HTTPMethod.POST,
            "Share document with entity",
            requires_consent=False  # Patient sharing own documents
        ),
        "get_shared_documents": APIEndpoint(
            "/patients/{patient_id}/shared",
            HTTPMethod.GET,
            "Get documents shared with patient",
            requires_consent=False
        ),

        # Integration endpoints
        "register_entity": APIEndpoint(
            "/entities/register",
            HTTPMethod.POST,
            "Register new entity in NIX network",
            requires_consent=False
        ),
        "update_entity": APIEndpoint(
            "/entities/{entity_id}",
            HTTPMethod.PUT,
            "Update entity information",
            requires_consent=False
        ),

        # Provenance endpoints
        "get_document_provenance": APIEndpoint(
            "/documents/{document_id}/provenance",
            HTTPMethod.GET,
            "Get document provenance chain",
            requires_consent=True
        ),
        "get_document_locations": APIEndpoint(
            "/documents/{document_id}/locations",
            HTTPMethod.GET,
            "Get all locations where document exists",
            requires_consent=True
        ),

        # Audit endpoints
        "get_audit_trail": APIEndpoint(
            "/patients/{patient_id}/audit-trail",
            HTTPMethod.GET,
            "Get patient data access audit trail",
            requires_consent=False  # Patient viewing own audit trail
        ),

        # Emergency access
        "emergency_access": APIEndpoint(
            "/patients/{patient_id}/emergency-access",
            HTTPMethod.POST,
            "Request emergency break-glass access",
            requires_consent=False  # Emergency override
        )
    }

    def __init__(self):
        """Initialize NIX API"""
        self.rate_limiter = {}  # entity_id -> request counts
        self.api_keys = {}  # api_key -> entity_id

    def authenticate_request(self, bearer_token: str) -> Optional[str]:
        """
        Authenticate API request

        Args:
            bearer_token: OAuth 2.0 bearer token

        Returns:
            Entity ID if authenticated, None otherwise
        """
        # In production, validate JWT token
        # Verify signature, expiration, issuer, etc.

        # For demonstration, simple lookup
        return self.api_keys.get(bearer_token)

    def generate_api_key(self, entity_id: str) -> str:
        """
        Generate API key for entity

        Args:
            entity_id: Entity ID

        Returns:
            API key
        """
        api_key = secrets.token_urlsafe(32)
        self.api_keys[api_key] = entity_id
        return api_key

    def check_rate_limit(self, entity_id: str) -> bool:
        """
        Check if entity has exceeded rate limit

        Args:
            entity_id: Entity ID

        Returns:
            True if within rate limit
        """
        # Simplified rate limiting
        # In production, use Redis or similar for distributed rate limiting
        current_hour = datetime.now().hour
        key = f"{entity_id}:{current_hour}"

        if key not in self.rate_limiter:
            self.rate_limiter[key] = 0

        self.rate_limiter[key] += 1

        return self.rate_limiter[key] <= 1000  # 1000 requests/hour

    def handle_request(self,
                      endpoint_name: str,
                      bearer_token: str,
                      path_params: Dict[str, str],
                      query_params: Optional[Dict[str, str]] = None,
                      body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle API request

        Args:
            endpoint_name: Name of endpoint
            bearer_token: Bearer token
            path_params: Path parameters
            query_params: Query parameters
            body: Request body

        Returns:
            API response
        """
        # 1. Authenticate
        entity_id = self.authenticate_request(bearer_token)
        if not entity_id:
            return {
                "error": "Unauthorized",
                "message": "Invalid or missing bearer token",
                "status_code": 401
            }

        # 2. Check rate limit
        if not self.check_rate_limit(entity_id):
            return {
                "error": "Rate Limit Exceeded",
                "message": "Maximum 1000 requests per hour",
                "status_code": 429
            }

        # 3. Get endpoint
        endpoint = self.ENDPOINTS.get(endpoint_name)
        if not endpoint:
            return {
                "error": "Not Found",
                "message": f"Endpoint {endpoint_name} not found",
                "status_code": 404
            }

        # 4. Verify consent if required
        if endpoint.requires_consent:
            patient_id = path_params.get("patient_id")
            if not self._verify_consent(entity_id, patient_id):
                return {
                    "error": "Forbidden",
                    "message": "No valid consent for this operation",
                    "status_code": 403
                }

        # 5. Log to audit trail
        self._audit_log(entity_id, endpoint_name, path_params)

        # 6. Process request
        return self._process_endpoint(endpoint_name, entity_id, path_params, query_params, body)

    def _verify_consent(self, entity_id: str, patient_id: str) -> bool:
        """Verify consent for access"""
        # In production, check consent database
        return True

    def _audit_log(self, entity_id: str, endpoint: str, params: Dict[str, str]):
        """Log request to audit trail"""
        # In production, log to HIPAA audit system
        pass

    def _process_endpoint(self,
                         endpoint_name: str,
                         entity_id: str,
                         path_params: Dict[str, str],
                         query_params: Optional[Dict[str, str]],
                         body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process specific endpoint request"""
        # Endpoint-specific logic would go here
        # This would integrate with storage, consent, provenance, etc.

        return {
            "status": "success",
            "endpoint": endpoint_name,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_api_documentation(self) -> Dict[str, Any]:
        """
        Generate API documentation

        Returns:
            OpenAPI/Swagger specification
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "NIX API",
                "version": self.VERSION,
                "description": "National Information Exchange API for Healthcare Data"
            },
            "servers": [
                {
                    "url": f"{self.BASE_URL}/{self.VERSION}",
                    "description": "Production server"
                }
            ],
            "security": [
                {
                    "BearerAuth": []
                }
            ],
            "paths": {}
        }

        # Add endpoint definitions
        for name, endpoint in self.ENDPOINTS.items():
            spec["paths"][endpoint.path] = {
                endpoint.method.value.lower(): {
                    "summary": endpoint.description,
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "429": {"description": "Rate Limit Exceeded"}
                    }
                }
            }

        return spec


# Example usage
if __name__ == "__main__":
    api = NIXAPI()

    # Generate API key for hospital
    api_key = api.generate_api_key("hospital_001")
    print(f"API Key generated: {api_key}")

    # Handle request
    response = api.handle_request(
        endpoint_name="get_medical_records",
        bearer_token=api_key,
        path_params={"patient_id": "patient_12345"}
    )

    print(f"Response: {response}")

    # Get API documentation
    docs = api.get_api_documentation()
    print(f"\nAPI Documentation: {len(docs['paths'])} endpoints")
