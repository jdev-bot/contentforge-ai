#!/bin/bash
set -e

# ContentForge AI - Development Setup Script
# One-command setup for local development

echo "🚀 Setting up ContentForge AI for local development..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}❌ $1 is required but not installed.${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 found${NC}"
        return 0
    fi
}

echo "📋 Checking prerequisites..."
check_command "git" || exit 1
check_command "docker" || exit 1
check_command "docker-compose" || check_command "docker compose" || exit 1
check_command "python3" || exit 1
check_command "node" || exit 1
check_command "npm" || exit 1
echo ""

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Create environment files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Created .env from .env.example - please update with your actual values!${NC}"
    else
        echo -e "${YELLOW}⚠️  No .env.example found - creating empty .env${NC}"
        touch .env
    fi
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi

# Backend environment
if [ ! -f "src/backend/.env" ]; then
    cat > src/backend/.env << 'EOF'
# Development environment for ContentForge AI Backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/contentforge
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
N8N_WEBHOOK_URL=http://localhost:5678/webhook
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
    echo -e "${YELLOW}⚠️  Created src/backend/.env - please update with your actual API keys!${NC}"
else
    echo -e "${GREEN}✅ src/backend/.env already exists${NC}"
fi

# Frontend environment
if [ ! -f "src/frontend/.env.local" ]; then
    cat > src/frontend/.env.local << 'EOF'
# Development environment for ContentForge AI Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
EOF
    echo -e "${YELLOW}⚠️  Created src/frontend/.env.local - please update with your actual values!${NC}"
else
    echo -e "${GREEN}✅ src/frontend/.env.local already exists${NC}"
fi

echo ""

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd src/backend
python3 -m venv venv 2>/dev/null || echo "Virtual environment already exists"
source venv/bin/activate || . venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ../..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# Install frontend dependencies
echo "⚡ Installing frontend dependencies..."
cd src/frontend
npm install
cd ../..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

# Create necessary directories
echo "📂 Creating project directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Pull Docker images for services
echo "🐳 Pulling Docker images for external services..."
docker-compose -f infra/docker/services.yml pull 2>/dev/null || docker compose -f infra/docker/services.yml pull 2>/dev/null || echo "Using standalone database setup"
echo ""

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. 🔑 Update environment files with your actual API keys:"
echo "   - .env"
echo "   - src/backend/.env"
echo "   - src/frontend/.env.local"
echo ""
echo "2. 🗄️  Start external services (PostgreSQL, Redis, n8n):"
echo "   ./scripts/dev-start.sh --services-only"
echo ""
echo "3. 🚀 Start all services:"
echo "   ./scripts/dev-start.sh"
echo ""
echo "4. 🌐 Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - n8n: http://localhost:5678"
echo ""
echo "For more information, see README.md"
