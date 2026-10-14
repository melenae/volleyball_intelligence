import { ApiError } from "@/lib/api-client";

export function LoadingBlock({ label = "Загрузка…" }: { label?: string }) {
  return (
    <p className="text-muted" role="status" aria-live="polite">
      {label}
    </p>
  );
}

export function ErrorBlock({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const message =
    error instanceof ApiError
      ? error.message
      : error instanceof Error
        ? error.message
        : "Не удалось загрузить данные.";

  return (
    <div
      className="rounded-lg border border-danger/50 bg-danger/10 px-4 py-3 text-sm"
      role="alert"
    >
      <p>{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 text-accent underline-offset-2 hover:underline"
        >
          Повторить
        </button>
      ) : null}
    </div>
  );
}

export function EmptyBlock({ children }: { children: React.ReactNode }) {
  return (
    <p className="rounded-lg border border-line bg-card px-4 py-6 text-center text-muted">
      {children}
    </p>
  );
}
