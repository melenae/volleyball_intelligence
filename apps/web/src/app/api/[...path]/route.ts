import type { NextRequest } from "next/server";

const REQUEST_TIMEOUT_MS = 5_000;

function apiBaseUrl(): string {
  const env = process.env;
  const configured = env.API_INTERNAL_URL?.trim();
  if (!configured) {
    return "http://localhost:8000";
  }
  return configured.replace(/\/$/, "");
}

function isSafeSegment(segment: string): boolean {
  return (
    segment.length > 0 &&
    segment !== "." &&
    segment !== ".." &&
    !segment.includes("/") &&
    !segment.includes("\\")
  );
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (path.some((segment) => !isSafeSegment(segment))) {
    return Response.json(
      { error: { code: "invalid_path", message: "Некорректный путь запроса." } },
      { status: 400 },
    );
  }

  const target = new URL(`${apiBaseUrl()}/api/${path.map(encodeURIComponent).join("/")}`);
  target.search = request.nextUrl.search;

  try {
    const upstream = await fetch(target, {
      method: "GET",
      headers: { accept: request.headers.get("accept") ?? "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    const body = await upstream.arrayBuffer();
    const headers = new Headers();
    const contentType = upstream.headers.get("content-type");
    if (contentType) {
      headers.set("content-type", contentType);
    }
    return new Response(body, { status: upstream.status, headers });
  } catch (error) {
    const reason = error instanceof Error ? error.name : "Error";
    console.error(`API proxy failed: ${reason}`);
    return Response.json(
      {
        error: {
          code: "api_unreachable",
          message: "Backend API недоступен.",
        },
      },
      { status: 502 },
    );
  }
}
