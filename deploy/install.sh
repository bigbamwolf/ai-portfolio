#!/bin/bash
# Installer for the ai-portfolio launchd auto refresh
# Loads the agent so portfolio.json regenerates every 15 minutes.

set -euo pipefail

PLIST_SRC="/Users/macbookair/Claude/ai-portfolio/deploy/com.boss.ai-portfolio-sync.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.boss.ai-portfolio-sync.plist"

cp "$PLIST_SRC" "$PLIST_DEST"
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo "ai-portfolio sync agent loaded"
echo "regenerates portfolio.json every 15 minutes"
echo "logs: /Users/macbookair/Claude/ai-portfolio/deploy/sync.out"
