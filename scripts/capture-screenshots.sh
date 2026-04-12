#!/bin/bash
# ContentForge AI - Automated Screenshot Capture Script
# Uses Playwright with Chromium to capture UI screenshots

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
SCREENSHOT_DIR="docs/screenshots"

# Ensure we're in the project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo -e "${BLUE}📸 ContentForge AI Screenshot Capture${NC}"
echo "================================================"

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npx not found. Please install Node.js.${NC}"
    exit 1
fi

# Install Chromium if not present
echo -e "${YELLOW}🔧 Checking Chromium installation...${NC}"
if ! npx playwright install chromium 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing Chromium browser...${NC}"
    npx playwright install chromium
fi

echo -e "${GREEN}✅ Chromium ready${NC}"

# Check for existing processes and clean up
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Ensure screenshot directory exists
mkdir -p "$SCREENSHOT_DIR"

# Start Backend
echo -e "${BLUE}🚀 Starting backend on port $BACKEND_PORT...${NC}"
cd src/backend
source venv/bin/activate 2>/dev/null || echo -e "${YELLOW}⚠️  Using system Python${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health &>/dev/null || \
       curl -s http://localhost:$BACKEND_PORT/ &>/dev/null; then
        echo -e "${GREEN}✅ Backend ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start within 30 seconds${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Start Frontend
echo -e "${BLUE}🚀 Starting frontend on port $FRONTEND_PORT...${NC}"
cd src/frontend
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# Wait for frontend to be ready
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT &>/dev/null || \
       curl -s http://localhost:$FRONTEND_PORT/login &>/dev/null; then
        echo -e "${GREEN}✅ Frontend ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Frontend failed to start within 60 seconds${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Additional wait for full hydration
echo -e "${YELLOW}⏳ Waiting for page hydration...${NC}"
sleep 5

# Capture Screenshots
echo -e "${BLUE}📷 Capturing screenshots...${NC}"
echo "================================================"

# Login Page
echo -e "${YELLOW}📸 Login page...${NC}"
npx playwright screenshot \
    --browser=chromium \
    --viewport-size=1280,720 \
    --full-page \
    --wait-for-timeout=3000 \
    "http://localhost:$FRONTEND_PORT/login" \
    "$SCREENSHOT_DIR/login-automated.png" || echo -e "${RED}⚠️  Login screenshot failed${NC}"

# Dashboard (may redirect to login if not authenticated)
echo -e "${YELLOW}📸 Dashboard...${NC}"
npx playwright screenshot \
    --browser=chromium \
    --viewport-size=1280,720 \
    --full-page \
    --wait-for-timeout=3000 \
    "http://localhost:$FRONTEND_PORT" \
    "$SCREENSHOT_DIR/dashboard-automated.png" || echo -e "${RED}⚠️  Dashboard screenshot failed (may require auth)${NC}"

# Content Page
echo -e "${YELLOW}📸 Content page...${NC}"
npx playwright screenshot \
    --browser=chromium \
    --viewport-size=1280,720 \
    --full-page \
    --wait-for-timeout=3000 \
    "http://localhost:$FRONTEND_PORT/content" \
    "$SCREENSHOT_DIR/content-automated.png" || echo -e "${RED}⚠️  Content screenshot failed${NC}"

# Mobile viewport - Login
echo -e "${YELLOW}📸 Login page (mobile)...${NC}"
npx playwright screenshot \
    --browser=chromium \
    --viewport-size=375,812 \
    --full-page \
    --wait-for-timeout=3000 \
    "http://localhost:$FRONTEND_PORT/login" \
    "$SCREENSHOT_DIR/login-mobile-automated.png" || echo -e "${RED}⚠️  Mobile login screenshot failed${NC}"

echo "================================================"
echo -e "${GREEN}✅ Screenshot capture complete!${NC}"
echo -e "${BLUE}📁 Screenshots saved to: $SCREENSHOT_DIR/${NC}"

# List captured screenshots
echo ""
echo "Captured files:"
ls -lh $SCREENSHOT_DIR/*-automated.png 2>/dev/null || echo "No automated screenshots found"

# Cleanup
echo ""
echo -e "${YELLOW}🧹 Stopping services...${NC}"
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true
wait $BACKEND_PID 2>/dev/null || true
wait $FRONTEND_PID 2>/dev/null || true

echo -e "${GREEN}✅ Done!${NC}"
