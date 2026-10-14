"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { TeamTimelineChart } from "@/components/teams/team-timeline-chart";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { SeasonSelect } from "@/components/ui/season-select";
import {
  fetchSeasons,
  fetchTeam,
  fetchTeamAnalytics,
  fetchTeamPlayers,
} from "@/lib/api";
import { formatDateTime, formatWinPercentage } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";

function TeamDetailContent() {
  const params = useParams<{ id: string }>();
  const teamId = params.id;
  const router = useRouter();
  const searchParams = useSearchParams();
  const seasonId = searchParams.get("season_id") ?? "";

  const teamQuery = useQuery({
    queryKey: queryKeys.team(teamId),
    queryFn: () => fetchTeam(teamId),
  });

  const seasonsQuery = useQuery({
    queryKey: queryKeys.seasons(50, 0),
    queryFn: () => fetchSeasons(50, 0),
  });

  const playersQuery = useQuery({
    queryKey: queryKeys.teamPlayers(teamId, seasonId),
    queryFn: () => fetchTeamPlayers(teamId, seasonId),
    enabled: Boolean(seasonId),
  });

  const analyticsQuery = useQuery({
    queryKey: queryKeys.teamAnalytics(teamId, seasonId),
    queryFn: () => fetchTeamAnalytics(teamId, seasonId),
    enabled: Boolean(seasonId),
  });

  function onSeasonChange(next: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (next) {
      params.set("season_id", next);
    } else {
      params.delete("season_id");
    }
    const query = params.toString();
    router.replace(`/teams/${teamId}${query ? `?${query}` : ""}`);
  }

  const loading = teamQuery.isLoading || seasonsQuery.isLoading;
  const teamError = teamQuery.isError ? teamQuery.error : null;

  return (
    <div className="flex flex-col gap-8">
      {loading ? <LoadingBlock /> : null}
      {teamError ? (
        <ErrorBlock error={teamError} onRetry={() => teamQuery.refetch()} />
      ) : null}

      {teamQuery.data ? (
        <>
          <PageHeader title={teamQuery.data.team.name} />
          <DemoBadge dataOrigin={teamQuery.data.data_origin} />
        </>
      ) : null}

      {seasonsQuery.data ? (
        <SeasonSelect
          id="team-season"
          label="Сезон для статистики и состава"
          seasons={seasonsQuery.data.items}
          value={seasonId}
          onChange={onSeasonChange}
        />
      ) : null}

      {!seasonId && seasonsQuery.isSuccess ? (
        <EmptyBlock>Выберите сезон, чтобы увидеть состав и статистику.</EmptyBlock>
      ) : null}

      {seasonId && analyticsQuery.isLoading ? (
        <LoadingBlock label="Загрузка статистики…" />
      ) : null}
      {seasonId && analyticsQuery.isError ? (
        <ErrorBlock
          error={analyticsQuery.error}
          onRetry={() => analyticsQuery.refetch()}
        />
      ) : null}

      {analyticsQuery.data ? (
        <section aria-labelledby="team-stats">
          <h2 id="team-stats" className="mb-3 text-xl font-medium">
            Статистика сезона
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Матчей" value={analyticsQuery.data.statistics.played_matches} />
            <Stat label="Побед" value={analyticsQuery.data.statistics.wins} />
            <Stat label="Поражений" value={analyticsQuery.data.statistics.losses} />
            <Stat
              label="% побед"
              value={formatWinPercentage(analyticsQuery.data.statistics.win_percentage)}
            />
            <Stat label="Сеты +" value={analyticsQuery.data.statistics.sets_won} />
            <Stat label="Сеты −" value={analyticsQuery.data.statistics.sets_lost} />
            <Stat label="Очки за" value={analyticsQuery.data.statistics.points_for} />
            <Stat
              label="Очки против"
              value={analyticsQuery.data.statistics.points_against}
            />
          </div>
          <TeamTimelineChart
            analytics={analyticsQuery.data}
            teamName={teamQuery.data?.team.name ?? ""}
          />
          {analyticsQuery.data.statistics.match_timeline.length > 0 ? (
            <div className="mt-6 overflow-x-auto rounded-lg border border-line">
              <table className="w-full min-w-[28rem] text-left text-sm">
                <caption className="px-4 py-3 text-left font-medium">
                  Матчи команды
                </caption>
                <thead className="bg-card text-muted">
                  <tr>
                    <th className="px-4 py-2 font-medium">Дата</th>
                    <th className="px-4 py-2 font-medium">Счёт по сетам</th>
                    <th className="px-4 py-2 font-medium">Исход</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsQuery.data.statistics.match_timeline.map((item) => (
                    <tr key={item.match_id} className="border-t border-line">
                      <td className="px-4 py-2">
                        <Link
                          href={`/matches/${item.match_id}`}
                          className="text-accent hover:underline"
                        >
                          {formatDateTime(item.scheduled_at)}
                        </Link>
                      </td>
                      <td className="px-4 py-2">
                        {item.home_sets_won}:{item.away_sets_won}
                      </td>
                      <td className="px-4 py-2">
                        {item.result === "win" ? "Победа" : "Поражение"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      ) : null}

      {seasonId && playersQuery.isLoading ? (
        <LoadingBlock label="Загрузка состава…" />
      ) : null}
      {seasonId && playersQuery.isError ? (
        <ErrorBlock
          error={playersQuery.error}
          onRetry={() => playersQuery.refetch()}
        />
      ) : null}

      {playersQuery.data ? (
        <section aria-labelledby="team-roster">
          <h2 id="team-roster" className="mb-3 text-xl font-medium">Состав</h2>
          {playersQuery.data.players.length === 0 ? (
            <EmptyBlock>В этом сезоне игроки не заявлены.</EmptyBlock>
          ) : (
            <ul className="divide-y divide-line rounded-lg border border-line">
              {playersQuery.data.players.map(({ player, jersey_number }) => (
                <li
                  key={player.id}
                  className="flex items-center justify-between gap-4 px-4 py-3"
                >
                  <Link
                    href={`/players/${player.id}`}
                    className="font-medium text-accent hover:underline"
                  >
                    {player.display_name}
                  </Link>
                  <span className="text-sm text-muted">
                    {jersey_number != null ? `№ ${jersey_number}` : "—"}
                    {player.position ? ` · ${player.position}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      ) : null}
    </div>
  );
}

function Stat({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border border-line bg-card p-3">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-xl font-semibold">{value}</dd>
    </div>
  );
}

export default function TeamDetailPage() {
  return (
    <Suspense fallback={<LoadingBlock />}>
      <TeamDetailContent />
    </Suspense>
  );
}
