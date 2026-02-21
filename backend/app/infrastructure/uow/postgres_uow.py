from asyncpg import Pool
from asyncpg.transaction import Transaction

from app.application.ports.event_bus import EventBus
from app.application.ports.repository import MatchRepository
from app.infrastructure.repositories.match_repositories import PostgresMatchRepository


class PostgresUnitOfWork:
    def __init__(self, pool: Pool):
        self._pool = pool
        self._matches = PostgresMatchRepository(pool)
        self._conn = None
        self._tx: Transaction = None

    def matches(self) -> MatchRepository:
        if self._conn is None:
            raise RuntimeError("UoW not started. Use async with")
        return self._matches

    async def __aenter__(self):
        self._conn = await self._pool.acquire()
        self._tx = self._conn.transaction()
        await self._tx.start()
        self._matches = PostgresMatchRepository(self._conn)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self._tx.rollback()
            else:
                await self._tx.commit()
        finally:
            await self._pool.release(self._conn)
            self._conn = None
            self._tx = None
            self._matches = None

    async def commit(self) -> None:
        if self._tx:
            await self._tx.commit()
            self._tx = self._conn.transaction()
            await self._tx.start()
            self._matches = PostgresMatchRepository(self._conn)
