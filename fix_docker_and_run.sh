#!/bin/bash
# Fix Docker permissions and run Pulse Agent in a new session

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  Docker Fix + Run"
echo "========================================="
echo ""

# Check if user is in docker group
if ! groups | grep -q '\bdocker\b'; then
    echo "Adding user to docker group..."
    sudo usermod -aG docker $USER
    echo "✓ User added to docker group"
    echo ""
fi

echo "Starting new session with docker access..."
echo "This will run Pulse Agent with proper Docker permissions."
echo ""

# Use sg (set group) to run in docker group context
# This is persistent within this shell
exec sg docker -c "cd '$SCRIPT_DIR' && ./run.sh"
