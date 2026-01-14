#!/bin/bash
# Verification script for GitHub App setup

set -e

echo "🔍 Verifying GitHub App Configuration"
echo "======================================"
echo ""

# Check if secrets.json exists
if [ ! -f "/home/samalabam/code/custom-cmre-mcp/config/secrets.json" ]; then
    echo "❌ MCP Vault secrets.json not found"
    exit 1
fi

echo "✅ MCP Vault secrets.json exists"

# Check if GitHub private key exists
if [ -f "/home/samalabam/code/custom-cmre-mcp/config/github-app-key.pem" ]; then
    echo "✅ GitHub App private key found"
else
    echo "⚠️  GitHub App private key not found (will be needed later)"
fi

# Check MCP Vault is running
echo ""
echo "Checking MCP Vault server..."
if curl -s http://localhost:8888/sse > /dev/null 2>&1; then
    echo "✅ MCP Vault server is running on port 8888"
else
    echo "❌ MCP Vault server is not accessible"
    echo "   Start it with: cd /home/samalabam/code/custom-cmre-mcp && docker-compose up -d"
    exit 1
fi

# Check GitHub CLI authentication
echo ""
echo "Checking GitHub CLI..."
if gh auth status > /dev/null 2>&1; then
    echo "✅ GitHub CLI authenticated"
    gh auth status | grep "Logged in to"
else
    echo "❌ GitHub CLI not authenticated"
    exit 1
fi

# Check repository access
echo ""
echo "Checking repository access..."
if gh repo view samtheloanman/unified-cmtg > /dev/null 2>&1; then
    echo "✅ Can access samtheloanman/unified-cmtg"
else
    echo "❌ Cannot access repository"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ All prerequisites verified!"
echo "========================================="
echo ""
echo "Next: Create the GitHub App using setup-github-app.sh"
