# HTTP API (v1)

Базовый URL: `http://localhost:8000`. Через Next.js proxy: `http://localhost:3000/api/...`.

Только **GET**. Ошибки:

```json
{
  "error": {
    "code": "not_found",
    "message": "Команда не найдена."
  }
}
```

Аналитические ответы содержат `data_origin: "demo"`.

## Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/health` | Состояние API и БД (без `data_origin`) |

## Сезоны

| GET | `/api/v1/seasons` | Список сезонов |
| Параметры | `limit` (1–100, default 20), `offset` (≥0) |

## Команды

| GET | `/api/v1/teams` | Список команд (пагинация) |
| GET | `/api/v1/teams/{team_id}` | Карточка команды |
| GET | `/api/v1/teams/{team_id}/players` | Состав; **обязателен** `season_id` |

## Игроки

| GET | `/api/v1/players` | Список игроков |
| GET | `/api/v1/players/{player_id}` | Профиль |

## Матчи

| GET | `/api/v1/matches` | Список; фильтры `season_id`, `team_id`; пагинация |
| GET | `/api/v1/matches/{match_id}` | Матч, сеты, флаг корректности, `winner_team_id` или `null` |

Сортировка списка: `scheduled_at` ASC (NULL в конце), затем `id` ASC.

## Аналитика

| GET | `/api/v1/analytics/teams/{team_id}` | Статистика команды; опционально `season_id` |
| GET | `/api/v1/analytics/players/{player_id}` | Составы; опционально `season_id`; без выдуманной личной статистики |

Пример фрагмента ответа команды:

```json
{
  "data_origin": "demo",
  "team_id": "...",
  "season_id": "...",
  "statistics": {
    "played_matches": 1,
    "wins": 1,
    "losses": 0,
    "sets_won": 2,
    "sets_lost": 1,
    "points_for": 73,
    "points_against": 64,
    "win_percentage": 100.0,
    "match_timeline": []
  }
}
```

## Dashboard

| GET | `/api/v1/dashboard/summary` | Сводка сезона; **обязателен** `season_id` |

Поля: `teams_count`, `matches_total`, `matches_valid_completed`, `standings`, `recent_matches`.

OpenAPI: `http://localhost:8000/docs`.
