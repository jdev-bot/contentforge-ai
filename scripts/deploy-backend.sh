#!/bin/bash
# ============================================
# ContentForge AI - Backend Deployment Script
# Deploys FastAPI backend to Render
# ============================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="contentforge-ai"
RENDER_SERVICE_NAME="contentforge-ai-api"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ContentForge AI - Backend Deploy     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}Error: render.yaml not found. Are you in the project root?${NC}"
    exit 1
fi

# Check environment variables
if [ -z "${RENDER_API_KEY:-}" ]; then
    echo -e "${YELLOW}RENDER_API_KEY not set. Some operations may fail.${NC}"
    echo -e "${YELLOW}Get your API key from: https://dashboard.render.com/settings/api-keys${NC}"
fi

echo -e "${BLUE}Step 1: Validating Docker configuration...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found locally. Skipping local build test.${NC}"
else
    echo -e "${BLUE}Building Docker image locally...${NC}"
    docker build -f infra/docker/Dockerfile.backend -t contentforge-ai-backend:test .
    echo -e "${GREEN}✓ Docker build successful${NC}"
fi

echo -e "${BLUE}Step 2: Checking render.yaml syntax...${NC}"
if command -v yq &> /dev/null; then
    yq eval '.' render.yaml > /dev/null 2>&1 && echo -e "${GREEN}✓ render.yaml is valid YAML${NC}" || echo -e "${YELLOW}! render.yaml syntax warning${NC}"
else
    echo -e "${YELLOW}yq not installed. Skipping YAML validation.${NC}"
fi

echo -e "${BLUE}Step 3: Pre-deployment checklist...${NC}"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Warning: .env.production not found!${NC}"
    echo -e "${YELLOW}Create it from .env.example before deploying.${NC}"
fi

# Check if required files exist
required_files=(
    "src/backend/requirements.txt"
    "src/backend/app/main.py"
    "infra/docker/Dockerfile.backend"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found: $file${NC}"
    else
        echo -e "${RED}✗ Missing: $file${NC}"
    fi
done

echo ""
echo -e "${BLUE}Step 4: Render Deployment Options${NC}"
echo ""
echo "Option 1: Deploy via Render Dashboard (Recommended)"
echo "  1. Go to: https://dashboard.render.com/blueprints"
echo "  2. Click 'New Blueprint Instance'"
echo "  3. Connect your GitHub repository"
echo "  4. Select the blueprint from render.yaml"
echo ""
echo "Option 2: Deploy via Render CLI"
echo "  Install: curl https://raw.githubusercontent.com/render-oss/render-cli/main/install.sh | bash"
echo "  Login:   render login"
echo "  Deploy:  render blueprint apply"
echo ""

if command -v render &> /dev/null; then
    echo -e "${GREEN}Render CLI found!${NC}"
    
    if [ "${1:-}" == "--apply" ] || [ "${1:-}" == "-a" ]; then
        echo -e "${YELLOW}Applying blueprint...${NC}"
        render blueprint apply
    else
        echo -e "${YELLOW}Run with --apply flag to deploy automatically${NC}"
    fi
else
    echo -e "${YELLOW}Render CLI not found. Please use Option 1 (Dashboard).${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Post-deployment verification${NC}"
echo ""
echo "After deployment, verify:"
echo "  - API Health: curl https://${RENDER_SERVICE_NAME}.onrender.com/api/v1/health"
echo "  - API Docs:   https://${RENDER_SERVICE_NAME}.onrender.com/docs"
echo "  - Dashboard:  https://dashboard.render.com/web/${RENDER_SERVICE_NAME}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Backend deployment guide complete!   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Required Environment Variables to set in Render Dashboard:${NC}"
grep -E '^\s+- key:' render.yaml | sed 's/.*- key: //' | grep -v 'generateValue\|fromService' | while read -r key; do
    echo "  - $key"
done
echo ""
echo -e "${YELLOW}Note: Variables marked with 'sync: false' must be set manually in Render dashboard.${NC}"