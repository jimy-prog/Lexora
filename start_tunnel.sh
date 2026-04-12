#!/bin/bash
# ═══════════════════════════════════════════════════════
#  Lexora — Start with Cloudflare Tunnel
#  Run this instead of "python3 main.py" when you want
#  phone/outside access.
# ═══════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "🚀 Starting Lexora..."
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing Cloudflare Tunnel (one time only)..."
    if command -v brew &> /dev/null; then
        brew install cloudflare/cloudflare/cloudflared
    else
        echo "❌ Homebrew not found. Install it first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "   Then run: brew install cloudflare/cloudflare/cloudflared"
        exit 1
    fi
fi

# Start the app in background
python3 main.py &
APP_PID=$!
echo "✅ App started (PID $APP_PID)"
sleep 2

# Start tunnel
echo ""
echo "🌐 Starting Cloudflare Tunnel..."
echo "   Your public URL will appear below — open it on your iPhone!"
echo ""
cloudflared tunnel --url http://localhost:8000 &
TUNNEL_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  App is running!"
echo "  Local:  http://localhost:8000"
echo "  Phone:  See the trycloudflare.com URL above ↑"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Set SESSION_SECRET_KEY and DEFAULT_ADMIN_PASSWORD for production use"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Press Ctrl+C to stop everything"
echo ""

# Wait and clean up on exit
trap "kill $APP_PID $TUNNEL_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait $TUNNEL_PID
