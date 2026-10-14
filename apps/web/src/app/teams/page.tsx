"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { PaginationControls } from "@/components/ui/pagination-controls";
import { fetchTeams } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

const PAGE_SIZE = 20;

export default function TeamsPage() {
  const [offset, setOffset] = useState(0);

  const query = useQuery({
    queryKey: queryKeys.teams(PAGE_SIZE, offset),
    queryFn: () => fetchTeams(PAGE_SIZE, offset),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Команды"
        description="Список команд демо-лиги. Детальная статистика доступна в карточке команды."
      />

      {query.isLoading ? <LoadingBlock /> : null}
      {query.isError ? (
        <ErrorBlock error={query.error} onRetry={() => query.refetch()} />
      ) : null}

      {query.data ? (
        <>
          <DemoBadge dataOrigin={query.data.data_origin} />
          {query.data.items.length === 0 ? (
            <EmptyBlock>Команды не найдены.</EmptyBlock>
          ) : (
            <ul className="grid gap-3 sm:grid-cols-2">
              {query.data.items.map((team) => (
                <li key={team.id}>
                  <Link
                    href={`/teams/${team.id}`}
                    className="block rounded-lg border border-line bg-card px-4 py-4 transition hover:border-accent/50"
                  >
                    <span className="text-lg font-medium">{team.name}</span>
                    <span className="mt-1 block text-sm text-muted">{team.slug}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          <PaginationControls
            pagination={query.data.pagination}
            onPageChange={setOffset}
          />
        </>
      ) : null}
    </div>
  );
}
