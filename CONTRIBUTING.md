# Contributing to WarmIt

Thank you for your interest in contributing to WarmIt! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints
- Accept responsibility for mistakes

## 🚀 How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/yourusername/warmit/issues) first
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (OS, Python version, Docker version)
   - Logs (if applicable)

### Suggesting Features

1. Check [existing issues](https://github.com/yourusername/warmit/issues) first
2. Use the feature request template
3. Explain:
   - Use case
   - Proposed solution
   - Alternatives considered
   - Impact on existing features

### Areas for Contribution

- 🐛 **Bug Fixes**: Fix issues from GitHub Issues
- ✨ **Features**: Implement new functionality
- 📝 **Documentation**: Improve or translate docs
- 🧪 **Tests**: Increase test coverage
- 🎨 **UI/UX**: Improve dashboard design
- 🌍 **Translations**: Add i18n support
- ⚡ **Performance**: Optimize code
- 🔒 **Security**: Find and fix vulnerabilities

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose
- Git

### Setup Steps

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/warmit.git
cd warmit

# 2. Install dependencies
poetry install

# 3. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start services
docker compose -f docker/docker-compose.yml up -d redis postgres

# 5. Run migrations
poetry run alembic upgrade head

# 6. Start development server
poetry run uvicorn warmit.main:app --reload

# 7. Start Celery (in another terminal)
poetry run celery -A warmit.tasks worker --loglevel=info

# 8. Start dashboard (in another terminal)
poetry run streamlit run dashboard/app.py
```

### Project Structure

```
warmit/
├── src/warmit/          # Main application code
│   ├── api/             # FastAPI routes
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── tasks/           # Celery tasks
│   └── utils/           # Utilities
├── dashboard/           # Streamlit dashboard
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── docker/              # Docker configuration
└── docs/                # Documentation
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Make changes**: Follow coding standards
3. **Test**: Ensure all tests pass
4. **Format**: Run code formatters
5. **Commit**: Use clear commit messages
6. **Update docs**: If needed

### Commit Message Format

```
type(scope): brief description

Longer description if needed.

Fixes #issue_number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(api): add endpoint for bulk account import
fix(scheduler): prevent duplicate email sending
docs(readme): update installation instructions
```

### Submitting PR

1. Push to your fork: `git push origin feature/your-feature-name`
2. Open PR on GitHub
3. Fill out PR template
4. Wait for review
5. Address feedback if any
6. PR will be merged once approved

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No merge conflicts
- [ ] Changelog updated (if applicable)

## 📝 Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these tools:

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/
```

### Code Quality

- **Type hints**: Use for all function signatures
- **Docstrings**: Google style for public APIs
- **Comments**: Explain "why", not "what"
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
- **Line length**: Max 100 characters
- **Imports**: Sort with `isort`

### Example

```python
"""Module for email warming scheduling."""

from typing import Optional
from datetime import datetime


class WarmupScheduler:
    """Manages email warming schedules.

    Args:
        session: Database session

    Attributes:
        session: Database session instance
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_daily_target(
        self,
        campaign: Campaign,
        current_week: int
    ) -> int:
        """Calculate target emails for current week.

        Args:
            campaign: Campaign instance
            current_week: Current week number

        Returns:
            Number of emails to send today
        """
        # Implementation here
        pass
```

## 🧪 Testing

### Run Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=warmit --cov-report=html

# Specific test
poetry run pytest tests/test_domain_checker.py

# Watch mode
poetry run pytest-watch
```

### Writing Tests

- **Location**: `tests/` directory
- **Naming**: `test_*.py` files, `test_*` functions
- **Structure**: Arrange-Act-Assert
- **Coverage**: Aim for 80%+ coverage
- **Fixtures**: Use pytest fixtures for common setup

```python
import pytest
from warmit.services.domain_checker import DomainChecker


class TestDomainChecker:
    """Test domain checking functionality."""

    def test_extract_domain(self):
        """Test domain extraction from email."""
        # Arrange
        email = "test@example.com"

        # Act
        domain = DomainChecker.extract_domain(email)

        # Assert
        assert domain == "example.com"

    @pytest.mark.asyncio
    async def test_check_domain(self):
        """Test domain age checking."""
        # Test implementation
        pass
```

## 📚 Documentation

### Types of Documentation

1. **Code Comments**: Explain complex logic
2. **Docstrings**: API documentation
3. **README**: Project overview
4. **User Guides**: How-to documents
5. **API Docs**: FastAPI auto-generated

### Documentation Style

- **Clear**: Easy to understand
- **Concise**: Get to the point
- **Complete**: Cover all aspects
- **Current**: Keep up-to-date
- **Examples**: Show real usage

### Updating Docs

When adding features:
1. Update relevant `docs/*.md` files
2. Add docstrings to new code
3. Update README if needed
4. Add examples to user guides

## 🎨 Dashboard Contributions

### Streamlit Components

- Follow existing UI patterns
- Use consistent colors and styling
- Add loading states
- Handle errors gracefully
- Test on different screen sizes

### UI Guidelines

```python
# Good: Clear structure with sections
st.title("Page Title")
st.subheader("Section")

col1, col2 = st.columns(2)
with col1:
    st.metric("Label", value)

# Good: User feedback
with st.spinner("Loading..."):
    data = fetch_data()

if data:
    st.success("Success!")
else:
    st.error("Error occurred")

# Good: Error handling
try:
    process_data()
except Exception as e:
    st.error(f"Error: {e}")
    logger.error("Failed to process", exc_info=True)
```

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email: security@yourdomain.com
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Security Best Practices

- Never commit secrets (.env, keys, passwords)
- Use environment variables
- Validate all inputs
- Sanitize database queries
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

## 📞 Getting Help

- **Documentation**: Check [docs/](docs/) first
- **Issues**: Search existing issues
- **Discussions**: Ask questions in GitHub Discussions
- **Discord**: Join our community (link)

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Top contributors may be invited to join the core team!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to WarmIt! 🔥**
