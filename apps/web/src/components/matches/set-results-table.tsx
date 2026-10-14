import type { MatchDetailResponse } from "@/types/api";

export function SetResultsTable({ detail }: { detail: MatchDetailResponse }) {
  const { set_results, match } = detail;

  if (match.status !== "completed" || set_results.length === 0) {
    return null;
  }

  return (
    <table className="w-full text-left text-sm">
      <caption className="mb-2 text-left font-medium">Сеты</caption>
      <thead>
        <tr className="border-b border-line text-muted">
          <th className="py-2 pr-4 font-medium">Сет</th>
          <th className="py-2 pr-4 font-medium">{detail.home_team.name}</th>
          <th className="py-2 font-medium">{detail.away_team.name}</th>
        </tr>
      </thead>
      <tbody>
        {set_results.map((set) => (
          <tr key={set.set_number} className="border-b border-line/60">
            <td className="py-2 pr-4">{set.set_number}</td>
            <td className="py-2 pr-4">{set.home_score}</td>
            <td className="py-2">{set.away_score}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
