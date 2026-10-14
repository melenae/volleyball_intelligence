from datetime import UTC, datetime
from uuid import UUID

from app.analytics.types import MatchForAnalytics, TeamMatchTimelineEntry, TeamStatistics
from app.services.match_result import evaluate_match_result


def _sort_key(match: MatchForAnalytics) -> tuple[int, datetime, UUID]:
    scheduled = match.scheduled_at
    if scheduled is None:
        return (1, datetime.min.replace(tzinfo=UTC), match.match_id)
    if scheduled.tzinfo is None:
        scheduled = scheduled.replace(tzinfo=UTC)
    return (0, scheduled, match.match_id)


def compute_team_statistics(
    team_id: UUID,
    matches: list[MatchForAnalytics],
) -> TeamStatistics:
    """Aggregate team metrics from canonical match rows (already loaded from PostgreSQL)."""

    relevant = [match for match in matches if team_id in (match.home_team_id, match.away_team_id)]
    relevant.sort(key=_sort_key)

    wins = 0
    losses = 0
    sets_won = 0
    sets_lost = 0
    points_for = 0
    points_against = 0
    played_matches = 0
    timeline: list[TeamMatchTimelineEntry] = []

    for match in relevant:
        evaluation = evaluate_match_result(
            status=match.status,
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id,
            sets=list(match.sets),
        )
        if not evaluation.is_valid_completed_match:
            continue

        played_matches += 1
        is_home = match.home_team_id == team_id
        team_sets_won = evaluation.home_sets_won if is_home else evaluation.away_sets_won
        opponent_sets_won = evaluation.away_sets_won if is_home else evaluation.home_sets_won
        sets_won += team_sets_won
        sets_lost += opponent_sets_won

        for set_row in sorted(match.sets, key=lambda row: row.set_number):
            if is_home:
                points_for += set_row.home_score
                points_against += set_row.away_score
            else:
                points_for += set_row.away_score
                points_against += set_row.home_score

        team_won = (evaluation.winner_side == "home" and is_home) or (
            evaluation.winner_side == "away" and not is_home
        )
        if team_won:
            wins += 1
            result = "win"
        else:
            losses += 1
            result = "loss"

        opponent_id = match.away_team_id if is_home else match.home_team_id
        timeline.append(
            TeamMatchTimelineEntry(
                match_id=match.match_id,
                scheduled_at=match.scheduled_at,
                opponent_team_id=opponent_id,
                is_home=is_home,
                result=result,
                home_sets_won=evaluation.home_sets_won,
                away_sets_won=evaluation.away_sets_won,
            )
        )

    win_percentage = None if played_matches == 0 else wins / played_matches * 100

    return TeamStatistics(
        played_matches=played_matches,
        wins=wins,
        losses=losses,
        sets_won=sets_won,
        sets_lost=sets_lost,
        points_for=points_for,
        points_against=points_against,
        win_percentage=win_percentage,
        match_timeline=tuple(timeline),
    )
