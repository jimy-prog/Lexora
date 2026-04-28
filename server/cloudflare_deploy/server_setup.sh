#!/bin/bash
set -eu

APP_DIR="${1:-$HOME/lexora-app}"

mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/cloudflare_deploy"

echo "Lexora server folder prepared at: $APP_DIR"
echo "Next steps:"
echo "1. Install Docker and Docker Compose on this server"
echo "2. Add your SSH public key to this server user"
echo "3. Point GitHub Actions SERVER_PATH to: $APP_DIR"
