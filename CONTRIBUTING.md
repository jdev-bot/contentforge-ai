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
4. Run the tests (`pytest` for backend, `npm test` for frontend)
5. Ensure all CI checks pass
6. Commit your changes using [Conventional Commits](#git-commit-messages)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- **Python 3.13+** (for backend)
- **Node.js 20+** (for frontend)
- **Docker and Docker Compose** (for local services)
- **Git** with SSH configured for `github.com`
- **Redis** (for Celery background tasks)
- **A Supabase account** (free tier works)
- **A Groq account** (free tier: 14M tokens/month)

### Local Development

1. Clone the repository:
   ```bash
   git clone git@github.com:jdev-bot/contentforge-ai.git
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
   pre-commit install  # Install pre-commit hooks
   uvicorn app.main:app --reload
   ```

5. Set up the frontend (in a new terminal):
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

6. Open http://localhost:3000 in your browser

For detailed setup instructions, see [docs/LOCAL_DEPLOYMENT_GUIDE.md](docs/LOCAL_DEPLOYMENT_GUIDE.md).

## Code Standards

### Python Code Style

We enforce strict code quality standards:

- **`black`** — Code formatter (zero violations tolerated)
- **`isort`** — Import sorter (zero violations tolerated)
- **`flake8`** — Linter (zero errors tolerated)
- **`mypy`** — Type checker with strict mode (zero errors tolerated)
- **`no-any`** — No `Any` types allowed; use proper type annotations
- **PEP 8** compliance with maximum line length of 100 characters
- **Type hints** required on all functions
- **Docstrings** required on all public functions and classes

**Current metrics:**
- 0 `print()` calls in production code (use `logging` module)
- 0 `datetime.utcnow()` calls (use timezone-aware `datetime.now(timezone.utc)`)
- 0 bare `except` clauses (always specify exception type)
- 0 `isort` violations
- 0 `black` violations

```bash
# Run all Python checks
black --check src/backend/
isort --check-only src/backend/
flake8 src/backend/
mypy src/backend/ --strict
```

### TypeScript Code Style

- **TypeScript strict mode** — Enabled, zero errors tolerated
- **ESLint** — Zero errors, zero warnings tolerated
- **No `any` types** — Use proper TypeScript interfaces
- **Proper interfaces** — Define interfaces for all data structures
- **Functional components with hooks** — For React components
- **Prefer `const` over `let`** — Immutable where possible

**Current metrics:**
- 0 `console.log()` calls in production code
- 0 TypeScript errors
- 0 ESLint errors/warnings
- 0 `any` type usage

```bash
# Run TypeScript checks
cd src/frontend
npx tsc --noEmit
npx eslint .
```

## Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, semicolons, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

Examples:
```
feat: add Twitter distribution endpoint
fix: resolve Redis connection timeout
docs: update API authentication examples
perf: add Redis caching to dashboard endpoints
refactor: eliminate N+1 queries in content listing
test: add integration tests for Stripe webhooks
```

**Commit message body:** Include a brief description of what changed and why.

## CI/CD Requirements

All PRs must pass the following CI pipelines before merge:

| Pipeline | Checks | Runner |
|----------|--------|--------|
| Backend Tests | pytest (530+ tests) | Self-hosted GitHub Actions runner |
| Frontend Build | TypeScript compilation + ESLint | Self-hosted GitHub Actions runner |
| Lint/Format | black, isort, flake8, mypy | Self-hosted GitHub Actions runner |
| Security Scan | Dependency + code scanning | Self-hosted GitHub Actions runner |

**All 4 pipelines must be green before merge.**

### Self-Hosted Runner

This project uses a self-hosted GitHub Actions runner for CI/CD. If you're contributing from a fork, GitHub Actions will use GitHub-hosted runners for your PR. Core maintainers can trigger runs on the self-hosted runner.

## Testing

### Backend Testing

```bash
cd src/backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_stripe_webhooks.py -v
```

**Current test coverage:**
- 530 backend tests passing
- 163/164 deep system tests passing (99.4%)

### Frontend Testing

```bash
cd src/frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Writing Tests

- Write tests for all new features
- Maintain or improve test coverage
- Integration tests for API endpoints
- Unit tests for service logic
- Mock external dependencies (Groq, Stripe, Supabase)

## Pre-Commit Hooks

Pre-commit hooks are configured to enforce code quality before commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Hooks include:**
- `black` formatting
- `isort` import sorting
- `flake8` linting
- `mypy` type checking
- Trailing whitespace removal
- YAML/JSON validation

## Documentation

- Update the README.md if you change functionality
- Update API documentation in `docs/` for endpoint changes
- Add architecture notes in `docs/ARCHITECTURE.md` for significant changes
- Update `docs/DESIGN_SYSTEM.md` for UI component changes

## Project Architecture

```
contentforge-ai/
├── src/
│   ├── backend/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/  # 49 router modules, 375 API routes
│   │   │   ├── services/ # 34 service modules
│   │   │   └── main.py   # App entry point
│   │   └── tests/        # 530+ tests
│   └── frontend/         # Next.js frontend
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── app/          # Pages & routes
│       │   └── lib/          # Utilities & API client
│       └── package.json
├── docs/                  # Documentation
├── infra/                 # Infrastructure config
│   ├── docker/            # Dockerfiles
│   └── supabase/           # DB schema & migrations
└── .github/workflows/     # CI/CD pipelines
```

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

---

Thank you for contributing! 🎉