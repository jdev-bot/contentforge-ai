# Contributing to ContentForge AI

First off, thank you for considering contributing to ContentForge AI! It's people like you that make this project a great tool for content creators.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if applicable**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`./scripts/test.sh` if available)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- Docker and Docker Compose (for local services)
- Git

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/jdev-bot/contentforge-ai.git
   cd contentforge-ai
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. Start local services:
   ```bash
   docker-compose up -d
   ```

4. Set up the backend:
   ```bash
   cd src/backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

5. Set up the frontend (in a new terminal):
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

6. Open http://localhost:3000 in your browser

## Style Guidelines

### Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, semicolons, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add Twitter distribution endpoint
fix: resolve Redis connection timeout
docs: update API authentication examples
```

### Python Code Style

- Follow PEP 8
- Use type hints where applicable
- Document functions with docstrings
- Maximum line length: 100 characters

### TypeScript/JavaScript Code Style

- Use TypeScript for new code
- Follow the existing ESLint configuration
- Use functional components with hooks
- Prefer `const` over `let`

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage

```bash
# Run backend tests
cd src/backend
pytest

# Run frontend tests
cd src/frontend
npm test
```

## Documentation

- Update the README.md if you change functionality
- Update API documentation in `docs/API.md` for endpoint changes
- Add architecture notes in `docs/ARCHITECTURE.md` for significant changes

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

---

Thank you for contributing! 🎉
