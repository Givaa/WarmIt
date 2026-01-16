# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **[your-email@example.com]**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report
- **Investigation**: We will investigate and validate the issue
- **Fix**: We will work on a fix and coordinate a release
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)
- **Disclosure**: We follow coordinated disclosure and will work with you on timing

## Security Best Practices

### For Users

1. **Environment Variables**: Never commit `.env` files or expose API keys
2. **Encryption**: Always set `ENCRYPTION_KEY` in production
3. **Passwords**: Use strong, unique passwords for database and dashboard
4. **Updates**: Keep WarmIt and dependencies up to date
5. **Network**: Run behind a firewall, limit exposed ports
6. **Monitoring**: Enable logging and monitoring
7. **Backups**: Regularly backup your database

### For Developers

1. **Dependencies**: Keep dependencies updated
2. **Secrets**: Never commit secrets or credentials
3. **Input Validation**: Validate all user input
4. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
5. **XSS**: Sanitize output in dashboard
6. **CSRF**: Use proper CSRF protection
7. **Authentication**: Implement proper session management
8. **Encryption**: Use strong encryption for sensitive data

## Known Security Features

### Implemented

- ✅ **Password Encryption**: Fernet symmetric encryption for email passwords
- ✅ **Dashboard Authentication**: Session-based auth with hashed passwords
- ✅ **Database Encryption**: Automatic encrypt/decrypt for sensitive fields
- ✅ **Environment Variables**: Sensitive config via env vars
- ✅ **Docker Isolation**: Services run in isolated containers
- ✅ **SQLAlchemy ORM**: Protection against SQL injection

### Planned

- ⏳ **Rate Limiting**: API rate limiting (coming soon)
- ⏳ **2FA**: Two-factor authentication for dashboard
- ⏳ **Audit Logging**: Security event logging
- ⏳ **Secrets Management**: Vault integration

## Security Updates

Security updates are released as:
- **Patch versions** (0.2.x) for minor security fixes
- **Minor versions** (0.x.0) for moderate security improvements
- **Security advisories** for critical vulnerabilities

Subscribe to GitHub notifications to stay informed about security updates.

## Disclosure Policy

We follow **coordinated disclosure**:

1. Reporter submits vulnerability
2. We acknowledge and investigate (48 hours)
3. We develop and test a fix
4. We coordinate release with reporter
5. We publish security advisory
6. We release patched version
7. Reporter receives credit (if desired)

## Security Tools

We use the following tools to maintain security:

- **Dependabot**: Automated dependency updates
- **GitHub Security Advisories**: Vulnerability tracking
- **Safety**: Python dependency security scanner
- **Bandit**: Python security linter
- **Ruff**: Code quality and security linting

## Contact

For security concerns, contact: **[your-email@example.com]**

For general questions, use GitHub Discussions.

---

**Last Updated**: 2026-01-17
