from enum import IntEnum


class ActionTypeEnum(IntEnum):
    SERVE = 1
    ATTACK = 2
    BLOCK = 3


class ResultEnum(IntEnum):
    SCORED = 1
    NEUTRAL = 2
    ERROR = 3


class MatchStatusEnum(IntEnum):
    LIVE = 1
    COMPLETED = 2
    CANCELLED = 3


__all__ = [
    "ActionTypeEnum",
    "ResultEnum",
    "MatchStatusEnum",
]
