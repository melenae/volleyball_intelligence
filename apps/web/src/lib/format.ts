export function formatWinPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "Нет данных";
  }
  return `${value.toFixed(1)}%`;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "Дата не назначена";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function matchStatusLabel(status: string): string {
  switch (status) {
    case "scheduled":
      return "Запланирован";
    case "completed":
      return "Завершён";
    case "cancelled":
      return "Отменён";
    default:
      return status;
  }
}

export function matchScoreLine(
  item: { status: string; home_team: { name: string }; away_team: { name: string } },
  sets?: Array<{ home_score: number; away_score: number }>,
): string {
  if (item.status !== "completed" || !sets || sets.length === 0) {
    return "—";
  }
  const homeSets = sets.filter((set) => set.home_score > set.away_score).length;
  const awaySets = sets.length - homeSets;
  return `${homeSets}:${awaySets}`;
}
