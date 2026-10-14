import uuid

from app.models.enums import MatchStatus
from app.services.match_result import InvalidMatchReason, SetScoreInput, evaluate_match_result


def test_valid_three_set_match_home_wins() -> None:
    home_id, away_id = uuid.uuid4(), uuid.uuid4()
    result = evaluate_match_result(
        status=MatchStatus.completed,
        home_team_id=home_id,
        away_team_id=away_id,
        sets=[
            SetScoreInput(1, 25, 21),
            SetScoreInput(2, 23, 25),
            SetScoreInput(3, 25, 18),
        ],
    )
    assert result.is_valid_completed_match is True
    assert result.winner_side == "home"
    assert result.home_sets_won == 2
    assert result.away_sets_won == 1


def test_scheduled_match_has_no_winner() -> None:
    result = evaluate_match_result(
        status=MatchStatus.scheduled,
        home_team_id=uuid.uuid4(),
        away_team_id=uuid.uuid4(),
        sets=[],
    )
    assert result.is_valid_completed_match is False
    assert result.winner_side == "none"
    assert result.reason == InvalidMatchReason.not_completed


def test_tied_sets_won_is_invalid() -> None:
    result = evaluate_match_result(
        status=MatchStatus.completed,
        home_team_id=uuid.uuid4(),
        away_team_id=uuid.uuid4(),
        sets=[
            SetScoreInput(1, 25, 20),
            SetScoreInput(2, 22, 25),
            SetScoreInput(3, 25, 23),
            SetScoreInput(4, 21, 25),
        ],
    )
    assert result.is_valid_completed_match is False
    assert result.winner_side == "none"
    assert result.reason == InvalidMatchReason.tied_sets_won


def test_gap_in_set_numbers_is_invalid() -> None:
    result = evaluate_match_result(
        status=MatchStatus.completed,
        home_team_id=uuid.uuid4(),
        away_team_id=uuid.uuid4(),
        sets=[SetScoreInput(1, 25, 20), SetScoreInput(3, 25, 22)],
    )
    assert result.is_valid_completed_match is False
    assert result.reason == InvalidMatchReason.invalid_set_numbers


def test_same_teams_is_invalid() -> None:
    team_id = uuid.uuid4()
    result = evaluate_match_result(
        status=MatchStatus.completed,
        home_team_id=team_id,
        away_team_id=team_id,
        sets=[SetScoreInput(1, 25, 20)],
    )
    assert result.is_valid_completed_match is False
    assert result.reason == InvalidMatchReason.same_teams
