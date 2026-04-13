# Security Policy

## Supported Versions

The following versions of ContentForge AI are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

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

### Security Measures

ContentForge AI implements the following security measures:

- **Authentication**: JWT-based authentication via Supabase Auth
- **Authorization**: Row-level security (RLS) on database tables
- **Data Encryption**: TLS 1.3 for all connections
- **API Security**: Rate limiting, CORS protection, input validation
- **Secrets Management**: Environment variables, never committed to code
- **Dependency Scanning**: Regular dependency updates

### Security Best Practices for Users

1. **Keep dependencies updated**: Run `npm update` and `pip install --upgrade` regularly
2. **Use strong passwords**: Enforce strong password policies
3. **Enable 2FA**: Use two-factor authentication where available
4. **Secure your API keys**: Never expose API keys in client-side code
5. **Regular backups**: Maintain backups of your data

## Security Updates

Security updates will be announced via:

- GitHub Security Advisories
- Email notifications to registered users
- Release notes

## Acknowledgments

We thank the following security researchers who have responsibly disclosed vulnerabilities:

*None yet - be the first!*

---

Last updated: April 13, 2026
