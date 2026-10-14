import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";

const push = vi.fn();
const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, replace }),
  useSearchParams: () => new URLSearchParams(""),
}));

vi.mock("@/lib/api", () => ({
  fetchSeasons: vi.fn(async () => ({
    data_origin: "demo",
    items: [
      {
        id: "season-1",
        league_id: "league-1",
        name: "Демо 2025",
        start_date: "2025-01-01",
        end_date: "2025-12-31",
      },
    ],
    pagination: { limit: 50, offset: 0, total: 1 },
  })),
  fetchDashboardSummary: vi.fn(async () => ({
    data_origin: "demo",
    season_id: "season-1",
    season_name: "Демо 2025",
    teams_count: 4,
    matches_total: 3,
    matches_valid_completed: 1,
    standings: [
      {
        team_id: "t1",
        team_name: "Команда А",
        team_slug: "a",
        played_matches: 1,
        wins: 1,
        losses: 0,
        win_percentage: null,
      },
    ],
    recent_matches: [],
  })),
}));

function renderDashboard() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <DashboardView />
    </QueryClientProvider>,
  );
}

describe("DashboardView", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("prompts to select season before summary", async () => {
    renderDashboard();
    await waitFor(() => {
      expect(
        screen.getByText("Выберите сезон, чтобы увидеть сводку и таблицу."),
      ).toBeInTheDocument();
    });
    expect(screen.queryByText("Корректно завершённых")).not.toBeInTheDocument();
  });

  it("loads summary after season selection", async () => {
    renderDashboard();
    await waitFor(() => screen.getByLabelText("Сезон"));
    fireEvent.change(screen.getByLabelText("Сезон"), {
      target: { value: "season-1" },
    });
    expect(replace).toHaveBeenCalledWith("/?season_id=season-1");
  });
});
