"use client";

import type { PaginationMeta } from "@/types/api";

type Props = {
  pagination: PaginationMeta;
  onPageChange: (offset: number) => void;
};

export function PaginationControls({ pagination, onPageChange }: Props) {
  const { limit, offset, total } = pagination;
  if (total <= limit) {
    return null;
  }

  const page = Math.floor(offset / limit) + 1;
  const pageCount = Math.ceil(total / limit);
  const prevOffset = Math.max(0, offset - limit);
  const nextOffset = offset + limit;
  const hasPrev = offset > 0;
  const hasNext = nextOffset < total;

  return (
    <nav
      className="flex flex-wrap items-center justify-between gap-3 text-sm"
      aria-label="Пагинация"
    >
      <span className="text-muted">
        Страница {page} из {pageCount} ({total} записей)
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={!hasPrev}
          onClick={() => onPageChange(prevOffset)}
          className="rounded-md border border-line px-3 py-1.5 disabled:opacity-40"
        >
          Назад
        </button>
        <button
          type="button"
          disabled={!hasNext}
          onClick={() => onPageChange(nextOffset)}
          className="rounded-md border border-line px-3 py-1.5 disabled:opacity-40"
        >
          Вперёд
        </button>
      </div>
    </nav>
  );
}
