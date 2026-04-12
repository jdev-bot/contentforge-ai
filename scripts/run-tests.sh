#!/bin/bash
#
# Test runner script for ContentForge AI Backend
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}ContentForge AI Test Suite${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/src/backend"
TEST_DIR="$PROJECT_ROOT/tests"

# Check if we're in the right place
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi

# Set up Python path
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# Set test environment
export APP_ENV="test"
export SECRET_KEY="test-secret-key-for-testing-only"
export SUPABASE_URL="https://test.supabase.co"
export SUPABASE_KEY="test-anon-key"
export SUPABASE_SERVICE_ROLE_KEY="test-service-role-key"
export GROQ_API_KEY="test-groq-api-key"
export DEBUG="true"

echo -e "${YELLOW}Environment:${NC}"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  APP_ENV: $APP_ENV"
echo ""

# Check for pytest
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found. Install with: pip install pytest pytest-asyncio${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pytest found${NC}"
echo ""

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
echo ""

cd "$PROJECT_ROOT"

# Run with coverage if available, otherwise just run tests
if python3 -c "import pytest_cov" 2>/dev/null; then
    pytest "$TEST_DIR" -v --tb=short --cov=src/backend/app --cov-report=term-missing "$@"
else
    pytest "$TEST_DIR" -v --tb=short "$@"
fi

TEST_EXIT_CODE=$?

echo ""
echo -e "${GREEN}================================${NC}"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed.${NC}"
fi
echo -e "${GREEN}================================${NC}"

exit $TEST_EXIT_CODE
