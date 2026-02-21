from abc import ABC, abstractmethod

from app.domain.entities.matches import Match
from app.domain.values.identifiers import ChatID, MatchID


class MatchRepository(ABC):
    @abstractmethod
    async def add(self, match: Match) -> None: ...

    @abstractmethod
    async def get(self, match_id: MatchID) -> Match: ...

    @abstractmethod
    async def get_live_by_chat(self, chat_id: ChatID) -> Match | None: ...


__all__ = [
    "MatchRepository",
]
