# Volleyball Intelligence

Аналитическая платформа для любительского волейбола. Read-only REST API, frontend MVP и импорт JSON v1 через CLI. Демо-данные не являются данными AVL.

## Стек

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy
- База: PostgreSQL 16
- Локальный запуск: Docker Compose

После старта Compose примените миграции и при необходимости загрузите demo-данные (см. ниже).

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

После успешного старта примените миграции и seed:

```powershell
docker compose exec api alembic upgrade head
docker compose exec api python -m app.ingestion.demo.seed
```

Локально без Docker (из `apps\api`, при работающей БД на порту 5433):

```powershell
uv run alembic upgrade head
uv run python -m app.ingestion.demo.seed
```

- приложение: http://localhost:3000
- health API: http://localhost:8000/api/v1/health
- тот же health через прокси Next.js: http://localhost:3000/api/v1/health
- OpenAPI: http://localhost:8000/docs
- примеры API: `docs/api.md` (сезоны, команды, матчи, dashboard, аналитика)

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

## Импорт данных (Phase 5)

Формат: `docs/ingestion/file-format-v1.md`. Пример: `apps/api/tests/fixtures/import_bundle_valid.v1.json`.

```powershell
cd apps\api
uv run python -m app.ingestion.cli validate .\tests\fixtures\import_bundle_valid.v1.json
uv run python -m app.ingestion.cli import .\tests\fixtures\import_bundle_valid.v1.json --dry-run
uv run python -m app.ingestion.cli import .\tests\fixtures\import_bundle_valid.v1.json
uv run python -m app.ingestion.cli summary --bundle "pytest-import-valid"
```

Demo-seed по-прежнему отдельно: `uv run python -m app.ingestion.demo.seed` (режим upsert фикстуры, не file strict).

## Что сознательно отсутствует

HTTP-загрузка файлов, CSV, живая интеграция с AVL, авторизация. Личная матчевая статистика игрока без `MatchEvent`. Документация: `docs/api.md`, `docs/analytics-definitions.md`, `docs/ingestion/avl-adapter-placeholder.md`.
