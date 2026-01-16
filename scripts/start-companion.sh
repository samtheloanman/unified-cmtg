#!/bin/bash
set -e

# Start Tailscale daemon in background
# Use userspace-networking to avoid TUN requirement if it fails
/usr/sbin/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock --tun=userspace-networking &

# Wait for tailscaled to start
sleep 5

# Check if we need to authenticate
if ! tailscale status > /dev/null 2>&1; then
    echo "⚠️  Tailscale not authenticated. Run this to auth:"
    echo "docker exec -it <container_id> tailscale up"
else
    echo "✅ Tailscale connected. IP: $(tailscale ip -4)"
fi

# Start the Web Server
echo "🚀 Starting Companion Server..."
if [ -d "/app/companion" ]; then
    cd /app/companion
    python3 server.py
else
    echo "❌ Error: /app/companion not found inside container!"
    exit 1
fi
