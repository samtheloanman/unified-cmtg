#!/bin/bash
set -e

CONDUCTOR_DIR="$(dirname "$0")"
VENV_DIR="$CONDUCTOR_DIR/venv"

# 1. Check/Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "🏗️  Creating virtual environment for Conductor..."
    python3 -m venv "$VENV_DIR"
    
    echo "📦 Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$CONDUCTOR_DIR/requirements.txt"
fi

# 2. Run Dashboard
echo "🚀 Launching Conductor Dashboard..."
source "$VENV_DIR/bin/activate"
streamlit run "$CONDUCTOR_DIR/dashboard/app.py"
