# Volleyball Intelligence

Аналитическая платформа для любительского волейбола. Сейчас это каркас Phase 1: веб-оболочка, HTTP API и PostgreSQL. Демонстрационные команды, игроки и матчи ещё не загружены. Это не интерфейс и не данные AVL.

## Стек

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy
- База: PostgreSQL 16
- Локальный запуск: Docker Compose

SQLAlchemy в этой фазе только проверяет соединение. Таблиц предметной области нет.

## Требования

- Docker Desktop
- Для проверок без контейнеров: Node.js 22+ и [uv](https://docs.astral.sh/uv/) с Python 3.12

На этой машине локальный PostgreSQL уже слушает порт 5432, поэтому Compose публикует базу на порт **5433**. Внутри сети Compose API по-прежнему ходит на `db:5432`.

## Запуск в Windows PowerShell

Из корня репозитория:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

После успешного старта:

- приложение: http://localhost:3000
- health API: http://localhost:8000/api/v1/health
- тот же health через прокси Next.js: http://localhost:3000/api/v1/health
- OpenAPI: http://localhost:8000/docs

Остановка:

```powershell
docker compose down
```

Пароль в `.env.example` годится только для локальной базы. Для любого общего окружения замените его в `.env`, который не коммитится.

## Проверки без полного Compose

```powershell
cd apps\api
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest

cd ..\web
npm ci
npm run lint
npm run typecheck
npm run build
```

## Что сознательно отсутствует

Модели лиги, seed, аналитика, страницы команд, игроков и матчей, авторизация и интеграция с AVL. Правила будущего матча и идемпотентного seed записаны в `docs/decisions/0001-confirmed-architecture.md`.
