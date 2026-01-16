# Contributing to WarmIt

First off, thank you for considering contributing to WarmIt! It's people like you that make WarmIt such a great tool.

## 🎯 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, logs, screenshots)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, Docker version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List alternatives you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our code style guidelines
3. **Add tests** for any new functionality
4. **Update documentation** if needed
5. **Ensure all tests pass** (`make test`)
6. **Submit a pull request**

## 📝 Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/warmit.git
cd warmit

# Install Poetry if you haven't
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --with dev

# Setup pre-commit hooks (optional but recommended)
poetry run pre-commit install

# Start development environment
./warmit.sh start
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_models.py -v

# Run with coverage
make test-cov

# Run linting
make lint

# Run type checking
make type-check
```

## 💻 Code Style

We use the following tools to maintain code quality:

- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

### Code Standards

- **Follow PEP 8** style guide
- **Use type hints** on all functions
- **Write docstrings** (Google style) for all public methods
- **Keep functions small** and focused
- **Use async/await** for I/O operations
- **Add tests** for new functionality

### Example Function

```python
async def send_email(
    self,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    message: EmailMessage,
    use_tls: bool = True,
) -> bool:
    """
    Send an email via SMTP.

    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port (587 for STARTTLS, 465 for SSL)
        username: SMTP username
        password: SMTP password
        message: EmailMessage object to send
        use_tls: Whether to use STARTTLS

    Returns:
        True if email sent successfully, False otherwise

    Raises:
        SMTPException: If SMTP connection fails

    Example:
        >>> service = EmailService()
        >>> msg = EmailMessage(...)
        >>> success = await service.send_email(...)
    """
    # Implementation...
```

## 📚 Documentation

- Update documentation for any user-facing changes
- Add docstrings to new functions/classes
- Update README.md if needed
- Keep code comments clear and concise

## 🔄 Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/changes

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(email): add support for Outlook SMTP

Implement Outlook-specific SMTP configuration with App Password support.
Includes automatic port detection and SSL/TLS handling.

Closes #123
```

```
fix(tracking): resolve greenlet error on email open

Add eager loading with selectinload() to prevent lazy-load greenlet
errors when accessing email relationships in tracking endpoint.

Fixes #456
```

## 🧪 Testing Guidelines

### Writing Tests

- **Unit tests** for individual functions/methods
- **Integration tests** for component interactions
- **E2E tests** for complete workflows
- Aim for **>80% code coverage**

### Test Structure

```python
class TestEmailService:
    """Test EmailService class."""

    @pytest.mark.asyncio
    async def test_send_email_success(self, db_session):
        """Test successful email sending."""
        # Arrange
        service = EmailService()
        message = EmailMessage(...)

        # Act
        result = await service.send_email(...)

        # Assert
        assert result is True
```

## 🔒 Security

- **Never commit secrets** (API keys, passwords)
- **Use environment variables** for sensitive data
- **Encrypt sensitive data** at rest
- **Report security vulnerabilities** privately (see SECURITY.md)

## 📋 Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] Added/updated tests for changes
- [ ] All tests pass (`make test`)
- [ ] Updated documentation
- [ ] Added type hints
- [ ] Wrote clear commit messages
- [ ] Linked related issues

## 🎓 Resources

- [Developer Documentation](docs/developer/README.md)
- [Models Reference](docs/developer/MODELS.md)
- [Services Reference](docs/developer/SERVICES.md)
- [Architecture Overview](docs/developer/README.md#architecture-overview)

## 💬 Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to WarmIt!** 🙏
