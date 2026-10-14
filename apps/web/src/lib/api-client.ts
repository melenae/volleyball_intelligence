import type { ApiErrorBody } from "@/types/api";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

type QueryValue = string | number | boolean | null | undefined;

function buildSearch(params?: Record<string, QueryValue>): string {
  if (!params) {
    return "";
  }
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function apiGet<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<T> {
  const response = await fetch(`${path}${buildSearch(params)}`, {
    headers: { accept: "application/json" },
    cache: "no-store",
  });

  if (!response.ok) {
    let code = "http_error";
    let message = `Ошибка API (${response.status})`;
    try {
      const body = (await response.json()) as ApiErrorBody;
      if (body.error) {
        code = body.error.code;
        message = body.error.message;
      }
    } catch {
      // keep defaults
    }
    throw new ApiError(response.status, code, message);
  }

  return (await response.json()) as T;
}
