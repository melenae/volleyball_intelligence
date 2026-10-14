from uuid import UUID

from fastapi import HTTPException

from app.models import Match, Team
from app.schemas.api_responses import MatchListItem, MatchTeamSummary
from app.schemas.common import MatchRead
from app.services.match_result import SetScoreInput, evaluate_match_result


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "not_found", "message": message})


def team_summary(team: Team) -> MatchTeamSummary:
    return MatchTeamSummary(id=team.id, name=team.name, slug=team.slug)


def match_list_item(match: Match) -> MatchListItem:
    return MatchListItem(
        id=match.id,
        season_id=match.season_id,
        scheduled_at=match.scheduled_at,
        status=match.status.value,
        venue=match.venue,
        home_team=team_summary(match.home_team),
        away_team=team_summary(match.away_team),
    )


def match_read(match: Match) -> MatchRead:
    return MatchRead(
        id=match.id,
        season_id=match.season_id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        scheduled_at=match.scheduled_at,
        status=match.status.value,
        venue=match.venue,
    )


def evaluate_match(match: Match):
    sets = [
        SetScoreInput(
            set_number=row.set_number, home_score=row.home_score, away_score=row.away_score
        )
        for row in sorted(match.set_results, key=lambda item: item.set_number)
    ]
    return evaluate_match_result(
        status=match.status,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        sets=sets,
    )


def winner_team_id(match: Match) -> UUID | None:
    evaluation = evaluate_match(match)
    if not evaluation.is_valid_completed_match:
        return None
    if evaluation.winner_side == "home":
        return match.home_team_id
    if evaluation.winner_side == "away":
        return match.away_team_id
    return None
