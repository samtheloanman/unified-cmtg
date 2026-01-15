#!/bin/bash
# Self-Hosted GitHub Actions Runner Setup Script
# Run this on dell-brain to install and configure the runner

set -e

RUNNER_VERSION="2.321.0"
RUNNER_DIR="$HOME/actions-runner"
REPO="samtheloanman/unified-cmtg"

echo "========================================="
echo "GitHub Actions Runner Setup"
echo "========================================="
echo ""
echo "Repository: $REPO"
echo "Runner directory: $RUNNER_DIR"
echo "Runner version: $RUNNER_VERSION"
echo ""

# Check if runner directory exists
if [ -d "$RUNNER_DIR" ]; then
    echo "⚠️  Runner directory already exists: $RUNNER_DIR"
    read -p "Remove existing installation? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing runner..."
        cd "$RUNNER_DIR"
        if [ -f "./svc.sh" ]; then
            sudo ./svc.sh stop || true
            sudo ./svc.sh uninstall || true
        fi
        cd ..
        rm -rf "$RUNNER_DIR"
    else
        echo "Aborting. Remove $RUNNER_DIR manually and try again."
        exit 1
    fi
fi

echo "📦 Step 1: Downloading GitHub Actions Runner"
echo "----------------------------------------------"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
  -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo "✅ Downloaded runner package"
echo ""

echo "📦 Step 2: Extracting runner"
echo "-----------------------------"
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
echo "✅ Extracted runner"
echo ""

echo "🔑 Step 3: Getting registration token from GitHub"
echo "---------------------------------------------------"
RUNNER_TOKEN=$(gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/${REPO}/actions/runners/registration-token \
  --jq .token)

if [ -z "$RUNNER_TOKEN" ]; then
    echo "❌ Failed to get registration token"
    echo "Make sure you have admin access to the repository"
    exit 1
fi

echo "✅ Got registration token"
echo ""

echo "⚙️  Step 4: Configuring runner"
echo "------------------------------"
./config.sh \
  --url "https://github.com/${REPO}" \
  --token "${RUNNER_TOKEN}" \
  --name "dell-brain-conductor" \
  --labels "dell-brain,conductor,mcp-enabled,self-hosted,Linux,X64" \
  --work "_work" \
  --unattended \
  --replace

echo "✅ Runner configured"
echo ""

echo "🔧 Step 5: Installing runner as a service"
echo "-------------------------------------------"
sudo ./svc.sh install
echo "✅ Service installed"
echo ""

echo "🚀 Step 6: Starting runner service"
echo "------------------------------------"
sudo ./svc.sh start
echo "✅ Service started"
echo ""

echo "========================================="
echo "✅ Runner Installation Complete!"
echo "========================================="
echo ""
echo "Runner name: dell-brain-conductor"
echo "Labels: dell-brain, conductor, mcp-enabled"
echo ""
echo "Check status with:"
echo "  sudo $RUNNER_DIR/svc.sh status"
echo ""
echo "View logs with:"
echo "  journalctl -u actions.runner.${REPO//\//-}.dell-brain-conductor.service -f"
echo ""
echo "Next: Create GitHub Actions workflows in .github/workflows/"
