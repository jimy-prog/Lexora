#!/usr/bin/env bash
# Lexora — запуск одной командой (нужен установленный Docker).
# Из папки проекта:  bash deploy/start.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="$ROOT/deploy/.env"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Lexora — проверка Docker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v docker >/dev/null 2>&1; then
  echo ""
  echo "Docker не найден. Сделай так:"
  echo "  • Mac: установи «Docker Desktop» с docker.com и запусти его."
  echo "  • Потом снова запусти этот скрипт."
  echo ""
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo ""
  echo "Docker установлен, но не запущен. Запусти Docker Desktop и повтори."
  echo ""
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo ""
  echo "Первый раз: создам файл deploy/.env (секреты только у тебя на диске)."
  echo "Используй для паролей буквы и цифры, без пробелов и без символов @ # & \$"
  echo ""
  python3 << 'PY'
from pathlib import Path
import getpass
import secrets

deploy = Path("deploy")
env_path = deploy / ".env"

def ask(label: str) -> str:
    while True:
        a = getpass.getpass(label + ": ")
        b = getpass.getpass("Ещё раз для проверки: ")
        if a != b:
            print("Пароли не совпали, попробуй снова.\n")
            continue
        if len(a) < 8:
            print("Минимум 8 символов.\n")
            continue
        bad = set('@#&$ \n\t')
        if any(c in bad for c in a):
            print("Убери пробелы и символы @ # & $\n")
            continue
        return a

session_key = secrets.token_hex(32)
print("Пароль для ВХОДА на сайт (пользователь owner):")
admin_pw = ask("Пароль админа")
print("\nПароль для базы данных (можно такой же):")
db_pw = ask("Пароль базы")

lines = [
    f"SESSION_SECRET_KEY={session_key}",
    f"DEFAULT_ADMIN_PASSWORD={admin_pw}",
    f"POSTGRES_PASSWORD={db_pw}",
    "APP_NAME=Lexora",
    "POSTGRES_USER=lexora",
    "POSTGRES_DB=lexora",
    "EXPOSE_PORT=8000",
]
print("\n─── Доступ из интернета (телефон вне Wi‑Fi, другая страна) ───")
print("Без токена Cloudflare сайт работает только на этом Mac / в одной Wi‑Fi.")
print("Пошаговая инструкция:  deploy/INTERNET_RU.md")
tok = input("Если токен уже есть — вставь одной строкой (или Enter — пропустить): ").strip()
if tok:
    lines.append(f"CLOUDFLARE_TUNNEL_TOKEN={tok}")
    print("Токен сохранён — при запуске поднимется Cloudflare Tunnel.")
env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nСохранено: {env_path}")
PY
fi

echo ""
echo "Собираю и запускаю контейнеры (может занять минуту)..."

TUNNEL_ARGS=()
if grep -qE '^CLOUDFLARE_TUNNEL_TOKEN=.+' "$ENV_FILE" 2>/dev/null; then
  TUNNEL_ARGS=( --profile tunnel )
  echo "(Включён Cloudflare Tunnel — см. deploy/INTERNET_RU.md для настройки hostname)"
fi

docker compose "${TUNNEL_ARGS[@]}" -f deploy/docker-compose.yml --env-file "$ENV_FILE" up -d --build

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Готово"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  На этом компьютере:  http://127.0.0.1:8000/"
if [[ ${#TUNNEL_ARGS[@]} -gt 0 ]]; then
  echo ""
  echo "  Из интернета: HTTPS-адрес смотри в Cloudflare (Zero Trust → Networks → Connectors → твой туннель)."
  echo "  В настройке hostname должен быть URL:  http://app:8000"
else
  echo ""
  echo "  С телефона ВНЕ домашнего Wi‑Fi: нужен туннель — см. deploy/INTERNET_RU.md"
  echo "  Добавь CLOUDFLARE_TUNNEL_TOKEN в deploy/.env и снова: bash deploy/start.sh"
fi
echo ""
echo "  Логин: owner  |  Пароль: тот, что для «входа на сайт»"
echo ""
echo "  Остановить:  docker compose -f deploy/docker-compose.yml --env-file deploy/.env down"
echo ""
