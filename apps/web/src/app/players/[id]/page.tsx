"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { SeasonSelect } from "@/components/ui/season-select";
import { fetchPlayer, fetchPlayerAnalytics, fetchSeasons, fetchTeams } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

function PlayerDetailContent() {
  const params = useParams<{ id: string }>();
  const playerId = params.id;
  const router = useRouter();
  const searchParams = useSearchParams();
  const seasonId = searchParams.get("season_id") ?? "";

  const playerQuery = useQuery({
    queryKey: queryKeys.player(playerId),
    queryFn: () => fetchPlayer(playerId),
  });

  const seasonsQuery = useQuery({
    queryKey: queryKeys.seasons(50, 0),
    queryFn: () => fetchSeasons(50, 0),
  });

  const analyticsQuery = useQuery({
    queryKey: queryKeys.playerAnalytics(playerId, seasonId || undefined),
    queryFn: () =>
      fetchPlayerAnalytics(playerId, seasonId ? seasonId : undefined),
    enabled: playerQuery.isSuccess,
  });

  const teamsQuery = useQuery({
    queryKey: queryKeys.teams(100, 0),
    queryFn: () => fetchTeams(100, 0),
    enabled: Boolean(analyticsQuery.data?.rosters.length),
  });

  const teamNameById = useMemo(() => {
    const map = new Map<string, string>();
    teamsQuery.data?.items.forEach((team) => map.set(team.id, team.name));
    return map;
  }, [teamsQuery.data]);

  function onSeasonChange(next: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (next) {
      params.set("season_id", next);
    } else {
      params.delete("season_id");
    }
    const query = params.toString();
    router.replace(`/players/${playerId}${query ? `?${query}` : ""}`);
  }

  const filteredRosters =
    analyticsQuery.data?.rosters.filter((entry) =>
      seasonId ? entry.season_id === seasonId : true,
    ) ?? [];

  return (
    <div className="flex flex-col gap-8">
      {playerQuery.isLoading ? <LoadingBlock /> : null}
      {playerQuery.isError ? (
        <ErrorBlock error={playerQuery.error} onRetry={() => playerQuery.refetch()} />
      ) : null}

      {playerQuery.data ? (
        <>
          <PageHeader
            title={playerQuery.data.player.display_name}
            description={
              playerQuery.data.player.position
                ? `Позиция: ${playerQuery.data.player.position}`
                : undefined
            }
          />
          <DemoBadge dataOrigin={playerQuery.data.data_origin} />
        </>
      ) : null}

      <p className="rounded-md border border-line bg-card px-4 py-3 text-sm text-muted">
        Личная статистика игровых действий (эйсы, атаки, блоки, приём) пока не
        собирается — в системе нет событий матча для расчёта этих показателей.
      </p>

      {seasonsQuery.data ? (
        <SeasonSelect
          id="player-season-filter"
          label="Фильтр по сезону (необязательно)"
          seasons={seasonsQuery.data.items}
          value={seasonId}
          onChange={onSeasonChange}
          placeholder="Все сезоны"
        />
      ) : null}

      {analyticsQuery.isLoading ? <LoadingBlock label="Загрузка составов…" /> : null}
      {analyticsQuery.isError ? (
        <ErrorBlock
          error={analyticsQuery.error}
          onRetry={() => analyticsQuery.refetch()}
        />
      ) : null}

      {analyticsQuery.data ? (
        <section aria-labelledby="player-rosters">
          <h2 id="player-rosters" className="mb-2 text-xl font-medium">
            Заявки по сезонам
          </h2>
          <p className="mb-4 text-sm text-muted">{analyticsQuery.data.note}</p>
          {filteredRosters.length === 0 ? (
            <EmptyBlock>Записей о составе не найдено.</EmptyBlock>
          ) : (
            <ul className="divide-y divide-line rounded-lg border border-line">
              {filteredRosters.map((entry) => (
                <li
                  key={`${entry.season_id}-${entry.team_id}`}
                  className="flex flex-wrap items-center justify-between gap-2 px-4 py-3"
                >
                  <Link
                    href={`/teams/${entry.team_id}`}
                    className="text-accent hover:underline"
                  >
                    {teamNameById.get(entry.team_id) ?? `Команда ${entry.team_id}`}
                  </Link>
                  <span className="text-sm text-muted">
                    Сезон:{" "}
                    {seasonsQuery.data?.items.find((s) => s.id === entry.season_id)
                      ?.name ?? entry.season_id}
                    {entry.jersey_number != null
                      ? ` · № ${entry.jersey_number}`
                      : ""}
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

export default function PlayerDetailPage() {
  return (
    <Suspense fallback={<LoadingBlock />}>
      <PlayerDetailContent />
    </Suspense>
  );
}
