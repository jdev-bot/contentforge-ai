# Security Policy

## Supported Versions

The following versions of ContentForge AI are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0.0 | :x:                |

## Security Audit Status

**Last Audit:** April 14, 2026  
**Status:** ✅ ALL FINDINGS RESOLVED (9/9)

| Finding | Severity | Status |
|---------|----------|--------|
| All 9 security findings | Mixed | ✅ Fixed |

The codebase has undergone a comprehensive security audit. All identified vulnerabilities have been resolved and verified through testing.

## Reporting a Vulnerability

If you discover a security vulnerability in ContentForge AI, please report it responsibly.

### How to Report

**Please do NOT disclose security vulnerabilities publicly** (e.g., GitHub issues, discussions, or social media).

Instead, please report security vulnerabilities via email:

📧 **security@contentforge.ai**

Please include the following details in your report:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact of the vulnerability
- **Steps to reproduce**: Step-by-step instructions to reproduce the issue
- **Affected versions**: Which versions are affected
- **Suggested fix**: If you have a suggestion for fixing the issue

### Response Timeline

We aim to respond to security reports within:

- **24 hours**: Initial acknowledgment
- **72 hours**: Initial assessment and next steps
- **7 days**: Fix implemented or timeline provided

## Security Measures

ContentForge AI implements the following security measures:

### Authentication & Authorization
- **JWT Authentication**: Token-based auth with refresh rotation via Supabase Auth
- **Row-Level Security (RLS)**: Database-level access control on all tables
- **SSO Support**: OpenID Connect (OIDC) and SAML 2.0 for enterprise SSO
- **Role-Based Access**: Admin/Editor/Viewer permissions with organization support

### API Security
- **Rate Limiting**: Per-endpoint rate limiting to prevent abuse
- **Input Validation**: Pydantic schemas on all endpoints for strict input validation
- **SQL Injection Prevention**: Parameterized queries via Supabase client (no raw SQL)
- **XSS Protection**: Output sanitization and Content Security Policy headers
- **CSRF Protection**: Token-based verification on state-changing requests
- **CORS**: Whitelisted origins only (configurable)

### Data Protection
- **TLS 1.3**: Enforced for all connections
- **Data Encryption**: TLS in transit, Supabase encryption at rest
- **Secrets Management**: Environment variables only, never committed to code
- **Data Retention Policies**: Configurable retention and deletion (P4 feature)
- **Audit Logging**: Comprehensive audit trail of all significant actions (P4 feature)

### Infrastructure Security
- **Dependency Scanning**: Regular dependency updates and vulnerability scanning
- **Security Scanning**: Automated security scanning in CI/CD pipeline
- **Health Monitoring**: Real-time health checks and response time monitoring
- **Request Tracing**: X-Request-ID headers for security event correlation

### Code Security Standards
- 0 `print()` calls (proper logging only)
- 0 `console.log()` calls in production
- 0 bare `except` clauses (specific exception types required)
- 0 `datetime.utcnow()` (timezone-aware datetime only)
- Strict type checking (mypy strict, TypeScript strict)
- Pre-commit hooks enforcing security-related linting rules

## Security Best Practices for Users

1. **Keep dependencies updated**: Run `npm update` and `pip install --upgrade` regularly
2. **Use strong passwords**: Enforce strong password policies
3. **Enable 2FA**: Use two-factor authentication where available
4. **Secure your API keys**: Never expose API keys in client-side code
5. **Regular backups**: Maintain backups of your data
6. **Configure SSO**: Use SSO/SAML for enterprise deployments
7. **Review audit logs**: Regularly review audit logs for suspicious activity
8. **Set data retention**: Configure retention policies per compliance requirements

## Security Updates

Security updates will be announced via:

- GitHub Security Advisories
- Email notifications to registered users
- Release notes

## Acknowledgments

We thank the following security researchers who have responsibly disclosed vulnerabilities:

*None yet - be the first!*

---

Last updated: April 14, 2026