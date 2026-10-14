from app.analytics.types import MatchForAnalytics
from app.models import Match
from app.services.match_result import SetScoreInput


def match_to_analytics(match: Match) -> MatchForAnalytics:
    sets = tuple(
        SetScoreInput(
            set_number=row.set_number, home_score=row.home_score, away_score=row.away_score
        )
        for row in sorted(match.set_results, key=lambda item: item.set_number)
    )
    return MatchForAnalytics(
        match_id=match.id,
        season_id=match.season_id,
        scheduled_at=match.scheduled_at,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        status=match.status,
        sets=sets,
    )
