#!/bin/bash
# Pulse Agent v2 - Installation Script

set -e

echo "========================================="
echo "  Pulse Agent v2 - Installation"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "📝 IMPORTANT: Please edit .env and configure your settings:"
    echo "   - Database credentials (PA_DB_*)"
    echo "   - API endpoint (PA_PUSH_URL)"
    echo "   - API token (PA_PUSH_TOKEN)"
    echo "   - Client/Site IDs (PA_CLIENT_ID, PA_SITE_ID)"
    echo ""
    echo "Edit with: nano .env"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create data directory
DATA_DIR=$(grep PA_DATA_DIR .env 2>/dev/null | cut -d'=' -f2 || echo "/tmp/pulse-agent-data")
echo "Creating data directory: $DATA_DIR"
mkdir -p "$DATA_DIR"
if [ $? -eq 0 ]; then
    echo "✓ Data directory created"
else
    echo "⚠️  Warning: Could not create data directory"
fi
echo ""

# Make scripts executable
chmod +x run.sh setup_docker.sh
echo "✓ Made scripts executable"
echo ""

# Check Docker permissions
echo "Checking Docker permissions..."
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null 2>&1; then
        echo "✓ Docker access is working"
    else
        echo "⚠️  Docker permission issue detected"
        echo ""
        read -p "Would you like to fix Docker permissions now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./setup_docker.sh
        else
            echo "Skipped. You can run './setup_docker.sh' later to fix this."
        fi
    fi
else
    echo "ℹ️  Docker not installed (optional for container metrics)"
fi
echo ""

echo "========================================="
echo "  Installation Complete! ✅"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure your settings:"
echo "   nano .env"
echo ""
echo "2. Test database connection:"
echo "   python3 -c 'from pulse_agent_complete.config import Config; from pulse_agent_complete.db_client import DatabaseClient; db = DatabaseClient(Config.DB_TYPE, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD); db.connect(); print(\"✓ Connected\"); db.disconnect()'"
echo ""
echo "3. Run the agent:"
echo "   ./run.sh"
echo ""
echo "4. Schedule with cron (optional):"
echo "   crontab -e"
echo "   Add: 0 * * * * cd $(pwd) && ./run.sh >> /var/log/pulse-agent.log 2>&1"
echo ""
