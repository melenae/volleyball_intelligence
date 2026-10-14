"""Pure rules for match result completeness and consistency."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from app.models.enums import MatchStatus


class InvalidMatchReason(StrEnum):
    not_completed = "not_completed"
    same_teams = "same_teams"
    no_sets = "no_sets"
    invalid_set_numbers = "invalid_set_numbers"
    tied_set_score = "tied_set_score"
    negative_set_score = "negative_set_score"
    tied_sets_won = "tied_sets_won"


WinnerSide = Literal["home", "away", "none"]


@dataclass(frozen=True)
class SetScoreInput:
    set_number: int
    home_score: int
    away_score: int


@dataclass(frozen=True)
class MatchResultEvaluation:
    is_valid_completed_match: bool
    winner_side: WinnerSide
    home_sets_won: int
    away_sets_won: int
    reason: InvalidMatchReason | None = None


def evaluate_match_result(
    *,
    status: MatchStatus,
    home_team_id: object,
    away_team_id: object,
    sets: list[SetScoreInput],
) -> MatchResultEvaluation:
    if status != MatchStatus.completed:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=0,
            away_sets_won=0,
            reason=InvalidMatchReason.not_completed,
        )

    if home_team_id == away_team_id:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=0,
            away_sets_won=0,
            reason=InvalidMatchReason.same_teams,
        )

    if not sets:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=0,
            away_sets_won=0,
            reason=InvalidMatchReason.no_sets,
        )

    numbers = [item.set_number for item in sets]
    if len(numbers) != len(set(numbers)) or min(numbers) != 1:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=0,
            away_sets_won=0,
            reason=InvalidMatchReason.invalid_set_numbers,
        )
    expected = set(range(1, max(numbers) + 1))
    if set(numbers) != expected:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=0,
            away_sets_won=0,
            reason=InvalidMatchReason.invalid_set_numbers,
        )

    home_sets_won = 0
    away_sets_won = 0
    for item in sorted(sets, key=lambda row: row.set_number):
        if item.home_score < 0 or item.away_score < 0:
            return MatchResultEvaluation(
                is_valid_completed_match=False,
                winner_side="none",
                home_sets_won=0,
                away_sets_won=0,
                reason=InvalidMatchReason.negative_set_score,
            )
        if item.home_score == item.away_score:
            return MatchResultEvaluation(
                is_valid_completed_match=False,
                winner_side="none",
                home_sets_won=0,
                away_sets_won=0,
                reason=InvalidMatchReason.tied_set_score,
            )
        if item.home_score > item.away_score:
            home_sets_won += 1
        else:
            away_sets_won += 1

    if home_sets_won == away_sets_won:
        return MatchResultEvaluation(
            is_valid_completed_match=False,
            winner_side="none",
            home_sets_won=home_sets_won,
            away_sets_won=away_sets_won,
            reason=InvalidMatchReason.tied_sets_won,
        )

    winner: WinnerSide = "home" if home_sets_won > away_sets_won else "away"
    return MatchResultEvaluation(
        is_valid_completed_match=True,
        winner_side=winner,
        home_sets_won=home_sets_won,
        away_sets_won=away_sets_won,
        reason=None,
    )
