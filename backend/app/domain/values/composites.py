from dataclasses import dataclass
from typing import Optional

from app.domain.enums import ActionTypeEnum, ResultEnum
from app.domain.values.identifiers import PlayerID
from app.domain.values.primitives import PlayerNumber, RotationPosition, ScoreValue
from app.domain.values.timestamps import Timestamp


@dataclass(frozen=True)
class Score:
    a: ScoreValue
    b: ScoreValue

    def __post_init__(self):
        if not isinstance(self.a, ScoreValue):
            raise TypeError("Score.a must be ScoreValue")
        if not isinstance(self.b, ScoreValue):
            raise TypeError("Score.b must be ScoreValue")

    def increment(self, team: int) -> "Score":
        if team == 1:
            return Score(a=ScoreValue(self.a.value + 1), b=self.b)
        elif team == 2:
            return Score(a=self.a, b=ScoreValue(self.b.value + 1))
        else:
            raise ValueError("Team must be 1 or 2")

    def is_set_won(self) -> tuple[bool, Optional[int]]:
        a, b = self.a.value, self.b.value
        if a >= 25 and a - b >= 2:
            return True, 1
        if b >= 25 and b - a >= 2:
            return True, 2
        return False, None

    def as_dict(self) -> dict:
        return {"a": self.a.value, "b": self.b.value}


@dataclass(frozen=True)
class Rotation:
    team_a: RotationPosition
    team_b: RotationPosition

    def __post_init__(self):
        if not isinstance(self.team_a, RotationPosition):
            raise TypeError("Rotation.team_a must be RotationPosition")
        if not isinstance(self.team_b, RotationPosition):
            raise TypeError("Rotation.team_b must be RotationPosition")

    def next(self, team: int) -> "Rotation":
        if team == 1:
            previous_position_a = self.team_a.value
            new_position_a = previous_position_a + 1
            if new_position_a > 6:
                new_position_a = 1
            new_team_a = RotationPosition(new_position_a)
            new_team_b = self.team_b
            return Rotation(new_team_a, new_team_b)
        elif team == 2:
            previous_position_b = self.team_b.value
            new_position_b = previous_position_b + 1
            if new_position_b > 6:
                new_position_b = 1
            new_team_a = self.team_a
            new_team_b = RotationPosition(new_position_b)
            return Rotation(new_team_a, new_team_b)
        else:
            raise ValueError("Team must be 1 or 2")

    def as_dict(self) -> dict:
        return {"team_a": self.team_a.value, "team_b": self.team_b.value}


@dataclass(frozen=True)
class TeamComposition:
    players: list[PlayerNumber]

    def __post_init__(self):
        if not isinstance(self.players, list):
            raise TypeError("Players must be list")
        if len(self.players) != 6:
            raise ValueError("Players must be 6")
        if not all(isinstance(p, PlayerNumber) for p in self.players):
            raise TypeError("All players must be PlayerNumber")

    def has_player(self, number: PlayerNumber) -> bool:
        if number in self.players:
            return True
        return False

    def get_players(self) -> tuple[PlayerNumber, ...]:
        return tuple(self.players)

    def as_list(self) -> list[int]:
        return [p.value for p in self.players]


@dataclass(frozen=True)
class MatchEvent:
    timestamp: Timestamp
    player_id: PlayerID
    team_id: int
    action_type: ActionTypeEnum
    result: ResultEnum
    rotation: RotationPosition

    def __post_init__(self):
        if self.team_id != 1 and self.team_id != 2:
            raise ValueError("Team ID must be 1 or 2")

    def is_scoring(self) -> bool:
        return self.result == ResultEnum.SCORED

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.value.isoformat(),
            "player_id": self.player_id.value,
            "team_id": self.team_id,
            "action_type": self.action_type.value,
            "result": self.result.value,
            "rotation": self.rotation.value,
        }


__all__ = [
    "Score",
    "Rotation",
    "TeamComposition",
    "MatchEvent",
]
