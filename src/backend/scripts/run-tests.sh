#!/bin/bash
#
# Test runner script for ContentForge AI backend
#
# Usage:
#   ./scripts/run-tests.sh              # Run all tests
#   ./scripts/run-tests.sh -v           # Run with verbose output
#   ./scripts/run-tests.sh test_auth    # Run specific test file
#   ./scripts/run-tests.sh -k test_login # Run tests matching pattern
#   ./scripts/run-tests.sh --cov        # Run with coverage report
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_ROOT/tests"

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}ContentForge AI Test Suite${NC}"
echo -e "${BLUE}==================================${NC}"

# Check if we're in the right directory
if [ ! -d "$TEST_DIR" ]; then
    echo -e "${RED}Error: Tests directory not found at $TEST_DIR${NC}"
    exit 1
fi

# Change to backend directory
cd "$PROJECT_ROOT"

# Check for virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements.txt
fi

# Default test arguments
PYTEST_ARGS="-v"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --cov|--coverage)
            PYTEST_ARGS="$PYTEST_ARGS --cov=app --cov-report=term-missing --cov-report=html:htmlcov"
            shift
            ;;
        -k)
            PYTEST_ARGS="$PYTEST_ARGS -k $2"
            shift 2
            ;;
        -m)
            PYTEST_ARGS="$PYTEST_ARGS -m $2"
            shift 2
            ;;
        --integration)
            PYTEST_ARGS="$PYTEST_ARGS -m integration"
            shift
            ;;
        --unit)
            PYTEST_ARGS="$PYTEST_ARGS -m unit"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [TEST_FILE]"
            echo ""
            echo "Options:"
            echo "  --cov, --coverage   Run with coverage report"
            echo "  --integration       Run only integration tests"
            echo "  --unit              Run only unit tests"
            echo "  -k PATTERN          Run tests matching pattern"
            echo "  -m MARKER           Run tests with marker"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run all tests"
            echo "  $0 test_auth                # Run auth tests only"
            echo "  $0 -k test_login            # Run tests matching 'test_login'"
            echo "  $0 --cov                    # Run with coverage"
            echo "  $0 --unit                   # Run only unit tests"
            exit 0
            ;;
        -*)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
        *)
            # Specific test file or directory
            TEST_PATH="$TEST_DIR/$1"
            if [ -f "$TEST_PATH" ] || [ -d "$TEST_PATH" ]; then
                PYTEST_ARGS="$PYTEST_ARGS $TEST_PATH"
            else
                echo -e "${RED}Error: Test file not found: $TEST_PATH${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Set test environment variables
export APP_ENV="testing"
export DEBUG="true"
export SECRET_KEY="test-secret-key-for-testing-only"
export SUPABASE_URL="https://test.supabase.co"
export SUPABASE_KEY="test-anon-key"
export SUPABASE_SERVICE_ROLE_KEY="test-service-role-key"
export GROQ_API_KEY="test-groq-api-key"

# Run tests
echo -e "${YELLOW}Running tests with args: $PYTEST_ARGS${NC}"
echo ""

if pytest $PYTEST_ARGS "$TEST_DIR"; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}==================================${NC}"
    
    # Show coverage report if generated
    if [[ $PYTEST_ARGS == *"--cov"* ]] && [ -f "htmlcov/index.html" ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated at: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}Some tests failed!${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
