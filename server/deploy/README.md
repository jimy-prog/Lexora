# Запуск Lexora

## Задача «открыть откуда угодно»

**Так было задумано по ADS:** веб-платформа должна быть доступна из интернета, а не только с одного компьютера.

- **Локально** (этот Mac, иногда та же Wi‑Fi) — после `bash deploy/start.sh` уже работает.
- **Откуда угодно** (мобильный интернет, другой город) — нужен **бесплатный Cloudflare Tunnel** + **свой домен** в Cloudflare.  
  **Пошагово, по-русски:** **[deploy/INTERNET_RU.md](INTERNET_RU.md)**

Кратко: получаешь токен в Cloudflare → добавляешь в `deploy/.env` строку `CLOUDFLARE_TUNNEL_TOKEN=...` → в панели туннеля указываешь сервис **`http://app:8000`** → снова **`bash deploy/start.sh`** (скрипт сам поднимет туннель, если токен есть).

При **первом** запуске скрипт может спросить токен сразу после паролей — можно нажать Enter и добавить позже в `.env`.

---

## Что нужно один раз

1. **Docker Desktop** с [docker.com](https://www.docker.com/products/docker-desktop/) — запущен (иконка кита).

2. В терминале перейти в папку проекта:

   ```bash
   cd ~/Desktop/teacher_admin
   ```

## Запуск

```bash
bash deploy/start.sh
```

Первый раз создастся `deploy/.env` и спросятся пароли (ввод не отображается — это нормально).

## Остановить

```bash
docker compose -f deploy/docker-compose.yml --env-file deploy/.env down
```

## Если порт занят

В `deploy/.env` поменяй `EXPOSE_PORT=8000` на например `8001` и снова `bash deploy/start.sh`.

---

Технические детали: [DEPLOY.md](../DEPLOY.md), архитектура: [docs/ADS_LEXORA.md](../docs/ADS_LEXORA.md).
