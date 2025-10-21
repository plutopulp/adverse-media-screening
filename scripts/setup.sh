#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Adverse Media Screening - Setup Script"
echo "=========================================="
echo ""

# Track if setup is successful
SETUP_SUCCESS=true

# Check Docker installation
echo -n "Checking Docker installation... "
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC}"
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker Desktop from: https://docs.docker.com/get-docker/"
    SETUP_SUCCESS=false
else
    echo -e "${GREEN}✓${NC}"
fi

# Check Docker daemon is running
if [ "$SETUP_SUCCESS" = true ]; then
    echo -n "Checking Docker daemon is running... "
    if ! docker ps &> /dev/null; then
        echo -e "${RED}✗${NC}"
        echo -e "${RED}Error: Docker daemon is not running.${NC}"
        echo "Please start Docker Desktop and try again."
        SETUP_SUCCESS=false
    else
        echo -e "${GREEN}✓${NC}"
    fi
fi

# Check Docker Compose v2
if [ "$SETUP_SUCCESS" = true ]; then
    echo -n "Checking Docker Compose v2... "
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}✗${NC}"
        echo -e "${RED}Error: Docker Compose v2 is not available.${NC}"
        echo "Please upgrade to Docker Desktop with Compose v2 support."
        SETUP_SUCCESS=false
    else
        COMPOSE_VERSION=$(docker compose version --short)
        echo -e "${GREEN}✓${NC} (version ${COMPOSE_VERSION})"
    fi
fi

# Check Make (optional)
echo -n "Checking Make (optional)... "
if ! command -v make &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}"
    echo -e "${YELLOW}Warning: Make is not installed. You can still use docker compose commands directly.${NC}"
else
    echo -e "${GREEN}✓${NC}"
fi

# Exit if critical dependencies are missing
if [ "$SETUP_SUCCESS" = false ]; then
    echo ""
    echo -e "${RED}Setup failed due to missing dependencies.${NC}"
    exit 1
fi

echo ""
echo "Creating environment configuration files..."
echo ""

# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create AI service .env.secrets
AI_SECRETS_FILE="$PROJECT_ROOT/services/ai/.env.secrets"
if [ -f "$AI_SECRETS_FILE" ]; then
    echo -e "${YELLOW}⚠${NC}  $AI_SECRETS_FILE already exists, skipping..."
else
    cat > "$AI_SECRETS_FILE" << 'EOF'
# =============================================================================
# SECRETS FILE - DO NOT COMMIT TO GIT
# =============================================================================
# This file contains API keys and other sensitive data that override .env.defaults.
# The .env.defaults file contains placeholder keys - replace them here with your real keys.

# REQUIRED: Add your real OpenAI API key here (replaces placeholder in .env.defaults)
# Get one at: https://platform.openai.com/api-keys
OPENAI__API_KEY=

# OPTIONAL: Add your real Anthropic API key if you want to use Claude models
# Get one at: https://console.anthropic.com/account/keys
# ANTHROPIC__API_KEY=

# OPTIONAL: Override any other settings from .env.defaults here
# Examples:
# DEFAULT_LLM_PROVIDER=anthropic
# LOG_LEVEL=DEBUG
EOF
    echo -e "${GREEN}✓${NC}  Created $AI_SECRETS_FILE"
fi

# Create Web service .env.local (Next.js convention)
WEB_LOCAL_FILE="$PROJECT_ROOT/services/web/.env.local"
if [ -f "$WEB_LOCAL_FILE" ]; then
    echo -e "${YELLOW}⚠${NC}  $WEB_LOCAL_FILE already exists, skipping..."
else
    cat > "$WEB_LOCAL_FILE" << 'EOF'
# =============================================================================
# LOCAL ENVIRONMENT - DO NOT COMMIT TO GIT
# =============================================================================
# This file overrides values from .env (Next.js convention)
# It is automatically loaded by Next.js and takes precedence over .env

# Currently no local overrides are needed for development.
# Add environment-specific overrides here if needed.
# Examples:
# AI_SERVICE_URL=http://localhost:5001  (if running services outside Docker)
EOF
    echo -e "${GREEN}✓${NC}  Created $WEB_LOCAL_FILE"
fi

echo ""
echo -e "${GREEN}=========================================="
echo -e "  Setup completed successfully! ✓"
echo -e "==========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Add your real OpenAI API key to replace the placeholder:"
echo -e "   ${YELLOW}services/ai/.env.secrets${NC}"
echo ""
echo "   Note: .env.defaults has placeholder keys - replace them in .env.secrets"
echo ""
echo "2. Start the application:"
echo -e "   ${YELLOW}make start${NC}"
echo "   or"
echo -e "   ${YELLOW}cd docker && docker compose up -d${NC}"
echo ""
echo "3. Access the application at:"
echo -e "   🌐 Web UI: ${BLUE}http://localhost:3000${NC}"
echo -e "   📚 API Docs: ${BLUE}http://localhost:5001/docs${NC}"
echo ""

