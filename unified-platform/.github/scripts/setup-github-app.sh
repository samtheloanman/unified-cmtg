#!/bin/bash
# GitHub App Setup Script for CMTG Conductor Bot
# This script helps create and configure the GitHub App

set -e

echo "========================================="
echo "CMTG Conductor Bot - GitHub App Setup"
echo "========================================="
echo ""

REPO="samtheloanman/unified-cmtg"
MANIFEST_FILE=".github/github-app-manifest.json"
WEBHOOK_SECRET="${1:-e7d28062a7bb33824b978a2ccc7b8d0d3ee4e278b95f03c3188757c92115f3fd}"

echo "📋 Step 1: GitHub App Creation"
echo "-------------------------------"
echo ""
echo "To create a GitHub App from manifest, you need to:"
echo "1. Go to: https://github.com/settings/apps/new?state=RANDOM_STATE"
echo "2. Paste the contents of: $MANIFEST_FILE"
echo "3. Click 'Create GitHub App from manifest'"
echo ""
echo "Alternatively, use the GitHub CLI (requires manual steps):"
echo ""
echo "Opening GitHub App creation URL..."
echo ""

# Generate the manifest URL
MANIFEST_CONTENT=$(cat "$MANIFEST_FILE")
echo "Manifest ready at: $(pwd)/$MANIFEST_FILE"
echo ""

echo "📋 Step 2: Manual GitHub App Configuration"
echo "-------------------------------------------"
echo ""
echo "After creating the app via web interface:"
echo "1. Note down the App ID"
echo "2. Generate a private key (download the .pem file)"
echo "3. Install the app on your repository"
echo "4. Note down the Installation ID"
echo ""

echo "🔐 Step 3: Store Credentials in MCP Vault"
echo "------------------------------------------"
echo ""
echo "Generated webhook secret: $WEBHOOK_SECRET"
echo ""
echo "Update your MCP Vault secrets.json with:"
echo ""
cat <<EOF
{
  "github": {
    "app_id": "YOUR_APP_ID",
    "installation_id": "YOUR_INSTALLATION_ID",
    "private_key_path": "/app/config/github-app-key.pem",
    "webhook_secret": "$WEBHOOK_SECRET",
    "personal_token": "$(gh auth token)"
  }
}
EOF
echo ""
echo ""

echo "📁 Step 4: Copy private key to MCP Vault"
echo "-----------------------------------------"
echo ""
echo "After downloading the .pem file from GitHub:"
echo "  cp ~/Downloads/your-app-name.*.private-key.pem /home/samalabam/code/custom-cmre-mcp/config/github-app-key.pem"
echo ""

echo "✅ Next Steps:"
echo "--------------"
echo "1. Create the GitHub App using the web interface"
echo "2. Save the credentials to MCP Vault"
echo "3. Run verification script: ./verify-github-app.sh"
echo ""
echo "For more details, see: implementation_plan.md"
