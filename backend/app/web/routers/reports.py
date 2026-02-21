from fastapi import APIRouter, Depends

from app.application.queries.matches import MatchQueries
from app.web.deps import get_queries
from app.web.schemas.matches import MatchResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=list[MatchResponse])
async def get_reports(
    queries: MatchQueries = Depends(get_queries),
):
    return await queries.get_live()
