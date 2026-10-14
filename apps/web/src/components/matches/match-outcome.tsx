import type { MatchDetailResponse } from "@/types/api";

export function MatchOutcomeMessage({ detail }: { detail: MatchDetailResponse }) {
  const { match, is_valid_completed_match, winner_team_id, home_team, away_team } =
    detail;

  if (match.status === "scheduled") {
    return (
      <p className="text-muted">
        Матч запланирован. Итоговый счёт появится после завершения игры.
      </p>
    );
  }

  if (match.status === "cancelled") {
    return <p className="text-muted">Матч отменён. Результат не учитывается.</p>;
  }

  if (match.status !== "completed") {
    return <p className="text-muted">Статус матча: {match.status}</p>;
  }

  if (!is_valid_completed_match || !winner_team_id) {
    return (
      <p className="rounded-md border border-line bg-card px-3 py-2 text-sm text-muted">
        Результат матча некорректен или победитель не определён. Счёт по сетам
        приведён только для справки.
      </p>
    );
  }

  const winnerName =
    winner_team_id === home_team.id ? home_team.name : away_team.name;

  return (
    <p className="text-ok font-medium" role="status">
      Победитель: {winnerName}
    </p>
  );
}
