#!/usr/bin/env bash
# Elite Research Pipeline — First-time setup
set -euo pipefail

echo "═══════════════════════════════════════════════"
echo "  Elite Research Pipeline — Setup"
echo "═══════════════════════════════════════════════"
echo

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'" 2>/dev/null || {
    echo "ERROR: Python 3.10+ is required"
    exit 1
}

# Install dependencies
echo "→ Installing Python dependencies..."
pip install -r requirements.txt
echo "  ✓ Dependencies installed"
echo

# Install Playwright browser for notebooklm login
echo "→ Installing Playwright Chromium browser..."
playwright install chromium
echo "  ✓ Playwright ready"
echo

# Initialize database
echo "→ Initializing SQLite database..."
python3 -c "
from pipeline.db import PipelineDB
db = PipelineDB()
db.connect()
db.close()
print('  ✓ Database initialized: pipeline.db')
"
echo

# Setup .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "→ Created .env from template"
    echo "  ⚠ Edit .env with your YouTube OAuth credentials"
    echo
fi

# YouTube OAuth setup guide
echo "═══════════════════════════════════════════════"
echo "  YouTube OAuth Setup (one-time)"
echo "═══════════════════════════════════════════════"
echo
echo "1. Go to https://console.cloud.google.com"
echo "2. Create a new project (or use existing)"
echo "3. Enable 'YouTube Data API v3' under APIs & Services → Library"
echo "4. Go to APIs & Services → Credentials"
echo "5. Create Credentials → OAuth client ID → Desktop app"
echo "6. Copy Client ID and Client Secret to .env"
echo "7. Set up OAuth consent screen:"
echo "   - Add scope: youtube.readonly"
echo "   - Add yourself as a test user"
echo
echo "After filling .env, the first pipeline run will open a browser"
echo "for YouTube OAuth authorization."
echo

# NotebookLM login
echo "═══════════════════════════════════════════════"
echo "  NotebookLM Login"
echo "═══════════════════════════════════════════════"
echo
echo "Run: notebooklm login"
echo "This opens Chromium — log in with your Google account."
echo "Session saves to ~/.notebooklm/storage_state.json"
echo "(Re-run every few weeks when session expires)"
echo

read -p "Run 'notebooklm login' now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    notebooklm login
    echo "  ✓ NotebookLM authenticated"
fi

echo
echo "═══════════════════════════════════════════════"
echo "  Setup complete!"
echo "═══════════════════════════════════════════════"
echo
echo "Next steps:"
echo "  1. Create a 'Research Queue' playlist on YouTube"
echo "  2. Set playlist_id in config.yaml"
echo "  3. Fill in .env with your YouTube OAuth credentials"
echo "  4. Add a few videos to your playlist"
echo "  5. Run: bash scripts/run_once.sh"
