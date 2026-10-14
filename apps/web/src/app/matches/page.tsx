"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { PaginationControls } from "@/components/ui/pagination-controls";
import { fetchMatches, fetchSeasons, fetchTeams } from "@/lib/api";
import { formatDateTime, matchStatusLabel } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";

const PAGE_SIZE = 20;

export default function MatchesPage() {
  const [offset, setOffset] = useState(0);
  const [seasonId, setSeasonId] = useState("");
  const [teamId, setTeamId] = useState("");

  const seasonsQuery = useQuery({
    queryKey: queryKeys.seasons(50, 0),
    queryFn: () => fetchSeasons(50, 0),
  });

  const teamsQuery = useQuery({
    queryKey: queryKeys.teams(100, 0),
    queryFn: () => fetchTeams(100, 0),
  });

  const matchParams = useMemo(
    () => ({
      limit: PAGE_SIZE,
      offset,
      season_id: seasonId,
      team_id: teamId,
    }),
    [offset, seasonId, teamId],
  );

  const matchesQuery = useQuery({
    queryKey: queryKeys.matches(matchParams),
    queryFn: () => fetchMatches(matchParams),
  });

  function onSeasonChange(value: string) {
    setSeasonId(value);
    setOffset(0);
  }

  function onTeamChange(value: string) {
    setTeamId(value);
    setOffset(0);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Матчи"
        description="Расписание и результаты. Счёт по сетам доступен в карточке матча."
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="match-season" className="text-sm font-medium text-muted">
            Сезон
          </label>
          <select
            id="match-season"
            value={seasonId}
            onChange={(e) => onSeasonChange(e.target.value)}
            className="rounded-md border border-line bg-card px-3 py-2"
          >
            <option value="">Все сезоны</option>
            {seasonsQuery.data?.items.map((season) => (
              <option key={season.id} value={season.id}>
                {season.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="match-team" className="text-sm font-medium text-muted">
            Команда
          </label>
          <select
            id="match-team"
            value={teamId}
            onChange={(e) => onTeamChange(e.target.value)}
            className="rounded-md border border-line bg-card px-3 py-2"
          >
            <option value="">Все команды</option>
            {teamsQuery.data?.items.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {matchesQuery.isLoading ? <LoadingBlock /> : null}
      {matchesQuery.isError ? (
        <ErrorBlock error={matchesQuery.error} onRetry={() => matchesQuery.refetch()} />
      ) : null}

      {matchesQuery.data ? (
        <>
          <DemoBadge dataOrigin={matchesQuery.data.data_origin} />
          {matchesQuery.data.items.length === 0 ? (
            <EmptyBlock>Матчи по выбранным фильтрам не найдены.</EmptyBlock>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-line">
              <table className="w-full min-w-[32rem] text-left text-sm">
                <thead className="bg-card text-muted">
                  <tr>
                    <th className="px-4 py-3 font-medium">Дата</th>
                    <th className="px-4 py-3 font-medium">Матч</th>
                    <th className="px-4 py-3 font-medium">Статус</th>
                    <th className="px-4 py-3 font-medium">Площадка</th>
                  </tr>
                </thead>
                <tbody>
                  {matchesQuery.data.items.map((item) => (
                    <tr key={item.id} className="border-t border-line">
                      <td className="px-4 py-3 whitespace-nowrap">
                        {formatDateTime(item.scheduled_at)}
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          href={`/matches/${item.id}`}
                          className="text-accent hover:underline"
                        >
                          {item.home_team.name} — {item.away_team.name}
                        </Link>
                      </td>
                      <td className="px-4 py-3">{matchStatusLabel(item.status)}</td>
                      <td className="px-4 py-3 text-muted">
                        {item.venue ?? "Нейтральная / не указана"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <PaginationControls
            pagination={matchesQuery.data.pagination}
            onPageChange={setOffset}
          />
        </>
      ) : null}
    </div>
  );
}
