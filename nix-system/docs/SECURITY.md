# NIX System Security Documentation

## Table of Contents
1. [Security Overview](#security-overview)
2. [HIPAA Compliance](#hipaa-compliance)
3. [Encryption](#encryption)
4. [Authentication & Authorization](#authentication--authorization)
5. [Network Security](#network-security)
6. [Audit Logging](#audit-logging)
7. [Incident Response](#incident-response)
8. [Security Best Practices](#security-best-practices)

## Security Overview

The NIX system implements defense-in-depth security with multiple layers of protection for Protected Health Information (PHI) and Personally Identifiable Information (PII).

### Security Architecture Layers

1. **Network Layer**: TLS 1.3, firewall rules, DDoS protection
2. **Application Layer**: Input validation, rate limiting, WAF
3. **Authentication Layer**: OAuth 2.0, MFA, biometric authentication
4. **Authorization Layer**: RBAC, consent-based access control
5. **Data Layer**: AES-256 encryption at rest, encrypted backups
6. **Audit Layer**: Comprehensive logging, SIEM integration

## HIPAA Compliance

### Privacy Rule (45 CFR § 164.502)

The NIX system enforces HIPAA Privacy Rule requirements:

#### Minimum Necessary Standard
```python
# Only requested data types are retrieved
def get_patient_data(patient_id, requester_id, data_types, purpose):
    # Verify consent
    if not verify_consent(patient_id, requester_id, data_types):
        raise UnauthorizedAccess("No consent for requested data")

    # Return only minimum necessary data
    return retrieve_data(patient_id, data_types, purpose)
```

#### Individual Rights
- Right to access PHI
- Right to request amendments
- Right to accounting of disclosures
- Right to request restrictions
- Right to confidential communications

### Security Rule (45 CFR § 164.306)

#### Administrative Safeguards

**§ 164.308(a)(1) - Security Management Process**
- Risk analysis conducted quarterly
- Risk management procedures documented
- Sanction policy enforced
- Information system activity review via audit logs

**§ 164.308(a)(3) - Workforce Security**
- Authorization and supervision procedures
- Workforce clearance procedures
- Termination procedures (access revocation)

**§ 164.308(a)(4) - Information Access Management**
- Access authorization policies
- Access establishment and modification procedures
- Role-based access control (RBAC)

**§ 164.308(a)(5) - Security Awareness and Training**
- Security reminders
- Protection from malicious software
- Log-in monitoring
- Password management

**§ 164.308(a)(6) - Security Incident Procedures**
- Incident response plan
- Breach notification procedures (see [Incident Response](#incident-response))

**§ 164.308(a)(7) - Contingency Plan**
- Data backup plan (encrypted backups)
- Disaster recovery plan
- Emergency mode operation plan
- Testing and revision procedures

**§ 164.308(a)(8) - Evaluation**
- Annual security evaluation
- Compliance audits

#### Physical Safeguards

**§ 164.310(a) - Facility Access Controls**
- Facility security plan
- Access control and validation procedures
- Contingency operations

**§ 164.310(d) - Device and Media Controls**
- Disposal procedures (secure deletion)
- Media re-use procedures (cryptographic erasure)
- Accountability (asset inventory)
- Data backup and storage

#### Technical Safeguards

**§ 164.312(a) - Access Control**
- Unique user identification (UUID)
- Emergency access procedures (break-glass)
- Automatic logoff (30 minutes inactivity)
- Encryption and decryption (AES-256-GCM)

**§ 164.312(b) - Audit Controls**
- Comprehensive audit logging (see [Audit Logging](#audit-logging))

**§ 164.312(c) - Integrity**
- Cryptographic integrity checks (SHA-256)
- Document provenance tracking
- Blockchain-based audit trail

**§ 164.312(d) - Person or Entity Authentication**
- Multi-factor authentication (MFA)
- Biometric authentication support
- OAuth 2.0 / OpenID Connect

**§ 164.312(e) - Transmission Security**
- TLS 1.3 for data in transit
- VPN for remote access
- Encrypted messaging

### Breach Notification Rule (45 CFR § 164.400)

#### Breach Detection
```python
def detect_breach(event_type, affected_patients, data_compromised):
    """Automated breach detection"""
    audit_logger.log_breach_detection(
        description=event_type,
        affected_patients=affected_patients,
        data_compromised=data_compromised
    )

    # Immediate notification to security team
    notify_security_team(event_type)

    # If breach affects 500+ individuals
    if len(affected_patients) >= 500:
        notify_hhs_immediately()
        notify_media()
```

#### Notification Timeline
- **60 days**: Notify affected individuals
- **60 days**: Notify HHS if 500+ individuals affected
- **Annual**: Report to HHS if fewer than 500 individuals

## Encryption

### Data at Rest

**AES-256-GCM Encryption**
```python
from nix_system.security.encryption.aes_encryption import AESEncryption

# Initialize with master key
aes = AESEncryption(master_key)

# Encrypt PHI
ciphertext, iv, auth_tag = aes.encrypt(phi_data)

# Decrypt PHI
plaintext = aes.decrypt(ciphertext, iv, auth_tag)
```

**Key Features:**
- AES-256-GCM authenticated encryption
- Unique IV for each encryption operation
- Authentication tags for integrity verification
- Key rotation every 90 days

### Data in Transit

**TLS 1.3 Configuration**
```nginx
ssl_protocols TLSv1.3;
ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### Key Management

**Master Key Storage:**
- AWS KMS (production)
- HashiCorp Vault (alternative)
- Hardware Security Module (HSM) for highest security

**Key Rotation:**
```bash
# Rotate encryption keys every 90 days
python manage.py rotate_encryption_keys

# Re-encrypt data with new key
python manage.py re_encrypt_database --old-key-id key_001 --new-key-id key_002
```

## Authentication & Authorization

### Multi-Factor Authentication (MFA)

**Required for:**
- All administrative access
- Emergency break-glass access
- PHI access by providers
- Account recovery

**Supported Methods:**
1. Time-based One-Time Password (TOTP)
2. SMS codes (fallback)
3. Biometric authentication
4. Hardware security keys (FIDO2/WebAuthn)

### OAuth 2.0 Flow

```
┌──────────┐                                           ┌───────────┐
│  Client  │                                           │   NIX     │
│          │──────(1) Authorization Request───────────>│  Server   │
│          │                                           │           │
│          │<─────(2) Authorization Grant──────────────│           │
│          │                                           │           │
│          │──────(3) Authorization Grant─────────────>│   Token   │
│          │                                           │  Endpoint │
│          │<─────(4) Access Token─────────────────────│           │
│          │                                           │           │
│          │──────(5) Access Token────────────────────>│ Resource  │
│          │                                           │  Server   │
│          │<─────(6) Protected Resource───────────────│           │
└──────────┘                                           └───────────┘
```

### Role-Based Access Control (RBAC)

**Roles:**
- `patient`: Can view own data, grant consent, revoke consent
- `provider`: Can view patient data (with consent), create records
- `admin_staff`: Can manage appointments, billing
- `system_admin`: Can configure system, manage users
- `security_admin`: Can view audit logs, manage security
- `emergency_access`: Can access data in emergencies (logged)

**Permissions Matrix:**
| Role | View PHI | Create PHI | Modify PHI | Delete PHI | Grant Access | Audit Logs |
|------|----------|------------|------------|------------|--------------|------------|
| Patient | Own | Own | Own | Own | Yes | Own |
| Provider | With Consent | Yes | With Consent | No | No | No |
| Admin Staff | Limited | Limited | No | No | No | No |
| System Admin | No | No | No | No | No | Yes |
| Security Admin | Audit Only | No | No | No | No | Yes |

## Network Security

### Firewall Rules

**Inbound Rules:**
```bash
# Allow HTTPS only
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow SSH from specific IP ranges (management network)
iptables -A INPUT -p tcp --dport 22 -s 10.0.1.0/24 -j ACCEPT

# Drop all other inbound traffic
iptables -A INPUT -j DROP
```

**Outbound Rules:**
```bash
# Allow outbound HTTPS (for API calls to external systems)
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

# Allow DNS
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT

# Drop all other outbound traffic
iptables -A OUTPUT -j DROP
```

### Rate Limiting

**Rate Limit Tiers:**
```python
from nix_system.security.firewall.rate_limiter import RateLimitTier

# Basic tier: 1,000 requests/hour
limiter.set_entity_tier("hospital_001", RateLimitTier.BASIC)

# Enterprise tier: 100,000 requests/hour
limiter.set_entity_tier("cms_integration", RateLimitTier.ENTERPRISE)

# Emergency tier: Unlimited (for emergencies only)
limiter.set_entity_tier("emergency_services", RateLimitTier.EMERGENCY)
```

### DDoS Protection

**Automatic IP Blocking:**
- 100+ requests in 10 seconds: Temporary block (1 hour)
- 500+ requests in 60 seconds: Extended block (24 hours)
- Repeated violations: Permanent block (manual review required)

### Web Application Firewall (WAF)

**Protected Against:**
- SQL injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- XML External Entity (XXE)
- Server-Side Request Forgery (SSRF)
- Path traversal
- Command injection

## Audit Logging

### What is Logged

**All PHI Access:**
```python
audit_logger.log_phi_access(
    user_id="dr_smith_001",
    patient_id="patient_12345",
    resource_type="medical_record",
    resource_id="mr_67890",
    action="view",
    ip_address="192.168.1.100",
    purpose="treatment"
)
```

**Security Events:**
- Login attempts (success and failure)
- Password changes
- MFA enrollment/removal
- Permission changes
- Emergency break-glass access
- Consent grants/revocations
- Data exports
- System configuration changes

### Audit Log Retention

**Retention Period:** 7 years (2,555 days) per HIPAA requirements

**Storage:**
- Encrypted at rest
- Write-once, read-many (WORM) storage
- Tamper-evident (cryptographic hashing)
- Regular integrity verification

### Audit Log Format

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-11-20T10:30:45.123Z",
  "event_type": "access_phi",
  "severity": "info",
  "user_id": "dr_smith_001",
  "action": "view_medical_record",
  "resource_type": "medical_record",
  "resource_id": "mr_67890",
  "patient_id": "patient_12345",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "integrity_hash": "a3f5b9c2d1e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2"
}
```

## Incident Response

### Incident Response Team
- **CISO**: Chief Information Security Officer
- **Privacy Officer**: HIPAA Privacy Officer
- **IT Security**: Security engineers
- **Legal**: Legal counsel
- **Communications**: Public relations

### Incident Response Procedure

1. **Detection**: Automated monitoring + manual reporting
2. **Containment**: Isolate affected systems
3. **Investigation**: Determine scope and cause
4. **Notification**: Notify affected parties per HIPAA requirements
5. **Remediation**: Fix vulnerabilities, restore systems
6. **Documentation**: Document incident and lessons learned
7. **Post-Incident Review**: Update procedures

### Breach Notification Workflow

```python
def handle_potential_breach(incident_details):
    # 1. Assess risk
    risk_assessment = assess_breach_risk(incident_details)

    if risk_assessment['is_breach']:
        # 2. Document breach
        breach_id = document_breach(incident_details, risk_assessment)

        # 3. Notify affected individuals (within 60 days)
        notify_affected_individuals(breach_id)

        # 4. Notify HHS if 500+ individuals
        if risk_assessment['affected_count'] >= 500:
            notify_hhs(breach_id)
            notify_media(breach_id)

        # 5. Notify business associates
        notify_business_associates(breach_id)

        # 6. Document all notifications
        document_notifications(breach_id)
```

## Security Best Practices

### For Developers

1. **Never log PHI in application logs**
2. **Use parameterized queries** (prevent SQL injection)
3. **Validate all inputs** (server-side validation)
4. **Implement least privilege** (minimum permissions)
5. **Keep dependencies updated** (security patches)
6. **Perform code reviews** (security-focused)
7. **Use static analysis tools** (Bandit, SonarQube)

### For System Administrators

1. **Regular security updates** (monthly patch cycle)
2. **Strong password policy** (12+ characters, complexity)
3. **Disable unused services** (reduce attack surface)
4. **Regular backups** (encrypted, tested monthly)
5. **Monitor audit logs** (daily review)
6. **Incident response drills** (quarterly)
7. **Security awareness training** (annual)

### For Users

1. **Use strong, unique passwords**
2. **Enable MFA** (required)
3. **Don't share credentials**
4. **Report suspicious activity**
5. **Lock workstation when away**
6. **Verify recipient before sharing PHI**
7. **Complete security training**

## Security Contacts

**Security Team:** security@nix.gov
**Privacy Officer:** privacy@nix.gov
**Incident Reporting:** incident@nix.gov
**24/7 Hotline:** +1-800-NIX-SECURE

## Compliance Certifications

- HIPAA Security Rule Compliant
- HITRUST CSF Certified
- SOC 2 Type II
- ISO 27001:2013
- NIST 800-53 Controls Implemented
- FedRAMP Ready (in progress)
