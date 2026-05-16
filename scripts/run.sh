#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "🚀 Starting Garage Sale Inventory App..."

# Init DB if needed
python3 -c "
import sys
sys.path.insert(0, 'python')
from db import init_db
init_db()
" 2>/dev/null || true

# Kill existing processes
pkill -f "uvicorn python.main:app" 2>/dev/null || true
pkill -f "cloudflared tunnel" 2>/dev/null || true

sleep 1

# Start FastAPI
echo "💼 Starting backend on port 8000..."
uvicorn python.main:app --host 0.0.0.0 --port 8000 --reload &
UVI_PID=$!

sleep 2

# Start cloudflared tunnel
echo "🌐 Starting Cloudflared tunnel..."
cloudflared tunnel --url http://localhost:8000 &
CF_PID=$!

sleep 4

# Extract public URL from cloudflared logs
TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared*.log 2>/dev/null | head -1 || echo "")

if [ -n "$TUNNEL_URL" ]; then
  echo ""
  echo "🎉 App is live!"
  echo "  🌐 Public URL: $TUNNEL_URL"
  echo "  📱 Open this on your phone!"
  echo ""
else
  echo ""
  echo "⚠️  Tunnel starting... check logs:"
  echo "  tail -f /tmp/cloudflared*.log"
  echo ""
fi

echo "Press Ctrl+C to stop"
wait $UVI_PID
