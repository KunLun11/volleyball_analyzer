from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class MatchID(BaseValueObject):
    value: UUID

    @classmethod
    def generate(cls) -> "MatchID":
        return cls(uuid4())

    def validate(self):
        if not isinstance(self.value, UUID):
            raise ValueError("MatchID must be UUID")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class PlayerID(BaseValueObject):
    value: int

    def validate(self):
        if self.value <= 0:
            raise ValueError("ID must be positive")

    def as_generic_type(self):
        return self.value


@dataclass(frozen=True)
class ChatID(BaseValueObject):
    value: int

    def validate(self):
        if self.value <= 0:
            raise ValueError("ID must be positive")

    def as_generic_type(self):
        return self.value


__all__ = [
    "MatchID",
    "PlayerID",
    "ChatID",
]
