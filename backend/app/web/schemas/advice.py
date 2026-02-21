from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdviceResponse(BaseModel):
    advice: str
    generated_at: datetime
    match_id: UUID

    class Config:
        from_attributes = True
