"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TeamAnalyticsResponse } from "@/types/api";
import { formatDateTime } from "@/lib/format";

type Props = {
  analytics: TeamAnalyticsResponse;
  teamName: string;
};

export function TeamTimelineChart({ analytics, teamName }: Props) {
  const timeline = analytics.statistics.match_timeline;
  if (timeline.length === 0) {
    return null;
  }

  const data = timeline.map((item, index) => {
    const setsFor =
      item.is_home ? item.home_sets_won : item.away_sets_won;
    const setsAgainst =
      item.is_home ? item.away_sets_won : item.home_sets_won;
    return {
      label: item.scheduled_at
        ? formatDateTime(item.scheduled_at)
        : `Матч ${index + 1}`,
      setsFor,
      setsAgainst,
      result: item.result === "win" ? "Победа" : "Поражение",
    };
  });

  return (
    <section aria-labelledby="team-timeline-chart">
      <h2 id="team-timeline-chart" className="mb-3 text-xl font-medium">
        Сеты по матчам ({teamName})
      </h2>
      <div className="h-72 w-full rounded-lg border border-line bg-card p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a3b55" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={60} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="setsFor" name="Сеты за" fill="#e8a317" />
            <Bar dataKey="setsAgainst" name="Сеты против" fill="#93a4bd" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
