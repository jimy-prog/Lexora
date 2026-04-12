#!/bin/sh
set -eu

mkdir -p /app/data /app/backups /app/uploads /app/static

if [ ! -f /app/data/lexora.db ] && [ -f /app/teacher_admin.db ]; then
  cp /app/teacher_admin.db /app/data/lexora.db
  echo "[Lexora] Seeded /app/data/lexora.db from existing teacher_admin.db"
fi

if [ ! -f /app/lexora_auth_password.txt ] && [ -f /app/auth_password.txt ]; then
  cp /app/auth_password.txt /app/lexora_auth_password.txt
  echo "[Lexora] Seeded lexora_auth_password.txt from existing auth_password.txt"
fi

exec "$@"
