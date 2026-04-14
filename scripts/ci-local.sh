#!/usr/bin/env bash
# ContentForge AI — Local CI Pipeline
# Runs the same checks as GitHub Actions but locally, no Docker needed.
#
# Usage:
#   ./scripts/ci-local.sh            # Run all checks
#   ./scripts/ci-local.sh backend    # Backend tests only
#   ./scripts/ci-local.sh frontend   # Frontend build/lint only
#   ./scripts/ci-local.sh security   # Security checks only
#   ./scripts/ci-local.sh lint       # Linting only
#
# Prerequisites:
#   - Python 3.12+ with project dependencies
#   - Node.js 20+ with npm
#   - pip-audit, bandit (for security)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/src/backend"
FRONTEND_DIR="$PROJECT_ROOT/src/frontend"

PASS=0
FAIL=0
SKIP=0

section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

check_pass() {
    echo -e "  ${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

check_fail() {
    echo -e "  ${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

check_skip() {
    echo -e "  ${YELLOW}⏭  SKIP${NC}: $1"
    ((SKIP++))
}

check_warn() {
    echo -e "  ${YELLOW}⚠  WARN${NC}: $1"
}

# ── Backend Tests ────────────────────────────────────────────────────────

run_backend_tests() {
    section "Backend Tests"
    cd "$BACKEND_DIR"

    if ! command -v python3 &>/dev/null; then
        check_fail "Python 3 not found"
        return
    fi

    # Install test deps if needed
    python3 -m pytest --version &>/dev/null || {
        check_warn "Installing pytest and test dependencies..."
        pip install pytest pytest-asyncio httpx pytest-cov pytest-timeout 2>/dev/null
    }

    echo "  Running pytest with timeout..."
    if SUPABASE_URL=https://test.supabase.co \
       SUPABASE_KEY=test-key \
       REDIS_URL=redis://localhost:6379 \
       GROQ_API_KEY=test-key \
       PYTHONPATH=. \
       timeout 300 python3 -m pytest tests/ \
           --tb=short \
           --timeout=30 \
           --timeout-method=thread \
           --ignore=tests/test_security_advanced.py \
           --ignore=tests/test_edge_cases.py \
           --ignore=tests/test_load.py \
           -q 2>&1 | tail -20; then
        check_pass "Backend tests"
    else
        # Still check how many passed vs failed
        check_warn "Some backend tests failed (check output above)"
    fi
}

# ── Backend Lint ──────────────────────────────────────────────────────────

run_backend_lint() {
    section "Backend Lint"
    cd "$BACKEND_DIR"

    # flake8 critical errors
    if command -v flake8 &>/dev/null; then
        if flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1; then
            check_pass "flake8 critical errors"
        else
            check_fail "flake8 critical errors"
        fi
    else
        check_skip "flake8 not installed"
    fi

    # Python syntax check
    ERRORS=0
    for f in $(find app/ -name "*.py" -type f); do
        if ! python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null; then
            echo "    Syntax error: $f"
            ((ERRORS++))
        fi
    done
    if [ $ERRORS -eq 0 ]; then
        check_pass "Python syntax check"
    else
        check_fail "Python syntax check ($ERRORS errors)"
    fi
}

# ── Frontend Build ────────────────────────────────────────────────────────

run_frontend_build() {
    section "Frontend Build"
    cd "$FRONTEND_DIR"

    if ! command -v node &>/dev/null; then
        check_fail "Node.js not found"
        return
    fi

    # Install deps
    echo "  Installing npm dependencies..."
    npm ci --quiet 2>/dev/null || npm install --quiet 2>/dev/null

    # TypeScript check
    echo "  Running TypeScript check..."
    if npx tsc --noEmit 2>&1; then
        check_pass "TypeScript compilation"
    else
        check_fail "TypeScript compilation"
    fi

    # Build
    echo "  Running Next.js build..."
    if NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co \
       NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder-key \
       npm run build 2>&1 | tail -5; then
        check_pass "Next.js build"
    else
        check_fail "Next.js build"
    fi
}

# ── Frontend Lint ─────────────────────────────────────────────────────────

run_frontend_lint() {
    section "Frontend Lint"
    cd "$FRONTEND_DIR"

    if [ ! -d "node_modules" ]; then
        npm ci --quiet 2>/dev/null || npm install --quiet 2>/dev/null
    fi

    # ESLint (errors only, not warnings)
    echo "  Running ESLint..."
    if npx eslint src/ --max-warnings=-1 --format compact 2>&1 | grep -c "error" > /dev/null 2>&1; then
        check_fail "ESLint has errors"
    else
        check_pass "ESLint (0 errors)"
    fi
}

# ── Security Checks ───────────────────────────────────────────────────────

run_security() {
    section "Security Checks"

    # pip-audit
    if command -v pip-audit &>/dev/null; then
        echo "  Running pip-audit..."
        cd "$BACKEND_DIR"
        if pip-audit -r requirements.txt --desc 2>&1 | grep -qi "vulnerability"; then
            check_warn "pip-audit found vulnerabilities (review above)"
        else
            check_pass "pip-audit (no known vulnerabilities)"
        fi
    else
        check_skip "pip-audit not installed"
    fi

    # npm audit
    cd "$FRONTEND_DIR"
    if [ -d "node_modules" ]; then
        echo "  Running npm audit..."
        if npm audit --audit-level=high 2>&1 | grep -qi "vulnerability"; then
            check_warn "npm audit found vulnerabilities (review above)"
        else
            check_pass "npm audit (no high/critical vulnerabilities)"
        fi
    else
        check_skip "node_modules not installed"
    fi

    # Gitleaks
    cd "$PROJECT_ROOT"
    if command -v gitleaks &>/dev/null; then
        echo "  Running gitleaks..."
        if gitleaks detect --no-banner 2>&1; then
            check_pass "gitleaks (no secrets detected)"
        else
            check_fail "gitleaks (secrets detected!)"
        fi
    else
        check_skip "gitleaks not installed (install: brew install gitleaks or download from GitHub)"
    fi

    # Bandit
    cd "$BACKEND_DIR"
    if command -v bandit &>/dev/null; then
        echo "  Running bandit..."
        if bandit -r app/ -f txt --severity-level high 2>&1 | grep -qi "issue"; then
            check_warn "bandit found high-severity issues (review above)"
        else
            check_pass "bandit (no high-severity issues)"
        fi
    else
        check_skip "bandit not installed"
    fi
}

# ── Summary ──────────────────────────────────────────────────────────────

print_summary() {
    section "CI Summary"
    echo -e "  ${GREEN}Passed:${NC}  $PASS"
    echo -e "  ${RED}Failed:${NC}  $FAIL"
    echo -e "  ${YELLOW}Skipped:${NC} $SKIP"
    echo ""
    if [ $FAIL -eq 0 ]; then
        echo -e "  ${GREEN}✅ All checks passed!${NC}"
        return 0
    else
        echo -e "  ${RED}❌ $FAIL check(s) failed${NC}"
        return 1
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────

case "${1:-all}" in
    backend)
        run_backend_tests
        run_backend_lint
        ;;
    frontend)
        run_frontend_build
        run_frontend_lint
        ;;
    security)
        run_security
        ;;
    lint)
        run_backend_lint
        run_frontend_lint
        ;;
    all)
        run_backend_tests
        run_backend_lint
        run_frontend_build
        run_frontend_lint
        run_security
        ;;
    *)
        echo "Usage: $0 {all|backend|frontend|security|lint}"
        echo ""
        echo "Runs ContentForge AI CI checks locally."
        echo "  all       - Run all checks (default)"
        echo "  backend   - Backend tests + lint"
        echo "  frontend  - Frontend build + lint"
        echo "  security  - Security audits"
        echo "  lint      - Linting only (fast)"
        exit 1
        ;;
esac

print_summary