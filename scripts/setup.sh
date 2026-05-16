#!/usr/bin/env bash
set -e

echo "🛠️  Setting up Garage Sale Inventory App..."

cd "$(dirname "$0")/.."

# Create directories
mkdir -p data uploads

# Install Python deps
if [ -f python/requirements.txt ]; then
  pip install -r python/requirements.txt -q
fi

# Init database
python3 -c "
import sys
sys.path.insert(0, 'python')
from db import init_db
init_db()
print('Database initialized')
"

# Check cloudflared
if ! command -v cloudflared &> /dev/null; then
  echo "⚠️  cloudflared not found. Downloading..."
  curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb 2>/dev/null || true
  if [ -f /tmp/cloudflared.deb ]; then
    sudo dpkg -i /tmp/cloudflared.deb 2>/dev/null || true
  fi
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set API key for AI vision (optional):"
echo "     export OPENAI_API_KEY=sk-..."
echo ""
echo "  2. Start the app:"
echo "     ./scripts/run.sh"
echo ""
