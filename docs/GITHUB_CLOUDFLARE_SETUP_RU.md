# Lexora: простой гайд для GitHub + Deploy + Cloudflare

## 1. Что мы строим

Наша схема будет такой:

`Ты -> GitHub branch -> автодеплой тестовой версии -> ты проверяешь -> потом production`

То есть:

- я меняю код
- изменения идут в новую ветку
- GitHub отправляет код на сервер
- сервер поднимает сайт через Docker
- Cloudflare Tunnel открывает доступ к сайту
- ты проверяешь
- если нравится, потом отдельно запускаешь production deploy

## 2. Очень важный момент

`GitHub Pages` не подходит для этого проекта.

Причина:

- GitHub Pages умеет только статические сайты
- твой проект это FastAPI-приложение с базой данных, логикой сервера и загрузкой файлов

Поэтому GitHub у нас будет:

- хранить код
- запускать автоматический deploy

А сам сайт будет работать на сервере.

## 3. Что уже подготовлено в проекте

Готовые файлы:

- [cloudflare_deploy/README.md](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/README.md)
- [cloudflare_deploy/docker-compose.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/docker-compose.yml)
- [cloudflare_deploy/Dockerfile](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/Dockerfile)
- [cloudflare_deploy/cloudflare_main.py](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/cloudflare_main.py)
- [cloudflare_deploy/entrypoint.sh](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/entrypoint.sh)
- [cloudflare_deploy/.env.example](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/.env.example)
- [.github/workflows/staging.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/staging.yml)
- [.github/workflows/staging-direct.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/staging-direct.yml)
- [.github/workflows/production.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/production.yml)

## 4. Что тебе нужно подготовить

Нужно 3 вещи:

1. GitHub repository
2. сервер
3. Cloudflare Tunnel

## 5. Шаг 1. Создай GitHub repository

Сделай новый репозиторий, например:

- `lexora`

Потом загрузи туда проект.

Если репозиторий уже есть, просто используй его.

## 6. Шаг 2. Подготовь сервер

Подойдёт любой VPS:

- Ubuntu 22.04 или 24.04
- 2 GB RAM минимум
- 1 vCPU минимум

На сервере нужно установить:

- Docker
- Docker Compose plugin

После этого:

1. Подключись к серверу по SSH
2. Создай папку, например:

```bash
mkdir -p ~/lexora-app
```

Можно использовать helper script:

```bash
bash cloudflare_deploy/server_setup.sh ~/lexora-app
```

## 7. Шаг 3. Настрой SSH-доступ для GitHub Actions

Нужно, чтобы GitHub мог заходить на сервер.

### Что сделать

1. На своём компьютере создай SSH key, если его нет:

```bash
ssh-keygen -t ed25519 -C "lexora-deploy"
```

2. У тебя появятся 2 файла:

- приватный ключ
- публичный ключ

3. Публичный ключ добавь на сервер в:

```bash
~/.ssh/authorized_keys
```

4. Приватный ключ потом добавишь в GitHub Secrets

## 8. Шаг 4. Создай Cloudflare Tunnel

В Cloudflare сделай:

1. Зайди в Zero Trust
2. Открой `Networks` -> `Tunnels`
3. Создай новый tunnel
4. Выбери Docker
5. Получи `Tunnel Token`

Этот токен потом нужно сохранить в GitHub Secrets.

Если домена пока нет, у тебя есть 2 варианта:

1. временно тестировать сайт просто по IP сервера
2. позже подключить Cloudflare Tunnel

Для временного теста по IP используй файл:

- [cloudflare_deploy/docker-compose.direct.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/cloudflare_deploy/docker-compose.direct.yml)

Тогда сайт будет открываться так:

- `http://IP_СЕРВЕРА:8000`

Если хочешь сразу через Cloudflare, тогда делай tunnel setup.

Но лучше сразу создать тестовый hostname вида:

- `staging.<твой-домен>`
- или потом, когда будет домен

Если домена пока нет, можно пока поднять просто сервер и тестировать локально по IP/портам до подключения домена.

## 9. Шаг 5. Добавь Secrets в GitHub

Открой в GitHub:

`Repository -> Settings -> Secrets and variables -> Actions`

Потом создай 2 environment:

- `staging`
- `production`

И в каждый environment добавь такие secrets:

### Обязательные secrets

- `SSH_PRIVATE_KEY`
- `SERVER_HOST`
- `SERVER_PORT`
- `SERVER_USER`
- `SERVER_PATH`
- `SESSION_SECRET_KEY`
- `DEFAULT_ADMIN_PASSWORD`
- `CLOUDFLARE_TUNNEL_TOKEN`

### Пример значений

- `SERVER_HOST` = IP сервера
- `SERVER_PORT` = `22`
- `SERVER_USER` = например `ubuntu`
- `SERVER_PATH` = `/home/ubuntu/lexora-app`
- `SESSION_SECRET_KEY` = длинный случайный секрет
- `DEFAULT_ADMIN_PASSWORD` = временный пароль админа
- `CLOUDFLARE_TUNNEL_TOKEN` = токен из Cloudflare

Важно:

- для `staging` и `production` можно использовать разные токены
- лучше использовать разные `SERVER_PATH`

Например:

- staging: `/home/ubuntu/lexora-staging`
- production: `/home/ubuntu/lexora-production`

## 10. Шаг 6. Как будет работать staging

Файл:

- [.github/workflows/staging.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/staging.yml)

Он запускается когда ты пушишь ветки:

- `feature/...`
- `codex/...`
- `staging`

Что он делает:

1. забирает код из GitHub
2. по SSH подключается к серверу
3. копирует проект на сервер
4. создаёт `.env` для docker deploy
5. выполняет:

```bash
docker compose up -d --build
```

То есть тестовая версия обновляется автоматически.

Если Cloudflare пока не готов, используй временный workflow:

- [.github/workflows/staging-direct.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/staging-direct.yml)

Он поднимает сайт просто по IP сервера без tunnel.

## 11. Шаг 7. Как будет работать production

Файл:

- [.github/workflows/production.yml](/Users/jamshidmahkamov/Desktop/teacher_admin/.github/workflows/production.yml)

Production не запускается автоматически.

Он запускается только вручную.

Это значит:

- сначала тестируешь staging
- если всё хорошо, сам нажимаешь deploy production

Это именно тот контроль, который тебе нужен.

## 12. Твой будущий рабочий процесс

### Когда ты хочешь новую функцию

1. Ты даёшь мне задачу
2. Я делаю изменения
3. Мы создаём новую ветку:
   - `codex/new-auth`
   - `feature/mock-tests-v1`
4. Ты пушишь ветку в GitHub
5. GitHub сам обновляет staging
6. Ты тестируешь

### Если не понравилось

1. Не деплоим production
2. Удаляем ветку
3. При желании останавливаем staging

### Если понравилось

1. Merge в `main`
2. Запускаешь production workflow вручную
3. Платформа обновляется

## 13. Первый запуск вручную

После того как ты всё настроишь:

1. Залей код в GitHub
2. Создай ветку, например:

```bash
git checkout -b codex/test-deploy
git push -u origin codex/test-deploy
```

3. Открой GitHub:

`Actions -> Staging Deploy`

4. Если Cloudflare уже готов, используй `Staging Deploy`
5. Если Cloudflare ещё не готов, используй `Staging Deploy Direct`
6. Убедись, что workflow прошёл успешно

Если Cloudflare пока не настроен, можно руками проверить через IP сервера:

```bash
cd /home/ubuntu/lexora-staging/cloudflare_deploy
docker compose -f docker-compose.direct.yml up -d --build
```

После этого сайт будет доступен по:

```bash
http://IP_СЕРВЕРА:8000
```

## 14. Как проверить сервер

Зайди по SSH на сервер и выполни:

```bash
cd /home/ubuntu/lexora-staging/cloudflare_deploy
docker compose ps
docker compose logs -f
```

Если нужно смотреть отдельно:

```bash
docker compose logs -f lexora-app
docker compose logs -f cloudflared
```

## 15. Как сделать откат

Самый простой откат:

1. не запускать production deploy, если это staging
2. если уже задеплоил production, откатиться на прошлый commit

Пример:

```bash
git checkout main
git revert <commit_id>
git push origin main
```

Потом снова запускаешь production deploy.

## 16. Очень простая логика для тебя

Запомни только это:

- `branch` = тестовая версия
- `main` = основная версия
- `staging workflow` = автотестовый деплой
- `production workflow` = ручной боевой деплой

## 17. Что тебе лучше сделать прямо сейчас

По порядку:

1. Создать GitHub repository
2. Купить или арендовать VPS
3. Установить Docker на сервер
4. Добавить SSH key
5. Создать Cloudflare Tunnel
6. Добавить GitHub Secrets
7. Запустить первую тестовую ветку

## 18. Что сделаю я потом

Когда это будет готово, я смогу работать с тобой так:

1. Ты пишешь задачу
2. Я меняю код
3. Я готовлю изменения под новую ветку
4. Ты пушишь
5. Ты тестируешь staging
6. По твоей команде я готовлю production update

Это уже будет нормальный профессиональный цикл разработки для `Lexora`.
