#!/bin/bash
# Docker Permissions Setup Script
# Adds current user to docker group and makes it persistent

set -e

echo "========================================="
echo "  Docker Permissions Setup"
echo "========================================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Warning: Docker is not installed"
    echo "To install Docker, visit: https://docs.docker.com/engine/install/"
    exit 0
fi

# Get current user
CURRENT_USER=$(whoami)
echo "Current user: $CURRENT_USER"
echo ""

# Check if user is already in docker group
if groups $CURRENT_USER | grep -q '\bdocker\b'; then
    echo "✓ User '$CURRENT_USER' is already in docker group"

    # Check if we can access Docker
    if docker ps &> /dev/null; then
        echo "✓ Docker access is working!"
        echo ""
        echo "No action needed. Docker is ready to use."
        exit 0
    else
        echo "⚠️  User is in docker group but session hasn't been updated"
        echo ""
        echo "To fix this, choose one of these options:"
        echo ""
        echo "Option 1 (Immediate - current session only):"
        echo "  Run: newgrp docker"
        echo "  Then: ./run.sh"
        echo ""
        echo "Option 2 (Persistent - log out and back in):"
        echo "  1. Log out of your session"
        echo "  2. Log back in"
        echo "  3. Run: ./run.sh"
        echo ""
        echo "Option 3 (Automatic - restart shell):"
        echo "  Run: exec su -l $CURRENT_USER"
        echo "  Then: cd $(pwd) && ./run.sh"
        exit 0
    fi
fi

# User is not in docker group, need to add
echo "❌ User '$CURRENT_USER' is NOT in docker group"
echo ""
echo "Adding user to docker group..."

# Try to add user to docker group
if sudo usermod -aG docker $CURRENT_USER; then
    echo "✓ Successfully added '$CURRENT_USER' to docker group"
    echo ""
    echo "========================================="
    echo "  Important: Action Required"
    echo "========================================="
    echo ""
    echo "The docker group has been added to your user account."
    echo "To make this take effect, you need to do ONE of the following:"
    echo ""
    echo "Option 1 (Recommended - Full logout):"
    echo "  1. Log out of your entire session (GUI or SSH)"
    echo "  2. Log back in"
    echo "  3. Run: docker ps"
    echo "  4. Should work without sudo!"
    echo ""
    echo "Option 2 (Quick - Current terminal only):"
    echo "  Run: newgrp docker"
    echo "  Note: This only affects the current terminal"
    echo ""
    echo "Option 3 (Restart shell):"
    echo "  Run: exec su -l $CURRENT_USER"
    echo "  Then: cd $(pwd)"
    echo ""
    echo "After doing one of the above, run:"
    echo "  ./run.sh"
    echo ""
    echo "To verify Docker access works:"
    echo "  docker ps"
    echo ""
else
    echo "❌ Failed to add user to docker group"
    echo ""
    echo "Please run manually:"
    echo "  sudo usermod -aG docker $CURRENT_USER"
    echo ""
    echo "Then log out and log back in."
    exit 1
fi
