#!/bin/bash
# ============================================
# ContentForge AI - Frontend Deployment Script
# Deploys Next.js frontend to Vercel
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
FRONTEND_DIR="src/frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ContentForge AI - Frontend Deploy    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo -e "${RED}Error: vercel.json not found. Are you in the project root?${NC}"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}Please log in to Vercel:${NC}"
    vercel login
fi

# Environment check
if [ -z "${VERCEL_TOKEN:-}" ]; then
    echo -e "${YELLOW}Note: VERCEL_TOKEN not set. Will use interactive login.${NC}"
fi

echo -e "${BLUE}Step 1: Checking frontend build...${NC}"
cd "${FRONTEND_DIR}"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Run linting
echo -e "${BLUE}Step 2: Running linter...${NC}"
npm run lint || echo -e "${YELLOW}Linting completed with warnings${NC}"

# Build locally first to catch errors early
echo -e "${BLUE}Step 3: Building locally...${NC}"
npm run build

cd ../..

# Deploy to Vercel
echo -e "${BLUE}Step 4: Deploying to Vercel...${NC}"

if [ "${1:-}" == "--prod" ] || [ "${1:-}" == "-p" ]; then
    echo -e "${YELLOW}Deploying to PRODUCTION...${NC}"
    vercel --prod --confirm
else
    echo -e "${YELLOW}Deploying to PREVIEW...${NC}"
    vercel --confirm
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Frontend deployment complete!        ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  - Check deployment status: vercel --version"
echo "  - View logs: vercel logs --tail"
echo "  - Open dashboard: vercel dashboard"
echo ""
echo -e "${YELLOW}Tip: Use '$0 --prod' to deploy to production${NC}"