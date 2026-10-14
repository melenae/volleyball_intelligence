import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.ingestion.demo.seed import seed_demo_league
from app.models import Match
from app.services.match_result import SetScoreInput, evaluate_match_result

pytestmark = pytest.mark.postgres


def test_demo_valid_match_has_winner(db_session: Session) -> None:
    seed_demo_league(db_session)
    match = db_session.scalar(
        select(Match)
        .where(Match.venue == "Спорткомплекс «Север»")
        .options(selectinload(Match.set_results))
    )
    assert match is not None
    evaluation = evaluate_match_result(
        status=match.status,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        sets=[
            SetScoreInput(row.set_number, row.home_score, row.away_score)
            for row in match.set_results
        ],
    )
    assert evaluation.is_valid_completed_match is True
    assert evaluation.winner_side == "home"


def test_demo_tied_sets_match_has_no_winner(db_session: Session) -> None:
    seed_demo_league(db_session)
    match = db_session.scalar(
        select(Match)
        .where(Match.venue.is_(None), Match.status == "completed")
        .options(selectinload(Match.set_results))
    )
    assert match is not None
    evaluation = evaluate_match_result(
        status=match.status,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        sets=[
            SetScoreInput(row.set_number, row.home_score, row.away_score)
            for row in match.set_results
        ],
    )
    assert evaluation.is_valid_completed_match is False
    assert evaluation.winner_side == "none"
