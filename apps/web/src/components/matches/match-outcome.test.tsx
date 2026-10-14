import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MatchOutcomeMessage } from "@/components/matches/match-outcome";
import type { MatchDetailResponse } from "@/types/api";

const baseDetail: MatchDetailResponse = {
  data_origin: "demo",
  match: {
    id: "m1",
    season_id: "s1",
    home_team_id: "h1",
    away_team_id: "a1",
    scheduled_at: "2025-01-01T12:00:00Z",
    status: "completed",
    venue: null,
  },
  home_team: { id: "h1", name: "Домашние", slug: "home" },
  away_team: { id: "a1", name: "Гости", slug: "away" },
  set_results: [
    { set_number: 1, home_score: 25, away_score: 20 },
    { set_number: 2, home_score: 22, away_score: 25 },
    { set_number: 3, home_score: 15, away_score: 12 },
    { set_number: 4, home_score: 18, away_score: 25 },
  ],
  is_valid_completed_match: false,
  winner_team_id: null,
};

describe("MatchOutcomeMessage", () => {
  it("does not declare winner for invalid completed match", () => {
    render(<MatchOutcomeMessage detail={baseDetail} />);
    expect(screen.queryByText(/Победитель/)).not.toBeInTheDocument();
    expect(
      screen.getByText(/некорректен или победитель не определён/i),
    ).toBeInTheDocument();
  });

  it("shows winner when match is valid", () => {
    render(
      <MatchOutcomeMessage
        detail={{
          ...baseDetail,
          is_valid_completed_match: true,
          winner_team_id: "h1",
        }}
      />,
    );
    expect(screen.getByText("Победитель: Домашние")).toBeInTheDocument();
  });

  it("handles scheduled status", () => {
    render(
      <MatchOutcomeMessage
        detail={{
          ...baseDetail,
          match: { ...baseDetail.match, status: "scheduled" },
          set_results: [],
        }}
      />,
    );
    expect(screen.getByText(/запланирован/i)).toBeInTheDocument();
  });
});
