"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { SeasonSelect } from "@/components/ui/season-select";
import { fetchDashboardSummary, fetchSeasons } from "@/lib/api";
import { formatDateTime, formatWinPercentage, matchStatusLabel } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";

export function DashboardView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const seasonId = searchParams.get("season_id") ?? "";

  const seasonsQuery = useQuery({
    queryKey: queryKeys.seasons(50, 0),
    queryFn: () => fetchSeasons(50, 0),
  });

  const dashboardQuery = useQuery({
    queryKey: queryKeys.dashboard(seasonId),
    queryFn: () => fetchDashboardSummary(seasonId),
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
    router.replace(query ? `/?${query}` : "/");
  }

  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Обзор сезона"
        description="Сводка турнирной таблицы и последних матчей по данным API."
      />

      {seasonsQuery.isLoading ? <LoadingBlock label="Загрузка сезонов…" /> : null}
      {seasonsQuery.isError ? (
        <ErrorBlock error={seasonsQuery.error} onRetry={() => seasonsQuery.refetch()} />
      ) : null}

      {seasonsQuery.data ? (
        <SeasonSelect
          id="dashboard-season"
          label="Сезон"
          seasons={seasonsQuery.data.items}
          value={seasonId}
          onChange={onSeasonChange}
        />
      ) : null}

      {!seasonId && seasonsQuery.isSuccess ? (
        <EmptyBlock>Выберите сезон, чтобы увидеть сводку и таблицу.</EmptyBlock>
      ) : null}

      {seasonId && dashboardQuery.isLoading ? (
        <LoadingBlock label="Загрузка сводки…" />
      ) : null}
      {seasonId && dashboardQuery.isError ? (
        <ErrorBlock
          error={dashboardQuery.error}
          onRetry={() => dashboardQuery.refetch()}
        />
      ) : null}

      {dashboardQuery.data ? (
        <div className="flex flex-col gap-8">
          <DemoBadge dataOrigin={dashboardQuery.data.data_origin} />

          <section aria-labelledby="season-metrics">
            <h2 id="season-metrics" className="mb-3 text-xl font-medium">
              {dashboardQuery.data.season_name}
            </h2>
            <dl className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg border border-line bg-card p-4">
                <dt className="text-sm text-muted">Команд</dt>
                <dd className="text-2xl font-semibold">
                  {dashboardQuery.data.teams_count}
                </dd>
              </div>
              <div className="rounded-lg border border-line bg-card p-4">
                <dt className="text-sm text-muted">Матчей в сезоне</dt>
                <dd className="text-2xl font-semibold">
                  {dashboardQuery.data.matches_total}
                </dd>
              </div>
              <div className="rounded-lg border border-line bg-card p-4">
                <dt className="text-sm text-muted">Корректно завершённых</dt>
                <dd className="text-2xl font-semibold">
                  {dashboardQuery.data.matches_valid_completed}
                </dd>
              </div>
            </dl>
          </section>

          <section aria-labelledby="standings-title">
            <h2 id="standings-title" className="mb-3 text-xl font-medium">
              Турнирная таблица
            </h2>
            {dashboardQuery.data.standings.length === 0 ? (
              <EmptyBlock>Нет данных для таблицы в этом сезоне.</EmptyBlock>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-line">
                <table className="w-full min-w-[32rem] text-left text-sm">
                  <thead className="bg-card text-muted">
                    <tr>
                      <th className="px-4 py-3 font-medium">Команда</th>
                      <th className="px-4 py-3 font-medium">И</th>
                      <th className="px-4 py-3 font-medium">В</th>
                      <th className="px-4 py-3 font-medium">П</th>
                      <th className="px-4 py-3 font-medium">% побед</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardQuery.data.standings.map((row) => (
                      <tr key={row.team_id} className="border-t border-line">
                        <td className="px-4 py-3">
                          <Link
                            href={`/teams/${row.team_id}`}
                            className="text-accent hover:underline"
                          >
                            {row.team_name}
                          </Link>
                        </td>
                        <td className="px-4 py-3">{row.played_matches}</td>
                        <td className="px-4 py-3">{row.wins}</td>
                        <td className="px-4 py-3">{row.losses}</td>
                        <td className="px-4 py-3">
                          {formatWinPercentage(row.win_percentage)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section aria-labelledby="recent-matches-title">
            <h2 id="recent-matches-title" className="mb-3 text-xl font-medium">
              Последние матчи
            </h2>
            {dashboardQuery.data.recent_matches.length === 0 ? (
              <EmptyBlock>Матчи для отображения отсутствуют.</EmptyBlock>
            ) : (
              <ul className="divide-y divide-line rounded-lg border border-line">
                {dashboardQuery.data.recent_matches.map((item) => (
                  <li key={item.id} className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <Link
                        href={`/matches/${item.id}`}
                        className="font-medium text-accent hover:underline"
                      >
                        {item.home_team.name} — {item.away_team.name}
                      </Link>
                      <p className="text-sm text-muted">
                        {formatDateTime(item.scheduled_at)} ·{" "}
                        {matchStatusLabel(item.status)}
                      </p>
                    </div>
                    {item.venue ? (
                      <span className="text-sm text-muted">{item.venue}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      ) : null}
    </div>
  );
}
