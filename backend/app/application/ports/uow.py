from abc import ABC, abstractmethod

from app.application.ports.repository import MatchRepository


class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    def matches(self) -> MatchRepository: ...


__all__ = [
    "UnitOfWork",
]
