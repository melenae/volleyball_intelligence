import uuid
from datetime import UTC, datetime

from app.analytics.team import compute_team_statistics
from app.analytics.types import MatchForAnalytics
from app.models.enums import MatchStatus
from app.services.match_result import SetScoreInput


def _match(
    *,
    home: uuid.UUID,
    away: uuid.UUID,
    status: MatchStatus = MatchStatus.completed,
    sets: tuple[SetScoreInput, ...],
    scheduled_at: datetime | None = None,
) -> MatchForAnalytics:
    return MatchForAnalytics(
        match_id=uuid.uuid4(),
        season_id=uuid.uuid4(),
        scheduled_at=scheduled_at,
        home_team_id=home,
        away_team_id=away,
        status=status,
        sets=sets,
    )


def test_zero_matches_yields_null_win_percentage() -> None:
    team_id = uuid.uuid4()
    stats = compute_team_statistics(team_id, [])
    assert stats.played_matches == 0
    assert stats.wins == 0
    assert stats.losses == 0
    assert stats.win_percentage is None


def test_one_win_and_one_loss() -> None:
    team = uuid.uuid4()
    opponent_a = uuid.uuid4()
    opponent_b = uuid.uuid4()
    matches = [
        _match(home=team, away=opponent_a, sets=(SetScoreInput(1, 25, 20),)),
        _match(home=opponent_b, away=team, sets=(SetScoreInput(1, 25, 20),)),
    ]
    stats = compute_team_statistics(team, matches)
    assert stats.played_matches == 2
    assert stats.wins == 1
    assert stats.losses == 1
    assert stats.win_percentage == 50.0


def test_multiple_sets_points_and_set_counts() -> None:
    team = uuid.uuid4()
    opponent = uuid.uuid4()
    matches = [
        _match(
            home=team,
            away=opponent,
            sets=(
                SetScoreInput(1, 25, 21),
                SetScoreInput(2, 23, 25),
                SetScoreInput(3, 25, 18),
            ),
        )
    ]
    stats = compute_team_statistics(team, matches)
    assert stats.sets_won == 2
    assert stats.sets_lost == 1
    assert stats.points_for == 25 + 23 + 25
    assert stats.points_against == 21 + 25 + 18


def test_invalid_completed_match_excluded() -> None:
    team = uuid.uuid4()
    opponent = uuid.uuid4()
    matches = [
        _match(
            home=team,
            away=opponent,
            sets=(
                SetScoreInput(1, 25, 20),
                SetScoreInput(2, 22, 25),
                SetScoreInput(3, 25, 23),
                SetScoreInput(4, 21, 25),
            ),
        )
    ]
    stats = compute_team_statistics(team, matches)
    assert stats.played_matches == 0
    assert stats.wins == 0
    assert stats.losses == 0
    assert stats.win_percentage is None


def test_scheduled_and_cancelled_excluded() -> None:
    team = uuid.uuid4()
    opponent = uuid.uuid4()
    matches = [
        _match(home=team, away=opponent, status=MatchStatus.scheduled, sets=()),
        _match(
            home=team,
            away=opponent,
            status=MatchStatus.cancelled,
            sets=(SetScoreInput(1, 25, 20),),
        ),
    ]
    stats = compute_team_statistics(team, matches)
    assert stats.played_matches == 0


def test_incomplete_set_numbers_excluded() -> None:
    team = uuid.uuid4()
    opponent = uuid.uuid4()
    matches = [
        _match(
            home=team,
            away=opponent,
            sets=(SetScoreInput(1, 25, 20), SetScoreInput(3, 25, 22)),
        )
    ]
    stats = compute_team_statistics(team, matches)
    assert stats.played_matches == 0


def test_timeline_sorted_chronologically() -> None:
    team = uuid.uuid4()
    opponent = uuid.uuid4()
    early = datetime(2025, 1, 1, tzinfo=UTC)
    late = datetime(2025, 2, 1, tzinfo=UTC)
    matches = [
        _match(home=team, away=opponent, scheduled_at=late, sets=(SetScoreInput(1, 25, 20),)),
        _match(home=team, away=opponent, scheduled_at=early, sets=(SetScoreInput(1, 25, 22),)),
    ]
    stats = compute_team_statistics(team, matches)
    assert len(stats.match_timeline) == 2
    assert stats.match_timeline[0].scheduled_at == early
    assert stats.match_timeline[1].scheduled_at == late
