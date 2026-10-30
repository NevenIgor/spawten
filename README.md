# Django + Aiogram + Nginx + PostgreSQL + Redis + Elasticsearch

Стек поднят через docker compose.

## Сервисы

| Сервис    | Образ                              | Описание                                  |
|-----------|------------------------------------|-------------------------------------------|
| api       | python:3.12-slim (Django 6, gunicorn) | Django REST API, порт 8000 (внутри сети) |
| tg_bot    | python:3.12-slim (aiogram 3)       | Telegram-бот (long polling)               |
| nginx     | nginx:1.27-alpine                  | Reverse-proxy, статика; внешний порт 80   |
| postgres  | postgres:16-alpine                 | СУБД                                      |
| redis     | redis:7-alpine                     | Кэш / сессии / брокер                     |
| elastic   | elasticsearch:8.15.3               | Полнотекстовый поиск (single-node)        |

## Быстрый старт

```bash
cp .env.example .env        # затем отредактируйте значения (токен бота, пароли)
docker compose up -d --build
```

- API через nginx: http://localhost/healthz/
- Админка Django: http://localhost/admin/ (суперпользователь создаётся автоматически из `DJANGO_SUPERUSER_*`)
- Elasticsearch: http://localhost:9200

## Структура

```
├── docker-compose.yml
├── .env.example          # шаблон переменных окружения
├── nginx/                # конфиги reverse-proxy
├── api/                  # Django-проект (config/, manage.py, Dockerfile)
└── tg_bot/               # aiogram-бот (bot/, Dockerfile)
```

## Полезные команды

```bash
docker compose logs -f api          # логи API
docker compose logs -f tg_bot       # логи бота
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
docker compose down                 # остановить (данные в volumes сохранятся)
docker compose down -v              # удалить вместе с volumes
```

## Примечания

- Для разработки можно запускать API с `runserver` с авто-перезагрузкой:
  `docker compose run --rm --service-ports api python manage.py runserver 0.0.0.0:8000`
- Elasticsearch требует `vm.max_map_count >= 262144` на хосте:
  `sudo sysctl -w vm.max_map_count=262144`
- Суперпользователь создаётся автоматически при старте контейнера `api`
  (пароль по умолчанию — `admin`, смените в `.env`).
