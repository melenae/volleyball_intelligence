"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { DemoBadge } from "@/components/demo-badge";
import { PageHeader } from "@/components/page-header";
import { EmptyBlock, ErrorBlock, LoadingBlock } from "@/components/ui/async-state";
import { PaginationControls } from "@/components/ui/pagination-controls";
import { fetchPlayers } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

const PAGE_SIZE = 20;

export default function PlayersPage() {
  const [offset, setOffset] = useState(0);

  const query = useQuery({
    queryKey: queryKeys.players(PAGE_SIZE, offset),
    queryFn: () => fetchPlayers(PAGE_SIZE, offset),
  });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Игроки"
        description="Список игроков демо-лиги. Личная игровая статистика пока не собирается."
      />

      {query.isLoading ? <LoadingBlock /> : null}
      {query.isError ? (
        <ErrorBlock error={query.error} onRetry={() => query.refetch()} />
      ) : null}

      {query.data ? (
        <>
          <DemoBadge dataOrigin={query.data.data_origin} />
          {query.data.items.length === 0 ? (
            <EmptyBlock>Игроки не найдены.</EmptyBlock>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-line">
              <table className="w-full min-w-[24rem] text-left text-sm">
                <thead className="bg-card text-muted">
                  <tr>
                    <th className="px-4 py-3 font-medium">Игрок</th>
                    <th className="px-4 py-3 font-medium">Позиция</th>
                  </tr>
                </thead>
                <tbody>
                  {query.data.items.map((player) => (
                    <tr key={player.id} className="border-t border-line">
                      <td className="px-4 py-3">
                        <Link
                          href={`/players/${player.id}`}
                          className="font-medium text-accent hover:underline"
                        >
                          {player.display_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-muted">
                        {player.position ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
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
