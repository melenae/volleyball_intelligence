"use client";

import { useEffect, useState } from "react";

type HealthPayload = {
  status: "ok" | "degraded";
  service: string;
  environment: string;
  database: "ok" | "unavailable";
};

type ViewState =
  | { kind: "loading" }
  | { kind: "ready"; payload: HealthPayload }
  | { kind: "unreachable"; message: string }
  | { kind: "invalid" };

function isHealthPayload(value: unknown): value is HealthPayload {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const record = value as Record<string, unknown>;
  return (
    (record.status === "ok" || record.status === "degraded") &&
    typeof record.service === "string" &&
    typeof record.environment === "string" &&
    (record.database === "ok" || record.database === "unavailable")
  );
}

export function HealthStatus() {
  const [state, setState] = useState<ViewState>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch("/api/v1/health", {
          signal: controller.signal,
          headers: { accept: "application/json" },
        });
        const payload: unknown = await response.json();
        if (controller.signal.aborted) {
          return;
        }
        if (!isHealthPayload(payload)) {
          setState({ kind: "invalid" });
          return;
        }
        setState({ kind: "ready", payload });
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }
        const message = error instanceof Error ? error.message : "Неизвестная ошибка";
        setState({ kind: "unreachable", message });
      }
    }

    void load();
    return () => controller.abort();
  }, []);

  return (
    <section
      aria-live="polite"
      className="rounded-2xl border border-line bg-card p-6"
    >
      <h2 className="text-lg font-semibold">Связь с API</h2>
      <p className="mt-2 text-sm text-muted">
        Браузер запрашивает <span className="font-mono text-foreground">/api/v1/health</span>,
        Next.js передаёт запрос в FastAPI.
      </p>
      <div className="mt-5">{renderState(state)}</div>
    </section>
  );
}

function renderState(state: ViewState) {
  if (state.kind === "loading") {
    return <p className="text-muted">Проверяем API…</p>;
  }

  if (state.kind === "unreachable") {
    return (
      <p className="text-danger">
        API недоступен. Запустите backend и обновите страницу. {state.message}
      </p>
    );
  }

  if (state.kind === "invalid") {
    return <p className="text-danger">API ответил в неожиданном формате.</p>;
  }

  const databaseLabel = state.payload.database === "ok" ? "доступна" : "недоступна";
  const tone = state.payload.status === "ok" ? "text-ok" : "text-danger";

  return (
    <dl className="grid gap-3 text-sm sm:grid-cols-2">
      <div>
        <dt className="text-muted">Статус</dt>
        <dd className={`mt-1 font-medium ${tone}`}>{state.payload.status}</dd>
      </div>
      <div>
        <dt className="text-muted">База данных</dt>
        <dd className={`mt-1 font-medium ${tone}`}>{databaseLabel}</dd>
      </div>
      <div>
        <dt className="text-muted">Сервис</dt>
        <dd className="mt-1 font-mono">{state.payload.service}</dd>
      </div>
      <div>
        <dt className="text-muted">Окружение</dt>
        <dd className="mt-1 font-mono">{state.payload.environment}</dd>
      </div>
    </dl>
  );
}
