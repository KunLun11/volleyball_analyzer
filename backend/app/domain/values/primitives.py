from dataclasses import dataclass

from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class PlayerNumber(BaseValueObject):
    value: int

    def validate(self):
        if not (1 <= self.value <= 99):
            raise ValueError("Player number must be between 1 and 99")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class TeamName(BaseValueObject):
    value: str

    def validate(self):
        if not (1 <= len(self.value.strip()) <= 50):
            raise ValueError("Len team name must be between 1 and 50")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class SetNumber(BaseValueObject):
    value: int

    def validate(self):
        if not (1 <= self.value <= 5):
            raise ValueError("Count sets must be between 1 and 5")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class ScoreValue(BaseValueObject):
    value: int

    def validate(self):
        if not (0 <= self.value <= 100):
            raise ValueError("Scores must be between 0 and 100")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class RotationPosition(BaseValueObject):
    value: int

    def validate(self):
        if not (1 <= self.value <= 6):
            raise ValueError("Count rotation must be between 1 and 6")

    def as_generic_type(self):
        return self.value


__all__ = [
    "PlayerNumber",
    "TeamName",
    "SetNumber",
    "ScoreValue",
    "RotationPosition",
]
