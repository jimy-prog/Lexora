#!/bin/bash
# Run this ONCE to make Lexora start automatically at login
# Usage: bash install_autostart.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.lexora.app.plist"
PYTHON=$(which python3)
LOG="$SCRIPT_DIR/lexora.log"

cat > "$PLIST" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lexora.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$SCRIPT_DIR/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG</string>
    <key>StandardErrorPath</key>
    <string>$LOG</string>
</dict>
</plist>
PLISTEOF

launchctl load "$PLIST"
echo ""
echo "✅  Lexora will now start automatically every time your Mac starts."
echo "    Open: http://localhost:8000"
echo ""
echo "    To stop auto-start:  launchctl unload $PLIST"
echo "    To check status:     launchctl list | grep lexora"
