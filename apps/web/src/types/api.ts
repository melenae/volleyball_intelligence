export type DataOrigin = "demo";

export type PaginationMeta = {
  limit: number;
  offset: number;
  total: number;
};

export type WithDataOrigin = {
  data_origin: DataOrigin;
};

export type Season = {
  id: string;
  league_id: string;
  name: string;
  start_date: string;
  end_date: string;
};

export type Team = {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
};

export type Player = {
  id: string;
  demo_slug: string;
  first_name: string;
  last_name: string;
  display_name: string;
  position: string | null;
};

export type MatchTeamSummary = {
  id: string;
  name: string;
  slug: string;
};

export type MatchListItem = {
  id: string;
  season_id: string;
  scheduled_at: string | null;
  status: string;
  venue: string | null;
  home_team: MatchTeamSummary;
  away_team: MatchTeamSummary;
};

export type MatchDetailResponse = WithDataOrigin & {
  match: {
    id: string;
    season_id: string;
    home_team_id: string;
    away_team_id: string;
    scheduled_at: string | null;
    status: string;
    venue: string | null;
  };
  home_team: MatchTeamSummary;
  away_team: MatchTeamSummary;
  set_results: Array<{
    set_number: number;
    home_score: number;
    away_score: number;
  }>;
  is_valid_completed_match: boolean;
  winner_team_id: string | null;
};

/** @deprecated use MatchDetailResponse */
export type MatchDetail = MatchDetailResponse;

export type PaginatedSeasonsResponse = WithDataOrigin & {
  items: Season[];
  pagination: PaginationMeta;
};

export type PaginatedTeamsResponse = WithDataOrigin & {
  items: Team[];
  pagination: PaginationMeta;
};

export type PaginatedPlayersResponse = WithDataOrigin & {
  items: Player[];
  pagination: PaginationMeta;
};

export type PaginatedMatchesResponse = WithDataOrigin & {
  items: MatchListItem[];
  pagination: PaginationMeta;
};

export type TeamDetailResponse = WithDataOrigin & {
  team: Team;
};

export type PlayerDetailResponse = WithDataOrigin & {
  player: Player;
};

export type TeamPlayersResponse = WithDataOrigin & {
  team_id: string;
  season_id: string;
  players: Array<{
    player: Player;
    jersey_number: number | null;
  }>;
};

export type TeamAnalyticsResponse = WithDataOrigin & {
  team_id: string;
  season_id: string | null;
  statistics: {
    played_matches: number;
    wins: number;
    losses: number;
    sets_won: number;
    sets_lost: number;
    points_for: number;
    points_against: number;
    win_percentage: number | null;
    match_timeline: Array<{
      match_id: string;
      scheduled_at: string | null;
      opponent_team_id: string;
      is_home: boolean;
      result: "win" | "loss";
      home_sets_won: number;
      away_sets_won: number;
    }>;
  };
};

export type PlayerAnalyticsResponse = WithDataOrigin & {
  player_id: string;
  season_id: string | null;
  rosters: Array<{
    team_id: string;
    season_id: string;
    jersey_number: number | null;
  }>;
  note: string;
};

export type DashboardSummaryResponse = WithDataOrigin & {
  season_id: string;
  season_name: string;
  teams_count: number;
  matches_total: number;
  matches_valid_completed: number;
  standings: Array<{
    team_id: string;
    team_name: string;
    team_slug: string;
    played_matches: number;
    wins: number;
    losses: number;
    win_percentage: number | null;
  }>;
  recent_matches: MatchListItem[];
};

export type ApiErrorBody = {
  error: {
    code: string;
    message: string;
  };
};
