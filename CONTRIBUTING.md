# Contributing to NIX System

Thank you for your interest in contributing to the NIX (National Information Exchange) system!

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together towards common goals
- **Be professional**: Maintain professional standards in all interactions
- **Prioritize security**: Security and privacy are paramount in healthcare

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include**:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs (redact any PHI/PII!)

### Suggesting Features

1. **Check the roadmap** to see if it's already planned
2. **Open a feature request issue**
3. **Describe**:
   - The problem you're solving
   - Proposed solution
   - HIPAA compliance considerations
   - Security implications

### Security Vulnerabilities

**DO NOT** open public issues for security vulnerabilities!

Instead:
1. Email: security@nix.gov
2. Use encrypted email (PGP key available on request)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We'll respond within 48 hours and work with you to address the issue.

## Development Process

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/TimeLordHorus.git
cd TimeLordHorus
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `security/` - Security improvements
- `test/` - Test additions/improvements

### 3. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 4. Make Your Changes

#### Code Guidelines

**Security First**
- Never log PHI/PII
- Always encrypt sensitive data
- Use parameterized queries
- Validate all inputs
- Follow OWASP Top 10

**Code Style**
- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Maximum line length: 127 characters
- Use Black for formatting

**Testing Requirements**
- Write tests for all new features
- Maintain > 80% code coverage
- Test security-critical paths thoroughly
- Include HIPAA compliance tests

#### Example Function

```python
from typing import Dict, Any, Optional

def store_medical_record(
    patient_id: str,
    record_data: Dict[str, Any],
    consent_id: str,
    created_by: str
) -> str:
    """
    Store medical record with encryption and audit logging.

    Args:
        patient_id: Patient identifier
        record_data: Record content (will be encrypted)
        consent_id: Associated consent identifier
        created_by: User creating the record

    Returns:
        Created record ID

    Raises:
        ValidationError: If record_data is invalid
        UnauthorizedError: If consent is not valid

    HIPAA Compliance:
        - Encrypts PHI at rest (§164.312(a)(2)(iv))
        - Logs access to audit trail (§164.312(b))
        - Verifies consent before storage
    """
    # Validate inputs
    if not patient_id or not record_data:
        raise ValidationError("Patient ID and record data required")

    # Verify consent
    if not verify_consent(consent_id, patient_id):
        audit_logger.log_unauthorized_access(created_by, patient_id)
        raise UnauthorizedError("Invalid consent")

    # Encrypt data
    encrypted_data = encrypt(record_data)

    # Store record
    record_id = database.insert(
        patient_id=patient_id,
        data=encrypted_data,
        consent_id=consent_id
    )

    # Audit log
    audit_logger.log_record_creation(
        record_id=record_id,
        patient_id=patient_id,
        created_by=created_by
    )

    return record_id
```

### 5. Write Tests

```python
def test_store_medical_record_with_valid_consent():
    """Test storing medical record with valid consent"""
    record_id = store_medical_record(
        patient_id="patient_001",
        record_data={"diagnosis": "Test"},
        consent_id="consent_001",
        created_by="dr_smith"
    )

    assert record_id is not None
    # Verify audit log entry created
    # Verify data encrypted
    # Verify consent checked


def test_store_medical_record_without_consent():
    """Test that storing without consent raises error"""
    with pytest.raises(UnauthorizedError):
        store_medical_record(
            patient_id="patient_001",
            record_data={"diagnosis": "Test"},
            consent_id="invalid_consent",
            created_by="dr_smith"
        )
```

### 6. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nix_system --cov-report=html

# Run specific test file
pytest tests/test_consent.py -v

# Run security tests
pytest tests/ -m security -v
```

### 7. Run Code Quality Checks

```bash
# Format code
black nix-system/

# Check style
flake8 nix-system/

# Type checking
mypy nix-system/

# Security scan
bandit -r nix-system/

# Check for vulnerabilities
safety check
```

### 8. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add patient consent management

- Implement granular consent controls
- Add expiration tracking
- Include HIPAA compliance checks
- Add comprehensive tests

Closes #123"
```

Commit message format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `security`: Security improvement
- `perf`: Performance improvement

### 9. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Code coverage maintained/improved
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] HIPAA compliance verified
- [ ] No PHI/PII in code or tests
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Clear description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Security improvement
- [ ] Documentation update
- [ ] Other (describe)

## HIPAA Compliance
Describe how this change maintains HIPAA compliance

## Security Considerations
Describe security implications and mitigations

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #123
Related to #456
```

## Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and security scans
2. **Code Review**: At least one maintainer reviews the code
3. **Security Review**: Security-sensitive changes require security team review
4. **Compliance Review**: Changes affecting HIPAA compliance require compliance review
5. **Approval**: PR requires approval before merging
6. **Merge**: Maintainer merges the PR

## HIPAA Compliance Requirements

All contributions must maintain HIPAA compliance:

### Do's
✅ Encrypt all PHI at rest and in transit
✅ Log all PHI access to audit trail
✅ Verify consent before data access
✅ Use parameterized queries
✅ Validate all inputs
✅ Implement proper error handling
✅ Use secure authentication
✅ Follow principle of least privilege

### Don'ts
❌ Log PHI in application logs
❌ Store PHI unencrypted
❌ Allow access without consent
❌ Use string concatenation for SQL
❌ Trust user input
❌ Expose detailed error messages
❌ Use weak authentication
❌ Grant unnecessary permissions

## Testing Requirements

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Cover edge cases and error conditions

### Integration Tests
- Test component interactions
- Use test database and services
- Verify data flow

### Security Tests
- Test authentication and authorization
- Verify encryption
- Test input validation
- Check for common vulnerabilities

### HIPAA Compliance Tests
- Verify audit logging
- Test consent verification
- Check data encryption
- Verify access controls

## Documentation

All code changes should include:

1. **Code Comments**: For complex logic
2. **Docstrings**: For all public functions/classes
3. **API Documentation**: For new endpoints
4. **User Documentation**: For user-facing features
5. **Security Documentation**: For security changes
6. **Compliance Notes**: For HIPAA-related changes

## Questions?

- **General Questions**: Open a discussion on GitHub
- **Technical Questions**: Ask in PR comments
- **Security Questions**: Email security@nix.gov
- **Compliance Questions**: Email compliance@nix.gov

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website

Thank you for contributing to healthcare data security and privacy! 🏥🔒
