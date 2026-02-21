from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

VT = TypeVar("VT", bound=Any)


@dataclass(frozen=True)
class BaseValueObject(ABC, Generic[VT]):
    value: VT

    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self): ...

    @abstractmethod
    def as_generic_type(self): ...

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.as_generic_type() > other.as_generic_type()

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.as_generic_type() < other.as_generic_type()

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.as_generic_type() >= other.as_generic_type()

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.as_generic_type() <= other.as_generic_type()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.as_generic_type() == other.as_generic_type()

    def __hash__(self):
        return hash(self.as_generic_type())

    def __int__(self):
        return int(self.as_generic_type())

    def __str__(self):
        return str(self.as_generic_type())


__all__ = [
    "BaseValueObject",
]
