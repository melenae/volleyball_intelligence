"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Suspense } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { MatchOutcomeMessage } from "@/components/matches/match-outcome";
import { SetResultsTable } from "@/components/matches/set-results-table";
import { PageHeader } from "@/components/page-header";
import { ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { fetchMatch } from "@/lib/api";
import { formatDateTime, matchStatusLabel } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";

function MatchDetailContent() {
  const params = useParams<{ id: string }>();
  const matchId = params.id;

  const query = useQuery({
    queryKey: queryKeys.match(matchId),
    queryFn: () => fetchMatch(matchId),
  });

  if (query.isLoading) {
    return <LoadingBlock />;
  }

  if (query.isError) {
    return (
      <ErrorBlock error={query.error} onRetry={() => query.refetch()} />
    );
  }

  if (!query.data) {
    return null;
  }

  const { home_team, away_team, match } = query.data;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`${home_team.name} — ${away_team.name}`}
        description={`${formatDateTime(match.scheduled_at)} · ${matchStatusLabel(match.status)}`}
      />
      <DemoBadge dataOrigin={query.data.data_origin} />

      <div className="flex flex-wrap gap-4 text-sm">
        <Link href={`/teams/${home_team.id}`} className="text-accent hover:underline">
          {home_team.name} (дома)
        </Link>
        <Link href={`/teams/${away_team.id}`} className="text-accent hover:underline">
          {away_team.name} (гости)
        </Link>
      </div>

      <p className="text-muted">
        Площадка: {match.venue?.trim() ? match.venue : "Нейтральная / не указана"}
      </p>

      <MatchOutcomeMessage detail={query.data} />
      <SetResultsTable detail={query.data} />
    </div>
  );
}

export default function MatchDetailPage() {
  return (
    <Suspense fallback={<LoadingBlock />}>
      <MatchDetailContent />
    </Suspense>
  );
}
