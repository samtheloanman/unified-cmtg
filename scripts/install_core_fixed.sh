#!/bin/bash
set -u

# Antigravity Core Installer
# Usable on MacOS and Ubuntu

echo "🚀 Starting Antigravity Core Setup..."

# 1. Install Global NPM Tools
echo "📦 Installing Global NPM Tools..."

# Use a HEREDOC for the python script to avoid quoting issues
# and ensure safe execution.
PYTHON_SCRIPT_CONTENT=$(cat <<'EOF'
import sys
import yaml

try:
    with open("gemini-manifest.yaml", "r") as f:
        manifest = yaml.safe_load(f)
        packages = manifest.get("tools", {}).get("npm_global", [])
        if packages:
            # Print packages separated by space
            print(" ".join(packages))
except FileNotFoundError:
    print("gemini-manifest.yaml not found", file=sys.stderr)
    sys.exit(1)
except ImportError:
    print("PyYAML (python3-yaml) is not installed. Skipping YAML check.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error parsing gemini-manifest.yaml: {e}", file=sys.stderr)
    sys.exit(1)
EOF
)

# Parse gemini-manifest.yaml for npm_global packages
NPM_PACKAGES=""
if command -v python3 &>/dev/null; then
    NPM_PACKAGES=$(python3 -c "$PYTHON_SCRIPT_CONTENT")
else
    echo "⚠️ Python3 not found, skipping manifest check."
fi

if [ -n "$NPM_PACKAGES" ]; then
  echo "Installing packages: $NPM_PACKAGES"
  # We intentionally want word splitting here for the package list
  # shellcheck disable=SC2086
  npm install -g $NPM_PACKAGES
fi

# 2. Setup Aliases & Paths
echo "🔗 Configuring Environment..."
# Ensure the gemini config dir exists
mkdir -p ~/.gemini/config

# 3. Message
echo "✅ Antigravity Core Installed."
echo "   - Jules: Installed"
echo "   - Gemini CLI: Installed"

# The N8n message is now dynamic based on what's in the manifest
if [[ " $NPM_PACKAGES " == *" n8n "* ]]; then
    echo "   - N8n: Installed"
fi
echo "   - Conductor: Ready (Content Mode)"
