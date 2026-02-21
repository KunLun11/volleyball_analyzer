from dataclasses import dataclass
from datetime import datetime

from app.domain.values.base import BaseValueObject


@dataclass(frozen=True)
class Timestamp(BaseValueObject):
    value: datetime

    def validate(self):
        if not isinstance(self.value, datetime):
            raise TypeError("Value must be datetime")
        if self.value.tzinfo is None:
            raise ValueError("Timestamp must be timezone")

    def as_generic_type(self):
        return self.value


__all__ = [
    "Timestamp",
]
