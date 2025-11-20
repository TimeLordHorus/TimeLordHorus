# NIX System - Quick Start Guide

Get the NIX system up and running in minutes with Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB free disk space

## Quick Start (5 Minutes)

### 1. Clone and Navigate
```bash
git clone https://github.com/TimeLordHorus/TimeLordHorus.git
cd TimeLordHorus
```

### 2. Create Environment File
```bash
cat > .env << EOF
# Generate a secure encryption key
MASTER_ENCRYPTION_KEY=$(python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())")

# Database
DATABASE_URL=postgresql://nix_user:nix_password@postgres:5432/nix_db
POSTGRES_PASSWORD=nix_password

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=redis_password

# API Configuration
API_BASE_URL=https://localhost:8000
LOG_LEVEL=INFO
EOF
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Verify Installation
```bash
# Check all containers are running
docker-compose ps

# Check API health
curl http://localhost:8000/health
```

### 5. View Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f nix-app
```

## What's Running?

After `docker-compose up -d`, you'll have:

| Service | Port | Description |
|---------|------|-------------|
| NIX API | 8000 | Main application API |
| PostgreSQL | 5432 | Encrypted database |
| Redis | 6379 | Cache and rate limiting |
| RabbitMQ | 5672, 15672 | Message queue + management UI |
| Nginx | 80, 443 | Reverse proxy |

## Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (user: nix, pass: rabbitmq_password)

## First Steps

### Create Test Patient Record
```bash
# Get API token (in production, use OAuth 2.0)
export API_TOKEN="your_test_token"

# Create patient record
curl -X POST http://localhost:8000/v1/patients/test_patient_001/records \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "medical_history",
    "content": {
      "diagnosis": "Type 2 Diabetes",
      "icd_code": "E11.9",
      "provider": "dr_test_001",
      "date": "2024-11-20"
    }
  }'
```

### Grant Consent
```bash
curl -X POST http://localhost:8000/v1/patients/test_patient_001/consents \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": "dr_smith_001",
    "recipient_type": "provider",
    "consent_type": "treatment",
    "data_categories": ["medical_records", "prescriptions"],
    "purpose": "Ongoing treatment",
    "duration_days": 365,
    "permissions": {
      "can_view": true,
      "can_copy": true
    }
  }'
```

### View Audit Trail
```bash
curl -X GET http://localhost:8000/v1/patients/test_patient_001/audit-trail \
  -H "Authorization: Bearer $API_TOKEN"
```

## Running Tests

### Run All Tests
```bash
docker-compose exec nix-app pytest tests/ -v
```

### Run Specific Test Suite
```bash
# Audit logger tests
docker-compose exec nix-app pytest tests/test_audit_logger.py -v

# Encryption tests
docker-compose exec nix-app pytest tests/test_encryption.py -v

# Consent tests
docker-compose exec nix-app pytest tests/test_consent.py -v
```

### Check Coverage
```bash
docker-compose exec nix-app pytest tests/ --cov=nix_system --cov-report=html
```

## Development Mode

### Run with Live Reload
```bash
# Stop production containers
docker-compose down

# Run in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Interactive Python Shell
```bash
docker-compose exec nix-app python

>>> from nix_system.security.encryption.aes_encryption import AESEncryption
>>> aes = AESEncryption()
>>> encrypted = aes.encrypt_string("Test PHI data")
>>> print(encrypted)
```

## Troubleshooting

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Errors
```bash
# Check PostgreSQL is ready
docker-compose exec postgres pg_isready

# Check connection
docker-compose exec postgres psql -U nix_user -d nix_db
```

### API Not Responding
```bash
# Check API logs
docker-compose logs nix-app

# Restart API
docker-compose restart nix-app
```

### Clear All Data (Reset)
```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d
```

## Security Checklist

Before deploying to production:

- [ ] Change all default passwords in `.env`
- [ ] Generate new encryption keys
- [ ] Install SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Review audit logs
- [ ] Complete security assessment
- [ ] Test disaster recovery

## Next Steps

1. **Read Documentation**
   - [Installation Guide](nix-system/docs/INSTALLATION.md)
   - [Security Documentation](nix-system/docs/SECURITY.md)
   - [API Guide](nix-system/docs/API_GUIDE.md)
   - [Project Overview](PROJECT_OVERVIEW.md)

2. **Configure Integrations**
   - Set up state system connections
   - Configure federal system APIs
   - Connect to EHR/EMR systems

3. **Customize**
   - Add organization-specific workflows
   - Customize consent forms
   - Configure branding

4. **Deploy to Production**
   - Follow [Installation Guide](nix-system/docs/INSTALLATION.md)
   - Set up monitoring
   - Configure backups
   - Test disaster recovery

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart nix-app

# Execute command in container
docker-compose exec nix-app <command>

# Access shell
docker-compose exec nix-app bash

# Rebuild images
docker-compose build

# Check service status
docker-compose ps
```

## Getting Help

- **Documentation**: See `nix-system/docs/` directory
- **Issues**: Report bugs on GitHub
- **Support**: support@nix.gov
- **API Reference**: http://localhost:8000/docs

## Production Deployment

For production deployment, see:
- [Installation Guide](nix-system/docs/INSTALLATION.md)
- [Security Documentation](nix-system/docs/SECURITY.md)

Key differences for production:
- Use production-grade database (RDS, Cloud SQL)
- Enable TLS/SSL with valid certificates
- Configure load balancer
- Set up multi-region deployment
- Enable automated backups
- Configure monitoring and alerting
- Use secrets management (Vault, KMS)
- Implement disaster recovery

---

**Ready to build? Start with `docker-compose up -d` and you're live in 2 minutes!** 🚀
