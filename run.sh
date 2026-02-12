#!/bin/bash
# Pulse Agent v2 - Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  Pulse Agent v2 - Starting"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please run ./install.sh first or create .env manually"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check required Python packages
echo "Checking dependencies..."
python3 -c "import dotenv, requests, psycopg2, docker, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Some dependencies are missing${NC}"
    echo "Run: pip install -r requirements.txt"
    echo "Continuing anyway..."
    echo ""
fi

# Create data directory if it doesn't exist
DATA_DIR=$(grep PA_DATA_DIR .env 2>/dev/null | cut -d'=' -f2 || echo "/tmp/pulse-agent-data")
if [ ! -z "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR" 2>/dev/null || true
fi

# Check Docker permissions
if command -v docker &> /dev/null; then
    if ! docker ps &> /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Warning: Docker permission denied${NC}"
        echo "Docker metrics will not be collected. To fix this, run:"
        echo "  ./setup_docker.sh"
        echo ""
    fi
fi

# Run the agent
echo "Running Pulse Agent..."
echo ""
python3 main.py

EXIT_CODE=$?

echo ""
echo "========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Pulse Agent completed successfully${NC}"
else
    echo -e "${RED}❌ Pulse Agent failed with exit code $EXIT_CODE${NC}"
fi
echo "========================================="

exit $EXIT_CODE
