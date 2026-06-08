#!/bin/bash
set -euo pipefail
PLIST_DEST="$HOME/Library/LaunchAgents/com.boss.ai-portfolio-sync.plist"
launchctl unload "$PLIST_DEST" 2>/dev/null || true
rm -f "$PLIST_DEST"
echo "ai-portfolio sync agent removed"
