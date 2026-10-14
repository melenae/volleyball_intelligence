import enum


class MatchStatus(enum.StrEnum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
