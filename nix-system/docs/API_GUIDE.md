# NIX API Developer Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Webhooks](#webhooks)
8. [Code Examples](#code-examples)

## Getting Started

### Base URL
```
Production: https://api.nix.gov/v1
Sandbox: https://sandbox-api.nix.gov/v1
```

### API Versioning
The NIX API uses URL-based versioning. The current version is `v1`.

### Content Type
All requests must use `Content-Type: application/json` unless otherwise specified.

### Required Headers
```http
Authorization: Bearer {access_token}
Content-Type: application/json
X-Request-ID: {unique_request_id}  # Optional but recommended
```

## Authentication

### OAuth 2.0 Authorization Code Flow

**Step 1: Get Authorization Code**
```http
GET /oauth/authorize?
    response_type=code&
    client_id={your_client_id}&
    redirect_uri={your_redirect_uri}&
    scope=read:records write:records&
    state={random_state}
```

**Step 2: Exchange Code for Token**
```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code={authorization_code}&
client_id={your_client_id}&
client_secret={your_client_secret}&
redirect_uri={your_redirect_uri}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def50200abc...",
  "scope": "read:records write:records"
}
```

### Token Refresh
```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token={refresh_token}&
client_id={your_client_id}&
client_secret={your_client_secret}
```

## API Endpoints

### Patient Records

#### Get Patient Information
```http
GET /patients/{patient_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "patient_id": "patient_12345",
  "demographics": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-01-01",
    "gender": "M"
  },
  "contact": {
    "phone_mobile": "+1-555-123-4567",
    "email": "john.doe@example.com"
  }
}
```

#### Get Medical Records
```http
GET /patients/{patient_id}/records?
    start_date=2024-01-01&
    end_date=2024-12-31&
    type=medical_history
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "records": [
    {
      "record_id": "mr_001",
      "record_type": "medical_history",
      "created_at": "2024-03-15T10:30:00Z",
      "updated_at": "2024-03-15T10:30:00Z",
      "content": {
        "diagnosis": "Type 2 Diabetes",
        "icd_code": "E11.9",
        "provider": "Dr. Jane Smith"
      }
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "per_page": 50,
    "total_pages": 1
  }
}
```

#### Create Medical Record
```http
POST /patients/{patient_id}/records
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "record_type": "medical_history",
  "content": {
    "diagnosis": "Hypertension",
    "icd_code": "I10",
    "provider": "dr_smith_001",
    "date": "2024-11-20",
    "notes": "Patient presents with elevated blood pressure"
  }
}
```

**Response:**
```json
{
  "record_id": "mr_002",
  "status": "created",
  "created_at": "2024-11-20T14:22:00Z",
  "provenance_id": "prov_abc123"
}
```

### Prescriptions

#### Get Prescriptions
```http
GET /patients/{patient_id}/prescriptions?status=active
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "prescriptions": [
    {
      "prescription_id": "rx_001",
      "medication_name": "Metformin",
      "dosage": "500mg",
      "frequency": "Twice daily",
      "prescribed_date": "2024-11-15",
      "refills_remaining": 3,
      "prescriber": "Dr. Jane Smith"
    }
  ]
}
```

#### Create Prescription
```http
POST /patients/{patient_id}/prescriptions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "medication_name": "Lisinopril",
  "ndc_code": "0378-0410-93",
  "dosage": "10mg",
  "frequency": "Once daily",
  "quantity": 30,
  "refills": 3,
  "instructions": "Take with food",
  "diagnosis_codes": ["I10"]
}
```

### Consent Management

#### Grant Consent
```http
POST /patients/{patient_id}/consents
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "recipient_id": "hospital_001",
  "recipient_type": "hospital",
  "consent_type": "treatment",
  "data_categories": [
    "medical_records",
    "prescriptions",
    "lab_results"
  ],
  "purpose": "Ongoing treatment for diabetes",
  "duration_days": 365,
  "permissions": {
    "can_view": true,
    "can_copy": true,
    "can_print": false,
    "can_export": false
  }
}
```

**Response:**
```json
{
  "consent_id": "consent_001",
  "status": "active",
  "granted_at": "2024-11-20T15:00:00Z",
  "expiration_date": "2025-11-20T15:00:00Z",
  "signature_required": false
}
```

#### Revoke Consent
```http
POST /consents/{consent_id}/revoke
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "Patient request"
}
```

### Document Sharing

#### Share Document
```http
POST /patients/{patient_id}/share
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "document_id": "mr_001",
  "recipient_id": "specialist_clinic_005",
  "recipient_type": "provider",
  "purpose": "Consultation",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "share_id": "share_001",
  "status": "shared",
  "access_url": "https://api.nix.gov/v1/shared/abc123xyz",
  "access_code": "XYZ-789",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### Document Provenance

#### Get Document Provenance
```http
GET /documents/{document_id}/provenance
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "document_id": "mr_001",
  "creation_date": "2024-01-15T10:00:00Z",
  "provenance_chain": [
    {
      "record_id": "prov_001",
      "timestamp": "2024-01-15T10:00:00Z",
      "action": "created",
      "actor_id": "dr_smith_001",
      "device_id": "patient_phone_001",
      "hash": "abc123..."
    },
    {
      "record_id": "prov_002",
      "timestamp": "2024-03-20T14:30:00Z",
      "action": "copied",
      "actor_id": "patient_12345",
      "source_device": "patient_phone_001",
      "destination_device": "hospital_server_001",
      "hash": "def456..."
    }
  ],
  "current_locations": [
    {
      "device_id": "patient_phone_001",
      "device_type": "client_device"
    },
    {
      "device_id": "hospital_server_001",
      "device_type": "hospital_server"
    }
  ],
  "integrity_verified": true
}
```

### Audit Trail

#### Get Audit Trail
```http
GET /patients/{patient_id}/audit-trail?
    start_date=2024-01-01&
    end_date=2024-12-31&
    event_type=access_phi
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "audit_events": [
    {
      "event_id": "audit_001",
      "timestamp": "2024-11-20T10:30:00Z",
      "event_type": "access_phi",
      "user_id": "dr_smith_001",
      "action": "view_medical_record",
      "resource_id": "mr_001",
      "ip_address": "192.168.1.100",
      "success": true
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "per_page": 50
  }
}
```

### Integration Endpoints

#### Verify Medicare Eligibility
```http
POST /integrations/cms/verify-eligibility
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "medicare_id": "1EG4-TE5-MK73",
  "date_of_service": "2024-11-20"
}
```

**Response:**
```json
{
  "eligible": true,
  "coverage": {
    "part_a": true,
    "part_b": true,
    "part_c": true,
    "part_d": true
  },
  "copay_amount": 25.00,
  "deductible_met": true
}
```

## Data Models

### Patient
```json
{
  "patient_id": "string",
  "demographics": {
    "first_name": "string",
    "last_name": "string",
    "middle_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "gender": "M|F|O|U",
    "ssn": "string (encrypted)"
  },
  "contact": {
    "phone_mobile": "string",
    "phone_home": "string",
    "email": "string",
    "address": {
      "line1": "string",
      "line2": "string",
      "city": "string",
      "state": "string",
      "zip": "string"
    }
  }
}
```

### Medical Record
```json
{
  "record_id": "string",
  "patient_id": "string",
  "record_type": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "content": {
    "diagnosis": "string",
    "icd_code": "string",
    "provider": "string",
    "notes": "string"
  },
  "provenance_id": "string"
}
```

### Prescription
```json
{
  "prescription_id": "string",
  "patient_id": "string",
  "medication_name": "string",
  "ndc_code": "string",
  "dosage": "string",
  "frequency": "string",
  "quantity": "integer",
  "refills_remaining": "integer",
  "prescribed_date": "YYYY-MM-DD",
  "expiry_date": "YYYY-MM-DD",
  "prescriber": "string"
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error context"
    },
    "request_id": "req_123456"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (no consent) |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request validation failed |
| `UNAUTHORIZED` | Missing or invalid authentication |
| `FORBIDDEN` | No consent for operation |
| `NOT_FOUND` | Resource not found |
| `CONSENT_REQUIRED` | Operation requires patient consent |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 956
X-RateLimit-Reset: 1700512800
```

### Rate Limit Tiers

| Tier | Requests/Hour | Concurrent Connections |
|------|---------------|------------------------|
| Free | 100 | 5 |
| Basic | 1,000 | 20 |
| Professional | 10,000 | 100 |
| Enterprise | 100,000 | 500 |

### Handling Rate Limits
```python
import time
import requests

def make_request_with_retry(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        # Get retry-after header
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        return make_request_with_retry(url, headers)

    return response
```

## Webhooks

### Webhook Events

Subscribe to real-time events:

- `consent.granted`
- `consent.revoked`
- `document.shared`
- `record.created`
- `record.updated`
- `prescription.created`
- `emergency.access`

### Webhook Payload
```json
{
  "event_id": "evt_123",
  "event_type": "consent.granted",
  "timestamp": "2024-11-20T15:00:00Z",
  "data": {
    "consent_id": "consent_001",
    "patient_id": "patient_12345",
    "recipient_id": "hospital_001"
  },
  "signature": "sha256_hmac_signature"
}
```

### Webhook Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

## Code Examples

### Python
```python
import requests

# Initialize session
session = requests.Session()
session.headers.update({
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
})

# Get patient records
response = session.get(
    'https://api.nix.gov/v1/patients/patient_12345/records'
)

if response.status_code == 200:
    records = response.json()['records']
    for record in records:
        print(f"Record: {record['record_id']}")
```

### JavaScript
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://api.nix.gov/v1',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

// Get patient records
client.get('/patients/patient_12345/records')
  .then(response => {
    const records = response.data.records;
    records.forEach(record => {
      console.log(`Record: ${record.record_id}`);
    });
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### cURL
```bash
curl -X GET \
  https://api.nix.gov/v1/patients/patient_12345/records \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json'
```

## Best Practices

1. **Always use HTTPS** - Never make API calls over HTTP
2. **Store tokens securely** - Use secure storage for access tokens
3. **Implement retry logic** - Handle transient failures gracefully
4. **Respect rate limits** - Monitor rate limit headers
5. **Verify webhooks** - Always verify webhook signatures
6. **Log request IDs** - Include X-Request-ID for debugging
7. **Handle errors** - Implement proper error handling
8. **Use pagination** - For endpoints that return lists
9. **Keep tokens fresh** - Refresh tokens before they expire
10. **Follow HIPAA guidelines** - Ensure your application is HIPAA compliant

## Support

- **API Documentation**: https://docs.nix.gov/api
- **Developer Portal**: https://developers.nix.gov
- **Support Email**: api-support@nix.gov
- **Status Page**: https://status.nix.gov
