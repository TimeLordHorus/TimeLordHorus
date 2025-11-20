# NIX System Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Security Setup](#security-setup)
6. [Testing](#testing)
7. [Deployment](#deployment)

## Prerequisites

### Required Software
- Python 3.11 or higher
- PostgreSQL 14+ (with encryption support)
- Redis 7+ (for caching and rate limiting)
- RabbitMQ or Apache Kafka (message queue)
- OpenSSL 3.0+ (for TLS/SSL)
- Docker and Docker Compose (optional, for containerized deployment)

### Required Credentials
- API keys for integrated systems (CMS, VA, state systems, etc.)
- SSL/TLS certificates
- OAuth 2.0 client credentials
- Encryption master keys

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores (8+ recommended for production)
- **RAM**: 8 GB (16+ GB recommended for production)
- **Storage**: 100 GB SSD (for database and logs)
- **Network**: 1 Gbps connection
- **OS**: Linux (Ubuntu 22.04 LTS, RHEL 8+, or equivalent)

### Production Requirements
- **CPU**: 16+ cores
- **RAM**: 32+ GB
- **Storage**: 500 GB+ SSD with encryption
- **Network**: 10 Gbps connection with redundancy
- **High Availability**: Load balancer, database replication

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/your-org/nix-system.git
cd nix-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y postgresql-14 redis-server rabbitmq-server \
    openssl libssl-dev python3-dev build-essential

# RHEL/CentOS
sudo yum install -y postgresql14-server redis rabbitmq-server \
    openssl openssl-devel python3-devel gcc
```

### 5. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb nix_db
sudo -u postgres createuser nix_user -P

# Run migrations
python manage.py migrate

# Enable encryption at rest
sudo vim /etc/postgresql/14/main/postgresql.conf
# Add: ssl = on
# Add: ssl_cert_file = '/path/to/server.crt'
# Add: ssl_key_file = '/path/to/server.key'

sudo systemctl restart postgresql
```

### 6. Redis Setup

```bash
# Configure Redis for TLS
sudo vim /etc/redis/redis.conf
# Add: tls-port 6380
# Add: tls-cert-file /path/to/redis.crt
# Add: tls-key-file /path/to/redis.key
# Add: tls-ca-cert-file /path/to/ca.crt

sudo systemctl restart redis
```

### 7. Generate Encryption Keys

```bash
# Generate master encryption key
python -c "from nix_system.security.encryption.aes_encryption import AESEncryption; \
    import base64; \
    key = AESEncryption.generate_key(); \
    print('Master Key:', base64.b64encode(key).decode())"

# Store in secure key management system (AWS KMS, HashiCorp Vault, etc.)
```

## Configuration

### 1. Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://nix_user:password@localhost:5432/nix_db
DATABASE_SSL_MODE=require

# Redis
REDIS_URL=rediss://localhost:6380
REDIS_PASSWORD=your_redis_password

# Encryption
MASTER_ENCRYPTION_KEY=base64_encoded_key_here
KEY_ROTATION_DAYS=90

# API Configuration
API_BASE_URL=https://api.nix.gov/v1
API_RATE_LIMIT_DEFAULT=1000
API_RATE_LIMIT_EMERGENCY=unlimited

# OAuth 2.0
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_TOKEN_EXPIRY=3600

# External Integrations
CMS_API_KEY=your_cms_api_key
CMS_ENDPOINT=https://api.cms.gov/v1

VA_API_KEY=your_va_api_key
VA_ENDPOINT=https://api.va.gov/services/fhir/v0

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_PATH=/var/log/nix/audit
SECURITY_LOG_PATH=/var/log/nix/security

# Security
TLS_VERSION=1.3
ALLOWED_CIPHER_SUITES=TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256
SESSION_TIMEOUT=1800
MFA_REQUIRED=true

# Compliance
HIPAA_MODE=enabled
AUDIT_RETENTION_DAYS=2555  # 7 years
BREACH_NOTIFICATION_EMAIL=security@your-org.gov
```

### 2. Application Configuration

Edit `nix_system/core/config.py`:

```python
HIPAA_COMPLIANCE = {
    'enabled': True,
    'minimum_necessary': True,
    'audit_all_phi_access': True,
    'encryption_required': True,
    'mfa_required': True
}

RATE_LIMITING = {
    'enabled': True,
    'default_tier': 'basic',
    'redis_backend': True
}

PROVENANCE_TRACKING = {
    'enabled': True,
    'blockchain_enabled': True,
    'track_all_copies': True
}
```

## Security Setup

### 1. TLS/SSL Certificates

```bash
# Generate self-signed certificate (for development only)
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
    -keyout /etc/nix/ssl/server.key \
    -out /etc/nix/ssl/server.crt

# For production, use certificates from trusted CA
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH (restrict to specific IPs in production)
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 3. Set File Permissions

```bash
# Application files
sudo chown -R nix:nix /opt/nix-system
sudo chmod 750 /opt/nix-system

# Configuration files
sudo chmod 600 /opt/nix-system/.env
sudo chmod 600 /etc/nix/config/*

# Log directories
sudo mkdir -p /var/log/nix/{audit,security,application}
sudo chown -R nix:nix /var/log/nix
sudo chmod 750 /var/log/nix
```

### 4. Enable Audit Logging

```bash
# Configure audit logging
sudo vim /etc/audit/rules.d/nix.rules

# Add:
-w /opt/nix-system/nix_system/ -p wa -k nix_code_changes
-w /var/log/nix/ -p wa -k nix_log_access
-w /etc/nix/ -p wa -k nix_config_changes

sudo systemctl restart auditd
```

## Testing

### 1. Run Unit Tests

```bash
pytest tests/unit/ -v --cov=nix_system
```

### 2. Run Integration Tests

```bash
pytest tests/integration/ -v
```

### 3. Security Testing

```bash
# Run security scan
bandit -r nix_system/

# Check for vulnerabilities
safety check

# HIPAA compliance check
python scripts/hipaa_compliance_check.py
```

### 4. Performance Testing

```bash
# Load testing
locust -f tests/performance/load_test.py
```

## Deployment

### Option 1: Docker Deployment

```bash
# Build Docker image
docker build -t nix-system:latest .

# Run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/namespace.yaml
kubectl apply -f deployment/kubernetes/secrets.yaml
kubectl apply -f deployment/kubernetes/deployment.yaml
kubectl apply -f deployment/kubernetes/service.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml

# Check deployment
kubectl get pods -n nix-system
kubectl get svc -n nix-system
```

### Option 3: Systemd Service

Create `/etc/systemd/system/nix-system.service`:

```ini
[Unit]
Description=NIX National Information Exchange System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=nix
Group=nix
WorkingDirectory=/opt/nix-system
Environment="PATH=/opt/nix-system/venv/bin"
ExecStart=/opt/nix-system/venv/bin/python -m nix_system.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nix-system
sudo systemctl start nix-system
sudo systemctl status nix-system
```

## Post-Installation

### 1. Verify Installation

```bash
# Check API health
curl -k https://localhost/health

# Verify database connection
python -m nix_system.core.check_db

# Test encryption
python -m nix_system.security.encryption.test_encryption
```

### 2. Create Initial Admin User

```bash
python manage.py create_admin_user \
    --username admin \
    --email admin@your-org.gov
```

### 3. Register Initial Entities

```bash
# Register hospital
python manage.py register_entity \
    --type hospital \
    --name "Example Hospital" \
    --endpoint "https://hospital.example.com"
```

### 4. Configure Monitoring

```bash
# Set up Prometheus metrics
curl http://localhost:9090/metrics

# Configure Grafana dashboards
# Import dashboard from deployment/grafana/dashboards/
```

## Troubleshooting

### Common Issues

**Database connection failed:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U nix_user -d nix_db
```

**Encryption errors:**
```bash
# Verify encryption key is set
echo $MASTER_ENCRYPTION_KEY

# Test encryption
python -c "from nix_system.security.encryption.aes_encryption import AESEncryption; \
    aes = AESEncryption(); \
    encrypted = aes.encrypt_string('test'); \
    print('Encryption working:', encrypted)"
```

**Rate limiting not working:**
```bash
# Check Redis connection
redis-cli ping

# Check rate limiter
python -c "from nix_system.security.firewall.rate_limiter import RateLimiter; \
    limiter = RateLimiter(); \
    print('Rate limiter initialized')"
```

## Support

For installation support:
- Documentation: https://docs.nix.gov
- Email: support@nix.gov
- Issue Tracker: https://github.com/your-org/nix-system/issues
