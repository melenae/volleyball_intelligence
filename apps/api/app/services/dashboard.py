from uuid import UUID

from sqlalchemy.orm import Session

from app.analytics.team import compute_team_statistics
from app.models import Season
from app.repositories.match import MatchRepository
from app.repositories.season import SeasonRepository
from app.repositories.team import TeamRepository
from app.services.match_mapper import match_to_analytics
from app.services.match_result import evaluate_match_result


class DashboardService:
    def __init__(self, session: Session) -> None:
        self._seasons = SeasonRepository(session)
        self._teams = TeamRepository(session)
        self._matches = MatchRepository(session)

    def get_season(self, season_id: UUID) -> Season | None:
        return self._seasons.get_by_id(season_id)

    def build_summary(self, season_id: UUID) -> dict:
        season = self._seasons.get_by_id(season_id)
        if season is None:
            return None

        matches = self._matches.list_matches_for_season_with_sets(season_id)
        analytics_rows = [match_to_analytics(match) for match in matches]

        valid_completed = 0
        for row in analytics_rows:
            evaluation = evaluate_match_result(
                status=row.status,
                home_team_id=row.home_team_id,
                away_team_id=row.away_team_id,
                sets=list(row.sets),
            )
            if evaluation.is_valid_completed_match:
                valid_completed += 1

        teams = self._teams.list_all()
        standings = []
        for team in teams:
            stats = compute_team_statistics(team.id, analytics_rows)
            standings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "team_slug": team.slug,
                    "played_matches": stats.played_matches,
                    "wins": stats.wins,
                    "losses": stats.losses,
                    "win_percentage": stats.win_percentage,
                }
            )
        standings.sort(
            key=lambda row: (
                -row["wins"],
                -(row["win_percentage"] or 0.0),
                row["team_name"],
            )
        )

        recent_matches = list(reversed(matches))[:5]

        return {
            "season": season,
            "teams_count": len(teams),
            "matches_total": len(matches),
            "matches_valid_completed": valid_completed,
            "standings": standings,
            "recent_matches": recent_matches,
        }
