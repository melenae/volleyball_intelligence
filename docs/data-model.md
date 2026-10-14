# Модель данных (Phase 2)

Каноническая модель PostgreSQL. Внутренние ключи — UUID. Источник для экранов — только база после загрузки (demo seed, будущий импорт).

## Сущности

| Таблица | Назначение |
|---------|------------|
| `leagues` | Соревнование, уникальный `slug` |
| `seasons` | Сезон в лиге, уникальность `(league_id, name)` |
| `teams` | Команда, уникальный `slug` |
| `players` | Игрок, уникальный `demo_slug` для идемпотентного seed |
| `team_rosters` | Состав: команда + игрок + сезон |
| `matches` | Матч сезона, `home_team` / `away_team`, статус, опциональная `venue` |
| `set_results` | Счёт сета, уникальность `(match_id, set_number)` |

## Матч

- `home_team_id` и `away_team_id` обязательны и различаются (CHECK в БД).
- `venue` может быть `NULL` (нейтральная площадка).
- Статус: `scheduled`, `completed`, `cancelled`.

Корректность результата для аналитики — см. [match-result-validity.md](./match-result-validity.md).

## Миграции

Из `apps/api`:

```powershell
uv run alembic upgrade head
```

## Demo seed

```powershell
uv run python -m app.ingestion.demo.seed
```

Данные вымышленные, не AVL. Повторный запуск идемпотентен.
