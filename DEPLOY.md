# Deploy Lexora

## Просто запустить у себя на компьютере

```bash
cd /путь/к/teacher_admin
bash deploy/start.sh
```

Нужен установленный и **запущенный** Docker Desktop. Подробности: **[deploy/README.md](deploy/README.md)**.

**Доступ из интернета (телефон вне Wi‑Fi и т.д.):** **[deploy/INTERNET_RU.md](deploy/INTERNET_RU.md)** — Cloudflare Tunnel + токен в `deploy/.env`; `start.sh` сам добавит `--profile tunnel`, если токен задан.

## Вручную (как раньше)

```bash
cp deploy/.env.example deploy/.env
# заполнить deploy/.env

docker compose -f deploy/docker-compose.yml --env-file deploy/.env up -d --build
```

Проверка: `curl http://127.0.0.1:8000/healthz` → `ok`.

## Только SQLite + Cloudflare (старый вариант)

См. [cloudflare_deploy/README.md](cloudflare_deploy/README.md).
