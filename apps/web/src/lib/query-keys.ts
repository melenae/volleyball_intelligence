export const queryKeys = {
  seasons: (limit: number, offset: number) => ["seasons", limit, offset] as const,
  dashboard: (seasonId: string) => ["dashboard", seasonId] as const,
  teams: (limit: number, offset: number) => ["teams", limit, offset] as const,
  team: (id: string) => ["team", id] as const,
  teamPlayers: (teamId: string, seasonId: string) =>
    ["teamPlayers", teamId, seasonId] as const,
  teamAnalytics: (teamId: string, seasonId: string) =>
    ["teamAnalytics", teamId, seasonId] as const,
  players: (limit: number, offset: number) => ["players", limit, offset] as const,
  player: (id: string) => ["player", id] as const,
  playerAnalytics: (id: string, seasonId?: string) =>
    ["playerAnalytics", id, seasonId ?? "all"] as const,
  matches: (params: Record<string, string | number>) =>
    ["matches", params] as const,
  match: (id: string) => ["match", id] as const,
};
