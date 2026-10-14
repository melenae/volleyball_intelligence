# Формат импорта JSON v1

Импорт выполняется только через CLI (`python -m app.ingestion.cli`), не через HTTP API.

## Заголовок

| Поле | Тип | Описание |
|------|-----|----------|
| `schema_version` | `1` | Версия схемы |
| `source_label` | string | Идентификатор пакета (сохраняется в `bundle_ref`) |
| `league` | object | Одна лига в файле |
| `seasons` | array | Сезоны этой лиги |
| `teams` | array | Команды |
| `players` | array | Игроки |
| `rosters` | array | Заявки (опционально) |
| `matches` | array | Матчи и сеты (опционально) |

## Внешние ссылки

Внутри файла все связи задаются полями `*_ref`. При записи в PostgreSQL создаётся строка в `ingestion_external_keys` с `source=file`, `entity_type` и `external_id` (для состава — `team_ref|player_ref|season_ref`).

Поле `players[].ref` сохраняется в колонке `players.demo_slug` (нейтральное имя в файле, существующая колонка БД).

## Правила

- Уникальность `ref` внутри каждого типа сущности в файле.
- `season.league_ref` должен совпадать с `league.ref`.
- Матч: `home_team_ref` ≠ `away_team_ref`.
- Для `scheduled` и `cancelled` массив `sets` пустой.
- Сеты: целые неотрицательные счёта, без ничьей в сете.
- Повторный импорт того же файла идемпотентен: при полном совпадении данных строки не дублируются.
- При совпадении `ref`, но отличии полей — ошибка `data_conflict`.
- При совпадении `slug` / `demo_slug` с существующей строкой без привязки `ref` — ошибка `slug_conflict`.

Пример: `apps/api/tests/fixtures/import_bundle_valid.v1.json`.

## CLI

```powershell
cd apps\api
uv run python -m app.ingestion.cli validate path\to\bundle.json
uv run python -m app.ingestion.cli validate path\to\bundle.json --report report.json
uv run python -m app.ingestion.cli import path\to\bundle.json --dry-run
uv run python -m app.ingestion.cli import path\to\bundle.json
uv run python -m app.ingestion.cli summary --bundle "pytest-import-valid"
```

Полная проверка с учётом базы (без записи) — `import --dry-run`.
