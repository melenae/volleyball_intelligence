# Журнал запусков импорта (`ingestion_runs`)

**Status:** Proposed  
**Дата:** 2026-10-15  
**Связанные документы:** [0001-confirmed-architecture.md](./0001-confirmed-architecture.md), [Phase 7 Step 1](../phase7/step1-real-data-source-contract-discovery.md), [0002-data-origin-and-provenance.md](./0002-data-origin-and-provenance.md), [file-format-v1.md](../ingestion/file-format-v1.md)

---

## Context

Сейчас импорт JSON v1:

- выполняется через CLI (`python -m app.ingestion.cli import`);
- при успехе делает один `commit` на весь пакет, при ошибке или `--dry-run` — `rollback` (`app/ingestion/service.py`);
- сохраняет соответствия в `ingestion_external_keys` (`source`, `entity_type`, `external_id`, `internal_id`, `bundle_ref`);
- возвращает `ValidationReport` (в т.ч. `would_create` / `would_skip`), опционально JSON-файл через `--report`;
- **не** сохраняет в БД идентификатор запуска, время, оператора, полный список issues после завершения.

Команда `summary` агрегирует **текущее** состояние ключей по `bundle_ref`, а не историю попыток. Повторный успешный import с теми же данными увеличивает только skip-счётчики в отчёте CLI, не оставляя audit trail в PostgreSQL.

Demo-seed (`app/ingestion/demo/seed.py`) не использует `ingestion_external_keys` и не пишет journal.

Контракт AVL **не подтверждён**; модель journal должна описывать file import и будущий адаптер без полей/endpoint AVL.

Журнал запусков **не заменяет** `ingestion_external_keys`: ключи отвечают на вопрос «какой внешний id соответствует UUID», run — «когда и с каким результатом мы пытались загрузить пакет».

---

## Decision Drivers

- Операционная приёмка и разбор инцидентов (конфликты, dry-run перед prod).
- Связь успешного пакета с `bundle_ref` / `source_label` и с [происхождением сезона](./0002-data-origin-and-provenance.md).
- Безопасность: **не** хранить секреты, credentials, полные дампы PII в journal.
- Соответствие текущей транзакционной модели (один пакет — одна транзакция) с явной фиксацией **failed** попыток вне commit данных пакета.
- Минимальная нагрузка на ручной file-import в dev; полнота — для будущего scheduled AVL sync.
- Идемпотентность повторного import не должна ломаться из-за journal.

---

## Considered Options

### Option A — Без изменений (только `ingestion_external_keys` + CLI exit code / файл `--report`)

| | |
|--|--|
| **Плюсы** | Нулевая миграция; уже работает для пилота. |
| **Минусы** | Нет истории failed run; отчёт на диске не связан с БД; нельзя ответить «кто импортировал вчера»; слабая приёмка AVL. |
| **Частичный сбой** | Данные не коммитятся, след в БД отсутствует — только локальный отчёт. |
| **Связь с keys** | Только косвенно через `bundle_ref` на ключах без времени. |

### Option B — Таблица `ingestion_runs` в PostgreSQL

Запись run создаётся в начале попытки; обновляется при завершении. Опционально `ingestion_run_id` на строках `ingestion_external_keys`, созданных в этом run.

| | |
|--|--|
| **Плюсы** | Audit, UI/ops запросы, связь с provenance; failed runs видны. |
| **Минусы** | Миграция; дисциплина redaction в `report_payload`. |
| **Частичный сбой** | Статус `failed`; доменные данные откатаны; run остаётся. |
| **Связь с keys** | FK или nullable `ingestion_run_id` на keys, созданных при успехе. |

### Option C — Только внешний лог (файл, OpenTelemetry, SIEM)

| | |
|--|--|
| **Плюсы** | БД не растёт; привычные ops-пайплайны. |
| **Минусы** | Сложная корреляция с UUID сущностей; отдельная инфраструктура; не помогает `summary` в CLI из БД. |
| **Частичный сбой** | Зависит от агента логирования. |
| **Связь с keys** | Только по correlation id в логе. |

### Option D — Расширить `ingestion_external_keys` (version, run metadata на каждой строке)

| | |
|--|--|
| **Плюсы** | Одна таблица. |
| **Минусы** | Дублирование run на тысячах ключей; **не** фиксирует failed run без новых keys; смешивает идентичность и audit. **Не рекомендуется.** |

---

## Proposed Decision

Принять **Option B** (`ingestion_runs`) как целевую модель для controlled import; Option A остаётся допустимой для локального dev до включения feature flag.

### Предлагаемая схема (логическая, без миграции в этом шаге)

**Таблица `ingestion_runs`**

| Поле | Назначение |
|------|------------|
| `id` | UUID, идентификатор запуска |
| `source` | Код источника (`file`, в будущем константа для AVL — только после появления адаптера) |
| `bundle_ref` | Идентификатор пакета (`source_label` JSON v1 или эквивалент адаптера) |
| `schema_version` | nullable, например `1` для JSON v1 |
| `status` | enum: `running`, `succeeded`, `failed`, `cancelled` (опционально) |
| `dry_run` | boolean |
| `started_at` | timestamptz |
| `finished_at` | nullable timestamptz |
| `triggered_by` | nullable string (например `cli`, `scheduler`; **не** хранить OS user с PII без необходимости) |
| `input_ref` | nullable string (путь к файлу **или** хэш/идентификатор snapshot; не обязательно полный путь в prod) |
| `counts_created` | JSONB или отдельные int-поля по `entity_type` |
| `counts_skipped` | JSONB |
| `counts_errors` | int (число issues) |
| `report_payload` | JSONB: коды issues, entity_ref, field — **без** сырого файла и без секретов |
| `error_summary` | nullable text (краткое сообщение) |

**Связь с `ingestion_external_keys`**

- Добавить nullable `ingestion_run_id` (FK → `ingestion_runs.id`) на ключи, **созданные** в данном успешном non-dry-run (предпочтительно; skip-only run может не иметь ни одного FK).
- `bundle_ref` на ключах сохраняется для `cli summary`; journal **не заменяет** эту таблицу.
- Run **не** означает полный audit истории сущности — см. раздел «Связь run ↔ external keys».

**Жизненный цикл статуса run**

```text
                    ┌─────────────┐
                    │   running   │  INSERT при старте попытки
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐   ┌────────────┐
    │  failed    │  │ succeeded  │   │ cancelled  │  (опционально: ops/таймаут)
    └────────────┘  └────────────┘   └────────────┘
```

| Исход | `dry_run` | Доменные данные + external keys | `status` | `finished_at` |
|-------|-----------|----------------------------------|----------|---------------|
| Валидация/writer не прошли | `false` | rollback, **нет** частичного пакета | `failed` | set |
| Валидация прошла, commit данных | `false` | commit целиком (как сейчас) | `succeeded` | set |
| Dry-run, отчёт valid | `true` | rollback, keys **без изменений** | `succeeded` | set |
| Dry-run, отчёт invalid | `true` | rollback | `failed` | set |
| Процесс убит на `running` | любой | не определено | остаётся `running` или ops → `failed`/`cancelled` | nullable / позже |

Dry-run **не** меняет provenance сезона ([0002](./0002-data-origin-and-provenance.md)) и **не** создаёт/обновляет mappings в `ingestion_external_keys`.

**Диагностики: разрешено и запрещено**

| Разрешено в `report_payload` / `error_summary` | Запрещено |
|-----------------------------------------------|-----------|
| Коды issues (`data_conflict`, `slug_conflict`, …), `entity_type`, `entity_ref`, `field` | Секреты, API keys, заголовки Authorization, тела OAuth |
| Счётчики `would_create` / `would_skip` по типам сущностей | Полный JSON пакета или HTTP-ответа внешнего API |
| `schema_version`, `bundle_ref`, `source` run | Пароли, DSN с credentials |
| Для file: `entity_ref` из пакета (идентификаторы фикстуры) | Избыточные ПДн (email, телефон), если появятся в будущих контрактах — redact |
| `input_ref`: basename файла или SHA-256 содержимого | Полный путь с домашним каталогом пользователя в prod (PII) |
| Усечённый список issues + `truncated_issues_count` | Сырые stack traces с локальными путями (опционально strip) |

**Транзакционные границы (journal vs домен)**

Две логические области:

1. **Journal transaction** — `ingestion_runs` (insert `running`, update terminal status, diagnostics).
2. **Domain transaction** — strict writer, `ingestion_external_keys`, доменные таблицы (один commit или rollback на пакет, как `app/ingestion/service.py` сегодня).

Требование: после **rollback** domain transaction запись run с `failed` (или `succeeded` для dry-run) и диагностика **должны остаться** в БД.

**Предлагаемая стратегия (Proposed, не реализовано): «outbox run»**

| Шаг | Действие | Транзакция |
|-----|----------|------------|
| 1 | `INSERT ingestion_runs` (`running`, `dry_run`, `bundle_ref`, …) | **commit journal** (отдельная короткая транзакция / autocommit) |
| 2 | Domain import в сессии с writer | domain tx |
| 3a | Успех, не dry-run | commit domain → **commit journal** update `succeeded`, counts, `report_payload` (минимальный), опционально `ingestion_run_id` на **новые** keys |
| 3b | Успех, dry-run | rollback domain → journal update `succeeded`, `dry_run=true` |
| 3c | Ошибка writer | rollback domain → journal update `failed`, issues в payload |

**Сбой между commit доменных данных и обновлением run**

Риск: domain **уже закоммичен**, процесс падает до `UPDATE ingestion_runs SET status='succeeded'`.

| Стратегия | Описание | Trade-off |
|-----------|----------|-----------|
| **R1 — Финализация в той же транзакции, что domain** | Run остаётся `running` до commit domain; terminal status в **одной** транзакции с данными. | Failed run при rollback данных **теряется**, если journal в той же tx — **не подходит** для требования «failed виден после rollback». |
| **R2 — Двухфазный: journal commit, затем domain, затем journal finalize** | После шага 2 при успехе domain commit; шаг 3a — отдельный journal commit. При падении между 2 и 3a: данные в БД, run **`running`** или **`succeeded_pending_finalize`**. | Нужен **reconciler**: фоновый/job помечает stale `running` или дописывает `succeeded` по наличию keys с `bundle_ref` + timestamp. |
| **R3 — Saga / idempotent finalize** | Повторный вызов «finalize run» по `run_id` безопасен; CLI при старте дописывает незавершённые runs. | Сложнее код; лучшая ops-устойчивость. |

**Рекомендация для реализации (после Accepted):** комбинация шагов 1–3c выше + **R2/R3** — периодическая или при старте CLI финализация «зависших» `running` (не утверждается как единственный путь до ревью).

**Почему каждая попытка — отдельный run (включая повторный import только со skip)**

- Audit: «когда последний раз проверяли пакет» без изменения данных.
- Приёмка: счётчики `counts_skipped` доказывают идемпотентность.
- Отличие от `summary`: summary — срез keys; run — **событие во времени**.
- Failed и dry-run остаются сопоставимы с успешными по `bundle_ref`.

Повторный import **не** обязан менять external keys; run всё равно создаётся.

**Связь run ↔ external keys (без ложной полноты)**

- `ingestion_run_id` на key означает: «эта строка mapping **впервые создана** в данном run» (или «последний run, затронувший key» — **открытый вопрос**).
- Run **не** утверждает, что содержит полную историю изменений сущности: strict writer не делает update; старые keys могли появиться в **другом** run без обновления `ingestion_run_id`.
- Для audit полной картины нужны **все** runs с тем же `bundle_ref` + текущие keys; journal не заменяет `ingestion_external_keys`.
- При run только со **skip** новых keys нет — FK на keys может быть пустым; ценность run — counts и timestamp.

---

## Consequences

### Positive

- Приёмка импорта: «последний успешный run для `bundle_ref`».
- Связь с [0002](./0002-data-origin-and-provenance.md): run хранит `bundle_ref` / метаданные пакета; присвоение provenance сезону — **отдельное продуктовое решение**, не следует автоматически из `succeeded` run.
- Повторный import: новый run, skip-счётчики в `counts_skipped`, audit без изменения keys.
- Основа для watermark (`last_successful_sync_at` по source) без выдумывания AVL API.

### Negative

- Дополнительная миграция и код в CLI/service.
- Нужна политика retention (архивация старых runs).
- Риск утечки PII через `input_ref` или `report_payload` — требуются линтеры/redaction в реализации.

### Отличие от `ingestion_external_keys`

| | `ingestion_external_keys` | `ingestion_runs` |
|--|---------------------------|------------------|
| Назначение | Стабильное mapping внешний id → UUID | История попыток загрузки |
| Жизненный цикл | Переживает повторные import | Одна строка на попытку |
| Failed import | Без изменений | Run `failed`, данных нет |
| `summary --bundle` | Считает ключи | Дополняется `runs list --bundle` (будущий CLI) |

---

## Migration Plan

1. Миграция: таблица `ingestion_runs`; nullable FK на `ingestion_external_keys`.
2. CLI `import`: обернуть `import_file` записью run (feature flag `INGESTION_RUNS_ENABLED`).
3. Backfill: **не** создавать исторические runs для существующих ключей (или один synthetic run `migrated-unknown` — только по решению ops).
4. Документация: `docs/ingestion/file-format-v1.md` — ссылка на journal; обновить Phase 7 checklist.
5. Тесты: unit/integration на succeeded/failed/dry-run без секретов в payload.

Demo-seed: по умолчанию **без** run; опционально `source=demo_seed` run для единообразия аудита — Open Question.

---

## Open Questions

1. Финализация run: R2 vs R3 при сбое после domain commit (раздел «Сбой между commit доменных данных…»).
2. Проставлять `ingestion_run_id` на keys при **только skip** (повторный import) — или оставлять FK только на create?
3. Retention: сколько хранить `report_payload`?
4. Индекс / view «последний успешный run по `(source, bundle_ref)`»?
5. Scheduled sync (будущий адаптер): один run на полный sync или на сезон/дату — **без деталей AVL до контракта**.
6. Demo-seed: создавать run или нет?
7. HTTP admin для runs — позже или только CLI?
8. Статус `running` stale: TTL и автоматический `failed`?

---

## Согласованность с происхождением данных (0002)

| Сценарий | Journal (`ingestion_runs`) | Provenance (`seasons`, [0002](./0002-data-origin-and-provenance.md)) |
|----------|----------------------------|---------------------------------------------------------------------|
| Demo seed | Run по умолчанию **нет** | `demo` при реализации seed — не из journal |
| JSON import **успех** | `succeeded`, `dry_run=false`; keys по writer | **Не** auto-`imported` до продуктовой политики S*/P* |
| JSON import **dry-run** | `succeeded` или `failed`; `dry_run=true` | **Без изменений** provenance |
| JSON import **failed** | `failed`; diagnostics persisted | **Без изменений**; domain rollback — нет частичных данных |
| Повторный import (skip-only) | **Новый** run, `counts_skipped` | Origin не менять без политики update |
| Конфликт `data_conflict` | `failed` | Без изменений |
| Будущий AVL | Только после контракта + константа `source`; payload по контракту | `data_origin=avl` **не** до go-live адаптера |
| Keys vs runs | Keys = identity; runs = попытки | Provenance = продуктовый слой, не замена keys |

### Неуспешный run и внешние ключи

При failed транзакции новые keys не должны оставаться в БД. Существующие keys от прошлого успешного run не откатываются. Journal фиксирует неудачную **попытку**, не «отмену» прошлого успеха.

### Частичный сбой

Текущий writer не поддерживает частичный commit пакета. ADR сохраняет: **весь пакет — одна транзакция**; «частичный сбой» = failed run, нулевые изменения данных. Chunking по сезону — отдельное решение (Step 1 §4.7).

---

## Потенциальные breaking changes (при реализации)

- Семантика CLI: код выхода может оставаться `1` при failed, но появятся persisted runs — скрипты CI должны не полагаться только на отсутствие строк в БД.
- `summary --bundle` не заменяется; потребители должны явно перейти на runs API/CLI для audit.
- Расширение `ingestion_external_keys` FK — совместимо, если колонка nullable.

---

## Альтернатива для минимального scope

Если ревью отклонит полную Option B: принять **гибрид** — persist только `failed` + `dry_run` runs в БД, успешные — по-прежнему только keys + optional `--report` file. ADR не рекомендует это для AVL-ready состояния, но допускает поэтапное внедрение.
