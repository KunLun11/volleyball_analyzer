from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Protocol

from app.domain.values.identifiers import MatchID
from app.domain.values.primitives import ScoreValue, SetNumber, TeamName


class DomainEvent(Protocol):
    occurred_at: datetime


@dataclass(frozen=True)
class MatchStarted:
    match_id: MatchID
    team_a: TeamName
    team_b: TeamName
    occurred_at: datetime

    def to_dict(self) -> dict:
        return {
            "type": "MatchStarted",
            "match_id": str(self.match_id.value),
            "team_a": self.team_a.value,
            "team_b": self.team_b.value,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class PointScored:
    match_id: MatchID
    team_id: int
    new_score_a: ScoreValue
    new_score_b: ScoreValue
    current_set: SetNumber
    occurred_at: datetime

    def to_dict(self) -> dict:
        return {
            "type": "PointScored",
            "match_id": str(self.match_id.value),
            "team_id": self.team_id,
            "new_score_a": self.new_score_a.value,
            "new_score_b": self.new_score_b.value,
            "current_set": self.current_set.value,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class SetCompleted:
    match_id: MatchID
    set_number: SetNumber
    winner: int
    final_score_a: ScoreValue
    final_score_b: ScoreValue
    occurred_at: datetime

    def to_dict(self) -> dict:
        return {
            "type": "SetCompleted",
            "match_id": str(self.match_id.value),
            "set_number": self.set_number.value,
            "winner": self.winner,
            "final_score_a": self.final_score_a.value,
            "final_score_b": self.final_score_b.value,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class MatchCompleted:
    match_id: MatchID
    winner: int
    total_sets: int
    final_set_scores: list[tuple[int, int]]
    occurred_at: datetime

    def to_dict(self) -> dict:
        return {
            "type": "MatchCompleted",
            "match_id": str(self.match_id.value),
            "winner": self.winner,
            "total_sets": self.total_sets,
            "final_set_scores": self.final_set_scores,
            "occurred_at": self.occurred_at.isoformat(),
        }


__all__ = [
    "DomainEvent",
    "MatchStarted",
    "PointScored",
    "SetCompleted",
    "MatchCompleted",
]
