import { apiGet } from "@/lib/api-client";
import type {
  DashboardSummaryResponse,
  MatchDetailResponse,
  PaginatedMatchesResponse,
  PaginatedPlayersResponse,
  PaginatedSeasonsResponse,
  PaginatedTeamsResponse,
  PlayerAnalyticsResponse,
  PlayerDetailResponse,
  TeamAnalyticsResponse,
  TeamDetailResponse,
  TeamPlayersResponse,
} from "@/types/api";

const V1 = "/api/v1";

export function fetchSeasons(limit = 50, offset = 0) {
  return apiGet<PaginatedSeasonsResponse>(`${V1}/seasons`, { limit, offset });
}

export function fetchDashboardSummary(seasonId: string) {
  return apiGet<DashboardSummaryResponse>(`${V1}/dashboard/summary`, {
    season_id: seasonId,
  });
}

export function fetchTeams(limit: number, offset: number) {
  return apiGet<PaginatedTeamsResponse>(`${V1}/teams`, { limit, offset });
}

export function fetchTeam(teamId: string) {
  return apiGet<TeamDetailResponse>(`${V1}/teams/${teamId}`);
}

export function fetchTeamPlayers(teamId: string, seasonId: string) {
  return apiGet<TeamPlayersResponse>(`${V1}/teams/${teamId}/players`, {
    season_id: seasonId,
  });
}

export function fetchTeamAnalytics(teamId: string, seasonId: string) {
  return apiGet<TeamAnalyticsResponse>(`${V1}/analytics/teams/${teamId}`, {
    season_id: seasonId,
  });
}

export function fetchPlayers(limit: number, offset: number) {
  return apiGet<PaginatedPlayersResponse>(`${V1}/players`, { limit, offset });
}

export function fetchPlayer(playerId: string) {
  return apiGet<PlayerDetailResponse>(`${V1}/players/${playerId}`);
}

export function fetchPlayerAnalytics(playerId: string, seasonId?: string) {
  return apiGet<PlayerAnalyticsResponse>(`${V1}/analytics/players/${playerId}`, {
    season_id: seasonId,
  });
}

export function fetchMatches(params: {
  season_id?: string;
  team_id?: string;
  limit: number;
  offset: number;
}) {
  return apiGet<PaginatedMatchesResponse>(`${V1}/matches`, params);
}

export function fetchMatch(matchId: string) {
  return apiGet<MatchDetailResponse>(`${V1}/matches/${matchId}`);
}
